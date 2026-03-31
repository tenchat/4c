# CCCC Employment Analysis Platform - Technical Architecture

## 1. API Endpoint Inventory

### 1.1 Frontend API Files
- `frontend/src/api/student.ts` - Student management
- `frontend/src/api/job.ts` - Job management
- `frontend/src/api/statistics.ts` - Statistics queries
- `frontend/src/api/ai.ts` - AI services
- `frontend/src/api/auth.ts` - Authentication
- `frontend/src/api/dashboard.ts` - Dashboard data

### 1.2 Backend API Files
- `backend/app/api/v1/student.py` - Student endpoints
- `backend/app/api/v1/statistics.py` - Statistics endpoints
- `backend/app/api/v1/ai.py` - AI endpoints
- `backend/app/api/v1/auth.py` - Authentication endpoints

---

## 2. API Gap Analysis

### 2.1 FULLY IMPLEMENTED (Backend exists, Frontend matches)

| Endpoint | Frontend | Backend | Status |
|----------|----------|---------|--------|
| `GET /api/v1/students` | student.ts | student.py | OK |
| `GET /api/v1/students/{id}` | student.ts | student.py | OK |
| `PUT /api/v1/students/{id}` | student.ts | student.py | OK |
| `POST /api/v1/students` | student.ts | student.py | OK |
| `DELETE /api/v1/students/{id}` | student.ts | student.py | OK |
| `GET /api/v1/statistics/summary` | statistics.ts | statistics.py | OK |
| `GET /api/v1/statistics/by-college` | statistics.ts | statistics.py | OK |
| `GET /api/v1/statistics/by-major` | statistics.ts | statistics.py | OK |
| `GET /api/v1/statistics/by-province` | statistics.ts | statistics.py | OK |
| `POST /api/v1/auth/login` | auth.ts | auth.py | OK |
| `POST /api/v1/auth/logout` | auth.ts | auth.py | OK |
| `GET /api/v1/auth/me` | auth.ts | auth.py | OK |
| `POST /api/v1/auth/refresh` | auth.ts | auth.py | OK |
| `POST /api/v1/ai/employment-profile` | ai.ts | ai.py | OK |
| `POST /api/v1/ai/job-recommendation` | ai.ts | ai.py | OK |
| `POST /api/v1/ai/skill-path` | ai.ts | ai.py | OK |
| `POST /api/v1/ai/warning` | ai.ts | ai.py | OK |

### 2.2 MISSING ON BACKEND (Frontend calls but no backend implementation)

| Endpoint | Frontend | Backend | Priority |
|----------|----------|---------|----------|
| `POST /api/v1/students/import` | student.ts | MISSING | HIGH |
| `GET /api/v1/students/export` | student.ts | MISSING | HIGH |
| `GET /api/v1/jobs` | job.ts | MISSING | HIGH |
| `GET /api/v1/jobs/{jdNo}` | job.ts | MISSING | HIGH |
| `POST /api/v1/jobs` | job.ts | MISSING | HIGH |
| `PUT /api/v1/jobs/{jdNo}` | job.ts | MISSING | HIGH |
| `DELETE /api/v1/jobs/{jdNo}` | job.ts | MISSING | HIGH |
| `POST /api/v1/jobs/apply` | job.ts | MISSING | HIGH |
| `GET /api/v1/jobs/my-applications` | job.ts | MISSING | HIGH |
| `GET /api/v1/statistics/trend` | statistics.ts | MISSING | MEDIUM |
| `GET /api/v1/statistics/industry-salary` | statistics.ts | MISSING | MEDIUM |
| `GET /api/v1/dashboard/data` | dashboard.ts | MISSING | HIGH |
| `GET /api/v1/dashboard/stats` | dashboard.ts | MISSING | MEDIUM |
| `GET /api/v1/dashboard/visit-trend` | dashboard.ts | MISSING | MEDIUM |
| `GET /api/v1/dashboard/region` | dashboard.ts | MISSING | MEDIUM |
| `GET /api/v1/dashboard/traffic-sources` | dashboard.ts | MISSING | MEDIUM |
| `GET /api/v1/dashboard/realtime` | dashboard.ts | MISSING | MEDIUM |

### 2.3 PARTIAL MATCH / MISMATCH

| Issue | Frontend | Backend | Fix Needed |
|-------|----------|---------|------------|
| `POST /api/v1/ai/analyze-resume` | ai.ts (resume_url param) | ai.py (resume_text param) | Different request body |
| `POST /api/v1/ai/compare-options` | ai.ts (option_a, option_b, context) | MISSING | New endpoint needed |
| `WarningRequest` | `{student_id, college, threshold}` | `{major, gpa, employment_status, ...}` | Schema mismatch |

### 2.4 DATA STRUCTURE MISMATCHES

**Student Profile:**
- Frontend: `profile_id: number`, `employment_status?: number` (numeric)
- Backend StudentProfile: `id: Integer`, no `employment_status` field
- Backend uses `Student.employment_status` from different model

**JobDescription:**
- Frontend: `status: number` (0/1)
- Backend: `status: string` ("active"/"closed")

---

## 3. Recommended API Designs

### 3.1 Jobs API (`/api/v1/jobs/*`)

**File:** `backend/app/api/v1/job.py`

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.models.job import JobDescription, JobApplication
from app.schemas.job import (
    JobCreate, JobUpdate, JobResponse, JobListResponse,
    JobApplyRequest, JobApplyResponse, ApplicationListResponse
)

router = APIRouter(prefix="/jobs", tags=["岗位管理"])


@router.get("/", response_model=JobListResponse)
def list_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    city: Optional[str] = None,
    industry: Optional[str] = None,
    min_salary: Optional[int] = None,
    max_salary: Optional[int] = None,
    min_edu_level: Optional[int] = None,
    status: Optional[str] = "active",
    keyword: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取岗位列表"""
    query = db.query(JobDescription)

    if city:
        query = query.filter(JobDescription.city == city)
    if industry:
        query = query.filter(JobDescription.industry == industry)
    if min_salary:
        query = query.filter(JobDescription.min_salary >= min_salary)
    if max_salary:
        query = query.filter(JobDescription.max_salary <= max_salary)
    if min_edu_level:
        query = query.filter(JobDescription.min_edu_level >= min_edu_level)
    if status:
        query = query.filter(JobDescription.status == status)
    if keyword:
        query = query.filter(
            (JobDescription.jd_title.contains(keyword)) |
            (JobDescription.key_words.contains(keyword))
        )

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return JobListResponse(
        total=total,
        items=[JobResponse.model_validate(item) for item in items]
    )


@router.get("/{jd_no}", response_model=JobResponse)
def get_job(jd_no: str, db: Session = Depends(get_db)):
    """获取岗位详情"""
    job = db.query(JobDescription).filter(JobDescription.jd_no == jd_no).first()
    if not job:
        raise HTTPException(status_code=404, detail="岗位不存在")
    return job


@router.post("/", response_model=JobResponse, status_code=201)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    """创建岗位"""
    # Generate jd_no
    jd_no = f"JD{datetime.now().strftime('%Y%m%d%H%M%S')}"
    db_job = JobDescription(jd_no=jd_no, **job.model_dump())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


@router.put("/{jd_no}", response_model=JobResponse)
def update_job(jd_no: str, job: JobUpdate, db: Session = Depends(get_db)):
    """更新岗位"""
    db_job = db.query(JobDescription).filter(JobDescription.jd_no == jd_no).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="岗位不存在")

    for key, value in job.model_dump(exclude_unset=True).items():
        setattr(db_job, key, value)

    db.commit()
    db.refresh(db_job)
    return db_job


@router.delete("/{jd_no}", status_code=204)
def delete_job(jd_no: str, db: Session = Depends(get_db)):
    """删除岗位"""
    db_job = db.query(JobDescription).filter(JobDescription.jd_no == jd_no).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="岗位不存在")
    db.delete(db_job)
    db.commit()
    return None


@router.post("/apply", response_model=JobApplyResponse)
def apply_job(request: JobApplyRequest, db: Session = Depends(get_db)):
    """申请岗位"""
    # Check if already applied
    existing = db.query(JobApplication).filter(
        JobApplication.jd_no == request.jd_no,
        JobApplication.account_id == current_user.account_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="已申请过该岗位")

    application = JobApplication(
        jd_no=request.jd_no,
        account_id=current_user.account_id,
        cover_letter=request.cover_letter
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    return JobApplyResponse(
        id=application.id,
        jd_no=application.jd_no,
        status=application.status,
        applied_at=application.applied_at.isoformat()
    )


@router.get("/my-applications", response_model=ApplicationListResponse)
def get_my_applications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取我的申请记录"""
    query = db.query(JobApplication).filter(
        JobApplication.account_id == current_user.account_id
    )
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return ApplicationListResponse(
        total=total,
        items=[ApplicationResponse.model_validate(item) for item in items]
    )
```

### 3.2 Dashboard API (`/api/v1/dashboard/*`)

**File:** `backend/app/api/v1/dashboard.py`

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.core.database import get_db
from app.models.student import Student
from app.models.job import JobDescription, JobApplication

router = APIRouter(prefix="/dashboard", tags=["仪表盘"])


class DashboardStats(BaseModel):
    total_visits: int = 0
    active_users: int = 0
    avg_duration: str = "0m"
    conversion_rate: float = 0.0


class VisitData(BaseModel):
    date: str
    value: int


class RegionData(BaseModel):
    region: str
    value: int


class TrafficSource(BaseModel):
    name: str
    value: int


class DashboardData(BaseModel):
    stats: DashboardStats
    visit_trend: List[VisitData]
    region_distribution: List[RegionData]
    traffic_sources: List[TrafficSource]
    real_time_users: List[VisitData]


@router.get("/data", response_model=DashboardData)
def get_dashboard_data(db: Session = Depends(get_db)):
    """获取仪表盘完整数据"""
    # Stats
    total_students = db.query(func.count(Student.id)).scalar()
    total_jobs = db.query(func.count(JobDescription.id)).filter(
        JobDescription.status == "active"
    ).scalar()

    stats = DashboardStats(
        total_visits=total_students * 10,  # Mock data
        active_users=total_students,
        avg_duration="5m",
        conversion_rate=round(total_jobs / total_students * 100, 2) if total_students > 0 else 0
    )

    # Mock trend data (replace with real analytics table)
    visit_trend = [
        VisitData(date="2026-03-21", value=120),
        VisitData(date="2026-03-22", value=150),
        VisitData(date="2026-03-23", value=180),
        VisitData(date="2026-03-24", value=200),
        VisitData(date="2026-03-25", value=190),
        VisitData(date="2026-03-26", value=220),
        VisitData(date="2026-03-27", value=250),
    ]

    # Region distribution (from student data)
    regions = db.query(
        Student.province,
        func.count(Student.id)
    ).group_by(Student.province).all()

    region_distribution = [
        RegionData(region=r[0] or "未知", value=r[1])
        for r in regions
    ]

    traffic_sources = [
        TrafficSource(name="直接访问", value=45),
        TrafficSource(name="搜索引擎", value=30),
        TrafficSource(name="社交媒体", value=15),
        TrafficSource(name="邮件", value=10),
    ]

    real_time_users = [
        VisitData(date="14:00", value=15),
        VisitData(date="14:05", value=22),
        VisitData(date="14:10", value=18),
        VisitData(date="14:15", value=25),
        VisitData(date="14:20", value=20),
    ]

    return DashboardData(
        stats=stats,
        visit_trend=visit_trend,
        region_distribution=region_distribution,
        traffic_sources=traffic_sources,
        real_time_users=real_time_users
    )


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """获取统计摘要"""
    return {"total_jobs": 100, "total_applications": 500}


@router.get("/visit-trend")
def get_visit_trend(days: int = Query(7, ge=1, le=30)):
    """获取访问趋势"""
    # Mock data
    return [
        {"date": "2026-03-21", "value": 120},
        {"date": "2026-03-22", "value": 150},
        {"date": "2026-03-23", "value": 180},
        {"date": "2026-03-24", "value": 200},
        {"date": "2026-03-25", "value": 190},
        {"date": "2026-03-26", "value": 220},
        {"date": "2026-03-27", "value": 250},
    ]


@router.get("/region")
def get_region_distribution(db: Session = Depends(get_db)):
    """获取地区分布"""
    regions = db.query(
        Student.province,
        func.count(Student.id)
    ).group_by(Student.province).all()

    return [{"region": r[0] or "未知", "value": r[1]} for r in regions]


@router.get("/traffic-sources")
def get_traffic_sources():
    """获取流量来源"""
    return [
        {"name": "直接访问", "value": 45},
        {"name": "搜索引擎", "value": 30},
        {"name": "社交媒体", "value": 15},
        {"name": "邮件", "value": 10},
    ]


@router.get("/realtime")
def get_realtime_users():
    """获取实时在线用户"""
    return [
        {"date": "14:00", "value": 15},
        {"date": "14:05", "value": 22},
        {"date": "14:10", "value": 18},
        {"date": "14:15", "value": 25},
        {"date": "14:20", "value": 20},
    ]
```

### 3.3 Statistics Trend API (`/api/v1/statistics/trend`)

```python
@router.get("/trend")
def get_trend_data(
    graduation_year: Optional[int] = None,
    college: Optional[str] = None,
    years: int = Query(5, ge=1, le=10),
    db: Session = Depends(get_db)
):
    """获取就业趋势数据"""
    # This requires a historical tracking table
    # Returning mock data structure
    current_year = 2026
    return [
        {"year": current_year - i, "employment_rate": 85 + i, "total": 1000 + i * 50}
        for i in range(years)
    ][::-1]
```

### 3.4 Statistics Industry Salary API (`/api/v1/statistics/industry-salary`)

```python
@router.get("/industry-salary")
def get_industry_salary(
    graduation_year: Optional[int] = None,
    college: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取各行业薪资数据"""
    # This requires job application/salary data
    # Returning mock data structure
    return [
        {"industry": "互联网", "avg_salary": 15000},
        {"industry": "金融", "avg_salary": 14000},
        {"industry": "教育", "avg_salary": 10000},
        {"industry": "制造", "avg_salary": 9000},
        {"industry": "房地产", "avg_salary": 12000},
    ]
```

### 3.5 Student Import/Export API

```python
@router.post("/import")
async def import_students(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """批量导入学生"""
    # Read Excel file
    contents = await file.read()
    df = pd.read_excel(BytesIO(contents))

    errors = []
    success = 0

    for idx, row in df.iterrows():
        try:
            student = StudentProfile(
                student_id=str(row['学号']),
                college=row['学院'],
                major=row['专业'],
                # ... map other fields
            )
            db.add(student)
            success += 1
        except Exception as e:
            errors.append(f"Row {idx + 2}: {str(e)}")

    db.commit()

    return {
        "total": len(df),
        "success": success,
        "failed": len(errors),
        "errors": errors
    }


@router.get("/export")
def export_students(
    college: Optional[str] = None,
    major: Optional[str] = None,
    employment_status: Optional[str] = None,
    graduation_year: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """导出学生数据"""
    query = db.query(StudentProfile)

    if college:
        query = query.filter(StudentProfile.college == college)
    if major:
        query = query.filter(StudentProfile.major == major)
    if graduation_year:
        query = query.filter(StudentProfile.graduation_year == graduation_year)

    students = query.all()

    # Create Excel in memory
    df = pd.DataFrame([{
        '学号': s.student_id,
        '学院': s.college,
        '专业': s.major,
        # ... map other fields
    } for s in students])

    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=students.xlsx"}
    )
```

---

## 4. AI Endpoints Status

### 4.1 CURRENT IMPLEMENTATION (Stubs with Mock Data)

The AI endpoints in `backend/app/api/v1/ai.py` exist but delegate to `ai_service`:

```python
# backend/app/services/ai_service.py
class AIService:
    async def generate_employment_profile(self, ...):
        # Returns mock data - should integrate with MiniMax API
        return {
            "score": 75,
            "professional_match": 80,
            "skill_match": 70,
            ...
        }
```

### 4.2 AI ENDPOINTS TO PRESERVE AS STUBS

| Endpoint | Status | Notes |
|----------|--------|-------|
| `POST /api/v1/ai/employment-profile` | Stub | Returns mock employment profile |
| `POST /api/v1/ai/job-recommendation` | Stub | Returns mock job recommendations |
| `POST /api/v1/ai/skill-path` | Stub | Returns mock skill path |
| `POST /api/v1/ai/warning` | Stub | Returns mock warnings |
| `POST /api/v1/ai/resume-analysis` | Stub | Returns mock resume analysis |
| `POST /api/v1/ai/graduate-vs-job` | Stub | Returns mock comparison |

### 4.3 FRONTEND AI MISMATCHES

**`/ai/analyze-resume`:**
- Frontend sends: `{ resume_url: string }`
- Backend expects: `{ resume_text: string, target_position: string }`

**`/ai/compare-options`:**
- Frontend sends: `{ option_a: string, option_b: string, context: string }`
- Backend: MISSING

---

## 5. Data Flow Diagrams

### 5.1 Student Management Flow
```
Frontend                    Backend                      Database
   |                           |                             |
   |-- GET /api/v1/students ->|-- Query StudentProfile ---->|
   |                           |                             |
   |<--------- Response -------|                             |
   |                           |                             |
   |-- PUT /api/v1/students/1->|-- Update StudentProfile --->|
   |                           |                             |
```

### 5.2 Job Application Flow
```
Frontend                    Backend                      Database
   |                           |                             |
   |-- GET /api/v1/jobs ------>|-- Query JobDescription --->|
   |                           |                             |
   |<--------- Jobs List -------|                             |
   |                           |                             |
   |-- POST /api/v1/jobs/apply>|-- Insert JobApplication --->|
   |                           |                             |
   |<------- Application ID ----|                             |
```

### 5.3 AI Service Flow
```
Frontend                    Backend                      External
   |                           |                        (MiniMax)
   |                           |                             |
   |-- POST /ai/employment --->|-- Validate Request -------->|
   |                           |-- Call AI Service (MOCK) -->|
   |                           |                             |
   |<------- Mock Response ----|                             |
```

---

## 6. Module Structure

```
backend/app/
├── api/
│   └── v1/
│       ├── __init__.py          # Route aggregation
│       ├── auth.py              # Authentication endpoints
│       ├── student.py           # Student CRUD endpoints
│       ├── statistics.py        # Statistics endpoints
│       ├── ai.py                # AI service endpoints (STUBS)
│       ├── job.py               # [MISSING] Job endpoints
│       └── dashboard.py         # [MISSING] Dashboard endpoints
├── models/
│   ├── student.py               # StudentProfile model
│   ├── job.py                   # JobDescription, JobApplication
│   ├── company.py               # Company model
│   └── account.py               # Account model
├── schemas/
│   ├── student.py               # Student Pydantic schemas
│   ├── job.py                   # Job Pydantic schemas
│   └── auth.py                  # Auth Pydantic schemas
├── services/
│   ├── ai_service.py            # AI service (MOCK implementation)
│   └── auth/                    # Auth service modules
└── core/
    ├── database.py              # DB connection
    ├── dependencies.py           # Dependency injection
    └── config.py                 # Configuration
```

---

## 7. Extension Points

### 7.1 Job Recommendations
- Currently stub: returns mock data
- Future: integrate real job matching algorithm
- Extension: add skill matching, location preference

### 7.2 Analytics/Dashboard
- Currently stub: returns mock data
- Future: add real page view tracking table
- Extension: add user behavior analytics

### 7.3 AI Service
- Currently stub: mock responses
- Future: integrate MiniMax API
- Extension: add more AI-powered features

---

## 8. Security Considerations

### 8.1 Missing Validations
- Job endpoints need company ownership validation
- Student import should validate file size and format
- Dashboard stats should be role-based (admin only)

### 8.2 Rate Limiting
- Already implemented for auth endpoints
- Should extend to job search and AI endpoints

### 8.3 File Upload Security
- Student import: validate Excel file format
- Limit file size (max 10MB)
- Scan for malicious content

---

## 9. Implementation Priority

| Priority | Items |
|----------|-------|
| P0 (Critical) | Job CRUD API, Job Application API |
| P1 (High) | Dashboard API, Student Import/Export |
| P2 (Medium) | Statistics Trend, Industry Salary |
| P3 (Low) | AI compare-options endpoint, Resume analyze endpoint fix |
