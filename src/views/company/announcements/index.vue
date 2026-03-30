<script setup lang="ts">
  import { ref, computed } from 'vue'
  import { useTable } from '@/hooks/core/useTable'
  import {
    getAnnouncements,
    createAnnouncement,
    updateAnnouncement,
    deleteAnnouncement,
    type Announcement,
    type AnnouncementCreate
  } from '@/api/company_announcement'
  import { ElMessage, ElMessageBox } from 'element-plus'

  defineOptions({ name: 'CompanyAnnouncements' })

  const dialogVisible = ref(false)
  const dialogTitle = ref('新增公告')
  const isEdit = ref(false)
  const currentId = ref('')

  const DEGREE_MAP: Record<number, string> = {
    0: '不限',
    1: '高中/中专',
    2: '大专',
    3: '本科',
    4: '硕士',
    5: '博士'
  }

  const formData = ref<AnnouncementCreate>({
    title: '',
    content: '',
    target_major: '',
    target_degree: undefined,
    headcount: undefined,
    deadline: '',
    status: 1
  })

  const resetForm = () => {
    formData.value = {
      title: '',
      content: '',
      target_major: '',
      target_degree: undefined,
      headcount: undefined,
      deadline: '',
      status: 1
    }
  }

  const { columns, data, loading, pagination, getData, handleSizeChange, handleCurrentChange } =
    useTable({
      core: {
        apiFn: getAnnouncements as any,
        apiParams: computed(() => ({
          page: pagination.page,
          page_size: pagination.pageSize
        })),
        columnsFactory: () => [
          { type: 'index', width: 60, label: '序号' },
          { prop: 'title', label: '公告标题', minWidth: 180 },
          { prop: 'target_major', label: '目标专业', minWidth: 120 },
          {
            prop: 'headcount',
            label: '招聘人数',
            minWidth: 100,
            formatter: (row: Announcement) => row.headcount ?? '-'
          },
          { prop: 'deadline', label: '截止日期', minWidth: 120 },
          {
            prop: 'status',
            label: '状态',
            minWidth: 100,
            formatter: (row: Announcement) => {
              const map: Record<number, string> = { 0: '草稿', 1: '发布中', 2: '已过期' }
              return map[row.status] ?? String(row.status)
            }
          },
          { prop: 'published_at', label: '发布时间', minWidth: 160 },
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

  const handleCommand = async ({ key, row }: { key: string; row: Announcement }) => {
    if (key === 'edit') {
      isEdit.value = true
      currentId.value = row.announcement_id
      dialogTitle.value = '编辑公告'
      formData.value = {
        title: row.title,
        content: row.content,
        target_major: row.target_major ?? '',
        target_degree: row.target_degree,
        headcount: row.headcount,
        deadline: row.deadline ?? '',
        status: row.status
      }
      dialogVisible.value = true
    } else if (key === 'delete') {
      await ElMessageBox.confirm('确定删除该公告吗？', '提示', { type: 'warning' })
      await deleteAnnouncement(row.announcement_id)
      ElMessage.success('删除成功')
      getData()
    }
  }

  const handleAdd = () => {
    isEdit.value = false
    currentId.value = ''
    dialogTitle.value = '新增公告'
    resetForm()
    dialogVisible.value = true
  }

  const handleSubmit = async () => {
    if (!formData.value.title) {
      ElMessage.warning('请填写公告标题')
      return
    }
    if (!formData.value.content) {
      ElMessage.warning('请填写公告内容')
      return
    }
    try {
      if (isEdit.value) {
        await updateAnnouncement(currentId.value, formData.value)
        ElMessage.success('更新成功')
      } else {
        await createAnnouncement(formData.value)
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
  <div class="page-announcements">
    <ElRow justify="end" style="margin-bottom: 12px">
      <ElButton type="primary" @click="handleAdd">新增公告</ElButton>
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
        <ElFormItem label="公告标题" required>
          <ElInput
            v-model="formData.title"
            placeholder="请输入公告标题"
            maxlength="200"
            show-word-limit
          />
        </ElFormItem>
        <ElFormItem label="公告内容" required>
          <ElInput
            v-model="formData.content"
            type="textarea"
            :rows="4"
            placeholder="请输入公告内容..."
          />
        </ElFormItem>
        <ElFormItem label="目标专业">
          <ElInput v-model="formData.target_major" placeholder="多个专业用逗号分隔" />
        </ElFormItem>
        <ElFormItem label="目标学历">
          <ElSelect v-model="formData.target_degree" placeholder="请选择" style="width: 100%">
            <ElOption
              v-for="(label, value) in DEGREE_MAP"
              :key="value"
              :label="label"
              :value="Number(value)"
            />
          </ElSelect>
        </ElFormItem>
        <ElFormItem label="招聘人数">
          <ElInputNumber v-model="formData.headcount" :min="1" style="width: 100%" />
        </ElFormItem>
        <ElFormItem label="截止日期">
          <ElDatePicker
            v-model="formData.deadline"
            type="date"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </ElFormItem>
        <ElFormItem label="状态">
          <ElRadioGroup v-model="formData.status">
            <ElRadio :label="0">草稿</ElRadio>
            <ElRadio :label="1">发布</ElRadio>
          </ElRadioGroup>
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
  .page-announcements {
    padding: 20px;
  }
</style>
