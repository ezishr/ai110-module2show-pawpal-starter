"""
Main script for PawPal+ demo.

Demonstrates:
- Creating an Owner with pets
- Adding tasks to the owner
- Displaying a today's schedule
"""

from datetime import date
from pawpal_system import Owner, Pet, Task, Frequency, Planner, Scheduler


def main():
    """Run the PawPal+ demo."""
    
    # Create pets
    dog = Pet(
        pet_id="pet_001",
        name="Buddy",
        species="Dog",
        breed="Golden Retriever",
        age_years=3,
        special_needs=["needs daily exercise", "allergic to chicken"]
    )
    
    cat = Pet(
        pet_id="pet_002",
        name="Whiskers",
        species="Cat",
        breed="Siamese",
        age_years=2,
        special_needs=["indoor only", "sensitive stomach"]
    )
    
    # Create owner
    owner = Owner(
        owner_id="owner_001",
        name="Alice",
        available_minutes_per_day=480,  # 8 hours
        preferences={"morning_person": True},
        pet=dog  # Primary pet is the dog
    )
    
    # Create and add tasks (intentionally out-of-order by scheduled_time)
    task1 = Task(
        task_id="task_001",
        title="Morning Walk",
        category="exercise",
        duration_minutes=30,
        priority=9,
        frequency=Frequency.DAILY,
        preferred_time_window="morning",
        scheduled_time="08:30",
        assigned_pet_id=dog.pet_id,
        must_do=True,
    )
    
    task2 = Task(
        task_id="task_002",
        title="Feeding",
        category="feeding",
        duration_minutes=15,
        priority=10,
        frequency=Frequency.DAILY,
        preferred_time_window="morning",
        scheduled_time="08:00",
        assigned_pet_id=dog.pet_id,
        must_do=True,
    )
    
    task3 = Task(
        task_id="task_003",
        title="Playtime",
        category="enrichment",
        duration_minutes=20,
        priority=7,
        frequency=Frequency.DAILY,
        preferred_time_window="afternoon",
        scheduled_time="14:00",
        assigned_pet_id=dog.pet_id,
    )
    
    task4 = Task(
        task_id="task_004",
        title="Medication",
        category="health",
        duration_minutes=5,
        priority=10,
        frequency=Frequency.DAILY,
        preferred_time_window="evening",
        scheduled_time="18:00",
        assigned_pet_id=dog.pet_id,
        must_do=True,
    )

    task5 = Task(
        task_id="task_005",
        title="Litter Scoop",
        category="hygiene",
        duration_minutes=10,
        priority=8,
        frequency=Frequency.DAILY,
        preferred_time_window="morning",
        scheduled_time="08:00",
        assigned_pet_id=cat.pet_id,
    )
    
    # Add tasks to owner
    owner.add_task(task1)
    owner.add_task(task2)
    owner.add_task(task3)
    owner.add_task(task4)
    owner.add_task(task5)

    scheduler = Scheduler()

    # Mark complete using scheduler to auto-create next recurring instance.
    scheduler.mark_task_complete(owner, "task_004", date.today())
    
    # Display info
    print("=" * 60)
    print("PawPal+ - Today's Schedule")
    print("=" * 60)
    print()
    
    print(f"Owner: {owner.name}")
    print(f"Available time per day: {owner.available_minutes_per_day} minutes")
    print()
    
    print(f"Primary Pet: {owner.pet.name} ({owner.pet.species})")
    print(f"  Breed: {owner.pet.breed}")
    print(f"  Age: {owner.pet.age_years} years")
    if owner.pet.special_needs:
        print(f"  Special needs: {', '.join(owner.pet.special_needs)}")
    print()
    
    print("-" * 60)
    print("Sorted + Filtered Tasks (pending, Buddy):")
    print("-" * 60)

    pet_name_lookup = {dog.pet_id: dog.name, cat.pet_id: cat.name}
    pending_tasks = scheduler.filter_tasks(owner.get_tasks(), status="pending", pet_name="Buddy", pet_name_lookup=pet_name_lookup)
    tasks = scheduler.sort_by_time(pending_tasks)
    total_duration = 0
    
    for i, task in enumerate(tasks, 1):
        print(f"\n{i}. {task.title}")
        print(f"   ID: {task.task_id}")
        print(f"   Category: {task.category}")
        print(f"   Duration: {task.duration_minutes} minutes")
        print(f"   Priority: {task.priority}/10")
        print(f"   Frequency: {task.frequency.value}")
        print(f"   Scheduled time: {task.scheduled_time}")
        print(f"   Preferred time: {task.preferred_time_window}")
        print(f"   Must-do: {'yes' if task.must_do or task.priority >= 9 else 'no'}")
        total_duration += task.duration_minutes

    print()
    print("-" * 60)
    print("Conflict Warnings (exact same HH:MM):")
    print("-" * 60)
    pending_all_pets = scheduler.filter_tasks(owner.get_tasks(), status="pending")
    conflict_warnings = scheduler.detect_conflicts(pending_all_pets, pet_name_lookup=pet_name_lookup)
    if conflict_warnings:
        for warning in conflict_warnings:
            print(f"WARNING: {warning}")
    else:
        print("No conflicts found.")

    recurring_tasks = [task for task in owner.get_tasks() if "_next_" in task.task_id]
    if recurring_tasks:
        print()
        print("-" * 60)
        print("Auto-created Recurring Tasks:")
        print("-" * 60)
        for task in recurring_tasks:
            print(f"{task.task_id} -> due {task.due_date} at {task.scheduled_time}")

    print()
    print("-" * 60)
    print("Generated Daily Schedule:")
    print("-" * 60)

    planner = Planner()
    schedule = planner.generate_daily_schedule(owner, dog, date.today())
    for row in schedule.to_display_rows():
        print(
            f"{row['time']} | {row['task']} | priority={row['priority']} | "
            f"must-do={'yes' if row['must_do'] else 'no'}"
        )

    if schedule.skipped_tasks_with_reasons:
        print("\nSkipped tasks:")
        for task_id, reason in schedule.skipped_tasks_with_reasons.items():
            print(f"  - {task_id}: {reason}")
    
    print()
    print("-" * 60)
    print(f"Total pending duration: {total_duration} minutes ({total_duration // 60}h {total_duration % 60}m)")
    print(f"Available time: {owner.available_minutes_per_day} minutes ({owner.available_minutes_per_day // 60}h)")
    print(f"Remaining time: {owner.available_minutes_per_day - total_duration} minutes")
    print("=" * 60)


if __name__ == "__main__":
    main()
