<!-- 面试准备助手 -->
<template>
  <div class="page-interview-prep">
    <ElRow :gutter="20">
      <!-- 左侧配置 -->
      <ElCol :xs="24" :md="10">
        <ElCard class="art-card-xs mb-4">
          <template #header>
            <div class="flex items-center gap-2">
              <span>面试配置</span>
              <ElPopover placement="bottom-start" :width="400" trigger="click">
                <template #reference>
                  <ElIcon class="cursor-pointer text-gray-400 hover:text-blue-500" :size="18">
                    <QuestionFilled />
                  </ElIcon>
                </template>
                <div class="text-sm">
                  <div class="mb-3 font-semibold text-gray-700 dark:text-gray-200">面试配置说明</div>

                  <div class="mb-3">
                    <div class="font-medium text-blue-600 dark:text-blue-400 mb-1">根据面试类型调整问题重点：</div>
                    <ul class="pl-4 text-gray-600 dark:text-gray-400 space-y-1">
                      <li><span class="font-medium">技术面：</span>考察专业技能、场景题/算法题/设计题、技术选型能力</li>
                      <li><span class="font-medium">HR面：</span>考察职业素养、沟通表达、价值观匹配、团队协作</li>
                      <li><span class="font-medium">压力面：</span>连续质疑/否定/挑刺，考察心理素质和应变能力</li>
                      <li><span class="font-medium">群面：</span>无领导小组讨论，考察团队协作、领导力、说服技巧</li>
                    </ul>
                  </div>

                  <div class="mb-3">
                    <div class="font-medium text-blue-600 dark:text-blue-400 mb-1">根据面试轮次调整深度：</div>
                    <ul class="pl-4 text-gray-600 dark:text-gray-400 space-y-1">
                      <li><span class="font-medium">初试：</span>基础能力、岗位匹配度、简历真实性</li>
                      <li><span class="font-medium">复试：</span>深入专业能力、项目经验、深度思考</li>
                      <li><span class="font-medium">终面：</span>文化认同、职业价值观、稳定性与诚意</li>
                    </ul>
                  </div>

                  <div>
                    <div class="font-medium text-blue-600 dark:text-blue-400 mb-1">根据公司类型设计情境：</div>
                    <ul class="pl-4 text-gray-600 dark:text-gray-400 space-y-1">
                      <li><span class="font-medium">大厂：</span>流程规范、竞争激烈、重视品牌技术栈</li>
                      <li><span class="font-medium">中小厂：</span>扁平管理、一专多能、成长机会多</li>
                      <li><span class="font-medium">外企：</span>英语加分、开放文化、边界清晰</li>
                      <li><span class="font-medium">国企：</span>稳定优先、合规意识、福利体系</li>
                    </ul>
                  </div>
                </div>
              </ElPopover>
            </div>
          </template>

          <ElForm :model="formData" label-position="top" size="default">
            <ElFormItem label="目标岗位">
              <ElInput
                v-model="formData.job_title"
                placeholder="如：前端开发工程师"
                clearable
                @keyup.enter="handleGenerateQuestions"
              />
            </ElFormItem>

            <ElFormItem label="专业（档案填充）">
              <ElInput v-model="formData.major" placeholder="从档案自动填充" disabled />
            </ElFormItem>

            <ElFormItem label="技能标签">
              <div class="skill-wrap">
                <ElTag
                  v-for="skill in formData.skills"
                  :key="skill"
                  size="default"
                  closable
                  @close="handleRemoveSkill(skill)"
                >
                  {{ skill }}
                </ElTag>
                <ElInput
                  v-if="addingSkill"
                  ref="skillInputRef"
                  v-model="newSkill"
                  size="default"
                  class="skill-input"
                  @keyup.enter="handleAddSkill"
                  @blur="handleAddSkill"
                />
                <ElButton v-else size="default" @click="handleStartAddSkill">+ 添加</ElButton>
              </div>
            </ElFormItem>

            <ElDivider />

            <ElFormItem label="面试类型">
              <ElRadioGroup v-model="formData.interview_type" size="default">
                <ElRadioButton value="technical">技术面</ElRadioButton>
                <ElRadioButton value="hr">HR面</ElRadioButton>
                <ElRadioButton value="stress">压力面</ElRadioButton>
                <ElRadioButton value="group">群面</ElRadioButton>
              </ElRadioGroup>
            </ElFormItem>

            <ElFormItem label="面试轮次">
              <ElRadioGroup v-model="formData.interview_round" size="default">
                <ElRadioButton value="first">初试</ElRadioButton>
                <ElRadioButton value="second">复试</ElRadioButton>
                <ElRadioButton value="final">终面</ElRadioButton>
              </ElRadioGroup>
            </ElFormItem>

            <ElFormItem label="公司类型">
              <ElRadioGroup v-model="formData.company_type" size="default">
                <ElRadioButton value="large">大厂</ElRadioButton>
                <ElRadioButton value="medium">中小厂</ElRadioButton>
                <ElRadioButton value="foreign">外企</ElRadioButton>
                <ElRadioButton value="state">国企</ElRadioButton>
              </ElRadioGroup>
            </ElFormItem>
          </ElForm>
        </ElCard>

        <ElButton
          type="primary"
          :loading="loading"
          class="w-full mb-3"
          size="large"
          @click="handleGenerateQuestions"
        >
          <ElIcon><MagicStick /></ElIcon>
          生成面试问题
        </ElButton>

        <ElRow :gutter="12">
          <ElCol :span="12">
            <ElButton class="w-full" @click="handleQuick('self_intro', '自我介绍', 'self_intro')">
              <ElIcon><User /></ElIcon>
              自我介绍
            </ElButton>
          </ElCol>
          <ElCol :span="12">
            <ElButton
              class="w-full"
              @click="handleQuick('questions_to_ask', '反问准备', 'questions_to_ask')"
            >
              <ElIcon><ChatDotRound /></ElIcon>
              反问准备
            </ElButton>
          </ElCol>
          <ElCol :span="12" class="mt-3">
            <ElButton
              class="w-full"
              @click="handleQuick('salary_negotiation', '薪资谈判', 'salary_tips')"
            >
              <ElIcon><Money /></ElIcon>
              薪资谈判
            </ElButton>
          </ElCol>
          <ElCol :span="12" class="mt-3">
            <ElButton
              class="w-full"
              @click="handleQuick('follow_up_email', '跟进邮件', 'follow_up_email')"
            >
              <ElIcon><Message /></ElIcon>
              跟进邮件
            </ElButton>
          </ElCol>
        </ElRow>
      </ElCol>

      <!-- 右侧结果 -->
      <ElCol :xs="24" :md="14">
        <!-- 生成结果 -->
        <ElCard v-if="resultVisible" class="art-card-xs mb-4">
          <template #header>
            <div class="flex justify-between items-center">
              <span>{{ resultTitle }}</span>
              <ElSpace>
                <ElButton size="small" link @click="handleCopy">
                  <ElIcon><CopyDocument /></ElIcon>
                </ElButton>
                <ElButton size="small" link @click="handleCloseResult">
                  <ElIcon><Close /></ElIcon>
                </ElButton>
              </ElSpace>
            </div>
          </template>

          <ElScrollbar height="500px">
            <!-- 问题列表 -->
            <div v-if="resultType === 'questions'" class="flex flex-col gap-4">
              <div
                v-for="(q, idx) in parsedQuestions"
                :key="idx"
                class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 cursor-pointer transition-all hover:shadow-md bg-white dark:bg-gray-800"
                @click="handlePractice(q.question)"
              >
                <div class="flex items-center gap-3 mb-3">
                  <div
                    class="flex items-center justify-center w-7 h-7 rounded-full bg-blue-500 text-white text-sm font-bold flex-shrink-0"
                  >
                    {{ idx + 1 }}
                  </div>
                  <span class="text-base font-medium flex-1 text-gray-800 dark:text-gray-100">{{ q.question }}</span>
                  <ElTag size="small" type="primary">练习</ElTag>
                </div>
                <div class="flex flex-col gap-2">
                  <div class="rounded p-3 bg-green-50 dark:bg-green-900/20">
                    <div class="flex items-center gap-1 mb-1 text-xs font-semibold text-green-600 dark:text-green-400">
                      <ElIcon><SuccessFilled /></ElIcon>
                      优秀回答
                    </div>
                    <p class="text-sm text-gray-700 dark:text-gray-300">{{ q.answer_example }}</p>
                  </div>
                  <div class="rounded p-3 bg-blue-50 dark:bg-blue-900/20">
                    <div class="flex items-center gap-1 mb-1 text-xs font-semibold text-blue-600 dark:text-blue-400">
                      <ElIcon><Star /></ElIcon>
                      回答要点
                    </div>
                    <ul class="pl-4 text-sm list-disc text-gray-700 dark:text-gray-300">
                      <li v-for="(pt, pi) in q.key_points" :key="pi">{{ pt }}</li>
                    </ul>
                  </div>
                  <div v-if="q.notes" class="rounded p-3 bg-orange-50 dark:bg-orange-900/20">
                    <div class="flex items-center gap-1 mb-1 text-xs font-semibold text-orange-600 dark:text-orange-400">
                      <ElIcon><WarningFilled /></ElIcon>
                      注意事项
                    </div>
                    <p class="text-sm text-gray-700 dark:text-gray-300">{{ q.notes }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- 反问列表 -->
            <div v-else-if="resultType === 'questions_to_ask'" class="flex flex-col gap-3">
              <div
                v-for="(q, idx) in parsedQuestionsToAsk"
                :key="idx"
                class="flex items-center gap-3 p-3 rounded bg-gray-50 dark:bg-gray-800"
              >
                <div
                  class="flex items-center justify-center w-6 h-6 rounded-full bg-blue-500 text-white text-xs font-bold flex-shrink-0"
                >
                  {{ idx + 1 }}
                </div>
                <span class="text-sm text-gray-700 dark:text-gray-300">{{ q }}</span>
              </div>
            </div>

            <!-- 格式化内容（自我介绍、薪资谈判等） -->
            <div v-else-if="formattedContent.length > 0" class="flex flex-col gap-4 p-2">
              <div
                v-for="(section, idx) in formattedContent"
                :key="idx"
                class="p-4 rounded-lg bg-gray-50 dark:bg-gray-800"
              >
                <div class="text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">{{ section.title }}</div>
                <div v-if="Array.isArray(section.items)">
                  <ul class="pl-4 text-sm list-disc text-gray-700 dark:text-gray-300">
                    <li v-for="(item, i) in section.items" :key="i" class="mb-1">{{ item }}</li>
                  </ul>
                </div>
                <p v-else class="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{{ section.items }}</p>
              </div>
            </div>

            <!-- 纯文本内容（降级） -->
            <div v-else class="p-4 rounded text-sm whitespace-pre-wrap text-gray-700 dark:text-gray-300">
              {{ rawContent }}
            </div>
          </ElScrollbar>
        </ElCard>

        <!-- 模拟练习 -->
        <ElCard v-if="practiceVisible" class="art-card-xs">
          <template #header>
            <div class="flex justify-between items-center">
              <span>模拟练习</span>
              <ElSpace>
                <ElButton size="small" link @click="handleBackToResult">
                  <ElIcon><ArrowLeft /></ElIcon>
                  返回
                </ElButton>
                <ElButton size="small" link @click="handleClosePractice">
                  <ElIcon><Close /></ElIcon>
                </ElButton>
              </ElSpace>
            </div>
          </template>

          <div class="mb-4 p-4 rounded-lg bg-blue-50 dark:bg-blue-900/30">
            <div class="flex items-center gap-1 mb-2 text-xs font-semibold text-blue-600 dark:text-blue-400">
              <ElIcon><ChatLineSquare /></ElIcon>
              面试问题
            </div>
            <p class="text-base text-blue-600 dark:text-blue-300">{{ practiceQuestion }}</p>
          </div>

          <div class="mb-4">
            <div class="flex items-center gap-1 mb-2 text-sm text-gray-600 dark:text-gray-400">
              <ElIcon><EditPen /></ElIcon>
              请输入你的回答
            </div>
            <ElInput
              v-model="practiceAnswer"
              type="textarea"
              :rows="5"
              placeholder="在这里输入你的回答..."
            />
          </div>

          <div class="text-center mb-4">
            <ElButton
              type="primary"
              :loading="practiceLoading"
              size="default"
              @click="handlePracticeSubmit"
            >
              <ElIcon><Position /></ElIcon>
              提交点评
            </ElButton>
          </div>

          <!-- 点评结果 -->
          <div v-if="practiceResult">
            <ElDivider content-position="left">
              <ElIcon><Cpu /></ElIcon>
              AI 点评
            </ElDivider>

            <!-- 评分面板 -->
            <div class="mb-4 p-6 rounded-lg bg-blue-50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-800">
              <div class="text-sm text-blue-600 dark:text-blue-400 mb-2 text-center">综合评分</div>
              <div class="flex items-baseline justify-center gap-1">
                <span class="text-5xl font-bold text-blue-600 dark:text-blue-300">{{ practiceResult.score }}</span>
                <span class="text-lg text-blue-400 dark:text-blue-500">/ 100</span>
              </div>
              <!-- 进度条 -->
              <div class="mt-3 h-2 bg-blue-100 dark:bg-blue-900/50 rounded-full overflow-hidden">
                <div
                  class="h-full bg-gradient-to-r from-blue-500 to-blue-400 dark:from-blue-400 dark:to-blue-300 rounded-full transition-all duration-500"
                  :style="{ width: practiceResult.score + '%' }"
                ></div>
              </div>
            </div>

            <ElRow :gutter="12">
              <ElCol :span="12">
                <div class="p-3 rounded-lg bg-green-50 dark:bg-green-900/20">
                  <div class="flex items-center gap-1 mb-2 text-sm font-semibold text-green-600 dark:text-green-400">
                    <ElIcon><SuccessFilled /></ElIcon>
                    亮点
                  </div>
                  <ul class="pl-4 text-sm list-disc text-gray-700 dark:text-gray-300">
                    <li v-for="(s, idx) in practiceResult.strengths" :key="idx" class="mb-1">{{ s }}</li>
                  </ul>
                </div>
              </ElCol>
              <ElCol :span="12">
                <div class="p-3 rounded-lg bg-red-50 dark:bg-red-900/20">
                  <div class="flex items-center gap-1 mb-2 text-sm font-semibold text-red-600 dark:text-red-400">
                    <ElIcon><WarningFilled /></ElIcon>
                    改进点
                  </div>
                  <ul class="pl-4 text-sm list-disc text-gray-700 dark:text-gray-300">
                    <li v-for="(w, idx) in practiceResult.weaknesses" :key="idx" class="mb-1">{{ w }}</li>
                  </ul>
                </div>
              </ElCol>
            </ElRow>

            <div class="mt-4 p-4 rounded-lg bg-blue-50 dark:bg-blue-900/20">
              <div class="flex items-center gap-1 mb-2 text-sm font-semibold text-blue-600 dark:text-blue-400">
                <ElIcon><Cpu /></ElIcon>
                优化建议
              </div>
              <p class="text-sm whitespace-pre-wrap text-gray-700 dark:text-gray-300">{{ practiceResult.improved_answer }}</p>
            </div>
          </div>
        </ElCard>

        <!-- 空状态 -->
        <div
          v-if="!resultVisible && !practiceVisible && !loading"
          class="flex flex-col items-center justify-center py-24"
        >
          <ElIcon class="text-6xl text-gray-300 mb-4"><ChatLineSquare /></ElIcon>
          <p class="text-gray-400">配置左侧选项，点击按钮生成内容</p>
        </div>

        <!-- 加载状态 -->
        <div
          v-if="loading"
          class="flex flex-col items-center justify-center py-24"
        >
          <ElIcon class="text-6xl text-blue-400 mb-6 animate-spin"><Loading /></ElIcon>
          <p class="text-lg text-gray-600 dark:text-gray-400 mb-2">AI正在为您生成{{ generatingTitle }}中</p>
          <p class="text-sm text-gray-400">请稍候...</p>
        </div>
      </ElCol>
    </ElRow>
  </div>
</template>

<script setup lang="ts">
  import {
    MagicStick,
    User,
    ChatDotRound,
    Money,
    Message,
    CopyDocument,
    Close,
    SuccessFilled,
    Star,
    WarningFilled,
    ChatLineSquare,
    EditPen,
    Position,
    Cpu,
    ArrowLeft,
    Loading,
    QuestionFilled
  } from '@element-plus/icons-vue'
  import { interviewPrep, interviewPracticeReview, type InterviewPrepRequest } from '@/api/ai'
  import { fetchStudentProfile } from '@/api/student'
  import { ElMessage } from 'element-plus'

  defineOptions({ name: 'InterviewPrep' })

  // 结果缓存
  const resultCache = ref<Record<string, any>>({})

  // 结果状态
  const resultVisible = ref(false)
  const resultTitle = ref('')
  const resultType = ref('')
  const rawContent = ref('')
  const parsedQuestions = ref<any[]>([])
  const parsedQuestionsToAsk = ref<string[]>([])
  const formattedContent = ref<{ title: string; items: string | string[] }[]>([])

  // 练习状态
  const practiceVisible = ref(false)
  const practiceQuestion = ref('')
  const practiceAnswer = ref('')
  const practiceResult = ref<any>(null)
  const practiceLoading = ref(false)

  // 表单数据
  const formData = ref({
    job_title: '',
    major: '',
    skills: [] as string[],
    interview_type: 'technical' as InterviewPrepRequest['interview_type'],
    interview_round: 'first' as InterviewPrepRequest['interview_round'],
    company_type: 'medium' as InterviewPrepRequest['company_type']
  })

  // 技能管理
  const addingSkill = ref(false)
  const newSkill = ref('')
  const skillInputRef = ref()

  const handleStartAddSkill = () => {
    addingSkill.value = true
    nextTick(() => skillInputRef.value?.focus())
  }

  const handleAddSkill = () => {
    const skill = newSkill.value.trim()
    if (skill && !formData.value.skills.includes(skill)) {
      formData.value.skills.push(skill)
    }
    newSkill.value = ''
    addingSkill.value = false
  }

  const handleRemoveSkill = (skill: string) => {
    formData.value.skills = formData.value.skills.filter((s) => s !== skill)
  }

  // 加载档案
  const handleLoadProfile = async () => {
    try {
      const res: any = await fetchStudentProfile()
      if (res.data) {
        formData.value.major = res.data.major || ''
        formData.value.skills = res.data.skills || []
      }
    } catch {
      // ignore
    }
  }

  // 关闭结果
  const handleCloseResult = () => {
    resultVisible.value = false
  }

  // 返回结果列表
  const handleBackToResult = () => {
    practiceVisible.value = false
    if (rawContent.value) {
      resultVisible.value = true
    }
  }

  // 关闭练习面板
  const handleClosePractice = () => {
    practiceVisible.value = false
  }

  // 复制
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(rawContent.value)
      ElMessage.success('已复制')
    } catch {
      ElMessage.error('复制失败')
    }
  }

  // 发起练习
  const handlePractice = (question: string) => {
    practiceQuestion.value = question
    practiceAnswer.value = ''
    practiceResult.value = null
    practiceVisible.value = true
    resultVisible.value = false
  }

  // 提交练习
  const handlePracticeSubmit = async () => {
    if (!practiceAnswer.value.trim()) {
      ElMessage.warning('请输入回答')
      return
    }
    practiceLoading.value = true
    practiceResult.value = null
    try {
      const res: any = await interviewPracticeReview({
        question: practiceQuestion.value,
        user_answer: practiceAnswer.value,
        job_title: formData.value.job_title
      })
      // 支持多种响应格式
      const answerText = res.data?.answer || res.data?.content || res.data?.result || res.answer || ''
      if (answerText) {
        parsePracticeResult(answerText)
        if (practiceResult.value) {
          ElMessage.success('点评完成')
        }
      } else if (res.message) {
        ElMessage.error(res.message)
      } else {
        ElMessage.error('点评失败，未获取到有效内容')
      }
    } catch (e: any) {
      ElMessage.error(e.message || '点评失败')
    } finally {
      practiceLoading.value = false
    }
  }

  const parsePracticeResult = (text: string) => {
    if (!text || typeof text !== 'string') {
      practiceResult.value = null
      ElMessage.warning('未获取到有效的点评内容')
      return
    }
    try {
      // 尝试匹配 JSON 对象
      const match = text.match(/\{[\s\S]*\}/)
      if (match) {
        const data = JSON.parse(match[0])
        practiceResult.value = {
          score: data.score || data.total_score || 0,
          strengths: data.strengths || data.good_points || [],
          weaknesses: data.weaknesses || data.areas_for_improvement || [],
          improved_answer: data.improved_answer || data.suggested_answer || data.improvement || ''
        }
      } else {
        // 如果不是 JSON 格式，整体作为建议返回
        practiceResult.value = { score: 0, strengths: [], weaknesses: [], improved_answer: text }
      }
    } catch {
      // 解析失败，尝试直接使用原文
      practiceResult.value = { score: 0, strengths: [], weaknesses: [], improved_answer: text }
    }
  }

  // 核心生成函数
  const loading = ref(false)
  const generatingTitle = ref('')

  // 生成缓存 key（根据 action 和配置生成）
  const getCacheKey = (action: string) => {
    if (action === 'generate_questions') {
      // 生成面试问题时，缓存 key 应包含配置
      return `${action}_${formData.value.interview_type}_${formData.value.interview_round}_${formData.value.company_type}`
    }
    // 其他功能共用同一个缓存
    return action
  }

  const doGenerate = async (
    action: InterviewPrepRequest['action'],
    title: string,
    type: string
  ) => {
    if (!formData.value.job_title) {
      ElMessage.warning('请输入目标岗位')
      return
    }

    const cacheKey = getCacheKey(action)

    // 命中缓存
    if (resultCache.value[cacheKey]) {
      const cached = resultCache.value[cacheKey]
      resultTitle.value = title
      resultType.value = type
      rawContent.value = cached.rawContent
      parsedQuestions.value = cached.parsedQuestions || []
      parsedQuestionsToAsk.value = cached.parsedQuestionsToAsk || []
      formattedContent.value = cached.formattedContent || []
      resultVisible.value = true
      practiceVisible.value = false
      ElMessage.info('已加载缓存')
      return
    }

    // 显示加载状态
    loading.value = true
    generatingTitle.value = title
    resultVisible.value = false
    practiceVisible.value = false
    resultTitle.value = title
    resultType.value = type

    try {
      const res: any = await interviewPrep({
        job_title: formData.value.job_title,
        major: formData.value.major,
        skills: formData.value.skills,
        interview_type: formData.value.interview_type,
        interview_round: formData.value.interview_round,
        company_type: formData.value.company_type,
        action
      })

      if (res.status === 'success' && res.answer) {
        rawContent.value = res.answer
        let pQ: any[] = []
        let pQTA: string[] = []
        let fC: { title: string; items: string | string[] }[] = []

        if (type === 'questions') {
          pQ = parseQs(res.answer)
          parsedQuestions.value = pQ
        } else if (type === 'questions_to_ask') {
          pQTA = parseQsToAsk(res.answer)
          parsedQuestionsToAsk.value = pQTA
        } else {
          // 解析 JSON 格式内容（自我介绍、薪资谈判、跟进邮件等）
          fC = parseQuickContent(res.answer)
          formattedContent.value = fC
        }

        // 写入缓存
        resultCache.value[cacheKey] = {
          rawContent: res.answer,
          parsedQuestions: pQ,
          parsedQuestionsToAsk: pQTA,
          formattedContent: fC
        }

        resultVisible.value = true
        practiceVisible.value = false
      } else {
        ElMessage.error(res.message || '生成失败')
      }
    } catch (e: any) {
      ElMessage.error(e.message || '生成失败')
    } finally {
      loading.value = false
    }
  }

  const handleGenerateQuestions = () => {
    doGenerate('generate_questions', '高频面试问题', 'questions')
  }

  const handleQuick = (action: string, title: string, type: string) => {
    doGenerate(action as InterviewPrepRequest['action'], title, type)
  }

  // JSON 解析
  const parseQs = (text: string): any[] => {
    try {
      const match = text.match(/\{[\s\S]*"questions"[\s\S]*\}/)
      if (match) {
        const data = JSON.parse(match[0])
        return data.questions || []
      }
    } catch {
      // ignore parse error
    }
    return []
  }

  const parseQsToAsk = (text: string): string[] => {
    try {
      const match = text.match(/\{[\s\S]*"questions_to_ask"[\s\S]*\}/)
      if (match) {
        const data = JSON.parse(match[0])
        return data.questions_to_ask || []
      }
    } catch {
      // ignore parse error
    }
    return []
  }

  // 解析快速内容（自我介绍、薪资谈判、跟进邮件等）
  const parseQuickContent = (text: string): { title: string; items: string | string[] }[] => {
    try {
      // 尝试匹配 JSON 对象
      const match = text.match(/\{[\s\S]*\}/)
      if (match) {
        const data = JSON.parse(match[0])
        // 提取第一个键值对作为内容
        const key = Object.keys(data)[0]
        const value = data[key]
        if (typeof value === 'object' && value !== null) {
          return Object.entries(value).map(([k, v]) => ({
            title: k,
            items: Array.isArray(v) ? v : [v as string]
          }))
        } else if (typeof value === 'string') {
          return [{ title: key, items: value }]
        }
      }
    } catch {
      // JSON 解析失败，返回原始文本段落
    }
    // 如果解析失败，按行分割返回
    const lines = text.split('\n').filter((l: string) => l.trim())
    if (lines.length > 0) {
      return [{ title: '内容', items: lines }]
    }
    return []
  }

  onMounted(() => {
    handleLoadProfile()
  })
</script>

<style scoped>
  .page-interview-prep {
    padding: 20px;
  }

  .skill-wrap {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    align-items: center;
  }

  .skill-input {
    width: 100px;
  }

  @keyframes spin {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }

  .animate-spin {
    animation: spin 1s linear infinite;
  }
</style>
