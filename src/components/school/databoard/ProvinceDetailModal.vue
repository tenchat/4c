<!-- 省份详情弹窗 -->
<template>
  <ElDialog
    v-model="visible"
    :title="`${provinceName} - 详情`"
    width="960px"
    :destroy-on-close="true"
    class="province-detail-modal"
  >
    <!-- 加载状态 -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <ElIcon class="is-loading" :size="24">
        <Loading />
      </ElIcon>
      <span class="ml-2 text-gray-500">加载中...</span>
    </div>

    <template v-else>
      <!-- Tab 切换 -->
      <ElTabs v-model="activeTab" @tab-change="handleTabChange">
        <!-- ========== 学生 Tab ========== -->
        <ElTabPane label="学生" name="students">
          <!-- 汇总卡片 -->
          <div class="summary-cards">
            <div class="summary-card">
              <div class="summary-value">{{ studentSummary.total || 0 }}</div>
              <div class="summary-label">毕业生总数</div>
            </div>
            <div class="summary-card">
              <div class="summary-value text-green-600">{{ studentSummary.employment_distribution?.employed || 0 }}</div>
              <div class="summary-label">已就业</div>
            </div>
            <div class="summary-card">
              <div class="summary-value text-orange-500">{{ studentSummary.employment_distribution?.unemployed || 0 }}</div>
              <div class="summary-label">未就业</div>
            </div>
            <div class="summary-card">
              <div class="summary-value">{{ studentSummary.avg_salary || 0 }}元</div>
              <div class="summary-label">平均薪资</div>
            </div>
          </div>

          <!-- 学历分布 & 行业分布 -->
          <div class="distribution-row">
            <!-- 学历分布 -->
            <div class="dist-section">
              <div class="dist-title">学历分布</div>
              <div class="dist-bars">
                <div class="dist-item">
                  <span class="dist-label">本科</span>
                  <div class="dist-progress"><ElProgress :percentage="getDegreePercent('bachelor')" :stroke-width="10" /></div>
                  <span class="dist-count">{{ studentSummary.degree_distribution?.bachelor || 0 }}人</span>
                </div>
                <div class="dist-item">
                  <span class="dist-label">硕士</span>
                  <div class="dist-progress"><ElProgress :percentage="getDegreePercent('master')" :stroke-width="10" /></div>
                  <span class="dist-count">{{ studentSummary.degree_distribution?.master || 0 }}人</span>
                </div>
                <div class="dist-item">
                  <span class="dist-label">博士</span>
                  <div class="dist-progress"><ElProgress :percentage="getDegreePercent('doctoral')" :stroke-width="10" /></div>
                  <span class="dist-count">{{ studentSummary.degree_distribution?.doctoral || 0 }}人</span>
                </div>
              </div>
            </div>

            <!-- 热门行业 -->
            <div class="dist-section">
              <div class="dist-title">热门行业 Top 5</div>
              <div class="industry-list">
                <div
                  v-for="(item, index) in studentSummary.top_industries"
                  :key="index"
                  class="industry-item"
                >
                  <span class="industry-rank">{{ index + 1 }}</span>
                  <span class="industry-name">{{ industryText(item.industry) }}</span>
                  <span class="industry-count">{{ item.count }}人</span>
                </div>
                <div v-if="!studentSummary.top_industries?.length" class="text-gray-400 text-sm text-center py-4">
                  暂无数据
                </div>
              </div>
            </div>
          </div>

          <!-- 学生列表 -->
          <div class="student-table">
            <div class="table-title">学生列表</div>
            <ElTable :data="studentList" stripe size="small" max-height="240">
              <ElTableColumn prop="student_no" label="学号" width="110" />
              <ElTableColumn prop="college" label="学院" min-width="100" show-overflow-tooltip />
              <ElTableColumn prop="major" label="专业" min-width="100" show-overflow-tooltip />
              <ElTableColumn prop="degree" label="学历" width="70">
                <template #default="{ row }">
                  {{ degreeLabel(row.degree) }}
                </template>
              </ElTableColumn>
              <ElTableColumn prop="cur_company" label="当前公司" min-width="120" show-overflow-tooltip />
              <ElTableColumn prop="cur_city" label="城市" width="80" />
              <ElTableColumn prop="cur_industry" label="行业" min-width="100" show-overflow-tooltip>
                <template #default="{ row }">
                  {{ industryText(row.cur_industry) }}
                </template>
              </ElTableColumn>
              <ElTableColumn prop="cur_salary" label="薪资" width="80">
                <template #default="{ row }">
                  {{ row.cur_salary ? `${row.cur_salary}元` : '-' }}
                </template>
              </ElTableColumn>
              <ElTableColumn prop="employment_status" label="状态" width="70">
                <template #default="{ row }">
                  <ElTag :type="row.employment_status === 1 ? 'success' : 'warning'" size="small">
                    {{ row.employment_status === 1 ? '已就业' : '未就业' }}
                  </ElTag>
                </template>
              </ElTableColumn>
            </ElTable>

            <!-- 分页 -->
            <div class="pagination-wrap">
              <ElPagination
                v-model:current-page="studentPage"
                v-model:page-size="studentPageSize"
                :total="studentTotal"
                :page-sizes="[10, 20, 50]"
                layout="total, sizes, prev, pager, next"
                @size-change="loadStudents"
                @current-change="loadStudents"
              />
            </div>
          </div>
        </ElTabPane>

        <!-- ========== 企业 Tab ========== -->
        <ElTabPane label="企业" name="companies">
          <!-- 汇总卡片 -->
          <div class="summary-cards">
            <div class="summary-card">
              <div class="summary-value">{{ companySummary.total_companies || 0 }}</div>
              <div class="summary-label">企业总数</div>
            </div>
            <div class="summary-card">
              <div class="summary-value">{{ companySummary.total_jobs || 0 }}</div>
              <div class="summary-label">岗位总数</div>
            </div>
            <div class="summary-card">
              <div class="summary-value">
                {{ companySummary.avg_salary_min || 0 }}-{{ companySummary.avg_salary_max || 0 }}元
              </div>
              <div class="summary-label">平均薪资范围</div>
            </div>
            <div class="summary-card">
              <div class="summary-value">{{ companySummary.recent_activities_count || 0 }}</div>
              <div class="summary-label">近三月活动数</div>
            </div>
          </div>

          <!-- 行业分布 -->
          <div class="company-industry-section">
            <div class="dist-title">行业分布</div>
            <div class="industry-grid">
              <div
                v-for="(item, index) in companySummary.industry_distribution"
                :key="index"
                class="industry-grid-item"
              >
                <span class="industry-name">{{ industryText(item.industry) }}</span>
                <span class="industry-count">{{ item.count }}个岗位</span>
              </div>
              <div v-if="!companySummary.industry_distribution?.length" class="text-gray-400 text-sm text-center py-4">
                暂无数据
              </div>
            </div>
          </div>

          <!-- 企业列表 -->
          <div class="company-table">
            <div class="table-title">企业列表</div>
            <ElTable :data="companyList" stripe size="small" max-height="240">
              <ElTableColumn prop="company_name" label="企业名称" min-width="150" show-overflow-tooltip />
              <ElTableColumn prop="industry" label="行业" width="100" show-overflow-tooltip>
                <template #default="{ row }">
                  {{ industryText(row.industry) }}
                </template>
              </ElTableColumn>
              <ElTableColumn prop="city" label="城市" width="80" />
              <ElTableColumn prop="job_count" label="岗位数" width="70" align="center" />
              <ElTableColumn prop="verified" label="认证" width="70" align="center">
                <template #default="{ row }">
                  <ElTag :type="row.verified ? 'success' : 'info'" size="small">
                    {{ row.verified ? '已认证' : '未认证' }}
                  </ElTag>
                </template>
              </ElTableColumn>
            </ElTable>

            <!-- 分页 -->
            <div class="pagination-wrap">
              <ElPagination
                v-model:current-page="companyPage"
                v-model:page-size="companyPageSize"
                :total="companyTotal"
                :page-sizes="[10, 20, 50]"
                layout="total, sizes, prev, pager, next"
                @size-change="loadCompanies"
                @current-change="loadCompanies"
              />
            </div>
          </div>
        </ElTabPane>
      </ElTabs>
    </template>
  </ElDialog>
</template>

<script setup lang="ts">
  import { ref, watch, computed } from 'vue'
  import { fetchProvinceDetail } from '@/api/school'

  defineOptions({ name: 'ProvinceDetailModal' })

  interface Props {
    modelValue: boolean
    provinceName: string
    year?: number
  }

  const props = defineProps<Props>()
  const emit = defineEmits<{
    'update:modelValue': [value: boolean]
  }>()

  // ========== 状态 ==========
  const visible = computed({
    get: () => props.modelValue,
    set: (val) => emit('update:modelValue', val)
  })

  const activeTab = ref<'students' | 'companies'>('students')
  const loading = ref(false)

  // 学生数据
  const studentSummary = ref<any>({})
  const studentList = ref<any[]>([])
  const studentPage = ref(1)
  const studentPageSize = ref(10)
  const studentTotal = ref(0)

  // 企业数据
  const companySummary = ref<any>({})
  const companyList = ref<any[]>([])
  const companyPage = ref(1)
  const companyPageSize = ref(10)
  const companyTotal = ref(0)

  // ========== 方法 ==========
  const INDUSTRY_MAP: Record<string, string> = {
    // 英文key (job_descriptions表)
    internet: '互联网/IT',
    finance: '金融',
    education: '教育',
    manufacturing: '制造业',
    real_estate: '房地产',
    healthcare: '医疗健康',
    government: '政府/事业单位',
    other: '其他',
    // 中文raw值 (学生表cur_industry/desire_industry原始值)
    '金融/银行': '金融/银行',
    '教育培训': '教育培训',
    '房地产/建筑': '房地产/建筑',
    '医药生物': '医药生物',
    '政府/公共事业': '政府/公共事业',
    '计算机软件': '计算机软件',
    '电子/半导体': '电子/半导体',
    '化工': '化工',
    '机械/装备制造': '机械/装备制造',
    '汽车/交通设备': '汽车/交通设备',
    '通信/网络设备': '通信/网络设备',
    '电力/能源': '电力/能源',
    '新材料': '新材料',
    '航空航天': '航空航天',
    '现代农业': '现代农业',
    '批发/零售': '批发/零售',
    '文化/传媒': '文化/传媒',
    '保险': '保险',
    '环保': '环保',
    // 归一化后的中文行业 (dashboard雷达图)
    '人工智能': '人工智能',
    '金融': '金融',
    '制造业': '制造业',
    '互联网': '互联网',
    '医疗健康': '医疗健康',
    '教育': '教育',
    '房地产': '房地产',
    '交通运输': '交通运输',
    '能源': '能源',
    '文化传媒': '文化传媒',
    '电子信息': '电子信息',
    '建筑': '建筑',
    '法律': '法律',
    '消费零售': '消费零售',
    '农林牧渔': '农林牧渔',
    '军工': '军工',
    '其他': '其他',
  }

  const industryText = (val?: string) => INDUSTRY_MAP[val || ''] || val || ''

  const normalizeProvince = (name: string) => {
    if (!name) return name
    return name.replace(/市|省|自治区|特别行政区|壮族自治区|回族自治区|维吾尔自治区/g, '')
  }

  const loadStudents = async () => {
    try {
      const res: any = await fetchProvinceDetail({
        province: normalizeProvince(props.provinceName),
        tab: 'students',
        page: studentPage.value,
        page_size: studentPageSize.value,
        year: props.year
      })
      if (res) {
        studentSummary.value = res.summary || {}
        studentList.value = res.students?.list || []
        studentTotal.value = res.students?.total || 0
      }
    } catch (err) {
      ElMessage.error('加载学生数据失败')
    }
  }

  const loadCompanies = async () => {
    try {
      const res: any = await fetchProvinceDetail({
        province: normalizeProvince(props.provinceName),
        tab: 'companies',
        page: companyPage.value,
        page_size: companyPageSize.value,
        year: props.year
      })
      if (res) {
        companySummary.value = res.summary || {}
        companyList.value = res.companies?.list || []
        companyTotal.value = res.companies?.total || 0
      }
    } catch (err) {
      ElMessage.error('加载企业数据失败')
    }
  }

  const loadData = async () => {
    loading.value = true
    try {
      await Promise.all([loadStudents(), loadCompanies()])
    } finally {
      loading.value = false
    }
  }

  const handleTabChange = (tab: string) => {
    if (tab === 'students') {
      if (!studentList.value.length) loadStudents()
    } else {
      if (!companyList.value.length) loadCompanies()
    }
  }

  const getDegreePercent = (degree: 'bachelor' | 'master' | 'doctoral') => {
    const total = studentSummary.value.total || 0
    if (!total) return 0
    const count = studentSummary.value.degree_distribution?.[degree] || 0
    return Math.round((count / total) * 100)
  }

  const degreeLabel = (degree: number) => {
    const map: Record<number, string> = { 1: '本科', 2: '硕士', 3: '博士' }
    return map[degree] || '未知'
  }

  // ========== 监听 ==========
  watch(visible, (val) => {
    if (val) {
      activeTab.value = 'students'
      studentPage.value = 1
      companyPage.value = 1
      studentSummary.value = {}
      companySummary.value = {}
      loadData()
    }
  })
</script>

<style scoped>
  .summary-cards {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;
  }

  .summary-card {
    flex: 1;
    background: #f5f7fa;
    border-radius: 8px;
    padding: 12px 16px;
    text-align: center;
  }

  .summary-value {
    font-size: 20px;
    font-weight: 700;
    color: #1a1a1a;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
  }

  .summary-label {
    font-size: 12px;
    color: #8c8c8c;
    margin-top: 4px;
  }

  .distribution-row {
    display: flex;
    gap: 16px;
    margin-bottom: 16px;
  }

  .dist-section {
    flex: 1;
    background: #fafafa;
    border-radius: 8px;
    padding: 12px 16px;
  }

  .dist-title {
    font-size: 13px;
    font-weight: 500;
    color: #1a1a1a;
    margin-bottom: 10px;
  }

  .dist-bars {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .dist-item {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .dist-progress {
    flex: 1;
    min-width: 0;
  }

  .dist-label {
    font-size: 12px;
    color: #595959;
    width: 28px;
    flex-shrink: 0;
  }


  .dist-count {
    font-size: 12px;
    color: #8c8c8c;
    width: 50px;
    text-align: right;
    flex-shrink: 0;
  }

  .industry-list {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .industry-item {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .industry-rank {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: #1677ff;
    color: #fff;
    font-size: 11px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .industry-name {
    flex: 1;
    font-size: 12px;
    color: #3a3a3a;
  }

  .industry-count {
    font-size: 12px;
    color: #8c8c8c;
  }

  .student-table,
  .company-table {
    margin-top: 8px;
  }

  .table-title {
    font-size: 13px;
    font-weight: 500;
    color: #1a1a1a;
    margin-bottom: 8px;
  }

  .pagination-wrap {
    display: flex;
    justify-content: flex-end;
    margin-top: 12px;
  }

  .company-industry-section {
    background: #fafafa;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 16px;
  }

  .industry-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }

  .industry-grid-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 4px 0;
    font-size: 12px;
  }
</style>
