import { useQuery } from '@tanstack/react-query';
import { api, endpoints } from '@/lib/api';
import { mockThreadListItems } from '@/data/mockData';
import { ThreadListItem } from '@/types/dashboard';

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK_DATA === 'true';

export function useThreads(filter?: string) {
    return useQuery({
        queryKey: ['threads', filter],
        queryFn: async (): Promise<ThreadListItem[]> => {
            if (USE_MOCK) {
                // Simulate network delay
                await new Promise(resolve => setTimeout(resolve, 600));

                let items = mockThreadListItems;

                // Simple client-side filtering for mock mode
                if (filter === 'urgent') {
                    items = items.filter(t => t.urgency_score >= 70);
                } else if (filter === 'action_required') {
                    items = items.filter(t => t.intent === 'action_required');
                } else if (filter === 'fyi') {
                    items = items.filter(t => t.intent === 'fyi');
                }

                return items;
            }

            const { data } = await api.get(endpoints.threads, { params: { filter } });
            return data;
        },
        staleTime: 1000 * 60, // 1 minute
    });
}
