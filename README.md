# UI-Alchemy

### Overview

UI-Alchemy is a Python-based application designed to generate customizable React components using Material UI. It interacts with users through a CLI to collect UI requirements and outputs fully functional, production-ready components.

### Current Focus

This project is in an experimental phase. I'm currently exploring:

- Azure AI Agent Service for orchestrating component generation workflows.

- LangGraph as an alternative approach to managing multi-step AI agent logic.

### Structure:

- [agents](./agents/): Contains the UI generation agent code and instructions
- [config](./config/) Configuration for Azure AI services
- [utils](./config/): Utility functions for file handling and logging

### Conversation Flow:

```mermaid
flowchart TD
    A[Start] --> B[Initialize Agent]
    B --> C{Have Component?}

    C -- No --> F[Get User Prompt]
    C -- Yes --> D{Menu Choice}

    D -- "New Component" --> F
    D -- "Edit Component" --> E[Get Edit Feedback]
    D -- "Exit" --> Z[End]

    E --> EA[Edit Component]
    EA --> C

    F --> G[Run Agent]

    G --> H{Enough Information?}

    H -- No --> I[Get Follow-up Questions]
    H -- Yes --> M[Generate Component]

    I --> J[Get User Input]
    J -- More Input --> K[Update History]
    J -- Generate --> M

    K --> H

    M --> P[Display Component]
    P --> C
```

### Langgraph Graph (so far):

<img src='./graph.png'>
