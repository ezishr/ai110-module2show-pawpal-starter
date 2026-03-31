from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, time, datetime, timedelta
from enum import Enum
from typing import Any


TIME_WINDOW_ORDER = {
    "morning": 0,
    "afternoon": 1,
    "evening": 2,
    "night": 3,
    "anytime": 4,
}


TIME_WINDOW_STARTS = {
    "morning": time(8, 0),
    "afternoon": time(13, 0),
    "evening": time(18, 0),
    "night": time(20, 0),
    "anytime": time(9, 0),
}


class Frequency(Enum):
    """Supported task frequency patterns."""
    DAILY = "daily"
    EVERY_OTHER_DAY = "every_other_day"
    WEEKLY = "weekly"
    TWICE_WEEKLY = "twice_weekly"
    AS_NEEDED = "as_needed"


@dataclass
class Task:
    """Represents a single pet care activity."""

    task_id: str
    title: str
    category: str
    duration_minutes: int
    priority: int
    frequency: Frequency
    preferred_time_window: str
    scheduled_time: str = "09:00"
    due_date: date | None = None
    assigned_pet_id: str | None = None
    must_do: bool = False
    completion_history: list[date] = field(default_factory=list)

    @property
    def last_completed_on(self) -> date | None:
        """Return the most recent completion date, or None if never completed."""
        return self.completion_history[-1] if self.completion_history else None

    @property
    def completed_today(self) -> bool:
        """Return whether this task was completed on today's date."""
        today = date.today()
        return today in self.completion_history

    def is_due(self, on_date: date) -> bool:
        """Check if task is due on the specified date based on frequency."""
        if on_date in self.completion_history:
            return False

        if self.due_date is not None and on_date < self.due_date:
            return False

        if self.frequency == Frequency.AS_NEEDED:
            return True

        if self.frequency == Frequency.DAILY:
            return True

        last_completed = self.last_completed_on
        if last_completed is None:
            return True

        days_since_last = (on_date - last_completed).days
        if self.frequency == Frequency.EVERY_OTHER_DAY:
            return days_since_last >= 2
        if self.frequency == Frequency.WEEKLY:
            return days_since_last >= 7
        if self.frequency == Frequency.TWICE_WEEKLY:
            return days_since_last >= 3

        return False

    def mark_completed(self, on_date: date) -> None:
        """Record task completion on the given date."""
        if on_date not in self.completion_history:
            self.completion_history.append(on_date)

    def mark_incomplete(self) -> None:
        """Clear all completion history for this task."""
        self.completion_history.clear()

    def get_effective_priority(self, pet: Pet, on_date: date) -> int:
        """Calculate priority adjusted for pet context and time-based factors."""
        effective = self.priority

        if self.category.lower() == "health" and pet.special_needs:
            effective += 1

        if self.is_due(on_date) and self.last_completed_on:
            days_overdue = max(0, (on_date - self.last_completed_on).days - 1)
            effective += min(3, days_overdue)

        if self.must_do:
            effective += 5

        return effective


@dataclass
class Pet:
    """Stores profile and care-context information for a pet."""

    pet_id: str
    name: str
    species: str
    breed: str
    age_years: int
    special_needs: list[str] = field(default_factory=list)

    def update_profile(self, updates: dict[str, Any]) -> None:
        """Update pet profile fields from a dictionary of changes."""
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"Pet has no attribute '{key}'.")

    def add_special_need(self, need: str) -> None:
        """Add a special care need for this pet."""
        if need not in self.special_needs:
            self.special_needs.append(need)

    def remove_special_need(self, need: str) -> bool:
        """Remove a special care need and return success."""
        if need in self.special_needs:
            self.special_needs.remove(need)
            return True
        return False

    def get_care_context(self) -> str:
        """Generate a summary of the pet's profile and care needs."""
        context = f"{self.name} is a {self.age_years}-year-old {self.species} ({self.breed})"
        if self.special_needs:
            context += f". Special needs: {', '.join(self.special_needs)}"
        return context


@dataclass
class ScheduledTask:
    """A task assigned to a concrete time slot in a schedule."""

    task: Task
    start_time: time
    end_time: time
    reason: str

    def duration_minutes(self) -> int:
        """Calculate task duration in minutes based on start and end times."""
        start_dt = datetime.combine(date.today(), self.start_time)
        end_dt = datetime.combine(date.today(), self.end_time)
        return int((end_dt - start_dt).total_seconds() // 60)

    def overlaps(self, other: ScheduledTask) -> bool:
        """Check if this task conflicts with another scheduled task."""
        this_start = datetime.combine(date.today(), self.start_time)
        this_end = datetime.combine(date.today(), self.end_time)
        other_start = datetime.combine(date.today(), other.start_time)
        other_end = datetime.combine(date.today(), other.end_time)
        return this_start < other_end and other_start < this_end


@dataclass
class Schedule:
    """Represents the final daily plan generated by the planner."""

    schedule_date: date
    total_minutes_available: int
    total_minutes_used: int = 0
    items: list[ScheduledTask] = field(default_factory=list)
    explanations: list[str] = field(default_factory=list)
    skipped_tasks_with_reasons: dict[str, str] = field(default_factory=dict)

    def add_item(self, item: ScheduledTask) -> bool:
        """Add a scheduled task to the plan if there's available time."""
        for existing in self.items:
            if item.overlaps(existing):
                return False

        needed_minutes = item.duration_minutes()
        if self.total_minutes_used + needed_minutes > self.total_minutes_available:
            return False

        self.items.append(item)
        self.items.sort(key=lambda scheduled: scheduled.start_time)
        self.total_minutes_used += needed_minutes
        return True

    def remaining_minutes(self) -> int:
        """Calculate unallocated time remaining in the schedule."""
        return self.total_minutes_available - self.total_minutes_used

    def is_full(self) -> bool:
        """Check if the schedule has reached capacity."""
        return self.remaining_minutes() <= 0

    def to_display_rows(self) -> list[dict[str, Any]]:
        """Format schedule for UI display as a list of row dictionaries."""
        rows: list[dict[str, Any]] = []
        for scheduled in self.items:
            rows.append(
                {
                    "time": f"{scheduled.start_time.strftime('%H:%M')} - {scheduled.end_time.strftime('%H:%M')}",
                    "task": scheduled.task.title,
                    "category": scheduled.task.category,
                    "must_do": scheduled.task.must_do or scheduled.task.priority >= 9,
                    "priority": scheduled.task.priority,
                    "reason": scheduled.reason,
                }
            )
        return rows


@dataclass
class Owner:
    """Represents the app user and their scheduling constraints."""

    owner_id: str
    name: str
    available_minutes_per_day: int
    preferences: dict[str, Any] = field(default_factory=dict)
    tasks: list[Task] = field(default_factory=list)
    pet: Pet | None = None

    def add_task(self, task: Task) -> None:
        """Add a new task to the owner's task list (rejects duplicate IDs)."""
        if any(t.task_id == task.task_id for t in self.tasks):
            raise ValueError(f"Task with id '{task.task_id}' already exists.")
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> bool:
        """Remove a task by ID (raises ValueError if not found)."""
        original_length = len(self.tasks)
        self.tasks = [t for t in self.tasks if t.task_id != task_id]
        if len(self.tasks) == original_length:
            raise ValueError(f"Task with id '{task_id}' not found.")
        return True

    def update_task(self, task_id: str, updates: dict[str, Any]) -> bool:
        """Update task fields by ID (raises ValueError if not found or invalid field)."""
        for task in self.tasks:
            if task.task_id == task_id:
                for key, value in updates.items():
                    if hasattr(task, key):
                        setattr(task, key, value)
                    else:
                        raise ValueError(f"Task has no attribute '{key}'.")
                return True
        raise ValueError(f"Task with id '{task_id}' not found.")

    def get_tasks(
        self,
        pet_id: str | None = None,
        status: str = "all",
        sort_by_time: bool = False,
    ) -> list[Task]:
        """Return tasks with optional filtering by pet, status, and time-window sort."""
        today = date.today()
        filtered = self.tasks

        if pet_id is not None:
            filtered = [
                task for task in filtered
                if task.assigned_pet_id is None or task.assigned_pet_id == pet_id
            ]

        normalized_status = status.lower()
        if normalized_status == "completed":
            filtered = [task for task in filtered if today in task.completion_history]
        elif normalized_status == "pending":
            filtered = [task for task in filtered if today not in task.completion_history]

        if sort_by_time:
            filtered = sorted(
                filtered,
                key=lambda task: (
                    TIME_WINDOW_ORDER.get(task.preferred_time_window.lower(), 99),
                    -task.priority,
                    task.duration_minutes,
                ),
            )

        return filtered

    def get_due_tasks(
        self,
        on_date: date,
        pet_id: str | None = None,
        status: str = "pending",
        sort_by_time: bool = True,
    ) -> list[Task]:
        """Return tasks due on the specified date with optional filtering."""
        return [
            task
            for task in self.get_tasks(pet_id=pet_id, status=status, sort_by_time=sort_by_time)
            if task.is_due(on_date)
        ]


class Scheduler:
    """Utility scheduler logic for sorting, filtering, recurrence, and conflict checks."""

    @staticmethod
    def sort_by_time(tasks: list[Task]) -> list[Task]:
        """Return tasks sorted by HH:MM scheduled_time using a lambda key."""
        return sorted(tasks, key=lambda task: datetime.strptime(task.scheduled_time, "%H:%M"))

    @staticmethod
    def filter_tasks(
        tasks: list[Task],
        status: str = "all",
        pet_name: str | None = None,
        pet_name_lookup: dict[str, str] | None = None,
        on_date: date | None = None,
    ) -> list[Task]:
        """Filter tasks by completion status and optional pet name."""
        check_date = on_date or date.today()
        filtered = tasks

        normalized_status = status.lower()
        if normalized_status == "completed":
            filtered = [task for task in filtered if check_date in task.completion_history]
        elif normalized_status == "pending":
            filtered = [task for task in filtered if check_date not in task.completion_history]

        if pet_name and pet_name_lookup:
            filtered = [
                task
                for task in filtered
                if task.assigned_pet_id in pet_name_lookup
                and pet_name_lookup[task.assigned_pet_id].lower() == pet_name.lower()
            ]
        return filtered

    def mark_task_complete(self, owner: Owner, task_id: str, on_date: date | None = None) -> Task:
        """Mark a task complete and auto-create the next occurrence for daily/weekly tasks."""
        completion_date = on_date or date.today()
        target_task: Task | None = None
        for task in owner.tasks:
            if task.task_id == task_id:
                target_task = task
                break

        if target_task is None:
            raise ValueError(f"Task with id '{task_id}' not found.")

        target_task.mark_completed(completion_date)

        if target_task.frequency == Frequency.DAILY:
            self._create_next_recurring_task(owner, target_task, completion_date + timedelta(days=1))
        elif target_task.frequency == Frequency.WEEKLY:
            self._create_next_recurring_task(owner, target_task, completion_date + timedelta(days=7))

        return target_task

    @staticmethod
    def _create_next_recurring_task(owner: Owner, completed_task: Task, next_due_date: date) -> None:
        """Clone a completed recurring task into a new pending instance with a new due date."""
        next_task_id = f"{completed_task.task_id}_next_{next_due_date.strftime('%Y%m%d')}"
        if any(task.task_id == next_task_id for task in owner.tasks):
            return

        owner.tasks.append(
            replace(
                completed_task,
                task_id=next_task_id,
                due_date=next_due_date,
                completion_history=[],
            )
        )

    @staticmethod
    def detect_conflicts(tasks: list[Task], pet_name_lookup: dict[str, str] | None = None) -> list[str]:
        """Return warning messages for tasks that share the exact same scheduled HH:MM slot."""
        warnings: list[str] = []
        seen_slots: dict[str, list[Task]] = {}

        for task in tasks:
            seen_slots.setdefault(task.scheduled_time, []).append(task)

        for slot, slot_tasks in seen_slots.items():
            if len(slot_tasks) < 2:
                continue

            names: list[str] = []
            for task in slot_tasks:
                if task.assigned_pet_id and pet_name_lookup and task.assigned_pet_id in pet_name_lookup:
                    names.append(pet_name_lookup[task.assigned_pet_id])
                else:
                    names.append("unassigned")

            unique_pets = sorted(set(names))
            titles = ", ".join(task.title for task in slot_tasks)
            warnings.append(
                f"Conflict at {slot}: {titles} (pets: {', '.join(unique_pets)})."
            )

        return warnings


class Planner(Scheduler):
    """Core scheduling engine that builds a daily plan."""

    def __init__(self, strategy: str = "priority-first") -> None:
        """Initialize planner with scheduling strategy."""
        self.strategy = strategy

    def generate_daily_schedule(self, owner: Owner, pet: Pet, on_date: date) -> Schedule:
        """Generate an optimized daily schedule based on tasks and constraints."""
        schedule = Schedule(
            schedule_date=on_date,
            total_minutes_available=owner.available_minutes_per_day,
        )

        due_tasks = self.filter_due_tasks(
            owner.get_tasks(pet_id=pet.pet_id, status="pending", sort_by_time=False),
            on_date,
        )
        conflict_resolved = self.resolve_conflicts(due_tasks)
        prioritized = self.prioritize_tasks(conflict_resolved, pet, on_date)
        allocation = self.allocate_within_time(prioritized, owner.available_minutes_per_day)

        selected = sorted(
            allocation["selected"],
            key=lambda task: (
                TIME_WINDOW_ORDER.get(task.preferred_time_window.lower(), 99),
                -task.priority,
                task.duration_minutes,
            ),
        )

        current_dt = datetime.combine(on_date, time(8, 0))
        for task in selected:
            window_start = TIME_WINDOW_STARTS.get(task.preferred_time_window.lower(), time(9, 0))
            start_dt = max(current_dt, datetime.combine(on_date, window_start))
            end_dt = start_dt + timedelta(minutes=task.duration_minutes)

            scheduled = ScheduledTask(
                task=task,
                start_time=start_dt.time(),
                end_time=end_dt.time(),
                reason=f"Selected as {'must-do' if task.must_do or task.priority >= 9 else 'nice-to-have'}",
            )

            if not schedule.add_item(scheduled):
                allocation["skipped"][task.task_id] = "Could not fit due to schedule conflict or capacity"
            else:
                current_dt = end_dt

        schedule.skipped_tasks_with_reasons = allocation["skipped"]
        schedule.explanations = self.build_explanations(schedule.items, allocation["skipped"])
        return schedule

    def filter_due_tasks(self, tasks: list[Task], on_date: date) -> list[Task]:
        """Filter tasks to only those due on the specified date."""
        return [task for task in tasks if task.is_due(on_date)]

    def prioritize_tasks(self, tasks: list[Task], pet: Pet, on_date: date) -> list[Task]:
        """Sort tasks by effective priority considering pet context and recency."""
        return sorted(
            tasks,
            key=lambda task: (
                0 if task.must_do or task.priority >= 9 else 1,
                -task.get_effective_priority(pet, on_date),
                TIME_WINDOW_ORDER.get(task.preferred_time_window.lower(), 99),
                task.duration_minutes,
            ),
        )

    def allocate_within_time(self, tasks: list[Task], available_minutes: int) -> dict[str, Any]:
        """Select tasks that fit within time constraints and return selected/skipped info."""
        selected: list[Task] = []
        skipped: dict[str, str] = {}
        used_minutes = 0

        must_do_tasks = [task for task in tasks if task.must_do or task.priority >= 9]
        nice_to_have_tasks = [task for task in tasks if task not in must_do_tasks]

        for task in must_do_tasks + nice_to_have_tasks:
            if used_minutes + task.duration_minutes <= available_minutes:
                selected.append(task)
                used_minutes += task.duration_minutes
                continue

            if task in must_do_tasks:
                skipped[task.task_id] = "Not enough time for must-do task"
            else:
                skipped[task.task_id] = "Deferred as nice-to-have due to limited time"

        return {
            "selected": selected,
            "skipped": skipped,
            "minutes_used": used_minutes,
        }

    def resolve_conflicts(self, tasks: list[Task]) -> list[Task]:
        """Resolve scheduling conflicts and enforce task dependencies."""
        by_id: dict[str, Task] = {}
        for task in tasks:
            if task.duration_minutes <= 0:
                continue
            existing = by_id.get(task.task_id)
            if existing is None or task.priority > existing.priority:
                by_id[task.task_id] = task

        deduped = list(by_id.values())
        deduped.sort(
            key=lambda task: (
                task.title.lower(),
                task.preferred_time_window.lower(),
                -task.priority,
            )
        )

        resolved: list[Task] = []
        seen_title_window: set[tuple[str, str]] = set()
        for task in deduped:
            key = (task.title.lower(), task.preferred_time_window.lower())
            if key in seen_title_window:
                continue
            seen_title_window.add(key)
            resolved.append(task)
        return resolved

    def build_explanations(self, selected: list[ScheduledTask], skipped_info: dict[str, str]) -> list[str]:
        """Generate human-readable explanations for scheduling decisions."""
        explanations: list[str] = []
        for item in selected:
            bucket = "must-do" if item.task.must_do or item.task.priority >= 9 else "nice-to-have"
            explanations.append(
                f"{item.task.title} at {item.start_time.strftime('%H:%M')} ({bucket}, priority {item.task.priority})."
            )

        for task_id, reason in skipped_info.items():
            explanations.append(f"Skipped {task_id}: {reason}.")
        return explanations
