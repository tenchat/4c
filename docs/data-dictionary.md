# 数据字典 - 新增表结构

> **文档日期**: 2026-04-01 **来源**: `docs/data-analysis-report.md` Section 5 **状态**: Baseline - 待架构师确认

---

## 一、新增表结构

### 1.1 user_job_exposure（用户-职位曝光记录）

存储用户对职位的曝光记录，用于推荐算法训练。

| 字段名          | 类型 | 约束         | 说明                    | 来源字段                     |
| --------------- | ---- | ------------ | ----------------------- | ---------------------------- |
| `exposure_id`   | TEXT | PRIMARY KEY  | 曝光记录唯一ID          | 新生成 UUID                  |
| `user_id`       | TEXT | NOT NULL, FK | 用户ID                  | table3_action / exposure_A/B |
| `job_id`        | TEXT | NOT NULL, FK | 职位ID                  | table3_action / exposure_A/B |
| `exposure_type` | TEXT |              | 曝光类型 `'A'` 或 `'B'` | 区分数据集来源               |
| `created_at`    | TEXT | NOT NULL     | 创建时间                | 当前时间戳                   |

**索引**:

- `idx_exposure_user ON user_job_exposure(user_id)`
- `idx_exposure_job ON user_job_exposure(job_id)`

**外键关系**:

- `user_id` → `student_profiles(profile_id)`
- `job_id` → `job_descriptions(job_id)`

---

### 1.2 user_skills（用户技能多对多关系）

存储用户技能标签，支持多对多关系。

| 字段名       | 类型 | 约束         | 说明           | 来源字段               |
| ------------ | ---- | ------------ | -------------- | ---------------------- |
| `skill_id`   | TEXT | PRIMARY KEY  | 技能记录唯一ID | 新生成 UUID            |
| `user_id`    | TEXT | NOT NULL, FK | 用户ID         | table1_user.experience |
| `skill_name` | TEXT | NOT NULL     | 技能名称       | experience pipe分割    |
| `source`     | TEXT |              | 来源说明       | `'experience'`         |

**索引**:

- `idx_skills_user ON user_skills(user_id)`

**外键关系**:

- `user_id` → `student_profiles(profile_id)`

**示例数据**: | skill_id | user_id | skill_name | source | |----------|---------|------------|--------| | uuid1 | user_001 | 停车 | experience | | uuid2 | user_001 | 现场 | experience | | uuid3 | user_001 | 凤凰 | experience |

---

### 1.3 user_job_preference（用户求职意向）

存储用户的求职偏好设置。

| 字段名 | 类型 | 约束 | 说明 | 来源字段 |
| --- | --- | --- | --- | --- |
| `preference_id` | TEXT | PRIMARY KEY | 偏好记录唯一ID | 新生成 UUID |
| `user_id` | TEXT | NOT NULL, FK | 用户ID | table1_user.user_id |
| `desire_city_ids` | TEXT |  | 期望城市ID数组(JSON) | desire_jd_city_id |
| `desire_industry_ids` | TEXT |  | 期望行业ID数组(JSON) | desire_jd_industry_id |
| `desire_salary_min` | INTEGER |  | 期望最低薪资 | desire_jd_salary_id(解码) |
| `desire_salary_max` | INTEGER |  | 期望最高薪资 | desire_jd_salary_id(解码) |
| `created_at` | TEXT | NOT NULL | 创建时间 | 当前时间戳 |

**外键关系**:

- `user_id` → `student_profiles(profile_id)`

**数据格式示例**:

```json
{
  "desire_city_ids": ["551", "530"],
  "desire_industry_ids": ["房地产/建筑/建材/工程"],
  "desire_salary_min": 8000,
  "desire_salary_max": 15000
}
```

---

### 1.4 user_job_satisfaction（用户对投递结果的满意度）

记录用户对投递职位的满意度评价。

| 字段名            | 类型    | 约束         | 说明         | 来源字段                |
| ----------------- | ------- | ------------ | ------------ | ----------------------- |
| `satisfaction_id` | TEXT    | PRIMARY KEY  | 满意度记录ID | 新生成 UUID             |
| `user_id`         | TEXT    | NOT NULL, FK | 用户ID       | table3_action.user_id   |
| `job_id`          | TEXT    | NOT NULL, FK | 职位ID       | table3_action.jd_no     |
| `satisfied`       | INTEGER |              | 满意度 0/1   | table3_action.satisfied |

**约束**: `UNIQUE(user_id, job_id)` - 每个用户对每个职位只能有一条满意度记录

**外键关系**:

- `user_id` → `student_profiles(profile_id)`
- `job_id` → `job_descriptions(job_id)`

---

### 1.5 city_mapping（城市码映射表）

城市代码与城市名称的对照表。

| 字段名      | 类型    | 约束             | 说明                  |
| ----------- | ------- | ---------------- | --------------------- |
| `city_id`   | INTEGER | PRIMARY KEY      | 城市自增ID            |
| `city_code` | TEXT    | NOT NULL, UNIQUE | 城市代码，如 `"551"`  |
| `city_name` | TEXT    | NOT NULL         | 城市名称，如 `"合肥"` |
| `province`  | TEXT    |                  | 所属省份              |

**示例数据**: | city_id | city_code | city_name | province | |---------|-----------|-----------|---------| | 1 | 551 | 合肥 | 安徽 | | 2 | 530 | 南京 | 江苏 | | 3 | 791 | 南昌 | 江西 |

---

## 二、现有表新增字段

### 2.1 student_profiles 新增字段

| 字段名                | 类型 | 约束 | 说明       | 来源                            |
| --------------------- | ---- | ---- | ---------- | ------------------------------- |
| `live_city_id`        | TEXT |      | 居住城市码 | table1_user.live_city_id        |
| `desire_jd_salary_id` | TEXT |      | 期望薪资码 | table1_user.desire_jd_salary_id |

---

### 2.2 job_descriptions 新增字段

| 字段名 | 类型 | 约束 | 说明 | 来源 |
| --- | --- | --- | --- | --- |
| `jd_sub_type` | TEXT |  | 职位子类型/行业分类 | table2_jd.jd_sub_type |
| `require_nums` | INTEGER |  | 招聘人数 | table2_jd.require_nums |
| `is_travel` | INTEGER |  | 是否需要出差 | table2_jd.is_travel |
| `max_edu_level` | TEXT |  | 最高学历要求 | table2_jd.max_edu_level |
| `resume_language_required` | TEXT |  | 简历语言要求 | table2_jd.resume_language_required |

---

### 2.3 college_employment 字段类型变更

| 字段名               | 原类型 | 新类型 | 说明                       |
| -------------------- | ------ | ------ | -------------------------- |
| `employment_rate`    | TEXT   | REAL   | 就业率（百分比数值）       |
| `further_study_rate` | TEXT   | REAL   | 升学率（百分比数值）       |
| `overseas_rate`      | TEXT   | REAL   | 出国率（百分比数值，新增） |

---

## 三、数据类型映射参考

### 3.1 数据集 → SQLite 类型映射

| 数据集字段类型       | SQLite 存储类型 | 说明                 |
| -------------------- | --------------- | -------------------- |
| UUID 字符串          | TEXT            | 直接存储             |
| 整数（城市码、年龄） | INTEGER         | 直接存储             |
| 日期(YYYYMMDD)       | TEXT            | 转为 YYYY-MM-DD 格式 |
| 薪资                 | INTEGER         | 单位：元/月          |
| 长文本               | TEXT            | 含换行符需清洗       |
| 枚举字符串           | TEXT            | 建立字典表映射       |
| JSON 数组            | TEXT            | 字符串形式存储       |

---

## 四、建议新增索引

| 表名                 | 索引字段                           | 索引类型   | 理由              |
| -------------------- | ---------------------------------- | ---------- | ----------------- |
| `student_profiles`   | `(college, graduation_year)`       | 复合索引   | 学院+届次联合查询 |
| `student_profiles`   | `employment_status`                | 单字段索引 | 就业状态筛选      |
| `student_profiles`   | `major`                            | 单字段索引 | 专业维度查询      |
| `job_descriptions`   | `(company_id, status)`             | 复合索引   | 企业岗位查询      |
| `job_descriptions`   | `(industry, city)`                 | 复合索引   | 行业+城市筛选     |
| `job_applications`   | `(account_id, status)`             | 复合索引   | 用户申请记录查询  |
| `job_applications`   | `job_id`                           | 单字段索引 | 岗位收到投递查询  |
| `college_employment` | `(university_id, graduation_year)` | 复合索引   | 历年数据查询      |

---

**待更新**: 执行后的实际表结构确认
