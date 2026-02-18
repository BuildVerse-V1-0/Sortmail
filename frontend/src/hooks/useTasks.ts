import { useQuery } from '@tanstack/react-query';
import { api, endpoints } from '@/lib/api';
import { mockTasks } from '@/data/mockData';
import { TaskDTOv1 } from '@/types/dashboard';

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK_DATA === 'true';

export function useTasks() {
    return useQuery({
        queryKey: ['tasks'],
        queryFn: async (): Promise<TaskDTOv1[]> => {
            if (USE_MOCK) {
                // Simulate network delay
                await new Promise(resolve => setTimeout(resolve, 600));
                return mockTasks;
            }

            const { data } = await api.get(endpoints.tasks);
            return data;
        },
        staleTime: 1000 * 60 * 2, // 2 minutes
    });
}
