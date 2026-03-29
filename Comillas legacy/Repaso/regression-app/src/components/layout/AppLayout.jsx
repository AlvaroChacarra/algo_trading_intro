import React from 'react';
import { Presentation, ChevronRight, ChevronLeft } from 'lucide-react';
import { Button } from '../ui/Button';

export const AppLayout = ({ children, title, currentStep, totalSteps, onNext, onPrev }) => {
    return (
        <div className="w-full h-screen bg-slate-950 flex flex-col overflow-hidden font-sans text-slate-200">
            {/* Header */}
            <div className="h-14 border-b border-slate-800 flex items-center justify-between px-6 bg-slate-900/80 backdrop-blur z-20">
                <div className="flex items-center gap-3">
                    <div className="p-1.5 bg-blue-500/10 rounded-lg border border-blue-500/20">
                        <Presentation className="text-blue-500" size={18} />
                    </div>
                    <div className="flex flex-col">
                        <span className="font-bold text-sm tracking-tight text-white leading-none">Regression<span className="text-blue-500">Lab</span></span>
                        <span className="text-[10px] text-slate-500 font-mono">INTUITION SERIES v1.0</span>
                    </div>
                </div>
                <div className="text-xs uppercase font-bold text-slate-500 tracking-widest bg-slate-900 px-3 py-1 rounded border border-slate-800">
                    {title}
                </div>
            </div>

            {/* Main Content */}
            <main className="flex-1 p-4 md:p-6 lg:p-8 max-w-7xl mx-auto w-full h-full relative">
                {children}
            </main>

            {/* Footer / Navigation */}
            <div className="h-16 border-t border-slate-800 bg-slate-900/50 flex items-center justify-between px-6 z-20">
                {/* Progress Bar */}
                <div className="flex gap-1.5">
                    {Array.from({ length: totalSteps }).map((_, i) => (
                        <div key={i} className={`h-1.5 rounded-full transition-all duration-500 ${i === currentStep ? 'bg-blue-500 w-12' : i < currentStep ? 'bg-blue-900 w-6' : 'bg-slate-800 w-6'}`} />
                    ))}
                </div>

                <div className="flex gap-3">
                    <Button variant="secondary" onClick={onPrev} disabled={currentStep === 0} className="px-4 text-xs">
                        <ChevronLeft size={14} /> ANTERIOR
                    </Button>
                    <Button variant="primary" onClick={onNext} disabled={currentStep === totalSteps - 1} className="px-6 text-xs shadow-blue-500/20">
                        SIGUIENTE <ChevronRight size={14} />
                    </Button>
                </div>
            </div>
        </div>
    );
};
