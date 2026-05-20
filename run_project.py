import os
import subprocess
import sys
import time
import webbrowser
import socket
from pathlib import Path

# Configuration
PORT = 8000
BACKEND_URL = f"http://127.0.0.1:{PORT}"
FRONTEND_FILE = Path(__file__).parent / "frontend" / "index.html"
REQUIREMENTS_FILE = Path(__file__).parent / "requirements.txt"
BACKEND_SCRIPT = Path(__file__).parent / "backend" / "main.py"

def print_banner():
    print("=" * 60)
    print("      WASTE CLASSIFICATION SYSTEM - ONE-CLICK LAUNCHER      ")
    print("=" * 60)

def check_dependencies():
    print("[*] Checking dependencies...")
    try:
        import pkg_resources
        requirements = pkg_resources.parse_requirements(open(REQUIREMENTS_FILE).read())
        missing = []
        for req in requirements:
            try:
                pkg_resources.require(str(req))
            except pkg_resources.DistributionNotFound:
                missing.append(str(req))
            except pkg_resources.VersionConflict:
                missing.append(str(req))
        
        if missing:
            print(f"[!] Missing dependencies: {', '.join(missing)}")
            print("[*] Installing missing dependencies... this may take a moment.")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)])
            print("[+] Dependencies installed successfully.")
        else:
            print("[+] All dependencies are satisfied.")
    except Exception as e:
        print(f"[!] Error checking dependencies: {e}")
        print("[*] Attempting to install from requirements.txt anyway...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)])
        except Exception as e2:
            print(f"[!] Failed to install dependencies: {e2}")
            return False
    return True

def is_backend_running():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', PORT)) == 0

def start_backend():
    print(f"[*] Starting FastAPI backend on {BACKEND_URL}...")
    # Run from the root directory so imports work correctly
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).parent)
    
    process = subprocess.Popen(
        [sys.executable, str(BACKEND_SCRIPT)],
        cwd=str(Path(__file__).parent),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    return process

def main():
    print_banner()
    
    if not check_dependencies():
        print("[!] Could not prepare environment. Exiting.")
        sys.exit(1)
    
    backend_process = start_backend()
    
    print("[*] Waiting for backend to be ready...")
    start_time = time.time()
    timeout = 30  # 30 seconds timeout
    
    ready = False
    while time.time() - start_time < timeout:
        if is_backend_running():
            ready = True
            break
        
        # Check if process died
        if backend_process.poll() is not None:
            print("[!] Backend process failed to start.")
            out, _ = backend_process.communicate()
            print(out)
            sys.exit(1)
            
        time.sleep(1)
    
    if not ready:
        print("[!] Timeout waiting for backend. It might still be starting (first run with YOLO can be slow).")
    else:
        print("[+] Backend is UP and RUNNING!")
    
    print(f"[*] Opening frontend: {FRONTEND_FILE}")
    webbrowser.open(f"file:///{FRONTEND_FILE.absolute()}")
    
    print("\n" + "=" * 60)
    print("   SYSTEM IS ACTIVE! Press Ctrl+C to stop the servers.")
    print("=" * 60 + "\n")
    
    try:
        # Keep the script running to monitor the backend
        while True:
            line = backend_process.stdout.readline()
            if line:
                print(f"[Backend] {line.strip()}")
            if backend_process.poll() is not None:
                print("[!] Backend process terminated unexpectedly.")
                break
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n[*] Shutting down...")
    finally:
        backend_process.terminate()
        try:
            backend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            backend_process.kill()
        print("[+] Servers stopped.")

if __name__ == "__main__":
    main()
