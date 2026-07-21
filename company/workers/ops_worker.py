import subprocess
from core.worker import BaseWorker
from typing import Any, Dict

class OpsWorker(BaseWorker):
    async def execute(self, event: Dict[str, Any]) -> Any:
        try:
            uptime = subprocess.check_output(['uptime']).decode('utf-8')
            metrics = {"load": float(uptime.split('load average:')[1].split(',')[0].strip())}
        except:
            metrics = {"load": 0.0}
            
        if metrics["load"] > 5.0:
            return {"status": "action_required", "metrics": metrics, "recommendation": "scale_or_cleanup"}
        return {"status": "stable", "metrics": metrics}
