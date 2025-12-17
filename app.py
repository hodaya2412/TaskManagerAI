import streamlit as st
from main import add_task, load_tasks, update_task, delete_task
from datetime import datetime, timedelta
import pandas as pd

st.set_page_config(page_title="Task Manager AI", layout="wide")
st.title("📝 Task Manager AI")

# ==========================
# פונקציה להמרת תאריך
# ==========================
def parse_due_date(date_input):
    if isinstance(date_input, datetime):
        return date_input.date()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(str(date_input), fmt).date()
        except:
            continue
    return None

# ==========================
# צבע לפי תאריך יעד
# ==========================
def color_for_due_date(due_date_str):
    try:
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        today = datetime.today().date()
        if due_date < today:
            return "🔴"  # Overdue
        elif due_date <= today + timedelta(days=3):
            return "🟠"  # Urgent
        else:
            return "🟢"  # Normal
    except:
        return "⚪"  # Unknown

# ==========================
# Suggested Status לפי תאריך
# ==========================
def suggested_status_by_due_date(due_date_str):
    try:
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        today = datetime.today().date()
        if due_date < today:
            return "Overdue"
        elif due_date <= today + timedelta(days=3):
            return "Urgent"
        else:
            return "Not Urgent"
    except:
        return "Unknown"

# ==========================
# Session state flags
# ==========================
if 'reload' not in st.session_state:
    st.session_state['reload'] = False
if 'active_tab' not in st.session_state:
    st.session_state['active_tab'] = 'all'

# ==========================
# הוספת משימה חדשה
# ==========================
st.subheader("➕ Add New Task")
with st.form("add_task_form"):
    title = st.text_input("Title")
    description = st.text_area("Description")
    due_date = st.date_input("Due Date")
    status = st.selectbox("Status", ["Not Started", "In Progress", "Done"])
    submitted = st.form_submit_button("Add Task")

    if submitted:
        if not title or not due_date:
            st.error("Title and Due Date are required!")
        else:
            due_date_str = due_date.strftime("%Y-%m-%d")
            add_task(title, description, due_date_str, category="", status=status)
            st.success(f"Task '{title}' added successfully!")
            st.session_state['reload'] = not st.session_state['reload']

# ==========================
# טעינת משימות
# ==========================
tasks = load_tasks()
today = datetime.today().date()

# ==========================
# Search / Filter
# ==========================
search_term = st.text_input("🔍 Search tasks (by title or description)")
filtered_tasks = [t for t in tasks if search_term.lower() in t['title'].lower() or search_term.lower() in t['description'].lower()]

# ==========================
# Sorting
# ==========================
sort_by = st.selectbox("Sort by", ["Due Date", "Status"])
if sort_by == "Due Date":
    filtered_tasks.sort(key=lambda x: x['due_date'])
elif sort_by == "Status":
    status_order = {"Urgent": 0, "Not Started": 1, "In Progress": 2, "Done": 3, "Overdue": 4}
    filtered_tasks.sort(key=lambda x: status_order.get(x['status'], 5))

# ==========================
# Tabs
# ==========================
tab_all, tab_completed = st.tabs(["All Tasks", "Completed Tasks"])

# ==========================
# All Tasks Tab
# ==========================
with tab_all:
    st.session_state['active_tab'] = 'all'
    st.subheader("📋 All Tasks")
    all_tasks = [t for t in filtered_tasks if t['status'] != "Done"]

    if all_tasks:
        for t in all_tasks:
            task_id_obj = t['_id']
            task_str_id = str(task_id_obj)

            st.markdown(f"{color_for_due_date(t['due_date'])} **{t['title']}**")
            st.markdown(f"**Description:** {t['description']}")
            st.markdown(f"**Due Date:** {t['due_date']}")
            st.markdown(f"**Status:** {t['status']}")
            st.info(f"Suggested Status: {suggested_status_by_due_date(t['due_date'])}")

            col1, col2, col3 = st.columns(3)

            # Update Expander
            if task_str_id not in st.session_state:
                st.session_state[task_str_id] = False

            with col1:
                if st.button("Update Task", key=f"update_btn_{task_str_id}"):
                    st.session_state[task_str_id] = not st.session_state[task_str_id]

                with st.expander("Edit Task", expanded=st.session_state[task_str_id]):
                    new_title = st.text_input("Title", value=t['title'], key=f"title_{task_str_id}")
                    new_description = st.text_area("Description", value=t['description'], key=f"desc_{task_str_id}")
                    new_due_date = st.date_input("Due Date", value=parse_due_date(t['due_date']), key=f"due_{task_str_id}")
                    new_status = st.selectbox(
                        "Status",
                        ["Not Started", "In Progress", "Done"],
                        index=["Not Started", "In Progress", "Done"].index(t['status']),
                        key=f"status_{task_str_id}"
                    )

                    if st.button("Save Changes", key=f"save_{task_str_id}"):
                        update_task(
                            task_id_obj,
                            title=new_title,
                            description=new_description,
                            due_date=new_due_date.strftime("%Y-%m-%d"),
                            status=new_status
                        )
                        st.success("Task updated!")
                        st.session_state[task_str_id] = False
                        st.session_state['reload'] = not st.session_state['reload']

            # Complete
            with col2:
                if st.button("✅ Complete", key=f"complete_{task_str_id}"):
                    update_task(task_id_obj, status="Done")
                    st.session_state['reload'] = not st.session_state['reload']

            # Delete
            with col3:
                if st.button("🗑️ Delete", key=f"delete_{task_str_id}"):
                    delete_task(task_id_obj)
                    st.session_state['reload'] = not st.session_state['reload']

            st.markdown("---")
    else:
        st.info("No tasks found.")

# ==========================
# Completed Tasks Tab
# ==========================
with tab_completed:
    st.session_state['active_tab'] = 'completed'
    st.subheader("✅ Completed Tasks")
    completed_tasks = [t for t in filtered_tasks if t['status'] == "Done"]

    if completed_tasks:
        for t in completed_tasks:
            task_id_obj = t['_id']
            task_str_id = str(task_id_obj)

            st.markdown(f"{color_for_due_date(t['due_date'])} **{t['title']}**")
            st.markdown(f"**Description:** {t['description']}")
            st.markdown(f"**Due Date:** {t['due_date']}")
            st.markdown(f"**Status:** {t['status']}")

            col1, col2 = st.columns(2)

            # Delete from Completed
            with col1:
                if st.button("🗑️ Delete", key=f"delete_done_{task_str_id}"):
                    delete_task(task_id_obj)
                    st.session_state['reload'] = not st.session_state['reload']

            st.markdown("---")
    else:
        st.info("No completed tasks found.")

# ==========================
# Export CSV
# ==========================
if filtered_tasks:
    df = pd.DataFrame(filtered_tasks)
    st.download_button("📥 Export Tasks CSV", df.to_csv(index=False), "tasks.csv")
