import { useEffect, useState } from 'react'
import { adminApi } from '../../services/api'
import toast from 'react-hot-toast'
import { Users, CheckCircle2, XCircle, UserX, Clock } from 'lucide-react'
import type { User, UserRole } from '../../types'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

const ROL_OPTIONS: UserRole[] = ['AGRICULTOR', 'INVESTIGADOR', 'ADMIN']
const STATUS_CONFIG = {
  PENDIENTE_APROBACION: { label: 'Pendiente', className: 'badge-pendiente' },
  APROBADO: { label: 'Aprobado', className: 'badge-saludable' },
  RECHAZADO: { label: 'Rechazado', className: 'badge-critico' },
  DESACTIVADO: { label: 'Desactivado', className: 'bg-gray-100 text-gray-600 text-xs font-semibold px-2.5 py-1 rounded-full' },
}

type Tab = 'todos' | 'pendientes'

export default function UsuariosAdminPage() {
  const [usuarios, setUsuarios] = useState<User[]>([])
  const [tab, setTab] = useState<Tab>('pendientes')
  const [isLoading, setIsLoading] = useState(true)
  const [selectedRol, setSelectedRol] = useState<Record<string, UserRole>>({})

  const cargar = async () => {
    setIsLoading(true)
    try {
      const response = tab === 'pendientes'
        ? await adminApi.listarPendientes()
        : await adminApi.listarUsuarios()
      setUsuarios(response.data)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => { cargar() }, [tab])

  const handleAprobar = async (user: User) => {
    const rol = selectedRol[user.id] || 'AGRICULTOR'
    try {
      await adminApi.aprobar(user.id, rol)
      toast.success(`Usuario aprobado como ${rol}`)
      cargar()
    } catch (err: any) {
      toast.error(err.response?.data?.message || 'Error al aprobar')
    }
  }

  const handleRechazar = async (user: User) => {
    if (!confirm(`¿Rechazar la solicitud de ${user.full_name}?`)) return
    try {
      await adminApi.rechazar(user.id)
      toast.success('Usuario rechazado')
      cargar()
    } catch {
      toast.error('Error al rechazar')
    }
  }

  const handleDesactivar = async (user: User) => {
    if (!confirm(`¿Desactivar la cuenta de ${user.full_name}?`)) return
    try {
      await adminApi.desactivar(user.id)
      toast.success('Usuario desactivado')
      cargar()
    } catch {
      toast.error('Error al desactivar')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-primary-100 rounded-xl flex items-center justify-center">
          <Users className="w-5 h-5 text-primary-600" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Gestión de Usuarios</h1>
          <p className="text-gray-500 text-sm">{usuarios.length} usuario{usuarios.length !== 1 ? 's' : ''}</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 bg-gray-100 p-1 rounded-xl w-fit">
        <button
          onClick={() => setTab('pendientes')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            tab === 'pendientes'
              ? 'bg-white text-primary-700 shadow-sm'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Pendientes
        </button>
        <button
          onClick={() => setTab('todos')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            tab === 'todos'
              ? 'bg-white text-primary-700 shadow-sm'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Todos
        </button>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center h-48">
          <div className="animate-spin w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full" />
        </div>
      ) : usuarios.length === 0 ? (
        <div className="card text-center py-12">
          <Clock className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">
            {tab === 'pendientes' ? 'No hay solicitudes pendientes' : 'No hay usuarios registrados'}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {usuarios.map(user => {
            const statusCfg = STATUS_CONFIG[user.status]
            return (
              <div key={user.id} className="card flex items-center gap-4">
                {/* Avatar */}
                <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center flex-shrink-0">
                  <span className="text-primary-700 font-bold">
                    {user.full_name.charAt(0).toUpperCase()}
                  </span>
                </div>

                {/* Info */}
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-gray-900 truncate">{user.full_name}</p>
                  <p className="text-sm text-gray-500 truncate">{user.email}</p>
                  <p className="text-xs text-gray-400">
                    {format(new Date(user.created_at), 'd MMM yyyy', { locale: es })}
                    {user.role && ` · ${user.role}`}
                  </p>
                </div>

                {/* Status */}
                <span className={statusCfg.className}>{statusCfg.label}</span>

                {/* Actions */}
                {user.status === 'PENDIENTE_APROBACION' && (
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <select
                      value={selectedRol[user.id] || 'AGRICULTOR'}
                      onChange={e => setSelectedRol(prev => ({ ...prev, [user.id]: e.target.value as UserRole }))}
                      className="text-xs border border-gray-200 rounded-lg px-2 py-1.5 bg-white focus:outline-none focus:ring-1 focus:ring-primary-500"
                    >
                      {ROL_OPTIONS.map(r => <option key={r} value={r}>{r}</option>)}
                    </select>
                    <button
                      onClick={() => handleAprobar(user)}
                      className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                      title="Aprobar"
                    >
                      <CheckCircle2 size={18} />
                    </button>
                    <button
                      onClick={() => handleRechazar(user)}
                      className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                      title="Rechazar"
                    >
                      <XCircle size={18} />
                    </button>
                  </div>
                )}

                {user.status === 'APROBADO' && (
                  <button
                    onClick={() => handleDesactivar(user)}
                    className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors flex-shrink-0"
                    title="Desactivar"
                  >
                    <UserX size={18} />
                  </button>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
