import streamlit as st
from datetime import date, time
from pawpal_system import Frequency, Owner, Pet, Task, Planner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")


def _upsert_pet_lookup(name: str) -> str:
    """Return pet ID for a given pet name, creating one when needed."""
    pet_lookup = st.session_state["pet_lookup"]
    for pet_id, pet_name_value in pet_lookup.items():
        if pet_name_value.lower() == name.lower():
            return pet_id

    new_id = f"pet_{len(pet_lookup) + 1:03d}"
    pet_lookup[new_id] = name
    return new_id

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

if "pet_lookup" not in st.session_state:
    st.session_state["pet_lookup"] = {"pet_001": pet_name}

owner_obj = st.session_state["owner_obj"]
scheduler = Scheduler()
planner = Planner()
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
    st.session_state["pet_lookup"][owner_obj.pet.pet_id] = owner_obj.pet.name

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
st.caption("Use scheduler-aware task fields to enable sorting, filtering, recurrence, and conflict checks.")

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    scheduled_time_input = st.time_input("Scheduled time", value=time(9, 0))

col5, col6, col7 = st.columns(3)
with col5:
    category = st.text_input("Category", value="general")
with col6:
    frequency = st.selectbox("Frequency", [freq.value for freq in Frequency], index=0)
with col7:
    preferred_window = st.selectbox(
        "Preferred window",
        ["morning", "afternoon", "evening", "night", "anytime"],
        index=4,
    )

assigned_pet_name = st.text_input("Assign task to pet name", value=pet_name)
mark_as_must_do = st.checkbox("Mark as must-do", value=False)

if st.button("Add task"):
    task_id = f"task_{len(owner_obj.get_tasks()) + 1:03d}"
    assigned_pet_id = _upsert_pet_lookup(assigned_pet_name)
    scheduled_time_text = scheduled_time_input.strftime("%H:%M")

    try:
        owner_obj.add_task(
            Task(
                task_id=task_id,
                title=task_title,
                category=category,
                duration_minutes=int(duration),
                priority={"low": 3, "medium": 6, "high": 9}[priority],
                frequency=Frequency(frequency),
                preferred_time_window=preferred_window,
                scheduled_time=scheduled_time_text,
                assigned_pet_id=assigned_pet_id,
                must_do=mark_as_must_do,
            )
        )
        st.success(f"Added task '{task_title}'")
    except ValueError as err:
        st.error(str(err))

st.markdown("#### Filter and Sort Tasks")
filter_col1, filter_col2, filter_col3 = st.columns(3)
with filter_col1:
    status_filter = st.selectbox("Status", ["all", "pending", "completed"], index=1)
with filter_col2:
    pet_filter = st.selectbox("Pet", ["All pets"] + list(st.session_state["pet_lookup"].values()))
with filter_col3:
    sort_by_time = st.checkbox("Sort by HH:MM", value=True)

selected_pet_name = None if pet_filter == "All pets" else pet_filter
filtered_tasks = scheduler.filter_tasks(
    owner_obj.get_tasks(),
    status=status_filter,
    pet_name=selected_pet_name,
    pet_name_lookup=st.session_state["pet_lookup"],
)
if sort_by_time:
    filtered_tasks = scheduler.sort_by_time(filtered_tasks)

if filtered_tasks:
    st.table(
        [
            {
                "Task": task.title,
                "Pet": st.session_state["pet_lookup"].get(task.assigned_pet_id, "unassigned"),
                "HH:MM": task.scheduled_time,
                "Window": task.preferred_time_window,
                "Duration": task.duration_minutes,
                "Priority": task.priority,
                "Must-do": task.must_do,
                "Status": "completed" if task.completed_today else "pending",
            }
            for task in filtered_tasks
        ]
    )
    st.success(f"Showing {len(filtered_tasks)} task(s) after filters.")
else:
    st.info("No tasks match the current filters.")

pending_tasks_all_pets = scheduler.filter_tasks(owner_obj.get_tasks(), status="pending")
conflicts = scheduler.detect_conflicts(
    pending_tasks_all_pets,
    pet_name_lookup=st.session_state["pet_lookup"],
)
if conflicts:
    st.warning("Scheduling conflicts detected. Adjust one task time in each warning below.")
    for warning in conflicts:
        st.warning(warning)
else:
    st.success("No task time conflicts detected among pending tasks.")

st.markdown("#### Mark Task Complete")
pending_task_options = {
    f"{task.title} ({task.task_id})": task.task_id
    for task in scheduler.filter_tasks(owner_obj.get_tasks(), status="pending")
}
if pending_task_options:
    selected_completion_label = st.selectbox(
        "Select pending task",
        list(pending_task_options.keys()),
    )
    if st.button("Mark selected task complete"):
        completed_id = pending_task_options[selected_completion_label]
        scheduler.mark_task_complete(owner_obj, completed_id, date.today())
        st.success("Task marked complete. Recurring next instance created for daily/weekly tasks.")
else:
    st.info("No pending tasks available to mark complete.")

st.caption(
    f"Session vault check: owner_obj exists = {'owner_obj' in st.session_state} | "
    f"Owner tasks persisted = {len(owner_obj.get_tasks())}"
)

st.divider()

st.subheader("Build Schedule")
st.caption("Uses Planner and Scheduler methods to present a smart daily schedule.")

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

        schedule = planner.generate_daily_schedule(owner_obj, owner_obj.pet, date.today())
        rows = schedule.to_display_rows()
        if rows:
            st.table(rows)
        else:
            st.info("No tasks were selected for today.")

        st.write(f"Total scheduled minutes: {schedule.total_minutes_used}")
        st.write(f"Available time: {schedule.total_minutes_available} minutes")
        st.write(f"Remaining time: {schedule.remaining_minutes()} minutes")

        if schedule.skipped_tasks_with_reasons:
            st.warning("Some tasks were skipped:")
            for task_id, reason in schedule.skipped_tasks_with_reasons.items():
                st.warning(f"{task_id}: {reason}")

        if schedule.explanations:
            st.markdown("#### Why these tasks were chosen")
            for explanation in schedule.explanations:
                st.caption(f"- {explanation}")
