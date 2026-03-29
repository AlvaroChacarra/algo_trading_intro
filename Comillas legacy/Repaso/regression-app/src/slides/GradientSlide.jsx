import React, { useMemo } from 'react';
import { ResponsiveContainer, ComposedChart, Scatter, Line, XAxis, YAxis, CartesianGrid, Tooltip, AreaChart, Area } from 'recharts';
import { Play, Pause, RefreshCw, Zap, TrendingDown } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { useRegressionData } from '../hooks/useRegressionData';
import { useGradientDescent } from '../hooks/useGradientDescent';

const GradientSlide = () => {
    const { data } = useRegressionData(30);
    // Inicializamos mal para que se vea el viaje
    const { slope, intercept, iteration, costHistory, isRunning, setIsRunning, reset } = useGradientDescent(data, 0, 0, 0.000001);

    const chartData = useMemo(() => {
        return data.map(point => ({
            ...point,
            userLine: intercept + (point.x * slope)
        }));
    }, [data, slope, intercept]);

    const currentCost = costHistory.length > 0 ? costHistory[costHistory.length - 1].cost : 0;

    return (
        <div className="h-full grid grid-cols-12 gap-6 p-1">
            {/* Panel de Control y Métricas */}
            <div className="col-span-12 md:col-span-4 flex flex-col gap-6">
                <Card title="Panel de Control AI" icon={Zap} className="bg-slate-900/50">
                    <div className="flex gap-4 mb-6">
                        <Button
                            onClick={() => setIsRunning(!isRunning)}
                            variant={isRunning ? "secondary" : "primary"}
                            className="flex-1"
                        >
                            {isRunning ? <><Pause size={16} /> PAUSAR</> : <><Play size={16} /> AUTO-OPTIMIZAR</>}
                        </Button>
                        <Button onClick={reset} variant="ghost" className="px-3">
                            <RefreshCw size={16} />
                        </Button>
                    </div>

                    <div className="space-y-4">
                        <div className="p-4 bg-slate-800 rounded border border-slate-700">
                            <div className="text-[10px] font-bold text-slate-500 uppercase flex justify-between">
                                <span>Iteración</span>
                                <span>{iteration}</span>
                            </div>
                            <div className="w-full bg-slate-900 h-1.5 rounded-full mt-2 overflow-hidden">
                                {/* Animación de carga infinita mientras corre */}
                                <div className={`h-full bg-blue-500 ${isRunning ? 'animate-pulse w-full' : 'w-0'}`}></div>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <div className="text-[10px] text-slate-500 font-bold uppercase">Pendiente (m)</div>
                                <div className="font-mono text-blue-400 font-bold">{slope.toFixed(4)}</div>
                            </div>
                            <div>
                                <div className="text-[10px] text-slate-500 font-bold uppercase">Intercepto (b)</div>
                                <div className="font-mono text-purple-400 font-bold">{intercept.toFixed(2)}</div>
                            </div>
                        </div>
                    </div>
                </Card>

                <Card title="Curva de Aprendizaje (Coste)" icon={TrendingDown} className="flex-1 min-h-[200px]">
                    <div className="absolute top-4 right-4 z-10">
                        <Badge color={currentCost < 5000 ? 'green' : 'red'}>Error: {Math.round(currentCost)}</Badge>
                    </div>
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={costHistory}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                            <XAxis dataKey="i" hide />
                            <YAxis domain={['auto', 'auto']} hide />
                            <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff', fontSize: 12 }} />
                            <Area type="monotone" dataKey="cost" stroke="#ef4444" fill="#ef4444" fillOpacity={0.2} isAnimationActive={false} />
                        </AreaChart>
                    </ResponsiveContainer>
                </Card>
            </div>

            {/* Gráfico Principal */}
            <div className="col-span-12 md:col-span-8 h-full min-h-[400px]">
                <Card title="Entrenamiento en Tiempo Real" className="h-full relative">
                    <ResponsiveContainer width="100%" height="100%">
                        <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 10, bottom: 20 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                            <XAxis type="number" dataKey="x" domain={[0, 250]} stroke="#475569" tick={{ fontSize: 10 }} />
                            <YAxis domain={[0, 600]} stroke="#475569" tick={{ fontSize: 10 }} />

                            <Scatter name="Datos" dataKey="y" fill="#3b82f6" fillOpacity={0.3} />
                            <Line type="monotone" dataKey="userLine" stroke="#10b981" strokeWidth={3} dot={false} animationDuration={0} />
                        </ComposedChart>
                    </ResponsiveContainer>
                </Card>
            </div>
        </div>
    );
};

export default GradientSlide;
