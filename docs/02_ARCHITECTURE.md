# System Architecture - AutoResearch AI

**Last Updated**: November 25, 2024  
**Version**: 1.0  
**Status**: Sprint 1 - Foundation (50% Complete)

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [High-Level System Design](#high-level-system-design)
3. [Three-Layer Architecture](#three-layer-architecture)
4. [Technology Stack](#technology-stack)
5. [Core Components](#core-components)
6. [Data Flow](#data-flow)
7. [Communication Patterns](#communication-patterns)
8. [Scalability & Performance](#scalability--performance)
9. [Security Considerations](#security-considerations)
10. [Design Decisions](#design-decisions)

---

## 🎯 Architecture Overview

AutoResearch AI is built on a **multi-agent autonomous system architecture** where specialized agents collaborate to complete complex research and content generation tasks.

### Core Architectural Principles
```
1. SEPARATION OF CONCERNS
   • Meta agents handle orchestration
   • Workers execute specific tasks
   • Storage handles persistence

2. AUTONOMY
   • System makes decisions without human intervention
   • Agents adapt workflow based on context
   • Quality-driven iteration loops

3. MODULARITY
   • Each agent is independent
   • Workers are plug-and-play
   • Easy to add new capabilities

4. TRANSPARENCY
   • Every decision is tracked
   • Complete audit trail
   • Explainable AI principles

5. SCALABILITY
   • Parallel execution where possible
   • Stateless workers (can scale horizontally)
   • Caching to reduce costs
```

---

## 🏛️ High-Level System Design

### System Context Diagram
```
                    ┌─────────────────┐
                    │      USER       │
                    │  (Web Browser)  │
                    └────────┬────────┘
                             │
                     HTTPS / REST API
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐  ┌─────────────────┐  ┌──────────────┐
│   STREAMLIT   │  │    FASTAPI      │  │  POSTGRESQL  │
│   FRONTEND    │◄─┤    BACKEND      │◄─┤   DATABASE   │
│   (Sprint 4)  │  │   (Sprint 3)    │  │  (Sprint 3)  │
└───────────────┘  └────────┬────────┘  └──────────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
                    ▼                 ▼
        ┌──────────────────┐  ┌──────────────┐
        │   META AGENT     │  │    REDIS     │
        │  ORCHESTRATION   │◄─┤    CACHE     │
        │   (Sprint 1)     │  │  (Sprint 3)  │
        └────────┬─────────┘  └──────────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
┌──────────────┐  ┌──────────────────┐
│   WORKER     │  │  EXTERNAL TOOLS  │
│  EXECUTION   │─►│  • Tavily API    │
│ (Sprint 2)   │  │  • ArXiv API     │
└──────────────┘  │  • Anthropic     │
                  │  • NewsAPI       │
                  └──────────────────┘
```

---

### Component Architecture
```
┌─────────────────────────────────────────────────────────────────────┐
│                      AUTORESEARCH AI SYSTEM                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │                    PRESENTATION LAYER                       │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │   │
│  │  │  Streamlit   │  │     CLI      │  │   REST API   │    │   │
│  │  │      UI      │  │    Tool      │  │   Clients    │    │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘    │   │
│  └────────────────────────────────────────────────────────────┘   │
│                              ▲                                      │
│                              │ HTTP/WebSocket                       │
│                              ▼                                      │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │                       API LAYER                             │   │
│  │  ┌────────────────────────────────────────────────────┐   │   │
│  │  │                FastAPI Backend                      │   │   │
│  │  │  • Request validation                               │   │   │
│  │  │  • Authentication & authorization                   │   │   │
│  │  │  • Rate limiting                                    │   │   │
│  │  │  • Response formatting                              │   │   │
│  │  └────────────────────────────────────────────────────┘   │   │
│  └────────────────────────────────────────────────────────────┘   │
│                              ▲                                      │
│                              │                                      │
│                              ▼                                      │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │                   BUSINESS LOGIC LAYER                      │   │
│  │                                                              │   │
│  │  ┌─────────────────────────────────────────────────────┐  │   │
│  │  │            META AGENT ORCHESTRATION                  │  │   │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐         │  │   │
│  │  │  │Controller│→ │  Planner │→ │ Strategy │         │  │   │
│  │  │  └──────────┘  └──────────┘  └──────────┘         │  │   │
│  │  │        ↓              ↓              ↓              │  │   │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐         │  │   │
│  │  │  │Orchestr. │→ │Supervisor│→ │  Merger  │         │  │   │
│  │  │  └──────────┘  └──────────┘  └──────────┘         │  │   │
│  │  │                       ↕                             │  │   │
│  │  │              ┌──────────────┐                      │  │   │
│  │  │              │ State Manager│                      │  │   │
│  │  │              └──────────────┘                      │  │   │
│  │  └─────────────────────────────────────────────────────┘  │   │
│  │                              ↕                              │   │
│  │  ┌─────────────────────────────────────────────────────┐  │   │
│  │  │              WORKER EXECUTION LAYER                  │  │   │
│  │  │                                                       │  │   │
│  │  │  ┌──────────────────────────────────────────────┐  │  │   │
│  │  │  │         BaseWorker (Abstract)                 │  │  │   │
│  │  │  └──────────────────┬───────────────────────────┘  │  │   │
│  │  │                     │                               │  │   │
│  │  │  ┌──────────────────┼──────────────────────────┐  │  │   │
│  │  │  │                  │                          │  │  │   │
│  │  │  ▼                  ▼                          ▼  │  │   │
│  │  │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐ │  │   │
│  │  │  │Research│  │Analysis│  │ Writing│  │Quality │ │  │   │
│  │  │  │Workers │  │Workers │  │Workers │  │Workers │ │  │   │
│  │  │  │  (5)   │  │  (3)   │  │  (4)   │  │  (5)   │ │  │   │
│  │  │  └────────┘  └────────┘  └────────┘  └────────┘ │  │   │
│  │  │                                                   │  │   │
│  │  └──────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              ▲                                      │
│                              │                                      │
│                              ▼                                      │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │                    INTEGRATION LAYER                        │   │
│  │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐          │   │
│  │  │ Tavily │  │ ArXiv  │  │ Claude │  │ News   │          │   │
│  │  │  API   │  │  API   │  │  API   │  │  API   │ ...      │   │
│  │  └────────┘  └────────┘  └────────┘  └────────┘          │   │
│  └────────────────────────────────────────────────────────────┘   │
│                              ▲                                      │
│                              │                                      │
│                              ▼                                      │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │                      DATA LAYER                             │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │   │
│  │  │ PostgreSQL   │  │    Redis     │  │  Vector DB   │    │   │
│  │  │  (Persist)   │  │   (Cache)    │  │  (Future)    │    │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘    │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🧱 Three-Layer Architecture

The system follows a clean three-layer architecture pattern for maintainability and testability.

### Layer 1: Data Schema Layer
```
┌─────────────────────────────────────────────────────────────┐
│                    SCHEMA LAYER (Pydantic)                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Purpose: Define all data structures and validation rules   │
│                                                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │   Brief    │  │    Plan    │  │   Task     │           │
│  │  Schema    │  │  Schema    │  │  Schema    │           │
│  └────────────┘  └────────────┘  └────────────┘           │
│                                                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │   State    │  │   Worker   │  │   Result   │           │
│  │  Schema    │  │  Schema    │  │  Schema    │           │
│  └────────────┘  └────────────┘  └────────────┘           │
│                                                              │
│  Benefits:                                                   │
│  ✓ Type safety with Pydantic validation                    │
│  ✓ Auto-generated documentation                            │
│  ✓ Clear contracts between components                      │
│  ✓ Easy to test                                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Key Characteristics:**
- All classes inherit from `pydantic.BaseModel`
- Validation happens automatically
- JSON serialization built-in
- Immutable by default (can be configured)

**Example:**
```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Brief(BaseModel):
    """User input specification."""
    
    request_id: Optional[str] = None
    topic: str = Field(..., min_length=1, max_length=500)
    content_type: ContentType
    target_length: Optional[int] = Field(default=2000, ge=500, le=10000)
    
    class Config:
        use_enum_values = True
        validate_assignment = True
```

---

### Layer 2: Business Logic Layer
```
┌─────────────────────────────────────────────────────────────┐
│                   BUSINESS LOGIC LAYER                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Purpose: Implement all agents and workers                  │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │              META AGENTS (7)                        │    │
│  │  • Controller: Main orchestrator                   │    │
│  │  • StateManager: Track workflow state              │    │
│  │  • Planner: Create execution plans                 │    │
│  │  • Strategy: Optimize plans                        │    │
│  │  • Orchestrator: Execute plans                     │    │
│  │  • Supervisor: Evaluate quality                    │    │
│  │  • Merger: Create final output                     │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │              WORKERS (17)                           │    │
│  │  Research:  5 workers (web, academic, news, etc.)  │    │
│  │  Analysis:  3 workers (synthesis, summary, etc.)   │    │
│  │  Writing:   4 workers (intro, article, etc.)       │    │
│  │  Quality:   5 workers (fact-check, edit, etc.)     │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  Patterns:                                                   │
│  ✓ Single Responsibility Principle                         │
│  ✓ Dependency Injection                                     │
│  ✓ Global instances with factory functions                 │
│  ✓ State immutability                                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Key Characteristics:**
- Each agent has a single, well-defined responsibility
- Agents communicate via AgentState object
- No direct dependencies between agents (loose coupling)
- Testable with mock data

**Agent Pattern:**
```python
class AgentName:
    """Agent description."""
    
    def __init__(self):
        """Initialize agent with dependencies."""
        self.counter = 0
    
    def main_method(self, state: AgentState) -> OutputType:
        """
        Main agent functionality.
        
        Args:
            state: Current workflow state
            
        Returns:
            Result of agent's work
        """
        # 1. Record action
        state.add_agent_action("AgentName", "action", {...})
        
        # 2. Do work
        result = self._do_work(state)
        
        # 3. Update state
        state.field = result
        
        # 4. Return
        return result

# Global instance
agent = AgentName()

# Helper function
def helper_function(state):
    return agent.main_method(state)
```

---

### Layer 3: LLM Prompt Layer
```
┌─────────────────────────────────────────────────────────────┐
│                     PROMPT LAYER (Sprint 2)                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Purpose: Define LLM instructions for each task             │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │            PROMPT TEMPLATES                         │    │
│  │                                                      │    │
│  │  Research Prompts:                                  │    │
│  │  • Web search query generation                      │    │
│  │  • Source summarization                             │    │
│  │  • Relevance evaluation                             │    │
│  │                                                      │    │
│  │  Analysis Prompts:                                  │    │
│  │  • Multi-source synthesis                           │    │
│  │  • Insight extraction                               │    │
│  │  • Theme identification                             │    │
│  │                                                      │    │
│  │  Writing Prompts:                                   │    │
│  │  • Article generation                               │    │
│  │  • Citation formatting                              │    │
│  │  • Tone adaptation                                  │    │
│  │                                                      │    │
│  │  Quality Prompts:                                   │    │
│  │  • Fact verification                                │    │
│  │  • Style checking                                   │    │
│  │  • SEO optimization                                 │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  Benefits:                                                   │
│  ✓ Consistent LLM behavior                                 │
│  ✓ Easy to test and improve                                │
│  ✓ Version control for prompts                             │
│  ✓ A/B testing capability                                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Prompt Structure:**
```python
RESEARCH_PROMPT_TEMPLATE = """
You are a research assistant helping to find information about: {topic}

Your task:
1. Search for relevant, recent sources (2023-2024)
2. Prioritize authoritative sources
3. Extract key information
4. Cite sources properly

Research depth: {research_depth}
Focus areas: {focus_areas}

Return JSON format:
{{
  "sources": [...],
  "key_findings": [...],
  "confidence": 0.0-1.0
}}
"""
```

---

## 🛠️ Technology Stack

### Core Technologies
```
┌─────────────────────────────────────────────────────────────┐
│                    TECHNOLOGY STACK                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  LANGUAGE & RUNTIME                                         │
│  ├─ Python 3.12+         Core language                     │
│  ├─ asyncio              Async execution                    │
│  └─ multiprocessing      Parallel processing                │
│                                                              │
│  AI & ML                                                     │
│  ├─ Anthropic Claude     LLM (Sonnet 3.5)                  │
│  ├─ LangChain            Agent framework                    │
│  ├─ LangGraph            State machine workflow             │
│  └─ LangSmith            Monitoring & tracing               │
│                                                              │
│  DATA & VALIDATION                                           │
│  ├─ Pydantic 2.5+        Data validation                   │
│  ├─ SQLAlchemy           ORM                                │
│  └─ Alembic              Database migrations                │
│                                                              │
│  WEB FRAMEWORK                                               │
│  ├─ FastAPI              REST API backend                   │
│  ├─ Uvicorn              ASGI server                        │
│  ├─ Streamlit            Frontend UI                        │
│  └─ WebSockets           Real-time updates                  │
│                                                              │
│  DATABASE & CACHE                                            │
│  ├─ PostgreSQL 15+       Relational database               │
│  ├─ Redis 7+             Cache & queue                      │
│  └─ (Pinecone/Chroma)    Vector DB (future)                │
│                                                              │
│  EXTERNAL APIs                                               │
│  ├─ Tavily API           Web search                         │
│  ├─ ArXiv API            Academic papers                    │
│  ├─ NewsAPI              News articles                      │
│  ├─ Firecrawl            Web scraping                       │
│  └─ LanguageTool         Grammar checking                   │
│                                                              │
│  DEVELOPMENT                                                 │
│  ├─ Docker               Containerization                   │
│  ├─ Docker Compose       Service orchestration              │
│  ├─ pytest               Testing framework                  │
│  ├─ Black                Code formatting                    │
│  ├─ Ruff                 Linting                            │
│  └─ MyPy                 Type checking                      │
│                                                              │
│  DEPLOYMENT                                                  │
│  ├─ Railway/Render       Hosting platform                   │
│  ├─ GitHub Actions       CI/CD                              │
│  └─ Sentry               Error tracking (optional)          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

### Technology Decisions & Rationale

#### Why Python?
```
✓ Rich AI/ML ecosystem (LangChain, Anthropic SDK)
✓ Rapid development
✓ Excellent for prototyping
✓ Large community
✓ Easy to deploy

⚠ Slower than compiled languages (acceptable for I/O-bound tasks)
```

#### Why Claude (Anthropic)?
```
✓ Best reasoning capabilities
✓ 200K context window
✓ Excellent at following instructions
✓ Strong citation accuracy
✓ Good at structured output

vs OpenAI GPT-4:
- Better reasoning for complex tasks
- Longer context window (200K vs 128K)
- More reliable output formatting
```

#### Why LangGraph (vs alternatives)?
```
LangGraph:
✓ Built for complex agent workflows
✓ State machine design (explicit control)
✓ Excellent debugging with LangSmith
✓ Production-ready

vs AutoGen:
- LangGraph more flexible for custom workflows
- Better state management

vs CrewAI:
- LangGraph lower-level (more control)
- Better for custom orchestration logic
```

#### Why FastAPI (vs Flask/Django)?
```
FastAPI:
✓ Modern Python (3.7+ type hints)
✓ Automatic OpenAPI docs
✓ Built-in async support
✓ Fast performance
✓ Easy data validation (Pydantic)

vs Flask:
- FastAPI more modern
- Better async support
- Auto-generated docs

vs Django:
- FastAPI lighter weight
- Better for APIs
- Django better for full web apps
```

#### Why Streamlit (vs React)?
```
Streamlit:
✓ Python-based (no JS needed)
✓ Rapid development
✓ Built-in components
✓ Good for demos/MVPs

⚠ Less customizable than React
⚠ Full page reloads (less performant)

For Sprint 4 (MVP): Streamlit perfect
For Production v2: Consider React rewrite
```

#### Why PostgreSQL (vs MongoDB)?
```
PostgreSQL:
✓ ACID compliance
✓ Mature and reliable
✓ Excellent JSON support (JSONB)
✓ pgvector extension (for embeddings)
✓ Strong consistency

vs MongoDB:
- PostgreSQL better for structured data
- Transactions more reliable
- Better for complex queries
```

---

## 🔧 Core Components

### 1. Meta Agent Layer (7 Agents)
```
┌───────────────────────────────────────────────────────────┐
│                     META AGENTS                            │
├───────────────────────────────────────────────────────────┤
│                                                            │
│  ┌─────────────────────────────────────────────────┐     │
│  │  1. CONTROLLER AGENT                             │     │
│  │  Role: Main entry point & orchestrator          │     │
│  │  Input: Brief (user request)                    │     │
│  │  Output: FinalOutput (complete article)         │     │
│  │  Responsibilities:                               │     │
│  │  • Initialize workflow                           │     │
│  │  • Coordinate all agents                         │     │
│  │  • Handle errors                                 │     │
│  │  • Return final output                           │     │
│  └─────────────────────────────────────────────────┘     │
│                        │                                   │
│                        ▼                                   │
│  ┌─────────────────────────────────────────────────┐     │
│  │  2. STATE MANAGER AGENT                          │     │
│  │  Role: Track workflow state                     │     │
│  │  Responsibilities:                               │     │
│  │  • Initialize AgentState                         │     │
│  │  • Manage phase transitions                      │     │
│  │  • Record agent actions                          │     │
│  │  • Track costs and metrics                       │     │
│  │  • Create state snapshots                        │     │
│  └─────────────────────────────────────────────────┘     │
│                        │                                   │
│                        ▼                                   │
│  ┌─────────────────────────────────────────────────┐     │
│  │  3. PLANNER AGENT                                │     │
│  │  Role: Create execution plan                    │     │
│  │  Input: Brief + State                           │     │
│  │  Output: Plan (steps, workers, estimates)       │     │
│  │  Responsibilities:                               │     │
│  │  • Analyze brief complexity                      │     │
│  │  • Select appropriate workers                    │     │
│  │  • Create execution steps                        │     │
│  │  • Estimate cost and time                        │     │
│  └─────────────────────────────────────────────────┘     │
│                        │                                   │
│                        ▼                                   │
│  ┌─────────────────────────────────────────────────┐     │
│  │  4. STRATEGY AGENT                               │     │
│  │  Role: Optimize execution plan                  │     │
│  │  Responsibilities:                               │     │
│  │  • Optimize parallelization                      │     │
│  │  • Apply budget constraints                      │     │
│  │  • Apply time constraints                        │     │
│  │  • Balance cost vs quality                       │     │
│  └─────────────────────────────────────────────────┘     │
│                        │                                   │
│                        ▼                                   │
│  ┌─────────────────────────────────────────────────┐     │
│  │  5. ORCHESTRATOR AGENT                           │     │
│  │  Role: Execute the plan                         │     │
│  │  Responsibilities:                               │     │
│  │  • Execute steps in order                        │     │
│  │  • Dispatch tasks to workers                     │     │
│  │  • Handle parallel/sequential execution          │     │
│  │  • Collect and aggregate results                 │     │
│  │  • Handle failures and retries                   │     │
│  └─────────────────────────────────────────────────┘     │
│                        │                                   │
│                        ▼                                   │
│  ┌─────────────────────────────────────────────────┐     │
│  │  6. SUPERVISOR AGENT                             │     │
│  │  Role: Evaluate quality & decide next action    │     │
│  │  Decision: CONTINUE (iterate) or COMPLETE (done)│     │
│  │  Responsibilities:                               │     │
│  │  • Calculate quality scores                      │     │
│  │  • Check against thresholds                      │     │
│  │  • Generate improvement feedback                 │     │
│  │  • Decide continuation or completion             │     │
│  └─────────────────────────────────────────────────┘     │
│                        │                                   │
│                        ▼                                   │
│  ┌─────────────────────────────────────────────────┐     │
│  │  7. MERGER AGENT                                 │     │
│  │  Role: Create final output                      │     │
│  │  Responsibilities:                               │     │
│  │  • Synthesize all results                        │     │
│  │  • Format article                                │     │
│  │  • Add citations                                 │     │
│  │  • Calculate metrics                             │     │
│  │  • Generate FinalOutput                          │     │
│  └─────────────────────────────────────────────────┘     │
│                                                            │
└───────────────────────────────────────────────────────────┘
```

**Communication:**
- All agents communicate via `AgentState` object
- State is passed by reference (modifications visible to all)
- Each agent records its actions in `state.agent_actions`
- Agents are loosely coupled (don't call each other directly)

---

### 2. Worker Layer (17 Workers)
```
┌───────────────────────────────────────────────────────────┐
│                    WORKER ARCHITECTURE                     │
├───────────────────────────────────────────────────────────┤
│                                                            │
│  ┌─────────────────────────────────────────────────┐     │
│  │           BaseWorker (Abstract Class)            │     │
│  │  • Common interface for all workers             │     │
│  │  • execute() method (standard entry point)      │     │
│  │  • Tool integration helpers                     │     │
│  │  • Cost & time tracking                         │     │
│  └─────────────────────────────────────────────────┘     │
│                        │                                   │
│         ┌──────────────┼──────────────┬──────────────┐   │
│         │              │              │              │   │
│         ▼              ▼              ▼              ▼   │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐
│  │ RESEARCH  │  │ ANALYSIS  │  │  WRITING  │  │  QUALITY  │
│  │  WORKERS  │  │  WORKERS  │  │  WORKERS  │  │  WORKERS  │
│  │    (5)    │  │    (3)    │  │    (4)    │  │    (5)    │
│  └───────────┘  └───────────┘  └───────────┘  └───────────┘
│                                                            │
│  Research Workers:                                         │
│  1. Web Search Worker (Tavily)                            │
│  2. Academic Search Worker (ArXiv)                         │
│  3. News Search Worker (NewsAPI)                           │
│  4. Web Scraper Worker (Firecrawl)                        │
│  5. Social Media Worker (Twitter/Reddit)                   │
│                                                            │
│  Analysis Workers:                                         │
│  6. Content Synthesizer Worker                            │
│  7. Summarization Worker                                  │
│  8. Insight Extractor Worker                              │
│                                                            │
│  Writing Workers:                                          │
│  9. Introduction Writer Worker                            │
│  10. Article Writer Worker                                │
│  11. Conclusion Writer Worker                             │
│  12. Citation Formatter Worker                            │
│                                                            │
│  Quality Workers:                                          │
│  13. Fact Checker Worker                                  │
│  14. Editor Worker (LanguageTool)                         │
│  15. SEO Optimizer Worker                                 │
│  16. Readability Checker Worker                           │
│  17. Plagiarism Checker Worker                            │
│                                                            │
└───────────────────────────────────────────────────────────┘
```

**Worker Execution Modes:**
```python
class ExecutionMode(str, Enum):
    PARALLEL = "parallel"      # Can run simultaneously
    SEQUENTIAL = "sequential"  # Must run one after another

# Example:
# Research workers: PARALLEL (can all search at once)
# Writing workers: SEQUENTIAL (intro → article → conclusion)
```

---

### 3. Storage Layer
```
┌───────────────────────────────────────────────────────────┐
│                     STORAGE ARCHITECTURE                   │
├───────────────────────────────────────────────────────────┤
│                                                            │
│  ┌─────────────────────────────────────────────────┐     │
│  │           POSTGRESQL (Primary Storage)           │     │
│  │                                                   │     │
│  │  Tables:                                         │     │
│  │  • briefs         - User requests                │     │
│  │  • articles       - Generated content            │     │
│  │  • executions     - Workflow runs                │     │
│  │  • sources        - Research sources             │     │
│  │  • feedback       - User ratings                 │     │
│  │  • analytics      - Usage statistics             │     │
│  │                                                   │     │
│  │  Indexes:                                        │     │
│  │  • topic (for search)                            │     │
│  │  • created_at (for time-based queries)           │     │
│  │  • user_id (for user-specific data)              │     │
│  └─────────────────────────────────────────────────┘     │
│                                                            │
│  ┌─────────────────────────────────────────────────┐     │
│  │              REDIS (Cache Layer)                 │     │
│  │                                                   │     │
│  │  Usage:                                          │     │
│  │  • Query result caching                          │     │
│  │  • Embedding caching                             │     │
│  │  • Session storage                               │     │
│  │  • Rate limiting                                 │     │
│  │  • Task queue (Celery, optional)                 │     │
│  │                                                   │     │
│  │  Keys:                                           │     │
│  │  • query:{hash} → result                         │     │
│  │  • embedding:{text_hash} → vector                │     │
│  │  • session:{id} → user_data                      │     │
│  │  • rate_limit:{user} → count                     │     │
│  │                                                   │     │
│  │  TTL: 1 hour (default), configurable            │     │
│  └─────────────────────────────────────────────────┘     │
│                                                            │
│  ┌─────────────────────────────────────────────────┐     │
│  │         VECTOR DATABASE (Future - Sprint 5)      │     │
│  │                                                   │     │
│  │  Options: Pinecone / Chroma / Weaviate          │     │
│  │                                                   │     │
│  │  Usage:                                          │     │
│  │  • Store document embeddings                     │     │
│  │  • Semantic search                               │     │
│  │  • Similar content retrieval                     │     │
│  │  • Knowledge base                                │     │
│  └─────────────────────────────────────────────────┘     │
│                                                            │
└───────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow

### Complete Request Flow
```
┌──────────────────────────────────────────────────────────────┐
│                    END-TO-END DATA FLOW                       │
└──────────────────────────────────────────────────────────────┘

1. USER REQUEST
   ↓
   User submits: { topic, content_type, target_length, ... }
   ↓

2. API LAYER (FastAPI)
   ↓
   • Validate request (Pydantic)
   • Create Brief object
   • Generate request_id
   • Return: { task_id, status: "pending" }
   ↓

3. CONTROLLER AGENT
   ↓
   • Initialize AgentState
   • Set phase: INITIALIZED → PLANNING
   ↓

4. STATE MANAGER
   ↓
   • Create new AgentState
   • Record initialization
   • Create first snapshot
   ↓

5. PLANNER AGENT
   ↓
   • Analyze brief complexity
   • Select workers: [web_search, article_writer, fact_checker]
   • Create Plan with 3 steps:
     Step 1: Research (parallel)
     Step 2: Writing (sequential)
     Step 3: Quality (parallel)
   • Estimate: cost=$2.20, time=15min
   ↓

6. STRATEGY AGENT
   ↓
   • Optimize plan (parallel where possible)
   • Check budget constraints
   • Final plan: cost=$2.20, time=15min ✓
   ↓

7. ORCHESTRATOR AGENT
   ↓
   STEP 1: Research Phase
   ├─ Execute web_search_worker (parallel)
   │  ├─ Call Tavily API
   │  ├─ Get 8 sources
   │  ├─ Cost: $0.02
   │  └─ Store in state.research_results
   ↓
   STEP 2: Writing Phase
   ├─ Execute article_writer_worker (sequential)
   │  ├─ Get research results from state
   │  ├─ Call Claude API
   │  ├─ Generate 2000-word article
   │  ├─ Cost: $0.08
   │  └─ Store in state.writing_results
   ↓
   STEP 3: Quality Phase
   ├─ Execute fact_checker_worker (parallel)
   │  ├─ Verify claims against sources
   │  ├─ Score: 92/100
   │  ├─ Cost: $0.05
   │  └─ Store in state.quality_results
   ↓

8. SUPERVISOR AGENT
   ↓
   • Calculate quality_score: 88/100 ✓
   • Calculate completeness_score: 95/100 ✓
   • Decision: COMPLETE (quality > 80% threshold)
   ↓

9. MERGER AGENT
   ↓
   • Extract article from state.writing_results
   • Format with citations
   • Add quality scores
   • Calculate metrics
   • Create FinalOutput:
     {
       article: { title, content, summary, ... },
       quality: { overall: 88, accuracy: 92, ... },
       sources: [15 sources],
       metrics: { cost: $2.20, time: 15min, ... }
     }
   ↓

10. STORAGE
    ↓
    • Save to PostgreSQL:
      - briefs table
      - articles table
      - executions table
    • Cache in Redis:
      - key: query:{hash}
      - TTL: 1 hour
    ↓

11. API RESPONSE
    ↓
    Return to user: FinalOutput
    ↓

12. USER RECEIVES
    ↓
    Complete article with:
    • 2000 words
    • 15 cited sources
    • Quality score: 88/100
    • Generated in 15 minutes
    • Cost: $2.20
```

---

### State Transitions
```
WORKFLOW PHASES:

INITIALIZED
    ↓ (Controller initializes)
PLANNING
    ↓ (Planner creates plan)
STRATEGY
    ↓ (Strategy optimizes)
EXECUTING
    ↓ (Orchestrator executes)
EVALUATING
    ↓ (Supervisor evaluates)
    ├─ Quality Good (>80%) → MERGING → COMPLETED ✓
    └─ Quality Low (<80%) → RE_PLANNING → PLANNING (iterate)
                                  ↓
                         (Max iterations = 3)
                                  ↓
                           MERGING → COMPLETED
                           (Force complete)

Error at any stage → FAILED
```

---

## 🔗 Communication Patterns

### 1. Agent-to-Agent Communication
```
All agents communicate via AgentState:

┌──────────────┐
│ Controller   │
└──────┬───────┘
       │ Creates AgentState
       ▼
┌──────────────┐
│ Planner      │
└──────┬───────┘
       │ Updates state.current_plan
       ▼
┌──────────────┐
│ Strategy     │
└──────┬───────┘
       │ Updates state.current_plan (optimized)
       ▼
┌──────────────┐
│ Orchestrator │
└──────┬───────┘
       │ Updates state.research_results,
       │         state.writing_results, etc.
       ▼
┌──────────────┐
│ Supervisor   │
└──────┬───────┘
       │ Updates state.quality_score
       │         state.should_continue
       ▼
┌──────────────┐
│ Merger       │
└──────────────┘

Key: State is passed by reference
     All agents can read/write state
     No direct agent-to-agent calls
```

---

### 2. Worker Execution Patterns

#### Parallel Execution
```
Orchestrator receives step with 3 workers:

┌────────────────────────────────────┐
│  Step: Research (PARALLEL)         │
├────────────────────────────────────┤
│  Workers:                          │
│  • web_search_worker               │
│  • academic_search_worker          │
│  • news_search_worker              │
└────────────────────────────────────┘
         │
         ├──────────────┬──────────────┐
         ▼              ▼              ▼
    ┌────────┐     ┌────────┐     ┌────────┐
    │ Worker │     │ Worker │     │ Worker │
    │   1    │     │   2    │     │   3    │
    └───┬────┘     └───┬────┘     └───┬────┘
        │              │              │
        └──────────────┴──────────────┘
                       │
                       ▼
            ┌──────────────────┐
            │ Aggregate Results │
            └──────────────────┘

Sprint 1: Mock parallel (loop sequentially)
Sprint 2: Real parallel (asyncio.gather)

Benefits:
✓ Faster execution (3x speedup for 3 workers)
✓ Better resource utilization
```

#### Sequential Execution
```
Orchestrator receives step with 3 workers:

┌────────────────────────────────────┐
│  Step: Writing (SEQUENTIAL)        │
├────────────────────────────────────┤
│  Workers:                          │
│  • introduction_writer             │
│  • article_writer                  │
│  • conclusion_writer               │
└────────────────────────────────────┘
         │
         ▼
    ┌─────────────────────┐
    │ introduction_writer │
    └──────────┬──────────┘
               │ result → state
               ▼
    ┌─────────────────────┐
    │ article_writer      │  (uses intro from state)
    └──────────┬──────────┘
               │ result → state
               ▼
    ┌─────────────────────┐
    │ conclusion_writer   │  (uses article from state)
    └──────────┬──────────┘
               │
               ▼
         Final result

Why: Maintain narrative flow
     Each part builds on previous
```

---

### 3. External API Communication
```
Worker → External API Communication:

┌────────────────┐
│ Research Worker│
└────────┬───────┘
         │
         ├─ Tavily API
         │  • POST /search
         │  • Headers: { api_key }
         │  • Body: { query }
         │  • Response: { results: [...] }
         │  • Retry: 3 attempts
         │  • Timeout: 30s
         │
         ├─ ArXiv API
         │  • GET /query
         │  • Params: { search_query }
         │  • Response: XML (parse to JSON)
         │  • No rate limit
         │  • Timeout: 15s
         │
         └─ NewsAPI
            • GET /everything
            • Headers: { api_key }
            • Params: { q, from, sortBy }
            • Response: { articles: [...] }
            • Rate limit: 100/day
            • Timeout: 15s

Error Handling:
1. Retry with exponential backoff
2. Fallback to alternative API
3. Log error and continue
4. Never fail entire workflow for single API
```

---

## 📈 Scalability & Performance

### Scalability Strategy
```
┌──────────────────────────────────────────────────────────┐
│                  SCALABILITY LAYERS                       │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  LAYER 1: APPLICATION SCALING                            │
│  ┌─────────────────────────────────────────────────┐    │
│  │  • Stateless API servers                        │    │
│  │  • Horizontal scaling (add more instances)      │    │
│  │  • Load balancer (Nginx/AWS ALB)                │    │
│  │  • Session stored in Redis (not in-memory)      │    │
│  └─────────────────────────────────────────────────┘    │
│                                                           │
│  LAYER 2: WORKER SCALING                                 │
│  ┌─────────────────────────────────────────────────┐    │
│  │  • Workers are stateless                        │    │
│  │  • Can run on separate machines                 │    │
│  │  • Task queue (Celery) for distribution         │    │
│  │  • Auto-scaling based on queue length           │    │
│  └─────────────────────────────────────────────────┘    │
│                                                           │
│  LAYER 3: DATABASE SCALING                               │
│  ┌─────────────────────────────────────────────────┐    │
│  │  • Read replicas for queries                    │    │
│  │  • Write to primary                             │    │
│  │  • Connection pooling                           │    │
│  │  • Partitioning by date/user                    │    │
│  └─────────────────────────────────────────────────┘    │
│                                                           │
│  LAYER 4: CACHE SCALING                                  │
│  ┌─────────────────────────────────────────────────┐    │
│  │  • Redis cluster (multi-node)                   │    │
│  │  • Cache hit rate > 30%                         │    │
│  │  • Reduce DB load by 30-40%                     │    │
│  │  • Reduce LLM costs by 20-30%                   │    │
│  └─────────────────────────────────────────────────┘    │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

### Performance Optimizations
```
1. CACHING
   • Query results (1 hour TTL)
   • Embeddings (persistent)
   • Worker results (24 hour TTL)
   
   Impact: 30-40% cost reduction

2. PARALLEL EXECUTION
   • Research workers in parallel
   • Quality workers in parallel
   • 3x faster for 3-worker steps
   
   Impact: 60% time reduction

3. BATCHING
   • Batch embedding generation
   • Batch API calls where possible
   • Reduce API overhead
   
   Impact: 10-20% cost reduction

4. SMART ROUTING
   • Use Haiku for simple tasks ($0.25/MTok)
   • Use Sonnet for complex tasks ($3/MTok)
   • Use Opus only when necessary ($15/MTok)
   
   Impact: 40% cost reduction

5. CONNECTION POOLING
   • Reuse database connections
   • Reuse HTTP connections
   • Reduce handshake overhead
   
   Impact: 20% latency reduction

TOTAL IMPACT:
✓ 70% cost reduction
✓ 80% time reduction
✓ 3x throughput increase
```

---

### Performance Targets
```
┌──────────────────────────────────────────────────────────┐
│                  PERFORMANCE TARGETS                      │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Metric                Target        Achieved (Sprint 1) │
│  ───────────────────────────────────────────────────────  │
│  API Response Time     <3s (p95)     TBD (Sprint 3)     │
│  Article Generation    <20min        15min (mock)        │
│  Cache Hit Rate        >30%          TBD (Sprint 3)      │
│  Database Query Time   <100ms        TBD (Sprint 3)      │
│  Concurrent Requests   100+          TBD (Sprint 4)      │
│  Throughput            10+ QPS       TBD (Sprint 4)      │
│  Error Rate            <1%           0% (mock)           │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

---

## 🔒 Security Considerations

### Security Layers
```
1. API SECURITY
   ├─ Authentication: JWT tokens
   ├─ Authorization: Role-based access
   ├─ Rate limiting: 100 req/hour per user
   ├─ Input validation: Pydantic schemas
   └─ HTTPS only (TLS 1.3)

2. DATA SECURITY
   ├─ Encryption at rest (PostgreSQL)
   ├─ Encryption in transit (TLS)
   ├─ API keys in environment variables
   ├─ No sensitive data in logs
   └─ Regular backups

3. API KEY MANAGEMENT
   ├─ Never commit to git
   ├─ Use environment variables
   ├─ Rotate keys regularly
   ├─ Separate keys per environment
   └─ Minimum permissions

4. CONTENT SAFETY
   ├─ Input sanitization
   ├─ Output filtering
   ├─ No execution of user code
   ├─ Content moderation (optional)
   └─ GDPR compliance

5. INFRASTRUCTURE
   ├─ Firewall rules
   ├─ Private subnets for databases
   ├─ DDoS protection
   ├─ Security updates
   └─ Monitoring & alerts
```

---

## 💭 Design Decisions

### Key Architectural Decisions

#### 1. Why Multi-Agent vs Single LLM?
```
DECISION: Use multiple specialized agents

REASONING:
✓ Specialization improves quality
✓ Parallel execution improves speed
✓ Easier to test and improve individual agents
✓ Better error isolation
✓ More transparent (can see each agent's work)

TRADE-OFFS:
✗ More complex system
✗ More API calls (higher cost)
✗ Requires orchestration logic

CONCLUSION: Benefits outweigh costs for quality-critical application
```

#### 2. Why LangGraph vs Alternatives?
```
DECISION: Use LangGraph for orchestration

ALTERNATIVES CONSIDERED:
- AutoGen: Good but less flexible
- CrewAI: Higher-level, less control
- Custom: Too much work

REASONING:
✓ State machine design (explicit control)
✓ Built for complex workflows
✓ Excellent debugging (LangSmith)
✓ Production-ready
✓ Active development

CONCLUSION: Best fit for custom agent orchestration
```

#### 3. Why Pydantic for Schemas?
```
DECISION: Use Pydantic for all data models

REASONING:
✓ Runtime type checking
✓ Automatic validation
✓ JSON serialization built-in
✓ FastAPI integration
✓ Clear error messages
✓ Immutability options

CONCLUSION: Industry standard for Python data validation
```

#### 4. Why Mock-First Development?
```
DECISION: Build with mocks, replace incrementally

REASONING:
✓ Fast development (no API costs)
✓ Test architecture before implementation
✓ Easy to test
✓ Can show progress quickly

PROCESS:
Sprint 1: Build with mocks
Sprint 2: Replace with real implementations
Sprint 3-4: Optimize and deploy

CONCLUSION: Enables rapid iteration and validation
```

---

## 📚 Related Documentation

### Quick Links
- **[Project Overview](./01_PROJECT_OVERVIEW.md)** - What and why
- **[Data Models](./03_DATA_MODELS.md)** - Complete schema reference
- **[Agent Specifications](./04_AGENTS.md)** - Detailed agent docs
- **[Worker Specifications](./05_WORKERS.md)** - Worker implementations
- **[Workflow & State Machine](./06_WORKFLOW.md)** - Execution flow
- **[Development Guide](./09_DEVELOPMENT.md)** - How to develop

---

## 🎯 Next Steps

### For Developers
1. ✅ Understand this architecture
2. ✅ Read [Data Models](./03_DATA_MODELS.md)
3. ✅ Read [Agent Specifications](./04_AGENTS.md)
4. ✅ Clone repository and explore code
5. ✅ Run tests to see system in action

### For Architects
1. ✅ Review design decisions
2. ✅ Assess scalability strategy
3. ✅ Evaluate technology choices
4. ✅ Consider production deployment
5. ✅ Provide feedback on architecture

---

**Document Version**: 1.0  
**Last Updated**: November 25, 2024  
**Next Review**: End of Sprint 2

---

END OF ARCHITECTURE DOCUMENTATION