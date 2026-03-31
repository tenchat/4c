import request from '@/utils/http'

export const fetchAdminDashboard = () =>
  request.get<any>({ url: '/api/v1/admin/dashboard' })

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

export const fetchAdminDataboard = () =>
  request.get<any>({ url: '/api/v1/admin/databoard' })

export const fetchPendingCompanies = (params?: { status?: number }) =>
  request.get<any>({ url: '/api/v1/admin/companies/pending', params })

export const verifyCompany = (companyId: string, action: 'approve' | 'reject') =>
  request.put<any>({ url: `/api/v1/admin/companies/${companyId}/verify`, data: { action } })