import streamlit as st
from pawpal_system import Frequency, Owner, Pet, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner and Pet")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
breed = st.text_input("Breed", value="Unknown")
age_years = st.number_input("Age (years)", min_value=0, max_value=40, value=2)
special_needs_input = st.text_input(
    "Special needs (comma-separated)",
    value="",
    placeholder="e.g., daily exercise, sensitive stomach",
)

# Session "vault": keep one Owner object alive across reruns/navigation.
if "owner_obj" not in st.session_state or not isinstance(st.session_state["owner_obj"], Owner):
    default_pet = Pet(
        pet_id="pet_001",
        name=pet_name,
        species=species,
        breed="Unknown",
        age_years=0,
    )
    st.session_state["owner_obj"] = Owner(
        owner_id="owner_001",
        name=owner_name,
        available_minutes_per_day=120,
        preferences={},
        pet=default_pet,
    )

owner_obj = st.session_state["owner_obj"]
# Keep profile fields in sync with current inputs without recreating the object.
owner_obj.name = owner_name
if owner_obj.pet:
    owner_obj.pet.update_profile(
        {
            "name": pet_name,
            "species": species,
            "breed": breed,
            "age_years": int(age_years),
        }
    )

if st.button("Add/Update Pet"):
    if owner_obj.pet is None:
        owner_obj.pet = Pet(
            pet_id="pet_001",
            name=pet_name,
            species=species,
            breed=breed,
            age_years=int(age_years),
        )
    else:
        owner_obj.pet.update_profile(
            {
                "name": pet_name,
                "species": species,
                "breed": breed,
                "age_years": int(age_years),
            }
        )

    owner_obj.pet.special_needs.clear()
    for need in [item.strip() for item in special_needs_input.split(",") if item.strip()]:
        owner_obj.pet.add_special_need(need)
    st.success("Pet profile saved in session vault.")

st.markdown("### Tasks")
st.caption("Add tasks using Owner.add_task() from your backend model.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    task_id = f"task_{len(owner_obj.get_tasks()) + 1:03d}"
    try:
        owner_obj.add_task(
            Task(
                task_id=task_id,
                title=task_title,
                category="general",
                duration_minutes=int(duration),
                priority={"low": 3, "medium": 6, "high": 9}[priority],
                frequency=Frequency.DAILY,
                preferred_time_window="anytime",
            )
        )
        st.success(f"Added task '{task_title}'")
    except ValueError as err:
        st.error(str(err))

current_tasks = owner_obj.get_tasks()
if current_tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "title": task.title,
                "duration_minutes": task.duration_minutes,
                "priority": task.priority,
                "frequency": task.frequency.value,
            }
            for task in current_tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.caption(
    f"Session vault check: owner_obj exists = {'owner_obj' in st.session_state} | "
    f"Owner tasks persisted = {len(owner_obj.get_tasks())}"
)

st.divider()

st.subheader("Build Schedule")
st.caption("Uses your model methods and the same summary style as main.py.")

if st.button("Generate schedule"):
    if owner_obj.pet is None:
        st.warning("Please add a pet profile first.")
    elif not owner_obj.get_tasks():
        st.warning("Please add at least one task before generating a schedule.")
    else:
        st.markdown("### Today's Schedule")
        st.write(f"Owner: {owner_obj.name}")
        st.write(f"Pet: {owner_obj.pet.name} ({owner_obj.pet.species})")
        st.caption(owner_obj.pet.get_care_context())

        scheduled_rows = []
        total_minutes = 0
        for idx, task in enumerate(owner_obj.get_tasks(), start=1):
            scheduled_rows.append(
                {
                    "#": idx,
                    "Task": task.title,
                    "Duration": task.duration_minutes,
                    "Priority": task.priority,
                    "Frequency": task.frequency.value,
                }
            )
            total_minutes += task.duration_minutes

        st.table(scheduled_rows)
        st.write(f"Total task duration: {total_minutes} minutes")
        st.write(f"Available time: {owner_obj.available_minutes_per_day} minutes")
        st.write(
            f"Remaining time: {owner_obj.available_minutes_per_day - total_minutes} minutes"
        )
