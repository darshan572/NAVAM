import React from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAppStore } from '@/store/useAppStore';
import { 
  LayoutDashboard, 
  Map as MapIcon, 
  Home, 
  HelpCircle, 
  ListOrdered, 
  Search, 
  BarChart, 
  Settings 
} from 'lucide-react';

export const AppLayout: React.FC = () => {
  const { t, i18n } = useTranslation();
  const location = useLocation();
  const season = useAppStore(state => state.season);
  const setSeason = useAppStore(state => state.setSeason);

  const navItems = [
    { path: '/', label: 'nav.commandCenter', icon: LayoutDashboard },
    { path: '/map', label: 'nav.gisMap', icon: MapIcon },
    { path: '/habitation', label: 'nav.habitationDetail', icon: Home },
    { path: '/explainability', label: 'nav.explainability', icon: HelpCircle },
    { path: '/priority', label: 'nav.priorityList', icon: ListOrdered },
    { path: '/safe-site', label: 'nav.safeSiteFinder', icon: Search },
    { path: '/capacity', label: 'nav.capacityPlan', icon: BarChart },
    { path: '/policy', label: 'nav.policyEditor', icon: Settings },
  ];

  const toggleLanguage = () => {
    i18n.changeLanguage(i18n.language === 'en' ? 'hi' : 'en');
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r flex flex-col">
        <div className="p-4 border-b">
          <h1 className="text-xl font-bold text-blue-900">NAVAM</h1>
        </div>
        <nav className="flex-1 overflow-y-auto p-4 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center space-x-3 px-3 py-2 rounded-md transition-colors ${
                  isActive ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <Icon size={20} />
                <span className="font-medium">{t(item.label)}</span>
              </Link>
            );
          })}
        </nav>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Header */}
        <header className="bg-white border-b h-16 flex items-center justify-between px-6">
          <h2 className="text-xl font-semibold text-gray-800">{t('dashboard.title')}</h2>
          
          <div className="flex items-center space-x-4">
            <select 
              value={season}
              onChange={(e) => setSeason(e.target.value as any)}
              className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
            >
              <option value="monsoon">{t('season.monsoon')}</option>
              <option value="dry">{t('season.dry')}</option>
              <option value="winter">{t('season.winter')}</option>
            </select>

            <button 
              onClick={toggleLanguage}
              className="px-3 py-1 bg-gray-100 rounded-md hover:bg-gray-200 font-medium"
            >
              {i18n.language === 'en' ? 'हिंदी' : 'English'}
            </button>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
