
import React from 'react';
import { Attachment } from '@/types/dashboard';
import { FileText, Image, Table, File, Download } from 'lucide-react';
import gsap from 'gsap';

interface AttachmentVaultProps {
    attachments: Attachment[];
}

const AttachmentVault: React.FC<AttachmentVaultProps> = ({ attachments }) => {
    const getIcon = (type: string) => {
        switch (type) {
            case 'img': return <Image size={24} className="text-purple-400" />;
            case 'sheet': return <Table size={24} className="text-emerald-400" />;
            case 'pdf': return <FileText size={24} className="text-rose-400" />;
            default: return <File size={24} className="text-blue-400" />;
        }
    };

    const handleMouseEnter = (e: React.MouseEvent<HTMLDivElement>) => {
        const target = e.currentTarget.querySelector('.scan-bar');
        if (target) {
            gsap.fromTo(target,
                { left: '-100%', opacity: 1 },
                { left: '100%', opacity: 0, duration: 0.8, ease: "power1.inOut" }
            );
        }
    };

    return (
        <div className="h-full p-8 overflow-y-auto">
            <div className="flex items-end justify-between mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-white tracking-tight mb-2">Attachment Vault</h1>
                    <p className="text-slate-400">AI-Indexed files from your inbox.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {attachments.map((file) => (
                    <div
                        key={file.id}
                        onMouseEnter={handleMouseEnter}
                        className="group bg-slate-800/40 border border-slate-700 rounded-2xl p-4 hover:bg-slate-800 hover:border-indigo-500/50 transition-all duration-300 relative overflow-hidden"
                    >
                        <div className="flex items-start justify-between mb-4 relative z-10">
                            <div className="p-3 bg-slate-900 rounded-xl relative overflow-hidden">
                                {getIcon(file.type)}
                                {/* Mini scan effect specific to icon container */}
                                <div className="scan-bar absolute top-0 bottom-0 w-full bg-gradient-to-r from-transparent via-white/40 to-transparent -translate-x-full pointer-events-none" style={{ left: '-100%' }} />
                            </div>
                            {file.aiSummary && (
                                <span className="px-2 py-1 bg-indigo-500/10 text-indigo-400 text-[10px] font-bold uppercase rounded border border-indigo-500/20">
                                    AI Analyzed
                                </span>
                            )}
                        </div>

                        <h3 className="font-semibold text-slate-200 truncate mb-1 relative z-10">{file.name}</h3>
                        <p className="text-xs text-slate-500 mb-4 relative z-10">{file.size} • Uploaded 2h ago</p>

                        {file.aiSummary && (
                            <div className="p-3 bg-slate-900/50 rounded-lg mb-4 border border-slate-800 relative z-10">
                                <p className="text-xs text-slate-400 leading-relaxed line-clamp-2">
                                    <span className="text-indigo-400 mr-1">✦</span>
                                    {file.aiSummary}
                                </p>
                            </div>
                        )}

                        <button className="w-full py-2 flex items-center justify-center gap-2 bg-slate-700/50 hover:bg-indigo-600 text-slate-300 hover:text-white rounded-lg text-sm font-medium transition-colors relative z-10">
                            <Download size={14} /> Download
                        </button>
                    </div>
                ))}
                {/* Mock empty state filler */}
                <div className="border-2 border-dashed border-slate-800 rounded-2xl p-4 flex flex-col items-center justify-center text-slate-600 min-h-[200px]">
                    <p>Drag files here to upload to vault</p>
                </div>
            </div>
        </div>
    );
};

export default AttachmentVault;
