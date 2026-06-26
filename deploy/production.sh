#!/bin/bash
echo "🚀 Production Deployment"
mkdir -p ~/a1os_prod
cp -r api core memory knowledge agents scheduler cluster consensus events system workflows domain_packs config data ~/a1os_prod/
cd ~/a1os_prod
nohup python3 -m api.server > ~/a1os_prod/logs/a1os.log 2>&1 &
echo "A1OS deployed to ~/a1os_prod"
