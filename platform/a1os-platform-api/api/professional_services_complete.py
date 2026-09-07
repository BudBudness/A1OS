import sqlite3,uuid
from datetime import datetime
from fastapi import APIRouter,HTTPException
from pydantic import BaseModel
from pathlib import Path
DB="/data/data/com.termux/files/home/A1OS_RESTORED/data/professional_services.db"
router=APIRouter(prefix="/v1/professional-services",tags=["professional-services"])
def db():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def audit(c,action,resource,rid=None):
 c.execute("INSERT INTO professional_services_audit_log(tenant_id,actor,action,resource,resource_id) VALUES(?,?,?,?,?)",("primary-tenant","system",action,resource,rid))
class Payment(BaseModel):
 invoice_id:str
 amount:float
 currency:str="UGX"
 payment_method:str="cash"
 reference:str|None=None
 payment_date:str|None=None
 notes:str|None=None
class Task(BaseModel):
 client_id:str|None=None; project_id:str|None=None; title:str; description:str|None=None
 status:str="todo"; priority:str="medium"; due_date:str|None=None; assigned_to:str|None=None
class Document(BaseModel):
 client_id:str|None=None; project_id:str|None=None; name:str
 document_type:str="general"; storage_path:str|None=None; status:str="active"
class Setting(BaseModel):
 key:str; value:str|None=None
@router.get("/payments")
def payments():
 c=db(); x=[dict(r) for r in c.execute("SELECT p.*,i.invoice_number FROM professional_services_payments p LEFT JOIN professional_services_invoices i ON i.id=p.invoice_id ORDER BY p.created_at DESC")]; c.close(); return {"payments":x,"count":len(x)}
@router.post("/payments")
def payment(p:Payment):
 if p.amount<=0: raise HTTPException(400,"Payment amount must be positive")
 c=db(); i=c.execute("SELECT * FROM professional_services_invoices WHERE id=?",(p.invoice_id,)).fetchone()
 if not i: c.close(); raise HTTPException(404,"Invoice not found")
 outstanding=max(float(i["amount"])-float(i["paid_amount"] or 0),0)
 if p.amount>outstanding: c.close(); raise HTTPException(400,"Payment exceeds invoice outstanding balance")
 rid=str(uuid.uuid4())
 c.execute("INSERT INTO professional_services_payments(id,tenant_id,invoice_id,client_id,amount,currency,payment_method,reference,payment_date,notes) VALUES(?,?,?,?,?,?,?,?,?,?)",(rid,"primary-tenant",p.invoice_id,i["client_id"],p.amount,p.currency,p.payment_method,p.reference,p.payment_date,p.notes))
 paid=float(i["paid_amount"] or 0)+p.amount
 status="paid" if paid>=float(i["amount"]) else "partial"
 c.execute("UPDATE professional_services_invoices SET paid_amount=?,status=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",(paid,status,p.invoice_id)); audit(c,"create","payment",rid); audit(c,"payment_applied","invoice",p.invoice_id); c.commit(); c.close()
 return {"id":rid,"invoice_id":p.invoice_id,"amount":p.amount,"invoice_paid_amount":paid,"invoice_status":status}
@router.delete("/payments/{rid}")
def payment_delete(rid:str):
 c=db(); p=c.execute("SELECT * FROM professional_services_payments WHERE id=?",(rid,)).fetchone()
 if not p: c.close(); raise HTTPException(404,"Payment not found")
 i=c.execute("SELECT * FROM professional_services_invoices WHERE id=?",(p["invoice_id"],)).fetchone()
 paid=max(float(i["paid_amount"] or 0)-float(p["amount"]),0)
 status="paid" if paid>=float(i["amount"]) else ("partial" if paid else "unpaid")
 c.execute("UPDATE professional_services_invoices SET paid_amount=?,status=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",(paid,status,p["invoice_id"]))
 c.execute("DELETE FROM professional_services_payments WHERE id=?",(rid,)); audit(c,"delete","payment",rid); c.commit(); c.close(); return {"deleted":True,"id":rid}
@router.get("/tasks")
def tasks():
 c=db(); x=[dict(r) for r in c.execute("SELECT * FROM professional_services_tasks ORDER BY created_at DESC")]; c.close(); return {"tasks":x,"count":len(x)}
@router.post("/tasks")
def task(x:Task):
 c=db(); rid=str(uuid.uuid4()); c.execute("INSERT INTO professional_services_tasks(id,tenant_id,client_id,project_id,title,description,status,priority,due_date,assigned_to) VALUES(?,?,?,?,?,?,?,?,?,?)",(rid,"primary-tenant",x.client_id,x.project_id,x.title,x.description,x.status,x.priority,x.due_date,x.assigned_to)); audit(c,"create","task",rid); c.commit(); c.close(); return {"id":rid,**x.model_dump()}
@router.put("/tasks/{rid}")
def task_update(rid:str,x:Task):
 c=db()
 if not c.execute("SELECT id FROM professional_services_tasks WHERE id=?",(rid,)).fetchone(): c.close(); raise HTTPException(404,"Task not found")
 c.execute("UPDATE professional_services_tasks SET client_id=?,project_id=?,title=?,description=?,status=?,priority=?,due_date=?,assigned_to=? WHERE id=?",(x.client_id,x.project_id,x.title,x.description,x.status,x.priority,x.due_date,x.assigned_to,rid)); audit(c,"update","task",rid); c.commit(); c.close(); return {"id":rid,**x.model_dump()}
@router.delete("/tasks/{rid}")
def task_delete(rid:str):
 c=db(); q=c.execute("DELETE FROM professional_services_tasks WHERE id=?",(rid,)); audit(c,"delete","task",rid); c.commit(); c.close()
 if not q.rowcount: raise HTTPException(404,"Task not found")
 return {"deleted":True,"id":rid}
@router.get("/documents")
def documents():
 c=db(); x=[dict(r) for r in c.execute("SELECT * FROM professional_services_documents ORDER BY created_at DESC")]; c.close(); return {"documents":x,"count":len(x)}
@router.post("/documents")
def document(x:Document):
 c=db(); rid=str(uuid.uuid4()); c.execute("INSERT INTO professional_services_documents(id,tenant_id,client_id,project_id,name,document_type,storage_path,status) VALUES(?,?,?,?,?,?,?,?)",(rid,"primary-tenant",x.client_id,x.project_id,x.name,x.document_type,x.storage_path,x.status)); audit(c,"create","document",rid); c.commit(); c.close(); return {"id":rid,**x.model_dump()}
@router.delete("/documents/{rid}")
def document_delete(rid:str):
 c=db(); q=c.execute("DELETE FROM professional_services_documents WHERE id=?",(rid,)); audit(c,"delete","document",rid); c.commit(); c.close()
 if not q.rowcount: raise HTTPException(404,"Document not found")
 return {"deleted":True,"id":rid}
@router.get("/settings")
def settings():
 c=db(); x={r["setting_key"]:r["setting_value"] for r in c.execute("SELECT setting_key,setting_value FROM professional_services_settings")}; c.close(); return {"settings":x}
@router.put("/settings")
def setting(x:Setting):
 c=db(); c.execute("INSERT INTO professional_services_settings(id,tenant_id,setting_key,setting_value,updated_at) VALUES(?,?,?,?,CURRENT_TIMESTAMP) ON CONFLICT(tenant_id,setting_key) DO UPDATE SET setting_value=excluded.setting_value,updated_at=CURRENT_TIMESTAMP",(str(uuid.uuid4()),"primary-tenant",x.key,x.value)); audit(c,"update","setting",x.key); c.commit(); c.close(); return {"key":x.key,"value":x.value}
@router.get("/reports/financial")
def financial():
 c=db(); a=c.execute("SELECT COALESCE(SUM(amount),0) n FROM professional_services_invoices").fetchone()["n"]; p=c.execute("SELECT COALESCE(SUM(amount),0) n FROM professional_services_payments").fetchone()["n"]; c.close(); return {"currency":"UGX","invoiced":a,"paid":p,"outstanding":max(a-p,0)}
@router.get("/reports/receivables")
def receivables():
 c=db(); x=[dict(r) for r in c.execute("SELECT i.id,i.invoice_number,i.title,i.amount,i.paid_amount,MAX(i.amount-i.paid_amount,0) outstanding,i.due_date,c.name client_name FROM professional_services_invoices i LEFT JOIN professional_services_clients c ON c.id=i.client_id WHERE i.amount>i.paid_amount ORDER BY i.due_date")]; c.close(); return {"receivables":x,"count":len(x)}
