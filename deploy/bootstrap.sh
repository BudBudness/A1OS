#!/bin/bash
set -e

if ! command -v kubectl &> /dev/null; then
    echo "kubectl not found. Skipping Kubernetes orchestration."
    exit 0
fi

kubectl apply -f k8s/
