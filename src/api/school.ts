import request from '@/utils/http'

export const fetchSchoolDashboard = () =>
  request.get<any>({ url: '/api/v1/school/dashboard' })

export interface StudentListParams {
  college?: string
  major?: string
  employment_status?: number
  graduation_year?: number
  keyword?: string
  page?: number
  page_size?: number
}

export const fetchSchoolStudents = (params: StudentListParams) =>
  request.get<any>({ url: '/api/v1/school/students', params })

export const importStudents = (formData: FormData) =>
  request.post<any>({ url: '/api/v1/school/students/import', data: formData })

export const fetchSchoolWarnings = (params?: any) =>
  request.get<any>({ url: '/api/v1/school/warnings', params })

export const handleWarning = (warningId: string, data: any) =>
  request.put<any>({ url: `/api/v1/school/warnings/${warningId}`, data })

export const fetchSchoolDataboard = () =>
  request.get<any>({ url: '/api/v1/school/databoard' })

export const fetchSchoolProfile = () =>
  request.get<any>({ url: '/api/v1/school/profile' })

export const updateSchoolProfile = (data: any) =>
  request.put<any>({ url: '/api/v1/school/profile', data })