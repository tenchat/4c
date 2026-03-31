import request from '@/utils/http'

export interface LoginParams {
  username: string
  password: string
  role: 'student' | 'school_admin' | 'company_admin' | 'system_admin'
}

export interface RegisterParams {
  username: string
  password: string
  real_name?: string
  role: 'student' | 'school_admin' | 'company_admin'
}

export const fetchLogin = (params: LoginParams) =>
  request.post<any>({ url: '/api/v1/auth/login', params })

export const fetchRegister = (params: RegisterParams) =>
  request.post<any>({ url: '/api/v1/auth/register', params })

export const fetchLogout = () =>
  request.post<any>({ url: '/api/v1/auth/logout' })

export const fetchMe = () =>
  request.get<any>({ url: '/api/v1/auth/me' })

export const fetchGetUserInfo = () =>
  request.get<any>({ url: '/api/v1/auth/me' })

export const fetchRefresh = () =>
  request.post<any>({ url: '/api/v1/auth/refresh' })