import time
import os
import sys
import json
try:
    import requests
except ImportError:
    print("Error: 'requests' module missing. Install it via: pip install requests")
    sys.exit(1)

API_URL = "http://localhost:3000"

def get_status():
    try:
        health = requests.get(f"{API_URL}/v1/health", timeout=1).json()
        return health
    except Exception:
        return None

def main():
    while True:
        os.system('clear')
        status = get_status()
        
        print("=" * 60)
        print("          A1OS ARCHITECTURE RUNTIME TELEMETRY          ")
        print("=" * 60)
        
        if not status:
            print("\n   🔴 ENGINE STATUS: Offline / Unreachable")
            print("      Ensure main.py is actively running in the background.")
        else:
            print(f"   🟢 ENGINE STATUS: Active (Environment: {status.get('environment')})")
            print(f"      Core Core Version: {status.get('version')}")
            
            print("\n--- Telemetry Metrics ---")
            telemetry = status.get("telemetry", {})
            for key, val in telemetry.items():
                if key != "timestamp":
                    print(f"      {key.upper()}: {val}")
                    
            print("\n--- System Load Profile ---")
            try:
                import psutil
                print(f"      CPU Usage: {psutil.cpu_percent()}%")
                print(f"      Memory Available: {psutil.virtual_memory().available // (1024**2)} MB")
            except Exception:
                print("      System native profile metrics unavailable")
                
        print("\n" + "=" * 60)
        print(" Press [CTRL + C] to exit the telemetry view stream.")
        
        time.sleep(2)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nTelemetry connection closed cleanly.")
