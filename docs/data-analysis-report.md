# 数据结构分析报告：非结构化数据集 → SQLite 数据库导入方案

> **报告日期**: 2026-04-01 **任务类型**: 纯分析任务（不修改任何代码或数据） **分析范围**: `./dataset` 目录数据集 + `./backend/employment.db` 数据库

---

## ⚠️ 严重数据质量问题警告

1. **编码不一致**: 部分 CSV 文件（`大学生就业选择.csv` 系列）存在编码混合格式，导致中文显示为乱码
2. **格式不标准**: 招聘数据 CSV 使用嵌入逗号作为字段分隔符（同字段内含逗号），无法直接用标准 CSV 解析
3. **数据规模风险**: `table2_jd_part*.csv` 三个文件合计约 180K 行 × 3 ≈ 540K 行职位描述数据，需评估 SQLite 导入性能

---

## 一、数据集目录清单

### 1.1 文件总览

| 文件路径 | 类型 | 大小 | 行数（估算） | 命名推断含义 |
| --- | --- | --- | --- | --- |
| `train_data/table1_user.csv` | CSV | 2.6 MB | ~4,500 | 用户画像数据 |
| `train_data/table2_jd_part1.csv` | CSV | 95 MB | ~180,000 | 职位描述（上半） |
| `train_data/table2_jd_part2.csv` | CSV | 96 MB | ~180,000 | 职位描述（中段） |
| `train_data/table2_jd_part3.csv` | CSV | 96 MB | ~180,000 | 职位描述（下半） |
| `train_data/table3_action.csv` | CSV | 50 MB | ~700,000 | 用户行为数据 |
| `zhaopin_round1_test_20190716/user_ToBePredicted.csv` | CSV | 285 KB | ~2,000 | 待预测用户 |
| `zhaopin_round1_test_20190716/zhaopin_round1_user_exposure_A_20190723.csv` | CSV | 2.5 MB | ~20,000 | 曝光数据A |
| `zhaopin_round1_test_20190716/zhaopin_round1_user_exposure_B_20190819.csv` | CSV | 2.7 MB | ~20,000 | 曝光数据B |
| `大学生就业选择.csv` | CSV | 763 KB | ~10,000 | 就业选择数据 |
| `大学生就业选择(2).csv` | CSV | 763 KB | ~10,000 | 就业选择数据（副本） |
| `大学生毕业就业选择样例数据_10000条.csv` | CSV | 642 KB | ~10,000 | 就业样例数据 |
| `学校数据/1.各学历去向落实率（基数确定+就业过程数据）.xlsx` | XLSX | 11 KB | - | 学历就业率 |
| `学校数据/2.各学历去向落实率（过程数据）.xlsx` | XLSX | 11 KB | - | 学历就业率 |
| `学校数据/3.各学院去向落实情况统计表（过程数据）.xlsx` | XLSX | 32 KB | - | 学院就业统计 |
| `学校数据/4.各学院去向落实情况统计表（基数确定+就业过程数据）.xlsx` | XLSX | 32 KB | - | 学院就业统计 |
| `学校数据/5.各学历毕业去向分类统计（含升学-过程数据）.xlsx` | XLSX | 15 KB | - | 毕业去向分类 |
| `学校数据/6.区域流向情况统计表.xlsx` | XLSX | 16 KB | - | 区域流向统计 |
| `学校数据/7.各学历毕业去向分类统计（含升学-基数确定+就业过程）.xlsx` | XLSX | 15 KB | - | 毕业去向分类 |
| `学校数据/8.各学院毕业去向分类统计（含升学-过程数据）.xlsx` | XLSX | 69 KB | - | 学院毕业去向 |
| `字段说明.docx` | DOCX | 20 KB | - | 字段说明文档 |

**总数据规模估算**: ~350 MB，跨多种格式（CSV、XLSX、DOCX）

---

## 二、数据内容抽样分析

### 2.1 招聘数据集（`train_data/`）

#### table1_user.csv — 用户画像

| 字段名 | 数据类型 | 示例值 | 可空性 | 数据质量问题 | 建议处理 |
| --- | --- | --- | --- | --- | --- |
| `user_id` | UUID字符串 | `17e1b9f107dd1214bd78dec6d91593a4` | NOT NULL | 无 | 直接映射 |
| `live_city_id` | 整数（城市码） | `551` | NOT NULL | 无 | 直接映射 |
| `desire_jd_city_id` | 字符串（复合） | `551,-,-` | 可空 | 格式不统一，含多值 | 拆分为多表或JSON |
| `desire_jd_industry_id` | 字符串（枚举） | `房地产/建筑/建材/工程` | 可空 | 无 | 建立字典表映射 |
| `desire_jd_type_id` | 字符串（枚举） | `工程造价/预结算` | 可空 | 无 | 建立字典表映射 |
| `desire_jd_salary_id` | 字符串（薪资码） | `100002000` | 可空 | 编码格式特殊 | 需解码或区间化 |
| `cur_industry_id` | 字符串（枚举） | `房地产/建筑/建材/工程` | 可空 | 无 | 复用字典表 |
| `cur_jd_type` | 字符串（枚举） | `土木/建筑/装修/市政工程` | 可空 | 无 | 复用字典表 |
| `cur_salary_id` | 字符串（薪资码） | `0200104000` | 可空 | 编码格式特殊，含负值 `-7249` | 异常值清洗 |
| `cur_degree_id` | 字符串（枚举） | `大专`, `本科`, `硕士` | NOT NULL | 无 | 建立字典表 |
| `birthday` | 整数（年龄） | `24`, `33` | NOT NULL | 实际为年龄，非生日 | 重命名字段 |
| `start_work_date` | 整数（年份） | `2017`, `2015` | 可空 | 实际为开始工作年份 | 重命名字段 |
| `experience` | 字符串（技能标签） | `停车\|现场\|凤凰\|...` | 可空 | pipe分隔的技能列表，冗长 | 拆分为多对多关系 |

#### table2_jd_part\*.csv — 职位描述

| 字段名 | 数据类型 | 示例值 | 可空性 | 数据质量问题 | 建议处理 |
| --- | --- | --- | --- | --- | --- |
| `jd_no` | UUID字符串 | `3cf395f1d6f12de112d118c0349acbcd` | NOT NULL | 无 | 直接映射 |
| `jd_title` | 字符串 | `景观主创设计师` | NOT NULL | 无 | 直接映射 |
| `company_name` | 字符串 | `-`（空或占位） | 可空 | 部分为空 | 置空或"未知" |
| `city` | 整数（城市码） | `530` | NOT NULL | 无 | 外键关联城市表 |
| `jd_sub_type` | 字符串（枚举） | `园林/景观设计` | NOT NULL | 无 | 建立字典表 |
| `require_nums` | 整数 | `2`, `5` | 可空 | 无 | 直接映射 |
| `max_salary` | 整数 | `25000`, `8000` | 可空 | 部分为0 | 需确认含义 |
| `min_salary` | 整数 | `15000`, `4000` | 可空 | 无 | 直接映射 |
| `start_date` | 整数（日期） | `20190325` | 可空 | 格式为YYYYMMDD | 转为标准日期 |
| `end_date` | 整数（日期） | `20190524` | 可空 | 格式为YYYYMMDD | 转为标准日期 |
| `is_travel` | 整数（布尔） | `1` | 可空 | 无 | 直接映射 |
| `min_years` | 整数 | `510`, `305` | 可空 | 值异常大如510？ | 需核实，可能为编码 |
| `key` | 字符串 | `本科` | 可空 | 可能为关键词 | 需进一步分析 |
| `min_edu_level` | 字符串 | `本科`, `\N` | 可空 | `\N` 表示空 | 标准化处理 |
| `max_edu_level` | 字符串 | `\N` | 可空 | `\N` 表示空 | 标准化处理 |
| `is_mangerial` | 字符串 | `\N` | 可空 | 疑似typo（mangerial→managerial） | 重命名字段 |
| `resume_language_required` | 字符串 | `\N` | 可空 | 无 | 直接映射 |
| `job_description` | 长文本 | 岗位职责+任职要求... | 可空 | 含换行符、特殊字符 | 清洗或截断 |

#### table3_action.csv — 用户行为

| 字段名 | 数据类型 | 示例值 | 可空性 | 数据质量问题 | 建议处理 |
| --- | --- | --- | --- | --- | --- |
| `user_id` | UUID字符串 | `17e1b9f107dd1214bd78dec6d91593a4` | NOT NULL | 无 | 外键关联用户表 |
| `jd_no` | UUID字符串 | `4ce99de185f55bea127ccd74c4bbf0ad` | NOT NULL | 无 | 外键关联职位表 |
| `browsed` | 整数（布尔） | `0` | NOT NULL | 无 | 直接映射 |
| `delivered` | 整数（布尔） | `0` | NOT NULL | 无 | 直接映射 |
| `satisfied` | 整数（布尔） | `0` | NOT NULL | 无 | 直接映射 |

**关联关系**:

- `user_id` ↔ `table1_user.user_id`（用户行为→用户）
- `jd_no` ↔ `table2_jd_part*.jd_no`（用户行为→职位）

### 2.2 招聘测试数据集（`zhaopin_round1_test_20190716/`）

#### user_ToBePredicted.csv — 待预测用户

字段结构同 `table1_user.csv`，表示需要预测就业意向的用户。

#### zhaopin_round1_user_exposure_A/B — 曝光数据

| 字段名    | 数据类型   | 说明   |
| --------- | ---------- | ------ |
| `user_id` | UUID字符串 | 用户ID |
| `jd_no`   | UUID字符串 | 职位ID |

**用途**: 记录用户-职位的曝光记录，用于推荐算法训练。

### 2.3 就业选择数据集（中文 CSV）

> ⚠️ **编码问题严重**: 文件编码混用 GB2312/GBK/UTF-8，导致中文显示为乱码

从原始数据观察，结构推断为：

| 字段序号 | 推断字段名 | 推断类型                          | 问题                               |
| -------- | ---------- | --------------------------------- | ---------------------------------- |
| 1        | ID         | 整数                              | 无                                 |
| 2        | 性别       | 枚举（男/女）                     | 无                                 |
| 3        | 专业       | 字符串                            | 中文乱码                           |
| 4        | 学历       | 枚举（本科/硕士/大专）            | 中文乱码                           |
| 5        | 就业方向   | 枚举（创业/公务员/出国/自由职业） | 中文乱码                           |
| 6        | 行业       | 字符串                            | 中文乱码                           |
| 7        | 薪资       | 浮点数                            | 存在负值（-7249, -9367），疑似异常 |
| 8        | 城市       | 字符串                            | 中文乱码                           |
| 9        | 工作年限   | 整数或浮点                        | 存在浮点（4.1279...）              |
| 10       | 是否就业   | 枚举（是/否）                     | 中文乱码                           |
| 11       | 备注       | 字符串                            | 可空                               |

### 2.4 学校数据（Excel 文件）

8 个 XLSX 文件，内容涉及：

1. 各学历去向落实率（基数确定+就业过程数据）
2. 各学历去向落实率（过程数据）
3. 各学院去向落实情况统计表（过程数据）
4. 各学院去向落实情况统计表（基数确定+就业过程数据）
5. 各学历毕业去向分类统计（含升学-过程数据）
6. 区域流向情况统计表
7. 各学历毕业去向分类统计（含升学-基数确定+就业过程）
8. 各学院毕业去向分类统计（含升学-过程数据）

**与现有表的对应关系**:

- `college_employment` 表已存储部分学院就业数据
- XLSX 文件提供了更细粒度的分类统计（分学历、分学院、分去向类型）

---

## 三、现有数据库缺陷清单

**数据库文件**: `backend/employment.db` **数据库类型**: SQLite **表数量**: 18 张

### 3.1 表结构缺陷

| 表名 | 问题类型 | 具体描述 | 改进建议 |
| --- | --- | --- | --- |
| `student_profiles` | 外键缺失 | `account_id` 应为外键指向 `accounts`，但未建约束 | 添加 `FOREIGN KEY (account_id) REFERENCES accounts(account_id)` |
| `student_profiles` | 索引缺失 | `college`, `major`, `graduation_year`, `employment_status` 经常作为查询条件但无索引 | 为这些字段添加索引 |
| `student_profiles` | 字段冗余 | `province_origin` 存储省份但无标准编码 | 考虑建立省份字典表并外键关联 |
| `job_descriptions` | 主键类型 | 使用 UUID 字符串作为主键，影响查询性能 | 考虑使用自增整数或复合主键 |
| `job_descriptions` | 字段类型 | `min_salary`, `max_salary` 为 INTEGER 但可能需要处理范围查询 | 考虑拆分为起始值和单位 |
| `job_descriptions` | 索引缺失 | `company_id`, `industry`, `city`, `status` 无索引 | 添加复合索引 |
| `job_applications` | 外键缺失 | `job_id` 和 `account_id` 应建外键约束 | 添加外键约束 |
| `job_applications` | 索引缺失 | `(job_id, account_id)` 组合应建唯一索引防重复申请 | 添加 UNIQUE INDEX |
| `college_employment` | 字段类型 | `employment_rate`, `further_study_rate` 存储为 TEXT（百分比字符串），无法数值计算 | 改为 REAL 类型 |
| `college_employment` | 主键设计 | 使用 UUID 作为主键而非业务主键 | 考虑改为 `(university_id, college_name, graduation_year)` 复合主键 |
| `scarce_talents` | 字段歧义 | `job_type` 和 `industry` 字段含义需明确 | 检查是否与职位描述表的 `jd_sub_type` 统一 |
| `universities` | 数据缺失 | 仅 1 条数据 | 需补充或确认是否为种子数据 |
| **全局问题** | 无创建时间索引 | 所有表均无 `created_at` 索引 | 审计日志类查询会慢 |

### 3.2 外键关系缺失

当前数据库**所有表之间均无外键约束**，导致：

1. **引用完整性无法保证**: 可插入不存在的 `account_id` 到 `student_profiles`
2. **级联删除无法配置**: 删除 `accounts` 记录后 `student_profiles` 孤立
3. **JOIN 性能无法优化**: 数据库无法利用外键关系优化查询

### 3.3 索引使用情况

| 表名 | 现有索引 | 缺失索引 |
| --- | --- | --- |
| `accounts` | `pk` (主键) | `username`, `role` |
| `student_profiles` | `sqlite_autoindex` (隐式主键) | `college`, `major`, `graduation_year`, `employment_status`, `account_id` |
| `job_descriptions` | `pk` (主键) | `company_id`, `industry`, `city`, `status` |
| `companies` | `pk` (主键) | `account_id` |
| `job_applications` | `pk` (主键) | `(job_id, account_id)` 唯一索引 |
| `college_employment` | `pk` (主键) | `(university_id, graduation_year)` |

### 3.4 数据覆盖度问题

| Dataset 数据类型 | 现有表 | 是否有对应 | 缺失字段 |
| --- | --- | --- | --- |
| 用户画像（table1_user） | `student_profiles` | 部分 | `desire_jd_city_id`, `desire_jd_industry_id`, `experience`（技能标签） |
| 职位描述（table2_jd） | `job_descriptions` | 部分 | `jd_sub_type`, `require_nums`, `start_date`, `end_date`, `is_travel`, `min_years`, `max_edu_level`, `resume_language_required` |
| 用户行为（table3_action） | `job_applications` | 部分 | `browsed`, `satisfied` 字段无法映射 |
| 曝光数据 | **无对应表** | ❌ | 需新建 `user_job_exposure` 表 |
| 学校就业率 | `college_employment` | 部分 | 分学历统计、学院详细去向分类数据 |
| 稀缺人才 | `scarce_talents` | 部分 | `demand_rank`, `demand_index` 字段缺失 |

---

## 四、数据映射表

### 4.1 用户数据映射（table1_user → student_profiles）

| dataset 字段 | 来源文件 | 目标表 | 目标字段 | 转换规则 |
| --- | --- | --- | --- | --- |
| `user_id` | table1_user.csv | student_profiles | `profile_id` | 直接复制（UUID） |
| `live_city_id` | table1_user.csv | — | `cur_city` | 需关联城市码表转换为城市名 |
| `desire_jd_city_id` | table1_user.csv | **新建表** | `user_job_preference.desire_city_ids` | 解析 `551,-,-` 格式为 JSON 数组 |
| `desire_jd_industry_id` | table1_user.csv | **新建表** | `user_job_preference.industry_ids` | 行业名称标准化 |
| `desire_jd_salary_id` | table1_user.csv | student_profiles | `desire_salary_min/max` | 需解码薪资码为区间 |
| `cur_industry_id` | table1_user.csv | student_profiles | `cur_industry` | 直接映射 |
| `cur_degree_id` | table1_user.csv | student_profiles | `degree` | 需建立学历字典（大专→1, 本科→2, 硕士→3） |
| `birthday` | table1_user.csv | — | — | **跳过**：实为年龄，非生日 |
| `start_work_date` | table1_user.csv | student_profiles | — | 需确认是否需要 |
| `experience` | table1_user.csv | **新建表** | `user_skills.skill_tags` | pipe 分隔，需拆分为多对多关系 |

### 4.2 职位数据映射（table2_jd → job_descriptions）

| dataset 字段 | 来源文件 | 目标表 | 目标字段 | 转换规则 |
| --- | --- | --- | --- | --- |
| `jd_no` | table2_jd_part\*.csv | job_descriptions | `job_id` | 直接复制（UUID） |
| `jd_title` | table2_jd_part\*.csv | job_descriptions | `title` | 直接复制 |
| `company_name` | table2_jd_part\*.csv | job_descriptions | `company_name` | 空值转为"未知" |
| `city` | table2_jd_part\*.csv | job_descriptions | `city` | 城市码转城市名 |
| `jd_sub_type` | table2_jd_part\*.csv | job_descriptions | `industry` | 职位子类型作为行业 |
| `require_nums` | table2_jd_part\*.csv | job_descriptions | — | **跳过**：招聘人数非岗位属性 |
| `min_salary` | table2_jd_part\*.csv | job_descriptions | `min_salary` | 直接复制（单位：元/月） |
| `max_salary` | table2_jd_part\*.csv | job_descriptions | `max_salary` | 直接复制 |
| `start_date` | table2_jd_part\*.csv | job_descriptions | `published_at` | YYYYMMDD → `YYYY-MM-DD` |
| `end_date` | table2_jd_part\*.csv | job_descriptions | `expired_at` | YYYYMMDD → `YYYY-MM-DD` |
| `is_travel` | table2_jd_part\*.csv | job_descriptions | — | **跳过**：出差要求非核心字段 |
| `min_years` | table2_jd_part\*.csv | job_descriptions | `min_exp_years` | 需核实异常值（510等） |
| `min_edu_level` | table2_jd_part\*.csv | job_descriptions | `min_degree` | 标准化：本科→2，大专→1 |
| `job_description` | table2_jd_part\*.csv | job_descriptions | `description` | 清洗特殊字符 |

### 4.3 用户行为映射（table3_action → job_applications）

| dataset 字段 | 来源文件 | 目标表 | 目标字段 | 转换规则 |
| --- | --- | --- | --- | --- |
| `user_id` | table3_action.csv | job_applications | `account_id` | 需通过 table1_user 关联 accounts 获取 account_id |
| `jd_no` | table3_action.csv | job_applications | `job_id` | 直接复制 |
| `browsed` | table3_action.csv | — | — | **跳过**：浏览行为不计入申请表 |
| `delivered` | table3_action.csv | job_applications | `status` | 投递→1，未投递→0 |
| `satisfied` | table3_action.csv | **新建表** | `user_job_satisfaction.satisfied` | 标记用户对投递结果的满意度 |

---

## 五、需要新增/修改的表结构

### 5.1 新增表

#### user_job_exposure（用户-职位曝光记录）

```sql
CREATE TABLE user_job_exposure (
    exposure_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    job_id TEXT NOT NULL,
    exposure_type TEXT,  -- 'A' 或 'B'，区分数据集来源
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES student_profiles(profile_id),
    FOREIGN KEY (job_id) REFERENCES job_descriptions(job_id)
);

CREATE INDEX idx_exposure_user ON user_job_exposure(user_id);
CREATE INDEX idx_exposure_job ON user_job_exposure(job_id);
```

#### user_skills（用户技能多对多关系）

```sql
CREATE TABLE user_skills (
    skill_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    skill_name TEXT NOT NULL,
    source TEXT,  -- 'experience' 来自经历字段
    FOREIGN KEY (user_id) REFERENCES student_profiles(profile_id)
);

CREATE INDEX idx_skills_user ON user_skills(user_id);
```

#### user_job_preference（用户求职意向）

```sql
CREATE TABLE user_job_preference (
    preference_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    desire_city_ids TEXT,  -- JSON数组，如 ["551", "530"]
    desire_industry_ids TEXT,
    desire_salary_min INTEGER,
    desire_salary_max INTEGER,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES student_profiles(profile_id)
);
```

#### user_job_satisfaction（用户对投递结果的满意度）

```sql
CREATE TABLE user_job_satisfaction (
    satisfaction_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    job_id TEXT NOT NULL,
    satisfied INTEGER,  -- 0/1
    FOREIGN KEY (user_id) REFERENCES student_profiles(profile_id),
    FOREIGN KEY (job_id) REFERENCES job_descriptions(job_id),
    UNIQUE(user_id, job_id)
);
```

#### city_mapping（城市码映射表）

```sql
CREATE TABLE city_mapping (
    city_id INTEGER PRIMARY KEY,
    city_code TEXT NOT NULL,  -- 如 "551"
    city_name TEXT NOT NULL,
    province TEXT
);
```

### 5.2 需修改的现有表

#### student_profiles 新增字段

```sql
ALTER TABLE student_profiles ADD COLUMN live_city_id TEXT;
ALTER TABLE student_profiles ADD COLUMN desire_jd_salary_id TEXT;
```

#### job_descriptions 新增字段

```sql
ALTER TABLE job_descriptions ADD COLUMN jd_sub_type TEXT;
ALTER TABLE job_descriptions ADD COLUMN require_nums INTEGER;
ALTER TABLE job_descriptions ADD COLUMN is_travel INTEGER;
ALTER TABLE job_descriptions ADD COLUMN max_edu_level TEXT;
ALTER TABLE job_descriptions ADD COLUMN resume_language_required TEXT;
```

#### college_employment 修改字段类型

```sql
-- 将 TEXT 类型改为 REAL
ALTER TABLE college_employment ALTER COLUMN employment_rate TYPE REAL;
ALTER TABLE college_employment ALTER COLUMN further_study_rate TYPE REAL;
ALTER TABLE college_employment ALTER COLUMN overseas_rate TYPE REAL;
```

### 5.3 建议新增索引

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

## 六、数据清洗规则清单

### 6.1 通用清洗规则

| 规则类型       | 实现方式                            |
| -------------- | ----------------------------------- |
| 去除前后空白   | `strip()`                           |
| 统一 NULL 表示 | `\N`, `null`, `NULL`, `""` → `NULL` |
| 特殊字符清洗   | 换行符 `\n` → 空格，引号标准化      |

### 6.2 字段专项清洗

#### 日期字段

| 源格式             | 目标格式     | 示例                      |
| ------------------ | ------------ | ------------------------- |
| `YYYYMMDD`（整数） | `YYYY-MM-DD` | `20190325` → `2019-03-25` |

**异常值处理**: 若日期值 < `19900101` 或 > `20301231`，设为 `NULL`

#### 薪资字段

| 问题         | 清洗规则           | 示例                   |
| ------------ | ------------------ | ---------------------- |
| 含单位字符串 | 提取数字部分       | `"8000元/月"` → `8000` |
| 负值         | 设为 `NULL` 或 `0` | `-7249` → `NULL`       |
| 超出合理范围 | 上限 100 万/月     | `9999999` → `NULL`     |

#### 城市码字段

- 格式：`"551"` 或 `"551,-,-"`（多值）
- 清洗：提取主城市码，去除 `-` 占位符
- 需建立 `city_mapping` 表进行解码

#### 行业字段

- 标准化：去除首尾空格，移除 `/` 重复
- 建立 `industry_mapping` 表映射非标准名称

#### 学历字段

| 原始值 | 标准化值 |
| ------ | -------- |
| `大专` | `1`      |
| `本科` | `2`      |
| `硕士` | `3`      |
| `博士` | `4`      |

#### 薪资码字段（`*_salary_id`）

- 格式：如 `100002000`, `0200104000`
- 规律：前4位可能为分类，后6位为薪资区间
- **建议**：直接转为薪资区间值或咨询数据提供方

#### 技能标签字段（experience）

- 分隔符：`|`（pipe）
- 清洗：去除空标签，合并重复项
- 存储：拆分到 `user_skills` 表

### 6.3 异常值处理策略

| 字段        | 异常特征              | 处理方式                |
| ----------- | --------------------- | ----------------------- |
| `min_years` | 值 > 50（如510）      | 设为 `NULL`，需人工核实 |
| `salary`    | 负值                  | 设为 `NULL`             |
| `salary`    | 超出 100 万/月        | 设为 `NULL`             |
| `degree`    | 非标准枚举值          | 建立映射或设为 `NULL`   |
| `birthday`  | > 100 或 < 15（年龄） | 设为 `NULL`             |

---

## 七、导入顺序建议

基于外键依赖关系，建议按以下顺序导入数据：

```
1. city_mapping          (城市码对照表，无依赖)
       ↓
2. universities          (学校信息，无依赖)
       ↓
3. companies             (企业信息，无依赖)
       ↓
4. student_profiles       (依赖 accounts，通过 account_id 关联)
       ↓
5. job_descriptions       (依赖 companies)
       ↓
6. user_skills            (依赖 student_profiles)
       ↓
7. user_job_preference    (依赖 student_profiles)
       ↓
8. user_job_satisfaction  (依赖 student_profiles, job_descriptions)
       ↓
9. user_job_exposure      (依赖 student_profiles, job_descriptions)
       ↓
10. job_applications      (依赖 student_profiles, job_descriptions)
       ↓
11. college_employment    (依赖 universities)
```

---

## 八、风险与待确认问题

### 8.1 高风险问题

| # | 问题 | 影响 | 需要确认 |
| --- | --- | --- | --- |
| 1 | **编码不一致** | 大学生就业选择.csv 系列文件无法正确解析 | 确认源文件编码，或联系数据提供方 |
| 2 | **薪资码格式不明** | `desire_jd_salary_id`, `cur_salary_id` 无法解码 | 确认薪资码编码规则 |
| 3 | **min_years 异常值** | 值如 510, 305 超出合理范围 | 确认是否应为月份或其他单位 |
| 4 | **user_id 与 account_id 映射** | table3_action 使用 user_id，但 job_applications 用 account_id | 确认两个 ID 的对应关系 |

### 8.2 中风险问题

| # | 问题 | 影响 | 需要确认 |
| --- | --- | --- | --- |
| 5 | **company_name 大量为空** | 约 50%+ 职位描述缺少公司名 | 确认是否需要补充公司信息 |
| 6 | **职位数据分3个CSV** | table2_jd_part1/2/3 可能存在重复 jd_no | 导入前需去重 |
| 7 | **职位数据量级** | 540K 职位可能超出 SQLite 高效查询范围 | 考虑分表或优化索引 |

### 8.3 待人工确认问题

1. **数据归属**: table1_user 的 user_id 是否已关联 accounts 表？还是需要新建 account 记录？
2. **就业状态**: 大学生就业选择.csv 中的"是否就业"字段是否要反向填充 `student_profiles.employment_status`？
3. **数据时效性**: 招聘数据集标注 2019 年，是否需要与当前年份对齐或标记为历史数据？
4. **隐私合规**: 用户 experience 字段包含工作经历描述，是否需要脱敏处理？
5. **学校数据映射**: 8 个 Excel 文件的表头结构如何？是否与现有 `college_employment` 字段完全对应？

---

## 九、字段分析矩阵汇总

| 字段名                | 源文件        | 推断类型 | 可空性   | 质量问题   | 建议处理              |
| --------------------- | ------------- | -------- | -------- | ---------- | --------------------- |
| user_id               | table1_user   | UUID     | NOT NULL | 无         | 主键                  |
| live_city_id          | table1_user   | INTEGER  | NOT NULL | 无         | 外键关联 city_mapping |
| desire_jd_city_id     | table1_user   | STRING   | 可空     | 复合格式   | 解析为 JSON 数组      |
| desire_jd_industry_id | table1_user   | STRING   | 可空     | 无         | 标准化映射            |
| desire_jd_salary_id   | table1_user   | STRING   | 可空     | 格式不明   | **待确认解码规则**    |
| cur_industry_id       | table1_user   | STRING   | 可空     | 无         | 标准化映射            |
| cur_salary_id         | table1_user   | STRING   | 可空     | 含负值     | 异常值清洗            |
| cur_degree_id         | table1_user   | ENUM     | NOT NULL | 无         | 数值化映射            |
| birthday              | table1_user   | INTEGER  | NOT NULL | 实为年龄   | **跳过或重命名**      |
| start_work_date       | table1_user   | INTEGER  | 可空     | 实为年份   | 重命名字段            |
| experience            | table1_user   | STRING   | 可空     | pipe分隔   | 拆分到 user_skills    |
| jd_no                 | table2_jd     | UUID     | NOT NULL | 无         | 主键                  |
| jd_title              | table2_jd     | STRING   | NOT NULL | 无         | 直接映射              |
| company_name          | table2_jd     | STRING   | 可空     | 大量为空   | 空值处理为"未知"      |
| city                  | table2_jd     | INTEGER  | NOT NULL | 无         | 外键关联              |
| min_salary            | table2_jd     | INTEGER  | 可空     | 无         | 直接映射              |
| max_salary            | table2_jd     | INTEGER  | 可空     | 无         | 直接映射              |
| min_years             | table2_jd     | INTEGER  | 可空     | 异常值510+ | **待确认单位**        |
| min_edu_level         | table2_jd     | STRING   | 可空     | \N表示空   | 标准化                |
| job_description       | table2_jd     | TEXT     | 可空     | 含特殊字符 | 清洗存储              |
| user_id               | table3_action | UUID     | NOT NULL | 无         | 外键                  |
| jd_no                 | table3_action | UUID     | NOT NULL | 无         | 外键                  |
| browsed               | table3_action | BOOLEAN  | NOT NULL | 无         | 跳过或建曝光表        |
| delivered             | table3_action | BOOLEAN  | NOT NULL | 无         | 映射到 status         |
| satisfied             | table3_action | BOOLEAN  | NOT NULL | 无         | 新建满意度表          |

---

## 十、结论

### 10.1 可直接导入的数据

1. **table2_jd_part\*.csv** → `job_descriptions`：字段对应度较高，可直接清洗导入
2. **table1_user.csv** → `student_profiles`：基础字段可直接映射，但需补充 account_id 关联

### 10.2 需新建中间表的数据

1. **experience 字段** → `user_skills`：技能标签需多对多表
2. **曝光数据** → `user_job_exposure`：无现有表对应
3. **满意度数据** → `user_job_satisfaction`：table3_action.satisfied 需独立表

### 10.3 存在严重问题的数据

1. **大学生就业选择.csv 系列**：编码问题导致无法解析，需联系数据源
2. **薪资码字段**：解码规则不明，需确认

### 10.4 数据库改进建议优先级

| 优先级 | 改进项                           | 工作量             |
| ------ | -------------------------------- | ------------------ |
| P0     | 添加外键约束                     | 中等               |
| P0     | 为常用查询字段添加索引           | 低                 |
| P1     | 修改 college_employment 字段类型 | 低                 |
| P1     | 新建曝光表和技能表               | 中等               |
| P2     | 优化主键策略（UUID→自增）        | 高（涉及大量外键） |

---

**报告结束**

_本报告为纯分析输出，未包含任何 Python/ETL 实现代码。_
