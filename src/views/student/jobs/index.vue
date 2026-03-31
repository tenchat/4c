<!-- 岗位推荐页面 -->
<template>
  <div class="page-student-jobs art-full-height">
    <ElCard class="art-card-xs mb-4">
      <ArtSearchBar
        v-model="searchForm"
        :items="searchItems"
        :span="6"
        :gutter="12"
        @search="handleSearch"
        @reset="handleReset"
      />
    </ElCard>

    <ElCard class="art-card-xs">
      <div class="job-list" v-loading="loading">
        <ElEmpty v-if="!loading && data.length === 0" description="暂无岗位推荐" />

        <div v-else>
          <ElRow :gutter="20">
            <ElCol
              v-for="job in data"
              :key="job.job_id"
              :xs="24"
              :sm="12"
              :md="8"
              :lg="6"
              class="mb-4"
            >
              <ElCard class="job-card" shadow="hover">
                <template #header>
                  <div class="job-header">
                    <span class="job-title text-base font-medium">{{ job.title }}</span>
                    <ElTag v-if="isNewJob(job.published_at)" type="success" size="small">最新</ElTag>
                  </div>
                </template>

                <div class="job-content">
                  <div class="job-info mb-2">
                    <ElIcon class="mr-1"><Location /></ElIcon>
                    <span class="text-sm text-gray-600">{{ job.city || '未知城市' }}</span>
                  </div>

                  <div class="job-info mb-2">
                    <ElIcon class="mr-1"><Briefcase /></ElIcon>
                    <span class="text-sm text-gray-600">{{ job.industry || '互联网/IT' }}</span>
                  </div>

                  <div class="job-salary text-lg font-medium text-red-500 mb-3">
                    {{ job.min_salary || 0 }}-{{ job.max_salary || 0 }}元/月
                  </div>

                  <div class="job-tags mb-3">
                    <ElTag
                      v-for="keyword in (job.keywords || []).slice(0, 3)"
                      :key="keyword"
                      size="small"
                      class="mr-1 mb-1"
                    >
                      {{ keyword }}
                    </ElTag>
                  </div>
                </div>

                <template #footer>
                  <div class="flex justify-between items-center">
                    <span class="text-xs text-gray-400">{{ formatDate(job.published_at) }}</span>
                    <ElButton type="primary" size="small" @click="handleApply(job)">
                      投递简历
                    </ElButton>
                  </div>
                </template>
              </ElCard>
            </ElCol>
          </ElRow>

          <div class="pagination-wrapper mt-4 flex justify-end">
            <ElPagination
              v-model:current-page="pagination.current"
              v-model:page-size="pagination.size"
              :total="pagination.total"
              :page-sizes="[12, 24, 36, 48]"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </div>
      </div>
    </ElCard>
  </div>
</template>

<script setup lang="ts">
  import { fetchStudentJobs, applyForJob, type JobListParams } from '@/api/student'
  import { ElMessage, ElMessageBox } from 'element-plus'
  import { Location, Briefcase } from '@element-plus/icons-vue'

  defineOptions({ name: 'StudentJobs' })

  interface JobItem {
    job_id: string
    title: string
    city: string
    province: string
    industry: string
    min_salary: number
    max_salary: number
    keywords: string[]
    status: number
    published_at: string
    expired_at: string
  }

  const loading = ref(false)
  const data = ref<JobItem[]>([])

  const searchForm = ref<Partial<JobListParams>>({
    city: undefined,
    industry: undefined,
    min_salary: undefined,
    max_salary: undefined,
    keyword: undefined
  })

  const pagination = reactive({
    current: 1,
    size: 12,
    total: 0
  })

  const INDUSTRY_OPTIONS = [
    { label: '互联网/IT', value: 'internet' },
    { label: '金融', value: 'finance' },
    { label: '教育', value: 'education' },
    { label: '制造业', value: 'manufacturing' },
    { label: '房地产', value: 'real_estate' },
    { label: '医疗健康', value: 'healthcare' },
    { label: '政府/事业单位', value: 'government' },
    { label: '其他', value: 'other' }
  ]

  const searchItems = computed(() => [
    {
      key: 'city',
      label: '城市',
      type: 'input' as const,
      props: { placeholder: '请输入城市', clearable: true }
    },
    {
      key: 'industry',
      label: '行业',
      type: 'select' as const,
      props: { placeholder: '请选择行业', options: INDUSTRY_OPTIONS, clearable: true }
    },
    {
      key: 'min_salary',
      label: '最低薪资',
      type: 'number' as const,
      props: { placeholder: '最低薪资(元/月)', min: 0 }
    },
    {
      key: 'max_salary',
      label: '最高薪资',
      type: 'number' as const,
      props: { placeholder: '最高薪资(元/月)', min: 0 }
    },
    {
      key: 'keyword',
      label: '关键词',
      type: 'input' as const,
      props: { placeholder: '搜索岗位名称', clearable: true }
    }
  ])

  const isNewJob = (dateStr: string | null): boolean => {
    if (!dateStr) return false
    const publishDate = new Date(dateStr)
    const now = new Date()
    const diffDays = Math.floor((now.getTime() - publishDate.getTime()) / (1000 * 60 * 60 * 24))
    return diffDays <= 7
  }

  const formatDate = (dateStr: string | null): string => {
    if (!dateStr) return '-'
    const date = new Date(dateStr)
    return date.toLocaleDateString('zh-CN')
  }

  const fetchJobs = async () => {
    loading.value = true
    try {
      const params: JobListParams = {
        ...searchForm.value,
        page: pagination.current,
        page_size: pagination.size
      }
      const res: any = await fetchStudentJobs(params)
      if (res) {
        data.value = res.list || []
        pagination.total = res.total || 0
      }
    } catch (error) {
      console.error('获取岗位列表失败:', error)
    } finally {
      loading.value = false
    }
  }

  const handleSearch = (params: Record<string, unknown>) => {
    searchForm.value = { ...params }
    pagination.current = 1
    fetchJobs()
  }

  const handleReset = () => {
    searchForm.value = {}
    pagination.current = 1
    fetchJobs()
  }

  const handleSizeChange = (size: number) => {
    pagination.size = size
    pagination.current = 1
    fetchJobs()
  }

  const handleCurrentChange = (current: number) => {
    pagination.current = current
    fetchJobs()
  }

  const handleApply = async (job: JobItem) => {
    try {
      await ElMessageBox.confirm(`确定要投递 "${job.title}" 岗位吗？`, '投递简历', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      })
      const res: any = await applyForJob(job.job_id)
      if (res.code === 200) {
        ElMessage.success('投递成功')
      } else {
        ElMessage.error(res.message || '投递失败')
      }
    } catch (error) {
      if (error !== 'cancel') {
        console.error('投递失败:', error)
      }
    }
  }

  onMounted(() => {
    fetchJobs()
  })
</script>

<style scoped>
  .page-student-jobs {
    padding: 20px;
  }

  .job-card {
    height: 100%;
    transition: all 0.3s;
  }

  .job-card:hover {
    transform: translateY(-4px);
  }

  .job-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
  }

  .job-title {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .job-info {
    display: flex;
    align-items: center;
  }

  .job-salary {
    font-weight: 600;
  }

  .pagination-wrapper {
    padding: 16px 0;
  }
</style>
