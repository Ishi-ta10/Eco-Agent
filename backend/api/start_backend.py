#!/usr/bin/env python
"""Start the Energy Dashboard API backend server"""
import subprocess
import sys
import time

if __name__ == "__main__":
    print("🚀 Starting Energy Dashboard API Backend...")
    print("📍 Server running on: http://0.0.0.0:8000")
    print("📚 API Docs available at: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server.\n")

    try:
        subprocess.run(
            [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
            check=False
        )
    except KeyboardInterrupt:
        print("\n\n✅ Backend server stopped.")
        sys.exit(0)
