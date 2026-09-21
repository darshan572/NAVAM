import React from 'react';
import { useTranslation } from 'react-i18next';
import { useHabitations } from '@/hooks/useQueries';
import { PriorityScore } from '@/components/ui/PriorityScore';
import { SyntheticDataBadge } from '@/components/ui/SyntheticDataBadge';

export const PriorityList: React.FC = () => {
  const { t } = useTranslation();
  const { data: habitations, isLoading } = useHabitations();

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">{t('nav.priorityList')}</h1>
      
      <div className="bg-white rounded-lg shadow border p-6">
        <h2 className="text-lg font-semibold mb-4">Ranked Habitations for Intervention</h2>
        
        {isLoading ? (
          <div>Loading...</div>
        ) : (
          <ul className="divide-y divide-gray-200">
            {habitations?.sort((a, b) => b.priorityScore.score - a.priorityScore.score).map((hab) => (
              <li key={hab.id} className="py-4 flex items-center justify-between">
                <div>
                  <h3 className="text-md font-medium text-gray-900">{hab.name}</h3>
                  <p className="text-sm text-gray-500">{hab.district}</p>
                  {hab.priorityScore.isSynthetic && <div className="mt-1"><SyntheticDataBadge /></div>}
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-500">Vulnerability Score</p>
                  <PriorityScore 
                    score={hab.priorityScore.score} 
                    ciLower={hab.priorityScore.ciLower} 
                    ciUpper={hab.priorityScore.ciUpper}
                    className="text-lg font-bold text-red-600"
                  />
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};
