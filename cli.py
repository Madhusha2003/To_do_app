#To do list

#imports
import json
import os

# file name
file_name = "To_do_app/data/tasks.json"
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
    while True:
        print("\nTo-Do List Application")
        print("1. Add Task")
        print("2. View Tasks")
        print("3. Complete Task")
        print("4. Delete Task")
        print("5. Edit Task")
        print("6. Exit")
        
        choice = input("Choose an option: ")
        
        if choice == '1':
            task = input("Enter the task: ")
            add_task(task)
        elif choice == '2':
            view_tasks()
        elif choice == '3':
            task_id = int(input("Enter the task ID to complete: "))
            complete_task(task_id)
        elif choice == '4':
            task_id = int(input("Enter the task ID to delete: "))
            delete_task(task_id)
        elif choice == '5':
            task_id = int(input("Enter the task ID to edit: "))
            new_task = input("Enter the new task description: ")
            edit_task(task_id, new_task)    
        elif choice == '6':
            print("Exiting the application.")
            save_tasks() 
            break
        else:
            print("Invalid choice. Please try again.")

# run the main function      
if __name__ == "__main__":
    main()