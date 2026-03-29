import React, { useState, useMemo } from 'react';
import { ResponsiveContainer, ComposedChart, Scatter, Line, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine } from 'recharts';
import { Target, Trophy, AlertCircle } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { useRegressionData } from '../hooks/useRegressionData';

const IntuitionSlide = () => {
    const { data } = useRegressionData(30);

    // Estado del usuario (Intuición)
    const [slope, setSlope] = useState(1.0); // Pendiente inicial mala
    const [intercept, setIntercept] = useState(100); // Intercepto inicial malo

    // Calculamos la línea del usuario y el error
    const { chartData, mse, score } = useMemo(() => {
        let totalErrorSq = 0;

        // Generamos datos combinados para el gráfico
        const processed = data.map(point => {
            const userPred = intercept + (point.x * slope);
            const error = point.y - userPred;
            totalErrorSq += error * error;

            return {
                ...point,
                userLine: userPred
            };
        });

        const mseVal = totalErrorSq / data.length;
        // Score simple: MSE ideal oscila en ~2000 (ruido). Si MSE > 10000 es 0 puntos.
        // Ajuste "a ojo" de gamificación
        const maxError = 10000;
        const minError = 2500; // El error irreducible (ruido)
        let calcScore = Math.max(0, 100 - ((mseVal - minError) / (maxError - minError)) * 100);
        if (calcScore > 95) calcScore = 100; // Premia la aproximación

        return { chartData: processed, mse: mseVal, score: Math.floor(calcScore) };
    }, [data, slope, intercept]);

    const getScoreColor = (s) => {
        if (s >= 90) return "text-emerald-500";
        if (s >= 50) return "text-amber-500";
        return "text-rose-500";
    }

    return (
        <div className="h-full grid grid-cols-12 gap-6 p-1">
            {/* Panel de Control */}
            <div className="col-span-12 md:col-span-4 flex flex-col gap-6">
                <Card title="Tu Predicción" icon={Target} className="bg-slate-900/50">
                    <div className="space-y-8 py-4">
                        {/* Slider Pendiente */}
                        <div className="space-y-4">
                            <div className="flex justify-between text-xs font-bold text-slate-400 uppercase">
                                <span>Precio / Metro (Pendiente)</span>
                                <span className="text-blue-400">{slope.toFixed(2)}k €</span>
                            </div>
                            <input
                                type="range" min="0" max="5" step="0.1"
                                value={slope}
                                onChange={(e) => setSlope(parseFloat(e.target.value))}
                                className="w-full accent-blue-500 h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer hover:bg-slate-700 transition"
                            />
                            <p className="text-[10px] text-slate-500">
                                ¿Cuánto aumenta el precio por cada metro cuadrado extra?
                            </p>
                        </div>

                        {/* Slider Intercepto */}
                        <div className="space-y-4">
                            <div className="flex justify-between text-xs font-bold text-slate-400 uppercase">
                                <span>Precio Base (Intercepto)</span>
                                <span className="text-purple-400">{intercept}k €</span>
                            </div>
                            <input
                                type="range" min="-50" max="250" step="5"
                                value={intercept}
                                onChange={(e) => setIntercept(parseFloat(e.target.value))}
                                className="w-full accent-purple-500 h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer hover:bg-slate-700 transition"
                            />
                            <p className="text-[10px] text-slate-500">
                                ¿Cuánto costaría el terreno si el piso tuviera 0 m2?
                            </p>
                        </div>
                    </div>
                </Card>

                {/* Score Card */}
                <Card className="flex-1 flex flex-col items-center justify-center gap-4 relative overflow-hidden border-2 border-slate-800 hover:border-slate-700 transition-all">
                    <div className={`absolute inset-0 opacity-10 ${score > 80 ? 'bg-emerald-500' : 'bg-blue-500'}`}></div>
                    <Trophy size={48} className={getScoreColor(score)} />
                    <div className="text-center">
                        <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-1">Precisión del Modelo</h3>
                        <div className={`text-6xl font-mono font-black ${getScoreColor(score)}`}>
                            {score}<span className="text-2xl opacity-50">%</span>
                        </div>
                        <p className="text-xs text-slate-500 mt-2">
                            {score < 50 ? "Sigue ajustando..." : score < 90 ? "¡Casi lo tienes!" : "¡MODELO ÓPTIMO!"}
                        </p>
                    </div>
                </Card>
            </div>

            {/* Gráfico Principal */}
            <div className="col-span-12 md:col-span-8 h-full min-h-[400px]">
                <Card title="Mercado Inmobiliario" className="h-full relative">
                    <div className="absolute top-4 right-4 z-10 flex gap-2">
                        <Badge color="slate">Datos: {data.length} pisos</Badge>
                        <Badge color={score > 80 ? 'green' : 'amber'}>MSE: {Math.round(mse)}</Badge>
                    </div>

                    <ResponsiveContainer width="100%" height="100%">
                        <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 10, bottom: 20 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                            <XAxis
                                type="number"
                                dataKey="x"
                                domain={[0, 250]}
                                label={{ value: 'Tamaño (m²)', position: 'bottom', fill: '#64748b', fontSize: 12 }}
                                stroke="#475569"
                                tick={{ fontSize: 10 }}
                            />
                            <YAxis
                                domain={[0, 600]}
                                label={{ value: 'Precio (k€)', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 12 }}
                                stroke="#475569"
                                tick={{ fontSize: 10 }}
                            />
                            <Tooltip
                                cursor={{ strokeDasharray: '3 3' }}
                                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f1f5f9' }}
                                itemStyle={{ fontSize: 12 }}
                                labelStyle={{ display: 'none' }}
                                formatter={(value, name) => [Math.round(value) + 'k €', name === 'y' ? 'Precio Real' : 'Tu Modelo']}
                            />

                            {/* Puntos (Datos Reales) */}
                            <Scatter name="Mercado" dataKey="y" fill="#3b82f6" fillOpacity={0.6} />

                            {/* Línea del Usuario */}
                            <Line
                                type="monotone"
                                dataKey="userLine"
                                stroke={score > 80 ? '#10b981' : '#f59e0b'}
                                strokeWidth={3}
                                dot={false}
                                activeDot={false}
                                animationDuration={300}
                            />
                        </ComposedChart>
                    </ResponsiveContainer>
                </Card>
            </div>
        </div>
    );
};

export default IntuitionSlide;
