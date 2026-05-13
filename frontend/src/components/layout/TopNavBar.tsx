import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import toast from 'react-hot-toast'

interface NavItem {
  to: string
  label: string
  roles: string[]
}

const NAV_ITEMS: NavItem[] = [
  { to: '/dashboard',      label: 'Inicio',        roles: ['AGRICULTOR', 'INVESTIGADOR', 'ADMIN'] },
  { to: '/cultivos',       label: 'Mis Cultivos',  roles: ['AGRICULTOR'] },
  { to: '/diagnosticos',   label: 'Diagnóstico',   roles: ['AGRICULTOR', 'INVESTIGADOR'] },
  { to: '/historial',      label: 'Historial',     roles: ['AGRICULTOR', 'INVESTIGADOR'] },
  { to: '/planes',         label: 'Plan de Abono', roles: ['AGRICULTOR'] },
  { to: '/admin/usuarios', label: 'Usuarios',      roles: ['ADMIN'] },
]

export default function TopNavBar() {
  const { user, logout } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()

  const handleLogout = async () => {
    try { await logout() } finally {
      navigate('/login')
      toast.success('Sesión cerrada')
    }
  }

  const visible = NAV_ITEMS.filter(
    item => user?.role && item.roles.includes(user.role)
  )

  return (
    <header className="fixed top-0 z-50 w-full bg-white border-b border-[#004A99] flex justify-between items-center px-8 lg:px-12 h-20">
      {/* Logo izquierdo: Univalle */}
      <div className="flex items-center gap-4">
        <div className="w-10 h-10 bg-[#b6171e] rounded flex items-center justify-center flex-shrink-0">
          <span className="text-white font-display font-bold text-xs leading-none text-center">UV</span>
        </div>
        <span className="text-xl font-bold text-[#004A99] font-display tracking-tight">
          nutrI-plantA
        </span>
      </div>

      {/* Navegación central */}
      <nav className="hidden md:flex items-center gap-8 h-full">
        {visible.map(item => {
          const isActive = location.pathname === item.to ||
            (item.to !== '/dashboard' && location.pathname.startsWith(item.to))
          return (
            <Link
              key={item.to}
              to={item.to}
              className={`font-display text-sm font-medium h-full flex items-center border-b-2 transition-colors duration-150 ${
                isActive
                  ? 'text-[#004A99] border-[#004A99]'
                  : 'text-[#424751] border-transparent hover:text-[#004A99]'
              }`}
            >
              {item.label}
            </Link>
          )
        })}
      </nav>

      {/* Usuario + Logo Unicamacho */}
      <div className="flex items-center gap-4 lg:gap-6">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-[#004A99] flex items-center justify-center">
            <span className="text-white text-xs font-bold font-display">
              {user?.full_name?.charAt(0).toUpperCase()}
            </span>
          </div>
          <div className="hidden lg:block">
            <p className="text-xs font-semibold text-[#191c1d] font-display leading-tight">
              {user?.full_name?.split(' ')[0]}
            </p>
            <p className="text-xs text-[#737783]">{user?.role}</p>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="text-[#737783] hover:text-[#b6171e] transition-colors"
          title="Cerrar sesión"
        >
          <span className="material-symbols-outlined text-xl">logout</span>
        </button>
        {/* Logo derecho: Unicamacho */}
        <div className="w-10 h-10 bg-[#004A99] rounded flex items-center justify-center flex-shrink-0">
          <span className="text-white font-display font-bold text-xs leading-none text-center">UC</span>
        </div>
      </div>
    </header>
  )
}
