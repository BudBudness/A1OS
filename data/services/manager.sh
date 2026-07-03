#!/bin/bash
# A1OS Service Orchestrator
SERVICE_DIR="$HOME/A1OS/data/services/deploy"
REGISTRY="$HOME/A1OS/data/services/registry/schema.json"

case "$1" in
    "deploy")
        SERVICE_NAME="$2"
        if [ -f "$SERVICE_DIR/$SERVICE_NAME/init.sh" ]; then
            bash "$SERVICE_DIR/$SERVICE_NAME/init.sh"
            echo "[$(date)] SUCCESS: Deployed [$SERVICE_NAME]"
        else
            echo "[$(date)] ERROR: Service [$SERVICE_NAME] not found."
        fi
        ;;
    "list")
        ls -1 "$SERVICE_DIR"
        ;;
    *)
        echo "Usage: $0 {deploy|list} [service_name]"
        ;;
esac
