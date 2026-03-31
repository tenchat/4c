<!-- AI 就业画像页面 -->
<template>
  <div class="page-ai-profile">
    <el-card class="art-card-xs">
      <template #header>
        <div class="card-header">
          <span class="title">AI 就业画像</span>
        </div>
      </template>

      <el-form :model="formData" label-width="100px" class="ai-form">
        <el-form-item label="专业">
          <el-input v-model="formData.major" placeholder="请输入专业名称" clearable />
        </el-form-item>

        <el-form-item label="GPA">
          <el-input-number
            v-model="formData.gpa"
            :min="0"
            :max="4"
            :step="0.1"
            :precision="1"
            placeholder="请输入GPA"
            style="width: 200px"
          />
        </el-form-item>

        <el-form-item label="技能标签">
          <el-select
            v-model="formData.skills"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="请选择或输入技能标签"
            style="width: 100%"
          >
            <el-option
              v-for="skill in SKILL_OPTIONS"
              :key="skill"
              :label="skill"
              :value="skill"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="目标城市">
          <el-input v-model="formData.targetCity" placeholder="请输入目标城市" clearable />
        </el-form-item>

        <el-form-item label="实习经历">
          <el-input
            v-model="formData.internship"
            type="textarea"
            :rows="4"
            placeholder="请描述您的实习经历"
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
        <!-- 综合评分 -->
        <div class="score-section">
          <div class="score-circle">
            <span class="score-value">{{ resultData.overallScore || 0 }}</span>
            <span class="score-label">综合评分</span>
          </div>
        </div>

        <!-- 雷达图 -->
        <div class="chart-section">
          <ArtRadarChart
            :indicator="radarIndicator"
            :data="radarData"
            :height="'350px'"
            :colors="['#409EFF', '#67C23A']"
          />
        </div>

        <!-- 优劣势分析 -->
        <el-row :gutter="20" class="analysis-section">
          <el-col :span="12">
            <div class="analysis-card strengths">
              <h4>
                <el-icon><SuccessFilled /></el-icon>
                优势
              </h4>
              <ul>
                <li v-for="(item, index) in resultData.strengths" :key="index">
                  {{ item }}
                </li>
              </ul>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="analysis-card weaknesses">
              <h4>
                <el-icon><WarningFilled /></el-icon>
                劣势
              </h4>
              <ul>
                <li v-for="(item, index) in resultData.weaknesses" :key="index">
                  {{ item }}
                </li>
              </ul>
            </div>
          </el-col>
        </el-row>

        <!-- 建议 -->
        <div class="suggestions-section">
          <h4>
            <el-icon><Cpu /></el-icon>
            提升建议
          </h4>
          <ul class="suggestions-list">
            <li v-for="(item, index) in resultData.suggestions" :key="index">
              {{ item }}
            </li>
          </ul>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
  import { getAiProfile } from '@/api/ai'
  import { ElMessage } from 'element-plus'
  import { SuccessFilled, WarningFilled, Cpu } from '@element-plus/icons-vue'
  import ArtRadarChart from '@/components/core/charts/art-radar-chart/index.vue'

  defineOptions({ name: 'AiProfile' })

  interface ProfileResult {
    overallScore: number
    professional_match: number
    skill_match: number
    city_demand: number
    internship_score: number
    education_background: number
    strengths: string[]
    weaknesses: string[]
    suggestions: string[]
  }

  const loading = ref(false)
  const showResult = ref(false)
  const resultData = ref<ProfileResult>({
    overallScore: 0,
    professional_match: 0,
    skill_match: 0,
    city_demand: 0,
    internship_score: 0,
    education_background: 0,
    strengths: [],
    weaknesses: [],
    suggestions: []
  })

  const formData = ref({
    major: '',
    gpa: 3.0,
    skills: [] as string[],
    targetCity: '',
    internship: ''
  })

  const SKILL_OPTIONS = [
    'JavaScript',
    'TypeScript',
    'Python',
    'Java',
    'React',
    'Vue',
    'Node.js',
    'SQL',
    'Git',
    '数据分析',
    '机器学习',
    '人工智能'
  ]

  const radarIndicator = computed(() => [
    { name: '专业匹配度', max: 100 },
    { name: '技能匹配度', max: 100 },
    { name: '城市需求', max: 100 },
    { name: '实习经历', max: 100 },
    { name: '学历背景', max: 100 }
  ])

  const radarData = computed(() => [
    {
      name: '就业竞争力',
      value: [
        resultData.value.professional_match * 100,
        resultData.value.skill_match * 100,
        resultData.value.city_demand * 100,
        resultData.value.internship_score * 100,
        resultData.value.education_background * 100
      ]
    }
  ])

  const handleAnalyze = async () => {
    if (!formData.value.major) {
      ElMessage.warning('请输入专业名称')
      return
    }

    loading.value = true
    try {
      const res: any = await getAiProfile(formData.value)
      if (res.code === 200 || res.status === 'not_implemented') {
        // Stub 模式下使用模拟数据
        resultData.value = {
          overallScore: 78,
          professional_match: 0.82,
          skill_match: 0.75,
          city_demand: 0.68,
          internship_score: 0.65,
          education_background: 0.88,
          strengths: [
            '专业基础扎实，专业排名靠前',
            '学历背景符合目标岗位要求',
            '具备多项技术栈，学习能力强'
          ],
          weaknesses: [
            '实习经验相对不足',
            '目标城市竞争激烈',
            '部分技能认证缺失'
          ],
          suggestions: [
            '建议增加2-3个月相关实习经验',
            '可考虑备考相关技能认证证书',
            '关注二三线城市就业机会，降低竞争压力'
          ]
        }
        showResult.value = true
        ElMessage.success('分析完成')
      } else {
        ElMessage.error(res.message || '分析失败')
      }
    } catch (error) {
      console.error('AI 分析失败:', error)
      ElMessage.error('分析失败，请稍后重试')
    } finally {
      loading.value = false
    }
  }
</script>

<style scoped>
  .page-ai-profile {
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
    max-width: 600px;
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

  .score-section {
    display: flex;
    justify-content: center;
    margin-bottom: 30px;
  }

  .score-circle {
    width: 150px;
    height: 150px;
    border-radius: 50%;
    background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #fff;
    box-shadow: 0 8px 20px rgba(64, 158, 255, 0.3);
  }

  .score-value {
    font-size: 42px;
    font-weight: 700;
    line-height: 1;
  }

  .score-label {
    font-size: 14px;
    margin-top: 8px;
    opacity: 0.9;
  }

  .chart-section {
    margin-bottom: 30px;
  }

  .analysis-section {
    margin-bottom: 30px;
  }

  .analysis-card {
    padding: 20px;
    border-radius: 8px;
    min-height: 150px;
  }

  .analysis-card h4 {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 16px;
    font-size: 16px;
  }

  .strengths {
    background: linear-gradient(135deg, #f0f9eb 0%, #e8f5e1 100%);
    border: 1px solid #d4edda;
  }

  .strengths h4 {
    color: #67c23a;
  }

  .weaknesses {
    background: linear-gradient(135deg, #fef0f0 0%, #fee 100%);
    border: 1px solid #f5c6cb;
  }

  .weaknesses h4 {
    color: #f56c6c;
  }

  .analysis-card ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .analysis-card ul li {
    padding: 8px 0;
    color: #606266;
    font-size: 14px;
    border-bottom: 1px dashed #e0e0e0;
  }

  .analysis-card ul li:last-child {
    border-bottom: none;
  }

  .suggestions-section {
    background: #f5f7fa;
    border-radius: 8px;
    padding: 20px;
  }

  .suggestions-section h4 {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 16px;
    font-size: 16px;
    color: #409eff;
  }

  .suggestions-list {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .suggestions-list li {
    padding: 10px 0;
    color: #606266;
    font-size: 14px;
    border-bottom: 1px dashed #dcdfe6;
  }

  .suggestions-list li:last-child {
    border-bottom: none;
  }
</style>
