
from fastapi import APIRouter
import sqlite3
import uuid

router = APIRouter(prefix='/v1/finance', tags=['finance'])

DB='deployments/little-oaks/data/education.db'

def db():
    return sqlite3.connect(DB)

@router.post('/invoice/{student_id}')
def create_invoice(student_id:int, amount:float):
    conn=db()
    cur=conn.cursor()
    number='INV-'+str(uuid.uuid4())[:8]
    cur.execute(
        'INSERT INTO invoices(student_id,amount,invoice_number) VALUES(?,?,?)',
        (student_id,amount,number)
    )
    conn.commit()
    conn.close()
    return {
        'invoice_number':number,
        'student_id':student_id,
        'amount':amount,
        'status':'unpaid'
    }

@router.post('/payment/{invoice_id}')
def record_payment(invoice_id:int, amount:float, method:str='cash'):
    conn=db()
    cur=conn.cursor()
    cur.execute(
        'INSERT INTO receipts(invoice_id,amount,payment_method) VALUES(?,?,?)',
        (invoice_id,amount,method)
    )
    cur.execute(
        'UPDATE invoices SET status=? WHERE id=?',
        ('paid',invoice_id)
    )
    conn.commit()
    conn.close()
    return {
        'invoice_id':invoice_id,
        'amount':amount,
        'method':method,
        'status':'paid'
    }

@router.get('/reports')
def reports():
    conn=db()
    cur=conn.cursor()
    data={
        'invoices':cur.execute('SELECT COUNT(*) FROM invoices').fetchone()[0],
        'payments':cur.execute('SELECT COALESCE(SUM(amount),0) FROM receipts').fetchone()[0]
    }
    conn.close()
    return data
