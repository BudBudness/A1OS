from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import sqlite3, uuid
ROOT=Path(__file__).resolve().parents[3]
DB=ROOT/"data"/"construction.db"
router=APIRouter(prefix="/v1/construction",tags=["construction"])
RESOURCES={
 "projects":("id,name,description,status,client_name,budget,start_date,end_date"),
 "clients":("id,name,company,email,phone"),
 "estimates":("id,title,description,amount,status,client_id"),
 "invoices":("id,title,description,amount,paid_amount,status,due_date,client_id"),
 "payments":("id,invoice_id,amount,method,paid_at"),
 "tasks":("id,title,description,status,due_date,project_id"),
 "materials":("id,name,unit,quantity,unit_cost,project_id"),
 "sites":("id,name,location,client_id,status"),
}
FIELDS={
 "projects":["name","description","status","client_name","budget","start_date","end_date"],
 "clients":["name","company","email","phone"],
 "estimates":["title","description","amount","status","client_id"],
 "invoices":["title","description","amount","paid_amount","status","due_date","client_id"],
 "payments":["invoice_id","amount","method","paid_at"],
 "tasks":["title","description","status","due_date","project_id"],
 "materials":["name","unit","quantity","unit_cost","project_id"],
 "sites":["name","location","client_id","status"],
}
def db():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; c.execute("PRAGMA foreign_keys=ON"); return c
def init():
 c=db()
 for r,fs in FIELDS.items():
  cols=", ".join(["id TEXT PRIMARY KEY"]+[f"{f} TEXT" for f in fs]+["tenant_id TEXT NOT NULL DEFAULT 'primary-tenant'","created_at TEXT DEFAULT CURRENT_TIMESTAMP","updated_at TEXT DEFAULT CURRENT_TIMESTAMP"])
  c.execute(f"CREATE TABLE IF NOT EXISTS construction_{r} ({cols})")
 c.commit(); c.close()
init()
class Payload(BaseModel):
 data: dict={}
@router.get("/{resource}")
def list_resource(resource:str):
 if resource not in RESOURCES: raise HTTPException(404,"unknown construction resource")
 c=db(); rows=c.execute(f"SELECT * FROM construction_{resource} ORDER BY created_at DESC").fetchall(); c.close()
 return {resource:[dict(x) for x in rows],"count":len(rows)}
@router.post("/{resource}")
def create_resource(resource:str,p:Payload):
 if resource not in FIELDS: raise HTTPException(404,"unknown construction resource")
 data={k:v for k,v in p.data.items() if k in FIELDS[resource]}
 if resource in ("projects","clients","estimates","invoices","tasks","materials","sites") and not data.get(FIELDS[resource][0]): raise HTTPException(400,"required field missing")
 if resource in ("projects","estimates","invoices","materials") and data.get("amount") is not None and float(data["amount"])<0: raise HTTPException(400,"amount cannot be negative")
 if resource=="materials" and data.get("quantity") is not None and float(data["quantity"])<0: raise HTTPException(400,"quantity cannot be negative")
 rid=str(uuid.uuid4()); data["id"]=rid
 c=db(); cols=list(data); vals=[data[k] for k in cols]; c.execute(f"INSERT INTO construction_{resource} ({','.join(cols)}) VALUES ({','.join('?' for _ in vals)})",vals); c.commit(); c.close()
 return {"id":rid,"status":"created","resource":resource}
@router.delete("/{resource}/{rid}")
def delete_resource(resource:str,rid:str):
 if resource not in FIELDS: raise HTTPException(404,"unknown construction resource")
 c=db(); cur=c.execute(f"DELETE FROM construction_{resource} WHERE id=?",(rid,)); c.commit(); c.close()
 if not cur.rowcount: raise HTTPException(404,"record not found")
 return {"status":"deleted","id":rid,"resource":resource}
@router.get("/reports/summary")
def summary():
 c=db()
 out={}
 for r in FIELDS:
  out[r]=c.execute(f"SELECT COUNT(*) FROM construction_{r}").fetchone()[0]
 out["project_budget"]=c.execute("SELECT COALESCE(SUM(CAST(budget AS REAL)),0) FROM construction_projects").fetchone()[0]
 out["invoice_value"]=c.execute("SELECT COALESCE(SUM(CAST(amount AS REAL)),0) FROM construction_invoices").fetchone()[0]
 out["payments"]=c.execute("SELECT COALESCE(SUM(CAST(amount AS REAL)),0) FROM construction_payments").fetchone()[0]
 c.close(); return out
