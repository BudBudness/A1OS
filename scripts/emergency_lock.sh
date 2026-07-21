#!/bin/bash
echo "EMERGENCY LOCK INITIATED: Terminating all external tasks."
pkill -f "bash" # Customize to target specific supervisor-launched PIDs
# Reset state if necessary
echo "System suspended."
