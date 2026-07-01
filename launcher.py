#!/usr/bin/env python3
import sys
from launcher_core import A1OSKernel

def executive_interface():
    kernel = A1OSKernel()
    if len(sys.argv) < 3 or sys.argv[1] != "approve":
        print("Usage: ./launcher.py approve <id>")
        return
    
    req_id = int(sys.argv[2])
    result = kernel.approve_intent(req_id)
    print(result)

if __name__ == "__main__":
    executive_interface()
