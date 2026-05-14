import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import toast from 'react-hot-toast'

export default function RegisterPage() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ full_name: '', email: '', password: '', confirm: '' })
  const [isLoading, setIsLoading] = useState(false)

  const set = (k: string, v: string) => setForm(p => ({ ...p, [k]: v }))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (form.password !== form.confirm) { toast.error('Las contraseñas no coinciden'); return }
    setIsLoading(true)
    try {
      await register(form.email, form.full_name, form.password)
      toast.success('Solicitud enviada. Un administrador aprobará tu acceso.')
      navigate('/login')
    } catch (err: any) {
      toast.error(err.response?.data?.message || 'Error al registrarse')
    } finally { setIsLoading(false) }
  }

  return (
    <div className="min-h-screen bg-surface flex flex-col">
      <header className="bg-white border-b border-[#004A99] flex justify-between items-center px-8 lg:px-12 h-20 flex-shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-[#b6171e] rounded flex items-center justify-center">
            <span className="text-white font-display font-bold text-xs">UV</span>
          </div>
          <span className="text-xl font-bold text-[#004A99] font-display tracking-tight">nutrI-plantA</span>
        </div>
        <div className="w-10 h-10 bg-[#004A99] rounded flex items-center justify-center">
          <span className="text-white font-display font-bold text-xs">UC</span>
        </div>
      </header>

      <div className="flex-1 flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-md">
          <div className="mb-8">
            <span className="inline-block py-1 px-3 mb-4 border border-[#004A99] text-[#004A99] text-xs font-bold uppercase tracking-wider rounded-lg font-display">
              Solicitud de acceso
            </span>
            <h1 className="font-display text-3xl font-bold text-[#00346f] mb-2">Crear cuenta</h1>
            <p className="text-[#424751] text-sm">
              Tu cuenta quedará pendiente de aprobación por el administrador del sistema.
            </p>
          </div>

          <div className="card p-8">
            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="input-label">Nombre completo</label>
                <div className="relative">
                  <input type="text" value={form.full_name} onChange={e => set('full_name', e.target.value)}
                    className="input-field pl-10" required />
                </div>
              </div>

              <div>
                <label className="input-label">Correo electrónico</label>
                <div className="relative">
                  <input type="email" value={form.email} onChange={e => set('email', e.target.value)}
                    className="input-field pl-10" required />
                </div>
              </div>

              <div>
                <label className="input-label">Contraseña</label>
                <div className="relative">
                  <input type="password" value={form.password} onChange={e => set('password', e.target.value)}
                    placeholder="Mínimo 10 caracteres" className="input-field pl-10" required minLength={10} />
                </div>
                <p className="text-xs text-[#737783] mt-1">Debe incluir mayúsculas, minúsculas, números y símbolo especial.</p>
              </div>

              <div>
                <label className="input-label">Confirmar contraseña</label>
                <div className="relative">
                  <input type="password" value={form.confirm} onChange={e => set('confirm', e.target.value)}
                    placeholder="Repite la contraseña" className="input-field pl-10" required />
                </div>
              </div>

              {/* Aviso */}
              <div className="flex items-start gap-3 p-4 bg-blue-50 border border-blue-200 rounded">
                <span className="material-symbols-outlined text-[#004A99] text-xl mt-0.5 flex-shrink-0">info</span>
                <p className="text-xs text-[#004A99] leading-relaxed">
                  Una vez registrado, el administrador revisará tu solicitud y te asignará el rol correspondiente (Agricultor, Investigador u otro).
                </p>
              </div>

              <button type="submit" disabled={isLoading} className="btn-primary w-full py-4">
                {isLoading ? (
                  <><span className="material-symbols-outlined text-lg animate-spin">progress_activity</span>Enviando solicitud...</>
                ) : (
                  <><span className="material-symbols-outlined text-lg">send</span>Enviar solicitud</>
                )}
              </button>
            </form>

            <div className="flex items-center gap-3 my-5">
              <div className="flex-1 h-px bg-[#c2c6d3]" />
              <span className="text-xs text-[#737783] font-display">¿Ya tienes cuenta?</span>
              <div className="flex-1 h-px bg-[#c2c6d3]" />
            </div>
            <Link to="/login" className="btn-ghost w-full py-2.5 flex items-center justify-center gap-2 border border-[#c2c6d3] rounded hover:bg-surface-container-low">
              <span className="material-symbols-outlined text-lg">Volver al inicio de sesión</span>
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
