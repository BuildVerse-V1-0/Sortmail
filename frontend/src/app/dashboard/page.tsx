import { PriorityList } from "@/components/dashboard/PriorityList";
import { WaitingFor } from "@/components/dashboard/WaitingFor";
import { QuickStats } from "@/components/dashboard/QuickStats";

export default function DashboardPage() {
    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold">Dashboard</h1>

            {/* Quick Stats */}
            <QuickStats />

            {/* Main Grid */}
            <div className="grid lg:grid-cols-3 gap-6">
                {/* Priority Tasks - 2 columns */}
                <div className="lg:col-span-2">
                    <PriorityList />
                </div>

                {/* Waiting For - 1 column */}
                <div>
                    <WaitingFor />
                </div>
            </div>
        </div>
    );
}
