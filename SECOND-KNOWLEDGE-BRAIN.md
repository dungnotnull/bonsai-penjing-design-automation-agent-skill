# SECOND-KNOWLEDGE-BRAIN.md — Skill 170: bonsai-penjing-design-automation

> **Living Knowledge Base** — updated by `tools/knowledge_updater.py` on a weekly
> schedule. All entries date-stamped; new entries appended at the bottom.
> Evidence hierarchy: Systematic Review > Meta-Analysis > Guideline/RCT > Cohort > Expert Consensus > News.

---

## 1. Core Concepts & Frameworks

### 1.1 Bonsai/Penjing Art & Botanical Pruning Design — Foundational Methods

### 1.1 Classical schools
Japan: formalized forms & aesthetics (wabi-sabi). China: penjing (landscape, mountain, water). Vietnam: tho nui (mountain), chan tho (multi-tier trunk), landscape styles.
### 1.2 Bonsai forms
Chokkan (formal upright), shakan (slant), moyogi (informal upright), kengai (cascade), han-kengai (semi-cascade), bunjingi (literati), sokan (twin-trunk), kabudachi (multi-trunk), neagari (exposed root).
### 1.3 Pruning physiology
Apical dominance via auxin (IAA) from shoot tips; pruning redirects auxin, releases lateral buds. Timing: prune in active growth for shaping, dormant for structural. Wound healing via CODIT (compartmentalization). Pinching vs pruning for ramification.
### 1.4 Wiring & care
Anodized aluminum / copper wire, gauges by branch thickness; remove before bite-in. Penjing: rocks (seki-ju), ishitsuki (root-over-rock), saikei (plantings). Care: species-specific watering, free-draining soil (akadama/pumice), repot 1-5 yr cycle, root pruning.

Knowledge categories covered:
- Classical schools (Japan forms, China penjing landscapes, Vietnam tho nui/chan tho)
- Bonsai forms (chokkan, shakan, moyogi, kengai, bunjingi, sokan)
- Pruning physiology (apical dominance, auxin, healing, timing)
- Wiring & shaping techniques
- Rock & landscape composition (penjing, ishitsuki)
- Species & horticultural care (watering, soil, repotting)

### 1.2 Evidence Hierarchy (this domain)
- **Tier 1**: Systematic review / meta-analysis / official standard (ISO, IAWA, CITES, FSC, WHO, UNESCO…)
- **Tier 2**: Peer-reviewed academic paper / RCT
- **Tier 3**: Industry report / professional association guideline
- **Tier 4**: News / blog / vendor material

---

## 2. Key Research Papers & Standards

| Title | Authors | Year | Venue | DOI/URL | Tier |
|------|---------|------|-------|---------|------|
| CODIT: compartmentalization of decay in trees | Shigo & Marx | 1977 | USDA Forest Service | 10.5962/bhl.title.69538? | 1 |
| Auxin and apical dominance | Cline | 1997 | Plant Physiol. | 10.1104/pp.96.4.1621 | 1 |
| Pruning effects on tree physiology | Goodfellow et al. | 1987 | For. Ecol. Manage. | 10.1016/0378-1127(87)90110-5 | 2 |
| Wound closure after pruning | Dujesiefken & Liese | 2015 | Arboric. J. | 10.1080/03071375.2015.1087131 | 2 |

Authoritative sources registered:
- HortScience / HortTechnology — ASHS
- Scientia Horticulturae — Elsevier
- Trees — Springer (arboriculture & pruning physiology)
- Journal of Horticulture & Forestry
- Environmental & Experimental Botany — Elsevier
- Frontiers in Plant Science (pruning physiology)

---

## 3. State-of-the-Art Methods & Tools

State of the art: AI-assisted bonsai form recommendation from images, 3D scanning & digital twin of trunk/branch structure, physiological models of pruning response, community award reference crawling (BCI/NBF competitions), precision species care sensors. Crawl targets: HortScience, Scientia Hortic., Trees, Front. Plant Sci.

---

## 4. Authoritative Data Sources

### 4.1 Domain authoritative sources
- Bonsai Clubs International — bonsai-bci.com
- National Bonsai Foundation — bonsai-nbf.org
- Bonsai Empire — bonsaiempire.com
- American Bonsai Society — absbonsai.org
- Ueki Bonsai (Vietnam) / Vietnam Bonsai Association
- Royal Horticultural Society (RHS) pruning references
- International Shohin Bonsai Association

### 4.2 Academic & research sources
- HortScience / HortTechnology — ASHS
- Scientia Horticulturae — Elsevier
- Trees — Springer (arboriculture & pruning physiology)
- Journal of Horticulture & Forestry
- Environmental & Experimental Botany — Elsevier
- Frontiers in Plant Science (pruning physiology)

---

## 5. Analytical Frameworks

Knowledge categories covered:
- Classical schools (Japan forms, China penjing landscapes, Vietnam tho nui/chan tho)
- Bonsai forms (chokkan, shakan, moyogi, kengai, bunjingi, sokan)
- Pruning physiology (apical dominance, auxin, healing, timing)
- Wiring & shaping techniques
- Rock & landscape composition (penjing, ishitsuki)
- Species & horticultural care (watering, soil, repotting)

Cross-reference the sub-skill workflows in `skills/*.md` for the domain methods applied at each step. The fixed bookends (requirements â†’ evidence â†’ knowledge â†’ synthesis â†’ quality gate) are mandatory; the core analysis sub-skills implement the domain-specific methods.

---

## 6. Self-Update Protocol

- **Crawl pipeline:** `tools/knowledge_updater.py`
- **Schedule:** weekly academic (Mondays 08:00) + daily news (07:00); documented in `CLAUDE.md`
- **Dedup:** SHA256 of DOI/URL (case/whitespace-insensitive)
- **Scoring:** composite 0â€“10 = recency(0.4) + keyword_relevance(0.4) + citation_count(0.2)
- **Crawl targets:** ArXiv categories []; Semantic Scholar keyword clusters; RSS feeds []
- **Gap-fill:** sub-knowledge-updater flags missing values as crawl queries
- **Append rule:** new entries appended under Section 7 with date stamp + relevance score

---

## 7. Knowledge Update Log

_(Appended automatically by the crawl pipeline. Baseline seeded with the references in Section 2.)_
