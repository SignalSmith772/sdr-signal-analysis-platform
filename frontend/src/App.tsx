/**
 * App.tsx — Root component: sets up routing and the shared sidebar layout.
 */
import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, Radio, BarChart2, FileText,
  ChevronLeft, ChevronRight, Cpu, Wifi
} from 'lucide-react';
import Dashboard from './pages/Dashboard';
import Capture from './pages/Capture';
import Analysis from './pages/Analysis';
import Reports from './pages/Reports';

const NAV = [
  { to: '/',         label: 'Dashboard',  icon: LayoutDashboard },
  { to: '/capture',  label: 'Capture',    icon: Radio },
  { to: '/analysis', label: 'Analysis',   icon: BarChart2 },
  { to: '/reports',  label: 'Reports',    icon: FileText },
];

function Sidebar({ collapsed, toggle }: { collapsed: boolean; toggle: () => void }) {
  return (
    <aside
      className={`flex flex-col bg-slate-900 border-r border-slate-700/60 transition-all duration-300 ${
        collapsed ? 'w-16' : 'w-60'
      } shrink-0`}
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 py-5 border-b border-slate-700/60">
        <div className="w-8 h-8 rounded-lg bg-cyan-500/20 flex items-center justify-center shrink-0">
          <Wifi size={16} className="text-cyan-400" />
        </div>
        {!collapsed && (
          <div className="min-w-0">
            <p className="text-sm font-bold text-slate-100 truncate">SDR Platform</p>
            <p className="text-[10px] text-slate-500 truncate">Signal Analysis v1.0</p>
          </div>
        )}
      </div>

      {/* Nav links */}
      <nav className="flex-1 px-2 py-4 space-y-1">
        {NAV.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-cyan-500/15 text-cyan-400 border border-cyan-500/25'
                  : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800'
              }`
            }
          >
            <Icon size={18} className="shrink-0" />
            {!collapsed && <span className="truncate">{label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Collapse toggle */}
      <div className="px-2 py-4 border-t border-slate-700/60">
        <button
          onClick={toggle}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg
                     text-slate-500 hover:text-slate-300 hover:bg-slate-800 transition-colors"
        >
          {collapsed ? <ChevronRight size={16} /> : (
            <><ChevronLeft size={16} /><span className="text-xs">Collapse</span></>
          )}
        </button>
      </div>
    </aside>
  );
}

function Header() {
  const location = useLocation();
  const page = NAV.find(n => n.to === location.pathname);
  const Icon = page?.icon ?? LayoutDashboard;
  return (
    <header className="h-14 border-b border-slate-700/60 bg-slate-900/80 backdrop-blur
                       flex items-center gap-3 px-6 shrink-0">
      <Icon size={18} className="text-cyan-400" />
      <span className="font-semibold text-slate-100">{page?.label ?? 'SDR Platform'}</span>
      <div className="ml-auto flex items-center gap-2">
        <Cpu size={14} className="text-slate-500" />
        <span className="text-xs text-slate-500 font-mono">Demo Mode</span>
        <span className="w-2 h-2 rounded-full bg-green-500 live-dot" />
      </div>
    </header>
  );
}

function Layout() {
  const [collapsed, setCollapsed] = useState(false);
  return (
    <div className="flex h-screen bg-slate-950 overflow-hidden">
      <Sidebar collapsed={collapsed} toggle={() => setCollapsed(c => !c)} />
      <div className="flex flex-col flex-1 min-w-0">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <Routes>
            <Route path="/"         element={<Dashboard />} />
            <Route path="/capture"  element={<Capture />} />
            <Route path="/analysis" element={<Analysis />} />
            <Route path="/reports"  element={<Reports />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Layout />
    </BrowserRouter>
  );
}
