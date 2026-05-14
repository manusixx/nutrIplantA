// ============================================================
// Tipos del dominio nutrI-plantA
// ============================================================

export type UserRole = 'AGRICULTOR' | 'INVESTIGADOR' | 'ADMIN'
export type UserStatus = 'PENDIENTE_APROBACION' | 'APROBADO' | 'RECHAZADO' | 'DESACTIVADO'
export type EstadoGeneral = 'SALUDABLE' | 'REQUIERE_ATENCION' | 'CRITICO'
export type NivelConfianza = 'alta' | 'media' | 'baja'
export type EstadoRecordatorio = 'PENDIENTE' | 'COMPLETADO' | 'OMITIDO'

export interface User {
  id: string
  email: string
  full_name: string
  status: UserStatus
  role: UserRole | null
  created_at: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
  message: string
}

export interface Cultivo {
  id: string
  user_id: string
  nombre_finca: string
  variedad: string
  vereda: string
  fila: string
  subparcela: string
  notas: string
  created_at: string
  updated_at: string
}

export interface Deficiencia {
  nutriente: string
  evidencia_visual: string
  confianza: NivelConfianza
}

export interface Patologia {
  tipo: string
  nombre: string
  evidencia_visual: string
  confianza: NivelConfianza
  urgencia: NivelConfianza
}

export interface Diagnostico {
  id: string
  cultivo_id: string
  user_id: string
  foto_url: string
  confianza_global: number
  estado_general: EstadoGeneral
  es_imagen_valida: boolean
  razon_invalidez: string | null
  estado_fenologico: string | null
  deficiencias: Deficiencia[]
  patologias: Patologia[]
  descripcion_hallazgo: string
  recomendacion_tecnica: string
  recomendacion_natural: string
  created_at: string
}

export interface AplicacionFertilizante {
  producto: string
  dosis: string
  fecha_sugerida: string
  hora_sugerida: string
  observaciones: string
}

export interface PlanAbono {
  id: string
  diagnostico_id: string
  cultivo_id: string
  user_id: string
  aplicaciones: AplicacionFertilizante[]
  observaciones_generales: string
  created_at: string
}

export interface Recordatorio {
  id: string
  plan_id: string
  cultivo_id: string
  producto: string
  dosis: string
  fecha_programada: string
  hora_programada: string
  estado: EstadoRecordatorio
  notas: string
  created_at: string
  updated_at: string
}
