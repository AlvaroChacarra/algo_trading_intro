import React from "react";
import { cn } from "../../lib/utils";

export const Badge = ({ children, color = 'blue', className }) => {
    const colors = {
        blue: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
        green: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
        red: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
        amber: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
        purple: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
        slate: 'bg-slate-800 text-slate-400 border-slate-700'
    };

    return (
        <span className={cn("px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border", colors[color], className)}>
            {children}
        </span>
    );
};
