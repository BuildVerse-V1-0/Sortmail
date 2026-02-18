import { useQuery } from '@tanstack/react-query';
import { api, endpoints } from '@/lib/api';
import { mockWaitingFor } from '@/data/mockData';
import { WaitingForDTOv1 } from '@/types/dashboard';

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK_DATA === 'true';

export function useWaitingFor() {
    return useQuery({
        queryKey: ['waiting-for'],
        queryFn: async (): Promise<WaitingForDTOv1[]> => {
            if (USE_MOCK) {
                // Simulate network delay
                await new Promise(resolve => setTimeout(resolve, 600));
                return mockWaitingFor;
            }

            const { data } = await api.get(endpoints.waitingFor);
            return data;
        },
        staleTime: 1000 * 60 * 5,
    });
}
