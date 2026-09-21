import sqlite3
import json
import os

DB_NAME = "career.db"


class Database:
    """Класс для работы с базой данных SQLite"""

    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Создание всех таблиц согласно схеме"""

        # Таблица User
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS User (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name VARCHAR(100),
                phone VARCHAR(20),
                email VARCHAR(320),
                organization VARCHAR(255),
                birthday DATE,
                about_me VARCHAR(1000),
                contact VARCHAR(255),
                user_speciality JSON,
                work_list VARCHAR(1000),
                user_skills JSON,
                role VARCHAR(30)
            )
        """)

        # Таблица Resume
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Resume (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                resume TEXT,
                FOREIGN KEY (user_id) REFERENCES User(id)
                    ON DELETE CASCADE
            )
        """)

        # Таблица Job_opening
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Job_opening (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_skills JSON,
                salary INTEGER,
                job_name VARCHAR(255),
                address VARCHAR(100),
                about_job VARCHAR(1000),
                job_speciality JSON
            )
        """)

        # Таблица Employment_statistics
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Employment_statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                job_id INTEGER,
                status VARCHAR(20),
                FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE,
                FOREIGN KEY (job_id) REFERENCES Job_opening(id) ON DELETE CASCADE
            )
        """)

        self.conn.commit()

    # ============ USER ============

    def add_user(self, full_name, phone, email, organization,
                 birthday, about_me, contact, user_speciality,
                 work_list, user_skills, role):
        self.cursor.execute("""
            INSERT INTO User
            (full_name, phone, email, organization, birthday,
             about_me, contact, user_speciality, work_list,
             user_skills, role)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (full_name, phone, email, organization, birthday,
              about_me, contact, user_speciality, work_list,
              user_skills, role))
        self.conn.commit()
        return self.cursor.lastrowid

    def update_user(self, user_id, full_name, phone, email,
                    organization, birthday, about_me, contact,
                    user_speciality, work_list, user_skills, role):
        self.cursor.execute("""
            UPDATE User SET
                full_name = ?, phone = ?, email = ?,
                organization = ?, birthday = ?, about_me = ?,
                contact = ?, user_speciality = ?, work_list = ?,
                user_skills = ?, role = ?
            WHERE id = ?
        """, (full_name, phone, email, organization, birthday,
              about_me, contact, user_speciality, work_list,
              user_skills, role, user_id))
        self.conn.commit()

    def get_all_users(self):
        self.cursor.execute("SELECT * FROM User ORDER BY id")
        return self.cursor.fetchall()

    def get_user(self, user_id):
        self.cursor.execute("SELECT * FROM User WHERE id = ?", (user_id,))
        return self.cursor.fetchone()

    def delete_user(self, user_id):
        self.cursor.execute("DELETE FROM User WHERE id = ?", (user_id,))
        self.conn.commit()

    # ============ RESUME ============

    def add_resume(self, user_id, resume_text):
        self.cursor.execute("""
            INSERT INTO Resume (user_id, resume)
            VALUES (?, ?)
        """, (user_id, resume_text))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_all_resumes(self):
        self.cursor.execute("""
            SELECT r.id, r.user_id, u.full_name, r.resume
            FROM Resume r
            LEFT JOIN User u ON r.user_id = u.id
            ORDER BY r.id
        """)
        return self.cursor.fetchall()

    def delete_resume(self, resume_id):
        self.cursor.execute("DELETE FROM Resume WHERE id = ?", (resume_id,))
        self.conn.commit()

    # ============ JOB_OPENING ============

    def add_job(self, job_skills, salary, job_name,
                address, about_job, job_speciality):
        self.cursor.execute("""
            INSERT INTO Job_opening
            (job_skills, salary, job_name, address,
             about_job, job_speciality)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (job_skills, salary, job_name, address,
              about_job, job_speciality))
        self.conn.commit()
        return self.cursor.lastrowid

    def update_job(self, job_id, job_skills, salary, job_name,
                   address, about_job, job_speciality):
        self.cursor.execute("""
            UPDATE Job_opening SET
                job_skills = ?, salary = ?, job_name = ?,
                address = ?, about_job = ?, job_speciality = ?
            WHERE id = ?
        """, (job_skills, salary, job_name, address,
              about_job, job_speciality, job_id))
        self.conn.commit()

    def get_all_jobs(self):
        self.cursor.execute("SELECT * FROM Job_opening ORDER BY id")
        return self.cursor.fetchall()

    def delete_job(self, job_id):
        self.cursor.execute("DELETE FROM Job_opening WHERE id = ?", (job_id,))
        self.conn.commit()

    # ============ EMPLOYMENT_STATISTICS ============

    def add_response(self, user_id, job_id, status):
        self.cursor.execute("""
            INSERT INTO Employment_statistics
            (user_id, job_id, status)
            VALUES (?, ?, ?)
        """, (user_id, job_id, status))
        self.conn.commit()
        return self.cursor.lastrowid

    def update_response_status(self, resp_id, status):
        self.cursor.execute("""
            UPDATE Employment_statistics SET status = ? WHERE id = ?
        """, (status, resp_id))
        self.conn.commit()

    def get_all_responses(self):
        self.cursor.execute("""
            SELECT es.id, es.user_id, u.full_name,
                   es.job_id, j.job_name, es.status
            FROM Employment_statistics es
            LEFT JOIN User u ON es.user_id = u.id
            LEFT JOIN Job_opening j ON es.job_id = j.id
            ORDER BY es.id
        """)
        return self.cursor.fetchall()

    def delete_response(self, resp_id):
        self.cursor.execute(
            "DELETE FROM Employment_statistics WHERE id = ?", (resp_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()