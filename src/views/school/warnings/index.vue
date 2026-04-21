<!-- 就业预警页面 -->
<template>
  <div class="page-school-warnings art-full-height">
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
            <ElButton type="primary" :loading="generating" @click="handleGenerateWarnings" v-ripple>
              生成预警
            </ElButton>
            <ElButton
              type="danger"
              :disabled="selectedRows.length === 0"
              @click="handleBatchHandle"
              v-ripple
            >
              批量处理 ({{ selectedRows.length }})
            </ElButton>
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

      <!-- AI 辅导建议弹窗 -->
      <ElDialog v-model="aiAdviceVisible" title="AI 辅导建议" width="600px">
        <div v-if="currentAdvice" class="ai-advice-content">
          <ElAlert :type="currentAdvice.level" :title="currentAdvice.title" show-icon />
          <div class="mt-4">
            <h4 class="mb-2 font-medium">问题分析：</h4>
            <p class="text-gray-600">{{ currentAdvice.analysis }}</p>
          </div>
          <div class="mt-4">
            <h4 class="mb-2 font-medium">辅导建议：</h4>
            <p class="text-gray-600 whitespace-pre-wrap">{{ currentAdvice.suggestion }}</p>
          </div>
          <div class="mt-4">
            <h4 class="mb-2 font-medium">推荐行动：</h4>
            <ul class="list-disc pl-5 text-gray-600">
              <li v-for="(action, index) in currentAdvice.actions" :key="index">
                {{ action }}
              </li>
            </ul>
          </div>
        </div>
        <template #footer>
          <ElButton @click="aiAdviceVisible = false">关闭</ElButton>
          <ElButton type="primary" @click="handleMarkProcessed">标记已处理</ElButton>
        </template>
      </ElDialog>

      <!-- 预警生成结果弹窗 -->
      <ElDialog v-model="showGenerateResult" title="预警生成结果" width="900px">
        <div v-if="generateResult">
          <ElAlert type="success" :closable="false" class="mb-4">
            共扫描 {{ generateResult.summary?.total_students || 0 }} 名学生，生成预警
            {{ generateResult.summary?.generated || 0 }} 条（红色
            {{ generateResult.summary?.red_warnings || 0 }} / 黄色
            {{ generateResult.summary?.yellow_warnings || 0 }} / 绿色
            {{ generateResult.summary?.green_warnings || 0 }}）
          </ElAlert>

          <ElTable :data="generateResult.warnings?.list || []" stripe max-height="400" size="small">
            <ElTableColumn prop="student_no" label="学号" width="120" />
            <ElTableColumn prop="student_name" label="姓名" width="80" />
            <ElTableColumn prop="college" label="学院" min-width="120" />
            <ElTableColumn prop="major" label="专业" min-width="120" />
            <ElTableColumn prop="warning_type" label="预警类型" width="100">
              <template #default="{ row }">
                {{ WARNING_TYPE_MAP[row.warning_type] || row.warning_type }}
              </template>
            </ElTableColumn>
            <ElTableColumn prop="level" label="级别" width="80">
              <template #default="{ row }">
                <ElTag size="small" :type="(WARNING_LEVEL_MAP[row.level]?.type || 'info') as any">
                  {{ WARNING_LEVEL_MAP[row.level]?.text }}
                </ElTag>
              </template>
            </ElTableColumn>
          </ElTable>

          <div class="flex justify-end mt-4">
            <ElPagination
              v-model:current-page="generatePage"
              v-model:page-size="generatePageSize"
              :total="generateResult.warnings?.total || 0"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next"
              @size-change="handleGenerateResultPageSizeChange"
              @current-change="handleGenerateResultPageChange"
            />
          </div>
        </div>
        <template #footer>
          <ElButton @click="showGenerateResult = false">关闭</ElButton>
        </template>
      </ElDialog>

      <!-- 学生详情弹窗 -->
      <StudentProfileDialog v-model="showProfileDialog" :profile-id="currentProfileId" />
    </ElCard>
  </div>
</template>

<script setup lang="ts">
  import { fetchSchoolWarnings, handleWarning, generateWarnings } from '@/api/school'
  import { useTable } from '@/hooks/core/useTable'
  import ArtButtonTable from '@/components/core/forms/art-button-table/index.vue'
  import StudentProfileDialog from '@/components/school/student-profile-dialog/index.vue'
  import { ElTag, ElMessage, ElMessageBox } from 'element-plus'

  defineOptions({ name: 'SchoolWarnings' })

  interface WarningItem {
    warning_id: string
    profile_id: string
    account_id?: string
    student_no?: string
    student_name?: string
    college?: string
    major?: string
    graduation_year?: number
    employment_status?: number
    cur_company?: string
    cur_city?: string
    desire_city?: string
    profile_complete?: number
    warning_type: string
    level: number
    ai_suggestion?: string
    handled: boolean
    handled_at?: string
    created_at: string
  }

  interface AdviceDetail {
    title: string
    level: 'warning' | 'error' | 'info'
    analysis: string
    suggestion: string
    actions: string[]
  }

  const selectedRows = ref<WarningItem[]>([])
  const aiAdviceVisible = ref(false)
  const currentAdvice = ref<AdviceDetail | null>(null)
  const currentWarningId = ref<string>('')
  const showProfileDialog = ref(false)
  const currentProfileId = ref<string>('')
  const generating = ref(false)
  const showGenerateResult = ref(false)
  const generateResult = ref<any>(null)
  const generatePage = ref(1)
  const generatePageSize = ref(20)

  const searchForm = ref({
    level: undefined as number | undefined,
    handled: undefined as boolean | undefined,
    warning_type: undefined as string | undefined
  })

  const WARNING_LEVEL_MAP: Record<number, { type: string; text: string }> = {
    1: { type: 'danger', text: '红色预警' },
    2: { type: 'warning', text: '黄色预警' },
    3: { type: 'info', text: '绿色提醒' }
  }

  const WARNING_TYPE_MAP: Record<string, string> = {
    unemployed_long_term: '长期未就业',
    profile_incomplete: '档案不完整',
    salary_low: '薪资偏低',
    no_internship: '无实习经验',
    no_skills: '技能特长缺失'
  }

  const EMPLOYMENT_STATUS_MAP: Record<number, string> = {
    0: '待就业',
    1: '已就业',
    2: '升学',
    3: '出国'
  }

  const {
    columns,
    columnChecks,
    data,
    loading,
    pagination,
    fetchData,
    replaceSearchParams,
    resetSearchParams,
    handleSizeChange,
    handleCurrentChange,
    refreshData
  } = useTable({
    core: {
      apiFn: fetchSchoolWarnings as any,
      apiParams: {
        page: 1,
        page_size: 20,
        ...searchForm.value
      },
      paginationKey: {
        current: 'page',
        size: 'page_size'
      },
      columnsFactory: () => [
        { type: 'selection', width: 60 },
        { type: 'index', width: 60, label: '序号' },
        { prop: 'student_no', label: '学号', width: 130 },
        { prop: 'student_name', label: '姓名', width: 90 },
        { prop: 'college', label: '学院', minWidth: 140 },
        { prop: 'major', label: '专业', minWidth: 140 },
        { prop: 'graduation_year', label: '毕业年份', width: 100 },
        {
          prop: 'employment_status',
          label: '就业状态',
          width: 90,
          formatter: (row: WarningItem) => {
            const empStatus = row.employment_status ?? 0
            const status = empStatus === 1 ? 'success' : 'info'
            const text = EMPLOYMENT_STATUS_MAP[empStatus] || '未知'
            return h(ElTag, { type: status, size: 'small' }, () => text)
          }
        },
        {
          prop: 'warning_type',
          label: '预警类型',
          width: 120,
          formatter: (row: WarningItem) =>
            WARNING_TYPE_MAP[row.warning_type] || row.warning_type || '未知'
        },
        {
          prop: 'level',
          label: '预警级别',
          width: 100,
          formatter: (row: WarningItem) => {
            const config = WARNING_LEVEL_MAP[row.level] || { type: 'info', text: '未知' }
            return h(ElTag, { type: config.type as any }, () => config.text)
          }
        },
        { prop: 'cur_city', label: '当前城市', minWidth: 100 },
        { prop: 'desire_city', label: '期望城市', minWidth: 100 },
        {
          prop: 'profile_complete',
          label: '档案完整度',
          width: 100,
          formatter: (row: WarningItem) => `${row.profile_complete || 0}%`
        },
        {
          prop: 'handled',
          label: '处理状态',
          width: 90,
          formatter: (row: WarningItem) => {
            const type = row.handled ? 'success' : 'info'
            const text = row.handled ? '已处理' : '待处理'
            return h(ElTag, { type, size: 'small' }, () => text)
          }
        },
        { prop: 'created_at', label: '创建时间', width: 170 },
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
      ]
    },
    transform: {
      responseAdapter: (response: any) => ({
        records: response?.list || [],
        total: response?.total || 0,
        current: response?.page || 1,
        size: response?.page_size || 20
      })
    }
  })

  const searchItems = computed(() => [
    {
      key: 'level',
      label: '预警级别',
      type: 'select' as const,
      props: {
        placeholder: '请选择',
        options: Object.entries(WARNING_LEVEL_MAP).map(([value, config]) => ({
          label: config.text,
          value: Number(value)
        })),
        clearable: true
      }
    },
    {
      key: 'handled',
      label: '处理状态',
      type: 'select' as const,
      props: {
        placeholder: '请选择',
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
        placeholder: '请选择',
        options: Object.entries(WARNING_TYPE_MAP).map(([value, text]) => ({ label: text, value })),
        clearable: true
      }
    }
  ])

  const handleSearch = (params: Record<string, unknown>) => {
    replaceSearchParams(params)
    fetchData()
  }

  const handleReset = () => {
    resetSearchParams()
  }

  const handleSelectionChange = (selection: WarningItem[]) => {
    selectedRows.value = selection
  }

  const showAdvice = (row: WarningItem) => {
    currentWarningId.value = row.warning_id
    const levelType = WARNING_LEVEL_MAP[row.level]?.type
    currentAdvice.value = {
      title: `学生 ${row.student_name || row.account_id} 的就业预警`,
      level: levelType === 'danger' ? 'error' : levelType === 'warning' ? 'warning' : 'info',
      analysis: row.ai_suggestion || '该学生长期未找到合适工作，需要重点关注和个性化辅导。',
      suggestion: '建议与学生进行一对一沟通，了解其求职意向和困难点，同时推荐相关岗位资源。',
      actions: [
        '安排职业辅导老师与学生进行一对一沟通',
        '推荐相关实习/就业岗位',
        '邀请学生参加就业讲座和模拟面试',
        '建立跟踪档案，定期跟进'
      ]
    }
    aiAdviceVisible.value = true
  }

  const handleMarkProcessed = async () => {
    try {
      await handleWarning(currentWarningId.value, { handled: true })
      ElMessage.success('已标记为处理')
      aiAdviceVisible.value = false
      refreshData()
    } catch (error) {
      console.error('标记失败:', error)
    }
  }

  const handleSingle = async (row: WarningItem) => {
    try {
      await ElMessageBox.confirm(`确定要处理该预警吗？`, '处理预警', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      await handleWarning(row.warning_id, { handled: true })
      ElMessage.success('处理成功')
      refreshData()
    } catch (error) {
      if (error !== 'cancel') {
        console.error('处理失败:', error)
      }
    }
  }

  const handleBatchHandle = async () => {
    if (selectedRows.value.length === 0) {
      ElMessage.warning('请先选择要处理的预警')
      return
    }
    try {
      await ElMessageBox.confirm(
        `确定要批量处理 ${selectedRows.value.length} 条预警吗？`,
        '批量处理',
        { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
      )
      const promises = selectedRows.value.map((row) =>
        handleWarning(row.warning_id, { handled: true })
      )
      await Promise.all(promises)
      ElMessage.success('批量处理成功')
      refreshData()
    } catch (error) {
      if (error !== 'cancel') {
        console.error('批量处理失败:', error)
      }
    }
  }

  const handleGenerateWarnings = async () => {
    try {
      generating.value = true
      const res = await generateWarnings({
        page: generatePage.value,
        page_size: generatePageSize.value
      })
      generateResult.value = res.data || {}
      showGenerateResult.value = true
      refreshData()
    } catch (error: any) {
      ElMessage.error(error.message || '生成预警失败')
    } finally {
      generating.value = false
    }
  }

  const handleGenerateResultPageChange = async (page: number) => {
    generatePage.value = page
    try {
      const res = await generateWarnings({
        page: generatePage.value,
        page_size: generatePageSize.value
      })
      if (generateResult.value) {
        generateResult.value.warnings = res.data?.warnings || res.data
      }
    } catch (error: any) {
      ElMessage.error(error.message || '获取失败')
    }
  }

  const handleGenerateResultPageSizeChange = async (size: number) => {
    generatePageSize.value = size
    generatePage.value = 1
    try {
      const res = await generateWarnings({
        page: generatePage.value,
        page_size: generatePageSize.value
      })
      if (generateResult.value) {
        generateResult.value.warnings = res.data?.warnings || res.data
      }
    } catch (error: any) {
      ElMessage.error(error.message || '获取失败')
    }
  }

  const handleViewProfile = (row: WarningItem) => {
    currentProfileId.value = row.profile_id
    showProfileDialog.value = true
  }
</script>

<style scoped>
  .page-school-warnings {
    padding: 20px;
  }

  .art-table-card {
    width: 100%;
  }

  .ai-advice-content {
    padding: 10px 0;
  }
</style>