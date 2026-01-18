export function QuickStats() {
    return (
        <div className="grid grid-cols-4 gap-4">
            <StatCard
                label="Do Now"
                value={3}
                color="text-red-600"
                bgColor="bg-red-50"
            />
            <StatCard
                label="Do Today"
                value={5}
                color="text-orange-600"
                bgColor="bg-orange-50"
            />
            <StatCard
                label="Can Wait"
                value={12}
                color="text-green-600"
                bgColor="bg-green-50"
            />
            <StatCard
                label="Waiting For"
                value={2}
                color="text-blue-600"
                bgColor="bg-blue-50"
            />
        </div>
    );
}

function StatCard({
    label,
    value,
    color,
    bgColor,
}: {
    label: string;
    value: number;
    color: string;
    bgColor: string;
}) {
    return (
        <div className={`card p-4 ${bgColor}`}>
            <p className="text-sm text-gray-600">{label}</p>
            <p className={`text-3xl font-bold ${color}`}>{value}</p>
        </div>
    );
}
