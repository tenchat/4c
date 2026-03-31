import request from '@/utils/http'

export const fetchCompanyDashboard = () =>
  request.get<any>({ url: '/api/v1/company/dashboard' })

export const fetchCompanyJobs = (params?: any) =>
  request.get<any>({ url: '/api/v1/company/jobs', params })

export const getJob = (jobId: string) =>
  request.get<any>({ url: `/api/v1/company/jobs/${jobId}` })

export interface JobCreateParams {
  title: string
  city?: string
  province?: string
  industry?: string
  min_salary?: number
  max_salary?: number
  min_degree?: number
  min_exp_years?: number
  keywords?: string[]
  description?: string
}

export const createJob = (data: JobCreateParams) =>
  request.post<any>({ url: '/api/v1/company/jobs', data })

export const updateJob = (jobId: string, data: JobCreateParams) =>
  request.put<any>({ url: `/api/v1/company/jobs/${jobId}`, data })

export const deleteJob = (jobId: string) =>
  request.del<any>({ url: `/api/v1/company/jobs/${jobId}` })

export const toggleJobStatus = (jobId: string, status: number) =>
  request.patch<any>({ url: `/api/v1/company/jobs/${jobId}/status`, data: { status } })

export const fetchCompanyProfile = () =>
  request.get<any>({ url: '/api/v1/company/profile' })

export const updateCompanyProfile = (data: any) =>
  request.put<any>({ url: '/api/v1/company/profile', data })