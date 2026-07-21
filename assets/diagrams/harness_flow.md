# System Diagrams

## Harness Execution Flow Diagram

```mermaid
flowchart TD
    Start([User Input]) --> Detect[Language Detection]
    Detect --> Step1[Step 1: Requirements Service]
    Step1 --> Step2[Step 2: Evidence Collector]
    Step2 --> Step3[Step 3: Core Analysis]
    Step3 --> Step4[Step 4: Knowledge Updater]
    Step4 --> Step5[Step 5: Advisor]
    Step5 --> Step6[Step 6: Quality Gates]

    Step6 --> GateCheck{All Gates Pass?}
    GateCheck -->|Yes| Output([Generate Report])
    GateCheck -->|No| Retry[Auto-Fix & Retry]

    Retry --> MaxRetry{Max 2 Retries?}
    MaxRetry -->|No| Output
    MaxRetry -->|Yes| Step6

    style Start fill:#e1f5fe
    style Output fill:#c8e6c9
    style GateCheck fill:#fff9c4
    style Retry fill:#ffe0b2
```

## Quality Gate System Diagram

```mermaid
flowchart LR
    Input[Report Draft] --> U1[Gate U1: Source Count]
    U1 --> U2[Gate U2: Disclosure]
    U2 --> U3[Gate U3: Evidence Tier]
    U3 --> U4[Gate U4: Language Match]
    U4 --> U5[Gate U5: Template Format]
    U5 --> U6[Gate U6: Claim Traceability]
    U6 --> G1[Gate G1: School/Form ID]
    G1 --> G2[Gate G2: Physiology Grounding]
    G2 --> G3[Gate G3: Species-Specific Care]
    G3 --> G4[Gate G4: Scenario Analysis]

    G4 --> Check{All Passed?}
    Check -->|Yes| Final[Final Report]
    Check -->|No| Remediate[Apply Auto-Fix]
    Remediate --> Check

    style Input fill:#e1f5fe
    style Final fill:#c8e6c9
    style Check fill:#fff9c4
    style Remediate fill:#ffe0b2
```

## Graceful Degradation Levels

```mermaid
flowchart TD
    Start([Harness Start]) --> L0{Level 0: Full}
    L0 --> Error1{Error Type?}
    Error1 -->|Web Timeout| L1[Level 1: Fallback to KB]
    Error1 -->|KB Gap| L2[Level 2: Cached Data]
    Error1 -->|Analysis Fail| L3[Level 3: Best-Effort]
    Error1 -->|Critical| L4[Level 4: Limitation Only]

    L1 --> Continue[Continue with degraded capability]
    L2 --> Continue
    L3 --> Continue
    L4 --> Limitation[Show LIMITATION banner]

    style Start fill:#e1f5fe
    style Continue fill:#fff9c4
    style Limitation fill:#ffccbc
```

## Knowledge Pipeline Flow

```mermaid
flowchart LR
    Trigger[Schedule Trigger] --> Fetch1[Academic Sources]
    Trigger --> Fetch2[News Sources]
    Trigger --> Fetch3[Standards Docs]

    Fetch1 --> Process[Process & Score]
    Fetch2 --> Process
    Fetch3 --> Process

    Process --> Dedup[SHA256 Dedup]
    Dedup --> Filter[Confidence Filter]
    Filter --> Format[Format Entry]
    Format --> Append[Append to KB]

    Append --> Update[Update Log]
    Update --> Notify[Notification Complete]

    style Trigger fill:#e1f5fe
    style Notify fill:#c8e6c9
```

## Sub-Skill Interaction Diagram

```mermaid
flowchart TD
    Main[Main Harness] --> Req[Requirements Service]
    Main --> Evid[Evidence Collector]
    Main --> Core[Core Analysis]
    Main --> Know[Knowledge Updater]
    Main --> Adv[Advisor Service]
    Main --> QG[Quality Gate System]

    Req -->|Output| Core
    Evid -->|Output| Core
    Know -->|Output| Adv
    Core -->|Output| Adv
    Adv -->|Output| QG

    Know -.Query.-> KB[Knowledge Base]
    Evid -.Fetch.-> Web[Web Sources]

    style Main fill:#e1f5fe
    style KB fill:#fff9c4
    style Web fill:#ffe0b2
```

## Error Handling Flow

```mermaid
flowchart TD
    Start([Service Call]) --> Try{Execute with Retry}
    Try -->|Success| Result([Return Result])
    Try -->|Error| Check1{Is Retryable?}

    Check1 -->|Yes| Count{Attempts < Max?}
    Count -->|Yes| Wait[Backoff Wait]
    Wait --> Try

    Check1 -->|No| Check2{Fallback Available?}
    Count -->|No| Check2

    Check2 -->|Yes| Fallback[Execute Fallback]
    Fallback --> Result

    Check2 -->|No| Degradation{Degradation Level}
    Degradation --> L1[Level 1-3: Continue]
    Degradation --> L4[Level 4: Limitation]

    L1 --> Result
    L4 --> Limit([Limitation Response])

    style Start fill:#e1f5fe
    style Result fill:#c8e6c9
    style Limit fill:#ffccbc
```

## Token Optimization Flow

```mermaid
flowchart TD
    Start([Context Update]) --> Count[Count Tokens]
    Count --> Ratio{Usage Ratio}

    Ratio -->|< 80%| Add[Add Token]
    Ratio -->|>= 80%| Compress[Trigger Compression]

    Compress --> Sort[Sort by Priority]
    Sort --> Remove[Remove Low Priority]
    Remove --> Check{Still Over Threshold?}

    Check -->|Yes| Age[Remove Old Tokens]
    Age --> Check
    Check -->|No| Done([Context Ready])

    Add --> Done

    style Start fill:#e1f5fe
    style Done fill:#c8e6c9
    style Compress fill:#fff9c4
```

## Tool Invocation Flow

```mermaid
flowchart LR
    Request[Tool Request] --> Cache{Cache Hit?}
    Cache -->|Yes| Return([Return Cached])
    Cache -->|No| Validate[Validate Input]

    Validate --> Handler[Execute Handler]
    Handler --> Success{Success?}

    Success -->|Yes| Store[Store in Cache]
    Success -->|No| Fallback{Fallback Exists?}

    Fallback -->|Yes| Alt[Execute Fallback]
    Alt --> Return
    Fallback -->|No| Error([Return Error])

    Store --> Return
    Return --> End([Tool Result])

    style Request fill:#e1f5fe
    style Return fill:#c8e6c9
    style Error fill:#ffccbc
```

## Hook System Flow

```mermaid
flowchart TD
    Event([Event Emitted]) --> Lookup[Find Subscribers]
    Lookup --> Filter[Filter by Priority]

    Filter --> Exec[Execute Subscribers]
    Exec --> Check{Once Only?}

    Check -->|Yes| Remove[Remove Subscriber]
    Check -->|No| Next{More Subscribers?}

    Remove --> Next
    Next -->|Yes| Exec
    Next -->|No| Done([Event Complete])

    style Event fill:#e1f5fe
    style Done fill:#c8e6c9
```

## Configuration Loading Flow

```mermaid
flowchart TD
    Start([Load Settings]) --> Defaults[Load defaults.yaml]
    Defaults --> Local{Local Config Exists?}

    Local -->|Yes| LoadLocal[Load ~/.bonsai/config.yaml]
    Local -->|No| Env

    LoadLocal --> MergeLocal[Merge with Defaults]
    MergeLocal --> Env

    Env --> LoadEnv[Load Environment Variables]
    LoadEnv --> MergeEnv[Merge with Previous]

    MergeEnv --> Validate[Validate with Pydantic]
    Validate --> Error{Valid?}

    Error -->|No| Fail([Validation Error])
    Error -->|Yes| Cache[Cache Instance]

    Cache --> Return([Return Settings])

    style Start fill:#e1f5fe
    style Return fill:#c8e6c9
    style Fail fill:#ffccbc
```

## Test Suite Structure

```mermaid
flowchart TD
    Tests[pytest tests/] --> Unit[Unit Tests]
    Tests --> Integration[Integration Tests]
    Tests --> E2E[E2E Tests]

    Unit --> Models[models.py<br/>21 tests]
    Unit --> Config[config.py<br/>16 tests]
    Unit --> Errors[errors.py<br/>16 tests]
    Unit --> Services[services.py<br/>10 tests]

    Integration --> Pipeline[full_pipeline.py<br/>30 tests]

    E2E --> Harness[harness.py<br/>8 tests]

    style Tests fill:#e1f5fe
    style Unit fill:#e3f2fd
    style Integration fill:#fff9c4
    style E2E fill:#ffe0b2
```

## Deployment Architecture

```mermaid
flowchart TB
    User[Claude Code User] --> CLI[bonsai CLI]
    CLI --> Harness[Harness Orchestrator]

    Harness --> Services[Services Layer]
    Services --> Config[Config System]
    Services --> Hooks[Hook System]
    Services --> Tools[Tool Registry]

    Harness --> Knowledge[Knowledge Base]
    Harness --> Production[Production: Monitoring, Logging, Error Handling]

    Knowledge --> Crawl[Crawl Pipeline]

    style User fill:#e1f5fe
    style Harness fill:#fff9c4
    style Services fill:#e3f2fd
    style Production fill:#ffe0b2
```
