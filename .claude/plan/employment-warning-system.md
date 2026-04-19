# Implementation Plan: Employment Warning System (就业预警系统)

## Task Type
- [x] Frontend (Vue3 + TypeScript)
- [x] Backend (Python FastAPI + SQLite)

## Technical Solution

基于学生档案数据，设计一个**多维度就业预警评分系统**，触发条件的学生可在列表中查询，并可查看学生完整档案。

### 预警评分体系

| 预警级别 | 分数范围 | 触发条件（满足任一即触发） |
|---------|---------|--------------------------|
| 🔴 红色预警 | score ≥ 70 | 待就业超过6个月 / 档案完整度<30% / 薪资低于期望50% |
| 🟡 黄色预警 | 40 ≤ score < 70 | 待就业3-6个月 / 档案完整度30-60% / 无实习经历 / 技能为空 |
| 🟢 绿色提醒 | 20 ≤ score < 40 | 待就业1-3个月 / 档案完整度60-80% |
| ✅ 无预警 | score < 20 | 已就业 / 升学 / 出国 |

### 预警类型 (warning_type)

```python
WARNING_TYPES = {
    "unemployed_long_term": "长期未就业",      # 待就业>=6个月
    "profile_incomplete": "档案不完整",         # profile_complete < 60%
    "salary_mismatch": "薪资偏低",              # cur_salary < desire_salary_min * 0.5
    "no_internship": "无实习经验",              # internship 为空
    "no_skills": "技能特长缺失",               # skills 为空或 []
}
```

> ⚠️ **注意**: `high_expectation` 类型暂不实现（需要市场薪资数据支撑），如有需要后续迭代。

### 预警生成触发时机

| 触发方式 | 说明 | 适用场景 |
|---------|------|---------|
| **手动触发** | 学校管理员点击"生成预警"按钮 | 初始导入、季度审查 |
| **定时任务** | 每日凌晨跑批（可选） | 持续追踪 |

> ⚠️ **数据新鲜度**：预警列表展示的是**快照数据**（warnings 表存储历史记录），不是实时计算结果。用户处理预警后生成新记录，不会删除历史。

### Step 1: Create WarningEngine Service (Backend)

**File**: `backend/app/services/warning_engine.py`

```python
# 市场平均薪资（单位：元/月）- 后续应从数据库或配置表读取
DEFAULT_MARKET_AVG_SALARY = 8000

# 主要功能：
1. calculate_warning_score(student: StudentProfile) -> int
   - 根据多维度计算预警分数

2. generate_warnings_for_university(university_id: str, graduation_year: int)
   - 批量为该校学生生成预警

3. generate_single_student_warning(profile_id: str, university_id: str)
   - 为单个学生生成预警

4. get_warning_level(score: int) -> int
   - 根据分数返回级别 1=红 2=黄 3=绿
```

**评分算法**：
```python
def calculate_warning_score(student: StudentProfile) -> int:
    # ✅ 已就业/升学/出国 -> 第一行就返回，不过任何维度
    if student.employment_status in [1, 2, 3]:
        return 0

    score = 0

    # 1. 待就业时长（基础分 0-40）
    months_unemployed = calculate_months_unemployed(student)
    if student.employment_status == 0:  # 待就业
        if months_unemployed >= 6: score += 40
        elif months_unemployed >= 3: score += 25
        elif months_unemployed >= 1: score += 10

    # 2. 档案完整度（0-30）
    profile_complete = student.profile_complete or 0
    if profile_complete < 30: score += 30
    elif profile_complete < 60: score += 15
    elif profile_complete < 80: score += 5

    # 3. 薪资匹配度（0-20）
    if student.cur_salary and student.desire_salary_min:
        if student.cur_salary < student.desire_salary_min * 0.5: score += 20
        elif student.cur_salary < student.desire_salary_min * 0.8: score += 10

    # 4. 实习经历（0-10）
    if not student.internship: score += 10

    # 5. 技能特长（0-10）
    skills = student.skills or []
    if not skills or len(skills) == 0: score += 10

    return min(score, 100)  # 上限100分
```

> ⚠️ `profile_complete` 字段由前端学生档案页提交，存储在 `student_profiles.profile_complete`（0-100整数），预警依赖此字段的准确性。

### Step 2: Update SchoolService (Backend)

**File**: `backend/app/services/school_service.py`

新增方法：
```python
async def get_warnings_with_student_info(self, university_id: str, filters: dict) -> dict:
    """获取预警列表，关联学生信息用于显示"""
    # 返回字段增加：student_no, college, major, real_name
```

### Step 3: Update API Endpoint (Backend)

**File**: `backend/app/api/v1/school.py`

修改 `GET /warnings` 返回字段，增加学生信息：
```python
{
    "warning_id": "...",
    "account_id": "...",
    "student_no": "2021001234",      # 新增
    "student_name": "张三",           # 新增
    "college": "计算机学院",          # 新增
    "major": "软件工程",              # 新增
    "warning_type": "unemployed_long_term",
    "level": 1,
    "ai_suggestion": "...",
    "handled": False,
    "created_at": "2026-04-01"
}
```

### Step 4: Add View Student Profile Button (Frontend)

**File**: `src/views/school/warnings/index.vue`

修改操作列，增加"查看档案"按钮：
```vue
{
  prop: 'operation',
  label: '操作',
  width: 240,
  fixed: 'right',
  formatter: (row: WarningItem) =>
    h('div', [
      h(ArtButtonTable, {
        icon: 'ri:robot-line',
        iconColor: '#909399',
        buttonBgColor: '#f4f4f5',
        title: 'AI辅导',
        onClick: () => showAdvice(row)
      }),
      h(ArtButtonTable, {
        type: 'view',
        title: '查看档案',
        onClick: () => handleViewProfile(row)
      }),
      h(ArtButtonTable, {
        type: 'edit',
        title: '处理',
        disabled: row.handled,
        onClick: () => handleSingle(row)
      })
    ])
}
```

### Step 5: Extract Student Profile Dialog Component (Frontend)

**New File**: `src/components/school/student-profile-dialog/index.vue`

将 `students/index.vue` 的学生详情弹窗抽成独立组件：
```vue
<template>
  <ElDialog v-model="visible" title="学生档案详情" width="700px" @close="handleClose">
    <!-- 从 students/index.vue 迁移完整布局和样式 -->
  </ElDialog>
</template>

<script setup lang="ts">
  const visible = defineModel<boolean>('modelValue')
  const props = defineProps<{ profileId?: string }>()

  // 内部逻辑复用 students/index.vue 的 handleView
</script>
```

**Updated Files**:
- `src/views/school/students/index.vue` - 替换为使用 `<StudentProfileDialog v-model="showDetailDialog" :profile-id="currentProfileId" />`
- `src/views/school/warnings/index.vue` - 替换为使用同一组件

### Step 6: Update Search/Filter (Frontend)

**File**: `src/views/school/warnings/index.vue`

搜索条件：
```typescript
const searchItems = computed(() => [
  {
    key: 'level',
    label: '预警级别',
    type: 'select' as const,
    props: {
      options: [
        { label: '红色预警', value: 1 },
        { label: '黄色预警', value: 2 },
        { label: '绿色提醒', value: 3 }
      ],
      clearable: true
    }
  },
  {
    key: 'handled',
    label: '处理状态',
    type: 'select' as const,
    props: {
      options: [
        { label: '待处理', value: false },
        { label: '已处理', value: true }
      ],
      clearable: true
    }
  },
  {
    key: 'warning_type',
    label: '预警类型',
    type: 'select' as const,
    props: {
      options: Object.entries(WARNING_TYPE_MAP).map(([value, text]) => ({ label: text, value })),
      clearable: true
    }
  }
])
```

### Step 7: Update Table Columns (Frontend)

**File**: `src/views/school/warnings/index.vue`

显示列：
```typescript
columnsFactory: () => [
  { type: 'selection', width: 60 },
  { type: 'index', width: 60, label: '序号' },
  { prop: 'student_no', label: '学号', width: 140 },
  { prop: 'student_name', label: '姓名', width: 100 },
  { prop: 'college', label: '学院', minWidth: 150 },
  { prop: 'major', label: '专业', minWidth: 150 },
  {
    prop: 'warning_type',
    label: '预警类型',
    width: 120,
    formatter: (row: WarningItem) => WARNING_TYPE_MAP[row.warning_type] || row.warning_type
  },
  // ... level, handled, created_at, operation
]
```

---

## Key Files

| File | Operation | Description |
|------|-----------|-------------|
| `backend/app/services/warning_engine.py` | Create | 预警评分引擎 |
| `backend/app/services/school_service.py` | Modify | 增加预警关联学生信息查询 |
| `backend/app/api/v1/school.py` | Modify | 更新GET /warnings 返回字段 |
| `src/components/school/student-profile-dialog/index.vue` | Create | 抽取学生详情弹窗为公共组件 |
| `src/views/school/students/index.vue` | Modify | 使用 StudentProfileDialog 组件 |
| `src/views/school/warnings/index.vue` | Rewrite | 重写预警页面UI，使用 StudentProfileDialog |
| `src/api/school.ts` | Modify | 增加generateWarnings API |

---

## Risks and Mitigation

| Risk | Mitigation |
|------|------------|
| 预警评分 early return 位置错误 | ✅ 已修复：已就业判断移至函数第一行 |
| high_expectation 悬空定义 | ✅ 已移除：暂不实现该类型 |
| 市场平均薪资来源不明 | ✅ 已明确：暂用固定值 8000（后续迭代） |
| 预警触发时机未设计 | ✅ 已补充：手动触发 + 定时任务可选 |
| profile_complete 来源不透明 | ✅ 已说明：前端提交存储，依赖数据质量 |
| 学生详情弹窗重复代码 | ✅ 已修复：抽取为 StudentProfileDialog 组件 |
| 大数据量下生成预警慢 | 使用async generator分批处理 |

---

## Summary

1. **后端**：创建 `warning_engine.py` 实现评分算法，**已修复 early return 位置**，更新 API 返回学生信息
2. **前端**：重写 `warnings/index.vue`，抽取 `StudentProfileDialog` 组件复用，增加"查看档案"按钮
3. **评分维度**：待就业时长、档案完整度、薪资匹配、实习经历、技能特长
4. **触发时机**：手动触发 + 定时任务可选，数据为快照存储
5. **已知限制**：`high_expectation` 类型暂不实现，`profile_complete` 依赖前端提交质量
