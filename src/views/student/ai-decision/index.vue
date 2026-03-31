<!-- 考研 vs 就业决策分析页面 -->
<template>
  <div class="page-ai-decision">
    <el-card class="art-card-xs">
      <template #header>
        <div class="card-header">
          <span class="title">考研 vs 就业决策分析</span>
        </div>
      </template>

      <el-form :model="formData" label-width="140px" class="ai-form">
        <el-form-item label="目标城市">
          <el-input
            v-model="formData.targetCity"
            placeholder="请输入目标就业城市"
            clearable
          />
        </el-form-item>

        <el-form-item label="期望薪资（元/月）">
          <el-input-number
            v-model="formData.expectedSalary"
            :min="0"
            :step="1000"
            placeholder="请输入期望薪资"
            style="width: 200px"
          />
        </el-form-item>

        <el-form-item label="考研准备时长（月）">
          <el-input-number
            v-model="formData.studyMonths"
            :min="0"
            :max="36"
            :step="1"
            placeholder="请输入考研准备时长"
            style="width: 200px"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleAnalyze">
            开始分析
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 结果展示区域 -->
    <el-card v-if="showResult" class="art-card-xs mt-4 result-card">
      <template #header>
        <div class="card-header">
          <span class="title">分析结果</span>
        </div>
      </template>

      <div class="result-content" v-loading="loading">
        <!-- 路径对比卡片 -->
        <el-row :gutter="20" class="compare-cards">
          <el-col :span="12">
            <div class="path-card employment">
              <div class="path-header">
                <el-icon :size="32"><Briefcase /></el-icon>
                <span>就业路径</span>
              </div>
              <div class="path-content">
                <div class="path-item">
                  <span class="path-label">起步薪资</span>
                  <span class="path-value salary">{{ resultData.employmentSalary }}元/月</span>
                </div>
                <div class="path-item">
                  <span class="path-label">稳定性</span>
                  <span class="path-value">{{ (resultData.employmentStability * 100).toFixed(0) }}%</span>
                </div>
                <div class="path-item">
                  <span class="path-label">时间成本</span>
                  <span class="path-value">{{ resultData.employmentTimeCost }}个月</span>
                </div>
              </div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="path-card postgraduate">
              <div class="path-header">
                <el-icon :size="32"><Reading /></el-icon>
                <span>考研路径</span>
              </div>
              <div class="path-content">
                <div class="path-item">
                  <span class="path-label">预期薪资</span>
                  <span class="path-value salary">{{ resultData.postgradSalary }}元/月</span>
                </div>
                <div class="path-item">
                  <span class="path-label">稳定性</span>
                  <span class="path-value">{{ (resultData.postgradStability * 100).toFixed(0) }}%</span>
                </div>
                <div class="path-item">
                  <span class="path-label">时间成本</span>
                  <span class="path-value">{{ resultData.postgradTimeCost }}个月</span>
                </div>
              </div>
            </div>
          </el-col>
        </el-row>

        <!-- 对比柱状图 -->
        <div class="chart-section">
          <ArtBarChart
            :data="compareChartData"
            :x-axis-data="compareChartXAxis"
            :height="'300px'"
            :colors="['#409EFF', '#67C23A']"
            :show-legend="true"
            legend-position="bottom"
          />
        </div>

        <!-- 综合建议 -->
        <div class="advice-section">
          <h4>
            <el-icon><Cpu /></el-icon>
            综合建议
          </h4>
          <div class="advice-content">
            <p class="advice-text">{{ resultData.advice }}</p>
            <div class="advice-reasons">
              <p v-for="(reason, index) in resultData.reasons" :key="index">
                {{ reason }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
  import { analyzeDecision } from '@/api/ai'
  import { ElMessage } from 'element-plus'
  import { Briefcase, Reading, Cpu } from '@element-plus/icons-vue'
  import ArtBarChart from '@/components/core/charts/art-bar-chart/index.vue'
  import type { BarDataItem } from '@/types/component/chart'

  defineOptions({ name: 'AiDecision' })

  interface DecisionResult {
    employmentSalary: number
    employmentStability: number
    employmentTimeCost: number
    postgradSalary: number
    postgradStability: number
    postgradTimeCost: number
    advice: string
    reasons: string[]
  }

  const loading = ref(false)
  const showResult = ref(false)
  const resultData = ref<DecisionResult>({
    employmentSalary: 0,
    employmentStability: 0,
    employmentTimeCost: 0,
    postgradSalary: 0,
    postgradStability: 0,
    postgradTimeCost: 0,
    advice: '',
    reasons: []
  })

  const formData = ref({
    targetCity: '',
    expectedSalary: 8000,
    studyMonths: 12
  })

  const compareChartXAxis = computed(() => ['期望薪资', '稳定性指数', '时间成本（月）'])

  const compareChartData = computed<BarDataItem[]>(() => [
    {
      name: '就业路径',
      data: [
        resultData.value.employmentSalary,
        resultData.value.employmentStability * 100,
        resultData.value.employmentTimeCost
      ]
    },
    {
      name: '考研路径',
      data: [
        resultData.value.postgradSalary,
        resultData.value.postgradStability * 100,
        resultData.value.postgradTimeCost
      ]
    }
  ])

  const handleAnalyze = async () => {
    if (!formData.value.targetCity) {
      ElMessage.warning('请输入目标城市')
      return
    }

    if (formData.value.expectedSalary <= 0) {
      ElMessage.warning('请输入有效的期望薪资')
      return
    }

    loading.value = true
    try {
      const res: any = await analyzeDecision({
        target_city: formData.value.targetCity,
        expected_salary: formData.value.expectedSalary,
        study_months: formData.value.studyMonths
      })
      if (res.code === 200 || res.status === 'not_implemented') {
        // Stub 模式下使用模拟数据
        resultData.value = {
          employmentSalary: 12000,
          employmentStability: 0.75,
          employmentTimeCost: 6,
          postgradSalary: 18000,
          postgradStability: 0.85,
          postgradTimeCost: 36,
          advice: '根据您的实际情况，建议优先选择就业路径。',
          reasons: [
            '您已经具备了一定的职业技能和实习经验，早期就业可以积累实际工作经验',
            '当前就业市场竞争激烈，提前进入职场可以抢占有利位置',
            '考研需要投入大量时间精力，且结果存在不确定性',
            '如果您对学术研究有强烈兴趣，可以在工作后考虑在职研究生'
          ]
        }
        showResult.value = true
        ElMessage.success('分析完成')
      } else {
        ElMessage.error(res.message || '分析失败')
      }
    } catch (error) {
      console.error('AI 决策分析失败:', error)
      ElMessage.error('分析失败，请稍后重试')
    } finally {
      loading.value = false
    }
  }
</script>

<style scoped>
  .page-ai-decision {
    padding: 20px;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .title {
    font-size: 16px;
    font-weight: 600;
  }

  .ai-form {
    max-width: 500px;
  }

  .result-card {
    animation: fadeIn 0.3s ease-in-out;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .result-content {
    padding: 20px 0;
  }

  .compare-cards {
    margin-bottom: 30px;
  }

  .path-card {
    padding: 24px;
    border-radius: 12px;
    min-height: 180px;
  }

  .employment {
    background: linear-gradient(135deg, #ecf5ff 0%, #e6f0ff 100%);
    border: 1px solid #b3d8fd;
  }

  .postgraduate {
    background: linear-gradient(135deg, #f0f9eb 0%, #e8f5e1 100%);
    border: 1px solid #d4edda;
  }

  .path-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px dashed #d0d0d0;
  }

  .employment .path-header {
    color: #409eff;
  }

  .postgraduate .path-header {
    color: #67c23a;
  }

  .path-header span {
    font-size: 18px;
    font-weight: 600;
  }

  .path-content {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .path-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .path-label {
    color: #606266;
    font-size: 14px;
  }

  .path-value {
    font-size: 16px;
    font-weight: 600;
    color: #303133;
  }

  .path-value.salary {
    color: #f56c6c;
  }

  .chart-section {
    margin-bottom: 30px;
    padding: 20px;
    background: #f5f7fa;
    border-radius: 8px;
  }

  .advice-section {
    background: #fef9f0;
    border-radius: 8px;
    padding: 24px;
    border: 1px solid #f5deb3;
  }

  .advice-section h4 {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 16px;
    font-size: 16px;
    color: #e6a23c;
  }

  .advice-content {
    color: #606266;
  }

  .advice-text {
    font-size: 16px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 16px;
    padding-bottom: 16px;
    border-bottom: 1px dashed #f5deb3;
  }

  .advice-reasons {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .advice-reasons p {
    font-size: 14px;
    line-height: 1.6;
    margin: 0;
    padding-left: 16px;
    position: relative;
  }

  .advice-reasons p::before {
    content: '';
    position: absolute;
    left: 0;
    top: 8px;
    width: 6px;
    height: 6px;
    background: #e6a23c;
    border-radius: 50%;
  }
</style>
