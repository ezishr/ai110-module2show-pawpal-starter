"""
Main script for PawPal+ demo.

Demonstrates:
- Creating an Owner with pets
- Adding tasks to the owner
- Displaying a today's schedule
"""

from datetime import date, time
from pawpal_system import Owner, Pet, Task, Frequency


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
    
    # Create and add tasks
    task1 = Task(
        task_id="task_001",
        title="Morning Walk",
        category="exercise",
        duration_minutes=30,
        priority=9,
        frequency=Frequency.DAILY,
        preferred_time_window="morning"
    )
    
    task2 = Task(
        task_id="task_002",
        title="Feeding",
        category="feeding",
        duration_minutes=15,
        priority=10,
        frequency=Frequency.DAILY,
        preferred_time_window="morning"
    )
    
    task3 = Task(
        task_id="task_003",
        title="Playtime",
        category="enrichment",
        duration_minutes=20,
        priority=7,
        frequency=Frequency.DAILY,
        preferred_time_window="afternoon"
    )
    
    task4 = Task(
        task_id="task_004",
        title="Medication",
        category="health",
        duration_minutes=5,
        priority=10,
        frequency=Frequency.DAILY,
        preferred_time_window="evening"
    )
    
    # Add tasks to owner
    owner.add_task(task1)
    owner.add_task(task2)
    owner.add_task(task3)
    owner.add_task(task4)
    
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
    print("Tasks for Today:")
    print("-" * 60)
    
    tasks = owner.get_tasks()
    total_duration = 0
    
    for i, task in enumerate(tasks, 1):
        print(f"\n{i}. {task.title}")
        print(f"   ID: {task.task_id}")
        print(f"   Category: {task.category}")
        print(f"   Duration: {task.duration_minutes} minutes")
        print(f"   Priority: {task.priority}/10")
        print(f"   Frequency: {task.frequency.value}")
        print(f"   Preferred time: {task.preferred_time_window}")
        total_duration += task.duration_minutes
    
    print()
    print("-" * 60)
    print(f"Total task duration: {total_duration} minutes ({total_duration // 60}h {total_duration % 60}m)")
    print(f"Available time: {owner.available_minutes_per_day} minutes ({owner.available_minutes_per_day // 60}h)")
    print(f"Remaining time: {owner.available_minutes_per_day - total_duration} minutes")
    print("=" * 60)


if __name__ == "__main__":
    main()
