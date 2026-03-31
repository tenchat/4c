import request from '@/utils/http'

// TODO: AI - 等待 MiniMax API 接入后实现
export const getAiProfile = (data: any) => request.post<any>({
  url: '/v1/ai/employment-profile',
  data
}).then(() => ({
  status: 'not_implemented',
  message: 'AI 分析功能开发中'
}))

export const analyzeResume = (data: any) => request.post<any>({
  url: '/v1/ai/resume-analysis',
  data
}).then(() => ({
  status: 'not_implemented',
  message: 'AI 简历分析功能开发中'
}))

export const analyzeDecision = (data: any) => request.post<any>({
  url: '/v1/ai/graduate-vs-job',
  data
}).then(() => ({
  status: 'not_implemented',
  message: 'AI 决策分析功能开发中'
}))

export const generateWarnings = (data: any) => request.post<any>({
  url: '/v1/ai/warning',
  data
}).then(() => ({
  status: 'not_implemented',
  message: 'AI 预警功能开发中'
}))

export const aiQA = (data: any) => request.post<any>({
  url: '/v1/ai/qa',
  data
}).then(() => ({
  status: 'not_implemented',
  message: 'AI 问答功能开发中'
}))