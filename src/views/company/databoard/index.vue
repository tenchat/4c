<!-- 企业数据大屏 -->
<template>
  <div class="company-databoard">
    <!-- 顶部标题栏 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">企业数据大屏</h1>
        <span class="page-subtitle">{{ companyName || '加载中...' }}</span>
      </div>
      <div class="header-right">
        <ElSelect
          v-model="selectedYear"
          placeholder="选择年份"
          clearable
          @change="fetchData"
          style="width: 130px"
        >
          <ElOption v-for="y in years" :key="y" :value="y" :label="`${y}年`" />
        </ElSelect>
        <span class="current-time">{{ currentTime }}</span>
      </div>
    </div>

    <!-- 数字卡片 -->
    <div class="stat-row">
      <ArtStatsCard
        icon="ri:building-2-line"
        iconStyle="bg-blue-500"
        :count="summary.total_companies"
        :separator="','"
        description="平台企业总数"
      />
      <ArtStatsCard
        icon="ri:shield-check-line"
        iconStyle="bg-green-500"
        :count="summary.verified_companies"
        :separator="','"
        description="已认证企业"
      />
      <ArtStatsCard
        icon="ri:briefcase-3-line"
        iconStyle="bg-orange-500"
        :count="summary.active_jobs"
        :separator="','"
        description="在招岗位总数"
      />
      <ArtStatsCard
        icon="ri:user-3-line"
        iconStyle="bg-purple-500"
        :count="summary.total_graduates"
        :separator="','"
        description="毕业生总数"
      />
    </div>

    <!-- 主内容：地图 -->
    <div class="main-section">
      <!-- 地图卡片 -->
      <div class="map-panel">
        <div class="panel-title">
          <span>毕业生就业地域分布</span>
        </div>
        <ArtMapChart :mapData="mapData" height="360px" @regionClick="handleProvinceClick" />
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
  import {
    fetchEnterpriseDataboard,
    fetchEnterpriseWordCloud,
    fetchEnterpriseJobTitles,
    fetchCompanyProfile
  } from '@/api/company'
  import ArtBarChart from '@/components/core/charts/art-bar-chart/index.vue'
  import ArtHBarChart from '@/components/core/charts/art-h-bar-chart/index.vue'
  import ArtRadarChart from '@/components/core/charts/art-radar-chart/index.vue'
  import ArtMapChart from '@/components/core/charts/art-map-chart/index.vue'
  import ArtWordCloud from '@/components/core/charts/art-word-cloud/index.vue'
  import ArtStatsCard from '@/components/core/cards/art-stats-card/index.vue'
  import ProvinceDetailModal from '@/components/school/dashboard/ProvinceDetailModal.vue'

  defineOptions({ name: 'CompanyDataboard' })

  const years = [2022, 2023, 2024, 2025, 2026]
  const selectedYear = ref<number | undefined>(undefined)
  const currentTime = ref('')
  const companyName = ref('')
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
    total_companies: 0,
    verified_companies: 0,
    active_jobs: 0,
    total_graduates: 0
  })

  // 后端返回的原始数据
  const rawData = ref<any>({})

  // 省份弹窗
  const provinceModalVisible = ref(false)
  const selectedProvince = ref('')

  const handleProvinceClick = (region: { name: string; adcode: string; level: string }) => {
    if (region.level === 'province') {
      selectedProvince.value = region.name
      provinceModalVisible.value = true
    }
  }

  // 地图数据
  const mapData = computed(() => rawData.value.map_data || [])

  // 学历层次对比（毕业生数、就业数、升学数）
  const degreeData = computed(() => {
    const deg = rawData.value.degree_comparison || {}
    const degrees = ['doctoral', 'master', 'bachelor']
    return [
      {
        name: '毕业生数',
        data: degrees.map((d) => deg[d]?.graduate_nums || 0)
      },
      {
        name: '就业数',
        data: degrees.map((d) => deg[d]?.employed_nums || 0)
      },
      {
        name: '升学数',
        data: degrees.map((d) => deg[d]?.further_study_nums || 0)
      }
    ]
  })
  const degreeXAxisData = ['博士', '硕士', '本科']

  // 行业分布（雷达图）
  const INDUSTRY_MAP: Record<string, string> = {
    人工智能: '人工智能',
    金融: '金融',
    制造业: '制造业',
    互联网: '互联网',
    医疗健康: '医疗健康',
    教育: '教育',
    房地产: '房地产',
    交通运输: '交通运输',
    能源: '能源',
    文化传媒: '文化传媒',
    电子信息: '电子信息',
    建筑: '建筑',
    法律: '法律',
    消费零售: '消费零售',
    农林牧渔: '农林牧渔',
    军工: '军工',
    其他: '其他'
  }

  const industryIndicator = computed(() => {
    const industries = rawData.value.industry_radar?.slice(0, 8) || []
    const maxCount = Math.max(...industries.map((d: any) => d.count), 100)
    return industries.map((d: any) => ({
      name: INDUSTRY_MAP[d.industry] || d.industry,
      max: maxCount
    }))
  })
  const industryData = computed(() => [
    {
      name: '行业分布',
      value: (rawData.value.industry_radar?.slice(0, 8) || []).map((d: any) => d.count)
    }
  ])

  // 区域流向分布
  const regionalDistribution = computed(() =>
    (rawData.value.regional_flow?.distribution || []).map((d: any) => ({
      name: d.name,
      value: d.value
    }))
  )

  // 专业分布TOP20
  const majorData = computed(() => [
    { name: '人数', data: (rawData.value.major_distribution || []).map((d: any) => d.count) }
  ])
  const majorXAxisData = computed(() =>
    (rawData.value.major_distribution || []).map((d: any) => d.major)
  )

  // 城市偏好分布
  const cityPreferenceData = computed(() => [
    { name: '人数', data: (rawData.value.city_preference || []).map((d: any) => d.count) }
  ])
  const cityPreferenceXAxisData = computed(() =>
    (rawData.value.city_preference || []).map((d: any) => d.city)
  )

  // 紧缺人才分析
  const scarceTalentRegions = computed(() =>
    ((rawData.value.scarce_talent?.summary as any)?.top_regions || []).slice(0, 5)
  )
  const scarceTalentIndustries = computed(() =>
    ((rawData.value.scarce_talent?.summary as any)?.top_industries || []).slice(0, 5)
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
  const jobTitlesBarData = computed(() => [
    { name: '岗位数', data: jobTitlesData.value.map((d: any) => d.count) }
  ])

  // 词云数据
  const wordCloudData = ref<any[]>([])

  const fetchData = async () => {
    loading.value = true
    try {
      const res: any = await fetchEnterpriseDataboard(selectedYear.value)
      const data = res?.data || res
      if (data) {
        rawData.value = data
        summary.value = {
          total_companies: data.summary?.total_companies || 0,
          verified_companies: data.summary?.verified_companies || 0,
          active_jobs: data.summary?.active_jobs || 0,
          total_graduates: data.summary?.total_graduates || 0
        }
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
        fetchEnterpriseWordCloud(),
        fetchEnterpriseJobTitles()
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
    // 获取企业信息
    try {
      const profileRes: any = await fetchCompanyProfile()
      if (profileRes?.company_name) {
        companyName.value = profileRes.company_name
      }
    } catch (err) {
      console.error('获取企业信息失败:', err)
    }
    fetchData()
    fetchWordCloudAndJobTitles()
  })

  onBeforeUnmount(() => {
    if (timeTimer) clearInterval(timeTimer)
  })
</script>

<style lang="scss" scoped>
  .company-databoard {
    min-height: 100vh;
    background: #f0f2f5;
    padding-bottom: 24px;
  }

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

  .stat-row {
    display: flex;
    gap: 12px;
    padding: 20px 32px;

    > :deep(.art-card) {
      flex: 1;
      min-width: 0;
    }
  }

  .main-section {
    display: flex;
    gap: 16px;
    padding: 0 32px;
    margin-bottom: 16px;

    .map-panel {
      flex: 1;
      background: #fff;
      border-radius: 10px;
      border: 1px solid #eee;
      padding: 16px;
      overflow: hidden;
    }
  }

  .panel-title {
    font-size: 13px;
    font-weight: 500;
    color: #1a1a1a;
    margin-bottom: 10px;
    padding-bottom: 8px;
    border-bottom: 1px solid #f0f0f0;
  }

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

  @media (max-width: 1200px) {
    .main-section {
      flex-direction: column;
    }

    .map-panel {
      flex: none;
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
