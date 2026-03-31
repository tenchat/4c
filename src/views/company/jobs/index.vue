<!-- 企业岗位管理页面 -->
<template>
  <div class="page-company-jobs art-full-height">
    <ElCard class="art-card-xs">
      <div class="filter-bar flex items-center gap-4">
        <ElRadioGroup v-model="statusFilter" @change="(val: any) => handleStatusChange(val)">
          <ElRadioButton :value="undefined">全部</ElRadioButton>
          <ElRadioButton :value="1">招聘中</ElRadioButton>
          <ElRadioButton :value="0">已暂停</ElRadioButton>
          <ElRadioButton :value="2">已结束</ElRadioButton>
        </ElRadioGroup>
        <ElButton type="primary" @click="$router.push('/company/post-job')" v-ripple>
          发布新岗位
        </ElButton>
      </div>
    </ElCard>

    <ElCard class="art-table-card mt-4">
      <div class="flex justify-between items-center mb-3">
        <ElSpace v-if="batchMode">
          <ElButton @click="batchMode = false">取消批量</ElButton>
          <ElButton type="danger" @click="handleBatchDelete" :disabled="selectedRows.length === 0">
            批量删除 ({{ selectedRows.length }})
          </ElButton>
          <ElButton
            v-if="statusFilter !== 0 && statusFilter !== 2"
            type="warning"
            @click="handleBatchToggle(0)"
            :disabled="selectedRows.length === 0"
          >
            批量下架 ({{ selectedRows.length }})
          </ElButton>
          <ElButton
            v-if="statusFilter !== 1 && statusFilter !== 2"
            type="success"
            @click="handleBatchToggle(1)"
            :disabled="selectedRows.length === 0"
          >
            批量上架 ({{ selectedRows.length }})
          </ElButton>
        </ElSpace>
        <div v-else class="flex-1" />
        <ElButton v-if="!batchMode" @click="batchMode = true">批量操作</ElButton>
      </div>

      <ArtTable
        :loading="loading"
        :data="data"
        :columns="columns"
        :pagination="pagination"
        @selection-change="handleSelectionChange"
        @pagination:size-change="handleSizeChange"
        @pagination:current-change="handleCurrentChange"
      />

      <div class="mt-4 text-right">
        <ElSpace>
          <ElButton @click="refreshData">刷新</ElButton>
          <ElButton type="primary" @click="$router.push('/company/post-job')">发布新岗位</ElButton>
        </ElSpace>
      </div>
    </ElCard>
  </div>
</template>

<script setup lang="ts">
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

  const statusFilter = ref<number | undefined>(undefined)
  const batchMode = ref(false)
  const selectedRows = ref<JobItem[]>([])

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

  const {
    columns,
    data,
    loading,
    pagination,
    getData,
    handleSizeChange,
    handleCurrentChange,
    refreshData,
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

  const handleStatusChange = (status: number | undefined) => {
    batchMode.value = false
    selectedRows.value = []
    getData({ status })
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
      refreshData()
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
      refreshData()
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
      refreshData()
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
      refreshData()
    } catch (error) {
      if (error !== 'cancel') {
        console.error(`批量${actionText}失败:`, error)
      }
    }
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
    getData({ status: statusFilter.value })
  })
</script>

<style scoped>
  .page-company-jobs {
    padding: 20px;
  }

  .filter-bar {
    padding: 10px 0;
  }
</style>
