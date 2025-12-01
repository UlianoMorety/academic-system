# backend/seed.py
"""
Seeder script: run after create_tables.sql is executed.
Usage:
  python seed.py
This script will insert roles and sample users with hashed passwords, and sample projects/tasks.
"""
from db import DB_CONFIG
import pymysql
from passlib.hash import bcrypt

con = pymysql.connect(**DB_CONFIG)
try:
    with con.cursor() as cur:
        # roles
        roles = [('admin','full'),('teacher','teacher'),('student','student'),('administrative','administrative')]
        for r in roles:
            cur.execute("INSERT INTO roles (name, description) VALUES (%s,%s) ON DUPLICATE KEY UPDATE description = VALUES(description)", r)
        # get role ids
        cur.execute("SELECT id, name FROM roles")
        roles_map = {row['name']: row['id'] for row in cur.fetchall()}

        users = [
            ('admin', 'admin@example.com', 'admin123', 'admin'),
            ('teacher1','teach@example.com','teach123','teacher'),
            ('student1','stud@example.com','stud123','student'),
            ('adminst','adminst@example.com','adminst123','administrative')
        ]
        for username, email, pwd, role in users:
            hashed = bcrypt.hash(pwd)
            r_id = roles_map[role]
            cur.execute("SELECT id FROM users WHERE username = %s", (username,))
            if not cur.fetchone():
                cur.execute("INSERT INTO users (username,email,password_hash,role_id) VALUES (%s,%s,%s,%s)",
                            (username,email,hashed,r_id))

        # sample projects
        cur.execute("SELECT id FROM users WHERE username = %s", ('teacher1',))
        teacher = cur.fetchone()
        if teacher:
            teacher_id = teacher['id']
            cur.execute("SELECT id FROM projects WHERE name = %s", ("Intro Project",))
            if not cur.fetchone():
                cur.execute("INSERT INTO projects (name,description,owner_id) VALUES (%s,%s,%s)",
                            ("Intro Project", "A sample project created by seed", teacher_id))

        # sample task
        cur.execute("SELECT id FROM projects WHERE name = %s", ("Intro Project",))
        proj = cur.fetchone()
        if proj:
            pid = proj['id']
            cur.execute("SELECT id FROM users WHERE username = %s", ('student1',))
            stud = cur.fetchone()
            stud_id = stud['id'] if stud else None
            cur.execute("SELECT id FROM tasks WHERE title = %s", ("First Task",))
            if not cur.fetchone():
                cur.execute("INSERT INTO tasks (title, description, project_id, assigned_to, due_date) VALUES (%s,%s,%s,%s,%s)",
                            ("First Task", "Seeded task for demo", pid, stud_id, None))
    con.commit()
finally:
    con.close()
    print("Seed complete.")
