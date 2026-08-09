#!/data/data/com.termux/files/usr/bin/bash
# Adapter: restart a1os-core. Delegates to the single-owner launcher
# (kills any :3011 owner, waits for the port, starts exactly one core).
set -u
export PATH="/data/data/com.termux/files/usr/bin:$PATH"
exec "$HOME/A1OS_RESTORED/ops/a1os-core-launch.sh"
