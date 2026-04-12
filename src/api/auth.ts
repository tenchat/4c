import request from '@/utils/http'

export interface LoginParams {
  username: string
  password: string
  role: 'student' | 'school_admin' | 'company_admin' | 'system_admin'
}

export interface RegisterParams {
  username: string
  password: string
  role: 'student' | 'school_admin' | 'company_admin'
  student_no?: string       // 学生必填
  real_name?: string        // 学生姓名
  enterprise_name?: string  // 企业名称
  registration_code?: string // 学校管理员注册码
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

export interface ChangePasswordParams {
  old_password: string
  new_password: string
}

export const fetchChangePassword = (params: ChangePasswordParams) =>
  request.post<any>({ url: '/api/v1/auth/change-password', data: params })
