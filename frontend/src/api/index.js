import axios from 'axios'
import { ElMessage } from 'element-plus'

const extractErrorMessages = (data) => {
  if (!data) return []
  
  if (typeof data === 'string') {
    return [data]
  }
  
  if (Array.isArray(data)) {
    return data.flatMap(item => extractErrorMessages(item))
  }
  
  if (typeof data === 'object') {
    const messages = []
    for (const key in data) {
      if (key === 'non_field_errors' || key === 'detail' || key === 'error') {
        messages.push(...extractErrorMessages(data[key]))
      } else {
        const nestedMessages = extractErrorMessages(data[key])
        if (nestedMessages.length > 0) {
          messages.push(...nestedMessages)
        }
      }
    }
    return messages
  }
  
  return []
}

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          localStorage.removeItem('token')
          localStorage.removeItem('refresh')
          window.location.href = '/login'
          ElMessage.error('登录已过期，请重新登录')
          break
        case 403:
          ElMessage.error('没有权限访问')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        default:
          const data = error.response.data
          let errorMsg = '请求失败'
          if (data) {
            if (typeof data === 'string') {
              errorMsg = data
            } else {
              const messages = extractErrorMessages(data)
              if (messages.length > 0) {
                errorMsg = messages.join('；')
              }
            }
          }
          ElMessage.error(errorMsg)
      }
    } else {
      ElMessage.error('网络错误，请检查网络连接')
    }
    return Promise.reject(error)
  }
)

export const authApi = {
  login: (data) => api.post('/token/', data),
  refresh: (data) => api.post('/token/refresh/', data)
}

export const bookApi = {
  getCategories: (params) => api.get('/books/categories/', { params }),
  createCategory: (data) => api.post('/books/categories/', data),
  updateCategory: (id, data) => api.put(`/books/categories/${id}/`, data),
  deleteCategory: (id) => api.delete(`/books/categories/${id}/`),
  getList: (params) => api.get('/books/', { params }),
  getDetail: (id) => api.get(`/books/${id}/`),
  create: (data) => api.post('/books/', data),
  update: (id, data) => api.put(`/books/${id}/`, data),
  delete: (id) => api.delete(`/books/${id}/`),
  getAvailable: () => api.get('/books/available/'),
  checkAvailability: (id) => api.get(`/books/${id}/availability/`)
}

export const readerApi = {
  getList: (params) => api.get('/readers/', { params }),
  getDetail: (id) => api.get(`/readers/${id}/`),
  create: (data) => api.post('/readers/', data),
  update: (id, data) => api.put(`/readers/${id}/`, data),
  delete: (id) => api.delete(`/readers/${id}/`),
  suspend: (id) => api.post(`/readers/${id}/suspend/`),
  activate: (id) => api.post(`/readers/${id}/activate/`),
  close: (id) => api.post(`/readers/${id}/close/`),
  changePassword: (id, data) => api.post(`/readers/${id}/change_password/`, data),
  getCurrentUser: () => api.get('/readers/me/'),
  checkEligibility: (id) => api.get(`/readers/${id}/check_borrow_eligibility/`)
}

export const borrowingApi = {
  getBorrowings: (params) => api.get('/borrowings/borrowings/', { params }),
  getBorrowingDetail: (id) => api.get(`/borrowings/borrowings/${id}/`),
  createBorrowing: (data) => api.post('/borrowings/borrowings/', data),
  returnBook: (id) => api.post(`/borrowings/borrowings/${id}/return_book/`),
  renew: (id) => api.post(`/borrowings/borrowings/${id}/renew/`),
  getMyBorrowings: () => api.get('/borrowings/borrowings/my_borrowings/'),
  getOverdue: () => api.get('/borrowings/borrowings/overdue/'),
  getReservations: (params) => api.get('/borrowings/reservations/', { params }),
  getReservationDetail: (id) => api.get(`/borrowings/reservations/${id}/`),
  createReservation: (data) => api.post('/borrowings/reservations/', data),
  cancelReservation: (id) => api.post(`/borrowings/reservations/${id}/cancel/`),
  claimReservation: (id) => api.post(`/borrowings/reservations/${id}/claim/`),
  getMyReservations: () => api.get('/borrowings/reservations/my_reservations/')
}

export const fineApi = {
  getList: (params) => api.get('/fines/fines/', { params }),
  getDetail: (id) => api.get(`/fines/fines/${id}/`),
  pay: (id) => api.post(`/fines/fines/${id}/pay/`),
  waive: (id, data) => api.post(`/fines/fines/${id}/waive/`, data),
  generateFines: () => api.post('/fines/fines/generate_fines/'),
  getReminders: (params) => api.get('/fines/reminders/', { params }),
  getReminderDetail: (id) => api.get(`/fines/reminders/${id}/`),
  createReminder: (data) => api.post('/fines/reminders/', data),
  markReminderSent: (id) => api.post(`/fines/reminders/${id}/mark_as_sent/`),
  generateReminders: (data) => api.post('/fines/reminders/generate_reminders/', data)
}

export const purchaseApi = {
  getSuggestions: (params) => api.get('/purchases/suggestions/', { params }),
  getSuggestionDetail: (id) => api.get(`/purchases/suggestions/${id}/`),
  createSuggestion: (data) => api.post('/purchases/suggestions/', data),
  updateSuggestion: (id, data) => api.put(`/purchases/suggestions/${id}/`, data),
  cancelSuggestion: (id) => api.post(`/purchases/suggestions/${id}/cancel/`),
  reviewSuggestion: (id, data) => api.post(`/purchases/suggestions/${id}/review/`, data),
  getMySuggestions: () => api.get('/purchases/suggestions/my_suggestions/'),
  getOrders: (params) => api.get('/purchases/orders/', { params }),
  getOrderDetail: (id) => api.get(`/purchases/orders/${id}/`),
  createOrder: (data) => api.post('/purchases/orders/', data),
  updateOrder: (id, data) => api.put(`/purchases/orders/${id}/`, data),
  submitOrder: (id) => api.post(`/purchases/orders/${id}/submit/`),
  approveOrder: (id) => api.post(`/purchases/orders/${id}/approve/`),
  orderPurchase: (id) => api.post(`/purchases/orders/${id}/order/`),
  receiveOrder: (id) => api.post(`/purchases/orders/${id}/receive/`),
  cancelOrder: (id) => api.post(`/purchases/orders/${id}/cancel/`),
  getApprovedSuggestions: () => api.get('/purchases/orders/approved_suggestions/')
}

export const statisticsApi = {
  getDashboard: () => api.get('/statistics/dashboard/'),
  getHotBooks: (params) => api.get('/statistics/hot_books/', { params }),
  getBorrowTrend: (params) => api.get('/statistics/borrow_trend/', { params }),
  getCategoryStatistics: () => api.get('/statistics/category_statistics/'),
  getMonthlyStatistics: (params) => api.get('/statistics/monthly_statistics/', { params }),
  getReaderActivity: () => api.get('/statistics/reader_activity/')
}

export default api
