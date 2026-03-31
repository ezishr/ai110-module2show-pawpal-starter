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

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
