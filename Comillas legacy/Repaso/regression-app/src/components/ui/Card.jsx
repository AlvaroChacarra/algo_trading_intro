import React from "react";
import { cn } from "../../lib/utils";

export const Card = ({ children, className = "", title, icon: Icon }) => (
    <div className={cn("bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl flex flex-col", className)}>
        {(title || Icon) && (
            <div className="flex items-center gap-2 mb-3 border-b border-slate-800 pb-2">
                {Icon && <Icon size={16} className="text-blue-500" />}
                {title && <span className="text-xs font-bold uppercase text-slate-400 tracking-wider">{title}</span>}
            </div>
        )}
        <div className="flex-1 min-h-0 relative">{children}</div>
    </div>
);
