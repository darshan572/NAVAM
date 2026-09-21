import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AppLayout } from '@/components/layout/AppLayout';
import { CommandCenter } from '@/screens/CommandCenter';
import { GisMap } from '@/screens/GisMap';
import { PriorityList } from '@/screens/PriorityList';

// Placeholders for other screens
const HabitationDetail = () => <div className="p-4"><h1 className="text-2xl font-bold">Habitation Detail</h1></div>;
const Explainability = () => <div className="p-4"><h1 className="text-2xl font-bold">Explainability</h1></div>;
const SafeSiteFinder = () => <div className="p-4"><h1 className="text-2xl font-bold">Safe Site Finder</h1></div>;
const CapacityPlan = () => <div className="p-4"><h1 className="text-2xl font-bold">Capacity Plan</h1></div>;
const PolicyEditor = () => <div className="p-4"><h1 className="text-2xl font-bold">Policy Editor (Admin)</h1></div>;

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppLayout />}>
          <Route index element={<CommandCenter />} />
          <Route path="map" element={<GisMap />} />
          <Route path="habitation" element={<HabitationDetail />} />
          <Route path="explainability" element={<Explainability />} />
          <Route path="priority" element={<PriorityList />} />
          <Route path="safe-site" element={<SafeSiteFinder />} />
          <Route path="capacity" element={<CapacityPlan />} />
          <Route path="policy" element={<PolicyEditor />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;
