import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { useAppStore } from '@/store/useAppStore';

export interface Score {
  id: string;
  score: number;
  ciLower: number;
  ciUpper: number;
  isSynthetic: boolean;
}

export interface Habitation {
  id: string;
  name: string;
  district: string;
  priorityScore: Score;
}

export const useHabitations = () => {
  const season = useAppStore((state) => state.season);
  const selectedDistrict = useAppStore((state) => state.selectedDistrict);

  return useQuery({
    queryKey: ['habitations', season, selectedDistrict],
    queryFn: async () => {
      try {
        const rawData = await api.get<any[]>('/habitations');
        if (Array.isArray(rawData) && rawData.length > 0) {
          return rawData.map((h, i) => {
            const scoreVal = h.priority_score ?? (75 - (i * 3));
            return {
              id: String(h.id || i),
              name: h.village_name || `Habitation ${i + 1}`,
              district: h.district_name || 'Chamoli',
              priorityScore: {
                id: `s-${h.id || i}`,
                score: Math.round(scoreVal),
                ciLower: Math.max(0, Math.round(scoreVal - 6)),
                ciUpper: Math.min(100, Math.round(scoreVal + 7)),
                isSynthetic: h.data_source === 'SYNTHETIC' || true,
              },
            };
          });
        }
      } catch (err) {
        console.warn('Backend query error, falling back to seed preview:', err);
      }

      // Fallback preview
      return [
        {
          id: '1',
          name: 'Gopeshwar Pora',
          district: 'Chamoli',
          priorityScore: { id: 's1', score: 87, ciLower: 78, ciUpper: 92, isSynthetic: true },
        },
        {
          id: '2',
          name: 'Joshimath Lower',
          district: 'Chamoli',
          priorityScore: { id: 's2', score: 92, ciLower: 85, ciUpper: 96, isSynthetic: true },
        },
      ] as Habitation[];
    },
  });
};
