<!-- 学校端学生管理页面 -->
<template>
  <div class="page-school-students art-full-height">
    <ElCard class="art-card-xs">
      <ArtSearchBar
        v-model="searchForm"
        :items="searchItems"
        :span="6"
        :gutter="12"
        @search="handleSearch"
        @reset="handleReset"
      />
    </ElCard>

    <ElCard class="art-table-card mt-4">
      <ArtTableHeader v-model:columns="columnChecks" :loading="loading" @refresh="refreshData">
        <template #left>
          <ElSpace wrap>
            <ElButton @click="handleExport" v-ripple>导出Excel</ElButton>
          </ElSpace>
        </template>
      </ArtTableHeader>

      <ArtTable
        :loading="loading"
        :data="data"
        :columns="columns"
        :pagination="pagination"
        @selection-change="handleSelectionChange"
        @pagination:size-change="handleSizeChange"
        @pagination:current-change="handleCurrentChange"
      />

      <div class="mt-4">
        <ElButton
          v-if="selectedRows.length > 0"
          type="primary"
          @click="handleBatchExport"
          :loading="exportLoading"
        >
          导出选中学生 ({{ selectedRows.length }})
        </ElButton>
      </div>
    </ElCard>
  </div>
</template>

<script setup lang="ts">
  import { fetchSchoolStudents } from '@/api/school'
  import { useTable } from '@/hooks/core/useTable'
  import ArtButtonTable from '@/components/core/forms/art-button-table/index.vue'
  import { ElTag, ElMessage } from 'element-plus'

  defineOptions({ name: 'SchoolStudents' })

  interface StudentItem {
    profile_id: string
    account_id: string
    student_no: string
    college: string
    major: string
    degree: number
    graduation_year: number
    employment_status: number
    cur_company?: string
    cur_city?: string
  }

  const selectedRows = ref<StudentItem[]>([])
  const exportLoading = ref(false)

  const searchForm = ref({
    college: undefined,
    major: undefined,
    employment_status: undefined,
    graduation_year: undefined,
    keyword: undefined
  })

  const EMPLOYMENT_STATUS_MAP: Record<number, { type: string; text: string }> = {
    0: { type: 'info', text: '待就业' },
    1: { type: 'success', text: '已就业' },
    2: { type: 'warning', text: '升学' },
    3: { type: 'primary', text: '出国' }
  }

  const DEGREE_MAP: Record<number, string> = {
    1: '高中/中专',
    2: '大专',
    3: '本科',
    4: '硕士',
    5: '博士'
  }

  const {
    columns,
    columnChecks,
    data,
    loading,
    pagination,
    getData,
    replaceSearchParams,
    resetSearchParams,
    handleSizeChange,
    handleCurrentChange,
    refreshData
  } = useTable({
    core: {
      apiFn: fetchSchoolStudents as any,
      apiParams: {
        current: 1,
        size: 20,
        ...searchForm.value
      },
      columnsFactory: () => [
        { type: 'selection', width: 60 },
        { type: 'index', width: 60, label: '序号' },
        { prop: 'student_no', label: '学号', width: 140 },
        { prop: 'account_id', label: '账号ID', width: 180, show: false },
        { prop: 'college', label: '学院', minWidth: 150 },
        { prop: 'major', label: '专业', minWidth: 150 },
        {
          prop: 'degree',
          label: '学历',
          width: 80,
          formatter: (row: StudentItem) => DEGREE_MAP[row.degree] || '-'
        },
        { prop: 'graduation_year', label: '毕业年份', width: 100 },
        {
          prop: 'employment_status',
          label: '就业状态',
          width: 100,
          formatter: (row: StudentItem) => {
            const config = EMPLOYMENT_STATUS_MAP[row.employment_status] || { type: 'info', text: '未知' }
            return h(ElTag, { type: config.type as any }, () => config.text)
          }
        },
        { prop: 'cur_company', label: '当前公司', minWidth: 150 },
        { prop: 'cur_city', label: '当前城市', width: 100 },
        {
          prop: 'operation',
          label: '操作',
          width: 120,
          fixed: 'right',
          formatter: (row: StudentItem) =>
            h('div', [
              h(ArtButtonTable, { type: 'view', onClick: () => handleView(row) })
            ])
        }
      ]
    }
  })

  const searchItems = computed(() => [
    {
      key: 'college',
      label: '学院',
      type: 'input' as const,
      props: { placeholder: '请输入学院', clearable: true }
    },
    {
      key: 'major',
      label: '专业',
      type: 'input' as const,
      props: { placeholder: '请输入专业', clearable: true }
    },
    {
      key: 'employment_status',
      label: '就业状态',
      type: 'select' as const,
      props: {
        placeholder: '请选择',
        options: Object.entries(EMPLOYMENT_STATUS_MAP).map(([value, config]) => ({
          label: config.text,
          value: Number(value)
        })),
        clearable: true
      }
    },
    {
      key: 'graduation_year',
      label: '届次',
      type: 'number' as const,
      props: { placeholder: '请输入毕业年份', min: 2000, max: 2100 }
    }
  ])

  const handleSearch = (params: Record<string, unknown>) => {
    replaceSearchParams(params)
    getData()
  }

  const handleReset = () => {
    resetSearchParams()
  }

  const handleSelectionChange = (selection: StudentItem[]) => {
    selectedRows.value = selection
  }

  const handleView = (row: StudentItem) => {
    ElMessage.info(`查看学生档案: ${row.student_no}`)
  }

  const handleExport = async () => {
    ElMessage.info('导出功能开发中')
  }

  const handleBatchExport = async () => {
    if (selectedRows.value.length === 0) {
      ElMessage.warning('请先选择要导出的学生')
      return
    }
    ElMessage.info('导出功能开发中')
  }
</script>

<style scoped>
  .page-school-students {
    padding: 20px;
  }
</style>
