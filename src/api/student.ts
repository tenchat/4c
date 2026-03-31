import request from '@/utils/http'

export const fetchStudentDashboard = () =>
  request.get<any>({ url: '/api/v1/student/dashboard' })

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