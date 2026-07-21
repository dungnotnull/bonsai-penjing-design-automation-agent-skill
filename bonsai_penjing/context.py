"""
AI Agent context manager for robust context window management.

Implements strategies for:
- Token-aware context truncation
- Priority-based content preservation
- Multi-turn conversation memory with summarization
- Sliding-window evidence management for large knowledge bases
"""

from __future__ import annotations

import hashlib
import json
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from bonsai_penjing.config import get_logger
from bonsai_penjing.models import (
    DegradationLevel,
    DesignAnalysis,
    EvidenceBundle,
    HarnessReport,
    KnowledgeEvidence,
    Language,
    RequirementInput,
)

logger = get_logger(__name__)


@dataclass
class ContextBudget:
    """Manages context window budget for AI agent interactions."""
    max_tokens: int = 180_000
    reserved_system_tokens: int = 8_000
    reserved_output_tokens: int = 16_000
    tokens_used: int = 0

    @property
    def available(self) -> int:
        return max(0, self.max_tokens - self.reserved_system_tokens - self.reserved_output_tokens - self.tokens_used)

    def reserve(self, tokens: int) -> bool:
        if self.available >= tokens:
            self.tokens_used += tokens
            return True
        return False

    def release(self, tokens: int) -> None:
        self.tokens_used = max(0, self.tokens_used - tokens)

    def remaining_ratio(self) -> float:
        total = self.max_tokens - self.reserved_system_tokens - self.reserved_output_tokens
        return max(0.0, self.available / total) if total > 0 else 0.0


@dataclass
class PriorityChunk:
    """A chunk of content with priority for context inclusion."""
    content: str
    priority: int  # 0 (critical) to 100 (optional)
    source: str
    estimated_tokens: int = 0

    def __post_init__(self) -> None:
        if self.estimated_tokens <= 0:
            self.estimated_tokens = _estimate_tokens(self.content)


def _estimate_tokens(text: str) -> int:
    """Rough token estimation: ~4 chars per token for English, ~2 chars for CJK/VN."""
    if not text:
        return 0
    cjk_count = sum(1 for c in text if ord(c) > 0x2FFF)
    latin_count = len(text) - cjk_count
    return max(1, (latin_count // 4) + (cjk_count // 2))


@dataclass
class ContextWindow:
    """Manages the full context window contents with priority-based eviction."""
    budget: ContextBudget = field(default_factory=ContextBudget)
    chunks: OrderedDict = field(default_factory=OrderedDict)  # id -> PriorityChunk
    total_tokens: int = 0
    evicted_count: int = 0

    def add(self, chunk_id: str, content: str, priority: int, source: str) -> bool:
        chunk = PriorityChunk(content=content, priority=priority, source=source)
        est = chunk.estimated_tokens

        if priority == 0 and not self.budget.reserve(est):
            self._evict_lowest_priority(est)

        if priority > 0 and not self.budget.reserve(est):
            self._evict_lowest_priority(est)

        if not self.budget.reserve(est):
            logger.warning("context_overflow", chunk_id=chunk_id, tokens_needed=est, available=self.budget.available)
            self.budget.release(est)
            return False

        self.chunks[chunk_id] = chunk
        self.total_tokens += est
        return True

    def _evict_lowest_priority(self, needed_tokens: int) -> None:
        if not self.chunks:
            return
        sorted_chunks = sorted(self.chunks.items(), key=lambda x: x[1].priority, reverse=True)
        freed = 0
        for cid, chunk in reversed(sorted_chunks):
            if freed >= needed_tokens:
                break
            if chunk.priority > 90:  # preserve critical content
                continue
            freed += chunk.estimated_tokens
            del self.chunks[cid]
            self.budget.release(chunk.estimated_tokens)
            self.evicted_count += 1
            logger.debug("context_evicted", chunk_id=cid, tokens=chunk.estimated_tokens)

    def get_compact(self) -> str:
        """Return a compact representation of all chunks, ordered by priority."""
        sorted_chunks = sorted(self.chunks.values(), key=lambda x: x.priority)
        return "\n\n".join(c.content for c in sorted_chunks)

    def get_ids(self) -> List[str]:
        return list(self.chunks.keys())


class ConversationMemory:
    """Maintains multi-turn conversation memory with summarization."""

    def __init__(self, max_history_turns: int = 20, summary_trigger_turns: int = 10) -> None:
        self.turns: List[Dict[str, Any]] = []
        self.summary: Optional[str] = None
        self.max_history_turns = max_history_turns
        self.summary_trigger_turns = summary_trigger_turns

    def add_turn(self, role: str, content: str) -> None:
        self.turns.append({
            "role": role,
            "content": content,
            "turn_id": _short_hash(content[:100] + role + str(len(self.turns))),
        })
        if len(self.turns) > self.summary_trigger_turns * 2:
            self._summarize()

    def _summarize(self) -> None:
        partial_segments = len(self.turns) - self.max_history_turns
        if partial_segments <= 0:
            return
        to_summarize = self.turns[:partial_segments]
        topics = set()
        for t in to_summarize:
            words = t["content"].split()[:20]
            topics.update(w for w in words if len(w) > 3)
        self.summary = (
            f"[Conversation history summary: {len(to_summarize)} turns covering "
            f"topics including {', '.join(sorted(topics)[:15])}]"
        )
        self.turns = self.turns[partial_segments:]

    def get_history_for_render(self) -> str:
        lines = []
        if self.summary:
            lines.append(self.summary)
        for t in self.turns:
            lines.append(f"[{t['role']}]: {t['content'][:500]}")
        return "\n".join(lines)


class EvidenceSlot:
    """Transmission slot for passing evidence between harness steps."""

    def __init__(self, step_name: str) -> None:
        self.step_name = step_name
        self.data: Dict[str, Any] = {}
        self.checksum: str = ""

    def store(self, key: str, value: Any) -> None:
        self.data[key] = value
        self._update_checksum()

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def _update_checksum(self) -> None:
        raw = json.dumps(self.data, sort_keys=True, default=str)
        self.checksum = hashlib.sha256(raw.encode()).hexdigest()[:16]


def _short_hash(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()[:8]


class ContextPipeline:
    """Manages context flow across the 6-step harness pipeline."""

    def __init__(self, budget_tokens: int = 180_000) -> None:
        self.context = ContextWindow(budget=ContextBudget(max_tokens=budget_tokens))
        self.memory = ConversationMemory()
        self.slots: Dict[str, EvidenceSlot] = {}

    def init_step(self, step: str) -> EvidenceSlot:
        self.slots[step] = EvidenceSlot(step)
        return self.slots[step]

    def get_slot(self, step: str) -> Optional[EvidenceSlot]:
        return self.slots.get(step)

    def add_context(self, chunk_id: str, content: str, priority: int = 50, source: str = "harness") -> bool:
        return self.context.add(chunk_id, content, priority, source)

    def build_prompt_context(self, required_sections: List[str]) -> str:
        """Build the context string for the current step, including only required + critical sections."""
        parts = []
        memory_str = self.memory.get_history_for_render()
        if memory_str:
            parts.append(memory_str)
        for section in required_sections:
            for cid, chunk in self.context.chunks.items():
                if section in chunk.source and chunk.priority < 80:
                    parts.append(chunk.content)
        parts.append(self.context.get_compact())
        return "\n---\n".join(parts)
