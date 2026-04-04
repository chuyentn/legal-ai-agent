# Huong Dan Superadmin: Nang Cap Khach Hang That

Tai lieu nay dung cho superadmin van hanh he thong khi can nang cap goi va quyen cho khach hang production.

## 1) Muc tieu

- Nang cap cong ty len goi `starter`, `pro`, hoac `enterprise`.
- Dieu chinh `monthly_quota` theo hop dong that.
- Kich hoat/khoa user khi can.
- Dam bao user dau moi cua khach la `owner` de quan tri noi bo cong ty.

## 2) Nguyen tac an toan

- Khong doi user khach hang thanh `superadmin`.
- `superadmin` chi dung cho tai khoan van hanh nen tang.
- Tai khoan khach hang nen la `owner` (hoac `admin`) trong pham vi cong ty cua ho.
- Moi thay doi phai co ghi chu ticket/CRM noi bo.

## 3) Dieu kien truoc khi thao tac

- Dang nhap tai khoan superadmin hop le.
- Truy cap trang Platform Admin: `/platform-admin`.
- Xac nhan dung dung he thong production.

## 4) Quy trinh chuan qua Platform Admin API

Tat ca API duoi day can header:

- `Authorization: Bearer <SUPERADMIN_ACCESS_TOKEN>`
- `Content-Type: application/json`

### Buoc 1: Tim user khach hang theo email

```bash
curl -X GET "https://legal-ai-agent.coach.io.vn/v1/platform/users?search=dataphuan@gmail.com&limit=20" \
  -H "Authorization: Bearer <SUPERADMIN_ACCESS_TOKEN>"
```

Can lay:

- `user_id`
- `company_id`
- `role` hien tai
- `is_active`

### Buoc 2: Xem thong tin cong ty truoc khi nang cap

```bash
curl -X GET "https://legal-ai-agent.coach.io.vn/v1/platform/companies/<company_id>" \
  -H "Authorization: Bearer <SUPERADMIN_ACCESS_TOKEN>"
```

### Buoc 3: Nang cap goi va quota cong ty

Vi du nang len enterprise cho demo that:

```bash
curl -X PUT "https://legal-ai-agent.coach.io.vn/v1/platform/companies/<company_id>" \
  -H "Authorization: Bearer <SUPERADMIN_ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "plan": "enterprise",
    "monthly_quota": 100000,
    "used_quota": 0,
    "is_active": true
  }'
```

Gia tri `plan` hop le:

- `trial`
- `starter`
- `pro`
- `enterprise`

### Buoc 4: Dat role dung cho user dau moi

Khuyen nghi dat `owner` cho user chinh cua khach:

```bash
curl -X PUT "https://legal-ai-agent.coach.io.vn/v1/platform/users/<user_id>/role" \
  -H "Authorization: Bearer <SUPERADMIN_ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"role":"owner"}'
```

### Buoc 5: Dam bao user dang active

```bash
curl -X PUT "https://legal-ai-agent.coach.io.vn/v1/platform/users/<user_id>/status" \
  -H "Authorization: Bearer <SUPERADMIN_ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"is_active":true}'
```

### Buoc 6: Xac minh sau nang cap

- Dang nhap bang tai khoan khach.
- Kiem tra quota/plan tren giao dien app.
- Chay 1-2 thao tac that (chat/review) de chac chan khong con block quota.

## 5) Checklist van hanh nhanh

- Da xac nhan dung email khach hang.
- Da xac nhan dung company_id.
- Da set plan theo hop dong.
- Da set monthly_quota theo cam ket.
- Da dat user chinh = owner.
- Da bat is_active cho user va company.
- Da ghi log ticket sau thao tac.

## 6) SQL fallback (khi API admin tam thoi loi)

Chi dung khi bat buoc va phai thuc hien tren production DB dung tenant.

```sql
BEGIN;

WITH target AS (
  SELECT id, company_id
  FROM users
  WHERE lower(email) = lower('dataphuan@gmail.com')
  ORDER BY created_at DESC
  LIMIT 1
)
UPDATE users u
SET role = 'owner'::user_role,
    is_active = true
FROM target t
WHERE u.id = t.id;

WITH target AS (
  SELECT company_id
  FROM users
  WHERE lower(email) = lower('dataphuan@gmail.com')
  ORDER BY created_at DESC
  LIMIT 1
)
UPDATE companies c
SET plan = 'enterprise'::plan_type,
    monthly_quota = 100000,
    used_quota = 0,
    is_active = true
FROM target t
WHERE c.id = t.company_id;

COMMIT;
```

## 7) Rollback nhanh

Neu can rollback sau demo:

- Company ve `pro` hoac `starter`.
- Giam `monthly_quota` theo hop dong.
- Khong xoa user, chi doi role ve `admin` neu can.

Vi du rollback qua API:

```bash
curl -X PUT "https://legal-ai-agent.coach.io.vn/v1/platform/companies/<company_id>" \
  -H "Authorization: Bearer <SUPERADMIN_ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"plan":"pro","monthly_quota":5000}'
```

## 8) Luu y quan trong

- Neu thay `403` o API `/v1/platform/*`: token dang dung khong phai superadmin.
- Khong cap quyen `superadmin` cho tai khoan khach hang.
- Neu health van `degraded` do DB, xu ly env DB truoc khi demo lon.
