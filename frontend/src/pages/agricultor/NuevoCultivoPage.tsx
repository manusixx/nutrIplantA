import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { cultivosApi } from '../../services/api'
import toast from 'react-hot-toast'
import { ArrowLeft } from 'lucide-react'

const VARIEDADES = [
  'Isabella', 'Cabernet Sauvignon', 'Malbec', 'Syrah', 'Tempranillo',
  'Chardonnay', 'Merlot', 'Pinot Noir', 'Sauvignon Blanc', 'Muscat',
]

export default function NuevoCultivoPage() {
  const navigate = useNavigate()
  const [isLoading, setIsLoading] = useState(false)
  const [form, setForm] = useState({
    nombre_finca: '',
    variedad: '',
    vereda: '',
    fila: '',
    subparcela: '',
    notas: '',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.variedad) {
      toast.error('Selecciona una variedad de vid')
      return
    }
    setIsLoading(true)
    try {
      await cultivosApi.crear(form)
      toast.success('Cultivo registrado exitosamente')
      navigate('/cultivos')
    } catch (err: any) {
      toast.error(err.response?.data?.message || 'Error al registrar el cultivo')
    } finally {
      setIsLoading(false)
    }
  }

  const set = (key: string, value: string) => setForm(prev => ({ ...prev, [key]: value }))

  return (
    <div className="max-w-xl mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <button onClick={() => navigate(-1)} className="p-2 text-gray-500 hover:bg-gray-100 rounded-xl">
          <ArrowLeft size={20} />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Nuevo Cultivo</h1>
          <p className="text-gray-500 text-sm">Registra un cultivo de Vitis vinifera</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="card space-y-5">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Nombre de la finca *
          </label>
          <input
            type="text"
            value={form.nombre_finca}
            onChange={e => set('nombre_finca', e.target.value)}
            placeholder="Finca El Paraíso"
            className="input-field"
            required
            minLength={2}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Variedad de vid *
          </label>
          <select
            value={form.variedad}
            onChange={e => set('variedad', e.target.value)}
            className="input-field"
            required
          >
            <option value="">Selecciona una variedad</option>
            {VARIEDADES.map(v => (
              <option key={v} value={v}>{v}</option>
            ))}
          </select>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Vereda
            </label>
            <input
              type="text"
              value={form.vereda}
              onChange={e => set('vereda', e.target.value)}
              placeholder="El Placer"
              className="input-field"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Fila
            </label>
            <input
              type="text"
              value={form.fila}
              onChange={e => set('fila', e.target.value)}
              placeholder="A1"
              className="input-field"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Subparcela
          </label>
          <input
            type="text"
            value={form.subparcela}
            onChange={e => set('subparcela', e.target.value)}
            placeholder="Norte"
            className="input-field"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Notas adicionales
          </label>
          <textarea
            value={form.notas}
            onChange={e => set('notas', e.target.value)}
            placeholder="Observaciones sobre el cultivo..."
            className="input-field resize-none h-24"
            maxLength={1000}
          />
        </div>

        <div className="flex gap-3 pt-2">
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="btn-secondary flex-1"
          >
            Cancelar
          </button>
          <button type="submit" disabled={isLoading} className="btn-primary flex-1">
            {isLoading ? 'Guardando...' : 'Registrar cultivo'}
          </button>
        </div>
      </form>
    </div>
  )
}
