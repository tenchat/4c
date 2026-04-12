import request from '@/utils/http'
import { useUserStore } from '@/store/modules/user'

// 类型定义
export interface QARequest {
  question: string
  user_id: string
  role_type: string
  session_id?: string
}

export interface QAResponse {
  status: string
  message: string
  data?: {
    answer: string
    sources: any[]
    session_id: string
  }
}

export interface ChatHistoryResponse {
  session_id: string
  messages: ChatMessage[]
  has_more: boolean
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

// AI 问答
export const aiQA = (data: QARequest) => {
  return request.post<QAResponse>({
    url: '/v1/ai/qa',
    data
  })
}

// AI 流式问答 (SSE)
export const aiQAStream = async (
  data: QARequest,
  onChunk: (content: string, done: boolean) => void,
  onError?: (error: string) => void,
  onSessionId?: (sessionId: string) => void
): Promise<void> => {
  try {
    const userStore = useUserStore()
    const headers: Record<string, string> = {
      'Content-Type': 'application/json'
    }
    if (userStore.accessToken) {
      headers['Authorization'] = `Bearer ${userStore.accessToken}`
    }

    const response = await fetch('/api/v1/ai/qa/stream', {
      method: 'POST',
      headers,
      body: JSON.stringify(data)
    })

    if (!response.ok) {
      throw new Error(`HTTP error: ${response.status}`)
    }

    const reader = response.body?.getReader()
    const decoder = new TextDecoder()

    if (!reader) {
      throw new Error('No response body')
    }

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value)
      const lines = chunk.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const jsonStr = line.slice(6)
            if (jsonStr.trim() === '') continue
            const parsed = JSON.parse(jsonStr)
            // 提取 session_id（仅在第一帧返回）
            if (parsed.session_id && onSessionId) {
              onSessionId(parsed.session_id)
            }
            onChunk(parsed.content || '', parsed.done || false)
            if (parsed.done) return
          } catch (e) {
            // Skip malformed JSON
          }
        }
      }
    }
  } catch (error) {
    onError?.(error instanceof Error ? error.message : 'Unknown error')
  }
}

// 获取聊天历史
export const getChatHistory = (sessionId?: string, userId?: string) => {
  return request.get<ChatHistoryResponse>({
    url: '/api/v1/ai/chat/history',
    params: { session_id: sessionId, user_id: userId }
  })
}

// 上传知识库文件
export const uploadKnowledge = (file: File, title: string, category: string = 'shared') => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('title', title)
  formData.append('category', category)

  return request.post({
    url: '/v1/ai/knowledge/upload',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 就业画像分析
export const getAiProfile = (data: any) => {
  return request.post<any>({
    url: '/v1/ai/employment-profile',
    data
  })
}

// 简历分析
export const analyzeResume = (data: any) => {
  return request.post<any>({
    url: '/v1/ai/resume-analysis',
    data
  })
}

// 考研 vs 就业决策分析
export const analyzeDecision = (data: any) => {
  return request.post<any>({
    url: '/v1/ai/graduate-vs-job',
    data
  })
}

// 生成就业预警
export const generateWarnings = (data: any) => {
  return request.post<any>({
    url: '/v1/ai/warning',
    data
  })
}

// AI 简历优化（需要较长超时，因为涉及 LLM 调用）
export const optimizeResume = (data: { resume_text: string; target_job: string }) => {
  return request.post<any>({
    url: '/api/v1/ai/resume/optimize',
    data,
    timeout: 60000 // 60秒超时，LLM 调用较慢
  })
}

// 导出简历 PDF
export const exportResumePdf = (resumeText: string) => {
  return request.post<any>({
    url: '/api/v1/ai/resume/export-pdf',
    data: { resume_text: resumeText, target_job: '' },
    responseType: 'blob',
    timeout: 30000 // 30秒超时
  })
}

// 解析简历文件（上传 PDF/Word）
export const parseResumeFile = (file: File) => {
  const formData = new FormData()
  formData.append('file', file)

  return request.post<any>({
    url: '/api/v1/ai/resume/parse-file',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    timeout: 60000 // 60秒超时
  })
}

// 面试准备助手
export interface InterviewPrepRequest {
  job_title: string
  industry?: string
  city?: string
  major?: string
  skills: string[]
  internship?: string
  degree?: number
  salary_min?: number
  salary_max?: number
  interview_type: 'technical' | 'hr' | 'stress' | 'group'
  interview_round: 'first' | 'second' | 'final'
  company_type: 'large' | 'medium' | 'small' | 'foreign' | 'state'
  action: 'generate_questions' | 'self_intro' | 'questions_to_ask' | 'salary_negotiation' | 'follow_up_email' | 'dressing_advice'
}

export const interviewPrep = (data: InterviewPrepRequest) => {
  return request.post<any>({
    url: '/api/v1/ai/interview-prep',
    data,
    timeout: 60000 // 60秒超时
  })
}

// 模拟练习点评
export interface PracticeReviewRequest {
  question: string
  user_answer: string
  job_title: string
}

export const interviewPracticeReview = (data: PracticeReviewRequest) => {
  return request.post<any>({
    url: '/api/v1/ai/interview-practice-review',
    data,
    timeout: 60000 // 60秒超时
  })
}
