// src/api/company_announcement.ts
import http from '@/utils/http'

export interface Announcement {
  announcement_id: string
  company_id: string
  title: string
  content: string
  target_major?: string
  target_degree?: number
  headcount?: number
  deadline?: string
  status: number
  published_at?: string
  created_at: string
}

export interface AnnouncementCreate {
  title: string
  content: string
  target_major?: string
  target_degree?: number
  headcount?: number
  deadline?: string
  status?: number
}

export interface AnnouncementQuery {
  status?: number
  year?: number
  page?: number
  page_size?: number
}

export const getAnnouncements = (params?: AnnouncementQuery) =>
  http.get<{ list: Announcement[]; total: number; page: number; page_size: number }>(
    { url: '/company/announcements', params }
  )

export const getAnnouncement = (id: string) =>
  http.get<Announcement>({ url: `/company/announcements/${id}` })

export const createAnnouncement = (data: AnnouncementCreate) =>
  http.post<Announcement>({ url: '/company/announcements', data })

export const updateAnnouncement = (id: string, data: Partial<AnnouncementCreate>) =>
  http.put<Announcement>({ url: `/company/announcements/${id}`, data })

export const deleteAnnouncement = (id: string) =>
  http.delete({ url: `/company/announcements/${id}` })