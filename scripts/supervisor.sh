#!/bin/bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
python3 -c "import asyncio; from manager import A1OSManager; asyncio.run(A1OSManager().heartbeat_loop())"
