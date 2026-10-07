from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import sqlite3

app = FastAPI()

DATABASE = "tasks.db"


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_table():
    connection = get_db()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed INTEGER DEFAULT 0
        )
    """)

    connection.commit()
    connection.close()


create_table()

class TaskCreate(BaseModel):
    title: str
    


@app.get("/api/tasks")
def get_tasks():
    connection = get_db()

    tasks = connection.execute(
        "SELECT * FROM tasks"
    ).fetchall()

    connection.close()

    return [dict(task) for task in tasks]
@app.post("/api/tasks")
def create_task(task: TaskCreate):
    connection = get_db()

    cursor = connection.execute(
        "INSERT INTO tasks (title) VALUES (?)",
        (task.title,)
    )

    connection.commit()

    new_task = connection.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (cursor.lastrowid,)
    ).fetchone()

    connection.close()

    return dict(new_task)
@app.patch("/api/tasks/{task_id}")
def complete_task(task_id: int):
    connection = get_db()

    task = connection.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    if task is None:
        connection.close()
        return {"error": "Task not found"}

    new_status = 0 if task["completed"] else 1

    connection.execute(
        "UPDATE tasks SET completed = ? WHERE id = ?",
        (new_status, task_id)
    )

    connection.commit()

    updated_task = connection.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    connection.close()

    return dict(updated_task)
@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int):
    connection = get_db()

    task = connection.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    if task is None:
        connection.close()
        return {"error": "Task not found"}

    connection.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )

    connection.commit()
    connection.close()

    return {"message": "Task deleted successfully"}

app.mount(
    "/",
    StaticFiles(directory="static", html=True),
    name="static"
)