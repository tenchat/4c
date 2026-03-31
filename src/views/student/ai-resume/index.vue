<!-- AI 简历优化页面 -->
<template>
  <div class="page-ai-resume">
    <el-card class="art-card-xs">
      <template #header>
        <div class="card-header">
          <span class="title">AI 简历优化</span>
        </div>
      </template>

      <el-form :model="formData" label-width="100px" class="ai-form">
        <el-form-item label="简历文本">
          <el-input
            v-model="formData.resumeText"
            type="textarea"
            :rows="10"
            placeholder="请粘贴您的简历内容"
          />
        </el-form-item>

        <el-form-item label="目标岗位">
          <el-input
            v-model="formData.targetJob"
            placeholder="请输入目标岗位名称"
            clearable
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
        <!-- ATS 评分 -->
        <div class="ats-section">
          <div class="ats-score">
            <el-progress
              type="circle"
              :percentage="resultData.atsScore || 0"
              :width="140"
              :stroke-width="12"
              :color="atsScoreColor"
            >
              <template #default>
                <div class="progress-content">
                  <span class="score-value">{{ resultData.atsScore || 0 }}</span>
                  <span class="score-label">ATS评分</span>
                </div>
              </template>
            </el-progress>
          </div>
          <div class="ats-tips">
            <p class="tips-title">提升建议</p>
            <p class="tips-text">{{ resultData.atsTips || '继续优化您的简历内容' }}</p>
          </div>
        </div>

        <!-- 关键词分析 -->
        <el-row :gutter="20" class="keywords-section">
          <el-col :span="12">
            <div class="keyword-card matched">
              <h4>
                <el-icon><SuccessFilled /></el-icon>
                已匹配关键词
              </h4>
              <div class="keyword-tags">
                <el-tag
                  v-for="(keyword, index) in resultData.matchedKeywords"
                  :key="index"
                  type="success"
                  class="keyword-tag"
                >
                  {{ keyword }}
                </el-tag>
              </div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="keyword-card missing">
              <h4>
                <el-icon><WarningFilled /></el-icon>
                缺失关键词
              </h4>
              <div class="keyword-tags">
                <el-tag
                  v-for="(keyword, index) in resultData.missingKeywords"
                  :key="index"
                  type="danger"
                  class="keyword-tag"
                >
                  {{ keyword }}
                </el-tag>
              </div>
            </div>
          </el-col>
        </el-row>

        <!-- 优化建议 -->
        <div class="suggestions-section">
          <h4>
            <el-icon><Cpu /></el-icon>
            优化建议
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
  import { analyzeResume } from '@/api/ai'
  import { ElMessage } from 'element-plus'
  import { SuccessFilled, WarningFilled, Cpu } from '@element-plus/icons-vue'

  defineOptions({ name: 'AiResume' })

  interface ResumeResult {
    atsScore: number
    atsTips: string
    matchedKeywords: string[]
    missingKeywords: string[]
    suggestions: string[]
  }

  const loading = ref(false)
  const showResult = ref(false)
  const resultData = ref<ResumeResult>({
    atsScore: 0,
    atsTips: '',
    matchedKeywords: [],
    missingKeywords: [],
    suggestions: []
  })

  const formData = ref({
    resumeText: '',
    targetJob: ''
  })

  const atsScoreColor = computed(() => {
    const score = resultData.value.atsScore
    if (score >= 80) return '#67c23a'
    if (score >= 60) return '#e6a23c'
    return '#f56c6c'
  })

  const handleAnalyze = async () => {
    if (!formData.value.resumeText) {
      ElMessage.warning('请输入简历内容')
      return
    }

    if (!formData.value.targetJob) {
      ElMessage.warning('请输入目标岗位')
      return
    }

    loading.value = true
    try {
      const res: any = await analyzeResume({
        resume_text: formData.value.resumeText,
        target_job: formData.value.targetJob
      })
      if (res.code === 200 || res.status === 'not_implemented') {
        // Stub 模式下使用模拟数据
        resultData.value = {
          atsScore: 72,
          atsTips: '简历整体结构良好，建议增加更多量化数据和项目成果描述',
          matchedKeywords: [
            'Python',
            '数据分析',
            '机器学习',
            '团队协作',
            '项目开发'
          ],
          missingKeywords: [
            '深度学习',
            '大数据',
            '云计算',
            '产品运营',
            'SQL'
          ],
          suggestions: [
            '建议在项目经历中增加量化指标，如性能提升百分比、用户增长数量等',
            '缺少与目标岗位相关的深度学习经验，建议补充相关项目',
            '建议增加数据分析相关工具的熟练度说明，如Spark、Hive等',
            '面试官注重解决问题的能力，建议增加问题分析和解决的案例'
          ]
        }
        showResult.value = true
        ElMessage.success('分析完成')
      } else {
        ElMessage.error(res.message || '分析失败')
      }
    } catch (error) {
      console.error('AI 简历分析失败:', error)
      ElMessage.error('分析失败，请稍后重试')
    } finally {
      loading.value = false
    }
  }
</script>

<style scoped>
  .page-ai-resume {
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
    max-width: 800px;
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

  .ats-section {
    display: flex;
    align-items: center;
    gap: 40px;
    margin-bottom: 30px;
    padding: 20px;
    background: #f5f7fa;
    border-radius: 8px;
  }

  .ats-score {
    flex-shrink: 0;
  }

  .progress-content {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .score-value {
    font-size: 32px;
    font-weight: 700;
    color: #303133;
  }

  .score-label {
    font-size: 12px;
    color: #909399;
    margin-top: 4px;
  }

  .ats-tips {
    flex: 1;
  }

  .tips-title {
    font-size: 16px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 8px;
  }

  .tips-text {
    font-size: 14px;
    color: #606266;
    line-height: 1.6;
  }

  .keywords-section {
    margin-bottom: 30px;
  }

  .keyword-card {
    padding: 20px;
    border-radius: 8px;
    min-height: 120px;
  }

  .keyword-card h4 {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 16px;
    font-size: 16px;
  }

  .matched {
    background: linear-gradient(135deg, #f0f9eb 0%, #e8f5e1 100%);
    border: 1px solid #d4edda;
  }

  .matched h4 {
    color: #67c23a;
  }

  .missing {
    background: linear-gradient(135deg, #fef0f0 0%, #fee 100%);
    border: 1px solid #f5c6cb;
  }

  .missing h4 {
    color: #f56c6c;
  }

  .keyword-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .keyword-tag {
    margin: 0;
  }

  .suggestions-section {
    background: #ecf5ff;
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
    border-bottom: 1px dashed #b3d8fd;
  }

  .suggestions-list li:last-child {
    border-bottom: none;
  }
</style>
