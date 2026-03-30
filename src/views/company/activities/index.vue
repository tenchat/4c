<!-- src/views/company/activities/index.vue -->
<script setup lang="ts">
  import { ref, computed } from 'vue'
  import { useTable } from '@/hooks/core/useTable'
  import {
    getActivities,
    createActivity,
    updateActivity,
    deleteActivity,
    type Activity,
    type ActivityCreate
  } from '@/api/company_activity'
  import { ElMessage, ElMessageBox } from 'element-plus'

  defineOptions({ name: 'CompanyActivities' })

  const activeTab = ref<'seminar' | 'job_fair'>('seminar')
  const dialogVisible = ref(false)
  const dialogTitle = ref('新增活动')
  const isEdit = ref(false)
  const currentId = ref('')

  const formData = ref<ActivityCreate>({
    type: 'seminar',
    title: '',
    activity_date: '',
    location: '',
    start_time: '',
    end_time: '',
    description: '',
    expected_num: undefined
  })

  const resetForm = () => {
    formData.value = {
      type: activeTab.value,
      title: '',
      activity_date: '',
      location: '',
      start_time: '',
      end_time: '',
      description: '',
      expected_num: undefined
    }
  }

  const { columns, data, loading, pagination, getData, handleSizeChange, handleCurrentChange } =
    useTable({
      core: {
        apiFn: getActivities as any,
        apiParams: computed(() => ({
          type: activeTab.value,
          page: pagination.page,
          page_size: pagination.pageSize
        })),
        columnsFactory: () => [
          { type: 'index', width: 60, label: '序号' },
          { prop: 'title', label: '活动标题', minWidth: 150 },
          { prop: 'location', label: '地点', minWidth: 120 },
          { prop: 'activity_date', label: '活动日期', minWidth: 120 },
          { prop: 'start_time', label: '开始时间', minWidth: 100 },
          { prop: 'expected_num', label: '预计人数', minWidth: 100 },
          {
            prop: 'status',
            label: '状态',
            minWidth: 100,
            formatter: (row: Activity) => {
              const map: Record<number, string> = { 0: '已取消', 1: '进行中', 2: '已结束' }
              return map[row.status] ?? String(row.status)
            }
          },
          {
            label: '操作',
            width: 150,
            formatter: () => [
              { label: '编辑', key: 'edit', type: 'primary' },
              { label: '删除', key: 'delete', type: 'danger' }
            ]
          }
        ]
      }
    })

  const handleTabChange = () => {
    pagination.page = 1
    resetForm()
    getData()
  }

  const handleCommand = async ({ key, row }: { key: string; row: Activity }) => {
    if (key === 'edit') {
      isEdit.value = true
      currentId.value = row.activity_id
      dialogTitle.value = '编辑活动'
      formData.value = {
        type: row.type,
        title: row.title,
        activity_date: row.activity_date,
        location: row.location ?? '',
        start_time: row.start_time ?? '',
        end_time: row.end_time ?? '',
        description: row.description ?? '',
        expected_num: row.expected_num
      }
      dialogVisible.value = true
    } else if (key === 'delete') {
      await ElMessageBox.confirm('确定删除该活动吗？', '提示', { type: 'warning' })
      await deleteActivity(row.activity_id)
      ElMessage.success('删除成功')
      getData()
    }
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
      } else {
        await createActivity(formData.value)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      getData()
    } catch {
      // Error already shown by http interceptor
    }
  }
</script>

<template>
  <div class="page-activities">
    <ElTabs v-model="activeTab" @tab-change="handleTabChange" style="margin-bottom: 16px">
      <ElTabPane label="宣讲会" name="seminar" />
      <ElTabPane label="招聘会" name="job_fair" />
    </ElTabs>

    <ElRow justify="end" style="margin-bottom: 12px">
      <ElButton type="primary" @click="handleAdd">新增活动</ElButton>
    </ElRow>

    <ElTable :data="data" :loading="loading" :columns="columns" @command="handleCommand">
      <template #empty>
        <ElEmpty description="暂无数据" />
      </template>
    </ElTable>

    <ElPagination
      v-model:current-page="pagination.page"
      v-model:page-size="pagination.pageSize"
      :total="pagination.total"
      :page-sizes="[10, 20, 50]"
      layout="total, sizes, prev, pager, next"
      style="justify-content: flex-end; margin-top: 16px"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    />

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
        <ElFormItem label="活动类型">
          <ElTag>{{ activeTab === 'seminar' ? '宣讲会' : '招聘会' }}</ElTag>
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

<style scoped>
  .page-activities {
    padding: 20px;
  }
</style>
