import { NavLink, useLocation } from 'react-router-dom';
import { LayoutDashboard, FlaskConical, Database, BarChart3 } from 'lucide-react';

const links = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/evaluate', icon: FlaskConical, label: 'Evaluate' },
  { to: '/dataset', icon: Database, label: 'Dataset' },
  { to: '/analytics', icon: BarChart3, label: 'Analytics' },
];

export default function Sidebar() {
  const location = useLocation();

  return (
    <aside
      style={{ width: '220px', minWidth: '220px' }}
      className="fixed left-0 top-0 bottom-0 z-50 bg-[#0a0a0a] border-r border-[#1a1a1a] flex flex-col"
    >
      {/* Logo */}
      <div className="px-5 py-6">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-white flex items-center justify-center">
            <span className="text-black text-sm font-black">E</span>
          </div>
          <div>
            <span className="text-[15px] font-bold text-white tracking-tight">EvalFlow</span>
            <span className="text-[10px] text-surface-600 ml-1.5 font-medium">PRO</span>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 space-y-0.5">
        {links.map(({ to, icon: Icon, label }) => {
          const isActive = location.pathname === to;
          return (
            <NavLink
              key={to}
              to={to}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-[13px] font-medium transition-colors ${
                isActive
                  ? 'bg-[#171717] text-white'
                  : 'text-surface-500 hover:text-surface-300 hover:bg-[#111111]'
              }`}
            >
              <Icon className="w-4 h-4 flex-shrink-0" />
              <span>{label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-4 py-4 border-t border-[#1a1a1a]">
        <p className="text-[10px] text-surface-600 font-medium">OpenRouter · LLaMA 3.1</p>
        <p className="text-[10px] text-surface-700 mt-0.5">v1.0.0</p>
      </div>
    </aside>
  );
}
