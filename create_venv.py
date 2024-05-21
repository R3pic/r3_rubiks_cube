import subprocess
import sys
import os

venv_dir = 'venv'

subprocess.check_call([sys.executable, '-m', 'venv', venv_dir])
print("Virtual Environment Created..")

if os.name == 'nt':
    activate_script = os.path.join(venv_dir, 'Scripts', 'activate')
else:
    activate_script = os.path.join(venv_dir, 'bin', 'activate')

print("Activating Virtual Environment..")

if os.name == 'nt':
    pip_executable = os.path.join(venv_dir, 'Scripts', 'pip')
else:
    pip_executable = os.path.join(venv_dir, 'bin', 'pip')

requirements_file = 'requirements.txt'
subprocess.check_call([pip_executable, 'install', '-r', requirements_file])

print("Successfully Installed Required Packages..")
print("venv/Scripts/activate and run : python main.py")