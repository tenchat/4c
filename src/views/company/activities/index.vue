<!-- 企业活动管理页面 -->
<template>
  <div class="page-company-activities flex flex-col gap-4 pb-5 art-full-height">
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
          <h4 class="m-0">活动数据表格</h4>
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
            <ElButton type="primary" @click="handleAdd" v-ripple>
              <ElIcon><Plus /></ElIcon>新增活动
            </ElButton>

            <!-- 导出导入功能 -->
            <ArtExcelExport
              :data="exportData"
              :columns="exportColumns"
              filename="活动数据全部"
              :auto-index="true"
              button-text="全部导出"
              @export-success="handleExportSuccess"
            />
            <ArtExcelExport
              v-if="selectedRows.length > 0"
              :data="exportSelectedData"
              :columns="exportColumns"
              filename="活动数据选中"
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
                type="success"
                @click="handleBatchStart"
                :disabled="selectedRows.length === 0"
              >
                批量开始 ({{ selectedRows.length }})
              </ElButton>
              <ElButton
                type="warning"
                @click="handleBatchCancel"
                :disabled="selectedRows.length === 0"
              >
                批量取消 ({{ selectedRows.length }})
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

    <!-- 弹窗表单 -->
    <ElDialog v-model="dialogVisible" :title="dialogTitle" width="600px" destroy-on-close>
      <ElForm :model="formData" label-width="100px">
        <ElFormItem label="活动标题" required>
          <ElInput
            v-model="formData.title"
            placeholder="请输入活动标题"
            maxlength="200"
            show-word-limit
          />
        </ElFormItem>
        <ElFormItem label="活动类型" required>
          <ElRadioGroup v-model="formData.type">
            <ElRadio value="seminar">宣讲会</ElRadio>
            <ElRadio value="job_fair">招聘会</ElRadio>
            <ElRadio value="other">其他</ElRadio>
          </ElRadioGroup>
        </ElFormItem>
        <ElFormItem v-if="formData.type === 'other'" label="活动类型" required>
          <ElInput
            v-model="formData.type_name"
            placeholder="请输入自定义活动类型名称"
            maxlength="50"
            show-word-limit
          />
        </ElFormItem>
        <ElFormItem label="活动地点">
          <ElInput v-model="formData.location" placeholder="线下填写地址，线上填写平台名称" />
        </ElFormItem>
        <ElFormItem label="活动日期" required>
          <ElDatePicker
            v-model="formData.activity_date"
            type="date"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </ElFormItem>
        <ElFormItem label="开始时间">
          <ElTimePicker
            v-model="formData.start_time"
            format="HH:mm"
            value-format="HH:mm"
            style="width: 100%"
          />
        </ElFormItem>
        <ElFormItem label="结束时间">
          <ElTimePicker
            v-model="formData.end_time"
            format="HH:mm"
            value-format="HH:mm"
            style="width: 100%"
          />
        </ElFormItem>
        <ElFormItem label="预计人数">
          <ElInputNumber v-model="formData.expected_num" :min="1" style="width: 100%" />
        </ElFormItem>
        <ElFormItem label="活动描述">
          <ElInput
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入活动描述..."
          />
        </ElFormItem>
      </ElForm>
      <template #footer>
        <ElButton @click="dialogVisible = false">取消</ElButton>
        <ElButton type="primary" @click="handleSubmit">确定</ElButton>
      </template>
    </ElDialog>
  </div>
</template>

<script setup lang="ts">
  import { Plus } from '@element-plus/icons-vue'
  import {
    getActivities,
    createActivity,
    updateActivity,
    deleteActivity,
    toggleActivityStatus
  } from '@/api/company_activity'
  import { useTable } from '@/hooks/core/useTable'
  import ArtButtonTable from '@/components/core/forms/art-button-table/index.vue'
  import { ElTag, ElMessage, ElMessageBox } from 'element-plus'

  defineOptions({ name: 'CompanyActivities' })

  interface ActivityItem {
    activity_id: string
    company_id: string
    type: 'seminar' | 'job_fair' | 'other'
    type_name?: string
    title: string
    location?: string
    activity_date: string
    start_time?: string
    end_time?: string
    description?: string
    status: number
    expected_num?: number
    actual_num?: number
    created_at: string
  }

  // 搜索表单 ref
  const searchBarRef = ref()

  // 搜索表单状态
  const searchFormState = ref({
    title: '',
    type: '' as '' | 'seminar' | 'job_fair' | 'other',
    location: '',
    activity_date: '',
    start_time: '',
    end_time: '',
    min_expected_num: undefined as number | undefined,
    max_expected_num: undefined as number | undefined,
    description: ''
  })

  // 搜索表单配置
  const searchItems = computed(() => [
    {
      key: 'title',
      label: '活动标题',
      type: 'input',
      props: {
        placeholder: '请输入活动标题'
      }
    },
    {
      key: 'type',
      label: '活动类型',
      type: 'select',
      options: [
        { label: '全部', value: '' },
        { label: '宣讲会', value: 'seminar' },
        { label: '招聘会', value: 'job_fair' },
        { label: '其他', value: 'other' }
      ]
    },
    {
      key: 'location',
      label: '活动地点',
      type: 'input',
      props: {
        placeholder: '请输入活动地点'
      }
    },
    {
      key: 'activity_date',
      label: '活动日期',
      type: 'date',
      props: {
        type: 'date',
        placeholder: '请选择活动日期',
        valueFormat: 'YYYY-MM-DD'
      }
    },
    {
      key: 'min_expected_num',
      label: '最低人数',
      type: 'inputNumber',
      props: {
        placeholder: '请输入最低人数',
        min: 1
      }
    },
    {
      key: 'max_expected_num',
      label: '最大人数',
      type: 'inputNumber',
      props: {
        placeholder: '请输入最大人数',
        min: 1
      }
    }
  ])

  // 导出列配置 - 全部中文
  const exportColumns = computed(() => ({
    序号: { title: '序号', width: 8 },
    活动ID: { title: '活动ID', width: 36 },
    企业ID: { title: '企业ID', width: 36 },
    活动类型: {
      title: '活动类型',
      width: 10,
      formatter: (val: unknown) => TYPE_MAP[val as string] || String(val)
    },
    类型名称: { title: '类型名称', width: 15 },
    活动标题: { title: '活动标题', width: 20 },
    活动地点: { title: '活动地点', width: 15 },
    活动日期: { title: '活动日期', width: 12 },
    开始时间: { title: '开始时间', width: 10 },
    结束时间: { title: '结束时间', width: 10 },
    预计人数: { title: '预计人数', width: 10 },
    实际人数: { title: '实际人数', width: 10 },
    描述: { title: '描述', width: 20 },
    状态: {
      title: '状态',
      width: 10,
      formatter: (val: unknown) => STATUS_MAP[val as number]?.text || '未知'
    },
    创建时间: { title: '创建时间', width: 20 }
  }))

  // 导出数据格式化
  const getExportRow = (item: ActivityItem) => ({
    活动ID: item.activity_id,
    企业ID: item.company_id,
    活动类型: item.type,
    类型名称: item.type_name || '',
    活动标题: item.title,
    活动地点: item.location || '',
    活动日期: item.activity_date,
    开始时间: item.start_time || '',
    结束时间: item.end_time || '',
    预计人数: item.expected_num || '',
    实际人数: item.actual_num || '',
    描述: item.description || '',
    状态: item.status,
    创建时间: item.created_at
  })

  // 全部导出数据
  const exportData = computed(() => data.value.map(getExportRow))

  // 选中导出数据
  const exportSelectedData = computed(() => selectedRows.value.map(getExportRow))

  const STATUS_MAP: Record<number, { type: string; text: string }> = {
    1: { type: 'success', text: '进行中' },
    0: { type: 'danger', text: '已取消' },
    2: { type: 'info', text: '已结束' }
  }

  const TYPE_MAP: Record<string, string> = {
    seminar: '宣讲会',
    job_fair: '招聘会',
    other: '其他'
  }

  const batchMode = ref(false)
  const selectedRows = ref<ActivityItem[]>([])

  const dialogVisible = ref(false)
  const dialogTitle = ref('新增活动')
  const isEdit = ref(false)
  const currentId = ref('')

  const formData = ref({
    type: 'seminar' as 'seminar' | 'job_fair' | 'other',
    type_name: '',
    title: '',
    activity_date: '',
    location: '',
    start_time: '',
    end_time: '',
    description: '',
    expected_num: undefined as number | undefined
  })

  const resetForm = () => {
    formData.value = {
      type: 'seminar',
      type_name: '',
      title: '',
      activity_date: '',
      location: '',
      start_time: '',
      end_time: '',
      description: '',
      expected_num: undefined
    }
  }

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
    refreshCreate,
    addColumn,
    removeColumn
  } = useTable({
    core: {
      apiFn: getActivities as any,
      apiParams: {
        current: 1,
        size: 20
      },
      paginationKey: {
        current: 'page',
        size: 'page_size'
      },
      columnsFactory: () => [
        { type: 'index', width: 60, label: '序号' },
        {
          prop: 'type',
          label: '活动类型',
          width: 100,
          formatter: (row: ActivityItem) => {
            const base = TYPE_MAP[row.type] || row.type
            return row.type === 'other' && row.type_name ? `${base}(${row.type_name})` : base
          }
        },
        { prop: 'title', label: '活动标题', minWidth: 150 },
        { prop: 'location', label: '活动地点', minWidth: 120 },
        { prop: 'activity_date', label: '活动日期', minWidth: 120 },
        { prop: 'start_time', label: '开始时间', minWidth: 100 },
        { prop: 'expected_num', label: '预计人数', minWidth: 100 },
        {
          prop: 'status',
          label: '状态',
          width: 100,
          formatter: (row: ActivityItem) => {
            const config = STATUS_MAP[row.status] || { type: 'info', text: '未知' }
            return h(ElTag, { type: config.type as any }, () => config.text)
          }
        },
        {
          prop: 'operation',
          label: '操作',
          width: 280,
          fixed: 'right',
          formatter: (row: ActivityItem) =>
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
                title: row.status === 1 ? '取消' : row.status === 0 ? '开始' : '结束',
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

  const handleSelectionChange = (selection: ActivityItem[]) => {
    selectedRows.value = selection
  }

  const handleSearch = () => {
    const state = searchFormState.value
    getData({
      title: state.title || undefined,
      type: state.type || undefined,
      location: state.location || undefined,
      activity_date: state.activity_date || undefined,
      min_expected_num: state.min_expected_num || undefined,
      max_expected_num: state.max_expected_num || undefined
    })
  }

  const handleReset = () => {
    searchFormState.value = {
      title: '',
      type: '',
      location: '',
      activity_date: '',
      start_time: '',
      end_time: '',
      min_expected_num: undefined,
      max_expected_num: undefined,
      description: ''
    }
    getData()
  }

  const handleRefresh = () => {
    refreshData()
  }

  const handleEdit = (row: ActivityItem) => {
    isEdit.value = true
    currentId.value = row.activity_id
    dialogTitle.value = '编辑活动'
    formData.value = {
      type: row.type,
      type_name: row.type_name ?? '',
      title: row.title,
      activity_date: row.activity_date,
      location: row.location ?? '',
      start_time: row.start_time ?? '',
      end_time: row.end_time ?? '',
      description: row.description ?? '',
      expected_num: row.expected_num
    }
    dialogVisible.value = true
  }

  const handleAdd = () => {
    isEdit.value = false
    currentId.value = ''
    dialogTitle.value = '新增活动'
    resetForm()
    dialogVisible.value = true
  }

  const handleSubmit = async () => {
    if (!formData.value.title) {
      ElMessage.warning('请填写活动标题')
      return
    }
    if (!formData.value.activity_date) {
      ElMessage.warning('请选择活动日期')
      return
    }
    try {
      if (isEdit.value) {
        await updateActivity(currentId.value, formData.value)
        ElMessage.success('更新成功')
        refreshUpdate()
      } else {
        await createActivity(formData.value)
        ElMessage.success('创建成功')
        refreshCreate()
      }
      dialogVisible.value = false
    } catch {
      // Error already shown by http interceptor
    }
  }

  const handleToggleStatus = async (row: ActivityItem) => {
    const newStatus = row.status === 1 ? 0 : 1
    const actionText = newStatus === 1 ? '开始' : '取消'
    try {
      await ElMessageBox.confirm(
        `确定要${actionText} "${row.title}" 活动吗？`,
        `${actionText}确认`,
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
      await toggleActivityStatus(row.activity_id, newStatus)
      ElMessage.success(`${actionText}成功`)
      refreshUpdate()
    } catch (error) {
      if (error !== 'cancel') {
        console.error(`${actionText}失败:`, error)
      }
    }
  }

  const handleDelete = async (row: ActivityItem) => {
    if (!row.activity_id) {
      ElMessage.error('活动ID不存在，无法删除')
      return
    }
    try {
      await ElMessageBox.confirm(`确定要删除活动 "${row.title}" 吗？`, '删除确认', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      await deleteActivity(row.activity_id)
      ElMessage.success('删除成功')
      refreshRemove()
    } catch (error) {
      if (error !== 'cancel') {
        console.error('删除失败:', error)
      }
    }
  }

  const handleBatchDelete = async () => {
    if (selectedRows.value.length === 0) return
    try {
      await ElMessageBox.confirm(
        `确定要删除选中的 ${selectedRows.value.length} 个活动吗？`,
        '批量删除',
        { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
      )
      await Promise.all(selectedRows.value.map((row) => deleteActivity(row.activity_id)))
      ElMessage.success(`批量删除 ${selectedRows.value.length} 个活动成功`)
      selectedRows.value = []
      batchMode.value = false
      refreshRemove()
    } catch (error) {
      if (error !== 'cancel') {
        console.error('批量删除失败:', error)
      }
    }
  }

  const handleBatchStart = async () => {
    if (selectedRows.value.length === 0) return
    try {
      await ElMessageBox.confirm(
        `确定要批量开始选中的 ${selectedRows.value.length} 个活动吗？`,
        '批量开始',
        { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
      )
      await Promise.all(selectedRows.value.map((row) => toggleActivityStatus(row.activity_id, 1)))
      ElMessage.success(`批量开始 ${selectedRows.value.length} 个活动成功`)
      selectedRows.value = []
      batchMode.value = false
      refreshUpdate()
    } catch (error) {
      if (error !== 'cancel') {
        console.error('批量开始失败:', error)
      }
    }
  }

  const handleBatchCancel = async () => {
    if (selectedRows.value.length === 0) return
    try {
      await ElMessageBox.confirm(
        `确定要批量取消选中的 ${selectedRows.value.length} 个活动吗？`,
        '批量取消',
        { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
      )
      await Promise.all(selectedRows.value.map((row) => toggleActivityStatus(row.activity_id, 0)))
      ElMessage.success(`批量取消 ${selectedRows.value.length} 个活动成功`)
      selectedRows.value = []
      batchMode.value = false
      refreshUpdate()
    } catch (error) {
      if (error !== 'cancel') {
        console.error('批量取消失败:', error)
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
  .page-company-activities {
    padding: 20px;
  }
</style>
