# Data Models & Schemas - AutoResearch AI

**Last Updated**: November 25, 2024  
**Version**: 1.0  
**Status**: Sprint 1 - Complete (All 6 schemas implemented)

---

## 📋 Table of Contents

1. [Introduction](#introduction)
2. [Schema Overview](#schema-overview)
3. [Brief Schema - User Input](#brief-schema---user-input)
4. [Plan Schema - Execution Planning](#plan-schema---execution-planning)
5. [Task Schema - Execution Tracking](#task-schema---execution-tracking)
6. [State Schema - Workflow Management](#state-schema---workflow-management)
7. [Worker Schema - Task I/O](#worker-schema---task-io)
8. [Result Schema - Final Output](#result-schema---final-output)
9. [Data Flow Example](#data-flow-example)
10. [Validation & Best Practices](#validation--best-practices)

---

## 🎯 Introduction

### What Are Schemas?

Schemas are **data contracts** that define:
- What information the system needs
- How data flows between components
- What the system produces

Think of them as **blueprints** for all data in AutoResearch AI.

### Why We Use Pydantic

All schemas use **Pydantic v2** for:
- ✅ **Automatic validation** - Catch errors early
- ✅ **Type safety** - IDE autocomplete & type checking
- ✅ **JSON serialization** - Easy API integration
- ✅ **Clear errors** - Helpful error messages

### Schema Categories
```
INPUT                    User specifications
    ↓
PLANNING                 What to do & how
    ↓
EXECUTION                Task tracking & results
    ↓
STATE                    Workflow coordination
    ↓
OUTPUT                   Final deliverable
```

---

## 🗺️ Schema Overview

### The Big Picture
```
┌──────────────────────────────────────────────────────────────┐
│                     SCHEMA ECOSYSTEM                          │
└──────────────────────────────────────────────────────────────┘

USER REQUEST
    │
    ├─► Brief Schema
    │   "I want a 2000-word article about AI in healthcare"
    │
    └─► Creates AgentState
            │
            ├─► Planner creates Plan Schema
            │   - Step 1: Research (3 workers, parallel)
            │   - Step 2: Writing (1 worker)
            │   - Step 3: Quality (3 workers, parallel)
            │
            ├─► Orchestrator creates Task Schemas
            │   - Task 1: web_search → WorkerInput → WorkerOutput
            │   - Task 2: article_writer → WorkerInput → WorkerOutput
            │   - Task 3: fact_checker → WorkerInput → WorkerOutput
            │   [Results stored in AgentState]
            │
            └─► Merger creates Result Schemas
                - ArticleResult: The generated article
                - QualityScore: Quality metrics
                - Source: All citations
                - ExecutionMetrics: Cost, time, etc.
                    ↓
                FinalOutput
                    ↓
                USER RECEIVES RESULT
```

---

### Schema Relationships

| Schema | Created By | Used By | Contains |
|--------|-----------|---------|----------|
| **Brief** | User | Controller, Planner | User requirements |
| **Plan** | Planner | Strategy, Orchestrator | Execution steps |
| **PlanStep** | Planner | Orchestrator | Worker definitions |
| **Task** | Orchestrator | Workers, Supervisor | Execution tracking |
| **AgentState** | Controller | All Agents | Complete workflow state |
| **WorkerInput** | Orchestrator | Workers | Task parameters |
| **WorkerOutput** | Workers | Orchestrator | Task results |
| **FinalOutput** | Merger | API/User | Complete result |

---

## 📝 Brief Schema - User Input

### Purpose

The **Brief** is where everything starts. It captures what the user wants:
- What topic to research
- What type of content to create
- How long it should be
- Quality requirements
- Budget and time constraints

### Key Concepts

#### 1. Topic Definition
```
Simple Topic:
"Artificial Intelligence"
→ Too vague, leads to unfocused research

Better Topic:
"How AI is transforming medical diagnosis in 2024"
→ Specific, actionable, time-bound
```

#### 2. Content Types

| Type | Description | Typical Length | Use Case |
|------|-------------|----------------|----------|
| **Article** | General informative content | 1500-3000 words | Blogs, magazines |
| **Blog Post** | Casual, conversational | 1000-2000 words | Personal blogs |
| **Research Report** | In-depth analysis | 3000-5000 words | Business, academic |
| **Tutorial** | Step-by-step guide | 1500-2500 words | How-to content |
| **Documentation** | Technical reference | 1000-4000 words | API docs, manuals |
| **Summary** | Condensed overview | 500-1000 words | Executive summaries |

#### 3. Tone & Style

**Professional** (Default):
- Formal language
- Third-person perspective
- Objective tone
- Example: "Recent studies indicate that AI diagnostic systems achieve 92% accuracy..."

**Academic**:
- Research-focused
- Citations emphasized
- Technical terminology
- Example: "The efficacy of convolutional neural networks (CNNs) in radiological imaging has been extensively documented (Smith et al., 2024)..."

**Casual**:
- Conversational language
- First/second person okay
- Relatable examples
- Example: "You've probably heard about AI in healthcare, but here's what's really happening..."

**Technical**:
- Detailed technical explanations
- Code examples where relevant
- Assumes technical audience
- Example: "The implementation utilizes a transformer-based architecture with attention mechanisms..."

**Conversational**:
- Friendly, approachable
- Questions to reader
- Storytelling elements
- Example: "Let me tell you why this matters for your healthcare..."

#### 4. Research Depth
```
LIGHT (5-10 minutes)
- Quick web search
- 3-5 sources
- Surface-level information
- Use case: Simple explanations, FAQs
- Cost: ~$0.50

STANDARD (15-20 minutes) [DEFAULT]
- Web + news search
- 8-12 sources
- Balanced depth
- Use case: Most articles
- Cost: ~$2.00

DEEP (30-45 minutes)
- Web + academic + news
- 15-20 sources
- Comprehensive analysis
- Use case: Research reports, whitepapers
- Cost: ~$5.00
```

#### 5. Quality Requirements

**Minimum Quality Score** (0.0 - 1.0):
```
0.60 - 0.70: Acceptable (basic content)
0.70 - 0.80: Good (standard quality)
0.80 - 0.90: Excellent (high quality) [DEFAULT]
0.90 - 1.00: Outstanding (publication-ready)
```

Higher thresholds mean:
- More thorough research
- More fact-checking
- Possible iterations (if quality not met first time)
- Higher cost and time

**Minimum Sources**:
```
3-5 sources: Light articles
5-10 sources: Standard articles [DEFAULT]
10-15 sources: Research-heavy
15+ sources: Academic/comprehensive
```

#### 6. Budget & Time Constraints

**Budget Examples**:
```
$0.50 - $1.00:  Light content, minimal research
$1.00 - $3.00:  Standard articles
$3.00 - $5.00:  High-quality, research-heavy [DEFAULT MAX]
$5.00 - $10.00: Comprehensive reports
$10.00+:        Deep research, multiple iterations
```

**Time Examples**:
```
5-10 minutes:   Simple topics, light research
15-20 minutes:  Standard articles [TYPICAL]
30-45 minutes:  Deep research
1-2 hours:      Comprehensive reports [MAX]
```

---

### Real-World Examples

#### Example 1: Simple Blog Post
```
Topic: "5 Tips for Better Sleep"
Content Type: Blog Post
Length: 1200 words
Tone: Casual
Research Depth: Light
Budget: $1.00
Time: 10 minutes

Result: Quick, accessible article with basic tips
```

#### Example 2: Professional Article
```
Topic: "AI trends in healthcare diagnostic imaging 2024"
Content Type: Article
Length: 2500 words
Tone: Professional
Research Depth: Standard
Min Sources: 12
Min Quality: 0.85
Budget: $3.50
Time: 25 minutes

Result: Well-researched article with strong citations
```

#### Example 3: Research Report
```
Topic: "Comparative analysis of AI diagnostic accuracy vs human doctors"
Content Type: Research Report
Length: 4000 words
Tone: Academic
Research Depth: Deep
Min Sources: 20 (academic preferred)
Min Quality: 0.90
Budget: $8.00
Time: 60 minutes

Result: Comprehensive, publication-quality report
```

---

### Common User Mistakes

❌ **Topic too vague**: "AI" → Better: "AI in medical diagnosis"
❌ **Budget too low**: $0.50 for 3000-word research report → Increase to $5
❌ **Unrealistic time**: 5 minutes for deep research → Allow 30+ minutes
❌ **Contradictory requirements**: Casual tone + academic sources → Pick one
❌ **Too many sources**: 50 sources for 1000-word blog → Use 5-10

---

### Validation Rules

The system automatically checks:

| Field | Rule | Why |
|-------|------|-----|
| Topic | 1-500 characters | Prevent empty or excessively long topics |
| Length | 500-10,000 words | Ensure reasonable content size |
| Budget | $0.50 - $50 | Prevent too low (fails) or too high (wasteful) |
| Time | 60 - 7200 seconds | At least 1 minute, max 2 hours |
| Quality | 0.0 - 1.0 | Valid percentage range |
| Sources | 1-50 | Reasonable citation range |

**If validation fails**, you get clear error messages:
```
"Topic must be between 1 and 500 characters"
"Budget must be at least $0.50"
"Target length must be between 500 and 10,000 words"
```

---

### Tips for Success

✅ **Be Specific**: "AI in healthcare" → "AI diagnostic tools for cancer detection"
✅ **Set Realistic Budget**: Standard article = $2-3, Research report = $5-8
✅ **Allow Time**: Minimum 15-20 minutes for quality results
✅ **Match Tone to Audience**: Academic for research, casual for blogs
✅ **Source Count**: More sources = better quality, but diminishing returns after 15-20

---

## 📋 Plan Schema - Execution Planning

### Purpose

After receiving the Brief, the **Planner agent** creates a **Plan** that defines:
- What steps to execute
- Which workers to use
- In what order
- Estimated cost and time

The Plan is the **roadmap** for the entire workflow.

---

### Key Concepts

#### 1. Plan Structure
```
Plan
├─ Step 1: Research Phase
│  ├─ Worker 1: web_search
│  ├─ Worker 2: academic_search
│  └─ Worker 3: news_search
│  Execution: PARALLEL (all 3 at once)
│  Time: 5 minutes
│  Cost: $0.50
│
├─ Step 2: Analysis Phase
│  └─ Worker 4: content_synthesizer
│  Execution: SEQUENTIAL
│  Time: 2 minutes
│  Cost: $0.30
│
├─ Step 3: Writing Phase
│  └─ Worker 5: article_writer
│  Execution: SEQUENTIAL
│  Time: 5 minutes
│  Cost: $0.80
│
└─ Step 4: Quality Phase
   ├─ Worker 6: fact_checker
   ├─ Worker 7: editor
   └─ Worker 8: seo_optimizer
   Execution: PARALLEL
   Time: 3 minutes
   Cost: $0.60

Total: 4 steps, 8 workers, 15 minutes, $2.20
```

#### 2. Execution Modes

**PARALLEL** - Multiple workers execute simultaneously:
```
Time without parallelization: 15 minutes (3 + 3 + 3)
Time with parallelization:    3 minutes  (max of 3)
Speedup: 5x faster
```

Used for:
- ✅ Research (multiple sources)
- ✅ Quality checks (independent verifications)

**SEQUENTIAL** - Workers execute one after another:
```
Worker 1 → (result) → Worker 2 → (result) → Worker 3
```

Used for:
- ✅ Writing (intro → body → conclusion)
- ✅ Analysis (needs all research first)

#### 3. Step Dependencies
```
Step 1: Research
   ↓ (depends on nothing)
Step 2: Analysis
   ↓ (depends on Step 1 - needs research results)
Step 3: Writing
   ↓ (depends on Step 2 - needs analysis)
Step 4: Quality
   ↓ (depends on Step 3 - needs article to check)
```

Cannot start Step 3 until Step 2 completes.

---

### How Complexity Affects the Plan

#### Simple Topic: "What is Python?"
```
Plan (Simple):
├─ Step 1: Light research (2 workers, 3 minutes, $0.30)
├─ Step 2: Quick article (1 worker, 4 minutes, $0.50)
└─ Step 3: Basic check (1 worker, 2 minutes, $0.20)

Total: 3 steps, 4 workers, 9 minutes, $1.00
Complexity Score: 0.3
```

#### Medium Topic: "AI in healthcare 2024"
```
Plan (Medium):
├─ Step 1: Standard research (3 workers, 5 minutes, $0.50)
├─ Step 2: Analysis (1 worker, 2 minutes, $0.30)
├─ Step 3: Full article (1 worker, 5 minutes, $0.80)
└─ Step 4: Quality suite (3 workers, 3 minutes, $0.60)

Total: 4 steps, 8 workers, 15 minutes, $2.20
Complexity Score: 0.6 [DEFAULT]
```

#### Complex Topic: "Comparative analysis of quantum computing applications"
```
Plan (Complex):
├─ Step 1: Deep research (5 workers, 10 minutes, $1.20)
├─ Step 2: Multi-source analysis (2 workers, 5 minutes, $0.80)
├─ Step 3: Comprehensive writing (3 workers, 12 minutes, $1.80)
├─ Step 4: Rigorous quality (5 workers, 8 minutes, $1.50)
└─ Step 5: Academic review (2 workers, 5 minutes, $0.70)

Total: 5 steps, 17 workers, 40 minutes, $6.00
Complexity Score: 0.9
```

---

### Plan Optimization

The **Strategy agent** optimizes the plan by:

**1. Parallelization**:
```
Before: Research → Research → Research (15 min sequential)
After:  Research ∥ Research ∥ Research (5 min parallel)
Saving: 10 minutes
```

**2. Worker Selection**:
```
Remove: Unnecessary workers (e.g., social media for academic topic)
Add: Missing workers (e.g., plagiarism check for publication)
```

**3. Budget Constraints**:
```
User Budget: $2.00
Original Plan: $2.50 (exceeds budget)

Optimization:
- Use Haiku instead of Sonnet for simple tasks: -$0.30
- Reduce research depth slightly: -$0.20
Optimized: $2.00 ✓
```

**4. Time Constraints**:
```
User Time Limit: 10 minutes
Original Plan: 15 minutes (exceeds limit)

Optimization:
- Remove optional workers: -3 minutes
- Switch to faster models: -2 minutes
Optimized: 10 minutes ✓
```

---

### Plan Iterations

If quality is insufficient, the **Supervisor** triggers **re-planning**:
```
ATTEMPT 1:
Plan: Light research (5 sources)
Result: Quality = 65% (below 80% threshold)
Decision: RE-PLAN

ATTEMPT 2:
Plan: Deep research (12 sources)
Result: Quality = 88% (meets threshold)
Decision: COMPLETE ✓

Total Iterations: 2
```

**Iteration Limits**: Maximum 3 attempts to prevent infinite loops

---

### Real-World Example

**User Request:**
> "Write a 2000-word article about AI in healthcare, citing at least 10 sources, 
> professional tone, max budget $3.00, max time 20 minutes"

**Planner Creates:**
```
Plan ID: plan_20241125_001
Complexity: 0.65 (Medium-High)

Step 1: Research Phase (PARALLEL)
├─ web_search (max_results=10)
├─ academic_search (years=2020-2024)
└─ news_search (days_back=60)
Time: 5 min | Cost: $0.50

Step 2: Synthesis Phase (SEQUENTIAL)
└─ content_synthesizer
Time: 2 min | Cost: $0.30

Step 3: Writing Phase (SEQUENTIAL)
└─ article_writer (tone=professional, length=2000)
Time: 6 min | Cost: $0.90

Step 4: Quality Phase (PARALLEL)
├─ fact_checker (verify_all=true)
├─ editor (check_grammar=true)
└─ citation_formatter
Time: 4 min | Cost: $0.60

TOTALS:
Steps: 4
Workers: 7
Time: 17 minutes (within 20 min limit ✓)
Cost: $2.30 (within $3.00 budget ✓)
Expected Sources: 12 (exceeds 10 minimum ✓)
```

**Strategy Agent Optimizes:**
- ✅ All constraints met
- ✅ Parallelization maximized (2 parallel steps)
- ✅ No changes needed

**Plan Approved** → Execution begins

---

## ✅ Task Schema - Execution Tracking

### Purpose

**Tasks** track individual worker executions. Each worker that runs creates a Task record with:
- Status (pending → running → completed/failed)
- Timing (start, end, duration)
- Results (what the worker produced)
- Costs (how much it spent)

---

### Task Lifecycle
```
1. CREATED
   Status: PENDING
   Created by: Orchestrator
   When: Plan step starts

2. STARTED
   Status: RUNNING
   Started at: [timestamp]
   Worker begins execution

3. COMPLETED
   Status: COMPLETED
   Completed at: [timestamp]
   Result: {...}
   Cost: $0.02
   Duration: 2.5 seconds

   OR

   FAILED
   Status: FAILED
   Completed at: [timestamp]
   Error: "API timeout"
   Retry count: 1
```

---

### Task Priorities

Tasks can have different priorities:
```
HIGH Priority:
- Critical workers (e.g., article_writer)
- Time-sensitive operations
- Execute first if queue exists

MEDIUM Priority: [DEFAULT]
- Most workers
- Standard execution order

LOW Priority:
- Optional workers (e.g., seo_optimizer)
- Can be skipped if budget/time tight
- Execute last
```

---

### Task Status Meanings

| Status | Meaning | What Happens Next |
|--------|---------|-------------------|
| **PENDING** | Task created, waiting to execute | Orchestrator will start it |
| **RUNNING** | Worker is currently executing | Wait for completion |
| **COMPLETED** | Successfully finished | Store result in AgentState |
| **FAILED** | Execution failed | Retry (up to 3 times) or skip |
| **CANCELLED** | Manually cancelled | Skip, don't retry |

---

### Task Results Storage

Each task stores results differently:

**Research Workers** → `state.research_results`:
```
[
  {
    "worker": "web_search",
    "sources": [
      {"title": "...", "url": "...", "snippet": "..."},
      ...
    ]
  },
  {
    "worker": "academic_search",
    "sources": [...]
  }
]
```

**Writing Workers** → `state.writing_results`:
```
[
  {
    "worker": "article_writer",
    "content": "# Introduction\n\n...",
    "word_count": 2150
  }
]
```

**Quality Workers** → `state.quality_results`:
```
[
  {
    "worker": "fact_checker",
    "verified_claims": 45,
    "unverified_claims": 2,
    "accuracy_score": 0.96
  },
  {
    "worker": "editor",
    "grammar_score": 0.92,
    "suggestions": [...]
  }
]
```

---

### Task Batching (Parallel Execution)

When multiple tasks execute in parallel, they're grouped in a **TaskBatch**:
```
Batch: research_batch_001
Step: step_1
Execution Mode: PARALLEL

Tasks in Batch:
├─ Task 1: web_search (RUNNING)
├─ Task 2: academic_search (RUNNING)
└─ Task 3: news_search (RUNNING)

All 3 execute simultaneously

After completion:
├─ Task 1: COMPLETED (2.1s, $0.02)
├─ Task 2: COMPLETED (3.5s, $0.03)
└─ Task 3: COMPLETED (2.8s, $0.02)

Batch Duration: 3.5s (longest task)
Batch Cost: $0.07 (sum of all)
```

---

### Error Handling & Retries
```
Task: academic_search
Attempt 1: FAILED ("ArXiv API timeout")
   ↓
Wait 2 seconds
   ↓
Attempt 2: FAILED ("Connection refused")
   ↓
Wait 4 seconds
   ↓
Attempt 3: COMPLETED ✓

Retry count: 2
Final status: COMPLETED
```

**Retry Strategy**:
- Exponential backoff: 2s, 4s, 8s
- Maximum 3 attempts
- After 3 failures → Mark as FAILED, continue workflow

---

### Real-World Example

**User Request**: Article about AI

**Tasks Created During Execution**:
```
Task 1:
├─ ID: task_001
├─ Worker: web_search
├─ Step: step_1 (Research)
├─ Priority: HIGH
├─ Status: PENDING → RUNNING → COMPLETED
├─ Started: 14:30:15
├─ Completed: 14:30:18
├─ Duration: 2.8 seconds
├─ Cost: $0.02
├─ Tokens: 450
├─ Result: {"sources": [8 web sources]}

Task 2:
├─ ID: task_002
├─ Worker: academic_search
├─ Step: step_1 (Research)
├─ Priority: HIGH
├─ Status: PENDING → RUNNING → COMPLETED
├─ Started: 14:30:15 (parallel with task_001)
├─ Completed: 14:30:19
├─ Duration: 3.5 seconds
├─ Cost: $0.03
├─ Tokens: 520
├─ Result: {"sources": [4 academic papers]}

Task 3:
├─ ID: task_003
├─ Worker: article_writer
├─ Step: step_3 (Writing)
├─ Priority: HIGH
├─ Status: PENDING → RUNNING → COMPLETED
├─ Started: 14:30:22 (after research complete)
├─ Completed: 14:30:28
├─ Duration: 6.2 seconds
├─ Cost: $0.85
├─ Tokens: 3200
├─ Result: {"content": "# Title\n\n...", "word_count": 2150}

Task 4:
├─ ID: task_004
├─ Worker: fact_checker
├─ Step: step_4 (Quality)
├─ Priority: MEDIUM
├─ Status: PENDING → RUNNING → COMPLETED
├─ Started: 14:30:30
├─ Completed: 14:30:34
├─ Duration: 4.1 seconds
├─ Cost: $0.45
├─ Tokens: 1800
├─ Result: {"accuracy": 0.92, "verified": 42, "unverified": 3}

All Tasks Summary:
Total: 4 tasks
Completed: 4
Failed: 0
Total Cost: $1.35
Total Time: 19 seconds (with parallelization)
```

---

## 🔄 State Schema - Workflow Management

### Purpose

**AgentState** is the **single source of truth** for the entire workflow. It's like a shared whiteboard where all agents read and write.

Think of it as the **command center** tracking everything:
- Where are we in the workflow?
- What's been done so far?
- What are the results?
- How much have we spent?
- Any errors?

---

### What's Inside AgentState
```
AgentState
│
├─ Identification
│  ├─ execution_id: "exec_20241125_143022"
│  └─ current_phase: EXECUTING
│
├─ Input
│  └─ brief: {user's original request}
│
├─ Planning
│  ├─ current_plan: {active plan}
│  ├─ plan_history: [previous plans if re-planned]
│  └─ iteration_count: 0 (or 1, 2 if re-planned)
│
├─ Execution Tracking
│  ├─ all_tasks: [task_001, task_002, ...]
│  └─ current_step_index: 2 (executing step 2)
│
├─ Results (populated by workers)
│  ├─ research_results: [web sources, academic papers, ...]
│  ├─ analysis_results: [insights, themes, ...]
│  ├─ writing_results: [article content]
│  └─ quality_results: [fact-check, grammar, seo scores]
│
├─ Evaluation (set by Supervisor)
│  ├─ quality_score: 0.88
│  ├─ completeness_score: 0.95
│  ├─ should_continue: false (quality good!)
│  └─ feedback: null (no issues)
│
├─ Metrics
│  ├─ total_cost: $2.35
│  ├─ total_tokens: 12,500
│  ├─ started_at: 2024-11-25 14:30:00
│  └─ completed_at: 2024-11-25 14:45:20
│
└─ Audit Trail
   ├─ agent_actions: [all actions by all agents]
   ├─ errors: [any errors encountered]
   └─ warnings: [any warnings generated]
```

---

### Workflow Phases

The `current_phase` field tracks where we are:
```
INITIALIZED
│  System just started
│  Brief received
│  State created
│
├─► PLANNING
│   Planner analyzing brief
│   Creating execution plan
│
├─► STRATEGY
│   Strategy optimizing plan
│   Checking constraints
│
├─► EXECUTING
│   Orchestrator running workers
│   Tasks being executed
│   Results being collected
│
├─► EVALUATING
│   Supervisor checking quality
│   Deciding: continue or complete?
│
├─► RE_PLANNING (if quality low)
│   Creating improved plan
│   Back to EXECUTING
│
├─► MERGING
│   Creating final output
│   Formatting results
│
└─► COMPLETED ✓
    Final output ready
    Workflow done

    OR

    FAILED ✗
    Unrecoverable error
    Workflow aborted
```

---

### How Agents Use State

**All agents follow this pattern:**
```
1. READ from state
   • Get information needed for their task
   • Example: Planner reads brief, Orchestrator reads plan

2. DO WORK
   • Execute their specific responsibility
   • Example: Planner creates plan, Orchestrator runs workers

3. WRITE to state
   • Update state with results
   • Example: Store plan, store worker results

4. RECORD ACTION
   • Log what they did
   • Example: "Planner created plan with 4 steps"
```

**Example - Planner Agent**:
```
# 1. READ
brief = state.brief
budget_limit = brief.max_budget

# 2. DO WORK
plan = create_execution_plan(brief)

# 3. WRITE
state.current_plan = plan
state.current_phase = WorkflowPhase.STRATEGY

# 4. RECORD
state.add_agent_action(
    agent_name="Planner",
    action="create_plan",
    details={"steps": len(plan.steps), "cost": plan.estimated_total_cost}
)
```

---

### State Evolution During Workflow

**Initial State** (just created):
```
execution_id: exec_20241125_143022
current_phase: INITIALIZED
brief: {user request}
current_plan: null
all_tasks: []
research_results: []
writing_results: []
quality_results: []
quality_score: null
total_cost: $0.00
agent_actions: []
```

**After Planning**:
```
current_phase: STRATEGY
current_plan: {plan with 4 steps, 8 workers}
agent_actions: [
  "Controller: initialize",
  "Planner: create_plan"
]
```

**During Execution**:
```
current_phase: EXECUTING
current_step_index: 1 (step 2 of 4)
all_tasks: [task_001, task_002, task_003]
research_results: [
  {worker: "web_search", sources: [...]},
  {worker: "academic_search", sources: [...]}
]
total_cost: $0.85
agent_actions: [
  ...,
  "Orchestrator: execute_step",
  "Orchestrator: dispatch_task"
]
```

**After Completion**:
```
current_phase: COMPLETED
all_tasks: [8 tasks, all COMPLETED]
research_results: [12 sources]
writing_results: [{article: 2150 words}]
quality_results: [{fact_check: 92%}, {grammar: 90%}]
quality_score: 0.88
completeness_score: 0.95
should_continue: false
total_cost: $2.35
total_tokens: 12,500
completed_at: 2024-11-25 14:45:20
agent_actions: [15 actions total]
```

---

### Audit Trail

Every action by every agent is recorded:
```
agent_actions: [
  {
    agent_name: "Controller",
    action: "initialize",
    timestamp: 2024-11-25 14:30:00,
    details: {execution_id: "exec_..."}
  },
  {
    agent_name: "Planner",
    action: "create_plan",
    timestamp: 2024-11-25 14:30:02,
    details: {steps: 4, estimated_cost: 2.20}
  },
  {
    agent_name: "Strategy",
    action: "optimize_plan",
    timestamp: 2024-11-25 14:30:05,
    details: {parallelized: 2, cost_saved: 0.30}
  },
  {
    agent_name: "Orchestrator",
    action: "execute_step",
    timestamp: 2024-11-25 14:30:10,
    details: {step_id: "step_1", workers: 3}
  },
  ...
]
```

**Why This Matters:**
- 🔍 Debugging: See exactly what happened
- 📊 Analytics: Understand system behavior
- ✅ Transparency: User can see how article was created
- 🐛 Error tracking: Find where things went wrong

---

### Cost Tracking

State tracks all costs:
```
Initial: total_cost = $0.00

After web_search: add_cost(0.02)
→ total_cost = $0.02

After academic_search: add_cost(0.03)
→ total_cost = $0.05

After article_writer: add_cost(0.85)
→ total_cost = $0.90

After fact_checker: add_cost(0.45)
→ total_cost = $1.35

Final: total_cost = $2.35
```

**Budget Enforcement**:
```
if state.total_cost > brief.max_budget:
    warning = f"Cost ${state.total_cost} exceeds budget ${brief.max_budget}"
    state.add_warning(warning)
    # Decide: stop or continue with warning
```

---

### Iteration Handling

If quality is low, state tracks re-planning:
```
ITERATION 1:
current_plan: {light research plan}
quality_score: 0.65 (below 0.80 threshold)
should_continue: true
feedback: "Need more sources, especially academic"
iteration_count: 1

→ Save current_plan to plan_history
→ Go back to PLANNING phase

ITERATION 2:
current_plan: {deep research plan}
quality_score: 0.88 (meets threshold)
should_continue: false
feedback: null
iteration_count: 2

→ COMPLETE
```

**Iteration Limit**:
```
if state.iteration_count >= state.max_iterations:
    # Force complete even if quality low
    state.current_phase = MERGING
    state.add_warning("Reached max iterations, completing anyway")
```

---

## 🔧 Worker Schema - Task I/O

### Purpose

Workers are the **doers** of the system. Each worker:
- Receives **WorkerInput** (what to do)
- Executes its task
- Returns **WorkerOutput** (what it did)

This standardized input/output ensures **all workers have the same interface**.

---

### WorkerInput - What Workers Receive
```
WorkerInput
├─ task_id: "task_001"
├─ worker_id: "web_search"
├─ context: {
│    everything the worker needs to know
│  }
└─ config: {
     worker-specific settings
   }
```

**Context** contains:
- User's original brief
- Current execution state
- Results from previous workers (if needed)
- Any other relevant information

**Config** contains:
- Worker-specific parameters
- Example for web_search: `{max_results: 10, timeout: 30}`
- Example for article_writer: `{tone: "professional", length: 2000}`

---

### WorkerOutput - What Workers Return
```
WorkerOutput
├─ task_id: "task_001" (same as input)
├─ worker_id: "web_search" (same as input)
├─ success: true/false
├─ result: {
│    actual work product
│  }
├─ error: null (or error message if failed)
├─ cost: $0.02
├─ tokens_used: 450
├─ execution_time_seconds: 2.5
└─ metadata: {
     any additional info
   }
```

---

### Example Worker Execution

**Scenario**: Web search worker needs to find articles about "AI in healthcare"

**Input**:
```
WorkerInput {
  task_id: "task_001"
  worker_id: "web_search"
  context: {
    query: "AI in healthcare 2024",
    max_results: 10,
    brief: {
      topic: "AI trends in healthcare",
      content_type: "article",
      ...
    }
  }
  config: {
    timeout: 30,
    retry_count: 3
  }
}
```

**Worker Executes**:
```
1. Call Tavily API with query
2. Receive 10 search results
3. Process and format results
4. Track cost and time
```

**Output** (Success):
```
WorkerOutput {
  task_id: "task_001"
  worker_id: "web_search"
  success: true
  result: {
    sources: [
      {
        title: "AI Revolutionizes Healthcare Diagnostics",
        url: "https://healthtech.example.com/ai-diagnostics",
        snippet: "Recent advances in AI have led to 40% improvement...",
        published_date: "2024-10-15",
        relevance: 0.95
      },
      {
        title: "Machine Learning in Medical Imaging",
        url: "https://medjournal.example.com/ml-imaging",
        snippet: "Convolutional neural networks are now achieving...",
        published_date: "2024-09-20",
        relevance: 0.88
      },
      ... 8 more sources
    ],
    total_found: 10,
    search_time_seconds: 2.1
  }
  error: null
  cost: $0.02
  tokens_used: 450
  execution_time_seconds: 2.5
  metadata: {
    api: "tavily",
    query_refined: "AI healthcare diagnostics 2024"
  }
}
```

**Output** (Failure):
```
WorkerOutput {
  task_id: "task_001"
  worker_id: "web_search"
  success: false
  result: null
  error: "Tavily API timeout after 30 seconds"
  cost: $0.00
  tokens_used: 0
  execution_time_seconds: 30.5
  metadata: {
    retry_count: 3,
    last_error: "Connection timeout"
  }
}
```

---

### How Different Workers Use This

**Research Worker** (web_search):
```
Input context: {query, max_results}
Output result: {sources: [...]}
```

**Analysis Worker** (content_synthesizer):
```
Input context: {research_results, brief}
Output result: {insights: [...], themes: [...], outline: {...}}
```

**Writing Worker** (article_writer):
```
Input context: {outline, research_results, brief}
Output result: {content: "# Title\n\n...", word_count: 2150}
```

**Quality Worker** (fact_checker):
```
Input context: {article_content, research_results}
Output result: {verified_claims: 42, unverified: 3, accuracy: 0.93}
```

---

### Why This Standard Interface Matters

✅ **Consistency**: All workers look the same to the Orchestrator
✅ **Modularity**: Easy to add new workers
✅ **Testing**: Easy to mock workers for testing
✅ **Monitoring**: Unified metrics (cost, time, success rate)
✅ **Error Handling**: Consistent error reporting

---

## 📤 Result Schema - Final Output

### Purpose

After all the work is done, the **Merger agent** packages everything into a **FinalOutput** that contains:
- The generated article
- Quality metrics
- All sources cited
- Execution statistics

This is what the **user receives**.

---

### FinalOutput Structure
```
FinalOutput
│
├─ Identification
│  ├─ request_id: "req_abc123" (from user's Brief)
│  └─ execution_id: "exec_20241125_143022" (this workflow run)
│
├─ Article (ArticleResult)
│  ├─ title: "AI Trends in Healthcare 2024"
│  ├─ summary: "Comprehensive overview..."
│  ├─ content: "# Introduction\n\n..." (full Markdown)
│  ├─ word_count: 2,150
│  ├─ reading_time_minutes: 9
│  ├─ sections: ["Introduction", "Current Trends", ...]
│  ├─ keywords: ["AI", "healthcare", "diagnosis"]
│  └─ citations_count: 15
│
├─ Quality (QualityScore)
│  ├─ overall: 88.5
│  ├─ accuracy: 92.0
│  ├─ completeness: 87.0
│  ├─ readability: 85.0
│  ├─ citations: 95.0
│  └─ seo: 82.0
│
├─ Sources (List of Source)
│  ├─ [1] {title, url, type, relevance}
│  ├─ [2] {title, url, type, relevance}
│  └─ ... 15 sources total
│
├─ Metrics (ExecutionMetrics)
│  ├─ total_duration_seconds: 920 (15 min 20 sec)
│  ├─ total_cost: $2.35
│  ├─ total_tokens: 12,500
│  ├─ total_tasks: 8
│  ├─ successful_tasks: 8
│  ├─ failed_tasks: 0
│  ├─ iteration_count: 1
│  └─ workers_used: [list of 8 workers]
│
├─ Status: "completed"
│
└─ System Information
   ├─ system_notes: "Generated in standard mode..."
   ├─ warnings: [] (empty if no warnings)
   └─ created_at: 2024-11-25 14:45:20
```

---

### Article Result Details

The **ArticleResult** is the actual content generated:

**Title**:
```
"AI Trends Transforming Healthcare in 2024"
```

**Summary** (50-500 characters):
```
"Comprehensive overview of how artificial intelligence is revolutionizing 
healthcare through improved diagnostics, patient care, and medical research. 
Explores current applications, challenges, and future directions."
```

**Content** (Markdown format):
```markdown
# AI Trends Transforming Healthcare in 2024

## Introduction

Artificial intelligence is revolutionizing healthcare at an unprecedented 
pace. From diagnostic accuracy to personalized treatment plans, AI 
technologies are reshaping how medical professionals deliver care and 
how patients experience treatment [1].

## Current Applications

### Medical Diagnosis

Recent studies show that AI diagnostic systems now achieve 92% accuracy 
in detecting certain cancers, surpassing human performance in specific 
contexts [2]. Convolutional neural networks analyze medical imaging data 
to identify patterns invisible to the human eye [3].

### Patient Care Automation

AI-powered systems are streamlining patient care through:
- Automated scheduling and triage [4]
- Predictive analytics for patient deterioration [5]
- Personalized treatment recommendations [6]

[... continues for 2,150 words ...]

## References

[1] Healthcare AI Report 2024, HealthTech Journal
[2] Johnson et al., "CNN Performance in Cancer Detection", Nature Medicine
[... 15 sources total ...]
```

**Metadata**:
- Word count: 2,150 (matches target of 2,000)
- Reading time: 9 minutes (at 240 words/min)
- Sections: 6 main sections
- Keywords: AI, healthcare, diagnosis, treatment, machine learning
- Citations: 15 sources properly referenced

---

### Quality Score Breakdown

**Overall: 88.5/100** (Excellent)

Individual scores:

**Accuracy: 92/100**
- 45 claims made
- 42 verified against sources
- 3 general statements (not requiring verification)
- Verification rate: 93%

**Completeness: 87/100**
- Covers all major aspects of topic
- Addresses user's requirements
- Balanced coverage
- Minor: Could expand on future predictions

**Readability: 85/100**
- Flesch Reading Ease: 62 (college level)
- Clear structure with headers
- Good paragraph length
- Technical terms explained
- Minor: Some sentences could be shorter

**Citations: 95/100**
- 15 sources cited (exceeds minimum of 10)
- All claims properly attributed
- Diverse source types (web, academic, news)
- Proper citation format
- Minor: One claim could use additional source

**SEO: 82/100**
- Keywords well distributed
- Headers optimized
- Meta description present
- Good for search engines
- Minor: Could use more internal linking opportunities

**Grammar: 90/100**
- Excellent grammar throughout
- Consistent tone (professional)
- No spelling errors
- Minor: 2 comma splice opportunities

---

### Sources List Example
```
Source [1]:
├─ Title: "AI in Healthcare: 2024 Comprehensive Report"
├─ URL: https://healthtech.example.com/ai-report-2024
├─ Type: Web Article
├─ Author: Dr. Jane Smith
├─ Published: October 15, 2024
├─ Relevance: 0.95 (highly relevant)
└─ Snippet: "AI technologies are showing 40% improvement in diagnostic accuracy..."

Source [2]:
├─ Title: "Convolutional Neural Networks in Medical Imaging"
├─ URL: https://arxiv.org/abs/2024.12345
├─ Type: Academic Paper
├─ Author: Johnson et al.
├─ Published: September 20, 2024
├─ Relevance: 0.88
└─ Snippet: "Our CNN architecture achieved 92% accuracy in detecting..."

Source [3]:
├─ Title: "Latest Healthcare AI Breakthroughs"
├─ URL: https://news.example.com/healthcare-ai-2024
├─ Type: News Article
├─ Author: Medical News Today
├─ Published: November 10, 2024
├─ Relevance: 0.82
└─ Snippet: "Three major hospitals have implemented AI diagnostic systems..."

... 12 more sources ...

Sources by Type:
Web Articles: 8
Academic Papers: 4
News Articles: 3

Average Relevance: 0.87
```

---

### Execution Metrics Explained

**Total Duration: 920 seconds (15 min 20 sec)**
- Research Phase: 5 min
- Analysis Phase: 2 min
- Writing Phase: 6 min
- Quality Phase: 4 min
- Overhead: ~1 min

**Total Cost: $2.35**
```
Breakdown:
Research workers:    $0.50
Analysis workers:    $0.30
Writing workers:     $0.80
Quality workers:     $0.60
Orchestration:       $0.15
Total:               $2.35

Under budget: $3.00
Savings: $0.65 (22%)
```

**Total Tokens: 12,500**
```
Input tokens:  8,200 (research context, prompts)
Output tokens: 4,300 (generated content)
```

**Tasks Executed: 8**
```
✓ web_search: COMPLETED
✓ academic_search: COMPLETED
✓ news_search: COMPLETED
✓ content_synthesizer: COMPLETED
✓ article_writer: COMPLETED
✓ fact_checker: COMPLETED
✓ editor: COMPLETED
✓ seo_optimizer: COMPLETED

Success rate: 100%
```

**Workers Used**:
1. web_search (research)
2. academic_search (research)
3. news_search (research)
4. content_synthesizer (analysis)
5. article_writer (writing)
6. fact_checker (quality)
7. editor (quality)
8. seo_optimizer (quality)

**Iterations: 1**
- First attempt met quality threshold
- No re-planning needed

---

### System Notes & Warnings

**System Notes** (informational):
```
"Generated in standard mode with balanced research depth. 
Article includes 15 high-quality sources with 93% verification rate. 
Execution completed within budget and time constraints."
```

**Warnings** (if any):
```
Example warnings (none in this case):
[ ] "Cost exceeded budget by $0.50"
[ ] "Quality below target (75% vs 80%)"
[ ] "Some citations could not be verified"
[ ] "Academic search API was unavailable"
```

---

### Status Values

**"completed"**: ✅ Everything successful
- All quality thresholds met
- No critical errors
- Full article generated

**"partial"**: ⚠️ Completed with issues
- Article generated but quality lower than target
- Some workers failed but core content exists
- User should review carefully

**"failed"**: ❌ Execution failed
- Critical error occurred
- No usable article produced
- User needs to retry

---

### How Users Receive This

**Via API** (JSON):
```json
{
  "request_id": "req_abc123",
  "execution_id": "exec_20241125_143022",
  "article": {
    "title": "...",
    "content": "...",
    "word_count": 2150,
    ...
  },
  "quality": {
    "overall": 88.5,
    ...
  },
  "sources": [...],
  "metrics": {...},
  "status": "completed"
}
```

**Via UI** (formatted display):
```
✅ Your Article is Ready!

📄 Title: AI Trends Transforming Healthcare in 2024
📊 Length: 2,150 words (9 min read)
⭐ Quality: 88.5/100 (Excellent)
📚 Sources: 15 cited

⏱️ Generated in: 15 min 20 sec
💰 Cost: $2.35

[Read Article] [Download] [Share]
```

---

## 🔄 Data Flow Example

Let's trace data through the entire system with a real example.

### User Request
```
"Write a 2000-word professional article about AI in healthcare, 
citing at least 10 academic sources, with a maximum budget of $5"
```

---

### Step 1: Brief Created
```
Brief {
  request_id: "req_abc123"
  topic: "AI in healthcare"
  content_type: "article"
  target_length: 2000
  tone_style: "professional"
  min_sources: 10
  preferred_sources: ["academic"]
  max_budget: 5.00
  min_quality_score: 0.80
}
```

---

### Step 2: AgentState Initialized
```
AgentState {
  execution_id: "exec_20241125_143022"
  current_phase: INITIALIZED
  brief: {... Brief above ...}
  current_plan: null
  all_tasks: []
  research_results: []
  writing_results: []
  quality_results: []
  total_cost: 0.00
  agent_actions: [
    {
      agent: "Controller",
      action: "initialize",
      timestamp: "14:30:00"
    }
  ]
}
```

---

### Step 3: Plan Created
```
current_phase: PLANNING

Plan {
  plan_id: "plan_001"
  steps: [
    Step 1: Research (PARALLEL)
      - web_search
      - academic_search
      - news_search
      Est: 5 min, $0.50
    
    Step 2: Analysis (SEQUENTIAL)
      - content_synthesizer
      Est: 2 min, $0.30
    
    Step 3: Writing (SEQUENTIAL)
      - article_writer
      Est: 6 min, $0.90
    
    Step 4: Quality (PARALLEL)
      - fact_checker
      - editor
      - citation_formatter
      Est: 4 min, $0.70
  ]
  total_steps: 4
  estimated_time: 17 min
  estimated_cost: $2.40
}

state.current_plan = Plan
state.agent_actions += "Planner: create_plan"
```

---

### Step 4: Execution Begins
```
current_phase: EXECUTING

STEP 1 - Research Phase:

Task 1: web_search
├─ Input: WorkerInput {
│    context: {query: "AI healthcare 2024", max_results: 10}
│  }
└─ Output: WorkerOutput {
     success: true
     result: {sources: [8 web articles]}
     cost: $0.02
   }

Task 2: academic_search  
├─ Input: WorkerInput {
│    context: {query: "AI healthcare", years: "2020-2024"}
│  }
└─ Output: WorkerOutput {
     success: true
     result: {sources: [6 academic papers]}
     cost: $0.03
   }

Task 3: news_search
├─ Input: WorkerInput {
│    context: {query: "AI healthcare", days_back: 60}
│  }
└─ Output: WorkerOutput {
     success: true
     result: {sources: [4 news articles]}
     cost: $0.02
   }

state.research_results = [
  {worker: "web_search", sources: [8]},
  {worker: "academic_search", sources: [6]},
  {worker: "news_search", sources: [4]}
]
state.total_cost = $0.07
state.current_step_index = 1
```

---

### Step 5: Analysis
```
STEP 2 - Analysis Phase:

Task 4: content_synthesizer
├─ Input: WorkerInput {
│    context: {
│      research_results: [18 sources total],
│      brief: {topic, requirements}
│    }
│  }
└─ Output: WorkerOutput {
     success: true
     result: {
       themes: ["Diagnostics", "Patient Care", "Research"],
       key_insights: [...],
       outline: {
         sections: ["Introduction", "Current Applications", ...]
       }
     }
     cost: $0.30
   }

state.analysis_results = [{
  worker: "content_synthesizer",
  themes: [...],
  outline: {...}
}]
state.total_cost = $0.37
state.current_step_index = 2
```

---

### Step 6: Writing
```
STEP 3 - Writing Phase:

Task 5: article_writer
├─ Input: WorkerInput {
│    context: {
│      outline: {from analysis},
│      research_results: [18 sources],
│      brief: {tone: "professional", length: 2000}
│    }
│  }
└─ Output: WorkerOutput {
     success: true
     result: {
       title: "AI Trends Transforming Healthcare in 2024",
       content: "# Introduction\n\n...",  // 2150 words
       word_count: 2150,
       citations_used: 15
     }
     cost: $0.85
   }

state.writing_results = [{
  worker: "article_writer",
  content: "...",
  word_count: 2150
}]
state.total_cost = $1.22
state.current_step_index = 3
```

---

### Step 7: Quality Checks
```
STEP 4 - Quality Phase (PARALLEL):

Task 6: fact_checker
└─ Output: {
     verified_claims: 42,
     unverified_claims: 3,
     accuracy_score: 0.93
   }

Task 7: editor
└─ Output: {
     grammar_score: 0.90,
     readability_score: 0.85,
     suggestions: [...]
   }

Task 8: citation_formatter
└─ Output: {
     citations_formatted: 15,
     citation_quality: 0.95
   }

state.quality_results = [
  {worker: "fact_checker", accuracy: 0.93},
  {worker: "editor", grammar: 0.90, readability: 0.85},
  {worker: "citation_formatter", quality: 0.95}
]
state.total_cost = $1.92
state.current_step_index = 4
```

---

### Step 8: Evaluation
```
current_phase: EVALUATING

Supervisor calculates:
├─ quality_score: 0.88 (from all quality checks)
├─ completeness_score: 0.92 (topic well covered)
├─ Citations: 15 sources (exceeds minimum of 10 ✓)
├─ Length: 2150 words (meets target ✓)
└─ Decision: Quality = 0.88 > 0.80 threshold

state.quality_score = 0.88
state.completeness_score = 0.92
state.should_continue = false  // Quality good!
state.agent_actions += "Supervisor: evaluate (COMPLETE)"
```

---

### Step 9: Merging
```
current_phase: MERGING

Merger creates FinalOutput:

ArticleResult {
  title: "AI Trends Transforming Healthcare in 2024"
  summary: "Comprehensive overview..."
  content: "# Introduction\n\n..." (2150 words)
  word_count: 2150
  reading_time_minutes: 9
  citations_count: 15
}

QualityScore {
  overall: 88.5
  accuracy: 92.0
  completeness: 87.0
  readability: 85.0
  citations: 95.0
}

Sources [15 total] {
  [1] {title: "...", url: "...", type: "academic", relevance: 0.95}
  [2] {title: "...", url: "...", type: "web", relevance: 0.88}
  ...
}

ExecutionMetrics {
  total_duration_seconds: 920
  total_cost: 2.35
  total_tokens: 12500
  total_tasks: 8
  successful_tasks: 8
  workers_used: [8 workers]
}

FinalOutput {
  request_id: "req_abc123"
  execution_id: "exec_20241125_143022"
  article: {...}
  quality: {...}
  sources: [...]
  metrics: {...}
  status: "completed"
}
```

---

### Step 10: Completed
```
current_phase: COMPLETED
state.completed_at = "14:45:20"

Final State Summary:
✓ Duration: 15 min 20 sec
✓ Cost: $2.35 (under $5.00 budget)
✓ Quality: 88.5/100 (exceeds 80% threshold)
✓ Sources: 15 (exceeds 10 minimum)
✓ Length: 2150 words (meets 2000 target)
✓ All tasks completed successfully
✓ No errors or warnings
```

---

### User Receives
```json
{
  "request_id": "req_abc123",
  "status": "completed",
  "article": {
    "title": "AI Trends Transforming Healthcare in 2024",
    "content": "...",
    "word_count": 2150
  },
  "quality": {
    "overall": 88.5
  },
  "sources": [15 sources],
  "metrics": {
    "cost": 2.35,
    "duration": 920
  }
}
```

---

## ✅ Validation & Best Practices

### Automatic Validations

**Pydantic validates automatically:**
```
✓ Type checking: topic must be string, not integer
✓ Range checking: target_length must be 500-10,000
✓ Pattern checking: research_depth must be "light|standard|deep"
✓ Required fields: cannot omit topic
✓ List lengths: keywords max 20 items
✓ Enum values: content_type must be valid enum
```

**Example Error**:
```
Try to create Brief with target_length = 100:

ValidationError:
  Field: target_length
  Error: Input should be greater than or equal to 500
  Got: 100
  Expected: >= 500
```

---

### Best Practices

#### 1. Always Use Type Hints
```python
# ❌ Bad
def process(data):
    ...

# ✅ Good  
def process(brief: Brief) -> Plan:
    ...
```

#### 2. Validate at Boundaries
```python
# ✅ API endpoint automatically validates
@app.post("/research")
async def create_research(brief: Brief):
    # brief is guaranteed valid here
    ...
```

#### 3. Use Immutable Models Where Appropriate
```python
# Sources shouldn't change after creation
class Source(BaseModel):
    class Config:
        frozen = True  # Immutable
```

#### 4. Leverage Helper Methods
```python
# ✅ Better than manual tracking
state.add_cost(0.50)  # vs state.total_cost += 0.50
state.add_agent_action("Planner", "create_plan")
```

#### 5. Handle Validation Errors Gracefully
```python
from pydantic import ValidationError

try:
    brief = Brief(**user_input)
except ValidationError as e:
    # Return helpful error to user
    return {
        "error": "Invalid input",
        "details": e.errors()
    }
```

---

## 📚 Summary

### Schema Hierarchy
```
Brief (Input)
    ↓
AgentState (Created with Brief)
    ↓
Plan (Created by Planner)
    ├─ PlanStep
    └─ WorkerDefinition
    ↓
Task (Created by Orchestrator)
    ├─ WorkerInput (to worker)
    └─ WorkerOutput (from worker)
    ↓
Results stored in AgentState
    ├─ research_results
    ├─ analysis_results
    ├─ writing_results
    └─ quality_results
    ↓
FinalOutput (Created by Merger)
    ├─ ArticleResult
    ├─ QualityScore
    ├─ Source []
    └─ ExecutionMetrics
```

### Key Takeaways

1. **Brief** = What user wants
2. **Plan** = How to do it
3. **Task** = Individual worker execution
4. **AgentState** = Central coordination & tracking
5. **Worker I/O** = Standardized worker interface
6. **FinalOutput** = Complete result package

### Schema Files Location
```
src/schemas/
├─ brief.py          - User input
├─ plan.py           - Execution planning
├─ task.py           - Task tracking
├─ state.py          - Workflow state
├─ worker.py         - Worker I/O
├─ result.py         - Final output
└─ enums.py          - All enums & constants
```

---

## 🔗 Related Documentation

- **[Architecture](./02_ARCHITECTURE.md)** - How schemas fit in system
- **[Agent Specifications](./04_AGENTS.md)** - How agents use schemas
- **[Worker Specifications](./05_WORKERS.md)** - How workers use schemas
- **[Development Guide](./09_DEVELOPMENT.md)** - Working with schemas in code

For **technical implementation details**, see source code in `src/schemas/`

---

**Document Version**: 1.0  
**Last Updated**: November 25, 2024  
**Audience**: Users, Developers, Stakeholders

---

END OF DATA MODELS DOCUMENTATION