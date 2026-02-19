import { useQuery } from '@tanstack/react-query';
import { dashboardApi } from '@/services/api';
import { mockDashboard } from '@/data/mockData';
import { DashboardData } from '@/types/dashboard';

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK_DATA === 'true';

export function useDashboard() {
    return useQuery({
        queryKey: ['dashboard'],
        queryFn: async (): Promise<DashboardData> => {
            if (USE_MOCK) {
                // Simulate network delay
                await new Promise(resolve => setTimeout(resolve, 800));
                return mockDashboard;
            }

            return await dashboardApi.getStats();
        },
        staleTime: 1000 * 60 * 5, // 5 minutes
    });
}
