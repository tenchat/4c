<!-- AI 简历优化页面 -->
<template>
  <div class="page-ai-resume">
    <el-card class="art-card-xs">
      <template #header>
        <div class="card-header">
          <span class="title">AI 简历优化</span>
        </div>
      </template>

      <!-- 上传方式选择 -->
      <el-radio-group v-model="uploadType" class="mb-4">
        <el-radio value="text">输入简历内容</el-radio>
        <el-radio value="file">上传文档</el-radio>
      </el-radio-group>

      <el-form :model="formData" label-width="100px" class="ai-form">
        <!-- 文字输入模式 -->
        <el-form-item v-if="uploadType === 'text'" label="简历文本">
          <el-input
            v-model="formData.resumeText"
            type="textarea"
            :rows="10"
            placeholder="请粘贴您的简历内容，支持 Markdown 格式"
          />
        </el-form-item>

        <!-- 文件上传模式 -->
        <el-form-item v-else label="上传简历">
          <el-upload
            class="resume-uploader"
            drag
            accept=".pdf,.doc,.docx"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
          >
            <el-icon class="el-icon--upload"><Upload /></el-icon>
            <div class="el-upload__text">拖拽文件到此处 或 <em>点击上传</em></div>
            <template #tip>
              <div class="el-upload__tip">支持 PDF、Word 文档，大小不超过 10MB</div>
            </template>
          </el-upload>
        </el-form-item>

        <el-form-item label="目标岗位">
          <el-input
            v-model="formData.targetJob"
            placeholder="请输入目标岗位名称"
            clearable
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="optimizeLoading" @click="handleAnalyze">
            开始分析
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 优化结果弹窗 -->
    <el-dialog
      v-model="resultDialogVisible"
      title="简历优化结果"
      width="900px"
      :close-on-click-modal="false"
    >
      <div v-loading="optimizeLoading" class="result-container">
        <el-empty v-if="!optimizedResume && !suggestions.length" description="暂无优化结果" />

        <div v-else class="result-content">
          <!-- 左侧：优化后简历 -->
          <div class="resume-panel">
            <div class="panel-header">
              <span>优化后简历</span>
              <el-tag v-if="matchScore > 0" :type="matchScore >= 80 ? 'success' : matchScore >= 60 ? 'warning' : 'danger'">
                匹配度 {{ matchScore }}%
              </el-tag>
            </div>
            <el-input
              v-model="optimizedResume"
              type="textarea"
              :rows="18"
              class="resume-editor"
              placeholder="优化后的简历内容将显示在这里，您可以直接编辑"
            />
            <div class="panel-actions">
              <el-button type="primary" @click="handleApplyAll">采纳全部建议</el-button>
              <el-button @click="handleExportPdf">导出 PDF</el-button>
            </div>
          </div>

          <!-- 右侧：修改建议 -->
          <div class="suggestions-panel">
            <div class="panel-header">
              <span>修改建议</span>
              <el-badge :value="suggestions.length" type="primary" />
            </div>
            <div class="suggestions-list">
              <div v-for="(item, index) in suggestions" :key="index" class="suggestion-card">
                <div class="suggestion-section">
                  <el-tag size="small" type="info">{{ item.section }}</el-tag>
                </div>
                <div class="suggestion-content">
                  <div class="original">
                    <span class="label">原文：</span>
                    <span class="value">{{ item.original }}</span>
                  </div>
                  <div class="arrow">
                    <el-icon><Bottom /></el-icon>
                  </div>
                  <div class="suggested">
                    <span class="label">建议：</span>
                    <span class="value">{{ item.suggested }}</span>
                  </div>
                  <div class="reason">
                    <span class="label">原因：</span>
                    <span class="value">{{ item.reason }}</span>
                  </div>
                </div>
                <div class="suggestion-actions">
                  <el-button size="small" type="primary" @click="handleApplyOne(index)">
                    采纳此建议
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="resultDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
  import { optimizeResume, parseResumeFile } from '@/api/ai'
  import { ElMessage, ElMessageBox } from 'element-plus'
  import type { UploadFile } from 'element-plus'
  import { useUserStore } from '@/store/modules/user'
  import { Upload, Bottom } from '@element-plus/icons-vue'
  import { saveAs } from 'file-saver'

  defineOptions({ name: 'AiResume' })

  interface Suggestion {
    section: string
    original: string
    suggested: string
    reason: string
  }

  interface MatchAnalysis {
    score: number
    strengths: string[]
    weaknesses: string[]
  }

  interface OptimizeResult {
    optimized_resume: string
    suggestions: Suggestion[]
    match_analysis: MatchAnalysis
  }

  const uploadType = ref<'text' | 'file'>('text')
  const selectedFile = ref<File | null>(null)
  const optimizeLoading = ref(false)
  const resultDialogVisible = ref(false)

  const formData = ref({
    resumeText: '',
    targetJob: ''
  })

  const optimizedResume = ref('')
  const suggestions = ref<Suggestion[]>([])
  const matchScore = ref(0)
  const matchAnalysis = ref<MatchAnalysis | null>(null)

  // 处理文件选择
  const handleFileChange = async (uploadFile: UploadFile, _fileList: UploadFile[]) => {
    selectedFile.value = uploadFile.raw || null

    if (!uploadFile.raw) {
      ElMessage.error('文件读取失败')
      return
    }

    ElMessage.info('正在解析文件...')

    try {
      const res: any = await parseResumeFile(uploadFile.raw)
      if (res && res.text) {
        formData.value.resumeText = res.text
        ElMessage.success(`已加载文件: ${uploadFile.name}，解析了 ${res.char_count || 0} 个字符`)
      } else {
        ElMessage.error('文件解析失败')
      }
    } catch (error) {
      console.error('文件解析失败:', error)
      ElMessage.error('文件解析失败，请稍后重试')
    }
  }

  // 处理文件移除
  const handleFileRemove = () => {
    selectedFile.value = null
    formData.value.resumeText = ''
  }

  // 开始分析
  const handleAnalyze = async () => {
    if (uploadType.value === 'text' && !formData.value.resumeText) {
      ElMessage.warning('请输入简历内容')
      return
    }

    if (!formData.value.targetJob) {
      ElMessage.warning('请输入目标岗位')
      return
    }

    optimizeLoading.value = true
    resultDialogVisible.value = true

    try {
      const res: any = await optimizeResume({
        resume_text: formData.value.resumeText,
        target_job: formData.value.targetJob
      })

      // HTTP 工具已提取 data，所以 res 直接是 {optimized_resume, suggestions, match_analysis}
      if (res && res.optimized_resume) {
        optimizedResume.value = res.optimized_resume || formData.value.resumeText
        suggestions.value = res.suggestions || []
        matchAnalysis.value = res.match_analysis || null
        matchScore.value = res.match_analysis?.score || 0
        ElMessage.success('简历优化完成')
      } else {
        ElMessage.error('优化结果格式异常')
      }
    } catch (error) {
      console.error('AI 简历分析失败:', error)
      ElMessage.error('分析失败，请稍后重试')
    } finally {
      optimizeLoading.value = false
    }
  }

  // 采纳单条建议
  const handleApplyOne = (index: number) => {
    const suggestion = suggestions.value[index]
    if (!suggestion) return

    // 简单的替换逻辑
    if (optimizedResume.value.includes(suggestion.original)) {
      ElMessageBox.confirm(
        `将"${suggestion.original.slice(0, 30)}..."替换为"${suggestion.suggested.slice(0, 30)}..."？`,
        '采纳建议',
        { confirmButtonText: '确认', cancelButtonText: '取消', type: 'info' }
      ).then(() => {
        optimizedResume.value = optimizedResume.value.replace(
          suggestion.original,
          suggestion.suggested
        )
        suggestions.value.splice(index, 1)
        ElMessage.success('已采纳建议')
      }).catch(() => {})
    } else {
      ElMessage.warning('未找到匹配原文，请手动修改')
    }
  }

  // 采纳全部建议
  const handleApplyAll = () => {
    if (!suggestions.value.length) {
      ElMessage.warning('暂无建议可采纳')
      return
    }

    ElMessageBox.confirm(
      `确定要采纳全部 ${suggestions.value.length} 条建议吗？`,
      '采纳全部建议',
      { confirmButtonText: '确认', cancelButtonText: '取消', type: 'info' }
    ).then(() => {
      // 按顺序应用所有建议
      for (const suggestion of suggestions.value) {
        if (optimizedResume.value.includes(suggestion.original)) {
          optimizedResume.value = optimizedResume.value.replace(
            suggestion.original,
            suggestion.suggested
          )
        }
      }
      suggestions.value = []
      ElMessage.success('已采纳全部建议')
    }).catch(() => {})
  }

  // 导出 PDF
  const handleExportPdf = async () => {
    if (!optimizedResume.value) {
      ElMessage.warning('没有可导出的简历内容')
      return
    }

    try {
      ElMessage.info('正在生成 PDF...')

      // 使用 fetch 直接下载，避免 axios blob 处理问题
      const userStore = useUserStore()
      const response = await fetch('/api/v1/ai/resume/export-pdf', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': userStore.accessToken ? `Bearer ${userStore.accessToken}` : ''
        },
        body: JSON.stringify({ resume_text: optimizedResume.value, target_job: '' })
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const blob = await response.blob()
      saveAs(blob, '优化后简历.pdf')
      ElMessage.success('PDF 导出成功')
    } catch (error) {
      console.error('PDF 导出失败:', error)
      ElMessage.error('PDF 导出失败，请稍后重试')
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

  .mb-4 {
    margin-bottom: 16px;
  }

  .ai-form {
    max-width: 800px;
  }

  .resume-uploader {
    width: 100%;
  }

  .result-container {
    min-height: 400px;
  }

  .result-content {
    display: flex;
    gap: 20px;
    height: 100%;
  }

  .resume-panel {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 0;
  }

  .suggestions-panel {
    width: 380px;
    display: flex;
    flex-direction: column;
    min-width: 0;
  }

  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    font-weight: 600;
  }

  .resume-editor {
    flex: 1;
    font-family: 'Courier New', monospace;
    font-size: 13px;
  }

  .panel-actions {
    display: flex;
    gap: 8px;
    margin-top: 12px;
    justify-content: flex-end;
  }

  .suggestions-list {
    flex: 1;
    overflow-y: auto;
    max-height: 500px;
    padding-right: 8px;
  }

  .suggestion-card {
    background: #f5f7fa;
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 12px;
  }

  .suggestion-section {
    margin-bottom: 8px;
  }

  .suggestion-content {
    font-size: 13px;
    line-height: 1.6;
  }

  .suggestion-content .label {
    font-weight: 600;
    color: #606266;
  }

  .suggestion-content .value {
    color: #303133;
  }

  .suggestion-content .original {
    color: #909399;
    text-decoration: line-through;
  }

  .suggestion-content .suggested {
    color: #67c23a;
    font-weight: 500;
  }

  .suggestion-content .reason {
    color: #909399;
    font-size: 12px;
    margin-top: 4px;
  }

  .arrow {
    text-align: center;
    color: #409eff;
    padding: 4px 0;
  }

  .suggestion-actions {
    margin-top: 8px;
    text-align: right;
  }
</style>
