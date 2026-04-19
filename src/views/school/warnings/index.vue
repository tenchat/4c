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
            <ElButton type="success" :loading="generating" @click="handleGenerateWarnings" v-ripple>
              生成预警
            </ElButton>
            <ElButton
              type="primary"
              :disabled="selectedRows.length === 0"
              @click="handleBatchHandle"
              v-ripple
            >
              批量标记已处理 ({{ selectedRows.length }})
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
    </ElCard>
  </div>
</template>

<script setup lang="ts">
  import { fetchSchoolWarnings, handleWarning, generateWarnings } from '@/api/school'
  import { useTable } from '@/hooks/core/useTable'
  import ArtButtonTable from '@/components/core/forms/art-button-table/index.vue'
  import { ElTag, ElMessage, ElMessageBox } from 'element-plus'

  defineOptions({ name: 'SchoolWarnings' })

  interface WarningItem {
    warning_id: string
    account_id: string
    warning_type: string
    level: number
    ai_suggestion?: string
    handled: boolean
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
  const generating = ref(false)

  const searchForm = ref({
    level: undefined,
    handled: undefined
  })

  const WARNING_LEVEL_MAP: Record<number, { type: string; text: string }> = {
    1: { type: 'danger', text: '红色预警' },
    2: { type: 'warning', text: '黄色预警' },
    3: { type: 'info', text: '绿色提醒' }
  }

  const WARNING_TYPE_MAP: Record<string, string> = {
    long_term_unemployed: '长期未就业',
    skill_gap: '技能差距',
    high_expectation: '期望过高',
    location_limit: '地域限制',
    experience_lack: '经验缺乏',
    profile_incomplete: '档案不完整',
    general: '一般预警'
  }

  const adviceTypeMap: Record<string, any> = {
    warning: 'warning',
    error: 'danger',
    info: 'info'
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
      apiFn: fetchSchoolWarnings as any,
      apiParams: {
        current: 1,
        size: 20,
        ...searchForm.value
      },
      columnsFactory: () => [
        { type: 'selection', width: 60 },
        { type: 'index', width: 60, label: '序号' },
        { prop: 'account_id', label: '学生账号', width: 180 },
        {
          prop: 'warning_type',
          label: '预警类型',
          width: 180,
          formatter: (row: WarningItem) => {
            const types = (row.warning_type || '').split(',')
            const labels = types.map((t: string) => WARNING_TYPE_MAP[t] || t).filter(Boolean)
            return labels.length > 0 ? labels.join(', ') : '未知'
          }
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
        {
          prop: 'handled',
          label: '处理状态',
          width: 100,
          formatter: (row: WarningItem) => {
            const type = row.handled ? 'success' : 'info'
            const text = row.handled ? '已处理' : '待处理'
            return h(ElTag, { type }, () => text)
          }
        },
        { prop: 'created_at', label: '创建时间', width: 180 },
        {
          prop: 'operation',
          label: '操作',
          width: 180,
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
                type: 'edit',
                title: '处理',
                disabled: row.handled,
                onClick: () => handleSingle(row)
              })
            ])
        }
      ]
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
    }
  ])

  const handleSearch = (params: Record<string, unknown>) => {
    replaceSearchParams(params)
    getData()
  }

  const handleReset = () => {
    resetSearchParams()
  }

  const handleGenerateWarnings = async () => {
    generating.value = true
    try {
      const res = await generateWarnings()
      if (res.code === 200) {
        ElMessage.success(res.message || '预警生成完成')
        refreshData()
      } else {
        ElMessage.error(res.message || '预警生成失败')
      }
    } catch (error) {
      console.error('生成预警失败:', error)
      ElMessage.error('生成预警失败')
    } finally {
      generating.value = false
    }
  }

  const handleSelectionChange = (selection: WarningItem[]) => {
    selectedRows.value = selection
  }

  const showAdvice = (row: WarningItem) => {
    currentWarningId.value = row.warning_id
    currentAdvice.value = {
      title: `学生 ${row.account_id} 的就业预警`,
      level: WARNING_LEVEL_MAP[row.level]?.type === 'danger' ? 'error' :
             WARNING_LEVEL_MAP[row.level]?.type === 'warning' ? 'warning' : 'info',
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
      const promises = selectedRows.value.map((row) => handleWarning(row.warning_id, { handled: true }))
      await Promise.all(promises)
      ElMessage.success('批量处理成功')
      refreshData()
    } catch (error) {
      if (error !== 'cancel') {
        console.error('批量处理失败:', error)
      }
    }
  }
</script>

<style scoped>
  .page-school-warnings {
    padding: 20px;
  }

  .ai-advice-content {
    padding: 10px 0;
  }
</style>
