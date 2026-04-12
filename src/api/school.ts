import request from '@/utils/http'
import axios from 'axios'
import { useUserStore } from '@/store/modules/user'

export const fetchSchoolDashboard = () =>
  request.get<any>({ url: '/api/v1/school/dashboard' })

export interface StudentListParams {
  college?: string
  major?: string
  employment_status?: number
  graduation_year?: number
  keyword?: string
  is_registered?: boolean
  profile_ids?: string[]  // 用于批量导出选中学生
  page?: number
  page_size?: number
}

export const fetchSchoolStudents = (params: StudentListParams) =>
  request.get<any>({ url: '/api/v1/school/students', params })

export const exportSchoolStudents = (params: StudentListParams) => {
  const { VITE_API_BASE_URL } = import.meta.env
  // 转换profile_ids数组为逗号分隔字符串
  const exportParams = {
    ...params,
    profile_ids: params.profile_ids?.join(',')
  }
  return axios.get(`${VITE_API_BASE_URL}/api/v1/school/students/export`, {
    params: exportParams,
    responseType: 'blob',
    timeout: 60000,
    headers: {
      Authorization: `Bearer ${useUserStore().accessToken}`
    }
  })
}

export const fetchStudentDetail = (profileId: string) =>
  request.get<any>({ url: `/api/v1/school/students/${profileId}` })

export const importStudents = (formData: FormData) =>
  request.post<any>({ url: '/api/v1/school/students/import', data: formData })

export const importStudentsPreview = (formData: FormData) =>
  request.post<any>({ url: '/api/v1/school/students/import/preview', data: formData })

export const confirmImportStudents = (students: any[]) =>
  request.post<any>({ url: '/api/v1/school/students/confirm-import', data: { students } })

export const batchDeleteStudents = (profileIds: string[]) =>
  request.del<any>({ url: '/api/v1/school/students/batch', data: { profile_ids: profileIds } })

export const batchUpdateStudents = (profileIds: string[], updates: Record<string, unknown>) =>
  request.put<any>({ url: '/api/v1/school/students/batch', data: { profile_ids: profileIds, updates } })

export const fetchSchoolWarnings = (params?: any) =>
  request.get<any>({ url: '/api/v1/school/warnings', params })

export const handleWarning = (warningId: string, data: any) =>
  request.put<any>({ url: `/api/v1/school/warnings/${warningId}`, data })

export const fetchSchoolDataboard = (year?: number) =>
  request.get<any>({ url: '/api/v1/school/databoard', params: year ? { year } : undefined })

export const fetchWordCloudData = () =>
  request.get<any>({ url: '/api/v1/school/databoard/word-cloud' })

export const fetchJobTitlesStats = () =>
  request.get<any>({ url: '/api/v1/school/databoard/job-titles' })

export interface ProvinceDetailParams {
  province: string
  tab?: 'students' | 'companies'
  page?: number
  page_size?: number
  year?: number
}

export const fetchProvinceDetail = (params: ProvinceDetailParams) =>
  request.get<any>({ url: `/api/v1/school/databoard/province/${params.province}`, params: {
    tab: params.tab,
    page: params.page,
    page_size: params.page_size,
    year: params.year,
  }})

export const fetchSchoolProfile = () =>
  request.get<any>({ url: '/api/v1/school/profile' })

export const updateSchoolProfile = (data: any) =>
  request.put<any>({ url: `/api/v1/school/profile`, data })

// 学院就业管理
export const fetchSchoolColleges = (params?: {
  year?: number
  current?: number
  size?: number
  group_by?: boolean
}) =>
  request.get<any>({ url: '/api/v1/school/colleges', params })

export interface CompanyAnnouncement {
  announcement_id: string
  title: string
  company_name: string
  city?: string
  target_major?: string
  target_degree?: number
  headcount?: number
  deadline?: string
  content?: string
  published_at?: string
}

export interface CompanyActivity {
  activity_id: string
  title: string
  company_name: string
  city?: string
  type?: string
  activity_date?: string
  start_time?: string
  end_time?: string
  location?: string
  expected_num?: number
  actual_num?: number
  description?: string
}

export interface CompanyAnnouncementParams {
  keyword?: string
  company_name?: string
  major?: string
  degree?: number
  year?: number
  page?: number
  page_size?: number
}

export interface CompanyActivityParams {
  keyword?: string
  company_name?: string
  activity_type?: string
  year?: number
  page?: number
  page_size?: number
}

export const fetchCompanyAnnouncements = (params?: CompanyAnnouncementParams) =>
  request.get<any>({ url: '/api/v1/school/company/announcements', params })

export const fetchCompanyAnnouncementDetail = (id: string) =>
  request.get<any>({ url: `/api/v1/school/company/announcements/${id}` })

export const fetchCompanyActivities = (params?: CompanyActivityParams) =>
  request.get<any>({ url: '/api/v1/school/company/activities', params })

export const fetchCompanyActivityDetail = (id: string) =>
  request.get<any>({ url: `/api/v1/school/company/activities/${id}` })
