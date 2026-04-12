import request from '@/utils/http'

export const fetchStudentDashboard = () =>
  request.get<any>({ url: '/api/v1/student/dashboard' })

export const fetchJobStatistics = () =>
  request.get<any>({ url: '/api/v1/student/job-statistics' })

export const fetchStudentDataboard = () =>
  request.get<any>({ url: '/api/v1/student/databoard' })

export const fetchStudentProfile = () =>
  request.get<any>({ url: '/api/v1/student/profile' })

export const updateStudentProfile = (data: any) =>
  request.put<any>({ url: '/api/v1/student/profile', data })

export interface JobListParams {
  city?: string
  industry?: string
  min_salary?: number
  max_salary?: number
  degree?: number
  keyword?: string
  page?: number
  page_size?: number
}

export const fetchStudentJobs = (params: JobListParams) =>
  request.get<any>({ url: '/api/v1/student/jobs', params })

export const applyForJob = (jobId: string) =>
  request.post<any>({ url: `/api/v1/student/jobs/${jobId}/apply` })

export interface JobRecommendation {
  job_id: string
  title: string
  company_name: string
  city: string
  province: string
  industry: string
  min_salary: number
  max_salary: number
  keywords: string
  description: string
  match_score: number
  distance_score: number
  // 细分分数（用于雷达图）
  city_score: number
  industry_score: number
  salary_score: number
  degree_score: number
  skills_score: number
}

export const getJobRecommendations = (topK = 6) =>
  request.get<any>({ url: '/api/v1/student/job/recommend', params: { top_k: topK } })

export interface ResumeUploadResponse {
  file_path: string
  file_name: string
  text: string
  char_count: number
}

export const uploadResume = (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return request.post<ResumeUploadResponse>({
    url: '/api/v1/student/resume/upload',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const getResumeText = (filePath: string) =>
  request.get<{ file_path: string; text: string; char_count: number }>({
    url: '/api/v1/student/resume/text',
    params: { file_path: filePath }
  })

export const deleteResume = (filePath: string) =>
  request.del<{ code: number; message: string }>({
    url: '/api/v1/student/resume',
    params: { file_path: filePath }
  })

// AI 分析历史记录
export interface AiHistoryItem {
  record_id: string
  date: string
  score: number
  input_data: any
  result_data: any
}

export const getAiHistory = (analysisType = 'employment_profile', page = 1, pageSize = 10) =>
  request.get<{ code: number; message: string; data: AiHistoryItem[] }>({
    url: '/api/v1/student/ai-history',
    params: { analysis_type: analysisType, page, page_size: pageSize }
  })

export const saveAiHistory = (data: {
  analysis_type: string
  input_data: any
  result_data: any
}) =>
  request.post<{ code: number; message: string; data: { record_id: string } }>({
    url: '/api/v1/student/ai-history',
    data
  })

export const deleteAiHistory = (recordId: string) =>
  request.del<{ code: number; message: string }>({
    url: `/api/v1/student/ai-history/${recordId}`
  })

// 学生端公告列表
export interface StudentAnnouncementParams {
  keyword?: string
  major?: string
  degree?: number
  year?: number
  page?: number
  page_size?: number
}

export interface StudentAnnouncement {
  announcement_id: string
  company_id: string
  company_name: string
  title: string
  content: string
  target_major: string | null
  target_degree: number | null
  headcount: number | null
  deadline: string | null
  status: number
  published_at: string | null
}

export const fetchStudentAnnouncements = (params: StudentAnnouncementParams) =>
  request.get<any>({ url: '/api/v1/student/announcements', params })

export const fetchStudentAnnouncementDetail = (announcementId: string) =>
  request.get<any>({ url: `/api/v1/student/announcements/${announcementId}` })

// 学生端宣讲会/活动列表
export interface StudentActivityParams {
  keyword?: string
  activity_type?: string
  year?: number
  page?: number
  page_size?: number
}

export interface StudentActivity {
  activity_id: string
  company_id: string
  company_name: string
  type: string
  type_name: string | null
  title: string
  location: string | null
  activity_date: string | null
  start_time: string | null
  end_time: string | null
  description: string | null
  expected_num: number | null
  actual_num: number | null
  status: number
}

export const fetchStudentActivities = (params: StudentActivityParams) =>
  request.get<any>({ url: '/api/v1/student/activities', params })

export const fetchStudentActivityDetail = (activityId: string) =>
  request.get<any>({ url: `/api/v1/student/activities/${activityId}` })