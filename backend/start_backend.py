#!/usr/bin/env python
"""Start the Energy Dashboard API backend server"""
import subprocess
import sys
import os

if __name__ == "__main__":
    # Ensure we're in the backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)

    print("🚀 Starting Energy Dashboard API Backend...")
    print("📍 Server running on: http://127.0.0.1:8890")
    print("📚 API Docs available at: http://localhost:8890/docs")
    print("\nPress Ctrl+C to stop the server.\n")

    try:
        subprocess.run(
            [sys.executable, "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8890", "--reload"],
            check=False
        )
    except KeyboardInterrupt:
        print("\n\n✅ Backend server stopped.")
        sys.exit(0)
