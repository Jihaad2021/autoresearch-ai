# Workflow & State Machine - AutoResearch AI

**Last Updated**: November 25, 2024  
**Version**: 1.0  
**Status**: Sprint 1 - Complete (State machine implemented)

---

## 📋 Table of Contents

1. [Introduction](#introduction)
2. [Workflow Overview](#workflow-overview)
3. [State Machine](#state-machine)
4. [Workflow Phases](#workflow-phases)
5. [Execution Patterns](#execution-patterns)
6. [Decision Points](#decision-points)
7. [Error Handling](#error-handling)
8. [Iteration & Re-planning](#iteration--re-planning)
9. [Complete Examples](#complete-examples)

---

## 🎯 Introduction

### What is the Workflow?

The **workflow** is the complete journey from user request to final output. It defines:
- What happens when
- Who does what
- How components interact
- What decisions are made

Think of it as a **choreographed dance** where each agent knows when to step in.

### Why a State Machine?

**State Machine Benefits:**
- ✅ Clear phases (know where we are)
- ✅ Predictable transitions (know what's next)
- ✅ Easy debugging (trace execution path)
- ✅ Resumable (can pause/resume)
- ✅ Testable (each state testable independently)

**Alternative Approaches (why we didn't use them):**

❌ **Linear Script:**
```python
# Simple but inflexible
research()
analyze()
write()
quality_check()
return_result()
# Can't handle iterations or failures
```

❌ **Event-Driven:**
```python
# Complex and unpredictable
on_event("research_complete", analyze)
on_event("analysis_complete", write)
# Hard to understand flow
```

✅ **State Machine (our choice):**
```python
# Clear, predictable, flexible
INITIALIZED → PLANNING → EXECUTING → EVALUATING → COMPLETED
# Can loop back for iterations
# Clear current state at all times
```

---

## 🗺️ Workflow Overview

### High-Level Flow
```
User Submits Brief
    ↓
┌─────────────────────────────────────────────────┐
│              INITIALIZATION                      │
│  Controller creates AgentState                  │
│  State Manager sets phase: INITIALIZED          │
└─────────────────┬───────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────┐
│              PLANNING PHASE                      │
│  Planner analyzes brief                         │
│  Creates execution plan                         │
│  Phase: PLANNING                                │
└─────────────────┬───────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────┐
│              STRATEGY PHASE                      │
│  Strategy optimizes plan                        │
│  Applies constraints                            │
│  Phase: STRATEGY                                │
└─────────────────┬───────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────┐
│              EXECUTION PHASE                     │
│  Orchestrator runs workers                      │
│  Collects results                               │
│  Phase: EXECUTING                               │
└─────────────────┬───────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────┐
│              EVALUATION PHASE                    │
│  Supervisor checks quality                      │
│  Makes decision: CONTINUE or COMPLETE?          │
│  Phase: EVALUATING                              │
└─────────────────┬───────────────────────────────┘
                  ↓
         ┌────────┴────────┐
         ↓                 ↓
    CONTINUE?         COMPLETE?
         │                 │
         ↓                 ↓
┌────────────────┐  ┌──────────────────┐
│  RE-PLANNING   │  │  MERGING PHASE   │
│  Go back to    │  │  Merger creates  │
│  PLANNING      │  │  FinalOutput     │
│  Phase:        │  │  Phase: MERGING  │
│  RE_PLANNING   │  └────────┬─────────┘
└────────┬───────┘           ↓
         │           ┌──────────────────┐
         │           │    COMPLETED     │
         │           │  Return output   │
         │           │  Phase:COMPLETED │
         │           └──────────────────┘
         │
         └──► (Loop back to PLANNING)
              Max 3 iterations
```

### Key Characteristics

**Sequential Phases:**
- Must complete one phase before next
- Cannot skip phases
- Clear checkpoints

**Conditional Branching:**
- After EVALUATING, can go two ways
- Decision based on quality score
- Enables iteration for improvement

**State Persistence:**
- State saved throughout workflow
- Can inspect at any point
- Complete audit trail

---

## 🔄 State Machine

### State Diagram
```
                    ┌──────────────┐
                    │ INITIALIZED  │ Entry point
                    └──────┬───────┘
                           ↓
                    ┌──────────────┐
                    │  PLANNING    │ Create plan
                    └──────┬───────┘
                           ↓
                    ┌──────────────┐
                    │  STRATEGY    │ Optimize plan
                    └──────┬───────┘
                           ↓
                    ┌──────────────┐
                    │  EXECUTING   │ Run workers
                    └──────┬───────┘
                           ↓
                    ┌──────────────┐
                    │ EVALUATING   │ Check quality
                    └──────┬───────┘
                           ↓
                   ┌───────┴────────┐
                   ↓                ↓
            Quality Low?      Quality Good?
                   ↓                ↓
           ┌──────────────┐  ┌──────────────┐
           │ RE_PLANNING  │  │   MERGING    │
           └──────┬───────┘  └──────┬───────┘
                  │                 ↓
                  │          ┌──────────────┐
                  │          │  COMPLETED   │ ✓ Success
                  │          └──────────────┘
                  │
                  └────► Back to PLANNING
                         (if iterations < max)
                         
                    OR
                         
                  └────► Force COMPLETED
                         (if iterations = max)
                         
             ┌──────────────┐
   ANY ────► │   FAILED     │ ✗ Critical error
   STATE     └──────────────┘
```

### Valid State Transitions

| From | To | Condition |
|------|-----|-----------|
| **-** | INITIALIZED | Workflow starts |
| INITIALIZED | PLANNING | Always |
| PLANNING | STRATEGY | Plan created |
| STRATEGY | EXECUTING | Plan optimized |
| EXECUTING | EVALUATING | Workers complete |
| EVALUATING | RE_PLANNING | Quality < threshold, iterations < max |
| EVALUATING | MERGING | Quality ≥ threshold |
| EVALUATING | COMPLETED | Iterations = max (forced) |
| RE_PLANNING | PLANNING | Ready to create new plan |
| MERGING | COMPLETED | Output created |
| **Any** | FAILED | Critical error |

### Invalid Transitions (Prevented)

❌ **Cannot skip phases:**
```
INITIALIZED → EXECUTING
Error: Must go through PLANNING and STRATEGY
```

❌ **Cannot go backwards (except re-planning):**
```
EXECUTING → PLANNING
Error: Can only go back via EVALUATING → RE_PLANNING
```

❌ **Cannot complete without evaluation:**
```
EXECUTING → COMPLETED
Error: Must evaluate quality first
```

### State Transition Code
```python
class WorkflowPhase(Enum):
    INITIALIZED = "initialized"
    PLANNING = "planning"
    STRATEGY = "strategy"
    EXECUTING = "executing"
    EVALUATING = "evaluating"
    RE_PLANNING = "re_planning"
    MERGING = "merging"
    COMPLETED = "completed"
    FAILED = "failed"

def transition_phase(state: AgentState, new_phase: WorkflowPhase):
    """Transition to new phase with validation"""
    
    current = state.current_phase
    
    # Validate transition
    if not is_valid_transition(current, new_phase):
        raise InvalidTransitionError(
            f"Cannot transition from {current} to {new_phase}"
        )
    
    # Record old phase
    state.phase_history.append({
        "from": current,
        "to": new_phase,
        "timestamp": datetime.now()
    })
    
    # Update phase
    state.current_phase = new_phase
    
    # Log action
    state.add_agent_action(
        agent_name="StateManager",
        action="transition_phase",
        details={"from": current.value, "to": new_phase.value}
    )
```

---

## 📍 Workflow Phases

### Phase 1: INITIALIZED

**Purpose**: Set up the workflow

**Duration**: < 1 second

**What Happens**:
```
1. Controller receives Brief from user
2. State Manager creates AgentState
3. Populate state with brief
4. Set execution_id
5. Set current_phase = INITIALIZED
6. Record initialization action
```

**State After Phase**:
```
AgentState {
  execution_id: "exec_20241125_143022"
  current_phase: INITIALIZED
  brief: {user's request}
  current_plan: null
  all_tasks: []
  total_cost: $0.00
  agent_actions: [
    {agent: "Controller", action: "initialize"}
  ]
}
```

**Next Phase**: Always → PLANNING

---

### Phase 2: PLANNING

**Purpose**: Create execution plan

**Duration**: 2-4 seconds

**What Happens**:
```
1. Planner analyzes brief
   ├─ Assess topic complexity
   ├─ Identify required workers
   └─ Estimate resources
   
2. Create Plan with steps
   ├─ Group workers into logical steps
   ├─ Determine execution order
   └─ Set parallelization
   
3. Calculate estimates
   ├─ Time per step
   ├─ Cost per step
   └─ Total time and cost
   
4. Store plan in state
```

**Example Plan Created**:
```
Plan {
  plan_id: "plan_001"
  complexity: 0.6
  steps: [
    Step 1: Research (3 workers, PARALLEL, 5min, $0.50)
    Step 2: Analysis (1 worker, SEQUENTIAL, 2min, $0.30)
    Step 3: Writing (1 worker, SEQUENTIAL, 6min, $0.90)
    Step 4: Quality (3 workers, PARALLEL, 4min, $0.70)
  ]
  estimated_time: 17 minutes
  estimated_cost: $2.40
}
```

**State After Phase**:
```
AgentState {
  current_phase: PLANNING
  current_plan: {plan above}
  agent_actions: [
    ...,
    {agent: "Planner", action: "create_plan", 
     details: {steps: 4, cost: 2.40}}
  ]
}
```

**Next Phase**: Always → STRATEGY

---

### Phase 3: STRATEGY

**Purpose**: Optimize the plan

**Duration**: 1-2 seconds

**What Happens**:
```
1. Strategy analyzes plan
   ├─ Check for parallelization opportunities
   ├─ Check budget constraints
   ├─ Check time constraints
   └─ Identify unnecessary workers
   
2. Apply optimizations
   ├─ Maximize parallelization
   ├─ Remove optional workers if over budget
   ├─ Adjust worker selection
   └─ Re-calculate estimates
   
3. Validate optimized plan
   ├─ Ensure constraints met
   ├─ Ensure quality maintained
   └─ Ensure feasibility
   
4. Update plan in state
```

**Optimization Example**:
```
Before:
├─ 5 steps
├─ Sequential execution: 28 minutes
├─ Cost: $3.80

After Optimization:
├─ 4 steps (merged two)
├─ Parallel execution: 17 minutes ✓
├─ Cost: $2.40 ✓
├─ Removed optional social_media worker
└─ Parallelized quality checks
```

**State After Phase**:
```
AgentState {
  current_phase: STRATEGY
  current_plan: {optimized plan}
  agent_actions: [
    ...,
    {agent: "Strategy", action: "optimize_plan",
     details: {time_saved: 11, cost_saved: 1.40}}
  ]
}
```

**Next Phase**: Always → EXECUTING

---

### Phase 4: EXECUTING

**Purpose**: Run all workers and collect results

**Duration**: 10-30 minutes (depends on plan)

**What Happens**:
```
1. Orchestrator receives optimized plan

2. For each step in plan:
   
   A. Create tasks for workers
      ├─ Task 1: worker_id, priority, status=PENDING
      ├─ Task 2: worker_id, priority, status=PENDING
      └─ ...
   
   B. Dispatch tasks based on execution mode
      
      If PARALLEL:
      ├─ Start all workers simultaneously
      ├─ Wait for all to complete
      └─ Continue when all done
      
      If SEQUENTIAL:
      ├─ Start worker 1
      ├─ Wait for completion
      ├─ Start worker 2
      └─ Continue one by one
   
   C. For each worker:
      ├─ Create WorkerInput
      ├─ Call worker.execute()
      ├─ Receive WorkerOutput
      ├─ Update task status
      ├─ Store result in state
      ├─ Add cost to total
      └─ Add tokens to total
   
   D. Handle failures
      ├─ Retry failed workers (up to 3 times)
      ├─ Skip optional workers if failed
      └─ Abort if critical worker fails
   
   E. Continue to next step

3. All steps complete
```

**Execution Timeline Example**:
```
14:30:00 - Start Step 1 (Research, PARALLEL)
  14:30:00 - web_search starts
  14:30:00 - academic_search starts
  14:30:00 - news_search starts
  14:30:03 - web_search completes ✓
  14:30:04 - news_search completes ✓
  14:30:05 - academic_search completes ✓
14:30:05 - Step 1 complete (5 seconds)

14:30:05 - Start Step 2 (Analysis, SEQUENTIAL)
  14:30:05 - content_synthesizer starts
  14:30:07 - content_synthesizer completes ✓
14:30:07 - Step 2 complete (2 seconds)

14:30:07 - Start Step 3 (Writing, SEQUENTIAL)
  14:30:07 - article_writer starts
  14:30:13 - article_writer completes ✓
14:30:13 - Step 3 complete (6 seconds)

14:30:13 - Start Step 4 (Quality, PARALLEL)
  14:30:13 - fact_checker starts
  14:30:13 - editor starts
  14:30:13 - citation_formatter starts
  14:30:17 - citation_formatter completes ✓
  14:30:18 - editor completes ✓
  14:30:18 - fact_checker completes ✓
14:30:18 - Step 4 complete (5 seconds)

Total execution: 18 seconds
```

**State After Phase**:
```
AgentState {
  current_phase: EXECUTING → EVALUATING
  current_step_index: 4 (completed all steps)
  all_tasks: [8 tasks, all COMPLETED]
  research_results: [
    {worker: "web_search", sources: [...]},
    {worker: "academic_search", sources: [...]},
    {worker: "news_search", sources: [...]}
  ]
  analysis_results: [
    {worker: "content_synthesizer", insights: [...], outline: {...}}
  ]
  writing_results: [
    {worker: "article_writer", content: "...", word_count: 2150}
  ]
  quality_results: [
    {worker: "fact_checker", accuracy: 0.92},
    {worker: "editor", grammar: 0.90},
    {worker: "citation_formatter", quality: 0.95}
  ]
  total_cost: $1.92
  total_tokens: 11,200
}
```

**Next Phase**: Always → EVALUATING

---

### Phase 5: EVALUATING

**Purpose**: Check quality and decide next action

**Duration**: 2-3 seconds

**What Happens**:
```
1. Supervisor receives state with all results

2. Calculate quality scores
   
   A. Article Quality
      ├─ Completeness (covers topic?)
      ├─ Structure (well-organized?)
      └─ Length (meets target?)
   
   B. Source Quality
      ├─ Count (meets minimum?)
      ├─ Diversity (multiple types?)
      └─ Citation accuracy
   
   C. Factual Quality
      ├─ Verified claims
      ├─ Accuracy score
      └─ No contradictions
   
   D. Writing Quality
      ├─ Grammar score
      ├─ Readability
      └─ Tone match

3. Calculate overall score
   overall = weighted average of all scores

4. Compare to threshold
   quality_score vs min_quality_score

5. Make decision
   
   If quality >= threshold:
   ├─ should_continue = false
   ├─ feedback = null
   └─ Decision: COMPLETE ✓
   
   Elif iterations < max:
   ├─ should_continue = true
   ├─ feedback = "What needs improvement"
   └─ Decision: CONTINUE (re-plan)
   
   Else:
   ├─ should_continue = false
   ├─ feedback = "Max iterations reached"
   └─ Decision: FORCE COMPLETE

6. Update state with decision
```

**Evaluation Example**:
```
Calculated Scores:
├─ article_quality: 0.94
├─ source_quality: 0.89
├─ factual_quality: 0.92
└─ writing_quality: 0.88

Overall: 0.91 (91%)
Threshold: 0.80 (80%)
Status: EXCEEDS ✓

Decision: COMPLETE
└─ Proceed to MERGING
```

**State After Phase**:
```
AgentState {
  current_phase: EVALUATING
  quality_score: 0.91
  completeness_score: 0.94
  should_continue: false
  feedback: null
  agent_actions: [
    ...,
    {agent: "Supervisor", action: "evaluate",
     details: {quality: 0.91, decision: "COMPLETE"}}
  ]
}
```

**Next Phase**: 
- If quality good → MERGING
- If quality low + iterations < max → RE_PLANNING
- If quality low + iterations = max → COMPLETED (forced)

---

### Phase 6a: RE_PLANNING (Conditional)

**Purpose**: Create improved plan for iteration

**Duration**: 2-3 seconds

**When Entered**: Quality below threshold, iterations < max

**What Happens**:
```
1. Save current plan to history
   state.plan_history.append(current_plan)

2. Increment iteration count
   state.iteration_count += 1

3. Analyze feedback from Supervisor
   ├─ What was insufficient?
   ├─ Which workers failed?
   └─ What needs improvement?

4. Create improved plan
   ├─ Add more research workers
   ├─ Add verification workers
   ├─ Increase depth/quality
   └─ Address specific issues

5. Set phase back to PLANNING
   └─ Re-run planning with improvements
```

**Re-planning Example**:
```
ITERATION 1:
Quality: 0.65 (below 0.80 threshold)
Feedback: "Need more sources, especially academic"

Re-planning:
├─ Add academic_search (wasn't in original plan)
├─ Add web_scraper (for full content)
├─ Keep all other workers
└─ New estimated cost: $2.80 (was $1.80)

ITERATION 2:
Execute new plan...
Quality: 0.88 ✓ (meets threshold)
Decision: COMPLETE
```

**State After Phase**:
```
AgentState {
  current_phase: RE_PLANNING → PLANNING
  iteration_count: 2
  plan_history: [original_plan]
  current_plan: null (will be recreated)
  agent_actions: [
    ...,
    {agent: "Supervisor", action: "re_plan",
     details: {iteration: 2, reason: "quality_low"}}
  ]
}
```

**Next Phase**: Back to PLANNING

---

### Phase 6b: MERGING (Main Path)

**Purpose**: Package final output

**Duration**: 1-2 seconds

**When Entered**: Quality meets threshold

**What Happens**:
```
1. Merger receives complete state

2. Extract article
   ├─ Get from state.writing_results
   ├─ Format as ArticleResult
   └─ Calculate metadata (word count, reading time)

3. Calculate quality
   ├─ Get from state.quality_results
   ├─ Create QualityScore
   └─ Overall + individual scores

4. Compile sources
   ├─ Get from state.research_results
   ├─ Deduplicate
   ├─ Sort by relevance
   └─ Format as Source[]

5. Calculate metrics
   ├─ Duration: completed_at - started_at
   ├─ Cost: state.total_cost
   ├─ Tokens: state.total_tokens
   └─ Task statistics

6. Create FinalOutput
   ├─ Package all components
   ├─ Add system notes
   ├─ Set status ("completed")
   └─ Return to Controller
```

**State After Phase**:
```
AgentState {
  current_phase: MERGING
  agent_actions: [
    ...,
    {agent: "Merger", action: "create_output",
     details: {status: "completed", quality: 0.91}}
  ]
}
```

**Output Created**:
```
FinalOutput {
  request_id: "req_abc123"
  execution_id: "exec_20241125_143022"
  article: {title, content, word_count, ...}
  quality: {overall: 0.91, accuracy: 0.92, ...}
  sources: [15 sources]
  metrics: {duration: 920s, cost: $2.35, ...}
  status: "completed"
}
```

**Next Phase**: Always → COMPLETED

---

### Phase 7: COMPLETED

**Purpose**: Workflow finished successfully

**Duration**: Instant

**What Happens**:
```
1. State Manager finalizes state
   ├─ Set current_phase = COMPLETED
   ├─ Set completed_at timestamp
   └─ Calculate final duration

2. Controller receives FinalOutput

3. Return to user
```

**Final State**:
```
AgentState {
  execution_id: "exec_20241125_143022"
  current_phase: COMPLETED
  iteration_count: 1
  total_cost: $2.35
  total_tokens: 12,500
  started_at: 2024-11-25 14:30:00
  completed_at: 2024-11-25 14:45:20
  duration: 920 seconds (15 min 20 sec)
  agent_actions: [15 actions total]
}
```

**Workflow Ends**: User receives FinalOutput

---

### Phase 8: FAILED (Error Path)

**Purpose**: Handle critical failures

**Duration**: Instant

**When Entered**: Critical error occurs

**What Happens**:
```
1. Error caught by Controller

2. State Manager sets phase = FAILED

3. Log error details
   ├─ Error type
   ├─ Error message
   ├─ Stack trace
   └─ Which phase failed

4. Create error response

5. Return to user with error
```

**Error Response**:
```
{
  "status": "failed",
  "error": {
    "type": "WorkerExecutionError",
    "message": "article_writer failed after 3 retries",
    "phase": "EXECUTING",
    "execution_id": "exec_20241125_143022"
  },
  "partial_results": {
    "research_results": [...],
    "cost_incurred": $0.50
  }
}
```

---

## ⚙️ Execution Patterns

### Pattern 1: Simple Linear (No Iterations)
```
User Request
    ↓
INITIALIZED
    ↓
PLANNING (4 steps, 8 workers)
    ↓
STRATEGY (optimized)
    ↓
EXECUTING
├─ Step 1: Research (3 workers, 5s)
├─ Step 2: Analysis (1 worker, 2s)
├─ Step 3: Writing (1 worker, 6s)
└─ Step 4: Quality (3 workers, 4s)
    ↓
EVALUATING
├─ Quality: 0.91 ✓
└─ Decision: COMPLETE
    ↓
MERGING
    ↓
COMPLETED
    ↓
User receives FinalOutput

Total time: 17 seconds
Iterations: 1
Status: Success ✓
```

---

### Pattern 2: Single Iteration
```
User Request
    ↓
INITIALIZED → PLANNING → STRATEGY → EXECUTING
    ↓
EVALUATING (Iteration 1)
├─ Quality: 0.65 ❌
├─ Threshold: 0.80
└─ Decision: CONTINUE
    ↓
RE_PLANNING
├─ Feedback: "Need more sources"
└─ Iteration count: 1 → 2
    ↓
PLANNING (improved)
├─ Add academic_search
└─ Add web_scraper
    ↓
STRATEGY → EXECUTING (with new plan)
    ↓
EVALUATING (Iteration 2)
├─ Quality: 0.88 ✓
└─ Decision: COMPLETE
    ↓
MERGING → COMPLETED
    ↓
User receives FinalOutput

Total time: 28 seconds (2 executions)
Iterations: 2
Status: Success ✓
```

---

### Pattern 3: Max Iterations (Forced Complete)
```
User Request
    ↓
[First Execution]
EVALUATING: Quality 0.65 → CONTINUE
    ↓
[Second Execution]
EVALUATING: Quality 0.72 → CONTINUE
    ↓
[Third Execution]
EVALUATING: Quality 0.78 → STILL BELOW
├─ Threshold: 0.80
├─ Iterations: 3 (= MAX_ITERATIONS)
└─ Decision: FORCE COMPLETE
    ↓
MERGING
├─ Warning: "Quality below target"
└─ Status: "partial"
    ↓
COMPLETED
    ↓
User receives FinalOutput with warning

Total time: 42 seconds (3 executions)
Iterations: 3
Status: Partial ⚠️
```

---

### Pattern 4: Critical Failure
```
User Request
    ↓
INITIALIZED → PLANNING → STRATEGY → EXECUTING
    ↓
Step 3: Writing
├─ article_writer starts
├─ Attempt 1: FAILED (API timeout)
├─ Attempt 2: FAILED (API error)
├─ Attempt 3: FAILED (API error)
└─ Critical worker failed ❌
    ↓
FAILED
├─ Cannot continue without article
├─ Log error
└─ Create error response
    ↓
User receives error message

Total time: 12 seconds
Iterations: 1
Status: Failed ❌
```

---

## 🎯 Decision Points

### Decision 1: Start Workflow?

**Location**: Controller initialization

**Checks**:
```
✓ Is Brief valid?
✓ All required fields present?
✓ Within system capacity?
✓ No critical system errors?

If all yes → START
If any no → REJECT with error
```

---

### Decision 2: Which Workers to Use?

**Location**: Planner

**Based On**:
```
Topic Complexity:
├─ Simple (0.0-0.4) → 3-5 workers
├─ Medium (0.4-0.7) → 6-10 workers
└─ Complex (0.7-1.0) → 11-17 workers

User Requirements:
├─ preferred_sources: ["academic"] → academic_search
├─ min_sources: 15 → More research workers
└─ tone: "academic" → citation_formatter

Constraints:
├─ Budget: $2.00 → Limit workers
└─ Time: 10 min → Skip optional workers
```

---

### Decision 3: Parallel or Sequential?

**Location**: Planner

**Logic**:
```
For each step:

If workers are independent:
├─ No dependencies
├─ Don't need each other's results
└─ Execute: PARALLEL

Example: Research workers
├─ web_search (independent)
├─ academic_search (independent)
└─ news_search (independent)
→ PARALLEL ✓

If workers depend on previous results:
├─ Need input from other workers
├─ Sequential order matters
└─ Execute: SEQUENTIAL

Example: Writing after analysis
├─ article_writer needs analysis results
└─ SEQUENTIAL ✓
```

---

### Decision 4: Apply Optimizations?

**Location**: Strategy

**Checks**:
```
Over Budget?
├─ Yes: Remove optional workers, use cheaper models
└─ No: Keep plan as is

Over Time Limit?
├─ Yes: Maximize parallelization, skip optional
└─ No: Keep plan as is

Can Parallelize More?
├─ Yes: Convert sequential to parallel where safe
└─ No: Keep execution modes

Remove Unnecessary Workers?
├─ Check each worker necessity
└─ Remove if truly optional
```

---

### Decision 5: Retry Failed Worker?

**Location**: Orchestrator

**Logic**:
```
Worker fails:
    ↓
Check retry count:
├─ < 3 attempts → RETRY
│  ├─ Wait (exponential backoff)
│  └─ Try again
└─ = 3 attempts → CHECK CRITICALITY
   ├─ Critical worker? → ABORT WORKFLOW
   └─ Optional worker? → SKIP and CONTINUE
```

**Example**:
```
fact_checker fails (attempt 1)
    ↓
Wait 2 seconds
    ↓
fact_checker fails (attempt 2)
    ↓
Wait 4 seconds
    ↓
fact_checker succeeds (attempt 3) ✓
    ↓
Continue workflow
```

---

### Decision 6: Continue or Complete?

**Location**: Supervisor

**Primary Decision Point**

**Logic**:
```
Calculate quality_score
    ↓
Compare to threshold
    ↓
┌─────────────────────────────────────┐
│ quality_score >= threshold?         │
├─────────────────────────────────────┤
│ YES → COMPLETE                      │
│   ├─ should_continue = false        │
│   ├─ feedback = null                │
│   └─ Go to MERGING                  │
│                                     │
│ NO → Check iterations               │
│   ├─ iterations < max?              │
│   │  ├─ YES → CONTINUE              │
│   │  │  ├─ should_continue = true   │
│   │  │  ├─ feedback = improvements  │
│   │  │  └─ Go to RE_PLANNING        │
│   │  │                              │
│   │  └─ NO → FORCE COMPLETE         │
│   │     ├─ should_continue = false  │
│   │     ├─ warning = "Max reached"  │
│   │     └─ Go to MERGING            │
└─────────────────────────────────────┘
```

**Examples**:

**Case 1: High Quality**
```
quality_score: 0.91
threshold: 0.80
iterations: 1

Decision: COMPLETE ✓
→ Go to MERGING
```

**Case 2: Low Quality, Can Iterate**
```
quality_score: 0.68
threshold: 0.80
iterations: 1
max_iterations: 3

Decision: CONTINUE
→ Go to RE_PLANNING
```

**Case 3: Low Quality, Max Iterations**
```
quality_score: 0.76
threshold: 0.80
iterations: 3
max_iterations: 3

Decision: FORCE COMPLETE ⚠️
→ Go to MERGING (with warning)
```

---

## 🚨 Error Handling

### Error Categories

**1. Validation Errors (Before Execution)**
```
Invalid Brief:
├─ Missing required fields
├─ Invalid value ranges
└─ Contradictory requirements

Action: REJECT immediately
Return: Error response
Don't start workflow
```

**2. Worker Errors (During Execution)**
```
Worker fails:
├─ API timeout
├─ API error
├─ Invalid response
└─ Unexpected error

Action: RETRY up to 3 times
If still fails:
├─ Critical worker → ABORT
└─ Optional worker → SKIP
```

**3. System Errors (Unexpected)**
```
Out of memory
Database connection lost
Unexpected exception

Action: FAIL gracefully
├─ Log error
├─ Save state
└─ Return error to user
```

---

### Error Recovery Strategies

**Strategy 1: Retry with Exponential Backoff**
```
Attempt 1: Immediate
    ↓ (fails)
Wait 2 seconds
    ↓
Attempt 2: After 2s
    ↓ (fails)
Wait 4 seconds
    ↓
Attempt 3: After 4s
    ↓ (fails)
Give up
```

**Strategy 2: Fallback Worker**
```
Primary worker fails:
    ↓
Try alternative:
web_scraper fails
    ↓
Use web_search snippet instead
    ↓
Continue with reduced quality
```

**Strategy 3: Partial Results**
```
Critical worker fails:
    ↓
Cannot complete full article
    ↓
Return what we have:
├─ Research results ✓
├─ Partial analysis ✓
├─ No article ❌
└─ Cost incurred: $0.50
```

**Strategy 4: Graceful Degradation**
```
Optional worker fails:
    ↓
Skip it, continue workflow
    ↓
Mark as warning in output
    ↓
User gets article but with note:
"SEO optimization unavailable"
```

---

### Error Handling Example
```
Workflow executing...
    ↓
Step 3: Writing
    ↓
article_writer called
    ↓
Claude API timeout (30s)
    ↓
Orchestrator: Retry attempt 1
    ↓
Wait 2 seconds
    ↓
article_writer called again
    ↓
Claude API error: "Rate limit"
    ↓
Orchestrator: Retry attempt 2
    ↓
Wait 4 seconds
    ↓
article_writer called again
    ↓
Success! ✓
    ↓
Continue workflow normally
    ↓
Total delay: 6 seconds (acceptable)
```

---

## 🔁 Iteration & Re-planning

### Why Iteration?

**Quality-Driven Development:**
```
First attempt often insufficient:
├─ Research may be shallow
├─ Sources may be too few
├─ Analysis may miss key points
└─ Quality below threshold

Solution: Iterate and improve
```

### Iteration Flow
```
ATTEMPT 1:
Create plan based on initial understanding
    ↓
Execute with selected workers
    ↓
Evaluate results
    ↓
Quality: 65% (below 80% threshold)
    ↓
Identify issues:
├─ Only 6 sources (need 10)
├─ No academic sources
└─ Missing key topic aspects
    ↓
Generate feedback

RE-PLANNING:
Analyze feedback
    ↓
Create improved plan:
├─ Add academic_search worker
├─ Add web_scraper for depth
└─ Increase research time
    ↓
New estimated cost: +$1.00
New estimated time: +10 minutes

ATTEMPT 2:
Execute improved plan
    ↓
More comprehensive research
    ↓
Better analysis
    ↓
Higher quality article
    ↓
Evaluate results
    ↓
Quality: 88% (meets threshold) ✓
    ↓
Complete successfully
```

---

### Iteration Limits

**Why Limit Iterations?**
```
Prevent infinite loops:
├─ User's brief may be impossible
├─ Budget may be insufficient
├─ Topic may be too vague
└─ System should eventually complete

Solution: MAX_ITERATIONS = 3
```

**What Happens at Max?**
```
Iteration 3:
Quality: 76% (still below 80%)
    ↓
Check: iterations == MAX_ITERATIONS (3)
    ↓
Decision: FORCE COMPLETE
    ↓
Create output anyway with:
├─ Status: "partial"
├─ Warning: "Quality below target"
├─ Explanation: "Max iterations reached"
└─ All available results
    ↓
User receives partial output ⚠️
```

---

### Iteration Tracking

**State tracks iterations:**
```
AgentState {
  iteration_count: 2
  max_iterations: 3
  plan_history: [
    {plan_1: original plan, quality: 0.65},
    {plan_2: improved plan, quality: 0.88}
  ]
  current_plan: plan_2
}
```

**User visibility:**
```
FinalOutput {
  metrics: {
    iteration_count: 2,
    improvement: "+23% quality (0.65 → 0.88)"
  },
  system_notes: "Generated after 2 iterations to meet quality threshold."
}
```

---

## 📊 Complete Examples

### Example 1: Perfect First Try

**User Request:**
```
Topic: "What is Python programming?"
Content Type: Blog Post
Length: 1000 words
Tone: Casual
Research Depth: Light
Max Budget: $2.00
```

**Execution:**
```
14:30:00 - INITIALIZED
14:30:01 - PLANNING
  └─ Simple topic (complexity: 0.3)
  └─ Plan: 3 steps, 3 workers

14:30:02 - STRATEGY
  └─ No optimization needed (under budget)

14:30:03 - EXECUTING
  14:30:03 - Step 1: web_search (2s)
  14:30:05 - Step 2: article_writer (4s)
  14:30:09 - Step 3: editor (2s)

14:30:11 - EVALUATING
  └─ Quality: 0.92 ✓
  └─ Decision: COMPLETE

14:30:12 - MERGING

14:30:13 - COMPLETED

Total: 13 seconds
Cost: $0.65
Iterations: 1
Status: Success ✓
```

---

### Example 2: One Iteration

**User Request:**
```
Topic: "AI in healthcare 2024"
Content Type: Article
Length: 2000 words
Min Sources: 10
Min Quality: 0.85
Max Budget: $5.00
```

**Execution:**
```
[ITERATION 1]
14:30:00 - INITIALIZED → PLANNING → STRATEGY
14:30:05 - EXECUTING
  └─ Research: web_search, news_search
  └─ Analysis: content_synthesizer
  └─ Writing: article_writer
  └─ Quality: fact_checker, editor

14:30:22 - EVALUATING
  └─ Quality: 0.72 ❌
  └─ Issues: Only 7 sources (need 10)
  └─ Decision: CONTINUE

14:30:23 - RE_PLANNING
  └─ Feedback: "Add academic sources"
  └─ Iteration: 1 → 2

[ITERATION 2]
14:30:24 - PLANNING (improved)
  └─ Add: academic_search, web_scraper
  
14:30:26 - EXECUTING
  └─ Research: web, academic, news, scraper
  └─ Analysis: synthesizer
  └─ Writing: article_writer
  └─ Quality: fact_checker, editor, citation_formatter

14:30:48 - EVALUATING
  └─ Quality: 0.89 ✓
  └─ Sources: 14 (exceeds 10) ✓
  └─ Decision: COMPLETE

14:30:49 - MERGING → COMPLETED

Total: 49 seconds
Cost: $3.20
Iterations: 2
Status: Success ✓
```

---

### Example 3: Max Iterations

**User Request:**
```
Topic: "Quantum computing future predictions"
Content Type: Research Report
Length: 3000 words
Min Sources: 20
Min Quality: 0.90 (very high!)
Max Budget: $10.00
```

**Execution:**
```
[ITERATION 1]
Quality: 0.78 ❌ (below 0.90)
Issues: "Need more academic papers"
→ RE_PLAN

[ITERATION 2]
Quality: 0.83 ❌ (still below 0.90)
Issues: "Need deeper technical analysis"
→ RE_PLAN

[ITERATION 3]
Quality: 0.87 ❌ (still below 0.90)
Issues: "Predictions need more evidence"
Iterations: 3 (= MAX_ITERATIONS)
→ FORCE COMPLETE ⚠️

MERGING:
└─ Status: "partial"
└─ Warning: "Quality 0.87 below target 0.90, but max iterations reached"
└─ Note: "Consider lowering quality threshold or increasing budget"

Total: 95 seconds
Cost: $8.50
Iterations: 3
Status: Partial ⚠️

User receives high-quality output but with warning
```

---

### Example 4: Worker Failure

**User Request:**
```
Topic: "AI trends"
Standard article
```

**Execution:**
```
14:30:00 - INITIALIZED → PLANNING → STRATEGY

14:30:05 - EXECUTING
  Step 1: Research
    ├─ web_search: SUCCESS ✓
    ├─ academic_search: SUCCESS ✓
    └─ news_search: FAILED (API timeout)
        ↓
        Retry 1: FAILED
        ↓
        Retry 2: FAILED
        ↓
        Retry 3: FAILED
        ↓
        news_search is OPTIONAL
        ↓
        SKIP and CONTINUE ⚠️

  Step 2: Analysis
    └─ content_synthesizer: SUCCESS ✓

  Step 3: Writing
    └─ article_writer: FAILED (API error)
        ↓
        article_writer is CRITICAL
        ↓
        Retry 1: FAILED
        ↓
        Retry 2: SUCCESS ✓
        ↓
        CONTINUE

  Step 4: Quality
    └─ All SUCCESS ✓

14:30:42 - EVALUATING
  └─ Quality: 0.85 ✓
  └─ Decision: COMPLETE

14:30:43 - MERGING
  └─ Warning: "News search unavailable"

14:30:44 - COMPLETED

Total: 44 seconds (includes retries)
Cost: $2.10
Status: Success with warnings ⚠️
```

---

## 📚 Summary

### Key Workflow Characteristics

**1. State Machine Based**
- Clear phases
- Predictable transitions
- Easy to debug

**2. Quality-Driven**
- Iterates to meet threshold
- Multiple verification layers
- Automatic improvement

**3. Fault Tolerant**
- Retry failed operations
- Skip optional workers
- Graceful degradation

**4. Transparent**
- Complete audit trail
- Visible decision points
- Clear status at all times

---

### Workflow Phases Quick Reference

| Phase | Duration | Purpose | Next Phase |
|-------|----------|---------|------------|
| **INITIALIZED** | <1s | Setup | PLANNING |
| **PLANNING** | 2-4s | Create plan | STRATEGY |
| **STRATEGY** | 1-2s | Optimize | EXECUTING |
| **EXECUTING** | 10-30min | Run workers | EVALUATING |
| **EVALUATING** | 2-3s | Check quality | MERGING or RE_PLANNING |
| **RE_PLANNING** | 2-3s | Improve plan | PLANNING |
| **MERGING** | 1-2s | Package output | COMPLETED |
| **COMPLETED** | Instant | Done ✓ | - |
| **FAILED** | Instant | Error ❌ | - |

---

### Decision Points Summary

1. **Start workflow?** → Controller validates brief
2. **Which workers?** → Planner selects based on complexity
3. **Parallel or sequential?** → Planner based on dependencies
4. **Optimizations?** → Strategy checks constraints
5. **Retry failed worker?** → Orchestrator based on criticality
6. **Continue or complete?** → Supervisor based on quality

---

### Iteration Patterns
```
No Iteration:
INITIALIZED → PLANNING → STRATEGY → EXECUTING → EVALUATING → MERGING → COMPLETED
(Quality good first try)

Single Iteration:
INIT → PLAN → STRATEGY → EXEC → EVAL → RE_PLAN → PLAN → EXEC → EVAL → MERGE → COMPLETE
(Quality low once, then good)

Max Iterations:
INIT → [PLAN → EXEC → EVAL → RE_PLAN] × 3 → MERGE → COMPLETE
(Quality never meets threshold, forced complete)
```

---

## 🔗 Related Documentation

- **[Architecture](./02_ARCHITECTURE.md)** - System components
- **[Data Models](./03_DATA_MODELS.md)** - AgentState structure
- **[Agent Specifications](./04_AGENTS.md)** - How agents work
- **[Worker Specifications](./05_WORKERS.md)** - What workers do
- **[Development Guide](./09_DEVELOPMENT.md)** - Implementation details

For **implementation**, see source code:
- `src/meta_agent/controller.py` - Main workflow orchestration
- `src/meta_agent/state_manager.py` - State transitions
- `src/schemas/state.py` - WorkflowPhase enum

---

**Document Version**: 1.0  
**Last Updated**: November 25, 2024  
**Status**: State machine implemented and tested

---

END OF WORKFLOW DOCUMENTATION