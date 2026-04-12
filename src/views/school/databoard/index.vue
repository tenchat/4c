<!-- 学校端数据大屏 -->
<template>
  <div class="school-databoard">
    <!-- 顶部标题栏 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">就业数据大屏</h1>
        <span class="page-subtitle">{{ universityName || '加载中...' }}</span>
      </div>
      <div class="header-right">
        <ElSelect
          v-model="selectedYear"
          placeholder="选择年份"
          @change="fetchData"
          style="width: 130px"
        >
          <ElOption :value="undefined" label="全部年份" />
          <ElOption v-for="y in years" :key="y" :value="y" :label="`${y}年`" />
        </ElSelect>
        <span class="current-time">{{ currentTime }}</span>
      </div>
    </div>

    <!-- 数字卡片 -->
    <div class="stat-row">
      <ArtStatsCard
        icon="ri:user-3-line"
        iconStyle="bg-blue-500"
        :count="summary.total_graduates"
        :separator="','"
        description="毕业生总数"
      />
      <ArtStatsCard
        icon="ri:trend-up-line"
        iconStyle="bg-orange-500"
        :count="summary.employment_rate"
        description="总体就业率"
        textColor="#fa8c16"
        suffix="%"
      />
      <ArtStatsCard
        icon="ri:book-open-line"
        iconStyle="bg-green-500"
        :count="summary.further_study_count"
        :separator="','"
        description="升学人数"
      />
      <ArtStatsCard
        icon="ri:file-list-3-line"
        iconStyle="bg-purple-500"
        :count="summary.contract_count"
        :separator="','"
        description="签约人数"
      />
      <ArtStatsCard
        icon="ri:global-line"
        iconStyle="bg-teal-500"
        :count="summary.overseas_count"
        :separator="','"
        description="出国人数"
      />
      <ArtStatsCard
        icon="ri:briefcase-3-line"
        iconStyle="bg-gray-500"
        :count="summary.overseas_rate"
        description="出国率"
        suffix="%"
      />
    </div>

    <!-- 主内容：地图 + 右侧图表 -->
    <div class="main-section">
      <!-- 地图卡片 -->
      <div class="map-panel">
        <div class="panel-title">
          <span>毕业生就业地域分布</span>
        </div>
        <ArtMapChart :mapData="mapData" height="360px" @regionClick="handleProvinceClick" />
      </div>

      <!-- 右侧三个小图表 -->
      <div class="side-panels">
        <!-- 学院就业TOP10（分学历层） -->
        <div class="side-panel-item">
          <div class="panel-title">学院就业TOP10</div>
          <ArtBarChart
            :data="rankingData"
            :xAxisData="rankingXAxisData"
            :showLegend="true"
            barWidth="20%"
          />
        </div>

        <!-- 毕业去向 -->
        <div class="side-panel-item">
          <div class="panel-title">毕业去向</div>
          <ArtRingChart :data="directionData" :radius="['40%', '65%']" legendPosition="bottom" />
        </div>

        <!-- 就业率趋势 -->
        <div class="side-panel-item">
          <div class="panel-title">就业率趋势</div>
          <ArtLineChart
            :data="trendData"
            :xAxisData="trendXAxisData"
            :showAreaColor="true"
            :showLegend="false"
          />
        </div>
      </div>
    </div>

    <!-- 下方图表区 -->
    <div class="chart-section">
      <div class="chart-grid">
        <!-- 学历层次对比 -->
        <div class="chart-panel">
          <div class="panel-title">
            <span>学历层次对比</span>
          </div>
          <ArtBarChart
            :data="degreeData"
            :xAxisData="degreeXAxisData"
            :showLegend="true"
            barWidth="25%"
          />
        </div>

        <!-- 行业分布 -->
        <div class="chart-panel">
          <div class="panel-title">
            <span>行业分布</span>
          </div>
          <ArtRadarChart :indicator="industryIndicator" :data="industryData" />
        </div>

        <!-- 热门岗位TOP5 -->
        <div class="chart-panel">
          <div class="panel-title">
            <span>热门岗位TOP5</span>
          </div>
          <ArtHBarChart :data="jobTitlesBarData" :xAxisData="jobTitlesXAxisData" barWidth="35%" />
        </div>

        <!-- 期望薪资分布 -->
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

        <!-- 热门关键词词云 -->
        <div class="chart-panel">
          <div class="panel-title">
            <span>热门关键词词云</span>
          </div>
          <ArtWordCloud :data="wordCloudData" height="240px" />
        </div>

        <!-- 区域流向分布 -->
        <div class="chart-panel">
          <div class="panel-title">
            <span>区域流向分布</span>
          </div>
          <ArtBarChart
            :data="[{ name: '人数', data: regionalDistribution.map((d: any) => d.value) }]"
            :xAxisData="regionalDistribution.map((d: any) => d.name)"
            :showLegend="false"
            barWidth="40%"
          />
        </div>

        <!-- 专业分布TOP20 -->
        <div class="chart-panel">
          <div class="panel-title">
            <span>专业分布TOP20</span>
          </div>
          <ArtHBarChart :data="majorData" :xAxisData="majorXAxisData" barWidth="30%" />
        </div>

        <!-- 城市偏好分布 -->
        <div class="chart-panel">
          <div class="panel-title">
            <span>城市偏好分布</span>
          </div>
          <ArtBarChart
            :data="cityPreferenceData"
            :xAxisData="cityPreferenceXAxisData"
            :showLegend="false"
            barWidth="35%"
          />
        </div>

        <!-- 紧缺地区TOP5 -->
        <div class="chart-panel">
          <div class="panel-title">
            <span>紧缺地区TOP5</span>
          </div>
          <ArtHBarChart :data="scarceRegionData" :xAxisData="scarceRegionXAxis" barWidth="40%" />
        </div>

        <!-- 紧缺行业TOP5 -->
        <div class="chart-panel">
          <div class="panel-title">
            <span>紧缺行业TOP5</span>
          </div>
          <ArtHBarChart
            :data="scarceIndustryData"
            :xAxisData="scarceIndustryXAxis"
            barWidth="40%"
          />
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-mask">
      <div class="loading-spinner" />
      <span>数据加载中...</span>
    </div>

    <!-- 省份详情弹窗 -->
    <ProvinceDetailModal
      v-model="provinceModalVisible"
      :province-name="selectedProvince"
      :year="selectedYear"
    />
  </div>
</template>

<script setup lang="ts">
  import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
  import { fetchSchoolDataboard, fetchSchoolProfile, fetchWordCloudData, fetchJobTitlesStats } from '@/api/school'
  import ArtLineChart from '@/components/core/charts/art-line-chart/index.vue'
  import ArtBarChart from '@/components/core/charts/art-bar-chart/index.vue'
  import ArtHBarChart from '@/components/core/charts/art-h-bar-chart/index.vue'
  import ArtRingChart from '@/components/core/charts/art-ring-chart/index.vue'
  import ArtRadarChart from '@/components/core/charts/art-radar-chart/index.vue'
  import ArtMapChart from '@/components/core/charts/art-map-chart/index.vue'
  import ArtWordCloud from '@/components/core/charts/art-word-cloud/index.vue'
  import ArtStatsCard from '@/components/core/cards/art-stats-card/index.vue'
  import ProvinceDetailModal from '@/components/school/databoard/ProvinceDetailModal.vue'

  defineOptions({ name: 'SchoolDataboard' })

  const years = [2022, 2023, 2024, 2025, 2026]
  const selectedYear = ref<number | undefined>(undefined)
  const currentTime = ref('')
  const universityName = ref('')
  let timeTimer: number

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

  const loading = ref(false)

  const summary = ref({
    total_graduates: 0,
    employment_rate: 0,
    further_study_count: 0,
    contract_count: 0,
    overseas_count: 0,
    overseas_rate: 0
  })
  const employment_trend = ref<any[]>([])
  const college_ranking = ref<any[]>([])
  const direction_distribution = ref<any[]>([])
  const degree_comparison = ref<any>({})
  const industry_radar = ref<any[]>([])
  const scarce_talent = ref<any>({})
  const salary_distribution = ref<any[]>([])
  const map_data = ref<any[]>([])
  const regional_distribution = ref<any[]>([])
  const major_distribution = ref<any[]>([])
  const city_preference = ref<any[]>([])

  // 省份弹窗
  const provinceModalVisible = ref(false)
  const selectedProvince = ref('')

  const handleProvinceClick = (region: { name: string; adcode: string; level: string }) => {
    if (region.level === 'province') {
      selectedProvince.value = region.name
      provinceModalVisible.value = true
    }
  }

  // 就业率趋势
  const trendData = computed(() => [
    { name: '就业率', data: employment_trend.value.map((d: any) => d.employment_rate) }
  ])
  const trendXAxisData = computed(() => employment_trend.value.map((d: any) => d.year))

  // 学院就业TOP10（按就业率从高到低排序，分学历层）
  const rankingData = computed(() => {
    const sorted = [...college_ranking.value].sort((a, b) => b.employment_rate - a.employment_rate)
    const sliced = sorted.slice(0, 10)
    return [
      { name: '博士就业数', data: sliced.map((d: any) => d.doctoral?.employed || 0) },
      { name: '硕士就业数', data: sliced.map((d: any) => d.master?.employed || 0) },
      { name: '本科就业数', data: sliced.map((d: any) => d.bachelor?.employed || 0) },
    ]
  })
  const rankingXAxisData = computed(() => {
    const sorted = [...college_ranking.value].sort((a, b) => b.employment_rate - a.employment_rate)
    return sorted.slice(0, 10).map((d: any) => d.college_name)
  })

  // 毕业去向分布
  const directionData = computed(() =>
    direction_distribution.value.map((d: any) => ({ name: d.name, value: d.value }))
  )

  // 学历层次对比（毕业生数、就业数、升学数）
  const degreeData = computed(() => {
    const degrees = ['doctoral', 'master', 'bachelor']
    return [
      {
        name: '毕业生数',
        data: degrees.map((d) => degree_comparison.value[d]?.graduate_nums || 0)
      },
      {
        name: '就业数',
        data: degrees.map((d) => degree_comparison.value[d]?.employed_nums || 0)
      },
      {
        name: '升学数',
        data: degrees.map((d) => degree_comparison.value[d]?.further_study_nums || 0)
      }
    ]
  })
  const degreeXAxisData = ['博士', '硕士', '本科']

  // 行业分布
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
    '互联网': '互联网/IT',
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
    // 归一化后的中文行业 (dashboard雷达图，来自backend normalize_industry)
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

  const industryIndicator = computed(() => {
    const industries = industry_radar.value.slice(0, 8)
    const maxCount = Math.max(...industries.map((d: any) => d.count), 100)
    return industries.map((d: any) => ({
      name: INDUSTRY_MAP[d.industry] || d.industry,
      max: maxCount
    }))
  })
  const industryData = computed(() => [
    {
      name: '行业分布',
      value: industry_radar.value.slice(0, 8).map((d: any) => d.count)
    }
  ])

  const salaryData = computed(() => salary_distribution.value)
  const mapData = computed(() => map_data.value)
  const regionalDistribution = computed(() =>
    regional_distribution.value.map((d: any) => ({ name: d.name, value: d.value }))
  )

  // 专业分布TOP20
  const majorData = computed(() => [
    { name: '人数', data: major_distribution.value.map((d: any) => d.count) }
  ])
  const majorXAxisData = computed(() => major_distribution.value.map((d: any) => d.major))

  // 城市偏好分布
  const cityPreferenceData = computed(() => [
    { name: '人数', data: city_preference.value.map((d: any) => d.count) }
  ])
  const cityPreferenceXAxisData = computed(() => city_preference.value.map((d: any) => d.city))

  // 紧缺人才分析
  const scarceTalentRegions = computed(() =>
    (scarce_talent.value.summary?.top_regions || []).slice(0, 5)
  )
  const scarceTalentIndustries = computed(() =>
    (scarce_talent.value.summary?.top_industries || []).slice(0, 5)
  )
  const scarceRegionData = computed(() => [
    { name: '紧缺地区', data: scarceTalentRegions.value.map((r: any) => r.value) }
  ])
  const scarceRegionXAxis = computed(() => scarceTalentRegions.value.map((r: any) => r.name))
  const scarceIndustryData = computed(() => [
    { name: '紧缺行业', data: scarceTalentIndustries.value.map((i: any) => i.value) }
  ])
  const scarceIndustryXAxis = computed(() => scarceTalentIndustries.value.map((i: any) => i.name))

  // 热门岗位TOP5（从job_descriptions获取）
  const jobTitlesData = ref<any[]>([])
  const jobTitlesXAxisData = computed(() => jobTitlesData.value.map((d: any) => d.title))
  const jobTitlesBarData = computed(() => [{ name: '岗位数', data: jobTitlesData.value.map((d: any) => d.count) }])

  // 词云数据
  const wordCloudData = ref<any[]>([])

  const fetchData = async () => {
    loading.value = true
    try {
      const res: any = await fetchSchoolDataboard(selectedYear.value)
      if (res) {
        summary.value = res.summary || summary.value
        employment_trend.value = res.employment_trend || []
        college_ranking.value = res.college_ranking || []
        direction_distribution.value = res.direction_distribution || []
        degree_comparison.value = res.degree_comparison || {}
        industry_radar.value = res.industry_radar || []
        scarce_talent.value = res.scarce_talent || {}
        salary_distribution.value = res.salary_distribution || []
        map_data.value = res.map_data || res.regional_flow?.distribution || []
        regional_distribution.value = res.regional_flow?.distribution || []
        major_distribution.value = res.major_distribution || []
        city_preference.value = res.city_preference || []
      }
    } catch (err) {
      console.error('获取数据失败:', err)
    } finally {
      loading.value = false
    }
  }

  // 获取词云数据和岗位统计数据
  const fetchWordCloudAndJobTitles = async () => {
    try {
      const [wordCloudRes, jobTitlesRes]: any = await Promise.all([
        fetchWordCloudData(),
        fetchJobTitlesStats()
      ])
      if (wordCloudRes) {
        wordCloudData.value = wordCloudRes || []
      }
      if (jobTitlesRes) {
        jobTitlesData.value = jobTitlesRes || []
      }
    } catch (err) {
      console.error('获取词云/岗位数据失败:', err)
    }
  }

  onMounted(async () => {
    updateTime()
    timeTimer = window.setInterval(updateTime, 1000)
    // 获取学校信息
    try {
      const profileRes: any = await fetchSchoolProfile()
      console.log('学校信息响应:', profileRes)
      if (profileRes?.name) {
        universityName.value = profileRes.name
      } else {
        console.warn('学校名称未找到，响应结构:', profileRes)
      }
    } catch (err) {
      console.error('获取学校信息失败:', err)
    }
    fetchData()
    fetchWordCloudAndJobTitles()
  })

  onBeforeUnmount(() => {
    if (timeTimer) clearInterval(timeTimer)
  })
</script>

<style lang="scss" scoped>
  .school-databoard {
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

  // 数字卡片行
  .stat-row {
    display: flex;
    gap: 12px;
    padding: 20px 32px;

    > :deep(.art-card) {
      flex: 1;
      min-width: 0;
    }
  }

  // 主内容区
  .main-section {
    display: flex;
    gap: 16px;
    padding: 0 32px;
    margin-bottom: 16px;

    .map-panel {
      flex: 3;
      background: #fff;
      border-radius: 10px;
      border: 1px solid #eee;
      padding: 16px;
      overflow: hidden;
    }

    .side-panels {
      flex: 2;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .side-panel-item {
      background: #fff;
      border-radius: 10px;
      border: 1px solid #eee;
      padding: 14px 16px;
      min-height: 0;

      .panel-title {
        margin-bottom: 8px;
      }
    }
  }

  // 图表标题
  .panel-title {
    font-size: 13px;
    font-weight: 500;
    color: #1a1a1a;
    margin-bottom: 10px;
    padding-bottom: 8px;
    border-bottom: 1px solid #f0f0f0;
  }

  // 下方图表区
  .chart-section {
    padding: 0 32px;
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
    transition: box-shadow 0.2s ease;
    min-height: 240px;

    &:hover {
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
    }

    .panel-title {
      margin-bottom: 10px;
    }
  }

  // 紧缺度列表
  .scarce-list {
    padding-top: 4px;
    max-height: 200px;
    overflow-y: auto;

    &.is-scrollable {
      scrollbar-width: thin;
      scrollbar-color: #d9d9d9 transparent;

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

    .empty-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 24px 0;
      color: #bfbfbf;
      font-size: 13px;
    }

    .scarce-item {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 10px;

      &:last-child {
        margin-bottom: 0;
      }

      .scarce-rank {
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
        font-weight: 600;
      }

      .scarce-name {
        width: 70px;
        font-size: 12px;
        color: #3a3a3a;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        flex-shrink: 0;
      }

      .scarce-bar {
        flex: 1;
      }

      .scarce-value {
        font-size: 12px;
        color: #8c8c8c;
        width: 32px;
        text-align: right;
        flex-shrink: 0;
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
      }
    }
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
    .main-section {
      flex-direction: column;
    }

    .map-panel {
      flex: none;
    }

    .side-panels {
      flex-direction: row;
      flex-wrap: wrap;

      .side-panel-item {
        flex: 1 1 calc(50% - 6px);
        min-height: 180px;
      }
    }

    .chart-grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }

  @media (max-width: 768px) {
    .stat-row {
      flex-wrap: wrap;
      gap: 8px;
      padding: 16px;
    }

    .main-section {
      padding: 0 16px;
    }

    .side-panels {
      flex-direction: column;

      .side-panel-item {
        flex: none;
        min-height: 180px;
      }
    }

    .chart-section {
      padding: 0 16px;
    }

    .chart-grid {
      grid-template-columns: 1fr;
    }

    .page-header {
      padding: 12px 16px;
    }
  }
</style>
