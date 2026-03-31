# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Smarter Scheduling

The scheduler now includes several algorithmic improvements:

- Sorting tasks by exact `HH:MM` task time via `Scheduler.sort_by_time()`.
- Filtering tasks by completion status and pet name via `Scheduler.filter_tasks()`.
- Recurring task automation: when daily or weekly tasks are completed, the next due instance is created automatically.
- Lightweight conflict detection via `Scheduler.detect_conflicts()` that returns warning messages for exact-time collisions.
- Must-do versus nice-to-have scheduling, so high-priority tasks are allocated first when time is limited.

## Testing PawPal+

Run the test suite with:

```bash
python -m pytest
```

Tests currently cover task completion tracking, owner task CRUD operations, pet profile updates, due-task and time-window sorting behavior, must-do versus nice-to-have allocation, recurring task auto-generation, and lightweight conflict detection warnings.

Confidence Level: ★★★★★ (5/5)

Based on the latest test run results, the scheduler behavior is reliable for the implemented scenarios and edge cases in the current suite.

