import { useEffect, useState, useRef } from 'react'
import { useNavigate, useSearchParams, Link, useParams } from 'react-router-dom'
import { cultivosApi, diagnosticosApi, planesApi } from '../../services/api'
import toast from 'react-hot-toast'
import type { Cultivo, Diagnostico } from '../../types'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

// ============================================================
// Nuevo Diagnóstico
// ============================================================
export function NuevoDiagnosticoPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const cultivoPresel = searchParams.get('cultivo') || ''
  const [cultivos, setCultivos] = useState<Cultivo[]>([])
  const [cultivoId, setCultivoId] = useState(cultivoPresel)
  const [fotoUrl, setFotoUrl] = useState('')
  const [fotoNombre, setFotoNombre] = useState('')
  const [fase, setFase] = useState<'captura' | 'analizando' | 'listo'>('captura')
  const [isLoading, setIsLoading] = useState(false)
  const [diagnosticoId, setDiagnosticoId] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)
  const cameraInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    cultivosApi.listar().then(r => setCultivos(r.data))
  }, [])

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setFotoUrl(`minio://diagnosticos/${file.name}`)
      setFotoNombre(file.name)
      toast.success(`Imagen seleccionada: ${file.name}`)
    }
  }

  const handleDiagnosticar = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!cultivoId) { toast.error('Selecciona un cultivo'); return }
    const url = fotoUrl || `minio://diagnosticos/muestra_${Date.now()}.jpg`
    setFase('analizando')
    setIsLoading(true)
    try {
      const response = await diagnosticosApi.crear(cultivoId, url)
      setDiagnosticoId(response.data.id)
      setFase('listo')
    } catch (err: any) {
      toast.error(err.response?.data?.message || 'Error al procesar la imagen')
      setFase('captura')
    } finally { setIsLoading(false) }
  }

  return (
    <div className="space-y-6">
      <header>
        <button onClick={() => navigate(-1)} className="flex items-center gap-1 text-sm text-[#737783] hover:text-[#004A99] mb-4 transition-colors">
          <span className="material-symbols-outlined text-lg">arrow_back</span>
          Volver
        </button>
        <h1 className="font-display text-3xl font-bold text-[#00346f] mb-1">Diagnóstico de Cultivo</h1>
        <p className="text-[#424751] text-sm max-w-2xl">
          Identifique deficiencias nutricionales en sus vides de forma instantánea utilizando inteligencia artificial avanzada.
        </p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        <div className="lg:col-span-7 space-y-6">
          <div className="card p-8">
            <h3 className="font-display text-lg font-semibold text-[#00346f] mb-6 flex items-center gap-2">
              <span className="material-symbols-outlined text-[#004A99]">add_a_photo</span>
              Captura de Muestra
            </h3>

            <input ref={fileInputRef} type="file" accept="image/*" className="hidden" onChange={handleFileChange} />
            <input ref={cameraInputRef} type="file" accept="image/*" capture="environment" className="hidden" onChange={handleFileChange} />

            <div
              onClick={() => fase === 'captura' && fileInputRef.current?.click()}
              className="relative w-full aspect-video bg-surface-container rounded overflow-hidden border-2 border-dashed border-[#c2c6d3] flex flex-col items-center justify-center hover:border-[#004A99] transition-colors cursor-pointer mb-6"
            >
              {fase === 'analizando' ? (
                <>
                  <div className="scan-line" />
                  <div className="relative z-10 bg-white/90 px-6 py-3 rounded-full flex items-center gap-3 shadow-lg">
                    <div className="w-5 h-5 border-2 border-[#004A99] border-t-transparent rounded-full animate-spin" />
                    <span className="font-display text-sm font-semibold text-[#004A99]">Identificando Patrones...</span>
                  </div>
                </>
              ) : fase === 'listo' ? (
                <div className="flex flex-col items-center text-center px-6">
                  <span className="material-symbols-outlined text-[#005914] text-6xl mb-3" style={{ fontVariationSettings: "'FILL' 1" }}>check_circle</span>
                  <p className="font-display font-semibold text-[#003f0b] text-lg">Análisis completado</p>
                  <p className="text-sm text-[#424751] mt-1">Revisa el resultado en el panel derecho</p>
                </div>
              ) : fotoNombre ? (
                <div className="flex flex-col items-center text-center px-6">
                  <span className="material-symbols-outlined text-[#004A99] text-6xl mb-3" style={{ fontVariationSettings: "'FILL' 1" }}>image</span>
                  <p className="font-display font-semibold text-[#004A99] text-lg mb-1">Imagen lista</p>
                  <p className="text-sm text-[#737783] max-w-xs truncate">{fotoNombre}</p>
                  <p className="text-xs text-[#004A99] mt-2 underline">Clic para cambiar la imagen</p>
                </div>
              ) : (
                <div className="flex flex-col items-center text-center px-6">
                  <span className="material-symbols-outlined text-[#004A99] text-6xl mb-3">add_a_photo</span>
                  <p className="font-display font-semibold text-[#424751] text-lg mb-1">Clic para seleccionar foto</p>
                  <p className="text-sm text-[#737783]">JPG, PNG — la hoja debe estar bien iluminada y centrada</p>
                </div>
              )}
            </div>

            <form onSubmit={handleDiagnosticar} className="space-y-4">
              <div>
                <label className="input-label">Cultivo a diagnosticar *</label>
                <select value={cultivoId} onChange={e => setCultivoId(e.target.value)} className="input-field" required>
                  <option value="">Seleccione un cultivo...</option>
                  {cultivos.map(c => (
                    <option key={c.id} value={c.id}>{c.nombre_finca} — {c.variedad}</option>
                  ))}
                </select>
              </div>

              {fotoNombre && (
                <div className="flex items-center gap-2 px-3 py-2 bg-surface-container-low rounded border border-[#c2c6d3]">
                  <span className="material-symbols-outlined text-[#004A99] text-lg">image</span>
                  <span className="text-xs text-[#424751] truncate flex-1">{fotoNombre}</span>
                  <span className="material-symbols-outlined text-[#005914] text-lg flex-shrink-0" style={{ fontVariationSettings: "'FILL' 1" }}>check_circle</span>
                </div>
              )}

              <div className="grid grid-cols-2 gap-3">
                <button type="button" onClick={() => cameraInputRef.current?.click()}
                  className="btn-secondary py-3 flex items-center justify-center gap-2 text-sm">
                  <span className="material-symbols-outlined text-lg">camera_alt</span>
                  Tomar foto
                </button>
                <button type="button" onClick={() => fileInputRef.current?.click()}
                  className="btn-secondary py-3 flex items-center justify-center gap-2 text-sm">
                  <span className="material-symbols-outlined text-lg">upload_file</span>
                  Subir desde galería
                </button>
              </div>

              <button type="submit" disabled={isLoading || fase === 'analizando'} className="btn-primary w-full py-4">
                {fase === 'analizando' ? (
                  <><div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />Analizando con IA...</>
                ) : (
                  <><span className="material-symbols-outlined">analytics</span>Analizar con IA</>
                )}
              </button>
            </form>
          </div>

          {fase === 'analizando' && (
            <div className="card p-8">
              <div className="flex items-center gap-3 mb-6">
                <span className="material-symbols-outlined text-[#004A99]">analytics</span>
                <h3 className="font-display text-lg font-semibold text-[#00346f]">Procesando con IA</h3>
              </div>
              <div className="space-y-3">
                {['Preprocesando imagen...', 'Extrayendo características foliares...', 'Comparando con base de datos...', 'Generando diagnóstico...'].map((step, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <div className={`w-4 h-4 rounded-full border-2 ${i === 0 ? 'border-[#004A99] border-t-transparent animate-spin' : 'border-[#c2c6d3]'}`} />
                    <span className={`text-sm ${i === 0 ? 'text-[#004A99] font-medium' : 'text-[#737783]'}`}>{step}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="lg:col-span-5">
          {fase === 'listo' && diagnosticoId ? (
            <div className="card overflow-hidden">
              <div className="bg-[#005914] text-[#7ecf79] px-6 py-4 flex justify-between items-center">
                <span className="font-display font-semibold">Resultado del Análisis</span>
                <Link to={`/diagnosticos/${diagnosticoId}`}
                  className="bg-[#7ecf79] text-[#002204] px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider hover:bg-[#a3f69c] transition-colors">
                  Ver informe →
                </Link>
              </div>
              <div className="p-6">
                <div className="flex items-center gap-3 mb-4">
                  <span className="material-symbols-outlined text-[#005914] text-4xl" style={{ fontVariationSettings: "'FILL' 1" }}>check_circle</span>
                  <div>
                    <p className="font-display font-bold text-lg text-[#003f0b]">Análisis completado</p>
                    <p className="text-sm text-[#424751]">El informe detallado está disponible</p>
                  </div>
                </div>
                <Link to={`/diagnosticos/${diagnosticoId}`} className="btn-primary w-full py-3 mt-2">
                  <span className="material-symbols-outlined">description</span>
                  Ver informe de diagnóstico
                </Link>
              </div>
            </div>
          ) : (
            <div className="card overflow-hidden">
              <div className="bg-[#004A99] text-white px-6 py-4">
                <span className="font-display font-semibold">Resultado del Análisis</span>
              </div>
              <div className="p-8 text-center">
                <span className="material-symbols-outlined text-5xl text-[#c2c6d3] mb-4 block">pending_actions</span>
                <p className="text-sm text-[#737783]">El resultado aparecerá aquí después de analizar la imagen</p>
              </div>
              <div className="border-t border-[#c2c6d3] px-6 py-4 bg-surface-container-low">
                <h4 className="font-display text-xs font-bold text-[#004A99] uppercase tracking-wide mb-3">Deficiencias detectables</h4>
                <div className="flex flex-wrap gap-1.5">
                  {['Nitrógeno (N)', 'Fósforo (P)', 'Potasio (K)', 'Magnesio (Mg)', 'Hierro (Fe)', 'Manganeso (Mn)', 'Boro (B)', 'Zinc (Zn)'].map(n => (
                    <span key={n} className="chip-neutral text-xs">{n}</span>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// ============================================================
// Detalle de diagnóstico
// ============================================================
export function DetalleDiagnosticoPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [diagnostico, setDiagnostico] = useState<Diagnostico | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [generandoPlan, setGenerandoPlan] = useState(false)

  useEffect(() => {
    if (!id) return
    diagnosticosApi.obtener(id)
      .then(r => setDiagnostico(r.data))
      .catch(() => toast.error('No se pudo cargar el diagnóstico'))
      .finally(() => setIsLoading(false))
  }, [id])

  const handleGenerarPlan = async () => {
    if (!diagnostico) return
    setGenerandoPlan(true)
    try {
      await planesApi.generar(diagnostico.id)
      toast.success('Plan de abono generado')
      navigate('/planes')
    } catch (err: any) {
      toast.error(err.response?.data?.message || 'No se puede generar el plan')
    } finally { setGenerandoPlan(false) }
  }

  if (isLoading) return (
    <div className="flex items-center justify-center h-64">
      <div className="w-10 h-10 border-2 border-[#004A99] border-t-transparent rounded-full animate-spin" />
    </div>
  )
  if (!diagnostico) return null

  const confianzaPct = Math.round(diagnostico.confianza_global * 100)
  const estadoConfig = {
    SALUDABLE: { header: 'bg-[#005914]', text: '#7ecf79', label: 'Saludable', icon: 'check_circle' },
    REQUIERE_ATENCION: { header: 'bg-amber-700', text: '#fef3c7', label: 'Requiere atención', icon: 'warning' },
    CRITICO: { header: 'bg-[#93000a]', text: '#ffdad6', label: 'Estado crítico', icon: 'dangerous' },
  }[diagnostico.estado_general]!

  return (
    <div className="space-y-6">
      <header>
        <button onClick={() => navigate(-1)} className="flex items-center gap-1 text-sm text-[#737783] hover:text-[#004A99] mb-4 transition-colors">
          <span className="material-symbols-outlined text-lg">arrow_back</span>
          Volver al historial
        </button>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="font-display text-3xl font-bold text-[#00346f] mb-1">Informe de Diagnóstico</h1>
            <p className="text-[#424751] text-sm">
              {format(new Date(diagnostico.created_at), "d 'de' MMMM 'de' yyyy 'a las' HH:mm", { locale: es })}
            </p>
          </div>
          <span className="chip-neutral font-display">ID: {diagnostico.id.slice(0, 8).toUpperCase()}</span>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        <div className="lg:col-span-7 space-y-6">
          <div className="card p-6">
            <h3 className="font-display font-semibold text-[#00346f] mb-4 flex items-center gap-2">
              <span className="material-symbols-outlined text-[#004A99]">image_search</span>
              Muestra analizada
            </h3>
            <div className="relative aspect-video bg-surface-container-low rounded overflow-hidden border border-[#c2c6d3] flex items-center justify-center">
              <span className="material-symbols-outlined text-7xl text-[#c2c6d3]">eco</span>
              <div className="absolute bottom-3 right-3">
                <span className="bg-white/90 text-[#004A99] text-xs font-bold font-display px-2 py-1 rounded border border-[#004A99]">
                  Confianza: {confianzaPct}%
                </span>
              </div>
            </div>
            <div className="mt-4 grid grid-cols-3 gap-4">
              <div className="text-center p-3 bg-surface-container-low rounded">
                <p className="data-label mb-1">Estado general</p>
                <p className="font-display font-bold text-sm text-[#191c1d]">{estadoConfig.label}</p>
              </div>
              <div className="text-center p-3 bg-surface-container-low rounded">
                <p className="data-label mb-1">Confianza IA</p>
                <p className="font-display font-bold text-sm text-[#004A99]">{confianzaPct}%</p>
              </div>
              <div className="text-center p-3 bg-surface-container-low rounded">
                <p className="data-label mb-1">Fase fenológica</p>
                <p className="font-display font-bold text-sm text-[#191c1d]">{diagnostico.estado_fenologico || '—'}</p>
              </div>
            </div>
          </div>

          {diagnostico.descripcion_hallazgo && (
            <div className="card p-6">
              <h3 className="font-display font-semibold text-[#00346f] mb-3 flex items-center gap-2">
                <span className="material-symbols-outlined text-[#004A99]">description</span>
                Descripción del hallazgo
              </h3>
              <p className="text-sm text-[#424751] leading-relaxed">{diagnostico.descripcion_hallazgo}</p>
            </div>
          )}

          {diagnostico.recomendacion_tecnica && (
            <div className="card p-6 border-l-4 border-[#004A99]">
              <h3 className="font-display font-semibold text-[#00346f] mb-3 flex items-center gap-2">
                <span className="material-symbols-outlined text-[#004A99]">clinical_notes</span>
                Recomendación técnica
              </h3>
              <p className="text-sm text-[#424751] leading-relaxed">{diagnostico.recomendacion_tecnica}</p>
            </div>
          )}
        </div>

        <div className="lg:col-span-5 space-y-4">
          <div className="card overflow-hidden">
            <div className={`${estadoConfig.header} px-6 py-4 flex justify-between items-center`}>
              <span className="font-display font-semibold" style={{ color: estadoConfig.text }}>
                Resultado del Análisis
              </span>
              <span className="bg-white/20 text-white px-3 py-1 rounded-full text-xs font-bold uppercase font-display">
                {confianzaPct}% confianza
              </span>
            </div>
            <div className="p-6">
              <div className="flex items-start gap-4 mb-6">
                <div className="bg-surface-container-low p-3 rounded flex-shrink-0">
                  <span className="material-symbols-outlined text-3xl text-[#004A99]">{estadoConfig.icon}</span>
                </div>
                <div>
                  <h2 className="font-display text-xl font-bold text-[#191c1d] mb-0.5">{estadoConfig.label}</h2>
                  <p className="text-xs text-[#737783]">Vitis vinifera · Variedad de vid</p>
                </div>
              </div>

              {diagnostico.deficiencias.length > 0 && (
                <div className="mb-4">
                  <h4 className="data-label mb-3">Deficiencias detectadas</h4>
                  <div className="space-y-3">
                    {diagnostico.deficiencias.map((d, i) => (
                      <div key={i} className="flex items-start gap-3 p-3 bg-surface-container-low rounded border border-[#c2c6d3]">
                        <div className="w-8 h-8 bg-amber-100 rounded flex items-center justify-center flex-shrink-0">
                          <span className="font-display font-bold text-xs text-amber-800">{d.nutriente}</span>
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="font-display text-sm font-semibold text-[#191c1d]">Deficiencia de {d.nutriente}</p>
                          <p className="text-xs text-[#737783] mt-0.5 leading-relaxed">{d.evidencia_visual}</p>
                        </div>
                        <span className={`flex-shrink-0 ${d.confianza === 'alta' ? 'chip-critico' : d.confianza === 'media' ? 'chip-atencion' : 'chip-neutral'}`}>
                          {d.confianza}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {diagnostico.patologias.length > 0 && (
                <div className="mb-4">
                  <h4 className="data-label mb-3">Patologías detectadas</h4>
                  <div className="space-y-3">
                    {diagnostico.patologias.map((p, i) => (
                      <div key={i} className="flex items-start gap-3 p-3 bg-[#ffdad6] rounded border border-[#ffb3ac]">
                        <span className="material-symbols-outlined text-[#93000a] mt-0.5 flex-shrink-0">warning</span>
                        <div>
                          <p className="font-display text-sm font-semibold text-[#93000a]">{p.nombre}</p>
                          <p className="text-xs text-[#410003] mt-0.5">{p.evidencia_visual}</p>
                          <p className="text-xs font-bold text-[#b6171e] mt-1">Urgencia: {p.urgencia}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {diagnostico.deficiencias.length === 0 && diagnostico.patologias.length === 0 && (
                <div className="flex items-center gap-3 p-4 bg-[#a3f69c] rounded mb-4">
                  <span className="material-symbols-outlined text-[#003f0b]" style={{ fontVariationSettings: "'FILL' 1" }}>check_circle</span>
                  <p className="text-sm font-display font-semibold text-[#002204]">No se detectaron deficiencias ni patologías</p>
                </div>
              )}
            </div>
          </div>

          {!diagnostico.patologias.some(p => p.urgencia === 'alta') ? (
            <button onClick={handleGenerarPlan} disabled={generandoPlan} className="btn-primary w-full py-4">
              {generandoPlan
                ? <><div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />Generando plan...</>
                : <><span className="material-symbols-outlined">assignment</span>Generar plan de abono</>
              }
            </button>
          ) : (
            <div className="card p-4 border-l-4 border-[#b6171e]">
              <div className="flex items-start gap-3">
                <span className="material-symbols-outlined text-[#b6171e] flex-shrink-0">block</span>
                <div>
                  <p className="font-display text-sm font-bold text-[#93000a]">Plan de abono no disponible</p>
                  <p className="text-xs text-[#424751] mt-1">Trate primero la patología antes de fertilizar.</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// ============================================================
// Historial
// ============================================================
export function HistorialPage() {
  const [diagnosticos, setDiagnosticos] = useState<Diagnostico[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [busqueda, setBusqueda] = useState('')

  useEffect(() => {
    diagnosticosApi.listar(50).then(r => setDiagnosticos(r.data)).finally(() => setIsLoading(false))
  }, [])

  const filtrados = diagnosticos.filter(d =>
    busqueda === '' ||
    d.id.toLowerCase().includes(busqueda.toLowerCase()) ||
    d.estado_general.toLowerCase().includes(busqueda.toLowerCase())
  )

  const estChip = (e: string) => {
    if (e === 'SALUDABLE') return <span className="chip-saludable">Saludable</span>
    if (e === 'CRITICO') return <span className="chip-critico">Crítico</span>
    return <span className="chip-atencion">Requiere atención</span>
  }

  return (
    <div className="space-y-6">
      <header>
        <h1 className="font-display text-3xl font-bold text-[#00346f] mb-1">Historial de Diagnósticos</h1>
        <p className="text-[#424751] text-sm">Consulta y filtra los resultados de análisis previos realizados en campo.</p>
      </header>

      <section className="grid grid-cols-1 md:grid-cols-12 gap-4 items-end">
        <div className="md:col-span-6">
          <label className="input-label">Buscar por ID o estado</label>
          <div className="relative">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-[#737783] text-xl">search</span>
            <input type="text" value={busqueda} onChange={e => setBusqueda(e.target.value)}
              placeholder="ID de muestra, estado..." className="input-field pl-10" />
          </div>
        </div>
        <div className="md:col-span-3">
          <label className="input-label">Rango de fecha</label>
          <div className="relative">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-[#737783] text-xl">calendar_today</span>
            <input type="date" className="input-field pl-10" />
          </div>
        </div>
        <div className="md:col-span-3">
          <Link to="/diagnosticos/nuevo" className="btn-primary w-full py-3">
            <span className="material-symbols-outlined">add_a_photo</span>
            Nuevo diagnóstico
          </Link>
        </div>
      </section>

      {isLoading ? (
        <div className="flex items-center justify-center h-48">
          <div className="w-10 h-10 border-2 border-[#004A99] border-t-transparent rounded-full animate-spin" />
        </div>
      ) : filtrados.length === 0 ? (
        <div className="card p-12 text-center">
          <span className="material-symbols-outlined text-5xl text-[#c2c6d3] mb-3 block">search_off</span>
          <p className="font-display font-semibold text-[#424751]">Sin resultados</p>
        </div>
      ) : (
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-surface-container-low border-b border-[#c2c6d3]">
                <tr>
                  <th className="table-header">Muestra</th>
                  <th className="table-header">Fecha / ID</th>
                  <th className="table-header">Estado IA</th>
                  <th className="table-header hidden md:table-cell">Confianza</th>
                  <th className="table-header text-right">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#c2c6d3]">
                {filtrados.map((d, i) => (
                  <tr key={d.id} className={`hover:bg-surface-container transition-colors ${i % 2 === 1 ? 'bg-surface-container-low' : ''}`}>
                    <td className="table-cell">
                      <div className="w-12 h-12 bg-surface-container rounded border border-[#c2c6d3] flex items-center justify-center">
                        <span className="material-symbols-outlined text-[#737783] text-2xl">eco</span>
                      </div>
                    </td>
                    <td className="table-cell">
                      <p className="data-value">{format(new Date(d.created_at), 'd MMM yyyy', { locale: es })}</p>
                      <p className="data-label">{d.id.slice(0, 12).toUpperCase()}</p>
                    </td>
                    <td className="table-cell">{estChip(d.estado_general)}</td>
                    <td className="table-cell hidden md:table-cell">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 bg-[#e1e3e4] rounded-full h-1.5 max-w-16">
                          <div className="bg-[#004A99] h-1.5 rounded-full" style={{ width: `${Math.round(d.confianza_global * 100)}%` }} />
                        </div>
                        <span className="data-value text-xs">{Math.round(d.confianza_global * 100)}%</span>
                      </div>
                    </td>
                    <td className="table-cell text-right">
                      <Link to={`/diagnosticos/${d.id}`} className="text-xs text-[#004A99] font-display font-semibold hover:underline">
                        Ver informe
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="px-6 py-3 border-t border-[#c2c6d3] bg-surface-container-low">
            <p className="text-xs text-[#737783] font-display">
              {filtrados.length} registro{filtrados.length !== 1 ? 's' : ''} encontrado{filtrados.length !== 1 ? 's' : ''}
            </p>
          </div>
        </div>
      )}
    </div>
  )
}