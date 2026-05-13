import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import toast from 'react-hot-toast'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPass, setShowPass] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    try {
      await login(email, password)
      navigate('/dashboard')
    } catch (err: any) {
      const msg = err.response?.data?.message || 'Correo o contraseña incorrectos'
      toast.error(msg)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-surface flex flex-col">
      {/* Header institucional */}
      <header className="bg-white border-b border-[#004A99] flex justify-between items-center px-8 lg:px-12 h-20 flex-shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-[#b6171e] rounded flex items-center justify-center">
            <span className="text-white font-display font-bold text-xs">UV</span>
          </div>
          <span className="text-xl font-bold text-[#004A99] font-display tracking-tight">
            nutrI-plantA
          </span>
        </div>
        <div className="w-10 h-10 bg-[#004A99] rounded flex items-center justify-center">
          <span className="text-white font-display font-bold text-xs">UC</span>
        </div>
      </header>

      {/* Contenido */}
      <div className="flex-1 flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-md">
          {/* Encabezado */}
          <div className="mb-8">
            <span className="inline-block py-1 px-3 mb-4 border border-[#004A99] text-[#004A99] text-xs font-bold uppercase tracking-wider rounded-lg font-display">
              Investigación Agrícola · IA
            </span>
            <h1 className="font-display text-3xl font-bold text-[#00346f] mb-2">
              Acceso a la Plataforma
            </h1>
            <p className="text-[#424751] text-sm leading-relaxed">
              Detección temprana de deficiencias nutricionales en vid mediante visión artificial.
            </p>
          </div>

          {/* Card de formulario */}
          <div className="card p-8">
            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="input-label">Correo electrónico</label>
                <div className="relative">
                  
                  <input
                    type="email"
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                    placeholder="nombre@institucion.edu.co"
                    className="input-field pl-10"
                    required
                    autoComplete="email"
                  />
                </div>
              </div>

              <div>
                <label className="input-label">Contraseña</label>
                <div className="relative">
                  <input
                    type={showPass ? 'text' : 'password'}
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                    placeholder="••••••••••"
                    className="input-field pl-10 pr-12"
                    required
                    autoComplete="current-password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPass(!showPass)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-[#737783] hover:text-[#004A99] transition-colors"
                  >
                    <span className="material-symbols-outlined text-xl">
                      {showPass ? 'visibility_off' : 'visibility'}
                    </span>
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading || !email || !password}
                className="btn-primary w-full py-4 text-sm"
              >
                {isLoading ? (
                  <>
                    <span className="material-symbols-outlined text-lg animate-spin">
                      progress_activity
                    </span>
                    Verificando credenciales...
                  </>
                ) : (
                  <>
                    <span className="material-symbols-outlined text-lg">login</span>
                    Iniciar sesión
                  </>
                )}
              </button>
            </form>

            {/* Divider */}
            <div className="flex items-center gap-3 my-6">
              <div className="flex-1 h-px bg-[#c2c6d3]" />
              <span className="text-xs text-[#737783] font-display">¿Nuevo usuario?</span>
              <div className="flex-1 h-px bg-[#c2c6d3]" />
            </div>

            <Link to="/register" className="btn-secondary w-full py-3 text-sm">
              <span className="material-symbols-outlined text-lg">Solicitar acceso</span>
            </Link>
          </div>

          {/* Pie institucional */}
          <p className="text-center text-xs text-[#737783] mt-6">
            Universidad del Valle · Institución Universitaria Antonio José Camacho<br />
            Proyecto de Investigación PI-0225 — Cali, Colombia
          </p>
        </div>
      </div>
    </div>
  )
}
