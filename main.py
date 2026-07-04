import sys
from modules.orchestrator import Orchestrator
from modules.log_manager import LogManager

def main():
    logger = LogManager()
    if len(sys.argv) < 2:
        print("Usage: python3 main.py [action]")
        return
    
    action = sys.argv[1]
    logger.log(f"CLI Action Executed: {action}")
    if action == "run_cycle":
        print(Orchestrator().run_cycle("BUY", "BTCUSDT", "Default_Asset", 1))

if __name__ == "__main__":
    main()
