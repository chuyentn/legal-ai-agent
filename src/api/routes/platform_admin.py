"""
Platform Admin Routes - Super Admin Only
Full system administration for self-hosted deployments
"""
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timedelta
from psycopg2.extras import RealDictCursor
import json
from ..middleware.auth import get_current_user, get_db
from ...services.file_storage import test_google_drive_connector

router = APIRouter(prefix="/v1/platform", tags=["platform-admin"])

# ============================================
# Auth Helper - SUPERADMIN ONLY
# ============================================

async def require_superadmin(current_user: Dict = Depends(get_current_user)):
    """Ensure user is superadmin"""
    if current_user.get("role") != "superadmin":
        raise HTTPException(
            status_code=403, 
            detail="Quyền truy cập bị từ chối. Chỉ dành cho Super Admin."
        )
    return current_user

# ============================================
# Models
# ============================================

class CompanyUpdate(BaseModel):
    plan: Optional[str] = None
    monthly_quota: Optional[int] = None
    used_quota: Optional[int] = None
    is_active: Optional[bool] = None

class UserRoleUpdate(BaseModel):
    role: str

class UserStatusUpdate(BaseModel):
    is_active: bool


class LeadStatusUpdate(BaseModel):
    status: str
    note: Optional[str] = None


class LeadAssignRequest(BaseModel):
    assigned_to_user_id: Optional[str] = None


class LeadConvertRequest(BaseModel):
    plan: str = "enterprise"
    monthly_quota: int = 100000
    user_role: str = "owner"
    note: Optional[str] = None

class PlatformSettings(BaseModel):
    default_llm_provider: Optional[str] = None
    default_llm_model: Optional[str] = None
    max_file_size_mb: Optional[int] = None
    max_queries_per_day_free: Optional[int] = None
    max_contracts_free: Optional[int] = None
    registration_enabled: Optional[bool] = None
    require_email_verification: Optional[bool] = None
    allowed_file_types: Optional[List[str]] = None
    maintenance_mode: Optional[bool] = None
    maintenance_message: Optional[str] = None
    feature_flags: Optional[Dict] = None


class GoogleDriveConnectorUpdate(BaseModel):
    service_account_json: Dict[str, Any]
    root_folder_id: Optional[str] = None
    auto_backup: bool = True
    realtime_sync: bool = True
    is_default: bool = True
    is_active: bool = True

# ============================================
# DASHBOARD
# ============================================

@router.get("/stats")
async def get_platform_stats(admin: Dict = Depends(require_superadmin)):
    """Overall platform statistics"""
    with get_db() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        stats = {}
        
        # Total companies
        cur.execute("SELECT COUNT(*) as count FROM companies")
        stats["total_companies"] = cur.fetchone()["count"]
        
        # Total users
        cur.execute("SELECT COUNT(*) as count FROM users WHERE is_active = true")
        stats["total_users"] = cur.fetchone()["count"]
        
        # Total documents
        try:
            cur.execute("SELECT COUNT(*) as count FROM documents")
            stats["total_documents"] = cur.fetchone()["count"]
        except:
            stats["total_documents"] = 0
        
        # Total contracts
        try:
            cur.execute("SELECT COUNT(*) as count FROM contracts WHERE status != 'deleted'")
            stats["total_contracts"] = cur.fetchone()["count"]
        except:
            stats["total_contracts"] = 0
        
        # Law database size
        cur.execute("SELECT COUNT(*) as count FROM law_documents")
        stats["total_law_documents"] = cur.fetchone()["count"]
        
        cur.execute("SELECT COUNT(*) as count FROM law_chunks")
        stats["total_law_chunks"] = cur.fetchone()["count"]
        
        # Queries today
        try:
            cur.execute("""
                SELECT COUNT(*) as count FROM usage_logs 
                WHERE created_at >= CURRENT_DATE
            """)
            stats["total_queries_today"] = cur.fetchone()["count"]
        except:
            stats["total_queries_today"] = 0
        
        # Queries this month
        try:
            cur.execute("""
                SELECT COUNT(*) as count FROM usage_logs 
                WHERE created_at >= date_trunc('month', CURRENT_DATE)
            """)
            stats["total_queries_month"] = cur.fetchone()["count"]
        except:
            stats["total_queries_month"] = 0
        
        # Active users today (last 24h)
        cur.execute("""
            SELECT COUNT(DISTINCT user_id) as count FROM usage_logs 
            WHERE created_at >= NOW() - INTERVAL '24 hours' AND user_id IS NOT NULL
        """)
        stats["active_users_today"] = cur.fetchone()["count"] or 0
        
        # Storage used (placeholder)
        stats["storage_used_mb"] = 0
        
        # Companies by plan
        cur.execute("""
            SELECT plan, COUNT(*) as count
            FROM companies
            GROUP BY plan
        """)
        plans = cur.fetchall()
        stats["companies_by_plan"] = {p["plan"]: p["count"] for p in plans}
        
        # Top companies by usage (this month)
        try:
            cur.execute("""
                SELECT c.name, COUNT(*) as queries
                FROM usage_logs ul
                JOIN companies c ON c.id = ul.company_id
                WHERE ul.created_at >= date_trunc('month', CURRENT_DATE)
                GROUP BY c.id, c.name
                ORDER BY queries DESC
                LIMIT 5
            """)
            stats["top_companies"] = [dict(r) for r in cur.fetchall()]
        except:
            stats["top_companies"] = []
        
        # Daily usage (last 30 days)
        try:
            cur.execute("""
                SELECT DATE(created_at) as date, 
                       COUNT(*) as queries,
                       COUNT(DISTINCT user_id) as users
                FROM usage_logs
                WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
                GROUP BY DATE(created_at)
                ORDER BY date ASC
            """)
            stats["daily_usage"] = [dict(r) for r in cur.fetchall()]
        except:
            stats["daily_usage"] = []

        # Lead pipeline KPIs
        try:
            cur.execute("SELECT COUNT(*) as count FROM customer_leads")
            stats["total_leads"] = cur.fetchone()["count"]

            cur.execute("SELECT COUNT(*) as count FROM customer_leads WHERE status = 'new'")
            stats["new_leads"] = cur.fetchone()["count"]

            cur.execute(
                """
                SELECT COUNT(*) as count
                FROM customer_leads
                WHERE status IN ('new', 'contacted', 'qualified')
                """
            )
            stats["open_leads"] = cur.fetchone()["count"]

            cur.execute(
                """
                SELECT COUNT(*) as count
                FROM customer_leads
                WHERE status = 'new'
                  AND created_at < NOW() - INTERVAL '15 minutes'
                """
            )
            overdue_new = cur.fetchone()["count"]

            cur.execute(
                """
                SELECT COUNT(*) as count
                FROM customer_leads
                WHERE status = 'contacted'
                  AND updated_at < NOW() - INTERVAL '2 hours'
                """
            )
            overdue_contacted = cur.fetchone()["count"]

            cur.execute(
                """
                SELECT COUNT(*) as count
                FROM customer_leads
                WHERE status = 'qualified'
                  AND updated_at < NOW() - INTERVAL '24 hours'
                """
            )
            overdue_qualified = cur.fetchone()["count"]

            stats["overdue_leads"] = overdue_new + overdue_contacted + overdue_qualified
        except Exception:
            stats["total_leads"] = 0
            stats["new_leads"] = 0
            stats["open_leads"] = 0
            stats["overdue_leads"] = 0
        
        return stats

# ============================================
# COMPANY MANAGEMENT
# ============================================

@router.get("/companies")
async def list_all_companies(
    search: Optional[str] = None,
    plan: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(200, le=500),
    offset: int = 0,
    admin: Dict = Depends(require_superadmin)
):
    """List all companies with stats"""
    with get_db() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT 
                c.id, c.name, c.slug, c.plan, c.monthly_quota, c.used_quota,
                c.is_active, c.created_at, c.metadata,
                COUNT(DISTINCT u.id) as user_count,
                COUNT(DISTINCT d.id) as document_count,
                COUNT(DISTINCT ct.id) as contract_count
            FROM companies c
            LEFT JOIN users u ON u.company_id = c.id AND u.is_active = true
            LEFT JOIN documents d ON d.company_id = c.id
            LEFT JOIN contracts ct ON ct.company_id = c.id AND ct.status != 'deleted'
            WHERE 1=1
        """
        params = []
        
        if search:
            query += " AND (c.name ILIKE %s OR c.slug ILIKE %s)"
            params.extend([f"%{search}%", f"%{search}%"])
        
        if plan:
            query += " AND c.plan = %s"
            params.append(plan)
        
        if status == "active":
            query += " AND c.is_active = true"
        elif status == "inactive":
            query += " AND c.is_active = false"
        
        query += """
            GROUP BY c.id
            ORDER BY c.created_at DESC
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        
        cur.execute(query, params)
        companies = [dict(r) for r in cur.fetchall()]
        
        # Convert UUID and datetime to string
        for c in companies:
            c["id"] = str(c["id"])
            if c.get("created_at"):
                c["created_at"] = c["created_at"].isoformat()
        
        return {"companies": companies, "total": len(companies)}

@router.get("/companies/{company_id}")
async def get_company_detail(company_id: str, admin: Dict = Depends(require_superadmin)):
    """Get detailed company info"""
    with get_db() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("SELECT * FROM companies WHERE id = %s", (company_id,))
        company = cur.fetchone()
        if not company:
            raise HTTPException(404, "Công ty không tồn tại")
        
        company = dict(company)
        company["id"] = str(company["id"])
        if company.get("created_at"):
            company["created_at"] = company["created_at"].isoformat()
        
        # Members
        cur.execute("""
            SELECT id, email, full_name, role, is_active, last_login_at, created_at
            FROM users
            WHERE company_id = %s
            ORDER BY created_at ASC
        """, (company_id,))
        members = cur.fetchall()
        company["members"] = []
        for m in members:
            member = dict(m)
            member["id"] = str(member["id"])
            if member.get("created_at"):
                member["created_at"] = member["created_at"].isoformat()
            if member.get("last_login_at"):
                member["last_login_at"] = member["last_login_at"].isoformat()
            company["members"].append(member)
        
        # Usage stats (last 30 days)
        try:
            cur.execute("""
                SELECT DATE(created_at) as date, COUNT(*) as queries
                FROM usage_logs
                WHERE company_id = %s AND created_at >= CURRENT_DATE - INTERVAL '30 days'
                GROUP BY DATE(created_at)
                ORDER BY date DESC
            """, (company_id,))
            usage = cur.fetchall()
            company["usage_history"] = [{"date": str(u["date"]), "queries": u["queries"]} for u in usage]
        except:
            company["usage_history"] = []
        
        return company


@router.get("/companies/{company_id}/storage-connectors")
async def get_company_storage_connectors(company_id: str, admin: Dict = Depends(require_superadmin)):
    """List storage connectors configured for a tenant."""
    with get_db() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            """
            SELECT id, provider, is_active, is_default, config, created_at, updated_at
            FROM company_storage_connections
            WHERE company_id = %s
            ORDER BY is_default DESC, updated_at DESC
            """,
            (company_id,),
        )
        rows = cur.fetchall()

    connectors = []
    for row in rows:
        item = dict(row)
        config = item.get("config") or {}
        item["id"] = str(item["id"])
        item["has_service_account"] = bool(config.get("service_account_json"))
        item["root_folder_id"] = config.get("root_folder_id")
        item["auto_backup"] = bool(config.get("auto_backup", True))
        item["realtime_sync"] = bool(config.get("realtime_sync", True))
        item.pop("config", None)
        if item.get("created_at"):
            item["created_at"] = item["created_at"].isoformat()
        if item.get("updated_at"):
            item["updated_at"] = item["updated_at"].isoformat()
        connectors.append(item)

    return {"connectors": connectors}


@router.put("/companies/{company_id}/storage-connectors/google-drive")
async def upsert_google_drive_connector(
    company_id: str,
    payload: GoogleDriveConnectorUpdate,
    admin: Dict = Depends(require_superadmin),
):
    """Upsert Google Drive connector for a tenant (service account + folder isolation)."""
    with get_db() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("SELECT id FROM companies WHERE id = %s", (company_id,))
        if not cur.fetchone():
            raise HTTPException(404, "Công ty không tồn tại")

        config = {
            "service_account_json": payload.service_account_json,
            "root_folder_id": payload.root_folder_id,
            "auto_backup": payload.auto_backup,
            "realtime_sync": payload.realtime_sync,
        }

        if payload.is_default:
            cur.execute(
                """
                UPDATE company_storage_connections
                SET is_default = false, updated_at = now()
                WHERE company_id = %s
                """,
                (company_id,),
            )

        cur.execute(
            """
            INSERT INTO company_storage_connections (
                company_id, provider, is_active, is_default, config, created_at, updated_at
            )
            VALUES (%s, 'google_drive', %s, %s, %s::jsonb, now(), now())
            ON CONFLICT (company_id, provider)
            DO UPDATE SET
                is_active = EXCLUDED.is_active,
                is_default = EXCLUDED.is_default,
                config = EXCLUDED.config,
                updated_at = now()
            RETURNING id, provider, is_active, is_default, created_at, updated_at
            """,
            (
                company_id,
                payload.is_active,
                payload.is_default,
                json.dumps(config, ensure_ascii=False),
            ),
        )
        connector = dict(cur.fetchone())

        try:
            cur.execute(
                """
                INSERT INTO platform_logs (user_id, action, target_type, target_id, details)
                VALUES (%s, 'upsert_storage_connector', 'company', %s, %s)
                """,
                (
                    admin["id"],
                    company_id,
                    json.dumps(
                        {
                            "provider": "google_drive",
                            "is_default": payload.is_default,
                            "is_active": payload.is_active,
                            "has_service_account": True,
                            "root_folder_id": payload.root_folder_id,
                        },
                        ensure_ascii=False,
                    ),
                ),
            )
        except Exception:
            pass

        conn.commit()

    connector["id"] = str(connector["id"])
    if connector.get("created_at"):
        connector["created_at"] = connector["created_at"].isoformat()
    if connector.get("updated_at"):
        connector["updated_at"] = connector["updated_at"].isoformat()
    connector["provider"] = "google_drive"
    connector["message"] = "Google Drive connector đã được cấu hình cho tenant"
    return connector


@router.post("/companies/{company_id}/storage-connectors/google-drive/test")
async def test_company_google_drive_connector(company_id: str, admin: Dict = Depends(require_superadmin)):
    """Test tenant Google Drive connector and validate isolated folder access."""
    result = await test_google_drive_connector(company_id)
    if not result.get("ok"):
        raise HTTPException(400, result.get("error", "Google Drive connector test failed"))
    return result

@router.put("/companies/{company_id}")
async def update_company(
    company_id: str,
    update: CompanyUpdate,
    admin: Dict = Depends(require_superadmin)
):
    """Update company settings"""
    with get_db() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        updates = []
        params = []
        
        if update.plan is not None:
            updates.append("plan = %s::plan_type")
            params.append(update.plan)
        
        if update.monthly_quota is not None:
            updates.append("monthly_quota = %s")
            params.append(update.monthly_quota)
        
        if update.used_quota is not None:
            updates.append("used_quota = %s")
            params.append(update.used_quota)
        
        if update.is_active is not None:
            updates.append("is_active = %s")
            params.append(update.is_active)
        
        if not updates:
            raise HTTPException(400, "Không có cập nhật nào")
        
        query = f"UPDATE companies SET {', '.join(updates)} WHERE id = %s RETURNING *"
        params.append(company_id)
        
        cur.execute(query, params)
        updated = cur.fetchone()
        
        if not updated:
            raise HTTPException(404, "Công ty không tồn tại")
        
        conn.commit()
        
        result = dict(updated)
        result["id"] = str(result["id"])
        if result.get("created_at"):
            result["created_at"] = result["created_at"].isoformat()
        
        # Log to platform_logs
        try:
            cur.execute("""
                INSERT INTO platform_logs (user_id, action, target_type, target_id, details)
                VALUES (%s, 'update_company', 'company', %s, %s)
            """, (admin["id"], company_id, json.dumps(update.dict(exclude_none=True))))
            conn.commit()
        except:
            pass
        
        return result

@router.get("/companies/{company_id}/users")
async def get_company_users(company_id: str, admin: Dict = Depends(require_superadmin)):
    """Get all users of a company"""
    with get_db() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT id, email, full_name, role, is_active, last_login_at, created_at
            FROM users
            WHERE company_id = %s
            ORDER BY created_at ASC
        """, (company_id,))
        users = cur.fetchall()
        
        result = []
        for u in users:
            user = dict(u)
            user["id"] = str(user["id"])
            if user.get("created_at"):
                user["created_at"] = user["created_at"].isoformat()
            if user.get("last_login_at"):
                user["last_login_at"] = user["last_login_at"].isoformat()
            result.append(user)
        
        return {"users": result}

# ============================================
# USER MANAGEMENT
# ============================================

@router.get("/users")
async def list_all_users(
    search: Optional[str] = None,
    role: Optional[str] = None,
    company_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(200, le=1000),
    offset: int = 0,
    admin: Dict = Depends(require_superadmin)
):
    """List all users across all companies"""
    with get_db() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT 
                u.id, u.email, u.full_name, u.role, u.company_id, u.is_active,
                u.last_login_at, u.created_at,
                c.name as company_name, c.plan as company_plan
            FROM users u
            LEFT JOIN companies c ON c.id = u.company_id
            WHERE 1=1
        """
        params = []
        
        if search:
            query += " AND (u.email ILIKE %s OR u.full_name ILIKE %s)"
            params.extend([f"%{search}%", f"%{search}%"])
        
        if role:
            query += " AND u.role = %s"
            params.append(role)
        
        if company_id:
            query += " AND u.company_id = %s"
            params.append(company_id)
        
        if status == "active":
            query += " AND u.is_active = true"
        elif status == "inactive":
            query += " AND u.is_active = false"
        
        query += " ORDER BY u.created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cur.execute(query, params)
        users = cur.fetchall()
        
        result = []
        for u in users:
            user = dict(u)
            user["id"] = str(user["id"])
            if user.get("company_id"):
                user["company_id"] = str(user["company_id"])
            if user.get("created_at"):
                user["created_at"] = user["created_at"].isoformat()
            if user.get("last_login_at"):
                user["last_login_at"] = user["last_login_at"].isoformat()
            result.append(user)
        
        return {"users": result}

@router.put("/users/{user_id}/role")
async def change_user_role(
    user_id: str,
    update: UserRoleUpdate,
    admin: Dict = Depends(require_superadmin)
):
    """Change user role"""
    with get_db() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            UPDATE users SET role = %s::user_role WHERE id = %s RETURNING *
        """, (update.role, user_id))
        
        updated = cur.fetchone()
        if not updated:
            raise HTTPException(404, "Người dùng không tồn tại")
        
        conn.commit()
        
        result = dict(updated)
        result["id"] = str(result["id"])
        
        return result

@router.put("/users/{user_id}/status")
async def change_user_status(
    user_id: str,
    update: UserStatusUpdate,
    admin: Dict = Depends(require_superadmin)
):
    """Activate/deactivate user"""
    with get_db() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            UPDATE users SET is_active = %s WHERE id = %s RETURNING *
        """, (update.is_active, user_id))
        
        updated = cur.fetchone()
        if not updated:
            raise HTTPException(404, "Người dùng không tồn tại")
        
        conn.commit()
        
        result = dict(updated)
        result["id"] = str(result["id"])
        
        return result


# ============================================
# LEADS MANAGEMENT
# ============================================

@router.get("/leads")
async def list_leads(
    search: Optional[str] = None,
    status: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = Query(200, le=1000),
    offset: int = 0,
    admin: Dict = Depends(require_superadmin),
):
    """List captured customer leads for superadmin operations."""
    with get_db() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT
                l.id, l.source, l.full_name, l.company_name, l.email, l.phone,
                l.ai_level, l.needs, l.detail, l.status, l.note,
                l.assigned_to,
                l.converted_company_id, l.converted_user_id, l.converted_at,
                l.created_at, l.updated_at,
                c.name as converted_company_name,
                u.full_name as converted_user_name,
                u.email as converted_user_email,
                assignee.full_name as assignee_name,
                assignee.email as assignee_email
            FROM customer_leads l
            LEFT JOIN companies c ON c.id = l.converted_company_id
            LEFT JOIN users u ON u.id = l.converted_user_id
            LEFT JOIN users assignee ON assignee.id = l.assigned_to
            WHERE 1=1
        """
        params: List[Any] = []

        if search:
            query += " AND (l.email ILIKE %s OR l.full_name ILIKE %s OR l.company_name ILIKE %s)"
            params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

        if status:
            query += " AND l.status = %s"
            params.append(status)

        if source:
            query += " AND l.source = %s"
            params.append(source)

        query += " ORDER BY l.created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cur.execute(query, params)
        rows = cur.fetchall()

        leads = []
        for row in rows:
            lead = dict(row)
            lead["id"] = str(lead["id"])
            if lead.get("converted_company_id"):
                lead["converted_company_id"] = str(lead["converted_company_id"])
            if lead.get("converted_user_id"):
                lead["converted_user_id"] = str(lead["converted_user_id"])
            if lead.get("assigned_to"):
                lead["assigned_to"] = str(lead["assigned_to"])
            if lead.get("created_at"):
                lead["created_at"] = lead["created_at"].isoformat()
            if lead.get("updated_at"):
                lead["updated_at"] = lead["updated_at"].isoformat()
            if lead.get("converted_at"):
                lead["converted_at"] = lead["converted_at"].isoformat()

            # SLA model inspired by CRM lead lifecycle operations.
            now = datetime.utcnow()
            anchor = row.get("updated_at") if row.get("status") in {"contacted", "qualified"} else row.get("created_at")
            sla_target_minutes = None
            if row.get("status") == "new":
                sla_target_minutes = 15
            elif row.get("status") == "contacted":
                sla_target_minutes = 120
            elif row.get("status") == "qualified":
                sla_target_minutes = 1440

            if anchor:
                age_minutes = int((now - anchor.replace(tzinfo=None)).total_seconds() // 60)
            else:
                age_minutes = 0

            lead["sla_age_minutes"] = age_minutes
            lead["sla_target_minutes"] = sla_target_minutes
            if sla_target_minutes is None:
                lead["sla_state"] = "n/a"
            elif age_minutes > sla_target_minutes:
                lead["sla_state"] = "overdue"
            else:
                lead["sla_state"] = "on_track"
            leads.append(lead)

        return {"leads": leads}


@router.get("/leads/assignees")
async def list_lead_assignees(admin: Dict = Depends(require_superadmin)):
    """List active users eligible for lead assignment."""
    with get_db() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            """
            SELECT id, full_name, email, role
            FROM users
            WHERE is_active = true
              AND role IN ('superadmin', 'admin', 'owner')
            ORDER BY
              CASE role WHEN 'superadmin' THEN 0 WHEN 'admin' THEN 1 ELSE 2 END,
              created_at DESC
            LIMIT 200
            """
        )
        assignees = []
        for row in cur.fetchall():
            item = dict(row)
            item["id"] = str(item["id"])
            assignees.append(item)
        return {"assignees": assignees}


@router.put("/leads/{lead_id}/assign")
async def assign_lead(
    lead_id: str,
    body: LeadAssignRequest,
    admin: Dict = Depends(require_superadmin),
):
    """Assign lead to an operator (or clear assignment)."""
    with get_db() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)

        assignee_id = body.assigned_to_user_id
        if assignee_id:
            cur.execute(
                "SELECT id FROM users WHERE id::text = %s AND is_active = true",
                (assignee_id,),
            )
            if not cur.fetchone():
                raise HTTPException(404, "Người phụ trách không tồn tại hoặc không active")

        cur.execute(
            """
            UPDATE customer_leads
            SET assigned_to = %s,
                updated_at = now(),
                note = COALESCE(note, %s)
            WHERE id::text = %s
            RETURNING id, assigned_to, updated_at
            """,
            (
                assignee_id,
                f"Assigned by {admin.get('email', 'superadmin')}",
                lead_id,
            ),
        )
        updated = cur.fetchone()
        if not updated:
            raise HTTPException(404, "Lead không tồn tại")

        conn.commit()
        return {
            "id": str(updated["id"]),
            "assigned_to": str(updated["assigned_to"]) if updated.get("assigned_to") else None,
            "updated_at": updated["updated_at"].isoformat() if updated.get("updated_at") else None,
        }


@router.put("/leads/{lead_id}/status")
async def update_lead_status(
    lead_id: str,
    update: LeadStatusUpdate,
    admin: Dict = Depends(require_superadmin),
):
    """Update lead status (new/contacted/qualified/converted/lost)."""
    allowed_statuses = {"new", "contacted", "qualified", "converted", "lost"}
    if update.status not in allowed_statuses:
        raise HTTPException(400, f"Invalid status. Allowed: {', '.join(sorted(allowed_statuses))}")

    with get_db() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            """
            UPDATE customer_leads
            SET status = %s, note = COALESCE(%s, note), updated_at = now(), assigned_to = %s
            WHERE id::text = %s
            RETURNING *
            """,
            (update.status, update.note, admin["id"], lead_id),
        )
        lead = cur.fetchone()
        if not lead:
            raise HTTPException(404, "Lead không tồn tại")
        conn.commit()

        result = dict(lead)
        result["id"] = str(result["id"])
        return result


@router.post("/leads/{lead_id}/convert")
async def convert_lead(
    lead_id: str,
    body: LeadConvertRequest,
    admin: Dict = Depends(require_superadmin),
):
    """One-click convert lead to upgraded customer account."""
    allowed_plans = {"trial", "starter", "pro", "enterprise"}
    if body.plan not in allowed_plans:
        raise HTTPException(400, f"Invalid plan. Allowed: {', '.join(sorted(allowed_plans))}")

    allowed_roles = {"owner", "admin", "member", "viewer"}
    if body.user_role not in allowed_roles:
        raise HTTPException(400, f"Invalid role. Allowed: {', '.join(sorted(allowed_roles))}")

    with get_db() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("SELECT * FROM customer_leads WHERE id::text = %s", (lead_id,))
        lead = cur.fetchone()
        if not lead:
            raise HTTPException(404, "Lead không tồn tại")

        cur.execute(
            """
            SELECT id, company_id, role
            FROM users
            WHERE lower(email) = lower(%s)
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (lead["email"],),
        )
        user = cur.fetchone()
        if not user:
            raise HTTPException(
                404,
                "Chưa tìm thấy tài khoản theo email lead. Vui lòng yêu cầu khách đăng ký trước.",
            )

        cur.execute(
            """
            UPDATE companies
            SET plan = %s::plan_type,
                monthly_quota = %s,
                is_active = true,
                updated_at = now()
            WHERE id = %s
            RETURNING id, name, plan, monthly_quota, is_active
            """,
            (body.plan, body.monthly_quota, user["company_id"]),
        )
        company = cur.fetchone()
        if not company:
            raise HTTPException(404, "Không tìm thấy công ty của user")

        cur.execute(
            """
            UPDATE users
            SET role = %s::user_role,
                is_active = true
            WHERE id = %s
            RETURNING id, email, role, company_id, is_active
            """,
            (body.user_role, user["id"]),
        )
        updated_user = cur.fetchone()

        cur.execute(
            """
            UPDATE customer_leads
            SET status = 'converted',
                assigned_to = %s,
                note = COALESCE(%s, note),
                converted_company_id = %s,
                converted_user_id = %s,
                converted_at = now(),
                updated_at = now()
            WHERE id::text = %s
            RETURNING id, status, converted_at
            """,
            (
                admin["id"],
                body.note,
                user["company_id"],
                user["id"],
                lead_id,
            ),
        )
        converted = cur.fetchone()

        try:
            cur.execute(
                """
                INSERT INTO platform_logs (user_id, action, target_type, target_id, details)
                VALUES (%s, 'convert_lead', 'lead', %s, %s)
                """,
                (
                    admin["id"],
                    lead_id,
                    json.dumps(
                        {
                            "plan": body.plan,
                            "monthly_quota": body.monthly_quota,
                            "user_role": body.user_role,
                            "email": lead["email"],
                            "company_id": str(user["company_id"]),
                            "user_id": str(user["id"]),
                        }
                    ),
                ),
            )
        except Exception:
            pass

        conn.commit()

        return {
            "ok": True,
            "lead": {
                "id": str(converted["id"]),
                "status": converted["status"],
                "converted_at": converted["converted_at"].isoformat() if converted.get("converted_at") else None,
            },
            "company": {
                "id": str(company["id"]),
                "name": company["name"],
                "plan": company["plan"],
                "monthly_quota": company["monthly_quota"],
                "is_active": company["is_active"],
            },
            "user": {
                "id": str(updated_user["id"]),
                "email": updated_user["email"],
                "role": updated_user["role"],
                "is_active": updated_user["is_active"],
            },
        }

# ============================================
# SYSTEM SETTINGS
# ============================================

@router.get("/settings")
async def get_platform_settings(admin: Dict = Depends(require_superadmin)):
    """Get all platform settings"""
    with get_db() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("SELECT key, value FROM platform_settings")
        rows = cur.fetchall()
        
        settings = {}
        for row in rows:
            settings[row["key"]] = row["value"]
        
        # Merge all settings into one object
        result = {
            "default_llm_provider": settings.get("llm", {}).get("default_provider", "anthropic"),
            "default_llm_model": settings.get("llm", {}).get("default_model", "claude-sonnet-4-20250514"),
            "max_file_size_mb": settings.get("limits", {}).get("max_file_size_mb", 50),
            "max_queries_per_day_free": settings.get("limits", {}).get("max_queries_per_day_free", 10),
            "max_contracts_free": settings.get("limits", {}).get("max_contracts_free", 1),
            "registration_enabled": settings.get("general", {}).get("registration_enabled", True),
            "require_email_verification": settings.get("general", {}).get("require_email_verification", False),
            "allowed_file_types": settings.get("limits", {}).get("allowed_file_types", [".pdf", ".doc", ".docx", ".txt"]),
            "maintenance_mode": settings.get("general", {}).get("maintenance_mode", False),
            "maintenance_message": settings.get("general", {}).get("maintenance_message", ""),
            "feature_flags": settings.get("features", {})
        }
        
        return result

@router.put("/settings")
async def update_platform_settings(
    settings: PlatformSettings,
    admin: Dict = Depends(require_superadmin)
):
    """Update platform settings"""
    with get_db() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Update general settings
        if settings.registration_enabled is not None or settings.require_email_verification is not None or settings.maintenance_mode is not None:
            cur.execute("SELECT value FROM platform_settings WHERE key = 'general'")
            row = cur.fetchone()
            general = row["value"] if row else {}
            
            if settings.registration_enabled is not None:
                general["registration_enabled"] = settings.registration_enabled
            if settings.require_email_verification is not None:
                general["require_email_verification"] = settings.require_email_verification
            if settings.maintenance_mode is not None:
                general["maintenance_mode"] = settings.maintenance_mode
            if settings.maintenance_message is not None:
                general["maintenance_message"] = settings.maintenance_message
            
            cur.execute("""
                INSERT INTO platform_settings (key, value, updated_by)
                VALUES ('general', %s, %s)
                ON CONFLICT (key) DO UPDATE SET value = %s, updated_by = %s, updated_at = NOW()
            """, (json.dumps(general), admin["id"], json.dumps(general), admin["id"]))
        
        # Update limits
        if any([settings.max_file_size_mb, settings.max_queries_per_day_free, settings.max_contracts_free, settings.allowed_file_types]):
            cur.execute("SELECT value FROM platform_settings WHERE key = 'limits'")
            row = cur.fetchone()
            limits = row["value"] if row else {}
            
            if settings.max_file_size_mb is not None:
                limits["max_file_size_mb"] = settings.max_file_size_mb
            if settings.max_queries_per_day_free is not None:
                limits["max_queries_per_day_free"] = settings.max_queries_per_day_free
            if settings.max_contracts_free is not None:
                limits["max_contracts_free"] = settings.max_contracts_free
            if settings.allowed_file_types is not None:
                limits["allowed_file_types"] = settings.allowed_file_types
            
            cur.execute("""
                INSERT INTO platform_settings (key, value, updated_by)
                VALUES ('limits', %s, %s)
                ON CONFLICT (key) DO UPDATE SET value = %s, updated_by = %s, updated_at = NOW()
            """, (json.dumps(limits), admin["id"], json.dumps(limits), admin["id"]))
        
        # Update LLM settings
        if settings.default_llm_provider or settings.default_llm_model:
            cur.execute("SELECT value FROM platform_settings WHERE key = 'llm'")
            row = cur.fetchone()
            llm = row["value"] if row else {}
            
            if settings.default_llm_provider:
                llm["default_provider"] = settings.default_llm_provider
            if settings.default_llm_model:
                llm["default_model"] = settings.default_llm_model
            
            cur.execute("""
                INSERT INTO platform_settings (key, value, updated_by)
                VALUES ('llm', %s, %s)
                ON CONFLICT (key) DO UPDATE SET value = %s, updated_by = %s, updated_at = NOW()
            """, (json.dumps(llm), admin["id"], json.dumps(llm), admin["id"]))
        
        # Update feature flags
        if settings.feature_flags:
            cur.execute("""
                INSERT INTO platform_settings (key, value, updated_by)
                VALUES ('features', %s, %s)
                ON CONFLICT (key) DO UPDATE SET value = %s, updated_by = %s, updated_at = NOW()
            """, (json.dumps(settings.feature_flags), admin["id"], json.dumps(settings.feature_flags), admin["id"]))
        
        conn.commit()
        
        return {"message": "Cài đặt đã được cập nhật", "updated_by": admin["email"]}

# ============================================
# AUDIT LOGS
# ============================================

@router.get("/logs")
async def get_platform_logs(
    action: Optional[str] = None,
    limit: int = Query(100, le=1000),
    admin: Dict = Depends(require_superadmin)
):
    """Get platform audit logs"""
    with get_db() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT pl.*, u.email as user_email, u.full_name as user_name
            FROM platform_logs pl
            LEFT JOIN users u ON u.id = pl.user_id
            WHERE 1=1
        """
        params = []
        
        if action:
            query += " AND pl.action = %s"
            params.append(action)
        
        query += " ORDER BY pl.created_at DESC LIMIT %s"
        params.append(limit)
        
        cur.execute(query, params)
        logs = cur.fetchall()
        
        result = []
        for log in logs:
            l = dict(log)
            if l.get("id"):
                l["id"] = str(l["id"])
            if l.get("user_id"):
                l["user_id"] = str(l["user_id"])
            if l.get("created_at"):
                l["created_at"] = l["created_at"].isoformat()
            result.append(l)
        
        return {"logs": result}

# ============================================
# LLM USAGE & COST
# ============================================

@router.get("/llm-usage")
async def get_llm_usage(admin: Dict = Depends(require_superadmin)):
    """LLM usage stats and cost estimation"""
    with get_db() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Total tokens today
        try:
            cur.execute("""
                SELECT SUM(input_tokens) as input, SUM(output_tokens) as output
                FROM llm_usage
                WHERE created_at >= CURRENT_DATE
            """)
            today = cur.fetchone()
        except:
            today = {"input": 0, "output": 0}
        
        # Total tokens this month
        try:
            cur.execute("""
                SELECT SUM(input_tokens) as input, SUM(output_tokens) as output
                FROM llm_usage
                WHERE created_at >= date_trunc('month', CURRENT_DATE)
            """)
            month = cur.fetchone()
        except:
            month = {"input": 0, "output": 0}
        
        # By provider
        try:
            cur.execute("""
                SELECT provider, SUM(input_tokens + output_tokens) as tokens
                FROM llm_usage
                WHERE created_at >= date_trunc('month', CURRENT_DATE)
                GROUP BY provider
            """)
            by_provider = {r["provider"]: r["tokens"] for r in cur.fetchall()}
        except:
            by_provider = {}
        
        # By company (top 10)
        try:
            cur.execute("""
                SELECT c.name, SUM(lu.input_tokens + lu.output_tokens) as tokens
                FROM llm_usage lu
                JOIN companies c ON c.id = lu.company_id
                WHERE lu.created_at >= date_trunc('month', CURRENT_DATE)
                GROUP BY c.id, c.name
                ORDER BY tokens DESC
                LIMIT 10
            """)
            by_company = [dict(r) for r in cur.fetchall()]
        except:
            by_company = []
        
        total_tokens_month = (month.get("input") or 0) + (month.get("output") or 0)
        
        # Simple cost estimation (Claude Sonnet 4: $3 per 1M input, $15 per 1M output)
        estimated_cost = ((month.get("input") or 0) / 1_000_000 * 3) + ((month.get("output") or 0) / 1_000_000 * 15)
        
        return {
            "total_tokens_today": (today.get("input") or 0) + (today.get("output") or 0),
            "total_tokens_month": total_tokens_month,
            "estimated_cost_month_usd": round(estimated_cost, 2),
            "by_provider": by_provider,
            "by_company": by_company
        }

# ============================================
# MAINTENANCE
# ============================================

@router.get("/maintenance/db-stats")
async def get_db_stats(admin: Dict = Depends(require_superadmin)):
    """Database statistics"""
    with get_db() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        stats = {}
        
        tables = ["companies", "users", "documents", "contracts", "law_documents", "law_chunks", "usage_logs"]
        
        for table in tables:
            try:
                cur.execute(f"SELECT COUNT(*) as count FROM {table}")
                stats[table] = cur.fetchone()["count"]
            except:
                stats[table] = 0
        
        # Database size (PostgreSQL)
        try:
            cur.execute("SELECT pg_database_size(current_database()) as size")
            size_bytes = cur.fetchone()["size"]
            stats["database_size_mb"] = round(size_bytes / 1024 / 1024, 2)
        except:
            stats["database_size_mb"] = 0
        
        return stats

@router.post("/maintenance/cleanup")
async def cleanup_deleted(admin: Dict = Depends(require_superadmin)):
    """Clean up soft-deleted documents older than 30 days"""
    with get_db() as conn:
        cur = conn.cursor()
        
        try:
            cur.execute("""
                DELETE FROM contracts
                WHERE status = 'deleted' AND updated_at < NOW() - INTERVAL '30 days'
            """)
            deleted = cur.rowcount
            conn.commit()
            
            return {"cleaned": deleted, "message": f"Đã xóa {deleted} hợp đồng"}
        except Exception as e:
            return {"error": str(e)}
