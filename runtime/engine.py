import time
import subprocess
import logging

# Configure system heartbeat logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def run_supervisor():
    logging.info("🚀 A1OS Runtime Supervisor Online.")
    while True:
        try:
            # 1. Run the AI Reasoner to update predictions
            subprocess.run(["python3", "ai/reasoner/engine.py"], capture_output=True)
            
            # 2. Run the replenishment daemon to handle stock
            subprocess.run(["python3", "scheduler/replenishment_daemon.py"], capture_output=True)
            
            # 3. Heartbeat delay (e.g., check every 60 seconds)
            time.sleep(60)
        except Exception as e:
            logging.error(f"Supervisor Fault: {e}")
            time.sleep(10)

if __name__ == "__main__":
    run_supervisor()
