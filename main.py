import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import shutil

from database import Database
from models import (
    USER_SPECIALITY_EXAMPLE,
    USER_SKILLS_EXAMPLE,
    JOB_SKILLS_EXAMPLE,
)

# Папка для загруженных резюме
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class CareerTrackerApp:
    """Главное приложение Карьерный трекер"""

    def __init__(self, main_window):
        # === Основное окно ===
        self.root = main_window
        self.root.title("Карьерный трекер")
        self.root.geometry("1100x700")
        self.root.configure(bg="#e8eef5")

        # === База данных ===
        self.db = Database()

        # === Объявления атрибутов (для ясности IDE) ===
        # Вкладка 1
        self.users_tree = None
        self.user_fields = {}
        # Вкладка 2
        self.resumes_tree = None
        self.resume_user_id = None
        # Вкладка 3
        self.jobs_tree = None
        self.job_fields = {}
        # Вкладка 4
        self.responses_tree = None
        self.resp_user_id = None
        self.resp_job_id = None
        self.resp_status = None

        # === Ноутбук (вкладки) ===
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Создаём 4 вкладки
        self.tab_users = ttk.Frame(self.notebook)
        self.tab_resumes = ttk.Frame(self.notebook)
        self.tab_jobs = ttk.Frame(self.notebook)
        self.tab_responses = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_users, text="База пользователей")
        self.notebook.add(self.tab_resumes, text="База резюме")
        self.notebook.add(self.tab_jobs, text="База вакансий")
        self.notebook.add(self.tab_responses, text="База откликов")

        # Строим каждую вкладку
        self.build_users_tab()
        self.build_resumes_tab()
        self.build_jobs_tab()
        self.build_responses_tab()

        # Загружаем данные
        self.refresh_users()
        self.refresh_resumes()
        self.refresh_jobs()
        self.refresh_responses()

    # ==================================================================
    # ВКЛАДКА 1: БАЗА ПОЛЬЗОВАТЕЛЕЙ
    # ==================================================================
    def build_users_tab(self):
        # ---- Левая часть: список ----
        left = ttk.Frame(self.tab_users)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(left, text="Список пользователей:",
                  font=("Arial", 11, "bold")).pack(anchor=tk.W)

        self.users_tree = ttk.Treeview(
            left,
            columns=("id", "full_name", "phone", "email", "role"),
            show="headings",
            height=20
        )
        self.users_tree.heading("id", text="ID")
        self.users_tree.heading("full_name", text="ФИО")
        self.users_tree.heading("phone", text="Телефон")
        self.users_tree.heading("email", text="Email")
        self.users_tree.heading("role", text="Роль")

        self.users_tree.column("id", width=50)
        self.users_tree.column("full_name", width=200)
        self.users_tree.column("phone", width=130)
        self.users_tree.column("email", width=200)
        self.users_tree.column("role", width=100)

        self.users_tree.pack(fill=tk.BOTH, expand=True)
        self.users_tree.bind("<<TreeviewSelect>>", self.on_user_select)

        # ---- Правая часть: форма ----
        right = ttk.Frame(self.tab_users)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

        ttk.Label(right, text="Добавить нового пользователя",
                  font=("Arial", 12, "bold")).grid(
            row=0, column=0, columnspan=2, pady=10, sticky=tk.W)

        # Поля формы
        fields = [
            ("id", "ID (авто)"),
            ("full_name", "ФИО"),
            ("phone", "Телефон"),
            ("email", "Email"),
            ("organization", "Организация"),
            ("birthday", "Дата рождения (ГГГГ-ММ-ДД)"),
            ("contact", "Контакт"),
            ("role", "Роль"),
        ]

        row = 1
        for key, label in fields:
            ttk.Label(right, text=label).grid(
                row=row, column=0, sticky=tk.W, padx=5, pady=3)
            entry = ttk.Entry(right, width=45)
            entry.grid(row=row, column=1, padx=5, pady=3)
            self.user_fields[key] = entry
            if key == "id":
                entry.config(state="readonly")
            row += 1

        # Многострочные поля
        ttk.Label(right, text="О себе").grid(
            row=row, column=0, sticky=tk.NW, padx=5, pady=3)
        self.user_fields["about_me"] = tk.Text(right, width=45, height=4)
        self.user_fields["about_me"].grid(row=row, column=1, padx=5, pady=3)
        row += 1

        ttk.Label(right, text="Список работ").grid(
            row=row, column=0, sticky=tk.NW, padx=5, pady=3)
        self.user_fields["work_list"] = tk.Text(right, width=45, height=3)
        self.user_fields["work_list"].grid(row=row, column=1, padx=5, pady=3)
        row += 1

        ttk.Label(right, text="user_speciality (JSON)").grid(
            row=row, column=0, sticky=tk.NW, padx=5, pady=3)
        self.user_fields["user_speciality"] = tk.Text(right, width=45, height=3)
        self.user_fields["user_speciality"].grid(
            row=row, column=1, padx=5, pady=3)
        row += 1

        ttk.Label(right, text="user_skills (JSON)").grid(
            row=row, column=0, sticky=tk.NW, padx=5, pady=3)
        self.user_fields["user_skills"] = tk.Text(right, width=45, height=3)
        self.user_fields["user_skills"].grid(
            row=row, column=1, padx=5, pady=3)
        row += 1

        # Кнопки
        btn_frame = ttk.Frame(right)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=15)

        ttk.Button(btn_frame, text="Добавить",
                   command=self.add_user).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="Обновить",
                   command=self.update_user).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="Удалить",
                   command=self.delete_user).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="Очистить",
                   command=self.clear_user_form).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="Пример JSON",
                   command=self.fill_user_json_example).pack(
            side=tk.LEFT, padx=3)

    def on_user_select(self, _event=None):
        sel = self.users_tree.selection()
        if not sel:
            return
        user_id = int(self.users_tree.item(sel[0])["values"][0])
        row = self.db.get_user(user_id)
        if row is None:
            return

        self.clear_user_form()

        keys = ["id", "full_name", "phone", "email", "organization",
                "birthday", "about_me", "contact", "user_speciality",
                "work_list", "user_skills", "role"]

        for i, key in enumerate(keys):
            value = row[i] if row[i] is not None else ""
            widget = self.user_fields[key]
            if isinstance(widget, tk.Text):
                widget.delete("1.0", tk.END)
                widget.insert("1.0", str(value))
            else:
                widget.config(state="normal")
                widget.delete(0, tk.END)
                widget.insert(0, str(value))
                if key == "id":
                    widget.config(state="readonly")

    def add_user(self):
        try:
            user_spec = self.user_fields["user_speciality"].get(
                "1.0", tk.END).strip()
            user_skills = self.user_fields["user_skills"].get(
                "1.0", tk.END).strip()
            if user_spec:
                json.loads(user_spec)
            if user_skills:
                json.loads(user_skills)

            self.db.add_user(
                full_name=self.user_fields["full_name"].get(),
                phone=self.user_fields["phone"].get(),
                email=self.user_fields["email"].get(),
                organization=self.user_fields["organization"].get(),
                birthday=self.user_fields["birthday"].get(),
                about_me=self.user_fields["about_me"].get(
                    "1.0", tk.END).strip(),
                contact=self.user_fields["contact"].get(),
                user_speciality=user_spec,
                work_list=self.user_fields["work_list"].get(
                    "1.0", tk.END).strip(),
                user_skills=user_skills,
                role=self.user_fields["role"].get(),
            )
            messagebox.showinfo("Успех", "Пользователь добавлен!")
            self.refresh_users()
            self.clear_user_form()
        except json.JSONDecodeError as e:
            messagebox.showerror("Ошибка JSON", f"Некорректный JSON:\n{e}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def update_user(self):
        user_id = self.user_fields["id"].get()
        if not user_id:
            messagebox.showwarning("Внимание", "Выберите пользователя!")
            return
        try:
            self.db.update_user(
                user_id=int(user_id),
                full_name=self.user_fields["full_name"].get(),
                phone=self.user_fields["phone"].get(),
                email=self.user_fields["email"].get(),
                organization=self.user_fields["organization"].get(),
                birthday=self.user_fields["birthday"].get(),
                about_me=self.user_fields["about_me"].get(
                    "1.0", tk.END).strip(),
                contact=self.user_fields["contact"].get(),
                user_speciality=self.user_fields["user_speciality"].get(
                    "1.0", tk.END).strip(),
                work_list=self.user_fields["work_list"].get(
                    "1.0", tk.END).strip(),
                user_skills=self.user_fields["user_skills"].get(
                    "1.0", tk.END).strip(),
                role=self.user_fields["role"].get(),
            )
            messagebox.showinfo("Успех", "Данные обновлены!")
            self.refresh_users()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def delete_user(self):
        user_id = self.user_fields["id"].get()
        if not user_id:
            messagebox.showwarning("Внимание", "Выберите пользователя!")
            return
        if messagebox.askyesno("Подтверждение", "Удалить пользователя?"):
            self.db.delete_user(int(user_id))
            self.refresh_users()
            self.clear_user_form()

    def clear_user_form(self):
        for key, widget in self.user_fields.items():
            if isinstance(widget, tk.Text):
                widget.delete("1.0", tk.END)
            else:
                widget.config(state="normal")
                widget.delete(0, tk.END)
                if key == "id":
                    widget.config(state="readonly")

    def fill_user_json_example(self):
        """Заполняет поля JSON примерами"""
        self.user_fields["user_speciality"].delete("1.0", tk.END)
        self.user_fields["user_speciality"].insert(
            "1.0", json.dumps(USER_SPECIALITY_EXAMPLE["specialities"]))
        self.user_fields["user_skills"].delete("1.0", tk.END)
        self.user_fields["user_skills"].insert(
            "1.0", json.dumps(USER_SKILLS_EXAMPLE["skills"]))

    def refresh_users(self):
        for row in self.users_tree.get_children():
            self.users_tree.delete(row)
        for user in self.db.get_all_users():
            self.users_tree.insert("", tk.END, values=(
                user[0],   # id
                user[1],   # full_name
                user[2],   # phone
                user[3],   # email
                user[11],  # role
            ))

    # ==================================================================
    # ВКЛАДКА 2: БАЗА РЕЗЮМЕ
    # ==================================================================
    def build_resumes_tab(self):
        top = ttk.Frame(self.tab_resumes)
        top.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(top, text="ID пользователя:").pack(side=tk.LEFT, padx=3)
        self.resume_user_id = ttk.Entry(top, width=10)
        self.resume_user_id.pack(side=tk.LEFT, padx=3)

        ttk.Button(top, text="Загрузить файл (.doc/.docx/.pdf)",
                   command=self.upload_resume).pack(side=tk.LEFT, padx=10)

        ttk.Button(top, text="Удалить выбранное",
                   command=self.delete_resume).pack(side=tk.LEFT, padx=10)

        # Таблица
        self.resumes_tree = ttk.Treeview(
            self.tab_resumes,
            columns=("id", "user_id", "full_name", "file"),
            show="headings"
        )
        self.resumes_tree.heading("id", text="ID резюме")
        self.resumes_tree.heading("user_id", text="ID пользователя")
        self.resumes_tree.heading("full_name", text="ФИО")
        self.resumes_tree.heading("file", text="Файл")

        self.resumes_tree.column("id", width=80)
        self.resumes_tree.column("user_id", width=120)
        self.resumes_tree.column("full_name", width=250)
        self.resumes_tree.column("file", width=400)

        self.resumes_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        info = ("Формат имени файла: <user_id>_<resume_id>.<ext>\n"
                "Например: 1_5.pdf — резюме пользователя с ID=1, файл №5")
        ttk.Label(self.tab_resumes, text=info,
                  foreground="gray").pack(anchor=tk.W, padx=10)

    def upload_resume(self):
        user_id_str = self.resume_user_id.get().strip()
        if not user_id_str.isdigit():
            messagebox.showwarning("Ошибка",
                                   "Введите ID пользователя (число)!")
            return

        user_id = int(user_id_str)

        if self.db.get_user(user_id) is None:
            messagebox.showerror(
                "Ошибка", f"Пользователя с ID={user_id} нет в базе!")
            return

        filepath = filedialog.askopenfilename(
            title="Выберите резюме",
            filetypes=[
                ("Все документы", "*.doc *.docx *.pdf"),
                ("Word", "*.doc *.docx"),
                ("PDF", "*.pdf"),
            ]
        )
        if not filepath:
            return

        ext = os.path.splitext(filepath)[1].lower()
        if ext not in (".doc", ".docx", ".pdf"):
            messagebox.showerror(
                "Ошибка", "Можно загружать только .doc, .docx или .pdf!")
            return

        new_resume_id = self.db.add_resume(user_id, "")

        filename = f"{user_id}_{new_resume_id}{ext}"
        dest_path = os.path.join(UPLOAD_DIR, filename)

        shutil.copy(filepath, dest_path)

        self.db.cursor.execute(
            "UPDATE Resume SET resume = ? WHERE id = ?",
            (dest_path, new_resume_id)
        )
        self.db.conn.commit()

        messagebox.showinfo("Успех", f"Файл загружен:\n{filename}")
        self.refresh_resumes()

    def delete_resume(self):
        sel = self.resumes_tree.selection()
        if not sel:
            messagebox.showwarning("Внимание", "Выберите резюме!")
            return
        resume_id = int(self.resumes_tree.item(sel[0])["values"][0])
        if messagebox.askyesno("Подтверждение", "Удалить резюме?"):
            self.db.delete_resume(resume_id)
            self.refresh_resumes()

    def refresh_resumes(self):
        for row in self.resumes_tree.get_children():
            self.resumes_tree.delete(row)
        for r in self.db.get_all_resumes():
            self.resumes_tree.insert("", tk.END, values=(
                r[0], r[1], r[2] or "—",
                os.path.basename(r[3]) if r[3] else "—"
            ))

    # ==================================================================
    # ВКЛАДКА 3: БАЗА ВАКАНСИЙ
    # ==================================================================
    def build_jobs_tab(self):
        left = ttk.Frame(self.tab_jobs)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(left, text="Список вакансий:",
                  font=("Arial", 11, "bold")).pack(anchor=tk.W)

        self.jobs_tree = ttk.Treeview(
            left,
            columns=("id", "job_name", "salary", "address"),
            show="headings",
            height=20
        )
        self.jobs_tree.heading("id", text="ID")
        self.jobs_tree.heading("job_name", text="Название")
        self.jobs_tree.heading("salary", text="Зарплата")
        self.jobs_tree.heading("address", text="Адрес")

        self.jobs_tree.column("id", width=50)
        self.jobs_tree.column("job_name", width=250)
        self.jobs_tree.column("salary", width=120)
        self.jobs_tree.column("address", width=200)

        self.jobs_tree.pack(fill=tk.BOTH, expand=True)
        self.jobs_tree.bind("<<TreeviewSelect>>", self.on_job_select)

        right = ttk.Frame(self.tab_jobs)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

        ttk.Label(right, text="Добавить новую вакансию",
                  font=("Arial", 12, "bold")).grid(
            row=0, column=0, columnspan=2, pady=10, sticky=tk.W)

        fields = [
            ("id", "ID (авто)"),
            ("job_name", "Название вакансии"),
            ("salary", "Зарплата"),
            ("address", "Адрес"),
        ]
        row = 1
        for key, label in fields:
            ttk.Label(right, text=label).grid(
                row=row, column=0, sticky=tk.W, padx=5, pady=3)
            entry = ttk.Entry(right, width=40)
            entry.grid(row=row, column=1, padx=5, pady=3)
            self.job_fields[key] = entry
            if key == "id":
                entry.config(state="readonly")
            row += 1

        ttk.Label(right, text="О вакансии").grid(
            row=row, column=0, sticky=tk.NW, padx=5, pady=3)
        self.job_fields["about_job"] = tk.Text(right, width=40, height=5)
        self.job_fields["about_job"].grid(row=row, column=1, padx=5, pady=3)
        row += 1

        ttk.Label(right, text="job_skills (JSON)").grid(
            row=row, column=0, sticky=tk.NW, padx=5, pady=3)
        self.job_fields["job_skills"] = tk.Text(right, width=40, height=3)
        self.job_fields["job_skills"].grid(row=row, column=1, padx=5, pady=3)
        row += 1

        ttk.Label(right, text="job_speciality (JSON)").grid(
            row=row, column=0, sticky=tk.NW, padx=5, pady=3)
        self.job_fields["job_speciality"] = tk.Text(right, width=40, height=3)
        self.job_fields["job_speciality"].grid(
            row=row, column=1, padx=5, pady=3)
        row += 1

        btn_frame = ttk.Frame(right)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=15)

        ttk.Button(btn_frame, text="Добавить",
                   command=self.add_job).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="Обновить",
                   command=self.update_job).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="Удалить",
                   command=self.delete_job).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="Очистить",
                   command=self.clear_job_form).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="Пример JSON",
                   command=self.fill_job_json_example).pack(
            side=tk.LEFT, padx=3)

    def on_job_select(self, _event=None):
        sel = self.jobs_tree.selection()
        if not sel:
            return
        job_id = int(self.jobs_tree.item(sel[0])["values"][0])
        for job in self.db.get_all_jobs():
            if job[0] == job_id:
                self.clear_job_form()
                keys = ["id", "job_skills", "salary",
                        "job_name", "address", "about_job",
                        "job_speciality"]
                for i, key in enumerate(keys):
                    value = job[i] if job[i] is not None else ""
                    widget = self.job_fields[key]
                    if isinstance(widget, tk.Text):
                        widget.delete("1.0", tk.END)
                        widget.insert("1.0", str(value))
                    else:
                        widget.config(state="normal")
                        widget.delete(0, tk.END)
                        widget.insert(0, str(value))
                        if key == "id":
                            widget.config(state="readonly")
                break

    def add_job(self):
        try:
            job_skills = self.job_fields["job_skills"].get(
                "1.0", tk.END).strip()
            job_spec = self.job_fields["job_speciality"].get(
                "1.0", tk.END).strip()
            if job_skills:
                json.loads(job_skills)
            if job_spec:
                json.loads(job_spec)

            salary_str = self.job_fields["salary"].get().strip()
            salary = int(salary_str) if salary_str else 0

            self.db.add_job(
                job_skills=job_skills,
                salary=salary,
                job_name=self.job_fields["job_name"].get(),
                address=self.job_fields["address"].get(),
                about_job=self.job_fields["about_job"].get(
                    "1.0", tk.END).strip(),
                job_speciality=job_spec,
            )
            messagebox.showinfo("Успех", "Вакансия добавлена!")
            self.refresh_jobs()
            self.clear_job_form()
        except json.JSONDecodeError as e:
            messagebox.showerror("Ошибка JSON", f"Некорректный JSON:\n{e}")
        except ValueError:
            messagebox.showerror("Ошибка", "Зарплата должна быть числом!")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def update_job(self):
        job_id = self.job_fields["id"].get()
        if not job_id:
            messagebox.showwarning("Внимание", "Выберите вакансию!")
            return
        try:
            salary_str = self.job_fields["salary"].get().strip()
            salary = int(salary_str) if salary_str else 0

            self.db.update_job(
                job_id=int(job_id),
                job_skills=self.job_fields["job_skills"].get(
                    "1.0", tk.END).strip(),
                salary=salary,
                job_name=self.job_fields["job_name"].get(),
                address=self.job_fields["address"].get(),
                about_job=self.job_fields["about_job"].get(
                    "1.0", tk.END).strip(),
                job_speciality=self.job_fields["job_speciality"].get(
                    "1.0", tk.END).strip(),
            )
            messagebox.showinfo("Успех", "Вакансия обновлена!")
            self.refresh_jobs()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def delete_job(self):
        job_id = self.job_fields["id"].get()
        if not job_id:
            messagebox.showwarning("Внимание", "Выберите вакансию!")
            return
        if messagebox.askyesno("Подтверждение", "Удалить вакансию?"):
            self.db.delete_job(int(job_id))
            self.refresh_jobs()
            self.clear_job_form()

    def clear_job_form(self):
        for key, widget in self.job_fields.items():
            if isinstance(widget, tk.Text):
                widget.delete("1.0", tk.END)
            else:
                widget.config(state="normal")
                widget.delete(0, tk.END)
                if key == "id":
                    widget.config(state="readonly")

    def fill_job_json_example(self):
        self.job_fields["job_skills"].delete("1.0", tk.END)
        self.job_fields["job_skills"].insert(
            "1.0", json.dumps(JOB_SKILLS_EXAMPLE["skills"]))
        self.job_fields["job_speciality"].delete("1.0", tk.END)
        self.job_fields["job_speciality"].insert(
            "1.0", json.dumps([1, 0, 0, 1, 0, 0]))

    def refresh_jobs(self):
        for row in self.jobs_tree.get_children():
            self.jobs_tree.delete(row)
        for j in self.db.get_all_jobs():
            # id, job_skills, salary, job_name, address, about_job, job_speciality
            self.jobs_tree.insert("", tk.END, values=(
                j[0], j[3], j[2], j[4]
            ))

    # ==================================================================
    # ВКЛАДКА 4: БАЗА ОТКЛИКОВ
    # ==================================================================
    def build_responses_tab(self):
        top = ttk.Frame(self.tab_responses)
        top.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(top, text="ID пользователя:").pack(side=tk.LEFT, padx=3)
        self.resp_user_id = ttk.Entry(top, width=8)
        self.resp_user_id.pack(side=tk.LEFT, padx=3)

        ttk.Label(top, text="ID вакансии:").pack(side=tk.LEFT, padx=3)
        self.resp_job_id = ttk.Entry(top, width=8)
        self.resp_job_id.pack(side=tk.LEFT, padx=3)

        ttk.Label(top, text="Статус:").pack(side=tk.LEFT, padx=3)
        self.resp_status = ttk.Combobox(
            top,
            values=["в рассмотрении", "принята", "отклонена"],
            state="readonly",
            width=18
        )
        self.resp_status.current(0)
        self.resp_status.pack(side=tk.LEFT, padx=3)

        ttk.Button(top, text="Добавить отклик",
                   command=self.add_response).pack(side=tk.LEFT, padx=10)
        ttk.Button(top, text="Изменить статус",
                   command=self.change_status).pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text="Удалить",
                   command=self.delete_response).pack(side=tk.LEFT, padx=5)

        self.responses_tree = ttk.Treeview(
            self.tab_responses,
            columns=("id", "user_id", "full_name",
                     "job_id", "job_name", "status"),
            show="headings"
        )
        self.responses_tree.heading("id", text="ID отклика")
        self.responses_tree.heading("user_id", text="ID польз.")
        self.responses_tree.heading("full_name", text="ФИО")
        self.responses_tree.heading("job_id", text="ID вакансии")
        self.responses_tree.heading("job_name", text="Вакансия")
        self.responses_tree.heading("status", text="Статус")

        self.responses_tree.column("id", width=80)
        self.responses_tree.column("user_id", width=80)
        self.responses_tree.column("full_name", width=200)
        self.responses_tree.column("job_id", width=80)
        self.responses_tree.column("job_name", width=250)
        self.responses_tree.column("status", width=150)

        self.responses_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def add_response(self):
        uid = self.resp_user_id.get().strip()
        jid = self.resp_job_id.get().strip()
        if not uid.isdigit() or not jid.isdigit():
            messagebox.showwarning("Ошибка", "ID должны быть числами!")
            return

        if self.db.get_user(int(uid)) is None:
            messagebox.showerror("Ошибка", f"Пользователя с ID={uid} нет!")
            return

        found = False
        for job in self.db.get_all_jobs():
            if job[0] == int(jid):
                found = True
                break
        if not found:
            messagebox.showerror("Ошибка", f"Вакансии с ID={jid} нет!")
            return

        self.db.add_response(int(uid), int(jid), self.resp_status.get())
        messagebox.showinfo("Успех", "Отклик добавлен!")
        self.refresh_responses()

    def change_status(self):
        sel = self.responses_tree.selection()
        if not sel:
            messagebox.showwarning("Внимание", "Выберите отклик!")
            return
        resp_id = int(self.responses_tree.item(sel[0])["values"][0])
        new_status = self.resp_status.get()
        self.db.update_response_status(resp_id, new_status)
        self.refresh_responses()

    def delete_response(self):
        sel = self.responses_tree.selection()
        if not sel:
            messagebox.showwarning("Внимание", "Выберите отклик!")
            return
        resp_id = int(self.responses_tree.item(sel[0])["values"][0])
        if messagebox.askyesno("Подтверждение", "Удалить отклик?"):
            self.db.delete_response(resp_id)
            self.refresh_responses()

    def refresh_responses(self):
        for row in self.responses_tree.get_children():
            self.responses_tree.delete(row)
        for r in self.db.get_all_responses():
            self.responses_tree.insert("", tk.END, values=(
                r[0], r[1], r[2] or "—", r[3], r[4] or "—", r[5]
            ))


# ==================================================================
# ЗАПУСК
# ==================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = CareerTrackerApp(root)
    root.mainloop()