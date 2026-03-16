import subprocess
import sys

# Install dependencies if needed
subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

# Run the main dashboard
exec(open("openclaw_mission_control_enhanced.py").read())
