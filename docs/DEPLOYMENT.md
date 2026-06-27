# A1OS Deployment
Local: cd ~/A1OS && python3 final_hybrid.py
PWA: cd ~/A1OS/ui/pwa && python3 -m http.server 8000
Background: nohup python3 final_hybrid.py > logs/server.log 2>&1 &
