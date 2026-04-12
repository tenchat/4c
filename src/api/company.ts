import request from '@/utils/http'

export const fetchCompanyDashboard = () => request.get<any>({ url: '/api/v1/company/dashboard' })

export const fetchEnterpriseDataboard = (year?: number) =>
  request.get<any>({ url: '/api/v1/company/enterprise-databoard', params: year ? { year } : undefined })

export const fetchEnterpriseWordCloud = () =>
  request.get<any>({ url: '/api/v1/company/enterprise-databoard/word-cloud' })

export const fetchEnterpriseJobTitles = () =>
  request.get<any>({ url: '/api/v1/company/enterprise-databoard/job-titles' })

export const fetchCompanyJobs = (params?: any) =>
  request.get<any>({ url: '/api/v1/company/jobs', params })

export const getJob = (jobId: string) => request.get<any>({ url: `/api/v1/company/jobs/${jobId}` })

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

export const fetchCompanyProfile = () => request.get<any>({ url: '/api/v1/company/profile' })

export const updateCompanyProfile = (data: any) =>
  request.put<any>({ url: '/api/v1/company/profile', data })

export interface ProfileUpdateParams {
  company_name: string
  industry?: string
  city?: string
  size?: string
  description?: string
  address?: string
  email?: string
  contact?: string
  contact_phone?: string
}

export const submitCompanyProfileForReview = (data: ProfileUpdateParams) =>
  request.post<any>({ url: '/api/v1/company/profile/submit', data })

export const fetchPendingProfile = () =>
  request.get<any>({ url: '/api/v1/company/profile/pending' })

// 简历管理
export interface ResumeListParams {
  status?: number
  page?: number
  page_size?: number
}

export const fetchCompanyResumes = (params?: ResumeListParams) =>
  request.get<any>({ url: '/api/v1/company/resumes', params })

export const updateResumeStatus = (applicationId: string, status: number) =>
  request.patch<any>({
    url: `/api/v1/company/resumes/${applicationId}/status`,
    data: { status }
  })

export const fetchStudentByAccount = (accountId: string) =>
  request.get<any>({ url: `/api/v1/company/resumes/student/${accountId}` })
