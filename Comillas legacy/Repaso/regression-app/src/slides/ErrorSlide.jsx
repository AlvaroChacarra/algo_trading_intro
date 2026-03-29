import React, { useState, useMemo } from 'react';
import { ResponsiveContainer, ComposedChart, Scatter, Line, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, Area } from 'recharts';
import { AlertCircle, Ruler, Square } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { useRegressionData } from '../hooks/useRegressionData';

const ErrorSlide = () => {
    const { data } = useRegressionData(30);
    const [slope, setSlope] = useState(0.5);
    const [intercept, setIntercept] = useState(150);
    const [showSquares, setShowSquares] = useState(true);

    const { chartData, totalErrorSq, residualLines } = useMemo(() => {
        let sumSq = 0;
        const residuals = [];

        const processed = data.map(point => {
            const userPred = intercept + (point.x * slope);
            const error = point.y - userPred;
            sumSq += error * error;

            // Datos para dibujar las líneas de residuo
            residuals.push({
                x: point.x,
                y1: point.y,
                y2: userPred,
                error: Math.abs(error)
            });

            return {
                ...point,
                userLine: userPred
            };
        });

        return { chartData: processed, totalErrorSq: Math.round(sumSq), residualLines: residuals };
    }, [data, slope, intercept]);

    const optimalMse = 2500 * 30; // Aprox ruido base * N

    return (
        <div className="h-full grid grid-cols-12 gap-6 p-1">
            {/* Panel Explicativo */}
            <div className="col-span-12 md:col-span-4 flex flex-col gap-6">
                <Card title="Concepto: Mínimos Cuadrados" icon={Square} className="bg-slate-900/50">
                    <div className="space-y-4 text-sm text-slate-400">
                        <p>
                            Para encontrar la "mejor" línea, no adivinamos. <span className="text-white font-bold">Medimos el dolor.</span>
                        </p>
                        <p>
                            Cada punto rojo representa la distancia entre tu predicción y la realidad. Esa distancia se llama <span className="text-rose-400 font-bold">Residuo</span>.
                        </p>
                        <p>
                            El objetivo matemático es minimizar el área total de los cuadrados de estos residuos.
                        </p>
                        <div className="p-4 bg-slate-800 rounded border border-slate-700 mt-4">
                            <div className="text-xs uppercase font-bold text-slate-500 mb-2">Suma de Errores al Cuadrado (SSE)</div>
                            <div className="text-4xl font-mono text-rose-500 font-bold animate-pulse">
                                {totalErrorSq.toLocaleString()}
                            </div>
                            <div className="w-full bg-slate-700 h-1.5 rounded-full mt-2 overflow-hidden">
                                <div className="bg-rose-500 h-full transition-all duration-300" style={{ width: `${Math.min(100, (totalErrorSq / (optimalMse * 10)) * 100)}%` }}></div>
                            </div>
                        </div>
                    </div>
                </Card>

                <Card title="Controles" className="flex-1">
                    <div className="space-y-6">
                        <div className="space-y-2">
                            <label className="text-xs font-bold text-slate-400">Pendiente</label>
                            <input type="range" min="0" max="5" step="0.1" value={slope} onChange={(e) => setSlope(Number(e.target.value))} className="w-full accent-blue-500 h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer" />
                        </div>
                        <div className="space-y-2">
                            <label className="text-xs font-bold text-slate-400">Intercepto</label>
                            <input type="range" min="-50" max="250" step="5" value={intercept} onChange={(e) => setIntercept(Number(e.target.value))} className="w-full accent-purple-500 h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer" />
                        </div>
                        <button
                            onClick={() => setShowSquares(!showSquares)}
                            className={`w-full py-2 rounded text-xs font-bold border transition-all ${showSquares ? 'bg-rose-500/20 border-rose-500 text-rose-400' : 'bg-slate-800 border-slate-700 text-slate-400'}`}
                        >
                            {showSquares ? 'OCULTAR RESIDUOS' : 'VISIÓN RAYOS X (MOSTRAR ERROR)'}
                        </button>
                    </div>
                </Card>
            </div>

            {/* Gráfico */}
            <div className="col-span-12 md:col-span-8 h-full min-h-[400px]">
                <Card title="Visualización de Residuos" className="h-full relative">
                    <ResponsiveContainer width="100%" height="100%">
                        <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 10, bottom: 20 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                            <XAxis type="number" dataKey="x" domain={[0, 250]} stroke="#475569" tick={{ fontSize: 10 }} />
                            <YAxis domain={[0, 600]} stroke="#475569" tick={{ fontSize: 10 }} />
                            <Tooltip contentStyle={{ display: 'none' }} />

                            {/* Líneas de Residuo (Manuales usando ReferenceLine) */}
                            {showSquares && residualLines.map((res, i) => (
                                <React.Fragment key={i}>
                                    {/* Línea vertical */}
                                    <ReferenceLine
                                        segment={[{ x: res.x, y: res.y1 }, { x: res.x, y: res.y2 }]}
                                        stroke="#f43f5e"
                                        strokeWidth={2}
                                        strokeOpacity={0.6}
                                    />
                                    {/* "Sombra/Cuerpo" del error para darle peso visual */}
                                    <ReferenceLine
                                        segment={[{ x: res.x, y: res.y1 }, { x: res.x, y: res.y2 }]}
                                        stroke="#f43f5e"
                                        strokeWidth={res.error / 5}
                                        strokeOpacity={0.1}
                                    />
                                </React.Fragment>
                            ))}

                            <Scatter name="Datos" dataKey="y" fill="#3b82f6" fillOpacity={0.4} />
                            <Line type="monotone" dataKey="userLine" stroke="#f59e0b" strokeWidth={3} dot={false} animationDuration={0} />
                        </ComposedChart>
                    </ResponsiveContainer>
                </Card>
            </div>
        </div>
    );
};

export default ErrorSlide;
