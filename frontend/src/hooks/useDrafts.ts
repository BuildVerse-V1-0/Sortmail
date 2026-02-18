import { useQuery } from '@tanstack/react-query';
import { api, endpoints } from '@/lib/api';
import { mockDraft } from '@/data/mockData';
import { DraftDTOv1 } from '@/types/dashboard';

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK_DATA === 'true';

export function useDrafts(threadId?: string) {
    return useQuery({
        queryKey: ['drafts', threadId],
        queryFn: async (): Promise<DraftDTOv1 | null> => {
            if (USE_MOCK) {
                // Simulate network delay
                await new Promise(resolve => setTimeout(resolve, 600));

                if (threadId && mockDraft.thread_id === threadId) {
                    return mockDraft;
                }
                // For the drafts page, just return the mock draft if no threadId spec or matches the mock
                if (!threadId) return mockDraft;

                return null;
            }

            const params = threadId ? { thread_id: threadId } : {};
            const { data } = await api.get(endpoints.drafts, { params });
            return data;
        },
        staleTime: 1000 * 60 * 2,
    });
}
