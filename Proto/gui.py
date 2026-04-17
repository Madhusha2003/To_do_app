#To do list

#imports
import json
import os
import tkinter as tk
from tkinter import ttk 
from tkinter import messagebox, simpledialog

# file name
file_name = "data\\tasks.json"
# Ensure the folder exists
folder = os.path.dirname(file_name)
os.makedirs(folder, exist_ok=True)

# load tasks
def load_tasks():
    if os.path.exists(file_name):
        with open(file_name, 'r') as file:
            return json.load(file)
    return []
# save tasks
def save_tasks():
    with open(file_name, 'w') as file:
        json.dump(tasks, file, indent=4)
# load existing tasks
tasks=load_tasks()

# gui functions
def add_task_gui():
    task = task_entry.get()
    if task:
        add_task(task)        # calls the logic
        task_entry.delete(0, tk.END)
        save_tasks()          # persist changes
        refresh_tasks()       # update Listbox
    else:
        messagebox.showwarning("Input Error", "Please enter a task.")

def complete_task_gui():
    try:
        selected_item = task_tree.selection()[0]
        task_id = int(task_tree.item(selected_item, "values")[0])
        complete_task(task_id)
        save_tasks()
        refresh_tasks()
    except IndexError:
        messagebox.showwarning("Selection Error", "Please select a task to complete.")

def delete_task_gui():
    try:
        selected_item = task_tree.selection()[0]
        task_id = int(task_tree.item(selected_item, "values")[0])
        delete_task(task_id)
        save_tasks()
        refresh_tasks()
    except IndexError:
        messagebox.showwarning("Selection Error", "Please select a task to delete.")

def edit_task_gui():
    try:
        selected_item = task_tree.selection()[0]
        task_id = int(task_tree.item(selected_item, "values")[0])
        new_task = simpledialog.askstring("Edit Task", "Enter the new task description:")
        if new_task:
            edit_task(task_id, new_task)
            save_tasks()
            refresh_tasks()
    except IndexError:
        messagebox.showwarning("Selection Error", "Please select a task to edit.")

# refresh tasks(gui)
def refresh_tasks():
    for item in task_tree.get_children():  # remove existing rows
        task_tree.delete(item)
    for task in tasks:
        if task["completed"]:
            status = "Done"
        else:
            status = "Pending"  
        task_tree.insert("", tk.END, values=(task["id"], task["task"], status))



# gui
root = tk.Tk()
root.title("To-Do List Application")
root.geometry("400x400")
root.resizable(False, False)

task_entry = ttk.Entry(root, width=50)

placeholder = "Enter task here..."
task_entry.insert(0, placeholder)
task_entry.config(foreground="grey") 

# Remove placeholder on focus
def on_focus_in(event):
    if task_entry.get() == placeholder:
        task_entry.delete(0, tk.END)
        task_entry.config(foreground="black")

# Restore placeholder if empty on focus out
def on_focus_out(event):
    if not task_entry.get():
        task_entry.insert(0, placeholder)
        task_entry.config(foreground="grey")

task_entry.bind("<FocusIn>", on_focus_in)
task_entry.bind("<FocusOut>", on_focus_out)

add_button = ttk.Button(root, text="Add Task", command=add_task_gui)

complete_button = ttk.Button(root, text="Complete Task", command=complete_task_gui)

edit_button = ttk.Button(root, text="Edit Task", command=edit_task_gui)

delete_button = ttk.Button(root, text="Delete Task", command=delete_task_gui)

task_tree = ttk.Treeview(root, columns=("ID", "Task", "Status"), show="headings")
task_tree.heading("ID", text="ID")
task_tree.heading("Task", text="Task")
task_tree.heading("Status", text="Status")
task_tree.column("ID", width=50, anchor="center")
task_tree.column("Task", width=200)
task_tree.column("Status", width=100, anchor="center")

#grid configuration
task_entry.grid(row=0, column=0, columnspan=4, padx=5, pady=10, sticky="we")
task_tree.grid(row=1, column=0, columnspan=4, padx=5, pady=10,sticky="nsew")
add_button.grid(row=2, column=0, padx=5, pady=5, sticky="")
complete_button.grid(row=2, column=1, padx=5, pady=5, sticky="")
edit_button.grid(row=2, column=2, padx=5, pady=5 , sticky="")
delete_button.grid(row=2, column=3, padx=5, pady=5, sticky="")

for i in range(4):
    root.grid_columnconfigure(i, weight=1)

refresh_tasks()


# unique id
next_id = max([task["id"] for task in tasks], default=0) + 1

# view tasks
def view_tasks():
    if not tasks:
        print("No tasks available.")
        return
    for task in tasks:
        if task["completed"]:
            status = "Done"
        else:
            status = "Pending"    
        print(f'ID: {task["id"]}, Task: {task["task"]}, Status: {status}') 

# add tasks
def add_task(task):
    global next_id
    task_id = next_id
    tasks.append({"id": task_id, "task": task, "completed": False})
    save_tasks()
    next_id += 1
    print(f'Task "{task}" added with ID {task_id}.')


# edit task
def edit_task(task_id, new_task):
    for task in tasks:
        if task["id"] == task_id:
            task["task"] = new_task
            print(f'Task ID {task_id} updated to "{new_task}".')
            return        

# mark task as completed
def complete_task(task_id):
    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = True
            print(f'Task ID {task_id} marked as completed.')
            return
    print(f'Task ID {task_id} not found.')

# delete task
def delete_task(task_id):
    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)
            print(f'Task ID {task_id} deleted.')
            return
        
    print(f'Task ID {task_id} not found.') 

# main function
def main():
    root.mainloop()
    

# run the main function      
if __name__ == "__main__":
    main()