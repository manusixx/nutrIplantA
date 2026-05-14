import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { cultivosApi, diagnosticosApi, recordatoriosApi } from '../../services/api'
import type { Cultivo, Diagnostico, Recordatorio } from '../../types'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

function EstadoChip({ estado }: { estado: string }) {
  if (estado === 'SALUDABLE') return <span className="chip-saludable">Saludable</span>
  if (estado === 'CRITICO') return <span className="chip-critico">Crítico</span>
  return <span className="chip-atencion">Requiere atención</span>
}

function MetricCard({ icon, value, label, color }: {
  icon: string; value: number; label: string; color: string
}) {
  return (
    <div className="card p-6 card-hover">
      <div className="flex items-start justify-between mb-4">
        <div className={`w-10 h-10 ${color} rounded flex items-center justify-center`}>
          <span className="material-symbols-outlined text-white text-xl">{icon}</span>
        </div>
        <span className="font-display text-3xl font-bold text-[#00346f]">{value}</span>
      </div>
      <p className="data-label">{label}</p>
    </div>
  )
}

export default function DashboardPage() {
  const { user } = useAuth()
  const [cultivos, setCultivos] = useState<Cultivo[]>([])
  const [diagnosticos, setDiagnosticos] = useState<Diagnostico[]>([])
  const [recordatorios, setRecordatorios] = useState<Recordatorio[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      cultivosApi.listar(),
      diagnosticosApi.listar(5),
      recordatoriosApi.listar(),
    ]).then(([c, d, r]) => {
      setCultivos(c.data)
      setDiagnosticos(d.data)
      setRecordatorios(r.data)
    }).finally(() => setIsLoading(false))
  }, [])

  const pendientes = recordatorios.filter(r => r.estado === 'PENDIENTE')
  const criticos = diagnosticos.filter(d => d.estado_general === 'CRITICO').length

  if (isLoading) return (
    <div className="flex items-center justify-center h-64">
      <div className="flex flex-col items-center gap-3">
        <div className="w-10 h-10 border-2 border-[#004A99] border-t-transparent rounded-full animate-spin" />
        <p className="text-sm text-[#737783] font-display">Cargando datos del sistema...</p>
      </div>
    </div>
  )

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <header>
        <h1 className="font-display text-3xl font-bold text-[#00346f] mb-1">
          Bienvenido, {user?.full_name?.split(' ')[0]}
        </h1>
        <p className="text-[#424751] text-sm">
          {format(new Date(), "EEEE d 'de' MMMM 'de' yyyy", { locale: es })} ·
          Sistema de diagnóstico nutricional en vid
        </p>
      </header>

      {/* Métricas */}
      <section>
        <h2 className="font-display text-base font-semibold text-[#00346f] uppercase tracking-wider mb-4">
          Resumen del sistema
        </h2>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
          <MetricCard icon="grass" value={cultivos.length} label="Cultivos registrados" color="bg-[#004A99]" />
          <MetricCard icon="biotech" value={diagnosticos.length} label="Diagnósticos realizados" color="bg-[#005914]" />
          <MetricCard icon="notifications_active" value={pendientes.length} label="Recordatorios pendientes" color={pendientes.length > 0 ? 'bg-amber-600' : 'bg-[#737783]'} />
          <MetricCard icon="warning" value={criticos} label="Alertas críticas" color={criticos > 0 ? 'bg-[#b6171e]' : 'bg-[#737783]'} />
        </div>
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Acciones rápidas */}
        <section className="lg:col-span-4">
          <h2 className="font-display text-base font-semibold text-[#00346f] uppercase tracking-wider mb-4">
            Acciones rápidas
          </h2>
          <div className="card overflow-hidden">
            <Link
              to="/diagnosticos/nuevo"
              className="flex items-center gap-4 px-6 py-5 hover:bg-surface-container-low transition-colors border-b border-[#c2c6d3] group"
            >
              <div className="w-10 h-10 bg-[#004A99] rounded flex items-center justify-center flex-shrink-0 group-hover:bg-[#00346f] transition-colors">
                <span className="material-symbols-outlined text-white text-xl">add_a_photo</span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-display font-semibold text-sm text-[#191c1d]">Realizar diagnóstico</p>
                <p className="text-xs text-[#737783]">Analiza una hoja con IA</p>
              </div>
              <span className="material-symbols-outlined text-[#c2c6d3] text-xl">chevron_right</span>
            </Link>
            <Link
              to="/cultivos/nuevo"
              className="flex items-center gap-4 px-6 py-5 hover:bg-surface-container-low transition-colors border-b border-[#c2c6d3] group"
            >
              <div className="w-10 h-10 bg-[#005914] rounded flex items-center justify-center flex-shrink-0 group-hover:bg-[#003f0b] transition-colors">
                <span className="material-symbols-outlined text-white text-xl">grass</span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-display font-semibold text-sm text-[#191c1d]">Registrar cultivo</p>
                <p className="text-xs text-[#737783]">Añade una nueva finca o parcela</p>
              </div>
              <span className="material-symbols-outlined text-[#c2c6d3] text-xl">chevron_right</span>
            </Link>
            {pendientes.length > 0 && (
              <Link
                to="/planes"
                className="flex items-center gap-4 px-6 py-5 hover:bg-surface-container-low transition-colors group"
              >
                <div className="w-10 h-10 bg-amber-600 rounded flex items-center justify-center flex-shrink-0">
                  <span className="material-symbols-outlined text-white text-xl">notifications</span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-display font-semibold text-sm text-[#191c1d]">
                    {pendientes.length} recordatorio{pendientes.length > 1 ? 's' : ''} pendiente{pendientes.length > 1 ? 's' : ''}
                  </p>
                  <p className="text-xs text-[#737783]">Aplicaciones programadas</p>
                </div>
                <span className="material-symbols-outlined text-[#c2c6d3] text-xl">chevron_right</span>
              </Link>
            )}
          </div>
        </section>

        {/* Últimos diagnósticos */}
        <section className="lg:col-span-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-display text-base font-semibold text-[#00346f] uppercase tracking-wider">
              Últimos diagnósticos
            </h2>
            <Link to="/historial" className="text-xs text-[#004A99] font-display font-semibold hover:underline flex items-center gap-1">
              Ver historial completo
              <span className="material-symbols-outlined text-base">open_in_new</span>
            </Link>
          </div>

          {diagnosticos.length === 0 ? (
            <div className="card p-12 text-center">
              <span className="material-symbols-outlined text-5xl text-[#c2c6d3] mb-4 block">biotech</span>
              <h3 className="font-display font-semibold text-[#424751] mb-2">Sin diagnósticos registrados</h3>
              <p className="text-sm text-[#737783] mb-6">Realiza tu primer diagnóstico para ver los resultados aquí.</p>
              <Link to="/diagnosticos/nuevo" className="btn-primary inline-flex">
                <span className="material-symbols-outlined text-lg">add_a_photo</span>
                Realizar primer diagnóstico
              </Link>
            </div>
          ) : (
            <div className="card overflow-hidden">
              <table className="w-full">
                <thead className="bg-surface-container-low border-b border-[#c2c6d3]">
                  <tr>
                    <th className="table-header">Fecha</th>
                    <th className="table-header">Estado</th>
                    <th className="table-header hidden md:table-cell">Confianza IA</th>
                    <th className="table-header text-right">Acción</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#c2c6d3]">
                  {diagnosticos.slice(0, 5).map((d, i) => (
                    <tr key={d.id} className={`hover:bg-surface-container transition-colors ${i % 2 === 1 ? 'bg-surface-container-low' : ''}`}>
                      <td className="table-cell">
                        <p className="data-value">{format(new Date(d.created_at), 'd MMM yyyy', { locale: es })}</p>
                        <p className="data-label">{format(new Date(d.created_at), 'HH:mm')}</p>
                      </td>
                      <td className="table-cell">
                        <EstadoChip estado={d.estado_general} />
                      </td>
                      <td className="table-cell hidden md:table-cell">
                        <div className="flex items-center gap-2">
                          <div className="flex-1 bg-[#e1e3e4] rounded-full h-1.5 max-w-20">
                            <div
                              className="bg-[#004A99] h-1.5 rounded-full"
                              style={{ width: `${Math.round(d.confianza_global * 100)}%` }}
                            />
                          </div>
                          <span className="data-value">{Math.round(d.confianza_global * 100)}%</span>
                        </div>
                      </td>
                      <td className="table-cell text-right">
                        <Link
                          to={`/diagnosticos/${d.id}`}
                          className="text-xs text-[#004A99] font-display font-semibold hover:underline"
                        >
                          Ver informe
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </div>
    </div>
  )
}
