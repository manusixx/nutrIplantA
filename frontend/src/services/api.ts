import axios from 'axios'

const API_URL = '/api'

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
})

// Interceptor: añadir token en cada petición
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Interceptor: manejar 401 globalmente
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// ============================================================
// Auth
// ============================================================
export const authApi = {
  login: (email: string, password: string) =>
    api.post('/v1/auth/login', { email, password }),

  register: (email: string, full_name: string, password: string) =>
    api.post('/v1/auth/register', { email, full_name, password }),

  logout: () =>
    api.post('/v1/auth/logout'),

  me: () =>
    api.get('/v1/auth/me'),
}

// ============================================================
// Cultivos
// ============================================================
export const cultivosApi = {
  listar: () =>
    api.get('/v1/diagnostico/cultivos'),

  crear: (data: {
    nombre_finca: string
    variedad: string
    vereda?: string
    fila?: string
    subparcela?: string
    notas?: string
  }) => api.post('/v1/diagnostico/cultivos', data),

  obtener: (id: string) =>
    api.get(`/v1/diagnostico/cultivos/${id}`),

  actualizar: (id: string, data: Partial<{
    nombre_finca: string
    variedad: string
    vereda: string
    fila: string
    subparcela: string
    notas: string
  }>) => api.put(`/v1/diagnostico/cultivos/${id}`, data),

  eliminar: (id: string) =>
    api.delete(`/v1/diagnostico/cultivos/${id}`),

  diagnosticos: (id: string) =>
    api.get(`/v1/diagnostico/cultivos/${id}/diagnosticos`),
}

// ============================================================
// Diagnósticos
// ============================================================
export const diagnosticosApi = {
  crear: (cultivo_id: string, foto_url: string) =>
    api.post('/v1/diagnostico/diagnosticos', { cultivo_id, foto_url }),

  listar: (limit = 20, offset = 0) =>
    api.get('/v1/diagnostico/diagnosticos', { params: { limit, offset } }),

  obtener: (id: string) =>
    api.get(`/v1/diagnostico/diagnosticos/${id}`),
}

// ============================================================
// Planes de abono
// ============================================================
export const planesApi = {
  generar: (diagnostico_id: string) =>
    api.post('/v1/diagnostico/planes', { diagnostico_id }),

  listar: () =>
    api.get('/v1/diagnostico/planes'),
}

// ============================================================
// Recordatorios
// ============================================================
export const recordatoriosApi = {
  listar: () =>
    api.get('/v1/diagnostico/recordatorios'),

  completar: (id: string, notas = '') =>
    api.patch(`/v1/diagnostico/recordatorios/${id}/completar`, { notas }),
}

// ============================================================
// Admin
// ============================================================
export const adminApi = {
  listarUsuarios: () =>
    api.get('/v1/admin/users'),

  listarPendientes: () =>
    api.get('/v1/admin/users/pendientes'),

  aprobar: (user_id: string, rol: string) =>
    api.post(`/v1/admin/users/${user_id}/aprobar`, { rol }),

  rechazar: (user_id: string) =>
    api.post(`/v1/admin/users/${user_id}/rechazar`),

  desactivar: (user_id: string) =>
    api.post(`/v1/admin/users/${user_id}/desactivar`),
}

export default api
