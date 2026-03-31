"""
Test suite for PawPal+ core functionality.

Tests cover:
- Task completion tracking
- Task addition to Owner
- Pet management
- Other critical behaviors
"""

import pytest
from datetime import date
from pawpal_system import Owner, Pet, Task, Frequency


class TestTaskCompletion:
    """Test task completion and status tracking."""

    @pytest.fixture
    def sample_task(self):
        """Create a sample task for testing."""
        return Task(
            task_id="task_001",
            title="Morning Walk",
            category="exercise",
            duration_minutes=30,
            priority=9,
            frequency=Frequency.DAILY,
            preferred_time_window="morning"
        )

    def test_mark_completed_adds_to_history(self, sample_task):
        """Verify that calling mark_completed() adds date to completion_history."""
        today = date.today()
        
        # Initially no completions
        assert len(sample_task.completion_history) == 0
        assert sample_task.last_completed_on is None
        assert not sample_task.completed_today
        
        # Mark as completed
        sample_task.mark_completed(today)
        
        # Verify completion tracked
        assert len(sample_task.completion_history) == 1
        assert today in sample_task.completion_history
        assert sample_task.last_completed_on == today
        assert sample_task.completed_today

    def test_mark_completed_prevents_duplicates(self, sample_task):
        """Verify that marking same date twice doesn't create duplicates."""
        today = date.today()
        
        sample_task.mark_completed(today)
        sample_task.mark_completed(today)
        
        # Should only have one entry
        assert len(sample_task.completion_history) == 1

    def test_mark_incomplete_clears_history(self, sample_task):
        """Verify that mark_incomplete() clears completion history."""
        today = date.today()
        
        # Complete task
        sample_task.mark_completed(today)
        assert sample_task.completed_today
        
        # Mark incomplete
        sample_task.mark_incomplete()
        
        # History should be cleared
        assert len(sample_task.completion_history) == 0
        assert sample_task.last_completed_on is None
        assert not sample_task.completed_today

    def test_completed_today_property(self, sample_task):
        """Verify completed_today property correctly identifies today's completion."""
        today = date.today()
        yesterday = date(today.year, today.month, max(1, today.day - 1))
        
        # Complete on yesterday
        sample_task.mark_completed(yesterday)
        assert not sample_task.completed_today
        
        # Complete on today
        sample_task.mark_completed(today)
        assert sample_task.completed_today


class TestTaskAddition:
    """Test adding tasks to Owner."""

    @pytest.fixture
    def sample_owner(self):
        """Create a sample owner for testing."""
        return Owner(
            owner_id="owner_001",
            name="Alice",
            available_minutes_per_day=480,
            preferences={}
        )

    @pytest.fixture
    def sample_task(self):
        """Create a sample task for testing."""
        return Task(
            task_id="task_001",
            title="Morning Walk",
            category="exercise",
            duration_minutes=30,
            priority=9,
            frequency=Frequency.DAILY,
            preferred_time_window="morning"
        )

    def test_add_task_increases_count(self, sample_owner, sample_task):
        """Verify that adding a task increases the owner's task count."""
        # Initial state
        assert len(sample_owner.tasks) == 0
        
        # Add task
        sample_owner.add_task(sample_task)
        
        # Count should increase
        assert len(sample_owner.tasks) == 1
        assert sample_task in sample_owner.tasks

    def test_add_multiple_tasks(self, sample_owner):
        """Verify that multiple tasks can be added."""
        task1 = Task("t1", "Walk", "exercise", 30, 9, Frequency.DAILY, "morning")
        task2 = Task("t2", "Feed", "feeding", 15, 10, Frequency.DAILY, "morning")
        task3 = Task("t3", "Play", "enrichment", 20, 7, Frequency.DAILY, "afternoon")
        
        sample_owner.add_task(task1)
        sample_owner.add_task(task2)
        sample_owner.add_task(task3)
        
        assert len(sample_owner.tasks) == 3
        assert task1 in sample_owner.tasks
        assert task2 in sample_owner.tasks
        assert task3 in sample_owner.tasks

    def test_add_duplicate_task_raises_error(self, sample_owner, sample_task):
        """Verify that adding a task with duplicate ID raises ValueError."""
        sample_owner.add_task(sample_task)
        
        # Try to add task with same ID
        duplicate = Task(
            task_id="task_001",  # Same ID
            title="Different Title",
            category="exercise",
            duration_minutes=30,
            priority=9,
            frequency=Frequency.DAILY,
            preferred_time_window="morning"
        )
        
        with pytest.raises(ValueError, match="already exists"):
            sample_owner.add_task(duplicate)

    def test_get_tasks_returns_all_tasks(self, sample_owner):
        """Verify that get_tasks() returns all tasks."""
        task1 = Task("t1", "Walk", "exercise", 30, 9, Frequency.DAILY, "morning")
        task2 = Task("t2", "Feed", "feeding", 15, 10, Frequency.DAILY, "morning")
        task3 = Task("t3", "Play", "enrichment", 20, 7, Frequency.DAILY, "afternoon")
        
        sample_owner.add_task(task1)
        sample_owner.add_task(task2)
        sample_owner.add_task(task3)
        
        tasks = sample_owner.get_tasks()
        
        assert len(tasks) == 3
        assert all(task in tasks for task in [task1, task2, task3])


class TestPetManagement:
    """Test pet profile and special needs management."""

    @pytest.fixture
    def sample_pet(self):
        """Create a sample pet for testing."""
        return Pet(
            pet_id="pet_001",
            name="Buddy",
            species="Dog",
            breed="Golden Retriever",
            age_years=3,
            special_needs=["needs daily exercise"]
        )

    def test_add_special_need(self, sample_pet):
        """Verify that special needs can be added."""
        assert "allergic to chicken" not in sample_pet.special_needs
        
        sample_pet.add_special_need("allergic to chicken")
        
        assert "allergic to chicken" in sample_pet.special_needs
        assert len(sample_pet.special_needs) == 2

    def test_add_duplicate_special_need(self, sample_pet):
        """Verify that adding duplicate special need doesn't create duplicates."""
        original_count = len(sample_pet.special_needs)
        
        sample_pet.add_special_need("needs daily exercise")
        
        # Count should not increase
        assert len(sample_pet.special_needs) == original_count

    def test_remove_special_need(self, sample_pet):
        """Verify that special needs can be removed."""
        sample_pet.add_special_need("allergic to chicken")
        assert "allergic to chicken" in sample_pet.special_needs
        
        success = sample_pet.remove_special_need("allergic to chicken")
        
        assert success
        assert "allergic to chicken" not in sample_pet.special_needs

    def test_remove_nonexistent_special_need(self, sample_pet):
        """Verify that removing non-existent special need returns False."""
        success = sample_pet.remove_special_need("nonexistent need")
        
        assert not success

    def test_update_profile(self, sample_pet):
        """Verify that pet profile can be updated."""
        sample_pet.update_profile({
            "age_years": 4,
            "breed": "Labrador Retriever"
        })
        
        assert sample_pet.age_years == 4
        assert sample_pet.breed == "Labrador Retriever"
        assert sample_pet.name == "Buddy"  # unchanged

    def test_get_care_context(self, sample_pet):
        """Verify that care context summary is generated."""
        context = sample_pet.get_care_context()
        
        assert "Buddy" in context
        assert "3-year-old" in context
        assert "Dog" in context
        assert "Golden Retriever" in context
        assert "needs daily exercise" in context


class TestOwnerTaskManagement:
    """Test Owner task management operations."""

    @pytest.fixture
    def sample_owner_with_tasks(self):
        """Create owner with sample tasks."""
        owner = Owner(
            owner_id="owner_001",
            name="Alice",
            available_minutes_per_day=480
        )
        task1 = Task("t1", "Walk", "exercise", 30, 9, Frequency.DAILY, "morning")
        task2 = Task("t2", "Feed", "feeding", 15, 10, Frequency.DAILY, "morning")
        owner.add_task(task1)
        owner.add_task(task2)
        return owner

    def test_remove_task(self, sample_owner_with_tasks):
        """Verify that tasks can be removed."""
        assert len(sample_owner_with_tasks.tasks) == 2
        
        sample_owner_with_tasks.remove_task("t1")
        
        assert len(sample_owner_with_tasks.tasks) == 1
        assert all(t.task_id != "t1" for t in sample_owner_with_tasks.tasks)

    def test_remove_nonexistent_task_raises_error(self, sample_owner_with_tasks):
        """Verify that removing non-existent task raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            sample_owner_with_tasks.remove_task("nonexistent")

    def test_update_task(self, sample_owner_with_tasks):
        """Verify that task attributes can be updated."""
        sample_owner_with_tasks.update_task("t1", {
            "title": "Evening Walk",
            "duration_minutes": 45
        })
        
        task = next(t for t in sample_owner_with_tasks.tasks if t.task_id == "t1")
        assert task.title == "Evening Walk"
        assert task.duration_minutes == 45

    def test_update_nonexistent_task_raises_error(self, sample_owner_with_tasks):
        """Verify that updating non-existent task raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            sample_owner_with_tasks.update_task("nonexistent", {"title": "New"})


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
