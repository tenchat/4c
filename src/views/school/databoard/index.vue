<!-- 学校端数据大屏 -->
<template>
  <div class="databoard-school" style="background: #0d1117; min-height: 100vh; padding: 20px;">
    <!-- 页面标题 -->
    <h1 class="databoard-title" style="color: #e6edf3;">学校数据大屏</h1>

    <!-- 第一行：4个统计卡片 -->
    <el-row :gutter="20" class="mb-4">
      <el-col :span="6">
        <art-stats-card
          title="本校学生总数"
          :count="stats.totalStudents"
          :description="stats.totalStudents + ' 人'"
          icon="ri:user-line"
          icon-style="bg-blue-500"
        />
      </el-col>
      <el-col :span="6">
        <art-stats-card
          title="合作企业"
          :count="stats.totalCompanies"
          :description="stats.totalCompanies + ' 家'"
          icon="ri:building-line"
          icon-style="bg-green-500"
        />
      </el-col>
      <el-col :span="6">
        <art-stats-card
          title="发布岗位数"
          :count="stats.totalJobs"
          :description="stats.totalJobs + ' 个'"
          icon="ri:briefcase-line"
          icon-style="bg-orange-500"
        />
      </el-col>
      <el-col :span="6">
        <art-stats-card
          title="本校就业率"
          :count="stats.employmentRate"
          :description="stats.employmentRate + '%'"
          icon="ri:trend-charts-line"
          icon-style="bg-red-500"
        />
      </el-col>
    </el-row>

    <!-- 第二行：专业分布环形图 + 就业去向环形图 -->
    <el-row :gutter="20" class="mb-4">
      <el-col :span="12">
        <art-card-banner title="专业分布" description="各专业学生占比">
          <art-ring-chart
            :data="majorDistribution"
            :radius="['50%', '80%']"
            :show-legend="true"
            legend-position="right"
            :colors="chartColors"
            height="300px"
            :loading="chartLoading"
          />
        </art-card-banner>
      </el-col>
      <el-col :span="12">
        <art-card-banner title="就业去向" description="已就业/升学/出国/待业分布">
          <art-ring-chart
            :data="employmentDestination"
            :radius="['50%', '80%']"
            :show-legend="true"
            legend-position="right"
            :colors="chartColors"
            height="300px"
            :loading="chartLoading"
          />
        </art-card-banner>
      </el-col>
    </el-row>

    <!-- 第三行：学院就业率对比 + 薪资分布 -->
    <el-row :gutter="20" class="mb-4">
      <el-col :span="12">
        <art-card-banner title="学院就业率对比" description="各学院就业情况">
          <art-dual-bar-compare-chart
            :positive-data="collegeEmploymentRate"
            :negative-data="[]"
            :x-axis-data="collegeLabels"
            positive-name="就业率"
            :colors="chartColors"
            :y-axis-min="0"
            :y-axis-max="100"
            height="300px"
            :loading="chartLoading"
          />
        </art-card-banner>
      </el-col>
      <el-col :span="12">
        <art-card-banner title="薪资分布" description="各薪资区间人数">
          <art-h-bar-chart
            :data="salaryDistribution"
            :x-axis-data="salaryLabels"
            :colors="chartColors"
            height="300px"
            :loading="chartLoading"
          />
        </art-card-banner>
      </el-col>
    </el-row>

    <!-- 第四行：就业趋势 + 最新动态 -->
    <el-row :gutter="20" class="mb-4">
      <el-col :span="12">
        <art-card-banner title="本校就业趋势" description="近5年就业率变化">
          <art-line-chart
            :data="trendData"
            :x-axis-data="trendLabels"
            :colors="chartColors"
            height="300px"
            :show-area-color="true"
            :loading="chartLoading"
          />
        </art-card-banner>
      </el-col>
      <el-col :span="12">
        <art-card-banner title="本校动态" description="学生就业动态信息">
          <div class="news-scroll" style="height: 300px; overflow-y: auto;">
            <div v-if="newsList.length === 0 && !chartLoading" class="flex-cc h-full text-gray-500">
              暂无动态数据
            </div>
            <div v-else class="news-list">
              <div
                v-for="(item, index) in newsList"
                :key="index"
                class="news-item"
              >
                <span class="news-time">{{ item.time }}</span>
                <span class="news-content">{{ item.content }}</span>
              </div>
            </div>
          </div>
        </art-card-banner>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
  import { fetchSchoolDataboard } from '@/api/school'
  import { onMounted, ref } from 'vue'
  import type { PieDataItem } from '@/types/component/chart'

  defineOptions({ name: 'SchoolDataboard' })

  // 图表颜色配置
  const chartColors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4']

  // 加载状态
  const chartLoading = ref(false)

  // 统计数据
  const stats = ref({
    totalStudents: 0,
    totalCompanies: 0,
    totalJobs: 0,
    employmentRate: 0
  })

  // 专业分布数据
  const majorDistribution = ref<PieDataItem[]>([])

  // 就业去向数据
  const employmentDestination = ref<PieDataItem[]>([])

  // 学院就业率数据
  const collegeEmploymentRate = ref<number[]>([])
  const collegeLabels = ref<string[]>([])

  // 薪资分布数据
  const salaryDistribution = ref<number[]>([])
  const salaryLabels = ref<string[]>([])

  // 趋势数据
  const trendData = ref<number[]>([])
  const trendLabels = ref<string[]>([])

  // 最新动态
  const newsList = ref<{ time: string; content: string }[]>([])

  // Mock 数据
  const mockData = {
    stats: {
      totalStudents: 3250,
      totalCompanies: 128,
      totalJobs: 856,
      employmentRate: 88.5
    },
    majorDistribution: [
      { name: '计算机科学', value: 680 },
      { name: '软件工程', value: 520 },
      { name: '网络工程', value: 320 },
      { name: '信息管理', value: 450 },
      { name: '电子商务', value: 380 },
      { name: '其他专业', value: 900 }
    ],
    employmentDestination: [
      { name: '已就业', value: 2200 },
      { name: '升学', value: 480 },
      { name: '出国', value: 120 },
      { name: '待业', value: 450 }
    ],
    collegeEmploymentRate: [92, 88, 85, 82, 78],
    collegeLabels: ['计算机学院', '软件学院', '信息学院', '商学院', '外语学院'],
    salaryDistribution: [180, 420, 580, 650, 520, 280],
    salaryLabels: ['5k以下', '5k-8k', '8k-12k', '12k-18k', '18k-25k', '25k以上'],
    trendData: [82, 84, 85, 87, 88.5],
    trendLabels: ['2021', '2022', '2023', '2024', '2025'],
    newsList: [
      { time: '2026-03-29', content: '计算机学院王同学成功签约华为' },
      { time: '2026-03-28', content: '软件学院举办专场招聘会' },
      { time: '2026-03-27', content: '信息学院李同学获得考研录取通知' },
      { time: '2026-03-26', content: '商学院张同学成功升学北大' },
      { time: '2026-03-25', content: '外语学院举办就业指导讲座' },
      { time: '2026-03-24', content: '计算机学院举办校企合作洽谈会' },
      { time: '2026-03-23', content: '软件学院赵同学获得出国offer' }
    ]
  }

  // 加载数据
  const loadData = async () => {
    chartLoading.value = true
    try {
      const res: any = await fetchSchoolDataboard()
      if (res) {
        // 使用API数据

        if (res.stats) {
          stats.value = {
            totalStudents: res.stats.total_students || 0,
            totalCompanies: res.stats.total_companies || 0,
            totalJobs: res.stats.total_jobs || 0,
            employmentRate: res.stats.employment_rate || 0
          }
        }

        if (res.major_distribution) {
          majorDistribution.value = res.major_distribution
        }

        if (res.employment_destination) {
          employmentDestination.value = res.employment_destination
        }

        if (res.college_employment) {
          collegeEmploymentRate.value = res.college_employment.values || []
          collegeLabels.value = res.college_employment.labels || []
        }

        if (res.salary_distribution) {
          salaryDistribution.value = res.salary_distribution.values || []
          salaryLabels.value = res.salary_distribution.labels || []
        }

        if (res.trend) {
          trendData.value = res.trend.values || []
          trendLabels.value = res.trend.labels || []
        }

        if (res.news_list) {
          newsList.value = res.news_list
        }
      } else {
        // 使用Mock数据
        useMockData()
      }
    } catch {
      // API调用失败，使用Mock数据
      useMockData()
    } finally {
      chartLoading.value = false
    }
  }

  // 使用Mock数据
  const useMockData = () => {
    stats.value = mockData.stats
    majorDistribution.value = mockData.majorDistribution
    employmentDestination.value = mockData.employmentDestination
    collegeEmploymentRate.value = mockData.collegeEmploymentRate
    collegeLabels.value = mockData.collegeLabels
    salaryDistribution.value = mockData.salaryDistribution
    salaryLabels.value = mockData.salaryLabels
    trendData.value = mockData.trendData
    trendLabels.value = mockData.trendLabels
    newsList.value = mockData.newsList
  }

  onMounted(() => {
    loadData()
  })
</script>

<style scoped>
  .databoard-school {
    background: #0d1117;
    min-height: 100vh;
    padding: 20px;
  }

  .databoard-title {
    color: #e6edf3;
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 20px;
  }

  .mb-4 {
    margin-bottom: 20px;
  }

  .news-scroll {
    padding: 10px 0;
  }

  .news-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .news-item {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 8px 12px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 6px;
    transition: background 0.3s;
  }

  .news-item:hover {
    background: rgba(255, 255, 255, 0.1);
  }

  .news-time {
    flex-shrink: 0;
    color: #8b949e;
    font-size: 12px;
  }

  .news-content {
    color: #e6edf3;
    font-size: 14px;
    line-height: 1.5;
  }
</style>
