from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .voice import make_silence
from .thumbnail import make_thumbnail
from pydantic import BaseModel, Field
from pathlib import Path
import uuid, json, threading, os, subprocess, httpx

app = FastAPI(title="YouTube High Profit API", version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
JOBS, LOCK = {}, threading.Lock()
WORKSPACE = Path("/workspace")
STAGES = ["opportunity","angle","research","script","voice","visuals","timeline","render","thumbnail","seo","chapters"]

class GenerateRequest(BaseModel):
    topic: str = Field(min_length=3, max_length=500)
    format: str = "explainer"
    target_minutes: int = Field(default=12, ge=3, le=60)
    audience: str = "general"
    monetization_goal: str = "ads"

def persist_job(job: dict):
    url, key = os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key: return
    payload = {k:job[k] for k in ("id","topic","format","target_minutes","status","progress","result","error") if k in job}
    try:
        httpx.post(f"{url}/rest/v1/yhp_jobs", headers={"apikey":key,"Authorization":f"Bearer {key}","Prefer":"resolution=merge-duplicates"}, json=payload, timeout=5)
    except Exception:
        pass

def render_placeholder(root: Path):
    out = root/"final"/"video.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(["ffmpeg","-y","-f","lavfi","-i","color=c=black:s=1280x720:r=30:d=1","-pix_fmt","yuv420p",str(out)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return str(out.relative_to(root))
    except Exception:
        return None

def demo_run(job_id, req):
    root = WORKSPACE / job_id
    root.mkdir(parents=True, exist_ok=True)
    outputs = {}
    for i, stage in enumerate(STAGES, 1):
        base = {"stage":stage,"version":1,"status":"succeeded"}
        if stage == "opportunity":
            out = base | {"demand_hypothesis":f"Audience interest around {req.topic}","ctr_levers":["specific promise","curiosity gap"],"retention_levers":["open loop","pattern changes"],"monetization_fit":req.monetization_goal}
        elif stage == "angle":
            out = base | {"primary":f"What most people misunderstand about {req.topic}","alternatives":[f"The hidden economics of {req.topic}",f"How {req.topic} changed over time"],"format":req.format}
        elif stage == "research":
            out = base | {"sources":[],"claims":[{"claim":f"Research plan for {req.topic}","confidence":"unverified"}],"note":"Demo provider; connect a live research provider for evidence."}
        elif stage == "script":
            out = base | {"title":f"The Truth About {req.topic}","sections":[{"heading":"Hook","narration":f"Why does {req.topic} matter now?"},{"heading":"Context","narration":f"This video explains the forces behind {req.topic}."},{"heading":"Implications","narration":"The evidence points to consequences viewers should understand."}],"estimated_minutes":req.target_minutes}
        elif stage == "voice":
            audio = make_silence(str(root/"voiceover"/"narration.wav"), req.target_minutes*60)
            out = base | {"provider":"demo","audio":audio,"duration_seconds":req.target_minutes*60}
        elif stage == "visuals":
            out = base | {"assets":[{"kind":"broll","query":req.topic,"duration_seconds":8},{"kind":"graphic","query":"key statistic","duration_seconds":5}]}
        elif stage == "timeline":
            out = base | {"edl":[{"start":0,"end":8,"asset":"broll-01"},{"start":8,"end":13,"asset":"graphic-01"}],"fps":30,"aspect_ratio":"16:9"}
        elif stage == "render":
            rendered = render_placeholder(root)
            out = base | {"renderer":"ffmpeg","output":rendered or "final/video.mp4","render_status":"ready" if rendered else "planned"}
        elif stage == "thumbnail":
            thumb = make_thumbnail(f"THE TRUTH ABOUT {req.topic.upper()}", str(root/"thumbnail"/"thumbnail.png"))
            out = base | {"output":thumb,"concepts":[{"hook":f"THE TRUTH ABOUT {req.topic.upper()}","composition":"single focal subject + strong text"}]}
        elif stage == "seo":
            out = base | {"titles":[f"The Truth About {req.topic}",f"How {req.topic} Really Works",f"What Nobody Tells You About {req.topic}"],"description":f"A researched video exploring {req.topic}.","keywords":[req.topic,req.format,"YouTube"]}
        else:
            out = base | {"chapters":[{"time":"00:00","title":"The hook"},{"time":"01:00","title":"Context"},{"time":"06:00","title":"What it means"}]}
        outputs[stage] = out
        (root/f"{stage}.json").write_text(json.dumps(out,indent=2), encoding="utf-8")
    manifest = {"job_id":job_id,"topic":req.topic,"format":req.format,"target_minutes":req.target_minutes,"status":"succeeded","stages":STAGES,"outputs":outputs}
    (root/"manifest.json").write_text(json.dumps(manifest,indent=2), encoding="utf-8")
    return manifest

@app.get("/health")
def health(): return {"status":"ok","service":"youtube-high-profit-api"}

@app.post("/api/jobs")
def create_job(req: GenerateRequest, bg: BackgroundTasks):
    job_id = str(uuid.uuid4())
    job = {"id":job_id,"topic":req.topic,"format":req.format,"target_minutes":req.target_minutes,"status":"queued","progress":0,"stages":[]}
    with LOCK: JOBS[job_id] = job
    persist_job(job)
    def work():
        try:
            with LOCK: JOBS[job_id].update(status="running",progress=5)
            result = demo_run(job_id,req)
            with LOCK: JOBS[job_id] = {"id":job_id,"topic":req.topic,"format":req.format,"target_minutes":req.target_minutes,"status":"succeeded","progress":100,"stages":[{"name":s,"status":"succeeded"} for s in STAGES],"result":result}
            persist_job(JOBS[job_id])
        except Exception as e:
            with LOCK: JOBS[job_id].update(status="failed",error=str(e))
            persist_job(JOBS[job_id])
    bg.add_task(work)
    return {"job_id":job_id,"status":"queued"}

@app.get("/api/jobs/{job_id}")
def get_job(job_id:str):
    with LOCK: job=JOBS.get(job_id)
    if not job: raise HTTPException(404,"job not found")
    return job
