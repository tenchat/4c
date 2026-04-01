<!-- 企业岗位管理页面 -->
<template>
  <div class="page-company-jobs flex flex-col gap-4 pb-5 art-full-height">
    <!-- 搜索区域 -->
    <ArtSearchBar
      ref="searchBarRef"
      v-model="searchFormState"
      :items="searchItems"
      :is-expand="false"
      :show-expand="true"
      :show-reset-button="true"
      :show-search-button="true"
      :disabled-search-button="false"
      @search="handleSearch"
      @reset="handleReset"
    />

    <!-- 表格区域 -->
    <ElCard class="flex-1 art-table-card" style="margin-top: 0">
      <template #header>
        <div class="flex-cb">
          <h4 class="m-0">岗位数据表格</h4>
          <div class="flex gap-2">
            <ElTag v-if="error" type="danger">{{ error.message }}</ElTag>
            <ElTag v-else-if="loading" type="warning">加载中...</ElTag>
            <ElTag v-else type="success">{{ pagination.total }} 条数据</ElTag>
          </div>
        </div>
      </template>

      <!-- 表格工具栏 -->
      <ArtTableHeader
        v-model:columns="columnChecks"
        :loading="loading"
        @refresh="handleRefresh"
        layout="refresh,size,fullscreen,columns,settings"
        fullClass="art-table-card"
      >
        <template #left>
          <ElSpace wrap>
            <ElButton type="primary" @click="$router.push('/company/post-job')" v-ripple>
              <ElIcon><Plus /></ElIcon>发布新岗位
            </ElButton>

            <!-- 导出导入功能 -->
            <ArtExcelExport
              :data="exportData"
              :columns="exportColumns"
              filename="岗位数据全部"
              :auto-index="true"
              button-text="全部导出"
              @export-success="handleExportSuccess"
            />
            <ArtExcelExport
              v-if="selectedRows.length > 0"
              :data="exportSelectedData"
              :columns="exportColumns"
              filename="岗位数据选中"
              :auto-index="true"
              button-text="批量导出"
              @export-success="handleExportSuccess"
            />
            <ArtExcelImport
              @import-success="handleImportSuccess"
              @import-error="handleImportError"
              style="margin: 0 12px"
            />

            <ElButton v-if="!batchMode" @click="batchMode = true">批量操作</ElButton>
            <template v-if="batchMode">
              <ElButton @click="batchMode = false">取消批量</ElButton>
              <ElButton
                type="danger"
                @click="handleBatchDelete"
                :disabled="selectedRows.length === 0"
              >
                批量删除 ({{ selectedRows.length }})
              </ElButton>
              <ElButton
                type="warning"
                @click="handleBatchToggle(0)"
                :disabled="selectedRows.length === 0"
              >
                批量下架 ({{ selectedRows.length }})
              </ElButton>
              <ElButton
                type="success"
                @click="handleBatchToggle(1)"
                :disabled="selectedRows.length === 0"
              >
                批量上架 ({{ selectedRows.length }})
              </ElButton>
            </template>
          </ElSpace>
        </template>
      </ArtTableHeader>

      <ArtTable
        ref="tableRef"
        :loading="loading"
        :data="data"
        :columns="columns"
        :pagination="pagination"
        @selection-change="handleSelectionChange"
        @pagination:size-change="handleSizeChange"
        @pagination:current-change="handleCurrentChange"
      />
    </ElCard>
  </div>
</template>

<script setup lang="ts">
  import { Plus } from '@element-plus/icons-vue'
  import { fetchCompanyJobs, deleteJob, toggleJobStatus } from '@/api/company'
  import { useTable } from '@/hooks/core/useTable'
  import ArtButtonTable from '@/components/core/forms/art-button-table/index.vue'
  import { ElTag, ElMessage, ElMessageBox } from 'element-plus'

  const router = useRouter()

  defineOptions({ name: 'CompanyJobs' })

  interface JobItem {
    job_id: string
    title: string
    city: string
    province: string
    industry: string
    min_salary: number
    max_salary: number
    min_degree: number
    min_exp_years: number
    keywords: string[]
    status: number
    published_at: string
    expired_at: string
  }

  // 搜索表单 ref
  const searchBarRef = ref()

  // 搜索表单状态
  const searchFormState = ref({
    title: '',
    city: '',
    industry: '',
    min_salary: undefined as number | undefined,
    max_salary: undefined as number | undefined,
    status: ''
  })

  // 搜索表单配置
  const searchItems = computed(() => [
    {
      key: 'title',
      label: '岗位名称',
      type: 'input',
      props: {
        placeholder: '请输入岗位名称'
      }
    },
    {
      key: 'city',
      label: '工作城市',
      type: 'input',
      props: {
        placeholder: '请输入工作城市'
      }
    },
    {
      key: 'industry',
      label: '行业',
      type: 'select',
      options: [
        { label: '全部', value: '' },
        { label: '互联网/IT', value: 'internet' },
        { label: '金融', value: 'finance' },
        { label: '教育', value: 'education' },
        { label: '制造业', value: 'manufacturing' },
        { label: '房地产', value: 'real_estate' },
        { label: '医疗健康', value: 'healthcare' },
        { label: '政府/事业单位', value: 'government' },
        { label: '其他', value: 'other' }
      ]
    },
    {
      key: 'status',
      label: '状态',
      type: 'select',
      options: [
        { label: '全部', value: '' },
        { label: '招聘中', value: '1' },
        { label: '已暂停', value: '0' },
        { label: '已结束', value: '2' }
      ]
    }
  ])

  const STATUS_MAP: Record<number, { type: string; text: string }> = {
    1: { type: 'success', text: '招聘中' },
    0: { type: 'warning', text: '已暂停' },
    2: { type: 'info', text: '已结束' }
  }

  const INDUSTRY_MAP: Record<string, string> = {
    internet: '互联网/IT',
    finance: '金融',
    education: '教育',
    manufacturing: '制造业',
    real_estate: '房地产',
    healthcare: '医疗健康',
    government: '政府/事业单位',
    other: '其他'
  }

  // 导出列配置 - 全部中文
  const exportColumns = computed(() => ({
    序号: { title: '序号', width: 8 },
    岗位ID: { title: '岗位ID', width: 36 },
    岗位名称: { title: '岗位名称', width: 20 },
    工作城市: { title: '工作城市', width: 10 },
    省份: { title: '省份', width: 10 },
    行业: {
      title: '行业',
      width: 12,
      formatter: (val: string) => INDUSTRY_MAP[val] || val
    },
    最低薪资: { title: '最低薪资', width: 10 },
    最高薪资: { title: '最高薪资', width: 10 },
    最低学历: { title: '最低学历', width: 10 },
    最低经验: { title: '最低经验(年)', width: 12 },
    关键词: { title: '关键词', width: 20 },
    状态: {
      title: '状态',
      width: 10,
      formatter: (val: number) => STATUS_MAP[val]?.text || '未知'
    },
    发布时间: { title: '发布时间', width: 20 },
    有效期至: { title: '有效期至', width: 20 }
  }))

  // 导出数据格式化
  const getExportRow = (item: JobItem) => ({
    序号: '',
    岗位ID: item.job_id,
    岗位名称: item.title,
    工作城市: item.city,
    省份: item.province,
    行业: item.industry,
    最低薪资: item.min_salary || '',
    最高薪资: item.max_salary || '',
    最低学历: item.min_degree || '',
    最低经验: item.min_exp_years || '',
    关键词: item.keywords?.join(', ') || '',
    状态: item.status,
    发布时间: item.published_at,
    有效期至: item.expired_at
  })

  // 全部导出数据
  const exportData = computed(() => data.value.map(getExportRow))

  // 选中导出数据
  const exportSelectedData = computed(() => selectedRows.value.map(getExportRow))

  const batchMode = ref(false)
  const selectedRows = ref<JobItem[]>([])

  const {
    columns,
    columnChecks,
    data,
    loading,
    error,
    pagination,
    getData,
    handleSizeChange,
    handleCurrentChange,
    refreshData,
    refreshUpdate,
    refreshRemove,
    addColumn,
    removeColumn
  } = useTable({
    core: {
      apiFn: fetchCompanyJobs as any,
      apiParams: {
        current: 1,
        size: 20
      },
      columnsFactory: () => [
        { type: 'index', width: 60, label: '序号' },
        { prop: 'title', label: '岗位名称', minWidth: 150 },
        { prop: 'city', label: '工作城市', width: 100 },
        {
          prop: 'salary',
          label: '薪资范围',
          width: 140,
          formatter: (row: JobItem) => {
            if (!row.min_salary && !row.max_salary) return '面议'
            return `${row.min_salary || 0}-${row.max_salary || 0}元/月`
          }
        },
        {
          prop: 'industry',
          label: '行业',
          width: 100,
          formatter: (row: JobItem) => INDUSTRY_MAP[row.industry] || row.industry || '-'
        },
        {
          prop: 'status',
          label: '状态',
          width: 100,
          formatter: (row: JobItem) => {
            const config = STATUS_MAP[row.status] || { type: 'info', text: '未知' }
            return h(ElTag, { type: config.type as any }, () => config.text)
          }
        },
        { prop: 'published_at', label: '发布时间', width: 180 },
        { prop: 'expired_at', label: '有效期至', width: 180 },
        {
          prop: 'operation',
          label: '操作',
          width: 200,
          fixed: 'right',
          formatter: (row: JobItem) =>
            h('div', { class: 'flex gap-1' }, [
              h(ArtButtonTable, {
                type: 'edit',
                title: '编辑',
                disabled: row.status === 2,
                onClick: () => handleEdit(row)
              }),
              h(ArtButtonTable, {
                type: 'more',
                icon: row.status === 1 ? 'ri:pause-circle-line' : 'ri:play-circle-line',
                iconColor: row.status === 1 ? '#E6A23C' : '#67C23A',
                onClick: () => handleToggleStatus(row)
              }),
              h(ArtButtonTable, {
                type: 'delete',
                title: '删除',
                onClick: () => handleDelete(row)
              })
            ])
        }
      ]
    }
  })

  const handleSelectionChange = (selection: JobItem[]) => {
    selectedRows.value = selection
  }

  const handleSearch = () => {
    const { title, city, industry, status } = searchFormState.value
    getData({
      title: title || undefined,
      city: city || undefined,
      industry: industry || undefined,
      status: status ? Number(status) : undefined
    })
  }

  const handleReset = () => {
    searchFormState.value = {
      title: '',
      city: '',
      industry: '',
      min_salary: undefined,
      max_salary: undefined,
      status: ''
    }
    getData()
  }

  const handleRefresh = () => {
    refreshData()
  }

  const handleEdit = (row: JobItem) => {
    router.push(`/company/post-job?id=${row.job_id}`)
  }

  const handleDelete = async (row: JobItem) => {
    if (!row.job_id) {
      ElMessage.error('岗位ID不存在，无法删除')
      return
    }
    try {
      await ElMessageBox.confirm(`确定要删除岗位 "${row.title}" 吗？`, '删除确认', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      await deleteJob(row.job_id)
      ElMessage.success('删除成功')
      refreshRemove()
    } catch (error) {
      if (error !== 'cancel') {
        console.error('删除失败:', error)
      }
    }
  }

  const handleToggleStatus = async (row: JobItem) => {
    const newStatus = row.status === 1 ? 0 : 1
    const actionText = newStatus === 1 ? '上架' : '下架'
    try {
      await ElMessageBox.confirm(
        `确定要${actionText} "${row.title}" 岗位吗？`,
        `${actionText}确认`,
        { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
      )
      await toggleJobStatus(row.job_id, newStatus)
      ElMessage.success(`${actionText}成功`)
      refreshUpdate()
    } catch (error) {
      if (error !== 'cancel') {
        console.error(`${actionText}失败:`, error)
      }
    }
  }

  const handleBatchDelete = async () => {
    if (selectedRows.value.length === 0) return
    try {
      await ElMessageBox.confirm(
        `确定要删除选中的 ${selectedRows.value.length} 个岗位吗？`,
        '批量删除',
        { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
      )
      await Promise.all(selectedRows.value.map((row) => deleteJob(row.job_id)))
      ElMessage.success(`批量删除 ${selectedRows.value.length} 个岗位成功`)
      selectedRows.value = []
      batchMode.value = false
      refreshRemove()
    } catch (error) {
      if (error !== 'cancel') {
        console.error('批量删除失败:', error)
      }
    }
  }

  const handleBatchToggle = async (newStatus: number) => {
    if (selectedRows.value.length === 0) return
    const actionText = newStatus === 1 ? '上架' : '下架'
    try {
      await ElMessageBox.confirm(
        `确定要批量${actionText}选中的 ${selectedRows.value.length} 个岗位吗？`,
        `批量${actionText}`,
        { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
      )
      await Promise.all(selectedRows.value.map((row) => toggleJobStatus(row.job_id, newStatus)))
      ElMessage.success(`批量${actionText} ${selectedRows.value.length} 个岗位成功`)
      selectedRows.value = []
      batchMode.value = false
      refreshUpdate()
    } catch (error) {
      if (error !== 'cancel') {
        console.error(`批量${actionText}失败:`, error)
      }
    }
  }

  // 导入导出回调
  const handleExportSuccess = (filename: string, count: number) => {
    ElMessage.success(`导出 ${count} 条数据成功`)
  }

  const handleImportSuccess = (data: Record<string, any>[]) => {
    ElMessage.success(`导入 ${data.length} 条数据成功`)
    refreshRemove()
  }

  const handleImportError = (error: Error) => {
    ElMessage.error(`导入失败：${error.message}`)
  }

  // 监听批量模式，动态添加/移除选择列
  watch(
    batchMode,
    (val) => {
      if (val) {
        addColumn?.({ type: 'selection', width: 50 }, 0)
      } else {
        removeColumn?.('__selection__')
        selectedRows.value = []
      }
    },
    { immediate: true }
  )

  onMounted(() => {
    getData()
  })
</script>

<style scoped>
  .page-company-jobs {
    padding: 20px;
  }
</style>
