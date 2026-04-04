<!-- 管理端数据大屏 -->
<template>
  <div class="databoard-admin">
    <!-- 页面标题 -->
    <div class="databoard-header">
      <h1 class="databoard-title">就业平台数据大屏</h1>
      <div class="header-time">{{ currentTime }}</div>
    </div>

    <!-- 统计卡片区域 -->
    <div class="stats-grid">
      <art-stats-card title="学生总数" :count="stats.totalStudents" :description="stats.totalStudents + ' 人'" icon="ri:user-line" icon-style="bg-blue-500" />
      <art-stats-card title="企业总数" :count="stats.totalCompanies" :description="stats.totalCompanies + ' 家'" icon="ri:building-line" icon-style="bg-green-500" />
      <art-stats-card title="在招岗位" :count="stats.totalJobs" :description="stats.totalJobs + ' 个'" icon="ri:briefcase-line" icon-style="bg-orange-500" />
      <art-stats-card title="整体就业率" :count="stats.overallRate" :description="stats.overallRate + '%'" icon="ri:trend-charts-line" icon-style="bg-red-500" />
      <art-stats-card title="本月新增简历" :count="stats.monthlyNewResumes" :description="stats.monthlyNewResumes + ' 份'" icon="ri:file-list-3-line" icon-style="bg-purple-500" />
      <art-stats-card title="待审核企业" :count="stats.pendingCompanies" :description="stats.pendingCompanies + ' 家'" icon="ri:government-line" icon-style="bg-yellow-500" />
    </div>

    <!-- 图表区域 -->
    <div class="charts-section">
      <!-- 第一行：3个环形图 -->
      <div class="charts-row three-cols">
        <art-card-banner title="就业状态分布" description="已就业/待就业/升学/出国占比">
          <art-ring-chart :data="employmentDistribution" :radius="['50%', '75%']" :show-legend="true" legend-position="bottom" :colors="chartColors" height="240px" :loading="chartLoading" center-text="总计" />
        </art-card-banner>
        <art-card-banner title="企业行业分布" description="各行业企业数量占比">
          <art-ring-chart :data="industryDistribution" :radius="['50%', '75%']" :show-legend="true" legend-position="bottom" :colors="chartColors" height="240px" :loading="chartLoading" />
        </art-card-banner>
        <art-card-banner title="学历层次分布" description="本/硕/博学历占比">
          <art-ring-chart :data="degreeDistribution" :radius="['50%', '75%']" :show-legend="true" legend-position="bottom" :colors="chartColors" height="240px" :loading="chartLoading" />
        </art-card-banner>
      </div>

      <!-- 第二行：2个图表 -->
      <div class="charts-row two-cols">
        <art-card-banner title="各学院就业率对比" description="不同学院毕业生就业率排名">
          <art-bar-chart :data="collegeEmploymentData" :x-axis-data="collegeLabels" :colors="chartColors" height="260px" :loading="chartLoading" :show-legend="true" />
        </art-card-banner>
        <art-card-banner title="热门岗位投递排名" description="投递量最高的岗位TOP10">
          <art-h-bar-chart :data="hotJobsData" :x-axis-data="hotJobsLabels" :colors="chartColors" height="260px" :loading="chartLoading" />
        </art-card-banner>
      </div>

      <!-- 第三行：2个图表 -->
      <div class="charts-row two-cols">
        <art-card-banner title="年度就业率趋势" description="近5年就业率变化趋势">
          <art-line-chart :data="trendData" :x-axis-data="trendLabels" :colors="chartColors" height="260px" :show-area-color="true" :loading="chartLoading" />
        </art-card-banner>
        <art-card-banner title="各专业薪资排名" description="不同专业平均薪资对比(元/月)">
          <art-h-bar-chart :data="salaryData" :x-axis-data="salaryLabels" :colors="chartColors" height="260px" :loading="chartLoading" />
        </art-card-banner>
      </div>

      <!-- 第四行：3个图表 -->
      <div class="charts-row three-cols">
        <art-card-banner title="学生能力雷达图" description="各维度能力评分">
          <art-radar-chart :indicator="radarIndicator" :data="radarData" height="260px" :loading="chartLoading" />
        </art-card-banner>
        <art-card-banner title="薪资与经验分布" description="薪资与工作经验关系">
          <art-scatter-chart :data="scatterData" height="260px" :loading="chartLoading" />
        </art-card-banner>
        <art-card-banner title="男女就业率对比" description="各专业男女就业率">
          <art-dual-bar-compare-chart :positive-data="maleData" :negative-data="femaleData" :x-axis-data="compareLabels" positive-name="男性就业率" negative-name="女性就业率" height="260px" />
        </art-card-banner>
      </div>

      <!-- 第五行：动态+紧缺人才 -->
      <div class="charts-row two-cols">
        <art-card-banner title="最新动态" description="实时就业动态信息">
          <div class="news-scroll">
            <div v-if="newsList.length === 0 && !chartLoading" class="flex-cc h-full text-gray-500">暂无动态数据</div>
            <div v-else class="news-list">
              <div v-for="(item, index) in newsList" :key="index" class="news-item">
                <span class="news-badge">{{ item.badge }}</span>
                <span class="news-time">{{ item.time }}</span>
                <span class="news-content">{{ item.content }}</span>
              </div>
            </div>
          </div>
        </art-card-banner>
        <art-card-banner title="紧缺人才岗位TOP10" description="市场需求最大的岗位">
          <art-h-bar-chart :data="scarceTalentsData" :x-axis-data="scarceTalentsLabels" :colors="chartColors" height="260px" :loading="chartLoading" />
        </art-card-banner>
      </div>

      <!-- 第六行：3个图表 -->
      <div class="charts-row three-cols">
        <art-card-banner title="企业规模分布" description="各规模企业数量">
          <art-ring-chart :data="companySizeData" :radius="['50%', '75%']" :show-legend="true" legend-position="bottom" :colors="chartColors" height="220px" :loading="chartLoading" />
        </art-card-banner>
        <art-card-banner title="就业地域分布" description="各省份学生就业分布TOP8">
          <art-h-bar-chart :data="regionData" :x-axis-data="regionLabels" :colors="chartColors" height="220px" :loading="chartLoading" />
        </art-card-banner>
        <art-card-banner title="城市等级分布" description="一线/二线/三线城市占比">
          <art-ring-chart :data="cityLevelData" :radius="['50%', '75%']" :show-legend="true" legend-position="bottom" :colors="chartColors" height="220px" :loading="chartLoading" />
        </art-card-banner>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { fetchAdminDataboard } from '@/api/admin'
  import { onMounted, onUnmounted, ref } from 'vue'
  import type { PieDataItem } from '@/types/component/chart'

  defineOptions({ name: 'AdminDataboard' })

  const chartColors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc', '#73c0de']

  const chartLoading = ref(false)
  const currentTime = ref('')

  const stats = ref({
    totalStudents: 0,
    totalCompanies: 0,
    totalJobs: 0,
    overallRate: 0,
    monthlyNewResumes: 0,
    pendingCompanies: 0
  })

  const employmentDistribution = ref<PieDataItem[]>([])
  const industryDistribution = ref<PieDataItem[]>([])
  const degreeDistribution = ref<PieDataItem[]>([])
  const collegeEmploymentData = ref<any[]>([])
  const collegeLabels = ref<string[]>([])
  const hotJobsData = ref<number[]>([])
  const hotJobsLabels = ref<string[]>([])
  const trendData = ref<number[]>([])
  const trendLabels = ref<string[]>([])
  const salaryData = ref<number[]>([])
  const salaryLabels = ref<string[]>([])
  const radarIndicator = ref<any[]>([])
  const radarData = ref<any[]>([])
  const scatterData = ref<any[]>([])
  const maleData = ref<number[]>([])
  const femaleData = ref<number[]>([])
  const compareLabels = ref<string[]>([])
  const newsList = ref<any[]>([])
  const scarceTalentsData = ref<number[]>([])
  const scarceTalentsLabels = ref<string[]>([])
  const companySizeData = ref<PieDataItem[]>([])
  const regionData = ref<number[]>([])
  const regionLabels = ref<string[]>([])
  const cityLevelData = ref<PieDataItem[]>([])

  const mockData = {
    stats: {
      totalStudents: 12580,
      totalCompanies: 856,
      totalJobs: 3420,
      overallRate: 86.5,
      monthlyNewResumes: 328,
      pendingCompanies: 12
    },
    employmentDistribution: [
      { name: '已就业', value: 5800 },
      { name: '待就业', value: 1200 },
      { name: '升学', value: 1500 },
      { name: '出国', value: 500 },
      { name: '创业', value: 280 }
    ],
    industryDistribution: [
      { name: '互联网/IT', value: 320 },
      { name: '金融', value: 180 },
      { name: '教育培训', value: 150 },
      { name: '制造业', value: 120 },
      { name: '房地产', value: 86 }
    ],
    degreeDistribution: [
      { name: '本科', value: 8500 },
      { name: '硕士', value: 3200 },
      { name: '博士', value: 880 }
    ],
    collegeEmploymentData: [
      { name: '计算机学院', data: [92, 88, 95, 91, 94] },
      { name: '经济管理学院', data: [85, 82, 88, 86, 90] },
      { name: '机械工程学院', data: [78, 75, 82, 80, 85] },
      { name: '外国语学院', data: [72, 70, 76, 74, 78] }
    ],
    collegeLabels: ['计算机学院', '经管学院', '机械学院', '外国语学院', '艺术学院'],
    hotJobsData: [280, 245, 198, 176, 165, 143, 128, 115, 98, 85],
    hotJobsLabels: ['前端开发', '后端开发', '数据分析师', '产品经理', '算法工程师', 'UI设计', '运营', '测试', '运维', '架构师'],
    trendData: [78, 80, 82, 85, 86.5],
    trendLabels: ['2021', '2022', '2023', '2024', '2025'],
    salaryData: [15000, 13500, 12500, 11500, 10500, 9500, 8800, 8200],
    salaryLabels: ['人工智能', '金融科技', '互联网', '法律', '医疗健康', '教育培训', '制造业', '房地产'],
    radarIndicator: [
      { name: '技术能力', max: 100 },
      { name: '沟通能力', max: 100 },
      { name: '领导力', max: 100 },
      { name: '创新能力', max: 100 },
      { name: '执行力', max: 100 },
      { name: '学习能力', max: 100 }
    ],
    radarData: [
      { name: '2025届毕业生', value: [85, 78, 65, 82, 90, 88] },
      { name: '企业需求', value: [90, 75, 70, 88, 85, 80] }
    ],
    scatterData: [
      { value: [1, 8000] },
      { value: [2, 12000] },
      { value: [3, 15000] },
      { value: [4, 18000] },
      { value: [5, 22000] },
      { value: [3, 14000] },
      { value: [4, 16000] },
      { value: [5, 20000] },
      { value: [2, 10000] },
      { value: [6, 25000] },
      { value: [7, 30000] },
      { value: [8, 35000] }
    ],
    maleData: [92, 88, 85, 78, 75, 72],
    femaleData: [88, 85, 82, 80, 76, 74],
    compareLabels: ['计算机', '金融', '法律', '医学', '教育', '艺术'],
    newsList: [
      { badge: '签约', time: '10:30', content: '计算机学院张同学成功签约腾讯' },
      { badge: '招聘', time: '10:15', content: '经济管理学院举办春季招聘会' },
      { badge: 'Offer', time: '09:45', content: '机械工程李同学获得华为Offer' },
      { badge: '升学', time: '09:20', content: '外国语学院王同学成功升学北大' },
      { badge: '合作', time: '昨天', content: '校企合作签约仪式成功举行' },
      { badge: '讲座', time: '昨天', content: '艺术学院举办就业指导讲座' }
    ],
    scarceTalentsData: [98, 95, 92, 88, 85, 82, 78, 75, 72, 68],
    scarceTalentsLabels: ['AI工程师', '芯片设计', '新能源', '生物医药', '网络安全', '云计算', '大数据', '物联网', '区块链', '量子计算'],
    companySizeData: [
      { name: '微型企业', value: 120 },
      { name: '小型企业', value: 320 },
      { name: '中型企业', value: 250 },
      { name: '大型企业', value: 166 }
    ],
    regionData: [1100, 920, 850, 780, 720, 650, 580, 520],
    regionLabels: ['广东', '北京', '上海', '浙江', '江苏', '四川', '湖北', '陕西'],
    cityLevelData: [
      { name: '一线城市', value: 4500 },
      { name: '新一线城市', value: 3200 },
      { name: '二线城市', value: 2800 },
      { name: '三线城市', value: 2080 }
    ]
  }

  const updateTime = () => {
    const now = new Date()
    currentTime.value = now.toLocaleString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })
  }

  const loadData = async () => {
    chartLoading.value = true
    try {
      const res: any = await fetchAdminDataboard()
      // API 返回结构: { code, message, data: { stats, ... } }
      // HTTP 拦截器可能直接返回 data 或整个响应
      const apiData = res?.data?.data || res?.data || res

      if (apiData) {
        // 统计卡片数据
        if (apiData.stats) {
          stats.value = {
            totalStudents: apiData.stats.total_students || 0,
            totalCompanies: apiData.stats.total_companies || 0,
            totalJobs: apiData.stats.total_jobs || 0,
            overallRate: apiData.stats.overall_employment_rate || 0,
            monthlyNewResumes: apiData.stats.monthly_new_resumes || 0,
            pendingCompanies: apiData.stats.pending_companies || 0
          }
        } else if (apiData.total_students !== undefined) {
          // 兼容直接返回 stats 字段的情况
          stats.value = {
            totalStudents: apiData.total_students || 0,
            totalCompanies: apiData.total_companies || 0,
            totalJobs: apiData.total_jobs || 0,
            overallRate: apiData.overall_employment_rate || 0,
            monthlyNewResumes: apiData.monthly_new_resumes || 0,
            pendingCompanies: apiData.pending_companies || 0
          }
        } else {
          useMockData()
        }

        // 行业分布
        if (apiData.industry_distribution) {
          industryDistribution.value = apiData.industry_distribution
        } else {
          industryDistribution.value = mockData.industryDistribution
        }

        // 学院就业数据
        if (apiData.university_stats) {
          const uniStats = apiData.university_stats.slice(0, 6)
          collegeLabels.value = uniStats.map((u: any) => u.name)
          collegeEmploymentData.value = uniStats.map((u: any) => ({
            name: u.name,
            data: [u.employment_rate]
          }))
        } else {
          collegeEmploymentData.value = mockData.collegeEmploymentData
          collegeLabels.value = mockData.collegeLabels
        }

        // 就业分布
        if (apiData.employment_distribution) {
          employmentDistribution.value = apiData.employment_distribution
        } else {
          employmentDistribution.value = mockData.employmentDistribution
        }

        // 学历分布
        if (apiData.degree_distribution) {
          degreeDistribution.value = apiData.degree_distribution
        } else {
          degreeDistribution.value = mockData.degreeDistribution
        }
      } else {
        useMockData()
      }
    } catch {
      useMockData()
    } finally {
      chartLoading.value = false
    }
  }

  const useMockData = () => {
    stats.value = mockData.stats
    employmentDistribution.value = mockData.employmentDistribution
    industryDistribution.value = mockData.industryDistribution
    degreeDistribution.value = mockData.degreeDistribution
    collegeEmploymentData.value = mockData.collegeEmploymentData
    collegeLabels.value = mockData.collegeLabels
    hotJobsData.value = mockData.hotJobsData
    hotJobsLabels.value = mockData.hotJobsLabels
    trendData.value = mockData.trendData
    trendLabels.value = mockData.trendLabels
    salaryData.value = mockData.salaryData
    salaryLabels.value = mockData.salaryLabels
    radarIndicator.value = mockData.radarIndicator
    radarData.value = mockData.radarData
    scatterData.value = mockData.scatterData
    maleData.value = mockData.maleData
    femaleData.value = mockData.femaleData
    compareLabels.value = mockData.compareLabels
    newsList.value = mockData.newsList
    scarceTalentsData.value = mockData.scarceTalentsData
    scarceTalentsLabels.value = mockData.scarceTalentsLabels
    companySizeData.value = mockData.companySizeData
    regionData.value = mockData.regionData
    regionLabels.value = mockData.regionLabels
    cityLevelData.value = mockData.cityLevelData
  }

  let timeInterval: any = null

  onMounted(() => {
    updateTime()
    timeInterval = setInterval(updateTime, 1000)
    loadData()
  })

  onUnmounted(() => {
    if (timeInterval) clearInterval(timeInterval)
  })
</script>

<style scoped>
  .databoard-admin {
    padding: 16px;
    min-height: 100vh;
    background: #ffffff;
  }

  .databoard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 1px solid #e5e7eb;
  }

  .databoard-title {
    color: #1f2937;
    font-size: 24px;
    font-weight: 700;
    margin: 0;
    background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .header-time {
    color: #6b7280;
    font-size: 12px;
  }

  /* 统计卡片网格 - 响应式 */
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 12px;
    margin-bottom: 20px;
  }

  @media (max-width: 1200px) {
    .stats-grid {
      grid-template-columns: repeat(3, 1fr);
    }
  }

  @media (max-width: 768px) {
    .stats-grid {
      grid-template-columns: repeat(2, 1fr);
      gap: 10px;
    }
  }

  @media (max-width: 480px) {
    .stats-grid {
      grid-template-columns: 1fr;
      gap: 8px;
    }
  }

  /* 图表区域 */
  .charts-section {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .charts-row {
    display: flex;
    gap: 16px;
  }

  .charts-row.three-cols > * {
    flex: 1;
    min-width: 0;
  }

  .charts-row.two-cols > * {
    flex: 1;
    min-width: 0;
  }

  /* 响应式适配 */
  @media (max-width: 1024px) {
    .charts-row {
      flex-direction: column;
      gap: 12px;
    }
  }

  @media (max-width: 768px) {
    .databoard-admin {
      padding: 12px;
    }

    .databoard-title {
      font-size: 18px;
    }

    .charts-section {
      gap: 12px;
    }
  }

  /* 新闻滚动区域 */
  .news-scroll {
    height: 220px;
    overflow-y: auto;
    padding: 4px;
  }

  .news-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .news-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 10px;
    background: #f3f4f6;
    border-radius: 6px;
    transition: all 0.3s ease;
  }

  .news-item:hover {
    background: #e5e7eb;
    transform: translateX(4px);
  }

  .news-badge {
    flex-shrink: 0;
    padding: 2px 6px;
    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
    border-radius: 4px;
    color: #fff;
    font-size: 10px;
    font-weight: 600;
  }

  .news-time {
    flex-shrink: 0;
    color: #9ca3af;
    font-size: 11px;
    min-width: 45px;
  }

  .news-content {
    color: #374151;
    font-size: 12px;
    line-height: 1.4;
  }
</style>