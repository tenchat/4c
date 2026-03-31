// src/api/stats.ts
import http from '@/utils/http'

export interface EnterpriseStats {
  total_companies: number
  new_companies_this_year: number
  job_demand_this_year: number
  seminars_this_year: number
  job_fairs_this_year: number
  announcements_this_year: number
  positions_this_year: number
  year: number
}

export const getEnterpriseStats = (year?: number) =>
  http.get<EnterpriseStats>({ url: '/admin/enterprise-stats', params: { year } })
