# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

The initial UML design for PawPal+ focuses on separating the system into three main components: core domain entities, scheduling logic, and application control. The system design enables maintenance of the data (which includes pets and tasks) and the decision-making logic (which handles task scheduling) and the user interface interactions because all components function as separate units.

The Owner, Pet, and Task classes form the fundamental components which contain all application information. The system includes a Planner (Scheduler) class which generates a daily care plan after evaluating task priorities and task durations and user restrictions about available time. The Schedule system uses ScheduledTask objects to arrange tasks into particular time slots based on its defined output.

The design enables independent development of the scheduling algorithm because it separates all system components which include user interface elements and data model elements and the scheduling algorithm itself.

***Classes and Their Responsibilities***

**Owner**

The Owner class represents the user of the application. It stores personal preferences and constraints, such as available time per day, and manages the list of care tasks.
	•	Responsibilities:
	•	Manage tasks (add, remove, update)
	•	Store user preferences and availability
	•	Provide task data to the planner

**Pet**

The Pet class stores information about the pet being cared for, such as its name, species, and any special needs.
	•	Responsibilities:
	•	Maintain pet profile information
	•	Provide context (e.g., special care requirements) for planning

**Task**

The Task class represents individual pet care activities (e.g., walking, feeding, medication).
	•	Responsibilities:
	•	Store task details such as duration, priority, and frequency
	•	Determine whether a task is due on a given day
	•	Track completion status

**Planner (Scheduler)**

The Planner is the core logic component of the system. It generates a daily schedule by selecting and organizing tasks based on constraints and priorities.
	•	Responsibilities:
	•	Filter tasks that are due
	•	Prioritize tasks based on importance
	•	Allocate tasks within the available time
	•	Handle scheduling conflicts
	•	Generate explanations for scheduling decisions

**Schedule**

The Schedule class represents the final daily plan produced by the Planner.
	•	Responsibilities:
	•	Store the list of scheduled tasks
	•	Track total time used and remaining time
	•	Provide a structured representation of the daily plan

**ScheduledTask**

This class represents a task assigned to a specific time slot within the schedule.
	•	Responsibilities:
	•	Associate a task with a start and end time
	•	Provide duration and timing details for display


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

My scheduler considers several constraints: daily time budget (`available_minutes_per_day`), task priority, whether a task is marked `must_do`, preferred time window (`morning`, `afternoon`, `evening`, etc.), completion status (`pending` vs `completed`), and recurring frequency (daily/weekly behavior).

I prioritized constraints in this order: (1) hard limits first (time capacity and pending status), (2) care-critical importance (`must_do` and high priority), and then (3) convenience constraints like time-window ordering. This order reflects realistic pet care decision-making: essential care should be scheduled before optional tasks, and tasks should only be included if they fit the owner's day.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One explicit tradeoff is conflict detection: the scheduler currently flags conflicts when two tasks share the exact same `HH:MM` start time, instead of computing full overlap windows for all task durations.

This is reasonable for this project because it keeps the algorithm lightweight and easy to explain while still catching the most common user mistake (double-booking the same time slot). It also avoids extra complexity in the first version, while leaving a clear upgrade path to interval-overlap checks in a future iteration.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used AI as a coding partner across design, implementation, testing, and documentation. During implementation, AI helped me translate requirements into concrete methods (sorting by `HH:MM`, filtering by status/pet, recurring task generation, and conflict warnings). During debugging, I used AI to identify syntax issues and edge cases quickly, then verified fixes by running tests and demo scripts. I also used AI to improve readability and documentation so the final code and README stayed aligned.

The most helpful prompts were specific and behavior-focused, such as: "implement filtering by pet/status while keeping existing APIs compatible," "add recurring logic using `timedelta` when a daily or weekly task is completed," and "surface conflict warnings in Streamlit without crashing the app." Prompts that included the target file and expected output made the results more accurate.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

One moment where I did not accept AI output as-is was when a generated demo edit introduced duplicated arguments in a task constructor, which caused a runtime syntax error. Instead of trusting it, I inspected the file, corrected the duplicate field, and reran the script.

I verified AI suggestions by running `pytest` and executing the demo script (`main.py`) to confirm behavior in real output. I also checked for regressions after each major change, especially around scheduling order, conflict warnings, and recurring task creation.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested both foundational behavior and algorithmic behavior. Foundational tests covered task completion history, duplicate prevention, owner task add/remove/update operations, and pet profile/special-needs updates. Algorithmic tests covered sorting by time window, filtering by pet and status, must-do vs nice-to-have allocation under limited time, recurring task creation for daily tasks, and conflict detection warnings.

These tests were important because the scheduler combines many rules that interact with each other. Without tests, it would be easy to break one behavior while improving another. The tests gave confidence that core scheduling outcomes (what gets scheduled, what gets skipped, and why) stayed consistent during refactors.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I am highly confident that the scheduler works correctly for the implemented scope because all tests pass and the terminal/Streamlit demos show the intended behaviors clearly.

If I had more time, I would test additional edge cases: malformed time strings, timezone/day-boundary behavior, overlapping-duration conflict checks (not just exact-time collisions), recurrence for more frequency types beyond daily/weekly auto-generation, and multi-pet balancing when many high-priority tasks compete for limited time.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I am most satisfied with how the backend algorithms and UI now reflect each other. The app does not just store tasks; it demonstrates practical scheduling intelligence (sorting, filtering, recurring automation, and conflict warnings) in a way users can immediately understand.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

In a future iteration, I would redesign conflict detection to use real interval overlap checks with duration-aware warnings and add automated rescheduling suggestions (for example, proposing the next available slot). I would also add edit/delete task controls directly in the Streamlit UI to make the app feel more production-ready.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

My key takeaway is that AI is most effective when paired with clear constraints, fast feedback loops, and human verification. Good system design made implementation easier, and structured testing made it safe to iterate quickly with AI assistance.
