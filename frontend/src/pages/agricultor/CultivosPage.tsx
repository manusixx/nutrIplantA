import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { cultivosApi } from '../../services/api'
import toast from 'react-hot-toast'
import { Plus, Sprout, ChevronRight, Trash2, Edit } from 'lucide-react'
import type { Cultivo } from '../../types'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

const VARIEDADES_LABELS: Record<string, string> = {
  Isabella: 'Isabella',
  'Cabernet Sauvignon': 'Cabernet Sauvignon',
  Malbec: 'Malbec',
  Syrah: 'Syrah',
  Tempranillo: 'Tempranillo',
  Chardonnay: 'Chardonnay',
  Merlot: 'Merlot',
  'Pinot Noir': 'Pinot Noir',
  'Sauvignon Blanc': 'Sauvignon Blanc',
  Muscat: 'Muscat',
}

export default function CultivosPage() {
  const [cultivos, setCultivos] = useState<Cultivo[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    cultivosApi.listar()
      .then(r => setCultivos(r.data))
      .finally(() => setIsLoading(false))
  }, [])

  const handleEliminar = async (id: string, nombre: string) => {
    if (!confirm(`¿Eliminar el cultivo "${nombre}"? Esta acción no se puede deshacer.`)) return
    try {
      await cultivosApi.eliminar(id)
      setCultivos(prev => prev.filter(c => c.id !== id))
      toast.success('Cultivo eliminado')
    } catch {
      toast.error('No se pudo eliminar el cultivo')
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full" />
      </div>
    )
  }

  return (
    <div className="space-y-6 pt-2">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-3xl font-bold text-[#00346f]">Mis Cultivos</h1>
          <p className="text-gray-500 mt-1">{cultivos.length} cultivo{cultivos.length !== 1 ? 's' : ''} registrado{cultivos.length !== 1 ? 's' : ''}</p>
        </div>
        <Link to="/cultivos/nuevo" className="btn-primary flex items-center gap-2 flex-shrink-0">
          <Plus size={18} />
          Nuevo cultivo
        </Link>
      </div>

      {cultivos.length === 0 ? (
        <div className="card text-center py-16">
          <Sprout className="w-16 h-16 text-gray-200 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-700">Sin cultivos registrados</h3>
          <p className="text-gray-500 mt-2 mb-6">Registra tu primer cultivo de vid para comenzar el diagnóstico.</p>
          <Link to="/cultivos/nuevo" className="btn-primary inline-flex items-center gap-2">
            <Plus size={18} />
            Registrar cultivo
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {cultivos.map(cultivo => (
            <div key={cultivo.id} className="card p-6 hover:shadow-card-hover transition-shadow">
              <div className="flex items-start justify-between mb-3">
                <div className="w-10 h-10 bg-primary-100 rounded-xl flex items-center justify-center">
                  <Sprout className="w-5 h-5 text-primary-600" />
                </div>
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => navigate(`/cultivos/${cultivo.id}/editar`)}
                    className="p-2 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                  >
                    <Edit size={16} />
                  </button>
                  <button
                    onClick={() => handleEliminar(cultivo.id, cultivo.nombre_finca)}
                    className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>

              <h3 className="font-bold text-gray-900 mb-1">{cultivo.nombre_finca}</h3>
              <p className="text-sm text-primary-600 font-medium mb-3">
                {VARIEDADES_LABELS[cultivo.variedad] || cultivo.variedad}
              </p>

              <div className="space-y-1 text-xs text-gray-500 mb-4">
                {cultivo.vereda && <p>📍 {cultivo.vereda}</p>}
                {cultivo.fila && <p>🌿 Fila: {cultivo.fila} {cultivo.subparcela && `· ${cultivo.subparcela}`}</p>}
                <p>📅 {format(new Date(cultivo.created_at), 'd MMM yyyy', { locale: es })}</p>
              </div>

              <div className="flex gap-2">
                <Link
                  to={`/diagnosticos/nuevo?cultivo=${cultivo.id}`}
                  className="flex-1 text-center text-xs font-medium text-primary-700 bg-primary-50 hover:bg-primary-100 py-2 rounded-lg transition-colors"
                >
                  Diagnosticar
                </Link>
                <Link
                  to={`/cultivos/${cultivo.id}/diagnosticos`}
                  className="flex-1 flex items-center justify-center gap-1 text-xs font-medium text-gray-600 bg-gray-50 hover:bg-gray-100 py-2 rounded-lg transition-colors"
                >
                  Historial
                  <ChevronRight size={12} />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
