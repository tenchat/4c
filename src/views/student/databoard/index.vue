<!-- 学生就业数据大屏 -->
<template>
  <div class="student-databoard">
    <!-- 顶部标题栏 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">就业数据大屏</h1>
        <span class="page-subtitle">2026就业全景分析</span>
      </div>
      <div class="header-right">
        <span class="current-time">{{ currentTime }}</span>
      </div>
    </div>

    <!-- 主内容：3列×3行 Grid -->
    <div class="chart-section">
      <div class="chart-grid">
        <!-- 第1行 -->
        <!-- ① 毕业生流向分布 - 环形图 -->
        <div class="chart-panel">
          <div class="panel-title">
            <span>毕业生流向分布</span>
          </div>
          <ArtRingChart :data="directionData" :radius="['40%', '65%']" legendPosition="bottom" />
        </div>

        <!-- ② 行业热门度TOP10 - 词云 -->
        <div class="chart-panel">
          <div class="panel-title">
            <span>行业热门度TOP10</span>
          </div>
          <ArtWordCloud :data="industryHotData" height="240px" />
        </div>

        <!-- ③ 城市就业热度TOP10 - 水平柱状图 -->
        <div class="chart-panel">
          <div class="panel-title">
            <span>城市就业热度TOP10</span>
          </div>
          <ArtHBarChart :data="cityHotData" :xAxisData="cityHotXAxisData" barWidth="40%" />
        </div>

        <!-- 第2行 -->
        <!-- ④ 期望薪资分布 - 直方图 -->
        <div class="chart-panel">
          <div class="panel-title">
            <span>期望薪资分布</span>
          </div>
          <ArtBarChart
            :data="[{ name: '人数', data: salaryData.map((d: any) => d.count) }]"
            :xAxisData="salaryData.map((d: any) => d.range)"
            :showLegend="false"
            barWidth="32%"
          />
        </div>

        <!-- ⑤ 行业薪资对比 - 雷达图 -->
        <div class="chart-panel">
          <div class="panel-title">
            <span>行业薪资对比</span>
          </div>
          <ArtRadarChart :indicator="industrySalaryIndicator" :data="industrySalaryData" />
        </div>

        <!-- ⑥ 紧缺岗位推荐 - 滚动列表 -->
        <div class="chart-panel">
          <div class="panel-title">
            <span>紧缺岗位推荐</span>
          </div>
          <div class="scarce-list">
            <div v-for="(job, idx) in scarceJobs" :key="idx" class="scarce-item">
              <div class="scarce-rank">{{ idx + 1 }}</div>
              <div class="scarce-info">
                <div class="scarce-title">{{ job.job_title }}</div>
                <div class="scarce-detail">
                  <span class="tag-industry">{{ job.industry }}</span>
                  <span class="tag-region">{{ job.region }}</span>
                </div>
              </div>
              <div class="scarce-level" :class="getLevelClass(job.level)">
                {{ job.level.toFixed(1) }}
              </div>
            </div>
            <div v-if="scarceJobs.length === 0" class="empty-state">
              <span>暂无数据</span>
            </div>
          </div>
        </div>

        <!-- 第3行 -->
        <!-- ⑦ 实习价值分析 - 对比柱状图 -->
        <div class="chart-panel">
          <div class="panel-title">
            <span>实习价值分析</span>
          </div>
          <ArtBarChart
            :data="internshipData"
            :xAxisData="internshipXAxisData"
            :showLegend="true"
            barWidth="40%"
          />
        </div>

        <!-- ⑧ 学历与就业方向 - 堆叠柱状图 -->
        <div class="chart-panel">
          <div class="panel-title">
            <span>学历与就业方向</span>
          </div>
          <ArtBarChart
            :data="degreeDirectionData"
            :xAxisData="degreeDirectionXAxisData"
            :showLegend="true"
            barWidth="50%"
            :stack="true"
          />
        </div>

        <!-- 第4行（扩展） -->
        <!-- ⑨ 专业就业率 - 柱状图 -->
        <div class="chart-panel">
          <div class="panel-title">
            <span>专业就业率</span>
          </div>
          <ArtBarChart
            :data="[{ name: '就业率(%)', data: majorEmployment.map((d: any) => d.rate) }]"
            :xAxisData="majorEmployment.map((d: any) => d.college)"
            :showLegend="false"
            barWidth="40%"
          />
        </div>

        <!-- ⑩ 紧缺行业分布 - 饼图 -->
        <div class="chart-panel">
          <div class="panel-title">
            <span>紧缺行业分布</span>
          </div>
          <ArtRingChart
            :data="scarceIndustryData"
            :radius="['40%', '65%']"
            legendPosition="bottom"
          />
        </div>

        <!-- ⑪ 紧缺岗位薪资 - 柱状图 -->
        <div class="chart-panel">
          <div class="panel-title">
            <span>紧缺岗位薪资分布</span>
          </div>
          <ArtBarChart
            :data="[{ name: '平均薪资(元)', data: scarceJobs.map((d: any) => d.salary || 0) }]"
            :xAxisData="scarceJobs.map((d: any) => d.job_title)"
            :showLegend="false"
            barWidth="50%"
          />
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-mask">
      <div class="loading-spinner" />
      <span>数据加载中...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
  import { fetchStudentDataboard } from '@/api/student'
  import ArtRingChart from '@/components/core/charts/art-ring-chart/index.vue'
  import ArtWordCloud from '@/components/core/charts/art-word-cloud/index.vue'
  import ArtHBarChart from '@/components/core/charts/art-h-bar-chart/index.vue'
  import ArtBarChart from '@/components/core/charts/art-bar-chart/index.vue'
  import ArtRadarChart from '@/components/core/charts/art-radar-chart/index.vue'

  defineOptions({ name: 'StudentDataboard' })

  const currentTime = ref('')
  const loading = ref(false)
  let timeTimer: number

  // 数据状态
  const direction_distribution = ref<any[]>([])
  const industry_hot = ref<any[]>([])
  const city_hot = ref<any[]>([])
  const salary_distribution = ref<any[]>([])
  const industry_salary_radar = ref<any[]>([])
  const scarce_jobs = ref<any[]>([])
  const major_employment = ref<any[]>([])
  const internship_value = ref<any[]>([])
  const degree_direction = ref<any[]>([])

  const updateTime = () => {
    const now = new Date()
    currentTime.value = now.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  // ① 毕业生流向分布
  const directionData = computed(() =>
    direction_distribution.value.map((d: any) => ({ name: d.name, value: d.value }))
  )

  // ② 行业热门度TOP10
  const industryHotData = computed(() =>
    industry_hot.value.map((d: any) => ({ name: d.name, value: d.value }))
  )

  // ③ 城市就业热度TOP10
  const cityHotData = computed(() => [
    { name: '人数', data: city_hot.value.map((d: any) => d.value) }
  ])
  const cityHotXAxisData = computed(() => city_hot.value.map((d: any) => d.name))

  // ④ 期望薪资分布
  const salaryData = computed(() => salary_distribution.value)

  // ⑤ 行业薪资对比
  const industrySalaryIndicator = computed(() => {
    const data = industry_salary_radar.value.slice(0, 8)
    const maxSalary = Math.max(...data.map((d: any) => d.salary), 10000)
    return data.map((d: any) => ({
      name: d.industry,
      max: maxSalary
    }))
  })
  const industrySalaryData = computed(() => [
    {
      name: '平均薪资',
      value: industry_salary_radar.value.slice(0, 8).map((d: any) => d.salary)
    }
  ])

  // ⑥ 紧缺岗位推荐
  const scarceJobs = computed(() => scarce_jobs.value)

  const getLevelClass = (level: number) => {
    if (level >= 8) return 'level-high'
    if (level >= 5) return 'level-medium'
    return 'level-low'
  }

  // ⑦ 实习价值分析
  const internshipData = computed(() => {
    if (internship_value.value.length === 0) return []
    return [
      { name: '已就业', data: internship_value.value.map((d: any) => d.employed) },
      { name: '未就业', data: internship_value.value.map((d: any) => Math.max(0, d.total - d.employed)) }
    ]
  })
  const internshipXAxisData = computed(() =>
    internship_value.value.map((d: any) => d.name)
  )

  // ⑧ 学历与就业方向
  const degreeDirectionData = computed(() => {
    if (degree_direction.value.length === 0) return []
    return [
      { name: '待就业', data: degree_direction.value.map((d: any) => d['待就业'] || 0) },
      { name: '已就业', data: degree_direction.value.map((d: any) => d['已就业'] || 0) },
      { name: '升学', data: degree_direction.value.map((d: any) => d['升学'] || 0) },
      { name: '出国', data: degree_direction.value.map((d: any) => d['出国'] || 0) }
    ]
  })
  const degreeDirectionXAxisData = computed(() =>
    degree_direction.value.map((d: any) => d.degree)
  )

  // ⑨ 专业就业率
  const majorEmployment = computed(() => major_employment.value)

  // ⑩ 紧缺行业分布
  const scarceIndustryData = computed(() => {
    const counter: Record<string, number> = {}
    scarce_jobs.value.forEach((job: any) => {
      const ind = job.industry || '其他'
      counter[ind] = (counter[ind] || 0) + 1
    })
    return Object.entries(counter).map(([name, value]) => ({ name, value }))
  })

  // 获取数据
  const fetchData = async () => {
    loading.value = true
    try {
      const res: any = await fetchStudentDataboard()
      if (res) {
        direction_distribution.value = res.direction_distribution || []
        industry_hot.value = res.industry_hot || []
        city_hot.value = res.city_hot || []
        salary_distribution.value = res.salary_distribution || []
        industry_salary_radar.value = res.industry_salary_radar || []
        scarce_jobs.value = res.scarce_jobs || []
        major_employment.value = res.major_employment || []
        internship_value.value = res.internship_value || []
        degree_direction.value = res.degree_direction || []
      }
    } catch (err) {
      console.error('获取数据失败:', err)
    } finally {
      loading.value = false
    }
  }

  onMounted(() => {
    updateTime()
    timeTimer = window.setInterval(updateTime, 1000)
    fetchData()
  })

  onBeforeUnmount(() => {
    if (timeTimer) clearInterval(timeTimer)
  })
</script>

<style lang="scss" scoped>
  .student-databoard {
    min-height: 100vh;
    background: #f0f2f5;
    padding-bottom: 24px;
  }

  // 顶部标题栏
  .page-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 32px;
    background: #fff;
    border-bottom: 1px solid #e8e8e8;

    .header-left {
      display: flex;
      align-items: baseline;
      gap: 10px;

      .page-title {
        font-size: 18px;
        font-weight: 600;
        color: #1a1a1a;
        margin: 0;
      }

      .page-subtitle {
        font-size: 13px;
        color: #8c8c8c;
      }
    }

    .header-right {
      display: flex;
      align-items: center;
      gap: 16px;

      .current-time {
        font-size: 13px;
        color: #8c8c8c;
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
      }
    }
  }

  // 图表区域
  .chart-section {
    padding: 20px 32px;
  }

  .chart-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
  }

  .chart-panel {
    background: #fff;
    border-radius: 10px;
    border: 1px solid #eee;
    padding: 16px;
    min-height: 280px;
    transition: box-shadow 0.2s ease;

    &:hover {
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
    }

    .panel-title {
      font-size: 13px;
      font-weight: 500;
      color: #1a1a1a;
      margin-bottom: 10px;
      padding-bottom: 8px;
      border-bottom: 1px solid #f0f0f0;
    }
  }

  // 紧缺列表
  .scarce-list {
    padding-top: 4px;
    max-height: 220px;
    overflow-y: auto;

    &::-webkit-scrollbar {
      width: 4px;
    }

    &::-webkit-scrollbar-thumb {
      background: #d9d9d9;
      border-radius: 2px;
    }

    &::-webkit-scrollbar-track {
      background: transparent;
    }
  }

  .scarce-item {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;

    &:last-child {
      margin-bottom: 0;
    }
  }

  .scarce-rank {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: #1677ff;
    color: #fff;
    font-size: 11px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    font-weight: 600;
  }

  .scarce-info {
    flex: 1;
    min-width: 0;
  }

  .scarce-title {
    font-size: 13px;
    color: #3a3a3a;
    font-weight: 500;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .scarce-detail {
    display: flex;
    gap: 6px;
    margin-top: 4px;
  }

  .tag-industry,
  .tag-region {
    font-size: 10px;
    padding: 1px 6px;
    border-radius: 2px;
    background: #f0f0f0;
    color: #666;
  }

  .tag-industry {
    background: #e6f4ff;
    color: #1677ff;
  }

  .scarce-level {
    font-size: 14px;
    font-weight: 600;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    padding: 2px 8px;
    border-radius: 4px;

    &.level-high {
      color: #ff4d4f;
      background: #fff2f0;
    }

    &.level-medium {
      color: #fa8c16;
      background: #fff7e6;
    }

    &.level-low {
      color: #52c41a;
      background: #f6ffed;
    }
  }

  // 空状态
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 40px 0;
    color: #bfbfbf;
    font-size: 13px;
  }

  // 加载状态
  .loading-mask {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.9);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 12px;
    color: #8c8c8c;
    z-index: 1000;
    backdrop-filter: blur(4px);

    .loading-spinner {
      width: 32px;
      height: 32px;
      border: 3px solid #e8e8e8;
      border-top-color: #1677ff;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  // 响应式
  @media (max-width: 1200px) {
    .chart-grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }

  @media (max-width: 768px) {
    .chart-section {
      padding: 16px;
    }

    .chart-grid {
      grid-template-columns: 1fr;
    }

    .page-header {
      padding: 12px 16px;
    }
  }
</style>
