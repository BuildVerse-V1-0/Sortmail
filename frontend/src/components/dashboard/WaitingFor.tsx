// Mock data - will be replaced with API call
const mockWaiting = [
    {
        id: "wait-001",
        recipient: "john@bigclient.com",
        subject: "Proposal Follow-up",
        daysWaiting: 5,
    },
    {
        id: "wait-002",
        recipient: "hr@company.com",
        subject: "Reference Check Request",
        daysWaiting: 3,
    },
];

export function WaitingFor() {
    return (
        <div className="card">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-lg font-semibold">Waiting For Reply</h2>
            </div>

            <div className="p-4 space-y-4">
                {mockWaiting.map((item) => (
                    <div
                        key={item.id}
                        className="flex items-start justify-between gap-4"
                    >
                        <div>
                            <p className="font-medium text-sm">{item.subject}</p>
                            <p className="text-xs text-gray-500">{item.recipient}</p>
                        </div>
                        <span className="text-xs text-orange-600 bg-orange-100 px-2 py-1 rounded-full">
                            {item.daysWaiting}d
                        </span>
                    </div>
                ))}

                {mockWaiting.length === 0 && (
                    <p className="text-sm text-gray-500 text-center">
                        No pending replies
                    </p>
                )}
            </div>
        </div>
    );
}
