"""A1OS-owned API resources for Jere's Car Wash & Parking.

Identity, tenant resolution, authorization and persistence remain platform-owned.
The vertical cannot read or write another organization's records.
"""
from __future__ import annotations

import re
from fastapi import APIRouter, HTTPException, Request


REGISTRATION_RE = re.compile(r"^[A-Z0-9][A-Z0-9 -]{1,15}$")
VEHICLE_STATUSES = {"queued", "washing", "in-progress", "completed", "cancelled"}


def build_car_wash_router(db, require_permission, audit):
    router = APIRouter(prefix="/api/car-wash", tags=["car-wash"])

    @router.get("/dashboard")
    def dashboard(request: Request):
        actor = require_permission(request, "car_wash:read")
        organization_id = actor["organization_id"]
        conn = db()
        try:
            today = conn.execute(
                "SELECT date('now') AS today"
            ).fetchone()["today"]
            vehicles_today = conn.execute(
                """SELECT COUNT(*) AS n FROM car_wash_vehicles
                   WHERE organization_id = ? AND date(created_at) = date('now')
                     AND status != 'cancelled'""",
                (organization_id,),
            ).fetchone()["n"]
            active_vehicles = conn.execute(
                """SELECT COUNT(*) AS n FROM car_wash_vehicles
                   WHERE organization_id = ? AND status IN ('queued','washing','in-progress')""",
                (organization_id,),
            ).fetchone()["n"]
            active_parking = conn.execute(
                """SELECT COUNT(*) AS n FROM car_wash_parking
                   WHERE organization_id = ? AND status = 'active'""",
                (organization_id,),
            ).fetchone()["n"]
            revenue = conn.execute(
                """SELECT COALESCE(SUM(amount), 0) AS total FROM car_wash_payments
                   WHERE organization_id = ? AND date(created_at) = date('now')""",
                (organization_id,),
            ).fetchone()["total"]
            return {
                "date": today,
                "vehiclesToday": vehicles_today,
                "activeVehicles": active_vehicles,
                "parkingOccupancy": active_parking,
                "revenueToday": revenue,
            }
        finally:
            conn.close()

    @router.get("/services")
    def list_services(request: Request):
        actor = require_permission(request, "car_wash:read")
        conn = db()
        try:
            rows = conn.execute(
                """SELECT id, name, price FROM car_wash_services
                   WHERE organization_id = ? AND active = 1 ORDER BY name""",
                (actor["organization_id"],),
            ).fetchall()
            return {"items": [dict(row) for row in rows]}
        finally:
            conn.close()

    @router.post("/services", status_code=201)
    def upsert_service(payload: dict, request: Request):
        actor = require_permission(request, "car_wash:write")
        service_id = str(payload.get("id", "")).strip().lower()
        name = str(payload.get("name", "")).strip()
        try:
            price = float(payload.get("price"))
        except (TypeError, ValueError):
            raise HTTPException(status_code=422, detail="A positive service price is required")
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,47}", service_id):
            raise HTTPException(status_code=422, detail="Service id must be a short lowercase slug")
        if not name or len(name) > 100 or price <= 0:
            raise HTTPException(status_code=422, detail="A service name and positive price are required")
        organization_id = actor["organization_id"]
        conn = db()
        try:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                """INSERT INTO car_wash_services (id, organization_id, name, price, active)
                   VALUES (?, ?, ?, ?, 1)
                   ON CONFLICT (organization_id, id)
                   DO UPDATE SET name = excluded.name, price = excluded.price,
                                 active = 1, updated_at = CURRENT_TIMESTAMP""",
                (service_id, organization_id, name, price),
            )
            audit(conn, actor, "car_wash_service", service_id, "upserted",
                  {"name": name, "price": price})
            conn.commit()
            return {"item": {"id": service_id, "name": name, "price": price}}
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @router.get("/vehicles")
    def list_vehicles(request: Request):
        actor = require_permission(request, "car_wash:read")
        status_filter = request.query_params.get("status", "active")
        if status_filter == "active":
            statuses = ("queued", "washing", "in-progress")
        elif status_filter in VEHICLE_STATUSES:
            statuses = (status_filter,)
        else:
            raise HTTPException(status_code=422, detail="Unsupported vehicle status")
        marks = ",".join("?" for _ in statuses)
        conn = db()
        try:
            rows = conn.execute(
                f"""SELECT id, registration, customer_name, customer_phone,
                           service_id, service_name, service_price, status, notes, created_at
                    FROM car_wash_vehicles
                    WHERE organization_id = ? AND status IN ({marks})
                    ORDER BY created_at DESC LIMIT 200""",
                (actor["organization_id"], *statuses),
            ).fetchall()
            items = []
            for row in rows:
                item = dict(row)
                item["customer"] = {"name": item.pop("customer_name"), "phone": item.pop("customer_phone")}
                item["service"] = {"id": item["service_id"], "name": item["service_name"]}
                item["price"] = item["service_price"]
                items.append(item)
            return {"items": items}
        finally:
            conn.close()

    @router.post("/vehicles", status_code=201)
    def create_vehicle(payload: dict, request: Request):
        actor = require_permission(request, "car_wash:write")
        registration = str(payload.get("registration", "")).strip().upper()
        customer = payload.get("customer") if isinstance(payload.get("customer"), dict) else {}
        customer_name = str(customer.get("name", "")).strip()
        customer_phone = str(customer.get("phone", "")).strip()
        service_id = str(payload.get("serviceId", "")).strip()
        notes = payload.get("notes")
        notes = str(notes).strip() if notes is not None else None
        if not REGISTRATION_RE.fullmatch(registration):
            raise HTTPException(status_code=422, detail="Enter a valid vehicle registration")
        if not customer_name or len(customer_name) > 120:
            raise HTTPException(status_code=422, detail="Customer name is required")
        if not customer_phone or len(customer_phone) > 24:
            raise HTTPException(status_code=422, detail="Customer phone is required")
        if notes and len(notes) > 500:
            raise HTTPException(status_code=422, detail="Notes must be 500 characters or fewer")
        if not service_id:
            raise HTTPException(status_code=422, detail="Select a configured wash service")

        organization_id = actor["organization_id"]
        conn = db()
        try:
            service = conn.execute(
                """SELECT id, name, price FROM car_wash_services
                   WHERE organization_id = ? AND id = ? AND active = 1""",
                (organization_id, service_id),
            ).fetchone()
            if not service:
                raise HTTPException(status_code=422, detail="Wash service is not configured for this organization")
            conn.execute("BEGIN IMMEDIATE")
            cur = conn.execute(
                """INSERT INTO car_wash_vehicles
                   (organization_id, registration, customer_name, customer_phone,
                    service_id, service_name, service_price, status, notes, created_by)
                   VALUES (?, ?, ?, ?, ?, ?, ?, 'queued', ?, ?)""",
                (organization_id, registration, customer_name, customer_phone,
                 service["id"], service["name"], service["price"], notes, actor["id"]),
            )
            vehicle_id = cur.lastrowid
            audit(conn, actor, "car_wash_vehicle", vehicle_id, "created",
                  {"registration": registration, "service_id": service_id})
            conn.commit()
            return {"id": vehicle_id, "status": "queued"}
        except HTTPException:
            conn.rollback()
            raise
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @router.get("/parking")
    def list_parking(request: Request):
        actor = require_permission(request, "car_wash:read")
        status_filter = request.query_params.get("status", "active")
        if status_filter not in {"active", "checked_out"}:
            raise HTTPException(status_code=422, detail="Unsupported parking status")
        conn = db()
        try:
            rows = conn.execute(
                """SELECT id, registration, customer_name, customer_phone,
                          parking_type, status, amount, check_in_at, expected_checkout_at
                   FROM car_wash_parking
                   WHERE organization_id = ? AND status = ?
                   ORDER BY check_in_at DESC LIMIT 200""",
                (actor["organization_id"], status_filter),
            ).fetchall()
            items = []
            for row in rows:
                item = dict(row)
                item["customerName"] = item.pop("customer_name")
                item["customerPhone"] = item.pop("customer_phone")
                item["period"] = "Overnight parking" if item["parking_type"] == "overnight" else "Day parking"
                items.append(item)
            return {"items": items}
        finally:
            conn.close()

    return router
