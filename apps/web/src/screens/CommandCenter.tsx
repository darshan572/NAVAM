import React from 'react';
import { useHabitations } from '@/hooks/useQueries';
import { PriorityScore } from '@/components/ui/PriorityScore';
import { SyntheticDataBadge } from '@/components/ui/SyntheticDataBadge';
import { useTranslation } from 'react-i18next';

export const CommandCenter: React.FC = () => {
  const { data: habitations, isLoading } = useHabitations();
  const { t } = useTranslation();

  if (isLoading) return <div>Loading...</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">{t('nav.commandCenter')}</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-medium text-gray-500">Total Habitations</h3>
          <p className="text-3xl font-bold mt-2">{habitations?.length || 0}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-medium text-gray-500">High Risk</h3>
          <p className="text-3xl font-bold mt-2 text-red-600">
            {habitations?.filter(h => h.priorityScore.score > 80).length || 0}
          </p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-medium text-gray-500">Safe Sites Needed</h3>
          <p className="text-3xl font-bold mt-2 text-yellow-600">12</p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Habitation</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">District</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Priority Score</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Data Type</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {habitations?.map((hab) => (
              <tr key={hab.id}>
                <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900">{hab.name}</td>
                <td className="px-6 py-4 whitespace-nowrap text-gray-500">{hab.district}</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <PriorityScore 
                    score={hab.priorityScore.score} 
                    ciLower={hab.priorityScore.ciLower} 
                    ciUpper={hab.priorityScore.ciUpper} 
                    className={hab.priorityScore.score > 80 ? 'text-red-600' : 'text-green-600'}
                  />
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {hab.priorityScore.isSynthetic && <SyntheticDataBadge />}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
