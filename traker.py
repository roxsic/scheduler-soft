import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import json
import os

class TaskTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Tracker")
        self.root.geometry("800x600")
        self.root.configure(bg="#ffffff")
        
        # Загрузка данных
        self.data_file = "tasks.json"
        self.tasks = self.load_data()
        
        # Стили
        self.style = ttk.Style()
        self.style.configure('Treeview', rowheight=25)
        self.style.configure('TButton', font=('Arial', 10))
        
        # Основные фреймы
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Фрейм для добавления задач
        self.add_frame = ttk.LabelFrame(self.main_frame, text="Добавить новую задачу", padding="10")
        self.add_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Элементы для добавления задач
        ttk.Label(self.add_frame, text="Описание:").grid(row=0, column=0, sticky=tk.W)
        self.task_entry = ttk.Entry(self.add_frame, width=50)
        self.task_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(self.add_frame, text="Срок выполнения:").grid(row=1, column=0, sticky=tk.W)
        self.due_date_entry = ttk.Entry(self.add_frame)
        self.due_date_entry.grid(row=1, column=1, padx=5, sticky=tk.W)
        self.due_date_entry.insert(0, (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'))
        
        ttk.Label(self.add_frame, text="Приоритет:").grid(row=2, column=0, sticky=tk.W)
        self.priority_var = tk.StringVar(value="Средний")
        self.priority_menu = ttk.Combobox(self.add_frame, textvariable=self.priority_var, 
                                        values=["Низкий", "Средний", "Высокий"], state="readonly")
        self.priority_menu.grid(row=2, column=1, padx=5, sticky=tk.W)
        
        self.add_btn = ttk.Button(self.add_frame, text="Добавить задачу", command=self.add_task)
        self.add_btn.grid(row=3, column=1, pady=5, sticky=tk.E)
        
        # Фрейм для отображения задач
        self.tasks_frame = ttk.LabelFrame(self.main_frame, text="Список задач", padding="10")
        self.tasks_frame.pack(fill=tk.BOTH, expand=True)
        
        # Дерево для отображения задач
        self.tasks_tree = ttk.Treeview(self.tasks_frame, columns=("id", "description", "due_date", "priority", "status"), 
                                     show="headings", selectmode="extended")
        
        self.tasks_tree.heading("id", text="ID", anchor=tk.W)
        self.tasks_tree.heading("description", text="Описание", anchor=tk.W)
        self.tasks_tree.heading("due_date", text="Срок выполнения", anchor=tk.W)
        self.tasks_tree.heading("priority", text="Приоритет", anchor=tk.W)
        self.tasks_tree.heading("status", text="Статус", anchor=tk.W)
        
        self.tasks_tree.column("id", width=50, stretch=tk.NO)
        self.tasks_tree.column("description", width=300)
        self.tasks_tree.column("due_date", width=120, stretch=tk.NO)
        self.tasks_tree.column("priority", width=100, stretch=tk.NO)
        self.tasks_tree.column("status", width=120, stretch=tk.NO)
        
        self.tasks_tree.pack(fill=tk.BOTH, expand=True)
        
        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(self.tasks_tree, orient="vertical", command=self.tasks_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tasks_tree.configure(yscrollcommand=scrollbar.set)
        
        # Контекстное меню
        self.context_menu = tk.Menu(root, tearoff=0)
        self.context_menu.add_command(label="Пометить как выполненную", command=self.mark_as_done)
        self.context_menu.add_command(label="Удалить", command=self.delete_task)
        self.context_menu.add_command(label="Редактировать", command=self.edit_task)
        
        self.tasks_tree.bind("<Button-3>", self.show_context_menu)
        
        # Кнопки управления
        self.controls_frame = ttk.Frame(self.main_frame)
        self.controls_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.filter_var = tk.StringVar(value="Все")
        self.filter_menu = ttk.Combobox(self.controls_frame, textvariable=self.filter_var, 
                                      values=["Все", "Активные", "Выполненные", "Просроченные"], 
                                      state="readonly", width=15)
        self.filter_menu.pack(side=tk.LEFT, padx=5)
        self.filter_menu.bind("<<ComboboxSelected>>", self.filter_tasks)
        
        self.refresh_btn = ttk.Button(self.controls_frame, text="Обновить", command=self.refresh_tasks)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Заполняем дерево задачами
        self.refresh_tasks()
        
        # Проверка просроченных задач
        self.check_overdue_tasks()
        
        # Привязываем обработчик закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        return []
    
    def save_data(self):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)
    
    def refresh_tasks(self):
        for item in self.tasks_tree.get_children():
            self.tasks_tree.delete(item)
        
        for task in self.tasks:
            status = task.get("status", "Активная")
            due_date = datetime.strptime(task["due_date"], "%Y-%m-%d")
            
            # Проверяем, просрочена ли задача
            if status == "Активная" and due_date < datetime.now():
                status = "Просроченная"
                task["status"] = status
            
            self.tasks_tree.insert("", tk.END, values=(
                task["id"],
                task["description"],
                task["due_date"],
                task["priority"],
                status
            ))
        
        # Раскрашиваем строки
        self.colorize_rows()
    
    def colorize_rows(self):
        for item in self.tasks_tree.get_children():
            values = self.tasks_tree.item(item, "values")
            status = values[4]
            
            if status == "Выполненная":
                self.tasks_tree.tag_configure("done", background="#00ff3c")
                self.tasks_tree.item(item, tags=("done",))
            elif status == "Просроченная":
                self.tasks_tree.tag_configure("overdue", background="#ff0015")
                self.tasks_tree.item(item, tags=("overdue",))
            elif values[3] == "Высокий":
                self.tasks_tree.tag_configure("high", background="#ffc815")
                self.tasks_tree.item(item, tags=("high",))
    
    def add_task(self):
        description = self.task_entry.get().strip()
        due_date = self.due_date_entry.get().strip()
        priority = self.priority_var.get()
        
        if not description:
            messagebox.showwarning("Предупреждение", "Введите описание задачи!")
            return
        
        try:
            datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Предупреждение", "Некорректный формат даты! Используйте ГГГГ-ММ-ДД.")
            return
        
        new_id = max([task["id"] for task in self.tasks]) + 1 if self.tasks else 1
        
        new_task = {
            "id": new_id,
            "description": description,
            "due_date": due_date,
            "priority": priority,
            "status": "Активная",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.tasks.append(new_task)
        self.save_data()
        self.refresh_tasks()
        
        self.task_entry.delete(0, tk.END)
        messagebox.showinfo("Успех", "Задача успешно добавлена!")
    
    def show_context_menu(self, event):
        item = self.tasks_tree.identify_row(event.y)
        if item:
            self.tasks_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def mark_as_done(self):
        selected_items = self.tasks_tree.selection()
        if not selected_items:
            return
        
        for item in selected_items:
            task_id = int(self.tasks_tree.item(item, "values")[0])
            for task in self.tasks:
                if task["id"] == task_id:
                    task["status"] = "Выполненная"
                    task["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    break
        
        self.save_data()
        self.refresh_tasks()
    
    def delete_task(self):
        selected_items = self.tasks_tree.selection()
        if not selected_items:
            return
        
        if not messagebox.askyesno("Подтверждение", "Удалить выбранные задачи?"):
            return
        
        task_ids = [int(self.tasks_tree.item(item, "values")[0]) for item in selected_items]
        self.tasks = [task for task in self.tasks if task["id"] not in task_ids]
        
        self.save_data()
        self.refresh_tasks()
    
    def edit_task(self):
        selected_items = self.tasks_tree.selection()
        if not selected_items or len(selected_items) > 1:
            messagebox.showwarning("Предупреждение", "Выберите одну задачу для редактирования!")
            return
        
        item = selected_items[0]
        task_id = int(self.tasks_tree.item(item, "values")[0])
        
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Редактирование задачи")
        edit_window.grab_set()
        
        # Находим задачу для редактирования
        task_to_edit = None
        for task in self.tasks:
            if task["id"] == task_id:
                task_to_edit = task
                break
        
        if not task_to_edit:
            edit_window.destroy()
            return
        
        # Элементы формы редактирования
        ttk.Label(edit_window, text="Описание:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        desc_entry = ttk.Entry(edit_window, width=50)
        desc_entry.grid(row=0, column=1, padx=5, pady=5)
        desc_entry.insert(0, task_to_edit["description"])
        
        ttk.Label(edit_window, text="Срок выполнения:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        due_entry = ttk.Entry(edit_window)
        due_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        due_entry.insert(0, task_to_edit["due_date"])
        
        ttk.Label(edit_window, text="Приоритет:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        priority_var = tk.StringVar(value=task_to_edit["priority"])
        priority_menu = ttk.Combobox(edit_window, textvariable=priority_var, 
                                   values=["Низкий", "Средний", "Высокий"], state="readonly")
        priority_menu.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(edit_window, text="Статус:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        status_var = tk.StringVar(value=task_to_edit["status"])
        status_menu = ttk.Combobox(edit_window, textvariable=status_var, 
                                 values=["Активная", "Выполненная"], state="readonly")
        status_menu.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        
        def save_changes():
            try:
                datetime.strptime(due_entry.get(), "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("Предупреждение", "Некорректный формат даты! Используйте ГГГГ-ММ-ДД.")
                return
            
            task_to_edit["description"] = desc_entry.get().strip()
            task_to_edit["due_date"] = due_entry.get().strip()
            task_to_edit["priority"] = priority_var.get()
            task_to_edit["status"] = status_var.get()
            
            if status_var.get() == "Выполненная" and "completed_at" not in task_to_edit:
                task_to_edit["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.save_data()
            self.refresh_tasks()
            edit_window.destroy()
            messagebox.showinfo("Успех", "Изменения сохранены!")
        
        save_btn = ttk.Button(edit_window, text="Сохранить", command=save_changes)
        save_btn.grid(row=4, column=1, padx=5, pady=5, sticky=tk.E)
    
    def filter_tasks(self, event=None):
        filter_value = self.filter_var.get()
        
        for item in self.tasks_tree.get_children():
            values = self.tasks_tree.item(item, "values")
            status = values[4]
            
            if filter_value == "Все":
                self.tasks_tree.item(item, open=True)
            elif filter_value == "Активные" and status != "Активная":
                self.tasks_tree.item(item, open=False)
            elif filter_value == "Выполненные" and status != "Выполненная":
                self.tasks_tree.item(item, open=False)
            elif filter_value == "Просроченные" and status != "Просроченная":
                self.tasks_tree.item(item, open=False)
    
    def check_overdue_tasks(self):
        now = datetime.now()
        overdue_count = 0
        
        for task in self.tasks:
            if task.get("status") == "Активная":
                due_date = datetime.strptime(task["due_date"], "%Y-%m-%d")
                if due_date < now:
                    overdue_count += 1
        
        if overdue_count > 0:
            self.root.after(100, lambda: messagebox.showwarning(
                "Просроченные задачи", 
                f"У вас {overdue_count} просроченных задач!"
            ))
    
    def on_closing(self):
        self.save_data()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskTracker(root)
    root.mainloop()