# Agent Specifications - AutoResearch AI

**Last Updated**: November 25, 2024  
**Version**: 1.0  
**Status**: Sprint 1 - Complete (All 7 agents implemented)

---

## 📋 Table of Contents

1. [Introduction](#introduction)
2. [Agent Architecture](#agent-architecture)
3. [Controller Agent](#controller-agent)
4. [State Manager Agent](#state-manager-agent)
5. [Planner Agent](#planner-agent)
6. [Strategy Agent](#strategy-agent)
7. [Orchestrator Agent](#orchestrator-agent)
8. [Supervisor Agent](#supervisor-agent)
9. [Merger Agent](#merger-agent)
10. [Agent Communication](#agent-communication)
11. [Decision Making](#decision-making)

---

## 🎯 Introduction

### What Are Agents?

**Agents** are autonomous components that perform specific roles in the workflow. Think of them as **specialized team members** working together:
```
Controller    = Project Manager (coordinates everything)
Planner       = Strategist (creates the plan)
Strategy      = Optimizer (makes plan efficient)
Orchestrator  = Executor (runs the plan)
Supervisor    = Quality Inspector (checks results)
Merger        = Editor (packages final output)
State Manager = Secretary (tracks everything)
```

### Why Multiple Agents?

**Instead of one big LLM doing everything:**

❌ Single LLM Approach:
```
User Request → LLM → Output
- Shallow analysis
- No verification
- One-size-fits-all
```

✅ Multi-Agent Approach:
```
User Request → 
    Controller (orchestrate) →
        Planner (strategize) →
            Orchestrator (execute) →
                Supervisor (verify) →
                    Merger (finalize) →
                        Quality Output

Benefits:
✓ Specialized expertise
✓ Quality checkpoints
✓ Iterative improvement
✓ Transparent process
```

---

### Agent Categories
```
┌─────────────────────────────────────────────────────┐
│                    META AGENTS                       │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ORCHESTRATION                                       │
│  ├─ Controller (main coordinator)                   │
│  └─ Orchestrator (task executor)                    │
│                                                      │
│  PLANNING                                            │
│  ├─ Planner (create strategy)                       │
│  └─ Strategy (optimize strategy)                    │
│                                                      │
│  EVALUATION                                          │
│  └─ Supervisor (quality control)                    │
│                                                      │
│  OUTPUT                                              │
│  └─ Merger (final packaging)                        │
│                                                      │
│  SUPPORT                                             │
│  └─ State Manager (state tracking)                  │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## 🏗️ Agent Architecture

### Standard Agent Pattern

Every agent follows this structure:
```
Agent Class
├─ __init__()
│  Initialize agent (if needed)
│
├─ main_method(state: AgentState)
│  Primary functionality
│  │
│  ├─ 1. Record action
│  ├─ 2. Read from state
│  ├─ 3. Do the work
│  ├─ 4. Update state
│  └─ 5. Return result
│
└─ _helper_methods()
   Private helper functions
```

### How Agents Communicate

**All communication happens through AgentState:**
```
┌──────────────┐
│ Controller   │
└──────┬───────┘
       │ Updates state.current_phase = PLANNING
       ▼
┌──────────────┐
│ Planner      │ Reads state.brief
└──────┬───────┘ Writes state.current_plan
       │
       ▼
┌──────────────┐
│ Strategy     │ Reads state.current_plan
└──────┬───────┘ Updates state.current_plan (optimized)
       │
       ▼
┌──────────────┐
│ Orchestrator │ Reads state.current_plan
└──────┬───────┘ Writes state.research_results
       │         Writes state.writing_results
       ▼

Key: Agents never call each other directly
     All data flows through shared state
```

### Agent Responsibilities

| Agent | Primary Role | Input | Output |
|-------|-------------|-------|--------|
| **Controller** | Workflow coordinator | Brief | FinalOutput |
| **State Manager** | State tracking | - | AgentState |
| **Planner** | Create execution plan | Brief | Plan |
| **Strategy** | Optimize plan | Plan | Optimized Plan |
| **Orchestrator** | Execute plan | Plan | Results in state |
| **Supervisor** | Quality evaluation | State | Decision |
| **Merger** | Package output | State | FinalOutput |

---

## 🎮 Controller Agent

### Role
The **Controller** is the **main orchestrator** - the entry point for all workflows. Like a project manager, it coordinates all other agents.

### Responsibilities
```
1. INITIALIZE WORKFLOW
   ├─ Receive user's Brief
   ├─ Create AgentState
   └─ Set phase to INITIALIZED

2. COORDINATE AGENTS
   ├─ Call State Manager
   ├─ Call Planner
   ├─ Call Strategy
   ├─ Call Orchestrator
   ├─ Call Supervisor
   └─ Call Merger (or loop back)

3. HANDLE ERRORS
   ├─ Catch any failures
   ├─ Log errors
   └─ Graceful degradation

4. RETURN RESULT
   └─ Deliver FinalOutput to user
```

### Workflow Control
```
Controller.execute(brief)
    │
    ├─► Initialize
    │   ├─ Create AgentState with brief
    │   ├─ Phase: INITIALIZED
    │   └─ Record action
    │
    ├─► Planning Phase
    │   ├─ Phase: PLANNING
    │   ├─ Call Planner → creates Plan
    │   └─ Phase: STRATEGY
    │       └─ Call Strategy → optimizes Plan
    │
    ├─► Execution Phase
    │   ├─ Phase: EXECUTING
    │   ├─ Call Orchestrator → runs workers
    │   └─ Collect results
    │
    ├─► Evaluation Phase
    │   ├─ Phase: EVALUATING
    │   ├─ Call Supervisor → check quality
    │   └─ Decision?
    │       ├─ CONTINUE → back to Planning
    │       └─ COMPLETE → proceed to Merging
    │
    ├─► Merging Phase
    │   ├─ Phase: MERGING
    │   ├─ Call Merger → create FinalOutput
    │   └─ Phase: COMPLETED
    │
    └─► Return FinalOutput
```

### Decision Points

**Controller makes these decisions:**

1. **Start new workflow?** → Yes, create state
2. **Any critical errors?** → Yes, abort and return error
3. **Max iterations reached?** → Yes, force complete
4. **Supervisor says continue?** → Yes, re-plan
5. **Supervisor says complete?** → Yes, merge and return

### Example Flow

**Simple Success Case:**
```
User submits Brief
    ↓
Controller receives
    ↓
Initialize: Create state
    ↓
Planning: Planner creates plan
    ↓
Strategy: Optimize plan
    ↓
Executing: Orchestrator runs workers
    ↓
Evaluating: Supervisor checks quality (88% ✓)
    ↓
Decision: COMPLETE
    ↓
Merging: Merger creates output
    ↓
Controller returns FinalOutput to user

Total time: 15 minutes
```

**Iteration Case:**
```
Initialize → Plan → Execute → Evaluate
    ↓
Quality: 65% (below 80% threshold)
    ↓
Supervisor: CONTINUE
    ↓
Re-plan with more sources
    ↓
Execute again → Evaluate
    ↓
Quality: 87% ✓
    ↓
Supervisor: COMPLETE
    ↓
Merge → Return

Total iterations: 2
Total time: 28 minutes
```

### Error Handling
```
Try:
    Execute workflow
    
Catch WorkerError:
    ├─ Log error to state
    ├─ Attempt recovery
    └─ Continue if possible

Catch PlanningError:
    ├─ Try simpler plan
    └─ Or return partial result

Catch BudgetExceededError:
    ├─ Stop execution
    └─ Return what we have

Catch TimeoutError:
    ├─ Complete current step
    └─ Return partial result

Finally:
    Always return something to user
    (FinalOutput or error response)
```

---

## 📊 State Manager Agent

### Role
The **State Manager** manages the **AgentState** - the central source of truth for the workflow. Like a secretary keeping meticulous records.

### Responsibilities
```
1. STATE INITIALIZATION
   └─ Create new AgentState from Brief

2. PHASE MANAGEMENT
   ├─ Transition between workflow phases
   ├─ Validate transitions
   └─ Track phase history

3. METRICS TRACKING
   ├─ Track costs (add_cost)
   ├─ Track tokens (add_tokens)
   └─ Calculate duration

4. ACTION LOGGING
   └─ Record all agent actions

5. STATE SNAPSHOTS
   └─ Create snapshots for debugging
```

### Phase Transitions

**Valid phase transitions:**
```
INITIALIZED
    ↓ (only valid next phase)
PLANNING
    ↓
STRATEGY
    ↓
EXECUTING
    ↓
EVALUATING
    ↓ (two possible paths)
    ├─► RE_PLANNING (if continue)
    │   └─► back to PLANNING
    │
    └─► MERGING (if complete)
        ↓
        COMPLETED ✓

Any phase can go to:
    └─► FAILED (on critical error)
```

**Example:**
```
state.current_phase = INITIALIZED
    ↓
StateManager.transition_phase(state, PLANNING)
    ✓ Valid transition
    state.current_phase = PLANNING
    ↓
StateManager.transition_phase(state, EXECUTING)
    ✗ Invalid (must go through STRATEGY first)
    Raises: InvalidTransitionError
```

### Cost Tracking
```
All costs flow through State Manager:

Worker 1 completes: add_cost($0.02)
    state.total_cost = $0.02

Worker 2 completes: add_cost($0.03)
    state.total_cost = $0.05

Worker 3 completes: add_cost($0.85)
    state.total_cost = $0.90

Check budget:
    if state.total_cost > brief.max_budget:
        raise BudgetExceededError

Final:
    state.total_cost = $2.35
```

### Action Recording

**Every agent action is logged:**
```
state.add_agent_action(
    agent_name="Planner",
    action="create_plan",
    details={
        "steps": 4,
        "estimated_cost": 2.20,
        "estimated_time": 900
    }
)

Later, can query:
actions = state.get_actions_by_agent("Planner")
# Returns all Planner actions
```

**Why this matters:**
- 🔍 Debugging: "What did Planner do?"
- 📊 Analytics: "How long does planning take?"
- ✅ Audit: "Who made this decision?"
- 🐛 Error tracking: "Where did it fail?"

### State Snapshots

**For debugging and analysis:**
```
Create snapshot at key points:

Snapshot 1: After planning
├─ Phase: PLANNING
├─ Plan created: 4 steps
└─ Cost so far: $0.00

Snapshot 2: After execution
├─ Phase: EXECUTING
├─ Tasks completed: 8
└─ Cost so far: $1.90

Snapshot 3: After evaluation
├─ Phase: EVALUATING
├─ Quality score: 0.88
└─ Decision: COMPLETE

Can compare snapshots to understand workflow
```

---

## 📝 Planner Agent

### Role
The **Planner** creates the **execution plan** by analyzing the Brief and determining what needs to be done. Like an architect designing a building.

### Responsibilities
```
1. ANALYZE BRIEF
   ├─ Understand topic complexity
   ├─ Identify requirements
   └─ Determine constraints

2. SELECT WORKERS
   ├─ Choose appropriate workers
   ├─ Based on topic and requirements
   └─ Consider budget/time

3. CREATE STEPS
   ├─ Group workers into logical steps
   ├─ Determine execution order
   └─ Set dependencies

4. ESTIMATE RESOURCES
   ├─ Estimate time per step
   ├─ Estimate cost per step
   └─ Calculate totals
```

### How Planning Works
```
INPUT: Brief
├─ Topic: "AI in healthcare 2024"
├─ Content Type: Article
├─ Length: 2000 words
├─ Research Depth: Standard
├─ Min Sources: 10
└─ Max Budget: $5.00

ANALYSIS:
├─ Topic Complexity: MEDIUM (0.6)
│  (Healthcare = specialized domain)
│
├─ Research Needs:
│  ✓ Web search (general info)
│  ✓ Academic search (medical papers)
│  ✓ News search (recent developments)
│
├─ Analysis Needs:
│  ✓ Synthesize multiple sources
│
├─ Writing Needs:
│  ✓ Professional article
│  ✓ With citations
│
└─ Quality Needs:
   ✓ Fact-checking (medical claims)
   ✓ Grammar check
   ✓ Citation formatting

OUTPUT: Plan with 4 steps
```

### Step Creation Logic

**Step 1: Research Phase (PARALLEL)**
```
Why parallel? All research can happen simultaneously
Workers needed:
├─ web_search (general articles)
├─ academic_search (medical papers)
└─ news_search (recent news)

Execution: All 3 run at once
Time: 5 minutes (longest worker)
Cost: $0.50 (sum of all)
```

**Step 2: Analysis Phase (SEQUENTIAL)**
```
Why sequential? Needs all research first
Workers needed:
└─ content_synthesizer (combine findings)

Execution: Runs after Step 1 complete
Dependencies: ["step_1"]
Time: 2 minutes
Cost: $0.30
```

**Step 3: Writing Phase (SEQUENTIAL)**
```
Why sequential? Needs analysis first
Workers needed:
└─ article_writer (create article)

Execution: Runs after Step 2 complete
Dependencies: ["step_2"]
Time: 6 minutes
Cost: $0.90
```

**Step 4: Quality Phase (PARALLEL)**
```
Why parallel? Independent checks
Workers needed:
├─ fact_checker (verify claims)
├─ editor (grammar/style)
└─ citation_formatter (format citations)

Execution: All 3 run at once after Step 3
Dependencies: ["step_3"]
Time: 4 minutes
Cost: $0.70
```

**Total Plan:**
- Steps: 4
- Workers: 8
- Time: 17 minutes
- Cost: $2.40

### Complexity-Based Planning

**Low Complexity (0.0 - 0.4):**
```
Topic: "What is Python?"
Plan:
├─ Step 1: Light research (1 worker)
├─ Step 2: Simple article (1 worker)
└─ Step 3: Basic check (1 worker)
Total: 3 steps, 3 workers, $1.00
```

**Medium Complexity (0.4 - 0.7):**
```
Topic: "AI in healthcare"
Plan:
├─ Step 1: Standard research (3 workers, parallel)
├─ Step 2: Analysis (1 worker)
├─ Step 3: Writing (1 worker)
└─ Step 4: Quality (3 workers, parallel)
Total: 4 steps, 8 workers, $2.40
```

**High Complexity (0.7 - 1.0):**
```
Topic: "Comparative analysis of quantum computing"
Plan:
├─ Step 1: Deep research (5 workers, parallel)
├─ Step 2: Multi-source analysis (2 workers)
├─ Step 3: Comprehensive writing (3 workers)
├─ Step 4: Rigorous quality (5 workers, parallel)
└─ Step 5: Academic review (2 workers)
Total: 5 steps, 17 workers, $6.00
```

### Worker Selection Criteria

**How Planner chooses workers:**

1. **Topic Analysis**
```
Topic contains "academic", "research", "study"?
→ Include academic_search

Topic is recent/trending?
→ Include news_search

Topic is technical?
→ Include specialized_scraper
```

2. **Brief Requirements**
```
preferred_sources: ["academic"]?
→ Prioritize academic_search

min_sources: 15?
→ Add more research workers

tone: "academic"?
→ Include citation_formatter
```

3. **Budget Constraints**
```
Max budget: $2.00?
→ Use fewer workers
→ Choose cheaper models

Max budget: $10.00?
→ Can use all workers
→ Use best models
```

4. **Time Constraints**
```
Max time: 10 minutes?
→ Maximize parallelization
→ Skip optional workers

Max time: 60 minutes?
→ Can do thorough analysis
→ Include all quality checks
```

---

## ⚡ Strategy Agent

### Role
The **Strategy** agent optimizes the plan created by Planner. Like an efficiency consultant improving a business process.

### Responsibilities
```
1. ANALYZE PLAN
   ├─ Review step structure
   ├─ Check resource estimates
   └─ Identify bottlenecks

2. OPTIMIZE PARALLELIZATION
   ├─ Find parallel opportunities
   ├─ Reduce sequential dependencies
   └─ Maximize concurrent execution

3. APPLY CONSTRAINTS
   ├─ Check budget limits
   ├─ Check time limits
   └─ Adjust if needed

4. BALANCE TRADE-OFFS
   └─ Cost vs Quality vs Speed
```

### Optimization Strategies

#### 1. Parallelization Optimization

**Before:**
```
Step 1: Research
├─ Worker A (5 min)
├─ Worker B (5 min)  } Sequential: 15 minutes
└─ Worker C (5 min)
```

**After:**
```
Step 1: Research (PARALLEL)
├─ Worker A (5 min) ┐
├─ Worker B (5 min) ├─ Parallel: 5 minutes
└─ Worker C (5 min) ┘
```

**Time saved: 10 minutes (67% faster)**

#### 2. Budget Optimization

**Before:**
```
Plan Cost: $5.50
User Budget: $5.00
Status: EXCEEDS BUDGET ❌
```

**Optimizations:**
```
1. Use Haiku instead of Sonnet for simple tasks
   Savings: $0.30

2. Reduce research workers from 5 to 3
   Savings: $0.20

3. Skip optional SEO optimizer
   Savings: $0.15
   
New Cost: $4.85 ✓ (under budget)
```

#### 3. Time Optimization

**Before:**
```
Plan Time: 25 minutes
User Limit: 20 minutes
Status: EXCEEDS LIMIT ❌
```

**Optimizations:**
```
1. Parallel execution where possible
   Savings: 5 minutes

2. Remove optional plagiarism check
   Savings: 3 minutes

3. Use faster model for simple tasks
   Savings: 2 minutes

New Time: 15 minutes ✓ (under limit)
```

#### 4. Quality Optimization
```
If user sets high quality threshold (>0.90):

Add:
├─ Additional fact-checker
├─ Academic review worker
└─ Citation quality verifier

Accept:
├─ Higher cost (+$1.00)
└─ Longer time (+5 min)

Result: Better quality
```

### Trade-off Balancing

**The Triangle:**
```
        Quality
         /\
        /  \
       /    \
      /      \
     /________\
  Cost      Speed

You can optimize for 2, but not all 3:
- High Quality + Fast = Expensive
- High Quality + Cheap = Slow
- Fast + Cheap = Low Quality
```

**Example Decisions:**

**Budget Priority:**
```
User Budget: $2.00 (strict)
Original Plan: $2.50

Strategy:
├─ Reduce workers (quality ↓)
├─ Use cheaper models (speed ↓)
└─ Meet budget: $1.95 ✓

Trade-off: Lower quality but affordable
```

**Quality Priority:**
```
User Quality: 0.90 (strict)
Original Plan Quality: 0.85

Strategy:
├─ Add verification workers (cost ↑)
├─ Deep research (time ↑)
└─ Meet quality: 0.92 ✓

Trade-off: Higher cost and slower but excellent quality
```

**Speed Priority:**
```
User Time: 10 minutes (strict)
Original Plan: 18 minutes

Strategy:
├─ Maximize parallelization (cost ↑)
├─ Remove optional steps (quality ↓)
└─ Meet time: 9 minutes ✓

Trade-off: Higher cost and lower quality but fast
```

### Optimization Example

**Original Plan (from Planner):**
```
Steps: 5
Workers: 12
Time: 28 minutes (too slow)
Cost: $4.20 (acceptable)
Parallelization: 40%

Issues:
❌ Exceeds 20-minute time limit
⚠️ Could be more parallel
```

**Optimized Plan (by Strategy):**
```
Steps: 4 (merged Step 4 & 5)
Workers: 10 (removed 2 optional)
Time: 17 minutes ✓ (under limit)
Cost: $3.60 (under budget)
Parallelization: 60% (improved)

Improvements:
✓ Meets time constraint
✓ More efficient
✓ Lower cost
✓ Quality maintained (0.85 → 0.83)
```

**Changes Made:**
1. Merged analysis and synthesis steps
2. Removed optional social_media_search
3. Removed optional plagiarism_checker
4. Parallelized quality checks
5. Used Haiku for simple summarization

---

## 🎯 Orchestrator Agent

### Role
The **Orchestrator** executes the plan by dispatching tasks to workers and collecting results. Like a construction foreman managing workers on site.

### Responsibilities
```
1. EXECUTE PLAN
   └─ Run each step in order

2. DISPATCH TASKS
   ├─ Create tasks for workers
   ├─ Execute parallel tasks simultaneously
   └─ Execute sequential tasks in order

3. COLLECT RESULTS
   ├─ Gather worker outputs
   ├─ Store in appropriate state fields
   └─ Track metrics (cost, time)

4. HANDLE FAILURES
   ├─ Retry failed workers
   ├─ Skip optional workers
   └─ Continue workflow
```

### Execution Flow
```
Orchestrator receives optimized Plan
    ↓
For each step in plan:
    │
    ├─ Get workers for this step
    │
    ├─ Check execution mode
    │   ├─ PARALLEL? → Execute all simultaneously
    │   └─ SEQUENTIAL? → Execute one by one
    │
    ├─ For each worker:
    │   ├─ Create Task
    │   ├─ Create WorkerInput
    │   ├─ Call worker.execute()
    │   ├─ Receive WorkerOutput
    │   ├─ Update Task status
    │   ├─ Store result in state
    │   └─ Track cost & time
    │
    ├─ Aggregate step results
    │
    └─ Continue to next step
    ↓
All steps complete
```

### Task Creation

**For each worker, Orchestrator creates a Task:**
```
Step 1 has 3 workers:
├─ web_search
├─ academic_search
└─ news_search

Orchestrator creates 3 tasks:

Task 1:
├─ task_id: "task_001"
├─ worker_id: "web_search"
├─ status: PENDING
└─ priority: HIGH

Task 2:
├─ task_id: "task_002"
├─ worker_id: "academic_search"
├─ status: PENDING
└─ priority: HIGH

Task 3:
├─ task_id: "task_003"
├─ worker_id: "news_search"
├─ status: PENDING
└─ priority: MEDIUM
```

### Parallel Execution

**How Orchestrator handles parallel workers:**
```
Step: Research (3 workers, PARALLEL)

Orchestrator:
├─ Create WorkerInput for all 3 workers
├─ Start all 3 workers simultaneously
│  ├─ Worker 1 starts: 14:30:00
│  ├─ Worker 2 starts: 14:30:00
│  └─ Worker 3 starts: 14:30:00
├─ Wait for all to complete
│  ├─ Worker 1 completes: 14:30:03 (3 sec)
│  ├─ Worker 3 completes: 14:30:04 (4 sec)
│  └─ Worker 2 completes: 14:30:05 (5 sec)
└─ Continue when all done: 14:30:05

Step duration: 5 seconds (longest worker)
vs Sequential: 12 seconds (3+4+5)
Speedup: 2.4x faster
```

**Implementation:**
```
Sprint 1 (Mock): Loop through sequentially
Sprint 2 (Real): Use asyncio.gather() for true parallelism
```

### Sequential Execution

**How Orchestrator handles sequential workers:**
```
Step: Writing (3 workers, SEQUENTIAL)

Worker 1: introduction_writer
├─ Start: 14:30:10
├─ Complete: 14:30:13
└─ Result stored in state.writing_results

Worker 2: article_writer (uses introduction)
├─ Start: 14:30:13 (waits for Worker 1)
├─ Reads introduction from state
├─ Complete: 14:30:19
└─ Result stored in state.writing_results

Worker 3: conclusion_writer (uses article)
├─ Start: 14:30:19 (waits for Worker 2)
├─ Reads full article from state
├─ Complete: 14:30:21
└─ Result stored in state.writing_results

Step duration: 11 seconds (sum of all)
Can't parallelize: Each depends on previous
```

### Result Storage

**Orchestrator stores results by category:**
```
Research Workers → state.research_results:
├─ {worker: "web_search", sources: [8 articles]}
├─ {worker: "academic_search", sources: [6 papers]}
└─ {worker: "news_search", sources: [4 articles]}

Analysis Workers → state.analysis_results:
└─ {worker: "content_synthesizer", insights: [...], outline: {...}}

Writing Workers → state.writing_results:
└─ {worker: "article_writer", content: "...", word_count: 2150}

Quality Workers → state.quality_results:
├─ {worker: "fact_checker", accuracy: 0.92, verified: 42}
├─ {worker: "editor", grammar: 0.90, readability: 0.85}
└─ {worker: "seo_optimizer", score: 0.82, keywords: [...]}
```

### Error Handling

**What Orchestrator does when workers fail:**
```
Worker fails:
    ↓
Check if retry possible:
    ├─ Retry count < 3?
    │  ├─ Yes: Wait and retry
    │  │  ├─ Attempt 1: Failed
    │  │  ├─ Wait 2 seconds
    │  │  ├─ Attempt 2: Failed
    │  │  ├─ Wait 4 seconds
    │  │  └─ Attempt 3: Success ✓
    │  │
    │  └─ No: Mark as failed
    │
    └─ Check if worker optional:
       ├─ Optional (e.g., seo_optimizer)?
       │  └─ Skip, continue workflow
       │
       └─ Critical (e.g., article_writer)?
          ├─ Try alternative worker
          └─ Or fail entire workflow
```

**Example - Non-critical failure:**
```
Step 4: Quality checks (parallel)
├─ fact_checker: COMPLETED ✓
├─ editor: COMPLETED ✓
└─ seo_optimizer: FAILED ❌ (API timeout)

Decision: Continue anyway
├─ SEO is optional
├─ Article still has 2/3 quality checks
└─ Warning added to final output

Result: Workflow completes successfully
        with warning about missing SEO check
```

**Example - Critical failure:**
```
Step 3: Writing
└─ article_writer: FAILED ❌ (after 3 retries)

Decision: Cannot continue
├─ Article is critical output
├─ No alternative worker available
└─ Workflow must fail

Result: Return error to user
        "Unable to generate article after multiple attempts"
```

### Progress Tracking

**Orchestrator tracks progress:**
```
state.current_step_index = 0  (Step 1 of 4)
    ↓
Executing Step 1: Research
├─ Tasks: 3 total
├─ Completed: 0/3
    ↓ (worker 1 completes)
├─ Completed: 1/3
    ↓ (worker 2 completes)
├─ Completed: 2/3
    ↓ (worker 3 completes)
└─ Completed: 3/3 ✓

state.current_step_index = 1  (Step 2 of 4)
    ↓
Executing Step 2: Analysis
...

Can show user:
"Executing step 2 of 4 (50% complete)"
```

---

## 🔍 Supervisor Agent

### Role
The **Supervisor** evaluates the quality of results and decides whether to complete the workflow or iterate for improvement. Like a quality inspector deciding if a product passes inspection.

### Responsibilities
```
1. EVALUATE QUALITY
   ├─ Calculate overall quality score
   ├─ Check completeness
   └─ Verify requirements met

2. MAKE DECISION
   ├─ Quality meets threshold? → COMPLETE
   └─ Quality below threshold? → CONTINUE

3. GENERATE FEEDBACK
   └─ If continuing, explain what needs improvement

4. ENFORCE LIMITS
   └─ Check max iterations not exceeded
```

### Quality Evaluation

**What Supervisor evaluates:**
```
1. Article Quality
   ├─ Content completeness (covers topic?)
   ├─ Structure quality (well-organized?)
   └─ Length appropriate (meets target?)

2. Source Quality
   ├─ Enough sources? (meets minimum)
   ├─ Source diversity (multiple types)
   └─ Citation accuracy (properly formatted)

3. Factual Quality
   ├─ Claims verified? (fact-check results)
   ├─ Accuracy score (from fact_checker)
   └─ No contradictions

4. Writing Quality
   ├─ Grammar score (from editor)
   ├─ Readability score
   └─ Tone appropriate (matches brief)
```

### Score Calculation
```
Overall Quality Score Formula:

quality_score = (
    article_quality * 0.30 +
    source_quality * 0.25 +
    factual_quality * 0.25 +
    writing_quality * 0.20
)

Example:
├─ article_quality: 0.90 * 0.30 = 0.27
├─ source_quality: 0.85 * 0.25 = 0.21
├─ factual_quality: 0.92 * 0.25 = 0.23
└─ writing_quality: 0.88 * 0.20 = 0.18
                              ────
                              0.89 (89%)
```

**Individual Score Calculations:**

**Article Quality (0-1):**
```
completeness = sections_covered / expected_sections
length_match = min(actual_words, target_words) / target_words
structure = has_intro + has_body + has_conclusion

article_quality = (completeness + length_match + structure) / 3

Example:
├─ completeness: 5/6 = 0.83
├─ length_match: 2000/2000 = 1.00
└─ structure: 3/3 = 1.00
    → article_quality = 0.94
```

**Source Quality (0-1):**
```
count_score = min(actual_sources, min_required) / min_required
diversity = unique_source_types / total_possible_types
citation_accuracy = correct_citations / total_citations

source_quality = (count_score + diversity + citation_accuracy) / 3

Example:
├─ count_score: 15/10 = 1.00 (exceeds minimum)
├─ diversity: 3/4 = 0.75 (web, academic, news)
└─ citation_accuracy: 14/15 = 0.93
    → source_quality = 0.89
```

**Factual Quality (0-1):**
```
From fact_checker worker:
├─ verified_claims: 42
├─ unverified_claims: 3
├─ total_claims: 45

factual_quality = verified_claims / total_claims = 42/45 = 0.93
```

**Writing Quality (0-1):**
```
From editor and readability_checker:
├─ grammar_score: 0.90
├─ readability_score: 0.85
└─ tone_match: 1.00 (professional as requested)

writing_quality = (0.90 + 0.85 + 1.00) / 3 = 0.92
```

### Decision Making
```
Supervisor evaluates:

quality_score: 0.89
threshold: 0.80 (from brief.min_quality_score)

Decision Logic:
if quality_score >= threshold:
    decision = COMPLETE ✓
    should_continue = false
    feedback = null
else:
    decision = CONTINUE
    should_continue = true
    feedback = "Quality below threshold. Suggestions: ..."
```

### Iteration Decisions

**COMPLETE (Quality Good):**
```
Quality: 0.89
Threshold: 0.80
Status: EXCEEDS ✓

Decision: COMPLETE
Action: Proceed to MERGING phase
Iterations: 1 (first attempt succeeded)
```

**CONTINUE (Quality Low - First Time):**
```
Quality: 0.65
Threshold: 0.80
Status: BELOW ❌

Decision: CONTINUE
Action: RE_PLANNING phase
Feedback: "Need more academic sources and deeper analysis"
Iterations: 1 → 2
```

**CONTINUE (Quality Low - Second Time):**
```
Quality: 0.72 (improved from 0.65)
Threshold: 0.80
Status: STILL BELOW ❌

Decision: CONTINUE
Action: RE_PLANNING phase again
Feedback: "Improve fact-checking, add more verified claims"
Iterations: 2 → 3
```

**FORCE COMPLETE (Max Iterations):**
```
Quality: 0.76
Threshold: 0.80
Iterations: 3 (MAX_ITERATIONS reached)
Status: BELOW but can't iterate more

Decision: COMPLETE (forced)
Action: MERGING phase
Warning: "Quality below target but max iterations reached"
Iterations: 3 (final)
```

### Feedback Generation

**When continuing, Supervisor provides specific feedback:**
```
Quality: 0.65
Issues found:

1. Source Quality: 0.55 (too low)
   └─ Only 6 sources (need 10 minimum)

2. Factual Quality: 0.70 (borderline)
   └─ 8 unverified claims

3. Article Quality: 0.75 (acceptable but could improve)
   └─ Missing conclusion section

Feedback generated:
"Quality score 0.65 is below threshold 0.80. Improvements needed:
1. Add 4+ more sources, preferably academic
2. Verify the 8 unverified claims with fact-checker
3. Add a proper conclusion section

Suggested plan changes:
- Add academic_search worker
- Run fact_checker again after adding sources
- Ensure conclusion_writer is included"
```

### Example Evaluations

**High Quality - Complete:**
```
Article: 2150 words, well-structured ✓
Sources: 15 cited (exceeds 10 minimum) ✓
Accuracy: 92% verified ✓
Grammar: 90% ✓
Readability: 85% ✓

Scores:
├─ article_quality: 0.94
├─ source_quality: 0.89
├─ factual_quality: 0.92
└─ writing_quality: 0.88

Overall: 0.91 (91%)
Threshold: 0.80
Decision: COMPLETE ✓
```

**Medium Quality - Continue:**
```
Article: 1800 words, missing sections ⚠️
Sources: 7 cited (below 10 minimum) ❌
Accuracy: 85% verified ✓
Grammar: 88% ✓
Readability: 82% ✓

Scores:
├─ article_quality: 0.75 (incomplete)
├─ source_quality: 0.65 (not enough sources)
├─ factual_quality: 0.85 (good)
└─ writing_quality: 0.85 (good)

Overall: 0.76 (76%)
Threshold: 0.80
Decision: CONTINUE
Feedback: "Add 3+ more sources, complete missing sections"
```

**Low Quality - Continue (Urgent):**
```
Article: 1200 words, poor structure ❌
Sources: 3 cited (far below 10) ❌
Accuracy: 68% verified ❌
Grammar: 75% ⚠️
Readability: 70% ⚠️

Scores:
├─ article_quality: 0.55
├─ source_quality: 0.40
├─ factual_quality: 0.68
└─ writing_quality: 0.73

Overall: 0.58 (58%)
Threshold: 0.80
Decision: CONTINUE
Feedback: "Major improvements needed:
- Double research (need 7+ more sources)
- Re-write for better structure
- Verify all claims
- Grammar and clarity improvements"
```

---

## 📦 Merger Agent

### Role
The **Merger** creates the final output by packaging all results into a `FinalOutput` object that's delivered to the user. Like a publisher preparing a book for release.

### Responsibilities
```
1. EXTRACT ARTICLE
   └─ Get article from state.writing_results

2. CALCULATE QUALITY
   └─ Create QualityScore from state.quality_results

3. COMPILE SOURCES
   └─ Extract all sources from state.research_results

4. CALCULATE METRICS
   ├─ Total duration
   ├─ Total cost
   ├─ Total tokens
   └─ Task statistics

5. CREATE FINAL OUTPUT
   └─ Package everything into FinalOutput
```

### Output Creation Process
```
Merger receives AgentState
    ↓
1. Extract Article
   ├─ Get from state.writing_results
   ├─ Format as ArticleResult
   │  ├─ title
   │  ├─ summary
   │  ├─ content (Markdown)
   │  ├─ word_count
   │  ├─ reading_time
   │  ├─ sections
   │  └─ keywords
   │
2. Calculate Quality
   ├─ Get scores from state.quality_results
   ├─ Calculate overall score
   ├─ Format as QualityScore
   │  ├─ overall (weighted average)
   │  ├─ accuracy (from fact_checker)
   │  ├─ completeness (from analysis)
   │  ├─ readability (from editor)
   │  ├─ citations (from formatter)
   │  └─ grammar (from editor)
   │
3. Compile Sources
   ├─ Get from state.research_results
   ├─ Deduplicate
   ├─ Sort by relevance
   ├─ Format as Source[]
   │  ├─ title
   │  ├─ url
   │  ├─ type (web/academic/news)
   │  ├─ author
   │  ├─ published_date
   │  └─ relevance_score
   │
4. Calculate Metrics
   ├─ Duration: completed_at - started_at
   ├─ Cost: state.total_cost
   ├─ Tokens: state.total_tokens
   ├─ Tasks: count from state.all_tasks
   ├─ Successful: tasks with COMPLETED status
   ├─ Failed: tasks with FAILED status
   ├─ Iterations: state.iteration_count
   └─ Workers: unique worker IDs used
   │
5. Add System Info
   ├─ system_notes (if any)
   ├─ warnings (from state.warnings)
   └─ status ("completed" / "partial" / "failed")
   │
6. Create FinalOutput
   └─ Package all components together
    ↓
Return FinalOutput to Controller
```

### Article Extraction

**From state.writing_results:**
```
writing_results = [
  {
    worker: "introduction_writer",
    content: "# Introduction\n\nAI is transforming...",
    word_count: 150
  },
  {
    worker: "article_writer",
    content: "# Main Content\n\n## Section 1...",
    word_count: 1800
  },
  {
    worker: "conclusion_writer",
    content: "# Conclusion\n\nIn summary...",
    word_count: 200
  }
]

Merger combines:
├─ Concatenate all content
├─ Calculate total word count: 2150
├─ Extract sections from headers
├─ Generate summary (first paragraph)
├─ Extract keywords (from content)
├─ Calculate reading time: 2150 / 240 = 9 minutes

ArticleResult:
├─ title: "AI Trends in Healthcare 2024"
├─ summary: "AI is transforming healthcare through..."
├─ content: "# Introduction\n\nAI is transforming..." (full)
├─ word_count: 2150
├─ reading_time_minutes: 9
├─ sections: ["Introduction", "Current Applications", ...]
├─ keywords: ["AI", "healthcare", "diagnosis", ...]
└─ citations_count: 15
```

### Quality Score Calculation

**From state.quality_results:**
```
quality_results = [
  {
    worker: "fact_checker",
    accuracy: 0.92,
    verified_claims: 42,
    unverified_claims: 3
  },
  {
    worker: "editor",
    grammar_score: 0.90,
    readability_score: 0.85,
    style_score: 0.88
  },
  {
    worker: "citation_formatter",
    citation_quality: 0.95,
    proper_format: 15
  }
]

Merger calculates:
├─ accuracy: 0.92 (from fact_checker)
├─ grammar: 0.90 (from editor)
├─ readability: 0.85 (from editor)
├─ citations: 0.95 (from formatter)
├─ completeness: 0.87 (from state.completeness_score)
├─ overall: weighted average = 0.89

QualityScore:
├─ overall: 89.0
├─ accuracy: 92.0
├─ completeness: 87.0
├─ readability: 85.0
├─ citations: 95.0
├─ grammar: 90.0
└─ notes: "High-quality article with strong citations"
```

### Source Compilation

**From state.research_results:**
```
research_results = [
  {
    worker: "web_search",
    sources: [
      {title: "AI Report 2024", url: "...", relevance: 0.95},
      {title: "Healthcare Tech", url: "...", relevance: 0.88},
      ...
    ]
  },
  {
    worker: "academic_search",
    sources: [
      {title: "CNN in Medical Imaging", url: "...", relevance: 0.90},
      ...
    ]
  },
  {
    worker: "news_search",
    sources: [
      {title: "Latest AI Breakthroughs", url: "...", relevance: 0.82},
      ...
    ]
  }
]

Merger processes:
├─ Collect all sources from all workers
├─ Remove duplicates (same URL)
├─ Sort by relevance score (high to low)
├─ Format consistently
└─ Add metadata (accessed_at, source_type)

Sources [15 total]:
├─ [1] AI Report 2024 (web, relevance: 0.95)
├─ [2] CNN in Medical Imaging (academic, relevance: 0.90)
├─ [3] Healthcare Tech (web, relevance: 0.88)
└─ ...
```

### Metrics Calculation
```
From AgentState:

started_at: 2024-11-25 14:30:00
completed_at: 2024-11-25 14:45:20
total_cost: $2.35
total_tokens: 12,500

all_tasks: [8 tasks]
├─ COMPLETED: 8
├─ FAILED: 0
└─ CANCELLED: 0

iteration_count: 1

Workers used (unique):
├─ web_search
├─ academic_search
├─ news_search
├─ content_synthesizer
├─ article_writer
├─ fact_checker
├─ editor
└─ citation_formatter

ExecutionMetrics:
├─ total_duration_seconds: 920
├─ total_cost: 2.35
├─ total_tokens: 12500
├─ total_tasks: 8
├─ successful_tasks: 8
├─ failed_tasks: 0
├─ iteration_count: 1
└─ workers_used: [8 workers]
```

### System Notes Generation
```
Merger generates notes based on execution:

Standard execution:
"Generated in standard mode with balanced research depth."

With iterations:
"Generated after 2 iterations to meet quality threshold."

With warnings:
"Completed with warnings: SEO optimization unavailable."

Budget conscious:
"Completed under budget ($2.35 of $5.00 allowed)."

Time efficient:
"Completed in 15 minutes (25% under time limit)."

Combined note:
"Generated in standard mode with balanced research depth. 
Article includes 15 high-quality sources with 93% verification rate. 
Completed under budget and within time constraints."
```

### Warnings Compilation
```
From state.warnings:

If warnings exist:
├─ "Cost exceeded initial estimate by $0.50"
├─ "SEO optimizer failed (API timeout)"
└─ "One citation could not be verified"

Merger includes all in FinalOutput

If no warnings:
└─ warnings: [] (empty array)
```

### Status Determination
```
Merger determines final status:

if quality_score >= threshold and no errors:
    status = "completed" ✓

elif quality_score < threshold but max_iterations:
    status = "partial" ⚠️
    warning = "Quality below target but max iterations reached"

elif critical_error:
    status = "failed" ❌
    error = "Unable to generate article"

Status affects how user sees result:
├─ "completed": Green checkmark, full confidence
├─ "partial": Yellow warning, review recommended
└─ "failed": Red X, error message
```

### Complete Example

**Input to Merger (AgentState):**
```
AgentState after successful execution:
├─ brief: {original user request}
├─ current_phase: EVALUATING (just evaluated)
├─ research_results: [18 sources from 3 workers]
├─ writing_results: [{article with 2150 words}]
├─ quality_results: [{accuracy: 0.92}, {grammar: 0.90}, ...]
├─ quality_score: 0.89
├─ completeness_score: 0.92
├─ total_cost: $2.35
├─ total_tokens: 12500
├─ all_tasks: [8 tasks, all COMPLETED]
├─ iteration_count: 1
├─ started_at: 14:30:00
├─ completed_at: 14:45:20
└─ warnings: []
```

**Output from Merger (FinalOutput):**
```
FinalOutput {
  request_id: "req_abc123"
  execution_id: "exec_20241125_143022"
  
  article: {
    title: "AI Trends Transforming Healthcare in 2024"
    summary: "Comprehensive overview of how AI..."
    content: "# Introduction\n\n..." (2150 words)
    word_count: 2150
    reading_time_minutes: 9
    sections: ["Introduction", "Current Applications", ...]
    keywords: ["AI", "healthcare", "diagnosis", ...]
    citations_count: 15
  }
  
  quality: {
    overall: 89.0
    accuracy: 92.0
    completeness: 87.0
    readability: 85.0
    citations: 95.0
    grammar: 90.0
  }
  
  sources: [
    {title: "AI Report 2024", url: "...", type: "web", relevance: 0.95},
    {title: "CNN in Medical Imaging", url: "...", type: "academic", relevance: 0.90},
    ... 13 more sources
  ]
  
  metrics: {
    total_duration_seconds: 920
    total_cost: 2.35
    total_tokens: 12500
    total_tasks: 8
    successful_tasks: 8
    failed_tasks: 0
    iteration_count: 1
    workers_used: [8 workers]
  }
  
  status: "completed"
  system_notes: "Generated in standard mode..."
  warnings: []
  created_at: 2024-11-25 14:45:20
}
```

---

## 🔄 Agent Communication

### Communication Principles

**1. State-Based Communication:**
```
All agents share AgentState
No direct agent-to-agent calls
Read → Process → Write pattern
```

**2. Loose Coupling:**
```
Agents don't know about each other
Only know about AgentState structure
Easy to add/remove/modify agents
```

**3. Sequential Execution:**
```
Controller orchestrates order
Each agent completes before next starts
(Except workers, which can run parallel)
```

### Communication Flow
```
┌──────────────┐
│ Controller   │ Creates & owns AgentState
└──────┬───────┘
       │ state.current_phase = PLANNING
       ▼
┌──────────────┐
│ Planner      │ Reads: state.brief
└──────┬───────┘ Writes: state.current_plan
       │
       ▼
┌──────────────┐
│ Strategy     │ Reads: state.current_plan
└──────┬───────┘ Writes: state.current_plan (optimized)
       │
       ▼
┌──────────────┐
│ Orchestrator │ Reads: state.current_plan
└──────┬───────┘ Writes: state.research_results
       │                 state.writing_results
       │                 state.quality_results
       ▼
┌──────────────┐
│ Supervisor   │ Reads: state.research_results
└──────┬───────┘         state.writing_results
       │                 state.quality_results
       │         Writes: state.quality_score
       │                 state.should_continue
       │                 state.feedback
       │
       ├─► should_continue = true  → back to Planner
       │
       └─► should_continue = false → continue
           ▼
       ┌──────────────┐
       │ Merger       │ Reads: Everything in state
       └──────────────┘ Returns: FinalOutput

State is passed by reference
All agents see the same state object
Changes by one agent visible to all
```

### State Fields Used by Each Agent

| Agent | Reads From | Writes To |
|-------|-----------|-----------|
| **Controller** | - | execution_id, current_phase |
| **State Manager** | Everything | All phase transitions, metrics |
| **Planner** | brief | current_plan |
| **Strategy** | current_plan, brief | current_plan (updated) |
| **Orchestrator** | current_plan | research_results, writing_results, quality_results, all_tasks |
| **Supervisor** | All results, brief | quality_score, completeness_score, should_continue, feedback |
| **Merger** | Everything | - (returns FinalOutput) |

### Example Communication Sequence
```
1. Controller creates state
   state.execution_id = "exec_20241125_143022"
   state.brief = {user request}
   state.current_phase = INITIALIZED

2. Planner reads & writes
   reads: state.brief
   creates plan
   writes: state.current_plan = {4 steps, 8 workers}
   adds action: "Planner created plan"

3. Strategy reads & writes
   reads: state.current_plan, state.brief.max_budget
   optimizes plan
   writes: state.current_plan = {optimized}
   adds action: "Strategy optimized plan"

4. Orchestrator reads & writes
   reads: state.current_plan
   executes workers
   writes: state.research_results = [{worker1}, {worker2}, ...]
          state.writing_results = [{article}]
          state.quality_results = [{scores}]
          state.all_tasks = [task1, task2, ...]
          state.total_cost += costs
   adds actions: "Orchestrator executed step 1", ...

5. Supervisor reads & writes
   reads: state.research_results
          state.writing_results
          state.quality_results
          state.brief.min_quality_score
   calculates quality
   writes: state.quality_score = 0.89
          state.completeness_score = 0.92
          state.should_continue = false (quality good!)
   adds action: "Supervisor evaluated quality"

6. Merger reads
   reads: Everything in state
   creates FinalOutput
   returns to Controller
```

---

## 🤔 Decision Making

### Key Decision Points

**1. Controller: Should we start?**
```
Checks:
├─ Is Brief valid? → Yes, proceed
├─ Any system errors? → No, proceed
└─ Within rate limits? → Yes, proceed

Decision: START WORKFLOW
```

**2. Planner: What workers do we need?**
```
Analyzes:
├─ Topic complexity → MEDIUM (0.6)
├─ Research depth → STANDARD
├─ User requirements → 10+ sources, professional tone
└─ Budget/time constraints → $5.00, 20 minutes

Decision: 
├─ Research: web, academic, news (parallel)
├─ Analysis: synthesizer
├─ Writing: article_writer
└─ Quality: fact_checker, editor, formatter (parallel)

Total: 4 steps, 8 workers
```

**3. Strategy: How do we optimize?**
```
Checks:
├─ Can we parallelize more? → Yes (2 parallel steps)
├─ Over budget? → No ($2.40 < $5.00)
├─ Over time? → No (17 min < 20 min)
└─ Any unnecessary workers? → No

Decision: APPROVE PLAN (no changes needed)
```

**4. Orchestrator: How do we execute?**
```
For each step:
├─ Execution mode?
│  ├─ PARALLEL → asyncio.gather (Sprint 2)
│  └─ SEQUENTIAL → one by one
│
├─ Worker failed?
│  ├─ Critical worker → Retry 3x or fail
│  └─ Optional worker → Skip and continue
│
└─ Continue to next step?
   ├─ All critical workers succeeded → Yes
   └─ Critical worker failed after retries → No, abort

Decisions made: ~8 (one per worker)
```

**5. Supervisor: Should we continue or complete?**
```
Evaluates:
├─ quality_score: 0.89
├─ threshold: 0.80
├─ Status: 0.89 >= 0.80 → EXCEEDS ✓

Decision: COMPLETE
├─ should_continue = false
├─ feedback = null
└─ Proceed to MERGING

Alternative (if quality low):
├─ quality_score: 0.72
├─ threshold: 0.80
├─ Status: 0.72 < 0.80 → BELOW ❌
└─ Decision: CONTINUE
    ├─ should_continue = true
    ├─ feedback = "Need more sources..."
    └─ Go back to PLANNING
```

**6. Merger: What status?**
```
Checks:
├─ quality_score >= threshold? → Yes
├─ Any critical errors? → No
├─ All required outputs present? → Yes

Decision: status = "completed" ✓

Alternative (if issues):
├─ quality_score < threshold
├─ max_iterations reached
└─ Decision: status = "partial" ⚠️
    └─ Add warning about quality
```

### Decision Matrix

| Scenario | Condition | Decision | Action |
|----------|-----------|----------|--------|
| **Start** | Brief valid | ✅ Proceed | Create state |
| **Start** | Brief invalid | ❌ Reject | Return error |
| **Planning** | High complexity | Use 15+ workers | Deep research |
| **Planning** | Low complexity | Use 5 workers | Light research |
| **Strategy** | Over budget | Optimize plan | Remove optional workers |
| **Strategy** | Under budget | Keep plan | No changes |
| **Execution** | Worker fails 3x | Critical worker? | Abort if critical |
| **Execution** | Worker fails 3x | Optional worker? | Skip and continue |
| **Evaluation** | Quality ≥ threshold | ✅ COMPLETE | Merge results |
| **Evaluation** | Quality < threshold | Iteration < max? | RE_PLAN |
| **Evaluation** | Quality < threshold | Iteration = max | Force complete |

---

## 📚 Summary

### Agent Roles Quick Reference
```
Controller    → Orchestrates entire workflow
State Manager → Manages workflow state
Planner       → Creates execution strategy
Strategy      → Optimizes for efficiency
Orchestrator  → Executes workers
Supervisor    → Ensures quality
Merger        → Packages final output
```

### Key Patterns

**1. All agents follow standard pattern:**
```
1. Record action
2. Read from state
3. Do the work
4. Update state
5. Return result
```

**2. Communication through shared state:**
```
No direct agent calls
State is single source of truth
Loose coupling enables flexibility
```

**3. Quality-driven iteration:**
```
Execute → Evaluate → Decision
├─ Quality good → Complete
└─ Quality low → Re-plan and retry
```

### Implementation Status

**Sprint 1 (Current):**
- ✅ All 7 agents implemented
- ✅ Mock implementations
- ✅ Complete test coverage
- ✅ State management working

**Sprint 2 (Next):**
- 📋 Real worker implementations
- 📋 Actual LLM calls
- 📋 True parallel execution

---

## 🔗 Related Documentation

- **[Architecture](./02_ARCHITECTURE.md)** - System design overview
- **[Data Models](./03_DATA_MODELS.md)** - Schema specifications
- **[Worker Specifications](./05_WORKERS.md)** - Worker details
- **[Workflow](./06_WORKFLOW.md)** - State machine & flow

For **implementation details**, see source code:
- `src/meta_agent/controller.py`
- `src/meta_agent/state_manager.py`
- `src/meta_agent/planner.py`
- `src/meta_agent/strategy.py`
- `src/meta_agent/orchestrator.py`
- `src/meta_agent/supervisor.py`
- `src/meta_agent/merger.py`

---

**Document Version**: 1.0  
**Last Updated**: November 25, 2024  
**Audience**: Developers, Technical Team

---

END OF AGENT SPECIFICATIONS