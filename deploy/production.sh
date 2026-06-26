#!/bin/bash
echo "🚀 Production Deployment"
mkdir -p /tmp/a1os_prod
cp -r api core memory knowledge agents scheduler cluster consensus events system workflows domain_packs config data /tmp/a1os_prod/
cd /tmp/a1os_prod
nohup python3 -m api.server > /var/log/a1os.log 2>&1 &
echo "A1OS deployed to /tmp/a1os_prod"
