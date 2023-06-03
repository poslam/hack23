import os
from sys import platform

if platform == "linux" or platform == "linux2" or platform == "darwin":
    os.system("python3 -m uvicorn src.app:app --reload --port 8000")
elif platform == "win32":
    os.system("python -m uvicorn src.app:app --reload --port 8000")
else:
    print(f"No matching function to OS {platform}")