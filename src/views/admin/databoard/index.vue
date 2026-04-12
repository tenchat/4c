<!-- 管理端数据大屏 -->
<template>
  <div class="databoard-admin" style="background: #0d1117; min-height: 100vh; padding: 20px;">
    <!-- 页面标题 -->
    <h1 class="databoard-title" style="color: #e6edf3;">管理端数据大屏</h1>

    <!-- 第一行：4个统计卡片 -->
    <el-row :gutter="20" class="mb-4">
      <el-col :span="6">
        <art-stats-card
          title="学生总数"
          :count="stats.totalStudents"
          :description="stats.totalStudents + ' 人'"
          icon="ri:user-line"
          icon-style="bg-blue-500"
        />
      </el-col>
      <el-col :span="6">
        <art-stats-card
          title="企业总数"
          :count="stats.totalCompanies"
          :description="stats.totalCompanies + ' 家'"
          icon="ri:building-line"
          icon-style="bg-green-500"
        />
      </el-col>
      <el-col :span="6">
        <art-stats-card
          title="在招岗位"
          :count="stats.totalJobs"
          :description="stats.totalJobs + ' 个'"
          icon="ri:briefcase-line"
          icon-style="bg-orange-500"
        />
      </el-col>
      <el-col :span="6">
        <art-stats-card
          title="整体就业率"
          :count="stats.overallRate"
          :description="stats.overallRate + '%'"
          icon="ri:trend-charts-line"
          icon-style="bg-red-500"
        />
      </el-col>
    </el-row>

    <!-- 第二行：就业分布环形图 + 全国热力图 -->
    <el-row :gutter="20" class="mb-4">
      <el-col :span="12">
        <art-card-banner title="就业分布" description="已就业/待就业/升学/出国占比">
          <art-ring-chart
            :data="employmentDistribution"
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
        <art-card-banner title="全国就业热力图" description="各省份学生就业分布">
          <art-map-chart
            :map-data="mapData"
            height="300px"
            :loading="chartLoading"
          />
        </art-card-banner>
      </el-col>
    </el-row>

    <!-- 第三行：行业薪资排名条形图 + 学院就业对比图 -->
    <el-row :gutter="20" class="mb-4">
      <el-col :span="12">
        <art-card-banner title="行业薪资排名" description="各行业平均薪资对比">
          <art-h-bar-chart
            :data="industrySalary"
            :x-axis-data="industrySalaryLabels"
            :colors="chartColors"
            height="300px"
            :loading="chartLoading"
          />
        </art-card-banner>
      </el-col>
      <el-col :span="12">
        <art-card-banner title="学院就业对比" description="各学院就业情况对比">
          <art-bar-chart
            :data="collegeEmployment"
            :x-axis-data="collegeLabels"
            :colors="chartColors"
            height="300px"
            :loading="chartLoading"
          />
        </art-card-banner>
      </el-col>
    </el-row>

    <!-- 第四行：趋势折线图 + 最新动态滚动栏 -->
    <el-row :gutter="20" class="mb-4">
      <el-col :span="12">
        <art-card-banner title="就业趋势" description="近5年就业率变化">
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
        <art-card-banner title="最新动态" description="实时就业动态信息">
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
  import { fetchAdminDataboard } from '@/api/admin'
  import { onMounted, ref } from 'vue'
  import type { PieDataItem } from '@/types/component/chart'

  defineOptions({ name: 'AdminDataboard' })

  // 图表颜色配置
  const chartColors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4']

  // 加载状态
  const chartLoading = ref(false)

  // 统计数据
  const stats = ref({
    totalStudents: 0,
    totalCompanies: 0,
    totalJobs: 0,
    overallRate: 0
  })

  // 就业分布数据
  const employmentDistribution = ref<PieDataItem[]>([])

  // 地图数据
  const mapData = ref<any[]>([])

  // 行业薪资数据
  const industrySalary = ref<number[]>([])
  const industrySalaryLabels = ref<string[]>([])

  // 学院就业对比数据
  const collegeEmployment = ref<any[]>([])
  const collegeLabels = ref<string[]>([])

  // 趋势数据
  const trendData = ref<number[]>([])
  const trendLabels = ref<string[]>([])

  // 最新动态
  const newsList = ref<{ time: string; content: string }[]>([])

  // Mock 数据
  const mockData = {
    stats: {
      totalStudents: 12580,
      totalCompanies: 856,
      totalJobs: 3420,
      overallRate: 86.5
    },
    employmentDistribution: [
      { name: '已就业', value: 4500 },
      { name: '待就业', value: 1200 },
      { name: '升学', value: 800 },
      { name: '出国', value: 300 }
    ],
    mapData: [
      { name: '北京', value: 850 },
      { name: '上海', value: 920 },
      { name: '广东', value: 1100 },
      { name: '浙江', value: 780 },
      { name: '江苏', value: 890 },
      { name: '四川', value: 650 },
      { name: '湖北', value: 580 },
      { name: '陕西', value: 520 },
      { name: '湖南', value: 490 },
      { name: '山东', value: 720 }
    ],
    industrySalary: [12500, 11500, 10500, 9500, 8800, 8200, 7800, 7200],
    industrySalaryLabels: ['互联网', '金融', '房地产', '教育', '医疗', '制造', '零售', '服务'],
    collegeEmployment: [
      { name: '计算机学院', data: [92, 88, 95, 91, 94] },
      { name: '经济管理学院', data: [85, 82, 88, 86, 90] },
      { name: '机械工程学院', data: [78, 75, 82, 80, 85] },
      { name: '外国语学院', data: [72, 70, 76, 74, 78] }
    ],
    collegeLabels: ['计算机学院', '经济管理学院', '机械工程学院', '外国语学院', '艺术学院'],
    trendData: [78, 80, 82, 85, 86.5],
    trendLabels: ['2021', '2022', '2023', '2024', '2025'],
    newsList: [
      { time: '2026-03-29', content: '计算机学院张同学成功签约腾讯' },
      { time: '2026-03-28', content: '经济管理学院举办春季招聘会' },
      { time: '2026-03-27', content: '机械工程学院李同学获得出国offer' },
      { time: '2026-03-26', content: '外国语学院王同学成功升学北大' },
      { time: '2026-03-25', content: '校企合作签约仪式成功举行' },
      { time: '2026-03-24', content: '艺术学院举办就业指导讲座' },
      { time: '2026-03-23', content: '计算机学院举办专场招聘会' }
    ]
  }

  // 加载数据
  const loadData = async () => {
    chartLoading.value = true
    try {
      const res: any = await fetchAdminDataboard()
      if (res) {
        // 使用API数据

        if (res.stats) {
          stats.value = {
            totalStudents: res.stats.total_students || 0,
            totalCompanies: res.stats.total_companies || 0,
            totalJobs: res.stats.total_jobs || 0,
            overallRate: res.stats.overall_employment_rate || 0
          }
        }

        if (res.employment_distribution) {
          employmentDistribution.value = res.employment_distribution
        }

        if (res.map_data) {
          mapData.value = res.map_data
        }

        if (res.industry_salary) {
          industrySalary.value = res.industry_salary.values || []
          industrySalaryLabels.value = res.industry_salary.labels || []
        }

        if (res.college_employment) {
          collegeEmployment.value = res.college_employment.data || []
          collegeLabels.value = res.college_employment.labels || []
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
    employmentDistribution.value = mockData.employmentDistribution
    mapData.value = mockData.mapData
    industrySalary.value = mockData.industrySalary
    industrySalaryLabels.value = mockData.industrySalaryLabels
    collegeEmployment.value = mockData.collegeEmployment
    collegeLabels.value = mockData.collegeLabels
    trendData.value = mockData.trendData
    trendLabels.value = mockData.trendLabels
    newsList.value = mockData.newsList
  }

  onMounted(() => {
    loadData()
  })
</script>

<style scoped>
  .databoard-admin {
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
