# 数据导入执行计划

> **基于**: `docs/data-analysis-report.md` **创建日期**: 2026-04-01 **执行角色**: planner agent

---

## 概述

本计划将非结构化数据集导入到 `backend/employment.db` SQLite 数据库，包含 5 个阶段，总工期约 5-7 天。

---

## 阶段依赖图

```
Phase 1 (Schema)
       │
       ▼
Phase 2 (Clean Functions)
       │
       ▼
Phase 3 (Import)
  ├── 3.1 字典表 (city_mapping, industry_mapping)
  ├── 3.2 主数据 (universities, companies)
  ├── 3.3 用户数据 (student_profiles, user_skills, user_job_preference)
  ├── 3.4 职位数据 (job_descriptions)
  ├── 3.5 行为数据 (job_applications, user_job_exposure, user_job_satisfaction)
  └── 3.6 学校数据 (college_employment)
       │
       ▼
Phase 4 (Tests)
       │
       ▼
Phase 5 (Documentation)
```

---

## Phase 1: 数据库 Schema 变更

**执行角色**: architect **依赖**: 无 **工作量**: 约 2-3 小时

### 1.1 新增表

| 序号 | 表名                    | 说明                   |
| ---- | ----------------------- | ---------------------- |
| 1    | `user_job_exposure`     | 用户-职位曝光记录      |
| 2    | `user_skills`           | 用户技能多对多关系     |
| 3    | `user_job_preference`   | 用户求职意向           |
| 4    | `user_job_satisfaction` | 用户对投递结果的满意度 |
| 5    | `city_mapping`          | 城市码映射表           |
| 6    | `industry_mapping`      | 行业字典表             |

### 1.2 现有表修改

| 表名 | 修改类型 | 具体内容 |
| --- | --- | --- |
| `student_profiles` | 新增字段 | `live_city_id`, `desire_jd_salary_id` |
| `job_descriptions` | 新增字段 | `jd_sub_type`, `require_nums`, `is_travel`, `max_edu_level`, `resume_language_required` |
| `college_employment` | 字段类型修改 | `employment_rate`, `further_study_rate`, `overseas_rate` 从 TEXT 改为 REAL |

### 1.3 新增索引

| 表名                 | 索引字段                           | 类型       |
| -------------------- | ---------------------------------- | ---------- |
| `student_profiles`   | `(college, graduation_year)`       | 复合索引   |
| `student_profiles`   | `employment_status`                | 单字段索引 |
| `student_profiles`   | `major`                            | 单字段索引 |
| `job_descriptions`   | `(company_id, status)`             | 复合索引   |
| `job_descriptions`   | `(industry, city)`                 | 复合索引   |
| `job_applications`   | `(account_id, status)`             | 复合索引   |
| `job_applications`   | `job_id`                           | 单字段索引 |
| `college_employment` | `(university_id, graduation_year)` | 复合索引   |

### 1.4 风险与缓解

| 风险             | 影响                 | 缓解措施               |
| ---------------- | -------------------- | ---------------------- |
| ALTER TABLE 锁定 | 大表修改可能阻塞写入 | 在低峰期执行，使用事务 |
| 外键约束冲突     | 现有数据不满足外键   | 先清理脏数据再添加约束 |

---

## Phase 2: 数据清洗函数开发

**执行角色**: tdd-guide + refactor-cleaner **依赖**: Phase 1 完成 **工作量**: 约 8-10 小时

### 2.1 清洗函数清单

#### 通用清洗

| 函数名                | 功能           | 输入示例               | 输出示例      |
| --------------------- | -------------- | ---------------------- | ------------- |
| `strip_whitespace`    | 去除前后空白   | `"  北京  "`           | `"北京"`      |
| `normalize_null`      | 统一 NULL 表示 | `"\N"`, `"null"`, `""` | `NULL`        |
| `clean_special_chars` | 清洗特殊字符   | `"薪资\n要求"`         | `"薪资 要求"` |

#### 日期字段清洗

| 函数名           | 功能                | 输入示例   | 输出示例         |
| ---------------- | ------------------- | ---------- | ---------------- |
| `parse_yyyymmdd` | YYYYMMDD 整数转日期 | `20190325` | `"2019-03-25"`   |
| `validate_date`  | 日期合法性校验      | `20190325` | `True` / `False` |

#### 薪资字段清洗

| 函数名                  | 功能         | 输入示例      | 输出示例 |
| ----------------------- | ------------ | ------------- | -------- |
| `parse_salary`          | 提取数字薪资 | `"8000元/月"` | `8000`   |
| `validate_salary`       | 校验合理范围 | `8000`        | `True`   |
| `clean_negative_salary` | 处理负值     | `-7249`       | `NULL`   |

#### 城市码清洗

| 函数名             | 功能         | 输入示例    | 输出示例 |
| ------------------ | ------------ | ----------- | -------- |
| `parse_city_code`  | 解析城市码   | `"551,-,-"` | `"551"`  |
| `lookup_city_name` | 城市码转名称 | `"551"`     | `"合肥"` |

#### 行业字段清洗

| 函数名               | 功能           | 输入示例                  | 输出示例                  |
| -------------------- | -------------- | ------------------------- | ------------------------- |
| `normalize_industry` | 标准化行业名称 | `"房地产/建筑/建材/工程"` | `"房地产/建筑/建材/工程"` |

#### 学历字段清洗

| 函数名             | 功能       | 输入示例 | 输出示例 |
| ------------------ | ---------- | -------- | -------- |
| `normalize_degree` | 学历数值化 | `"本科"` | `2`      |

#### 技能标签清洗

| 函数名               | 功能          | 输入示例             | 输出示例                   |
| -------------------- | ------------- | -------------------- | -------------------------- |
| `split_skills`       | pipe 分隔拆分 | `"停车\|现场\|凤凰"` | `["停车", "现场", "凤凰"]` |
| `deduplicate_skills` | 去重合并      | `["A", "B", "A"]`    | `["A", "B"]`               |

### 2.2 异常值处理规则

| 字段            | 异常条件                 | 处理方式    |
| --------------- | ------------------------ | ----------- |
| `min_years`     | > 50                     | 设为 `NULL` |
| `salary`        | 负值                     | 设为 `NULL` |
| `salary`        | > 1,000,000              | 设为 `NULL` |
| `birthday`      | < 15 或 > 100            | 设为 `NULL` |
| `min_edu_level` | `\N`                     | 设为 `NULL` |
| `start_date`    | < 19900101 或 > 20301231 | 设为 `NULL` |

### 2.3 风险与缓解

| 风险 | 影响 | 缓解措施 |
| --- | --- | --- |
| 薪资码解码规则不明 | `desire_jd_salary_id` 无法解码 | 标记为 TBD，先跳过该字段 |
| 编码问题导致中文乱码 | 大学生就业选择.csv 无法解析 | 尝试多种编码(GB2312/GBK/UTF-8)，失败则标记 |
| `min_years` 异常值 | 值如 510 无法确认含义 | 设为 `NULL`，日志记录 |

---

## Phase 3: 数据导入

**执行角色**: build-error-resolver **依赖**: Phase 2 完成 **工作量**: 约 12-16 小时（含大数据量处理）

### 3.1 导入顺序

```
1. city_mapping          (无依赖)
2. industry_mapping     (无依赖)
3. universities         (无依赖)
4. companies            (无依赖)
5. student_profiles      (依赖 accounts)
6. job_descriptions      (依赖 companies)
7. user_skills           (依赖 student_profiles)
8. user_job_preference   (依赖 student_profiles)
9. user_job_satisfaction (依赖 student_profiles, job_descriptions)
10. user_job_exposure    (依赖 student_profiles, job_descriptions)
11. job_applications     (依赖 student_profiles, job_descriptions)
12. college_employment   (依赖 universities)
```

### 3.2 数据源到目标表映射

| 优先级 | 源文件 | 目标表 | 数据量 | 清洗复杂度 |
| --- | --- | --- | --- | --- |
| P0 | `train_data/table2_jd_part*.csv` | `job_descriptions` | ~540K 行 | 中 |
| P0 | `train_data/table1_user.csv` | `student_profiles` | ~4.5K 行 | 低 |
| P0 | `train_data/table3_action.csv` | `job_applications` | ~700K 行 | 低 |
| P1 | `zhaopin_round1_test_20190716/user_ToBePredicted.csv` | `student_profiles` | ~2K 行 | 低 |
| P1 | `zhaopin_round1_test_20190716/zhaopin_round1_user_exposure_*.csv` | `user_job_exposure` | ~40K 行 | 低 |
| P2 | `大学生就业选择*.csv` | 新建临时表 | ~20K 行 | 高（编码问题） |
| P3 | `学校数据/*.xlsx` | `college_employment` | ~8 文件 | 中 |

### 3.3 大数据量处理策略

| 问题                            | 解决方案                            |
| ------------------------------- | ----------------------------------- |
| table2_jd_part\*.csv 约 540K 行 | 分批导入，每批 10K 行，事务隔离     |
| table3_action.csv 约 700K 行    | 分批导入，每批 10K 行               |
| 内存占用过高                    | 使用 pandas chunk 或 csv.DictReader |

### 3.4 去重策略

| 数据源               | 去重字段           | 策略                          |
| -------------------- | ------------------ | ----------------------------- |
| table2_jd_part\*.csv | `jd_no`            | 根据 `jd_no` 去重，保留第一条 |
| table3_action.csv    | `(user_id, jd_no)` | 全量导入，不去重              |
| 大学生就业选择\*.csv | `ID`               | 根据 ID 去重                  |

### 3.5 风险与缓解

| 风险                   | 影响                      | 缓解措施                         |
| ---------------------- | ------------------------- | -------------------------------- |
| 540K 职位数据导入超时  | SQLite 写入慢             | 分批事务，每 10K 行提交一次      |
| 职位数据重复           | 同一 jd_no 出现多次       | 导入前去重，以 `jd_no` 为主键    |
| user_id 无对应 account | job_applications 插入失败 | 先建立 user_id → account_id 映射 |
| XLSX 文件格式不一致    | 导入失败                  | 先解析表头校验字段               |

---

## Phase 4: 测试

**执行角色**: tdd-guide **依赖**: Phase 2 完成（清洗函数就绪） **工作量**: 约 6-8 小时

### 4.1 单元测试（清洗函数）

| 测试项   | 覆盖函数                                                    |
| -------- | ----------------------------------------------------------- |
| 通用清洗 | `strip_whitespace`, `normalize_null`, `clean_special_chars` |
| 日期解析 | `parse_yyyymmdd`, `validate_date`                           |
| 薪资处理 | `parse_salary`, `validate_salary`, `clean_negative_salary`  |
| 城市码   | `parse_city_code`, `lookup_city_name`                       |
| 学历映射 | `normalize_degree`                                          |
| 技能拆分 | `split_skills`, `deduplicate_skills`                        |

### 4.2 集成测试（导入流程）

| 测试项     | 验证内容                   |
| ---------- | -------------------------- |
| 外键约束   | 违反外键时插入失败         |
| 唯一索引   | 重复数据插入失败           |
| 字段类型   | TEXT/INTEGER/REAL 类型正确 |
| 索引存在性 | 关键字段索引已创建         |

### 4.3 数据验证测试

| 测试项       | SQL 验证                                                   |
| ------------ | ---------------------------------------------------------- |
| 非空约束     | `SELECT COUNT(*) WHERE field IS NULL` = 0                  |
| 薪资合理范围 | `SELECT COUNT(*) WHERE salary < 0 OR salary > 1000000` = 0 |
| 日期格式     | `SELECT * WHERE date NOT LIKE 'YYYY-MM-DD'`                |
| 重复检查     | `SELECT user_id, jd_no, COUNT(*) > 1` = 0                  |

### 4.4 测试覆盖率目标

| 类型     | 目标覆盖率 |
| -------- | ---------- |
| 清洗函数 | 90%+       |
| 导入脚本 | 80%+       |
| 整体     | 85%+       |

---

## Phase 5: 文档更新

**执行角色**: doc-updater **依赖**: Phase 3 & 4 完成 **工作量**: 约 3-4 小时

### 5.1 文档清单

| 文档                      | 内容           | 状态 |
| ------------------------- | -------------- | ---- |
| `docs/data-dictionary.md` | 数据库字段说明 | 新建 |
| `docs/import-log.md`      | 导入执行日志   | 新建 |
| `docs/cleaning-rules.md`  | 清洗规则说明   | 新建 |
| `README.md`               | 数据集说明     | 更新 |

### 5.2 导入日志内容

- 执行时间
- 导入数据量（成功/失败）
- 跳过记录数及原因
- 错误日志及堆栈

---

## 任务分配矩阵

| 任务                          | 执行角色             | 阶段        | 依赖任务   | 状态    |
| ----------------------------- | -------------------- | ----------- | ---------- | ------- |
| Task 1 (planner)              | planner              | -           | -          | ✅ 完成 |
| Task 2 (architect)            | architect            | Phase 1     | Task 1     | 待分配  |
| Task 3 (tdd-guide)            | tdd-guide            | Phase 2 & 4 | Task 2     | 待分配  |
| Task 4 (build-error-resolver) | build-error-resolver | Phase 3     | Task 2 & 3 | 待分配  |
| Task 5 (refactor-cleaner)     | refactor-cleaner     | Phase 2     | Task 3     | 待分配  |
| Task 6 (doc-updater)          | doc-updater          | Phase 5     | Task 4     | 待分配  |

---

## 高风险问题清单（需人工确认）

| # | 问题 | 影响 | 建议 |
| --- | --- | --- | --- |
| 1 | **薪资码解码规则不明** | `desire_jd_salary_id`, `cur_salary_id` 无法解码 | 暂时跳过该字段 |
| 2 | **编码不一致** | 大学生就业选择.csv 系列乱码 | 尝试 GB2312/GBK/UTF-8，失败则报告 |
| 3 | **min_years 异常值** | 值如 510 无法确认单位 | 设为 NULL，日志记录 |
| 4 | **user_id 与 account_id 映射** | 行为数据无法关联账户 | 先查数据库确认映射关系 |

---

## 执行检查点

| 阶段    | 完成标准                       |
| ------- | ------------------------------ |
| Phase 1 | 所有新表创建成功，索引添加完成 |
| Phase 2 | 清洗函数单元测试 90%+ 通过     |
| Phase 3 | 数据导入完成，无外键错误       |
| Phase 4 | 集成测试通过，覆盖率 85%+      |
| Phase 5 | 文档齐全，可重复执行           |

---

**计划结束**
