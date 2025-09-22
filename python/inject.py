import os

import psutil

from injector import DLLInjector

agent = DLLInjector()

# Get the project root directory (parent of python directory)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Try to find the DLL in various locations
dll_paths = [
    os.path.join(project_root, "DLLHooks.dll"),  # Root directory (compatibility)
    os.path.join(project_root, "bin", "Release", "x64", "DLLHooks.dll"),  # New build structure
    os.path.join(project_root, "bin", "Debug", "x64", "DLLHooks.dll"),  # Debug build
    os.path.join(project_root, "DLLHooks", "Release", "DLLHooks.dll"),  # Legacy structure
]

dll_file = None
for path in dll_paths:
    if os.path.exists(path):
        dll_file = path
        print(f"Found DLL at: {dll_file}")
        break

if dll_file is None:
    raise FileNotFoundError(f"DLLHooks.dll not found in any expected locations: {dll_paths}")

monitored_process = "LockDownBrowser"

for task in psutil.process_iter(["name"]):
    task_name = task.name()
    if monitored_process in task_name:
        try:
            print(f"Terminating: {task_name} (PID: {task.pid})")
            task.kill()
        except Exception as err:
            print("Could not terminate:", err)

print("Monitoring for target process...")

while True:
    found = False
    for task in psutil.process_iter(["name"]):
        task_name = task.name()
        if monitored_process in task_name:
            pid = task.pid
            print(f"Target detected: {task_name} (PID: {pid})")
            try:
                agent.attach_to_pid(pid)
                agent.inject_shared_library(dll_file)
                agent.cleanup()
                found = True
                break
            except Exception as err:
                print("Injection error:", err)
    if found:
        break

print("Operation completed.")
