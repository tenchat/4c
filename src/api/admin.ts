import request from '@/utils/http'

export const fetchAdminDashboard = () => request.get<any>({ url: '/api/v1/admin/dashboard' })

export const fetchAdminStatistics = (params?: any) =>
  request.get<any>({ url: '/api/v1/admin/statistics', params })

export const fetchAdminColleges = (params?: any) =>
  request.get<any>({ url: '/api/v1/admin/colleges', params })

export const updateCollege = (recordId: string, data: any) =>
  request.put<any>({ url: `/api/v1/admin/colleges/${recordId}`, data })

export const importColleges = (formData: FormData) =>
  request.post<any>({ url: '/api/v1/admin/colleges/import', data: formData })

export const fetchScarceTalents = (params?: any) =>
  request.get<any>({ url: '/api/v1/admin/scarce-talents', params })

export const fetchAdminDataboard = () => request.get<any>({ url: '/api/v1/admin/databoard' })

export const fetchPendingCompanies = (params?: { status?: number }) =>
  request.get<any>({ url: '/api/v1/admin/companies/pending', params })

export const verifyCompany = (companyId: string, action: 'approve' | 'reject') =>
  request.put<any>({ url: `/api/v1/admin/companies/${companyId}/verify`, data: { action } })

export const fetchPendingProfileUpdates = (params?: {
  status?: string
  current?: number
  size?: number
}) => request.get<any>({ url: '/api/v1/admin/company-profile-updates/pending', params })

export interface ProfileReviewParams {
  action: 'approve' | 'reject'
  reject_reason?: string
}

export const reviewProfileUpdate = (pendingId: string, data: ProfileReviewParams) =>
  request.put<any>({ url: `/api/v1/admin/company-profile-updates/${pendingId}/review`, data })

// 学校管理员账号审核
export const fetchSchoolAdmins = (params?: {
  status?: number
  current?: number
  size?: number
}) => request.get<any>({ url: '/api/v1/admin/school-admins/pending', params })

export const verifySchoolAdmin = (accountId: string, action: 'approve' | 'reject') =>
  request.put<any>({ url: `/api/v1/admin/school-admins/${accountId}/verify`, data: { action } })

// 企业管理员账号审核
export const fetchCompanyAdmins = (params?: {
  status?: number
  current?: number
  size?: number
}) => request.get<any>({ url: '/api/v1/admin/company-admins/pending', params })

export const verifyCompanyAdmin = (accountId: string, action: 'approve' | 'reject') =>
  request.put<any>({ url: `/api/v1/admin/company-admins/${accountId}/verify`, data: { action } })

// 系统配置
export const fetchConfigs = () => request.get<any>({ url: '/api/v1/admin/configs' })

export const updateConfig = (configKey: string, configValue: string, description?: string) =>
  request.put<any>({ url: `/api/v1/admin/configs/${configKey}`, data: { config_value: configValue, description } })
