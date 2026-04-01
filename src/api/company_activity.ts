// src/api/company_activity.ts
import http from '@/utils/http'

export interface Activity {
  activity_id: string
  company_id: string
  type: 'seminar' | 'job_fair' | 'other'
  type_name?: string
  title: string
  location?: string
  activity_date: string
  start_time?: string
  end_time?: string
  description?: string
  status: number
  expected_num?: number
  actual_num?: number
  created_at: string
}

export interface ActivityCreate {
  type: 'seminar' | 'job_fair' | 'other'
  type_name?: string
  title: string
  location?: string
  activity_date: string
  start_time?: string
  end_time?: string
  description?: string
  expected_num?: number
}

export interface ActivityQuery {
  type?: 'seminar' | 'job_fair' | 'other'
  year?: number
  status?: number
  min_expected_num?: number
  max_expected_num?: number
  page?: number
  page_size?: number
}

export const getActivities = (params?: ActivityQuery) =>
  http.get<{ list: Activity[]; total: number; page: number; page_size: number }>({
    url: '/api/v1/company/activities',
    params
  })

export const getActivity = (id: string) =>
  http.get<Activity>({ url: `/api/v1/company/activities/${id}` })

export const createActivity = (data: ActivityCreate) =>
  http.post<Activity>({ url: '/api/v1/company/activities', data })

export const updateActivity = (id: string, data: Partial<ActivityCreate>) =>
  http.put<Activity>({ url: `/api/v1/company/activities/${id}`, data })

export const deleteActivity = (id: string) => http.del({ url: `/api/v1/company/activities/${id}` })

export const toggleActivityStatus = (id: string, status: number) =>
  http.patch<Activity>({ url: `/api/v1/company/activities/${id}/status`, params: { status } })
