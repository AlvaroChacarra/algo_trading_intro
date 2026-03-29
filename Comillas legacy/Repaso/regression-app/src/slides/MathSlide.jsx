import React, { useState } from 'react';
import { ResponsiveContainer, ComposedChart, Scatter, Line, XAxis, YAxis, CartesianGrid, ReferenceLine } from 'recharts';
import { BookOpen, Calculator, Sigma } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { useRegressionData } from '../hooks/useRegressionData';

const MathTerm = ({ children, label, color, onHover, active }) => (
    <div
        className={`relative group cursor-pointer px-3 py-2 rounded-xl transition-all duration-300 ${active === label ? 'bg-slate-800 scale-110 ring-2 ring-' + color.split('-')[1] : 'hover:bg-slate-800/50'}`}
        onMouseEnter={() => onHover(label)}
        onMouseLeave={() => onHover(null)}
    >
        <span className={`text-3xl md:text-5xl font-mono font-bold ${active === label ? color : 'text-slate-400'} transition-colors`}>
            {children}
        </span>
        <div className={`absolute -bottom-8 left-1/2 -translate-x-1/2 text-[10px] font-bold uppercase whitespace-nowrap transition-opacity ${active === label ? 'opacity-100 ' + color : 'opacity-0'}`}>
            {label}
        </div>
    </div>
);

const MathSlide = () => {
    const { data } = useRegressionData(30);
    const [highlight, setHighlight] = useState(null);

    // Modelo "Perfecto" para el demo final
    const slope = 2.5;
    const intercept = 50;

    const chartData = data.map(point => {
        const pred = intercept + (point.x * slope);
        return {
            ...point,
            userLine: pred,
            resid: point.y - pred
        };
    });

    return (
        <div className="h-full grid grid-cols-12 gap-6 p-1">
            {/* Ecuación Interactiva */}
            <div className="col-span-12 h-1/3 min-h-[150px] flex flex-col justify-center items-center bg-slate-900/50 rounded-2xl border border-slate-800 relative overflow-hidden">
                <div className="absolute top-4 left-4 flex gap-2">
                    <Badge color="purple">Modelo Formal</Badge>
                </div>

                <div className="flex items-baseline gap-2 md:gap-4 select-none">
                    <MathTerm label="Predicción (Precio)" color="text-emerald-500" active={highlight} onHover={setHighlight}>
                        ŷ
                    </MathTerm>
                    <span className="text-4xl text-slate-600">=</span>
                    <MathTerm label="Intercepto (Base)" color="text-purple-500" active={highlight} onHover={setHighlight}>
                        β₀
                    </MathTerm>
                    <span className="text-4xl text-slate-600">+</span>
                    <MathTerm label="Pendiente (Marginal)" color="text-blue-500" active={highlight} onHover={setHighlight}>
                        β₁
                    </MathTerm>
                    <MathTerm label="Variable (Metros)" color="text-slate-200" active={highlight} onHover={setHighlight}>
                        x
                    </MathTerm>
                    <span className="text-4xl text-slate-600">+</span>
                    <MathTerm label="Error (Residuo)" color="text-rose-500" active={highlight} onHover={setHighlight}>
                        ε
                    </MathTerm>
                </div>
            </div>

            {/* Visualización Contextual */}
            <div className="col-span-12 md:col-span-8 h-2/3 min-h-[300px]">
                <Card className="h-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 10, bottom: 20 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.5} />
                            <XAxis type="number" dataKey="x" stroke="#475569" hide />
                            <YAxis domain={[0, 600]} stroke="#475569" hide />

                            {/* HIGHTLIGHT: Error (Residuos) */}
                            {(highlight === 'Error (Residuo)' || highlight === null) && chartData.map((d, i) => (
                                <ReferenceLine key={i} segment={[{ x: d.x, y: d.y }, { x: d.x, y: d.userLine }]} stroke="#f43f5e" strokeOpacity={highlight ? 1 : 0.2} strokeWidth={highlight ? 2 : 1} />
                            ))}

                            {/* HIGHTLIGHT: Intercepto (Linea horizontal base o punto en eje Y) */}
                            {(highlight === 'Intercepto (Base)' || highlight === null) && (
                                <ReferenceLine y={intercept} stroke="#a855f7" strokeDasharray="5 5" label={highlight ? { value: 'β₀ (Precio Base)', fill: '#a855f7', position: 'insideRight' } : ''} />
                            )}

                            {/* HIGHTLIGHT: Pendiente (Triángulo visual) */}
                            {(highlight === 'Pendiente (Marginal)' || highlight === null) && (
                                <ReferenceLine segment={[{ x: 100, y: intercept + 100 * slope }, { x: 150, y: intercept + 100 * slope }]} stroke="#3b82f6" strokeWidth={2} />
                            )}
                            {(highlight === 'Pendiente (Marginal)' || highlight === null) && (
                                <ReferenceLine segment={[{ x: 150, y: intercept + 100 * slope }, { x: 150, y: intercept + 150 * slope }]} stroke="#3b82f6" strokeWidth={2} label={{ value: 'β₁', position: 'right', fill: '#3b82f6' }} />
                            )}

                            <Scatter dataKey="y" fill="#3b82f6" opacity={highlight === 'Error (Residuo)' || highlight === 'Variable (Metros)' ? 1 : 0.3} />
                            <Line type="monotone" dataKey="userLine" stroke="#10b981" strokeWidth={highlight === 'Predicción (Precio)' ? 6 : 3} dot={false} animationDuration={500} />
                        </ComposedChart>
                    </ResponsiveContainer>
                </Card>
            </div>

            <div className="col-span-12 md:col-span-4 h-2/3 flex flex-col gap-4">
                <Card title="Glosario" icon={BookOpen} className="bg-slate-900/50">
                    <div className="space-y-4 text-sm text-slate-400">
                        <p><span className="text-emerald-500 font-bold">ŷ (Predicción)</span>: Lo que el modelo cree que vale el piso.</p>
                        <p><span className="text-purple-500 font-bold">β₀ (Intercepto)</span>: El precio desde donde empezamos a contar (suelo fijo).</p>
                        <p><span className="text-blue-500 font-bold">β₁ (Pendiente)</span>: Cuánto sube el precio por cada metro cuadrado adicional.</p>
                        <p><span className="text-rose-500 font-bold">ε (Error)</span>: La realidad caprichosa que el modelo no puede explicar.</p>
                    </div>
                </Card>
            </div>
        </div>
    );
};

export default MathSlide;
