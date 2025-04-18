# UI-Alchemy

A WIP of a tool for generating Material UI React components using Azure AI Services.

### Overview

UI-Alchemy is a Python application that leverages Azure AI Projects to generate customized React components using Material UI. It creates an interactive (CLI based, for now :) ) dialog with the user to gather requirements and then produces fully functional UI components.

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
