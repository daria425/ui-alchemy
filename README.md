<div align="center">
  <h1>UI-Alchemy ✨</h1>
  <img height="150px" width="150px" src='./ui_alchemy.png'>
</div>

## Overview

WIP: UI-Alchemy is a Python-based API tool designed to generate customizable React components.

## Architecture

This project uses LangGraph to orchestrate component generation and FastAPI to expose this as an API.

**Features so far**

- Conversational component generation
- Follow-up questions for clarification
- Validation of generated code
- Session-based API for persistent component generation

## Project Structure

-`/api`:

- `/app`: Main backend application code
  - `/agent`: Contains the LangGraph workflow and state management
    - `ui_alchemy.py`: Core LangGraph workflow
    - `state.py`: State definitions and management
    - `tools.py`: Tool implementations for component generation
    - `config.py`: Configuration settings
  - `/utils`: Utility functions for file handling and logging
- `/main.py`: Application entry point

## API Endpoints

| Endpoint                                         | Method | Description                                  |
| ------------------------------------------------ | ------ | -------------------------------------------- |
| `/ui-alchemy/api/sessions`                       | POST   | Create a new component generation session    |
| `/ui-alchemy/api/sessions/{session_id}/messages` | POST   | Continue an existing session with user input |

## Component Generation Flow

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#a867c9', 'primaryTextColor': '#fff', 'primaryBorderColor': '#9152b0', 'lineColor': '#e083cb', 'secondaryColor': '#f7c6e6', 'tertiaryColor': '#f4ebfa' }}}%%
flowchart TD
    classDef default fill:#a867c9,stroke:#9152b0,color:#fff
    classDef decision fill:#e083cb,stroke:#c767ad,color:#fff,stroke-width:2px
    classDef endpoint fill:#f7c6e6,stroke:#e4a8d4,color:#333

    A[Start] --> B[Initialize Session]
    B --> C[Understand Requirements]
    C --> D{Enough Information?}

    D -- No --> E[Generate Clarification Questions]
    E --> F[Return Questions to User]
    F --> G[Wait for User Response]
    G --> H[Process User Input]
    H --> C

    D -- Yes --> I[Select Libraries]
    I --> J[Generate Component Code]
    J --> K[Validate Component]
    K --> L{Valid Component?}

    L -- No --> M[Fix Validation Issues]
    M --> K

    L -- Yes --> N[Return Completed Component]

    class D,L decision
    class A,F,G,N endpoint
```
