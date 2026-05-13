import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider, useAuth } from './context/AuthContext'
import AppLayout from './components/layout/AppLayout'

import LoginPage from './pages/auth/LoginPage'
import RegisterPage from './pages/auth/RegisterPage'
import DashboardPage from './pages/agricultor/DashboardPage'
import CultivosPage from './pages/agricultor/CultivosPage'
import NuevoCultivoPage from './pages/agricultor/NuevoCultivoPage'
import {
  NuevoDiagnosticoPage,
  DetalleDiagnosticoPage,
  HistorialPage,
} from './pages/agricultor/DiagnosticoPages'
import UsuariosAdminPage from './pages/admin/UsuariosPage'

function RequireAuth({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth()
  if (isLoading) return (
    <div className="min-h-screen flex items-center justify-center bg-surface">
      <div className="flex flex-col items-center gap-3">
        <div className="w-10 h-10 border-2 border-[#004A99] border-t-transparent rounded-full animate-spin" />
        <p className="font-display text-sm text-[#737783]">Cargando plataforma...</p>
      </div>
    </div>
  )
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />
}

function RequireRole({ children, roles }: { children: React.ReactNode; roles: string[] }) {
  const { user } = useAuth()
  if (!user?.role || !roles.includes(user.role)) return <Navigate to="/dashboard" replace />
  return <>{children}</>
}

// Páginas placeholder para completar en sprints posteriores
function PlanesPage() {
  return (
    <div className="space-y-6">
      <h1 className="font-display text-3xl font-bold text-[#00346f]">Planes de Abono</h1>
      <p className="text-[#424751]">Gestión de planes disponible próximamente.</p>
    </div>
  )
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="/*" element={
        <RequireAuth>
          <AppLayout>
            <Routes>
              <Route path="/dashboard" element={<DashboardPage />} />

              {/* Agricultor */}
              <Route path="/cultivos" element={<RequireRole roles={['AGRICULTOR', 'ADMIN']}><CultivosPage /></RequireRole>} />
              <Route path="/cultivos/nuevo" element={<RequireRole roles={['AGRICULTOR', 'ADMIN']}><NuevoCultivoPage /></RequireRole>} />
              <Route path="/diagnosticos/nuevo" element={<RequireRole roles={['AGRICULTOR', 'INVESTIGADOR','ADMIN']}><NuevoDiagnosticoPage /></RequireRole>} />
              <Route path="/diagnosticos/:id" element={<RequireRole roles={['AGRICULTOR', 'INVESTIGADOR', 'ADMIN']}><DetalleDiagnosticoPage /></RequireRole>} />
              <Route path="/historial" element={<RequireRole roles={['AGRICULTOR', 'INVESTIGADOR', 'ADMIN']}><HistorialPage /></RequireRole>} />
              <Route path="/planes" element={<RequireRole roles={['AGRICULTOR', 'ADMIN']}><PlanesPage /></RequireRole>} />

              {/* Admin */}
              <Route path="/admin/usuarios" element={<RequireRole roles={['ADMIN']}><UsuariosAdminPage /></RequireRole>} />

              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </AppLayout>
        </RequireAuth>
      } />
    </Routes>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              borderRadius: '4px',
              background: '#191c1d',
              color: '#ffffff',
              fontSize: '13px',
              fontFamily: 'Public Sans, sans-serif',
              border: '1px solid #424751',
            },
            success: {
              iconTheme: { primary: '#7ecf79', secondary: '#191c1d' },
            },
            error: {
              iconTheme: { primary: '#ffdad6', secondary: '#191c1d' },
            },
          }}
        />
      </AuthProvider>
    </BrowserRouter>
  )
}
