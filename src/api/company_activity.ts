// src/api/company_activity.ts
import http from '@/utils/http'

export interface Activity {
  activity_id: string
  company_id: string
  type: 'seminar' | 'job_fair'
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
  type: 'seminar' | 'job_fair'
  title: string
  location?: string
  activity_date: string
  start_time?: string
  end_time?: string
  description?: string
  expected_num?: number
}

export interface ActivityQuery {
  type?: 'seminar' | 'job_fair'
  year?: number
  status?: number
  page?: number
  page_size?: number
}

export const getActivities = (params?: ActivityQuery) =>
  http.get<{ list: Activity[]; total: number; page: number; page_size: number }>(
    { url: '/company/activities', params }
  )

export const getActivity = (id: string) =>
  http.get<Activity>({ url: `/company/activities/${id}` })

export const createActivity = (data: ActivityCreate) =>
  http.post<Activity>({ url: '/company/activities', data })

export const updateActivity = (id: string, data: Partial<ActivityCreate>) =>
  http.put<Activity>({ url: `/company/activities/${id}`, data })

export const deleteActivity = (id: string) =>
  http.delete({ url: `/company/activities/${id}` })