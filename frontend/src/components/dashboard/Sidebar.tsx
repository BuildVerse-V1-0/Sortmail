
import React, { useEffect, useRef, useLayoutEffect } from 'react';
import { LayoutDashboard, ListFilter, BarChart3, Clock, Command } from 'lucide-react';
import { View } from '@/types/dashboard';
import gsap from 'gsap';
import { Flip } from 'gsap/all';

gsap.registerPlugin(Flip);

interface SidebarProps {
    currentView: View;
    onChangeView: (view: View) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ currentView, onChangeView }) => {
    const sidebarRef = useRef<HTMLDivElement>(null);
    const indicatorRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        // Entrance animation
        gsap.fromTo(sidebarRef.current,
            { x: -50, opacity: 0 },
            { x: 0, opacity: 1, duration: 0.4, ease: "power3.out" }
        );
    }, []);

    // Flip Animation for the active indicator
    useLayoutEffect(() => {
        const state = Flip.getState(indicatorRef.current);
        Flip.from(state, {
            duration: 0.2,
            ease: "power2.out",
            absolute: true,
            toggleClass: "flipping"
        });
    }, [currentView]);

    const navItems = [
        { id: View.DASHBOARD, icon: LayoutDashboard, label: 'Dashboard' },
        { id: View.PRIORITY, icon: ListFilter, label: 'Priority List' },
        { id: View.STATS, icon: BarChart3, label: 'Quick Stats' },
        { id: View.WAITING, icon: Clock, label: 'Waiting For' },
    ];

    return (
        <aside
            ref={sidebarRef}
            className="w-20 lg:w-64 h-screen bg-[#09090B] border-r border-[#27272a] flex flex-col items-center lg:items-stretch py-6 z-20 relative"
        >
            <div className="mb-10 px-6 flex items-center justify-center lg:justify-start gap-3">
                <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center shadow-[0_0_15px_rgba(79,70,229,0.4)]">
                    <Command size={18} className="text-white" />
                </div>
                <span className="hidden lg:block text-xl font-bold tracking-tight text-white">Sortmail</span>
            </div>

            <nav className="flex-1 w-full px-4 space-y-1 relative">
                {navItems.map((item) => {
                    const isActive = currentView === item.id;
                    return (
                        <button
                            key={item.id}
                            onClick={() => onChangeView(item.id)}
                            className={`
                relative w-full flex items-center gap-3 px-3 py-3 rounded-xl transition-colors duration-300 z-10
                ${isActive ? 'text-white' : 'text-zinc-500 hover:text-zinc-300'}
              `}
                        >
                            {isActive && (
                                <div
                                    ref={indicatorRef}
                                    data-flip-id="active-indicator"
                                    className="absolute inset-0 bg-[#27272a] rounded-xl border border-[#3f3f46] shadow-sm -z-10"
                                />
                            )}
                            <item.icon size={20} className={isActive ? 'text-indigo-400' : 'text-current'} />
                            <span className="hidden lg:block font-medium text-sm tracking-wide">{item.label}</span>

                            {isActive && (
                                <div className="absolute right-3 w-1.5 h-1.5 rounded-full bg-indigo-500 shadow-[0_0_8px_rgba(99,102,241,0.8)] hidden lg:block" />
                            )}
                        </button>
                    );
                })}
            </nav>

            <div className="px-6 mt-auto">
                <div className="hidden lg:flex items-center gap-3 p-3 rounded-xl bg-[#18181B] border border-[#27272a]">
                    <img src="https://picsum.photos/100/100" alt="User" className="w-8 h-8 rounded-full border border-zinc-700" />
                    <div className="overflow-hidden">
                        <p className="text-sm font-medium text-zinc-200 truncate">Alex Chen</p>
                        <p className="text-xs text-zinc-500 truncate">Pro Workspace</p>
                    </div>
                </div>
            </div>
        </aside>
    );
};

export default Sidebar;
