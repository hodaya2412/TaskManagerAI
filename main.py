from pymongo import MongoClient
from datetime import datetime

# ==========================
# חיבור ל-MongoDB
# ==========================
client = MongoClient("mongodb://localhost:27017/")
db = client["task_manager_db"]
tasks_collection = db["tasks"]

# ==========================
# פונקציה להוספת משימה
# ==========================
def add_task(title, description, due_date, category="", task_id=None, status="Pending"):
    """
    מוסיף משימה למסד הנתונים.
    אם task_id מסופק, נשמור אותו כמו שהוא.
    """
    # המרת תאריך לפורמט אחיד (YYYY-MM-DD)
    if isinstance(due_date, datetime):
        due_date_str = due_date.strftime("%Y-%m-%d")
    else:
        due_date_str = str(due_date)

    # יצירת ID ייחודי אם לא סופק
    if not task_id:
        task_id = str(datetime.now().timestamp())

    task = {
        "_id": task_id,
        "title": title,
        "description": description,
        "due_date": due_date_str,
        "category": category,
        "status": status
    }

    tasks_collection.insert_one(task)
    print(f"Task '{title}' added successfully with ID {task_id}!")

# ==========================
# פונקציה לטעינת כל המשימות
# ==========================
def load_tasks():
    return list(tasks_collection.find())

# ==========================
# פונקציה לעדכון משימה
# ==========================
def update_task(task_id, **kwargs):
    result = tasks_collection.update_one({"_id": task_id}, {"$set": kwargs})
    if result.modified_count > 0:
        print(f"Task {task_id} updated successfully!")
    else:
        print(f"No task found with id {task_id}")

# ==========================
# פונקציה למחיקת משימה
# ==========================
def delete_task(task_id):
    result = tasks_collection.delete_one({"_id": task_id})
    if result.deleted_count > 0:
        print(f"Task {task_id} deleted successfully!")
    else:
        print(f"No task found with id {task_id}")

# ==========================
# פונקציה לסינון משימות
# ==========================
def filter_tasks(field, value):
    return list(tasks_collection.find({field: value}))

# ==========================
# פונקציית AI לעדכון סטטוס
# ==========================
def ai_update_status(task):
    description = task.get("description", "").lower()
    due_date = task.get("due_date", "")

    updates = {}

    if "דחוף" in description or "urgent" in description:
        updates["status"] = "Urgent"

    try:
        due = datetime.strptime(due_date, "%Y-%m-%d")
        if due < datetime.today():
            updates["status"] = "Overdue"
    except:
        pass

    if "סיימתי" in description or "done" in description:
        updates["status"] = "Done"

    if updates:
        tasks_collection.update_one({"_id": task["_id"]}, {"$set": updates})

# ==========================
# הרצת AI על כל המשימות
# ==========================
def run_ai_on_tasks():
    tasks = load_tasks()
    for task in tasks:
        ai_update_status(task)

# ==========================
# דוגמה לשימוש
# ==========================
def main():
    add_task("לסיים פרויקט Python", "להכין מיני פרויקט Task Manager", "2025-12-25", "לימודים", task_id="task1")
    add_task("ללמוד MongoDB", "להבין CRUD ב-Python", "2025-12-20", "לימודים", task_id="task2")

    tasks = load_tasks()
    print("All tasks:", tasks)

    pending_tasks = filter_tasks("status", "Pending")
    print("Pending tasks:", pending_tasks)

if __name__ == "__main__":
    main()
