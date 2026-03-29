import React from "react";
import { cn } from "../../lib/utils";

export const Button = ({ onClick, children, variant = 'primary', disabled = false, className, ...props }) => {
    const baseStyle = "px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed select-none";

    const variants = {
        primary: "bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-900/20 active:scale-95",
        secondary: "bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 active:scale-95",
        ghost: "hover:bg-slate-800 text-slate-400 hover:text-white",
        danger: "bg-red-600 hover:bg-red-500 text-white shadow-lg shadow-red-900/20 active:scale-95",
        success: "bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-900/20 active:scale-95"
    };

    return (
        <button
            onClick={onClick}
            disabled={disabled}
            className={cn(baseStyle, variants[variant], className)}
            {...props}
        >
            {children}
        </button>
    );
};
