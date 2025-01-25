declare module 'react-query' {
  export * from '@tanstack/react-query'
}

declare module 'axios' {
  export interface AxiosResponse<T = any> {
    data: T
    status: number
    statusText: string
    headers: any
    config: any
  }

  export interface AxiosInstance {
    get<T = any>(url: string): Promise<AxiosResponse<T>>
    post<T = any>(url: string, data?: any): Promise<AxiosResponse<T>>
    put<T = any>(url: string, data?: any): Promise<AxiosResponse<T>>
    delete<T = any>(url: string): Promise<AxiosResponse<T>>
  }

  const axios: AxiosInstance
  export default axios
} 