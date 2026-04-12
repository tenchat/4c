<!-- 学院就业管理页面 -->
<template>
  <div class="page-admin-colleges art-full-height">
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
            <ElButton @click="handleImport" v-ripple>导入数据</ElButton>
          </ElSpace>
        </template>
      </ArtTableHeader>

      <ArtTable
        :loading="loading"
        :data="data"
        :columns="columns"
        :pagination="pagination"
        @pagination:size-change="handleSizeChange"
        @pagination:current-change="handleCurrentChange"
      />

      <!-- 编辑弹窗 -->
      <ElDialog v-model="editDialogVisible" title="编辑学院就业信息" width="500px">
        <ElForm ref="editFormRef" :model="editFormData" :rules="editFormRules" label-width="100px">
          <ElFormItem label="学院名称" prop="name">
            <ElInput v-model="editFormData.name" placeholder="请输入学院名称" />
          </ElFormItem>
          <ElFormItem label="就业率" prop="employmentRate">
            <ElInputNumber
              v-model="editFormData.employmentRate"
              :min="0"
              :max="100"
              :precision="2"
              style="width: 100%"
            />
            <span class="ml-2">%</span>
          </ElFormItem>
          <ElFormItem label="毕业生总数" prop="graduateCount">
            <ElInputNumber
              v-model="editFormData.graduateCount"
              :min="0"
              style="width: 100%"
            />
          </ElFormItem>
          <ElFormItem label="已就业人数" prop="employedCount">
            <ElInputNumber
              v-model="editFormData.employedCount"
              :min="0"
              style="width: 100%"
            />
          </ElFormItem>
          <ElFormItem label="备注" prop="remark">
            <ElInput
              v-model="editFormData.remark"
              type="textarea"
              :rows="3"
              placeholder="请输入备注信息"
            />
          </ElFormItem>
        </ElForm>
        <template #footer>
          <ElButton @click="editDialogVisible = false">取消</ElButton>
          <ElButton type="primary" :loading="editLoading" @click="handleEditSubmit">确定</ElButton>
        </template>
      </ElDialog>
    </ElCard>
  </div>
</template>

<script setup lang="ts">
  import { fetchAdminColleges, updateCollege } from '@/api/admin'
  import { useTable } from '@/hooks/core/useTable'
  import ArtButtonTable from '@/components/core/forms/art-button-table/index.vue'
  import ArtExcelImport from '@/components/core/forms/art-excel-import/index.vue'
  import { ElMessage, ElProgress } from 'element-plus'
  import type { FormInstance, FormRules } from 'element-plus'

  defineOptions({ name: 'AdminColleges' })

  interface CollegeItem {
    id: string
    name: string
    code: string
    employmentRate: number
    graduateCount: number
    employedCount: number
    unemployedCount: number
    remark?: string
    updateTime: string
  }

  const searchForm = ref({
    keyword: undefined
  })

  const editDialogVisible = ref(false)
  const editLoading = ref(false)
  const editFormRef = ref<FormInstance>()
  const currentCollegeId = ref('')

  const editFormData = ref({
    name: '',
    employmentRate: 0,
    graduateCount: 0,
    employedCount: 0,
    remark: ''
  })

  const editFormRules: FormRules = {
    name: [{ required: true, message: '请输入学院名称', trigger: 'blur' }],
    employmentRate: [{ required: true, message: '请输入就业率', trigger: 'blur' }]
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
      apiFn: fetchAdminColleges as any,
      apiParams: {
        current: 1,
        size: 20,
        ...searchForm.value
      },
      columnsFactory: () => [
        { type: 'index', width: 60, label: '序号' },
        { prop: 'name', label: '学院名称', minWidth: 150 },
        { prop: 'code', label: '学院代码', width: 120 },
        {
          prop: 'employmentRate',
          label: '就业率',
          width: 180,
          formatter: (row: CollegeItem) =>
            h('div', { class: 'flex items-center gap-2' }, [
              h(ElProgress, {
                percentage: row.employmentRate,
                width: 60,
                type: 'circle',
                strokeWidth: 6
              }),
              h('span', {}, `${row.employmentRate}%`)
            ])
        },
        { prop: 'graduateCount', label: '毕业生总数', width: 100 },
        { prop: 'employedCount', label: '已就业人数', width: 100 },
        { prop: 'unemployedCount', label: '未就业人数', width: 100 },
        { prop: 'updateTime', label: '更新时间', width: 180 },
        {
          prop: 'operation',
          label: '操作',
          width: 120,
          fixed: 'right',
          formatter: (row: CollegeItem) =>
            h('div', [
              h(ArtButtonTable, {
                type: 'edit',
                onClick: () => handleEdit(row)
              })
            ])
        }
      ]
    }
  })

  const searchItems = computed(() => [
    {
      key: 'keyword',
      label: '关键词',
      type: 'input' as const,
      props: { placeholder: '学院名称/代码', clearable: true }
    }
  ])

  const handleSearch = (params: Record<string, unknown>) => {
    replaceSearchParams(params)
    getData()
  }

  const handleReset = () => {
    resetSearchParams()
  }

  const handleImport = () => {
    ElMessage.info('导入功能开发中')
  }

  const handleEdit = (row: CollegeItem) => {
    currentCollegeId.value = row.id
    editFormData.value = {
      name: row.name,
      employmentRate: row.employmentRate,
      graduateCount: row.graduateCount,
      employedCount: row.employedCount,
      remark: row.remark || ''
    }
    editDialogVisible.value = true
  }

  const handleEditSubmit = async () => {
    try {
      await editFormRef.value?.validate()
      editLoading.value = true
      const res: any = await updateCollege(currentCollegeId.value, editFormData.value)
      if (res.code === 200) {
        ElMessage.success('保存成功')
        editDialogVisible.value = false
        refreshData()
      } else {
        ElMessage.error(res.message || '保存失败')
      }
    } catch (error) {
      console.error('保存失败:', error)
    } finally {
      editLoading.value = false
    }
  }
</script>

<style scoped>
  .page-admin-colleges {
    padding: 20px;
  }
</style>
