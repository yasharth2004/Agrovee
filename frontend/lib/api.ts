import axios from "axios"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 60000,  // 60s timeout (image uploads can be slow)
})

// Request interceptor - attach JWT token
api.interceptors.request.use(
  (config) => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("access_token")
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor - handle 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("access_token")
      localStorage.removeItem("refresh_token")
      localStorage.removeItem("user")
      window.location.href = "/login"
    }
    return Promise.reject(error)
  }
)

// ---- Auth API ---- //

export interface RegisterData {
  email: string
  password: string
  confirm_password: string
  full_name?: string
  phone?: string
  location?: string
  farm_size?: string
}

export interface LoginData {
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface User {
  id: number
  email: string
  full_name: string | null
  phone: string | null
  location: string | null
  farm_size: string | null
  is_active: boolean
  is_verified: boolean
  profile_picture_url: string | null
  created_at: string
  last_login: string | null
  updated_at?: string
  diagnosis_count: number
}

export const authAPI = {
  register: (data: RegisterData) => api.post<User>("/auth/register", data),
  login: (data: LoginData) => api.post<TokenResponse>("/auth/login", data),
  me: () => api.get<User>("/auth/me"),
  logout: () => api.post("/auth/logout"),
  refresh: () => api.post<TokenResponse>("/auth/refresh"),
  forgotPassword: (email: string) =>
    api.post<{ message: string; reset_code?: string }>("/auth/forgot-password", { email }),
  resetPassword: (token: string, new_password: string, confirm_password: string) =>
    api.post<{ message: string }>("/auth/reset-password", { token, new_password, confirm_password }),
}

// ---- Diagnosis API ---- //

export interface DiagnosisResponse {
  id: number
  user_id: number
  image_filename: string
  image_path: string
  predicted_disease: string | null
  confidence_score: number | null
  crop_type: string | null
  all_predictions: Array<{ disease: string; probability: number }> | null
  weather_data: Record<string, any> | null
  soil_type: string | null
  season: string | null
  fusion_confidence: number | null
  risk_assessment: string | null
  recommendations: Record<string, any> | null
  treatment_plan: string | null
  gradcam_path: string | null
  status: string
  error_message: string | null
  created_at: string
  processed_at: string | null
}

export interface DiagnosisListResponse {
  diagnoses: DiagnosisResponse[]
  total: number
  page: number
  per_page: number
}

export const diagnosisAPI = {
  create: (formData: FormData) =>
    api.post<DiagnosisResponse>("/diagnosis/diagnose", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  get: (id: number) => api.get<DiagnosisResponse>(`/diagnosis/diagnose/${id}`),
  history: (page = 1, perPage = 20) =>
    api.get<DiagnosisListResponse>(`/diagnosis/history?page=${page}&per_page=${perPage}`),
  recent: (limit = 10) => api.get<DiagnosisResponse[]>(`/diagnosis/recent?limit=${limit}`),
  delete: (id: number) => api.delete(`/diagnosis/diagnose/${id}`),
}

// ---- Chat API ---- //

export interface ChatMessage {
  id: number
  session_id: number
  role: "user" | "assistant"
  content: string
  sources: string | null
  created_at: string
}

export interface ChatSession {
  id: number
  user_id: number
  title: string
  is_active: boolean
  message_count: number
  created_at: string
  updated_at: string
}

export interface ChatSessionDetail extends ChatSession {
  messages: ChatMessage[]
}

export interface ChatSessionListResponse {
  sessions: ChatSession[]
  total: number
  page: number
  per_page: number
}

export const chatAPI = {
  sendMessage: (content: string, sessionId?: number, context?: Record<string, any>) =>
    api.post<ChatMessage>("/chat/message", {
      content,
      session_id: sessionId || null,
      context: context || null,
    }),
  sessions: (page = 1, perPage = 20) =>
    api.get<ChatSessionListResponse>(`/chat/sessions?page=${page}&per_page=${perPage}`),
  session: (id: number) => api.get<ChatSessionDetail>(`/chat/sessions/${id}`),
  deleteSession: (id: number) => api.delete(`/chat/sessions/${id}`),
  updateTitle: (id: number, title: string) =>
    api.put(`/chat/sessions/${id}/title?title=${encodeURIComponent(title)}`),
}

// ---- Users API ---- //

export interface UserStats {
  total_diagnoses: number
  healthy_count: number
  diseased_count: number
  most_common_disease: string | null
  average_confidence: number
  recent_diagnoses: DiagnosisResponse[]
}

export const usersAPI = {
  profile: () => api.get<User>("/users/profile"),
  updateProfile: (data: Partial<User>) => api.put<User>("/users/profile", data),
  changePassword: (data: { old_password: string; new_password: string; confirm_password: string }) =>
    api.post("/users/change-password", data),
  stats: () => api.get<UserStats>("/users/stats"),
  deleteAccount: () => api.delete("/users/account"),
}

export default api
