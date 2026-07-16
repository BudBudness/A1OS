import json, psycopg2, psycopg2.extras, uuid, hashlib
from datetime import datetime, date, timedelta

class PosWorker:
    def __init__(self):
        self.name = "pos"
        self.DB_PATH = "dbname=a1os_db user=u0_a433 host=/data/data/com.termux/files/usr/tmp"
        self._ensure_tables()

    def _get_db(self):
        return psycopg2.connect(self.DB_PATH)

    def _ensure_tables(self):
        conn = self._get_db(); cur = conn.cursor()
        tables = [
            "CREATE TABLE IF NOT EXISTS coffee_beans (id SERIAL PRIMARY KEY, name TEXT, origin TEXT, variety TEXT, process TEXT, roast_level TEXT, price_per_kg DECIMAL(10,2), stock_kg DECIMAL(10,2), created_at TIMESTAMP DEFAULT NOW())",
            "CREATE TABLE IF NOT EXISTS coffee_batches (id SERIAL PRIMARY KEY, bean_id INT REFERENCES coffee_beans(id), weight_kg DECIMAL(10,2), green_weight DECIMAL(10,2), roasted_weight DECIMAL(10,2), roast_date DATE, roast_master TEXT, notes TEXT, created_at TIMESTAMP DEFAULT NOW())",
            "CREATE TABLE IF NOT EXISTS products (id SERIAL PRIMARY KEY, name TEXT, price DECIMAL(10,2), category TEXT, stock INT DEFAULT 0, active BOOLEAN DEFAULT TRUE, created_at TIMESTAMP DEFAULT NOW())",
            "CREATE TABLE IF NOT EXISTS tables (id SERIAL PRIMARY KEY, table_number INT UNIQUE, capacity INT, section TEXT, status TEXT DEFAULT 'available')",
            "CREATE TABLE IF NOT EXISTS orders (id SERIAL PRIMARY KEY, table_id INT, customer_id INT, items JSONB, total DECIMAL(10,2), tax DECIMAL(10,2), discount DECIMAL(10,2), status TEXT DEFAULT 'pending', order_type TEXT, notes TEXT, created_at TIMESTAMP DEFAULT NOW())",
            "CREATE TABLE IF NOT EXISTS properties (id SERIAL PRIMARY KEY, name TEXT, description TEXT, property_type TEXT, bedrooms INT, bathrooms INT, capacity INT, base_price DECIMAL(10,2), cleaning_fee DECIMAL(10,2), active BOOLEAN DEFAULT TRUE, created_at TIMESTAMP DEFAULT NOW())",
            "CREATE TABLE IF NOT EXISTS bookings (id SERIAL PRIMARY KEY, property_id INT, customer_name TEXT, check_in DATE, check_out DATE, guests INT, total_price DECIMAL(10,2), status TEXT DEFAULT 'confirmed', created_at TIMESTAMP DEFAULT NOW())",
            "CREATE TABLE IF NOT EXISTS customers (id SERIAL PRIMARY KEY, name TEXT, phone TEXT, email TEXT, customer_type TEXT, created_at TIMESTAMP DEFAULT NOW())",
            "CREATE TABLE IF NOT EXISTS employees (id SERIAL PRIMARY KEY, name TEXT, role TEXT, salary DECIMAL(10,2), paid BOOLEAN DEFAULT FALSE, created_at TIMESTAMP DEFAULT NOW())",
            "CREATE TABLE IF NOT EXISTS payments (id SERIAL PRIMARY KEY, customer_name TEXT, amount DECIMAL(10,2), method TEXT, reference TEXT, created_at TIMESTAMP DEFAULT NOW())",
            "CREATE TABLE IF NOT EXISTS utilities (id SERIAL PRIMARY KEY, type TEXT, amount DECIMAL(10,2), units DECIMAL(10,2), month TEXT, created_at TIMESTAMP DEFAULT NOW())"
        ]
        for sql in tables:
            try: cur.execute(sql)
            except: pass
        conn.commit(); cur.close(); conn.close()

    async def process(self, payload):
        action = payload.get('action'); data = payload.get('data', {})
        
        # Coffee Roastery
        if action == "add_bean": return self._add_bean(data)
        if action == "get_beans": return self._get_beans()
        if action == "update_bean_stock": return self._update_bean_stock(data)
        if action == "create_batch": return self._create_batch(data)
        
        # Bar/Restaurant
        if action == "create_order": return self._create_order(data)
        if action == "get_orders": return self._get_orders(data)
        if action == "update_order_status": return self._update_order_status(data)
        if action == "get_tables": return self._get_tables()
        if action == "get_menu": return self._get_menu()
        if action == "assign_table": return self._assign_table(data)
        if action == "release_table": return self._release_table(data)
        
        # Airbnb
        if action == "create_booking": return self._create_booking(data)
        if action == "get_bookings": return self._get_bookings()
        if action == "get_properties": return self._get_properties()
        if action == "cancel_booking": return self._cancel_booking(data)
        if action == "check_availability": return self._check_availability(data)
        
        # Payments
        if action == "add_payment": return self._add_payment(data)
        if action == "get_payments": return self._get_payments()
        if action == "payment_summary": return self._payment_summary()
        
        # Employees
        if action == "add_employee": return self._add_employee(data)
        if action == "get_employees": return self._get_employees()
        if action == "mark_paid": return self._mark_paid(data)
        if action == "payroll_summary": return self._payroll_summary()
        
        # Customers
        if action == "add_customer": return self._add_customer(data)
        if action == "get_customers": return self._get_customers()
        if action == "get_customer": return self._get_customer(data)
        
        # Utilities
        if action == "add_utility": return self._add_utility(data)
        if action == "get_utilities": return self._get_utilities()
        
        # Reports
        if action == "daily_report": return self._daily_report()
        if action == "weekly_report": return self._weekly_report()
        if action == "monthly_report": return self._monthly_report()
        
        return {"error": f"Unknown action: {action}"}

    # --- COFFEE ROASTERY ---
    def _add_bean(self, data):
        if not data.get('name'): return {"error": "Bean name is required"}
        conn = self._get_db(); cur = conn.cursor()
        cur.execute("INSERT INTO coffee_beans (name, origin, variety, process, roast_level, price_per_kg, stock_kg) VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id", 
                    (data.get('name'), data.get('origin'), data.get('variety'), data.get('process'), data.get('roast_level'), data.get('price_per_kg'), data.get('stock_kg')))
        id = cur.fetchone()[0]; conn.commit(); cur.close(); conn.close()
        return {"status":"success","message":"Bean added","id":id}

    def _get_beans(self):
        conn = self._get_db(); cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM coffee_beans ORDER BY name")
        beans = cur.fetchall(); cur.close(); conn.close()
        return {"beans":[dict(b) for b in beans]}

    def _update_bean_stock(self, data):
        if not data.get('bean_id') or data.get('quantity') is None: return {"error": "bean_id and quantity required"}
        conn = self._get_db(); cur = conn.cursor()
        cur.execute("UPDATE coffee_beans SET stock_kg = stock_kg + %s WHERE id = %s RETURNING id", (data.get('quantity'), data.get('bean_id')))
        result = cur.fetchone(); conn.commit(); cur.close(); conn.close()
        if result: return {"status":"success","message":"Stock updated"}
        return {"error":"Bean not found"}

    def _create_batch(self, data):
        if not data.get('bean_id'): return {"error": "bean_id required"}
        conn = self._get_db(); cur = conn.cursor()
        cur.execute("INSERT INTO coffee_batches (bean_id, weight_kg, green_weight, roasted_weight, roast_date, roast_master, notes) VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                    (data.get('bean_id'), data.get('weight_kg'), data.get('green_weight'), data.get('roasted_weight'), data.get('roast_date'), data.get('roast_master'), data.get('notes')))
        id = cur.fetchone()[0]; conn.commit(); cur.close(); conn.close()
        return {"status":"success","message":"Batch created","id":id}

    # --- BAR/RESTAURANT ---
    def _create_order(self, data):
        items = data.get('items', [])
        if not items: return {"error": "Items required"}
        subtotal = sum(i.get('price',0)*i.get('qty',1) for i in items)
        tax = subtotal * 0.16
        total = subtotal + tax - data.get('discount',0)
        conn = self._get_db(); cur = conn.cursor()
        cur.execute("INSERT INTO orders (table_id, customer_id, items, total, tax, discount, status, order_type, notes) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id", 
                    (data.get('table_id'), data.get('customer_id'), json.dumps(items), total, tax, data.get('discount',0), 'pending', data.get('order_type','dine-in'), data.get('notes')))
        order_id = cur.fetchone()[0]
        if data.get('table_id'):
            cur.execute("UPDATE tables SET status='occupied' WHERE id=%s", (data.get('table_id'),))
        conn.commit(); cur.close(); conn.close()
        return {"status":"success","message":"Order created","order_id":order_id,"total":total}

    def _get_orders(self, data):
        status_filter = data.get('status', 'all')
        conn = self._get_db(); cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        if status_filter == 'all':
            cur.execute("SELECT * FROM orders ORDER BY created_at DESC LIMIT 50")
        else:
            cur.execute("SELECT * FROM orders WHERE status=%s ORDER BY created_at DESC LIMIT 50", (status_filter,))
        orders = cur.fetchall(); cur.close(); conn.close()
        return {"orders":[dict(o) for o in orders]}

    def _update_order_status(self, data):
        if not data.get('order_id') or not data.get('status'): return {"error": "order_id and status required"}
        conn = self._get_db(); cur = conn.cursor()
        cur.execute("UPDATE orders SET status=%s WHERE id=%s RETURNING id", (data.get('status'), data.get('order_id')))
        result = cur.fetchone(); conn.commit(); cur.close(); conn.close()
        if result: return {"status":"success","message":"Order status updated"}
        return {"error":"Order not found"}

    def _get_tables(self):
        conn = self._get_db(); cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM tables ORDER BY table_number")
        tables = cur.fetchall(); cur.close(); conn.close()
        return {"tables":[dict(t) for t in tables]}

    def _get_menu(self):
        conn = self._get_db(); cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM products WHERE active=true ORDER BY category, name")
        items = cur.fetchall(); cur.close(); conn.close()
        return {"menu":[dict(i) for i in items]}

    def _assign_table(self, data):
        if not data.get('table_id'): return {"error": "table_id required"}
        conn = self._get_db(); cur = conn.cursor()
        cur.execute("UPDATE tables SET status='occupied' WHERE id=%s RETURNING id", (data.get('table_id'),))
        result = cur.fetchone(); conn.commit(); cur.close(); conn.close()
        if result: return {"status":"success","message":"Table assigned"}
        return {"error":"Table not found"}

    def _release_table(self, data):
        if not data.get('table_id'): return {"error": "table_id required"}
        conn = self._get_db(); cur = conn.cursor()
        cur.execute("UPDATE tables SET status='available' WHERE id=%s RETURNING id", (data.get('table_id'),))
        result = cur.fetchone(); conn.commit(); cur.close(); conn.close()
        if result: return {"status":"success","message":"Table released"}
        return {"error":"Table not found"}

    # --- AIRBNB ---
    def _create_booking(self, data):
        property_id = data.get('property_id'); check_in = data.get('check_in'); check_out = data.get('check_out')
        if not property_id or not check_in or not check_out: return {"error": "property_id, check_in, check_out required"}
        nights = (datetime.strptime(check_out,'%Y-%m-%d') - datetime.strptime(check_in,'%Y-%m-%d')).days
        conn = self._get_db(); cur = conn.cursor()
        cur.execute("SELECT base_price, cleaning_fee FROM properties WHERE id=%s", (property_id,))
        prop = cur.fetchone()
        total = (prop[0] * nights) + prop[1] if prop else 0
        cur.execute("INSERT INTO bookings (property_id, customer_name, check_in, check_out, guests, total_price) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id", 
                    (property_id, data.get('customer_name','Guest'), check_in, check_out, data.get('guests',2), total))
        booking_id = cur.fetchone()[0]; conn.commit(); cur.close(); conn.close()
        return {"status":"success","message":"Booking created","booking_id":booking_id,"total":total}

    def _get_bookings(self):
        conn = self._get_db(); cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM bookings WHERE check_in >= CURRENT_DATE ORDER BY check_in LIMIT 50")
        bookings = cur.fetchall(); cur.close(); conn.close()
        return {"bookings":[dict(b) for b in bookings]}

    def _get_properties(self):
        conn = self._get_db(); cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM properties WHERE active=true")
        props = cur.fetchall(); cur.close(); conn.close()
        return {"properties":[dict(p) for p in props]}

    def _cancel_booking(self, data):
        if not data.get('booking_id'): return {"error": "booking_id required"}
        conn = self._get_db(); cur = conn.cursor()
        cur.execute("UPDATE bookings SET status='cancelled' WHERE id=%s RETURNING id", (data.get('booking_id'),))
        result = cur.fetchone(); conn.commit(); cur.close(); conn.close()
        if result: return {"status":"success","message":"Booking cancelled"}
        return {"error":"Booking not found"}

    def _check_availability(self, data):
        property_id = data.get('property_id'); check_in = data.get('check_in'); check_out = data.get('check_out')
        if not property_id or not check_in or not check_out: return {"error": "Missing parameters"}
        conn = self._get_db(); cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM bookings WHERE property_id=%s AND status != 'cancelled' AND check_in < %s AND check_out > %s", 
                    (property_id, check_out, check_in))
        count = cur.fetchone()[0]; cur.close(); conn.close()
        return {"available": count == 0}

    # --- PAYMENTS ---
    def _add_payment(self, data):
        if not data.get('amount'): return {"error": "Amount required"}
        conn = self._get_db(); cur = conn.cursor()
        cur.execute("INSERT INTO payments (customer_name, amount, method, reference) VALUES (%s,%s,%s,%s) RETURNING id", 
                    (data.get('customer_name','Guest'), data.get('amount'), data.get('method','cash'), data.get('reference')))
        pid = cur.fetchone()[0]; conn.commit(); cur.close(); conn.close()
        return {"status":"success","message":"Payment recorded","payment_id":pid}

    def _get_payments(self):
        conn = self._get_db(); cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM payments ORDER BY created_at DESC LIMIT 50")
        payments = cur.fetchall(); cur.close(); conn.close()
        return {"payments":[dict(p) for p in payments]}

    def _payment_summary(self):
        conn = self._get_db(); cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT method, COUNT(*) as count, SUM(amount) as total FROM payments WHERE DATE(created_at)=CURRENT_DATE GROUP BY method")
        summary = cur.fetchall(); cur.close(); conn.close()
        total = sum(s['total'] for s in summary) if summary else 0
        return {"date":str(date.today()), "summary":[dict(s) for s in summary], "total":float(total)}

    # --- EMPLOYEES ---
    def _add_employee(self, data):
        if not data.get('name'): return {"error": "Name required"}
        conn = self._get_db(); cur = conn.cursor()
        cur.execute("INSERT INTO employees (name, role, salary) VALUES (%s,%s,%s) RETURNING id", (data.get('name'), data.get('role','Staff'), data.get('salary',0)))
        eid = cur.fetchone()[0]; conn.commit(); cur.close(); conn.close()
        return {"status":"success","message":"Employee added","id":eid}

    def _get_employees(self):
        conn = self._get_db(); cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM employees ORDER BY name")
        emps = cur.fetchall(); cur.close(); conn.close()
        return {"employees":[dict(e) for e in emps]}

    def _mark_paid(self, data):
        if not data.get('employee_id'): return {"error": "employee_id required"}
        conn = self._get_db(); cur = conn.cursor()
        cur.execute("UPDATE employees SET paid=true WHERE id=%s RETURNING id", (data.get('employee_id'),))
        result = cur.fetchone(); conn.commit(); cur.close(); conn.close()
        if result: return {"status":"success","message":"Marked paid"}
        return {"error":"Employee not found"}

    def _payroll_summary(self):
        conn = self._get_db(); cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT role, COUNT(*) as count, SUM(salary) as total_salary FROM employees GROUP BY role")
        summary = cur.fetchall(); cur.close(); conn.close()
        return {"payroll":[dict(s) for s in summary]}

    # --- CUSTOMERS ---
    def _add_customer(self, data):
        if not data.get('name'): return {"error": "Name required"}
        conn = self._get_db(); cur = conn.cursor()
        cur.execute("INSERT INTO customers (name, phone, email, customer_type) VALUES (%s,%s,%s,%s) RETURNING id", 
                    (data.get('name'), data.get('phone'), data.get('email'), data.get('customer_type','retail')))
        cid = cur.fetchone()[0]; conn.commit(); cur.close(); conn.close()
        return {"status":"success","message":"Customer added","id":cid}

    def _get_customers(self):
        conn = self._get_db(); cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM customers ORDER BY name LIMIT 50")
        cust = cur.fetchall(); cur.close(); conn.close()
        return {"customers":[dict(c) for c in cust]}

    def _get_customer(self, data):
        conn = self._get_db(); cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        if data.get('id'):
            cur.execute("SELECT * FROM customers WHERE id=%s", (data.get('id'),))
        elif data.get('phone'):
            cur.execute("SELECT * FROM customers WHERE phone=%s", (data.get('phone'),))
        else:
            return {"error": "id or phone required"}
        cust = cur.fetchone(); cur.close(); conn.close()
        return {"customer": dict(cust) if cust else None}

    # --- UTILITIES ---
    def _add_utility(self, data):
        if not data.get('type') or not data.get('amount'): return {"error": "Type and amount required"}
        conn = self._get_db(); cur = conn.cursor()
        cur.execute("INSERT INTO utilities (type, amount, units, month) VALUES (%s,%s,%s,%s) RETURNING id", 
                    (data.get('type'), data.get('amount'), data.get('units'), data.get('month', datetime.now().strftime('%Y-%m'))))
        uid = cur.fetchone()[0]; conn.commit(); cur.close(); conn.close()
        return {"status":"success","message":"Utility added","id":uid}

    def _get_utilities(self):
        conn = self._get_db(); cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM utilities ORDER BY created_at DESC LIMIT 20")
        utils = cur.fetchall(); cur.close(); conn.close()
        return {"utilities":[dict(u) for u in utils]}

    # --- REPORTS ---
    def _daily_report(self):
        conn = self._get_db(); cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT COUNT(*) as count, COALESCE(SUM(total),0) as revenue FROM orders WHERE DATE(created_at)=CURRENT_DATE AND status='completed'")
        orders = cur.fetchone()
        cur.execute("SELECT COUNT(*) as count, COALESCE(SUM(total_price),0) as revenue FROM bookings WHERE DATE(created_at)=CURRENT_DATE AND status='confirmed'")
        bookings = cur.fetchone()
        cur.execute("SELECT COALESCE(SUM(amount),0) as revenue FROM payments WHERE DATE(created_at)=CURRENT_DATE")
        payments = cur.fetchone()
        cur.close(); conn.close()
        total = float(orders['revenue'] or 0) + float(bookings['revenue'] or 0) + float(payments['revenue'] or 0)
        return {"date":str(date.today()), "orders":{"count":orders['count'] or 0, "revenue":float(orders['revenue'] or 0)}, "bookings":{"count":bookings['count'] or 0, "revenue":float(bookings['revenue'] or 0)}, "payments":{"revenue":float(payments['revenue'] or 0)}, "total":total}

    def _weekly_report(self):
        conn = self._get_db(); cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT DATE(created_at) as date, COUNT(*) as count, COALESCE(SUM(total),0) as revenue FROM orders WHERE created_at > NOW() - INTERVAL '7 days' AND status='completed' GROUP BY DATE(created_at) ORDER BY date")
        data = cur.fetchall(); cur.close(); conn.close()
        return {"week":[{"date":str(d['date']), "count":d['count'], "revenue":float(d['revenue'] or 0)} for d in data]}

    def _monthly_report(self):
        conn = self._get_db(); cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT DATE_TRUNC('day', created_at) as date, COUNT(*) as count, COALESCE(SUM(total),0) as revenue FROM orders WHERE created_at > NOW() - INTERVAL '30 days' AND status='completed' GROUP BY date ORDER BY date")
        data = cur.fetchall(); cur.close(); conn.close()
        return {"month":[{"date":str(d['date']), "count":d['count'], "revenue":float(d['revenue'] or 0)} for d in data]}
