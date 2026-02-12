# State File

## A) Router / Decision Flow

```mermaid
flowchart TD
    A[User input] --> B{Starts with `outil:`?}
    B -->|Yes| C[Extract task name]
    C --> D["ensure_tool(task)"]
    D --> E["tool.run(user_input)"]

    B -->|No| F{Infer tool from keywords?}
    F -->|Yes| G["ensure_tool(inferred_task)"]
    G --> E

    F -->|No| H{LLM configured?}
    H -->|Yes| I[_generate_with_llm]
    H -->|No| J[Return no-LLM guidance response]

    E --> K[Assess errors]
    I --> K
    J --> K

    K --> L[Record interaction in knowledge + learning log]
    L --> M[Adjust caution level via tuner]
    M --> N{Improvement proposal warranted?}
    N -->|No| O[Return response]
    N -->|Yes| P[Judge evaluates proposal]
    P -->|Approved| Q[Apply change + track improvement]
    P -->|Rejected| O
    Q --> O
```

## B) Single Sequence for a Critical Test Case

### Critical case: no LLM available → error detected → improvement gets approved

1. Input is a generic prompt (e.g. `"Explique le plan"`) that does **not** start with `outil:`.
2. Router tries keyword inference; if no tool keyword is selected for this prompt path, it checks LLM availability.
3. Because no API key/client is configured, assistant returns the fallback "Je n'ai pas de LLM configuré..." message.
4. Error assessor marks the response with `errors_detected = 1` (marker-based detection).
5. Interaction is stored in `state.knowledge` and learning log.
6. Tuner increases caution level according to detected error.
7. Improvement proposal is generated (prudence reinforcement + verification tool).
8. Judge approves proposal.
9. Assistant applies change:
   - caution level increases again by +0.05 (bounded at 1.0),
   - `verification` tool is registered if missing,
   - proposal description is appended to `improvements_applied`.
10. Final response returned to the user is still the fallback message, but state is now safer for next turns.
