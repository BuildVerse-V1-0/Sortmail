'use client';

import Link from 'next/link';
import { Users, Gauge, Coins, ArrowRight, Brain } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

const liveModules = [
    {
        title: 'Live Metrics',
        description: 'Real backend operational metrics with 10s refresh.',
        href: '/admin/metrics',
        icon: Gauge,
    },
    {
        title: 'User Management',
        description: 'Real user directory from admin APIs.',
        href: '/admin/users',
        icon: Users,
    },
    {
        title: 'Credits',
        description: 'Admin credits module is being migrated to full live data.',
        href: '/admin/credits',
        icon: Coins,
    },
    {
        title: 'AI Usage',
        description: 'Live Bedrock calls, token consumption, and error telemetry.',
        href: '/admin/ai/usage',
        icon: Brain,
    },
    {
        title: 'Email Activity',
        description: 'Live email processing activity with latency, status, and queue context.',
        href: '/admin/emails/activity',
        icon: Gauge,
    },
];

const upcomingModules = [
    'System Health',
    'Security',
    'Billing',
    'Alerts',
    'Analytics',
    'Compliance',
    'Templates',
    'Global Rules',
    'Support',
    'Invites',
    'Announcements',
    'Experiments',
    'Audit Export',
];

export default function AdminDashboardPage() {
    return (
        <div className="p-8 max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500">
            <div>
                <h1 className="text-3xl font-display text-ink mb-1">Admin Control Center</h1>
                <p className="text-ink-light text-sm">
                    Stub dashboards were removed. Only live modules are shown here while remaining admin areas are being connected.
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {liveModules.map((item) => {
                    const Icon = item.icon;
                    return (
                        <Link key={item.href} href={item.href}>
                            <Card className="border-border-light shadow-sm hover:shadow-md transition-shadow h-full">
                                <CardContent className="p-5 space-y-4">
                                    <div className="w-10 h-10 rounded-xl bg-accent/10 border border-accent/20 flex items-center justify-center">
                                        <Icon size={18} className="text-accent" />
                                    </div>
                                    <div>
                                        <h2 className="text-lg font-display text-ink">{item.title}</h2>
                                        <p className="text-ink-light text-sm mt-1">{item.description}</p>
                                    </div>
                                    <Button variant="link" className="p-0 h-auto text-xs font-bold uppercase tracking-wider text-accent">
                                        Open <ArrowRight size={12} className="ml-1" />
                                    </Button>
                                </CardContent>
                            </Card>
                        </Link>
                    );
                })}
            </div>

            <Card className="border-border-light shadow-sm">
                <CardContent className="p-6">
                    <h3 className="text-xs font-mono font-bold uppercase tracking-widest text-ink-mid mb-4">Coming Soon Modules</h3>
                    <div className="flex flex-wrap gap-2">
                        {upcomingModules.map((name) => (
                            <span
                                key={name}
                                className="text-[10px] font-mono font-bold uppercase tracking-wider px-2 py-1 rounded border border-border-light bg-paper-mid text-ink-light"
                            >
                                {name}
                            </span>
                        ))}
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
