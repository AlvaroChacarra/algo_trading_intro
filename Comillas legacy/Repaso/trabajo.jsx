import React, { useState, useEffect, useMemo } from 'react';
import { 
  LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, ResponsiveContainer, Legend, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Cell 
} from 'recharts';
import { 
  TrendingUp, Briefcase, Globe, Search, FileText, CheckCircle, 
  ArrowRight, ArrowLeft, Target, Users, Zap, Layout, ChevronRight,
  GraduationCap, Building2, Plane, MousePointerClick, Clock, AlertTriangle, Star
} from 'lucide-react';

// --- SISTEMA DE DISEÑO (DARK FINTECH PRO) ---
const THEME = {
  bg: 'bg-slate-950',
  panel: 'bg-slate-900 border border-slate-800 backdrop-blur-sm',
  panelHover: 'hover:border-slate-700 transition-colors duration-300',
  textMain: 'text-slate-200',
  textSec: 'text-slate-500',
  accent: 'text-blue-500',
  success: 'text-green-500',
  danger: 'text-red-500',
  warning: 'text-amber-500',
  mono: 'font-mono'
};

// --- COMPONENTES UI ATÓMICOS ---

const Badge = ({ children, color = 'blue' }) => {
  const colors = {
    blue: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    green: 'bg-green-500/10 text-green-400 border-green-500/20',
    red: 'bg-red-500/10 text-red-400 border-red-500/20',
    amber: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  };
  return (
    <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border ${colors[color]}`}>
      {children}
    </span>
  );
};

const Card = ({ children, className = '', title = null, icon: Icon = null }) => (
  <div className={`${THEME.panel} rounded-xl p-5 shadow-xl flex flex-col h-full ${className}`}>
    {(title || Icon) && (
      <div className="flex items-center gap-2 mb-4 border-b border-slate-800 pb-3">
        {Icon && <Icon size={16} className="text-blue-500" />}
        {title && <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wide">{title}</h3>}
      </div>
    )}
    <div className="flex-1 min-h-0">{children}</div>
  </div>
);

const Button = ({ onClick, children, variant = 'primary', disabled = false, className='' }) => {
  const baseStyle = "px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed";
  const variants = {
    primary: "bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-900/20",
    secondary: "bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700",
    ghost: "hover:bg-slate-800 text-slate-400 hover:text-white"
  };
  return (
    <button onClick={onClick} disabled={disabled} className={`${baseStyle} ${variants[variant]} ${className}`}>
      {children}
    </button>
  );
};

// --- SLIDES (MODULOS) ---

// 1. DASHBOARD INICIAL
const SlideIntro = ({ onStart }) => (
  <div className="h-full grid grid-cols-12 grid-rows-6 gap-4 animate-fade-in">
    {/* Header Hero */}
    <div className="col-span-12 row-span-3 md:col-span-8 md:row-span-6 relative overflow-hidden rounded-2xl border border-slate-800 bg-gradient-to-br from-slate-900 via-slate-950 to-black p-8 flex flex-col justify-center">
      <div className="absolute top-0 right-0 p-32 bg-blue-600/10 blur-[100px] rounded-full pointer-events-none"></div>
      
      <Badge color="blue">Módulo: Estrategia Profesional</Badge>
      <h1 className="text-3xl md:text-5xl lg:text-6xl font-bold text-white mt-4 mb-6 leading-tight">
        Arquitectura de Carrera <br/>
        <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">Post-Máster</span>
      </h1>
      <p className="text-base md:text-lg text-slate-400 max-w-xl mb-8 leading-relaxed">
        El mercado laboral es eficiente pero saturado. Esta simulación te enseña a hackear el embudo de selección usando señalización (Máster), precisión (Targeting) e impacto (CV).
      </p>
      <div className="flex gap-4">
        <Button onClick={onStart} className="w-fit px-8 py-3 text-lg">
          Iniciar Simulación <ArrowRight size={20} />
        </Button>
      </div>
    </div>

    {/* Stat Cards - Bento Grid */}
    <Card className="col-span-6 row-span-3 md:col-span-4 md:row-span-2" title="Realidad de Mercado">
      <div className="flex flex-col justify-center h-full gap-2">
        <div className="flex justify-between items-end">
          <span className="text-4xl font-mono font-bold text-white">6s</span>
          <Clock className="text-red-500 mb-1" />
        </div>
        <p className="text-xs text-slate-500">Tiempo promedio que un reclutador dedica a tu CV antes de descartar.</p>
      </div>
    </Card>

    <Card className="col-span-6 row-span-3 md:col-span-4 md:row-span-2" title="El Valor del Máster">
      <div className="flex flex-col justify-center h-full gap-2">
        <div className="flex justify-between items-end">
          <span className="text-4xl font-mono font-bold text-green-500">+22%</span>
          <TrendingUp className="text-green-500 mb-1" />
        </div>
        <p className="text-xs text-slate-500">Prima salarial promedio de entrada vs. solo Grado (Señalización).</p>
      </div>
    </Card>

    <Card className="col-span-12 md:col-span-4 md:row-span-2 bg-gradient-to-br from-slate-900 to-blue-900/20" title="Objetivo">
      <div className="flex items-center gap-4 h-full">
        <div className="p-3 bg-blue-500 rounded-lg text-white">
          <Target size={24} />
        </div>
        <div>
          <p className="text-sm text-slate-300 font-bold">Optimizar Empleabilidad</p>
          <p className="text-xs text-slate-500">Transformar "Junior" en "High Potential".</p>
        </div>
      </div>
    </Card>
  </div>
);

// 2. ROI & VALOR (Denso)
const SlideMasterValue = () => {
  const [years, setYears] = useState(5);
  const [signaling, setSignaling] = useState(1.2); 

  const data = useMemo(() => Array.from({ length: 11 }, (_, i) => {
      const baseSalary = 24000 * Math.pow(1.03, i); // Crecimiento orgánico 3%
      const masterSalary = (24000 * 1.15) * Math.pow(1.03 + (0.02 * signaling), i); // Start higher + faster slope
      return {
        year: `Año ${i}`,
        Grado: Math.round(baseSalary),
        Master: Math.round(masterSalary),
        spread: Math.round(masterSalary - baseSalary)
      };
    }).slice(0, years + 1), [years, signaling]);

  return (
    <div className="h-full grid grid-cols-12 gap-4">
      {/* Controls Panel */}
      <div className="col-span-12 md:col-span-3 flex flex-col gap-4">
        <Card title="Configuración" icon={Zap}>
          <div className="space-y-6">
            <div>
              <label className="text-xs font-bold text-slate-500 flex justify-between mb-2">
                <span>VISIÓN (AÑOS)</span> <span className="text-blue-400">{years}</span>
              </label>
              <input type="range" min="2" max="10" value={years} onChange={(e) => setYears(Number(e.target.value))} className="w-full accent-blue-500 h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer"/>
            </div>
            <div>
              <label className="text-xs font-bold text-slate-500 flex justify-between mb-2">
                <span>FACTOR SEÑALIZACIÓN</span> <span className="text-purple-400">x{signaling}</span>
              </label>
              <input type="range" min="1" max="1.5" step="0.1" value={signaling} onChange={(e) => setSignaling(Number(e.target.value))} className="w-full accent-purple-500 h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer"/>
              <p className="text-[10px] text-slate-500 mt-2 leading-tight">
                Qué tanto "brilla" tu máster (Prestigio de escuela, notas, networking).
              </p>
            </div>
          </div>
        </Card>
        
        <Card title="Junior Insight" icon={AlertTriangle} className="bg-amber-500/5 border-amber-500/20">
          <p className="text-sm text-slate-300 mb-2">
            <span className="font-bold text-amber-400">El mito de la experiencia:</span>
          </p>
          <p className="text-xs text-slate-400 leading-relaxed">
            Las empresas saben que no sabes. Te contratan por tu <span className="text-white">pendiente de aprendizaje</span> (lo rápido que aprenderás), no por tu conocimiento actual. El máster demuestra capacidad de sacrificio y foco.
          </p>
        </Card>
      </div>

      {/* Chart Area */}
      <div className="col-span-12 md:col-span-9 flex flex-col gap-4">
        <Card className="flex-1 relative overflow-hidden" title="Proyección de Valor de Mercado">
            <div className="absolute right-6 top-6 z-10 flex gap-4">
               <div className="text-right">
                 <p className="text-[10px] uppercase text-slate-500 font-bold">Diferencial Acumulado</p>
                 <p className="text-xl font-mono font-bold text-blue-400">{(data[years].spread * years / 1000).toFixed(0)}k€</p>
               </div>
            </div>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data} margin={{ top: 20, right: 0, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorMaster" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis dataKey="year" stroke="#475569" tick={{fontSize: 10}} />
                <YAxis stroke="#475569" tick={{fontSize: 10}} tickFormatter={(val) => `${val/1000}k`} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }} />
                <Legend />
                <Area name="Carrera con Máster" type="monotone" dataKey="Master" stroke="#8b5cf6" strokeWidth={3} fill="url(#colorMaster)" />
                <Area name="Solo Grado" type="monotone" dataKey="Grado" stroke="#64748b" strokeWidth={2} strokeDasharray="5 5" fill="transparent" />
              </AreaChart>
            </ResponsiveContainer>
        </Card>
      </div>
    </div>
  );
};

// 3. RUTAS (Layout Maestro-Detalle)
const SlidePaths = () => {
  const [selected, setSelected] = useState('consulting');
  const details = {
    consulting: {
      role: "Consultoría / Banca",
      desc: "High risk, high reward. Aceleradora de carrera.",
      stats: [
        { label: "Salario", val: 90, max: 100 },
        { label: "Vida/Trabajo", val: 20, max: 100 },
        { label: "Aprendizaje", val: 95, max: 100 },
      ],
      reality: "Prepárate para jornadas largas. Ideal para 2-3 años y luego saltar a cliente."
    },
    corporate: {
      role: "Graduate Program (Cliente)",
      desc: "Estabilidad, formación estructurada y rotación.",
      stats: [
        { label: "Salario", val: 65, max: 100 },
        { label: "Vida/Trabajo", val: 75, max: 100 },
        { label: "Aprendizaje", val: 70, max: 100 },
      ],
      reality: "El crecimiento es más lento pero seguro. Compites contra burocracia interna."
    },
    abroad: {
      role: "Carrera Internacional",
      desc: "Salto cultural y madurez profesional acelerada.",
      stats: [
        { label: "Salario", val: 85, max: 100 },
        { label: "Vida/Trabajo", val: 60, max: 100 },
        { label: "Crecimiento", val: 90, max: 100 },
      ],
      reality: "Al principio estarás solo. Al volver, tu perfil vale doble por los idiomas."
    }
  };

  return (
    <div className="h-full grid grid-cols-12 gap-4">
      {/* Selector */}
      <div className="col-span-12 md:col-span-4 flex flex-col gap-3">
        <h2 className="text-xl font-bold text-white mb-2 px-1">Selecciona tu Ruta</h2>
        <div 
          onClick={() => setSelected('consulting')}
          className={`cursor-pointer p-4 rounded-xl border transition-all ${selected === 'consulting' ? 'bg-blue-900/20 border-blue-500 ring-1 ring-blue-500/50' : 'bg-slate-900 border-slate-800 hover:border-slate-700'}`}
        >
          <div className="flex items-center gap-3">
            <Building2 className={selected==='consulting' ? 'text-blue-400' : 'text-slate-500'} />
            <div>
              <h3 className="text-sm font-bold text-slate-200">Consultoría Estratégica</h3>
              <p className="text-[10px] text-slate-500">McKinsey, BCG, Big4...</p>
            </div>
          </div>
        </div>

        <div 
          onClick={() => setSelected('corporate')}
          className={`cursor-pointer p-4 rounded-xl border transition-all ${selected === 'corporate' ? 'bg-green-900/20 border-green-500 ring-1 ring-green-500/50' : 'bg-slate-900 border-slate-800 hover:border-slate-700'}`}
        >
          <div className="flex items-center gap-3">
            <Users className={selected==='corporate' ? 'text-green-400' : 'text-slate-500'} />
            <div>
              <h3 className="text-sm font-bold text-slate-200">Empresa Cliente</h3>
              <p className="text-[10px] text-slate-500">Graduate Programs, IBEX35...</p>
            </div>
          </div>
        </div>

        <div 
          onClick={() => setSelected('abroad')}
          className={`cursor-pointer p-4 rounded-xl border transition-all ${selected === 'abroad' ? 'bg-orange-900/20 border-orange-500 ring-1 ring-orange-500/50' : 'bg-slate-900 border-slate-800 hover:border-slate-700'}`}
        >
          <div className="flex items-center gap-3">
            <Plane className={selected==='abroad' ? 'text-orange-400' : 'text-slate-500'} />
            <div>
              <h3 className="text-sm font-bold text-slate-200">Internacional</h3>
              <p className="text-[10px] text-slate-500">Londres, Dublín, Ámsterdam...</p>
            </div>
          </div>
        </div>
      </div>

      {/* Details Panel */}
      <div className="col-span-12 md:col-span-8">
        <Card className="h-full border-t-4 border-t-slate-700">
          <div className="flex flex-col h-full">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h2 className="text-3xl font-bold text-white mb-2">{details[selected].role}</h2>
                <p className="text-slate-400 text-lg">{details[selected].desc}</p>
              </div>
              <Badge color={selected === 'consulting' ? 'blue' : selected === 'corporate' ? 'green' : 'amber'}>
                Ruta Común
              </Badge>
            </div>

            <div className="grid grid-cols-2 gap-8 flex-1">
              {/* Stats bars */}
              <div className="space-y-4 justify-center flex flex-col">
                {details[selected].stats.map((stat, i) => (
                  <div key={i}>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-slate-400 font-bold uppercase">{stat.label}</span>
                      <span className="text-slate-500">{stat.val}/100</span>
                    </div>
                    <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                      <div 
                        className={`h-full rounded-full transition-all duration-700 ${stat.val > 80 ? 'bg-green-500' : stat.val > 50 ? 'bg-blue-500' : 'bg-red-500'}`} 
                        style={{ width: `${stat.val}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>

              <div className="bg-slate-950 p-6 rounded-xl border border-slate-800 flex flex-col justify-center">
                <h4 className="text-xs font-bold text-slate-500 uppercase mb-3 flex items-center gap-2">
                  <Star size={12} className="text-yellow-500" /> Reality Check
                </h4>
                <p className="text-slate-300 text-sm leading-relaxed italic">
                  "{details[selected].reality}"
                </p>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

// 4. EMBUDO (Con foco en Calidad)
const SlideFunnel = () => {
  const [strategy, setStrategy] = useState('targeted');
  // Data simulated
  const data = strategy === 'massive' 
    ? [ { name: 'Envíos', val: 50 }, { name: 'Vistos', val: 5 }, { name: 'Entrevista', val: 1 }, { name: 'Oferta', val: 0 } ]
    : [ { name: 'Envíos', val: 10 }, { name: 'Vistos', val: 8 }, { name: 'Entrevista', val: 4 }, { name: 'Oferta', val: 1 } ];

  return (
    <div className="h-full grid grid-cols-12 gap-4">
      <div className="col-span-12 md:col-span-4 flex flex-col gap-4">
        <h2 className="text-xl font-bold text-white px-1">Estrategia de Caza</h2>
        <div className="grid grid-cols-2 md:grid-cols-1 gap-3">
            <button onClick={() => setStrategy('massive')} className={`p-4 rounded-xl border text-left transition-all ${strategy==='massive' ? 'bg-red-900/20 border-red-500 text-white' : 'bg-slate-900 border-slate-800 text-slate-500'}`}>
                <div className="font-bold text-sm mb-1">Estrategia Escopeta</div>
                <div className="text-xs opacity-70">50 CVs genéricos/semana.</div>
            </button>
            <button onClick={() => setStrategy('targeted')} className={`p-4 rounded-xl border text-left transition-all ${strategy==='targeted' ? 'bg-green-900/20 border-green-500 text-white' : 'bg-slate-900 border-slate-800 text-slate-500'}`}>
                <div className="font-bold text-sm mb-1">Estrategia Francotirador</div>
                <div className="text-xs opacity-70">10 CVs adaptados + Networking.</div>
            </button>
        </div>
        <Card title="Networking Multiplier" className="bg-blue-900/10 border-blue-500/20">
             <p className="text-xs text-blue-200 leading-relaxed">
                 <span className="font-bold">Pro Tip Junior:</span> Como no tienes experiencia previa, tu mejor baza es la <span className="underline">recomendación</span>. Contactar a un ex-alumno por LinkedIn multiplica x10 tus chances de entrevista frente a aplicar por web.
             </p>
        </Card>
      </div>
      <div className="col-span-12 md:col-span-8">
          <Card title="Conversión del Embudo">
              <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data} layout="vertical" margin={{left:20, right:20}}>
                      <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#334155" />
                      <XAxis type="number" stroke="#475569" hide />
                      <YAxis dataKey="name" type="category" stroke="#94a3b8" width={80} tick={{fontSize:12}} />
                      <Bar dataKey="val" barSize={40} radius={[0,4,4,0]}>
                          {data.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={strategy==='massive' ? '#ef4444' : '#22c55e'} />
                          ))}
                      </Bar>
                  </BarChart>
              </ResponsiveContainer>
              <div className="mt-4 text-center">
                  <p className={`text-lg font-bold ${strategy==='targeted' ? 'text-green-400' : 'text-red-400'}`}>
                      {strategy === 'targeted' ? 'Alta Eficiencia: Menos estrés, mejor resultado.' : 'Burnout Seguro: Mucho esfuerzo, cero feedback.'}
                  </p>
              </div>
          </Card>
      </div>
    </div>
  );
};

// 5. INGENIERÍA DE CV (Rediseñado con Regla de 1 Página)
const SlideCV = () => {
  const [mode, setMode] = useState('bad'); // 'bad' (Multi page, tasks) vs 'good' (1 page, achievements)

  return (
    <div className="h-full grid grid-cols-12 gap-4">
      <div className="col-span-12 md:col-span-5 flex flex-col gap-4">
        <div className="flex bg-slate-900 p-1 rounded-lg border border-slate-800">
           <button onClick={() => setMode('bad')} className={`flex-1 py-2 text-xs font-bold rounded ${mode==='bad' ? 'bg-slate-700 text-white' : 'text-slate-500'}`}>CV Genérico</button>
           <button onClick={() => setMode('good')} className={`flex-1 py-2 text-xs font-bold rounded ${mode==='good' ? 'bg-green-600 text-white' : 'text-slate-500'}`}>CV Alto Impacto</button>
        </div>

        <Card title="Diferencias Críticas">
            <ul className="space-y-4 mt-2">
                <li className="flex items-start gap-3">
                    {mode==='good' ? <CheckCircle className="text-green-500 shrink-0" size={16}/> : <AlertTriangle className="text-red-500 shrink-0" size={16}/>}
                    <div>
                        <span className="text-sm font-bold text-slate-200">Extensión:</span>
                        <p className="text-xs text-slate-400 mt-1">
                            {mode==='good' ? "1 Página estricta. Fuerza a priorizar lo relevante." : "2-3 Páginas. Incluye experiencias irrelevantes y mucho texto."}
                        </p>
                    </div>
                </li>
                <li className="flex items-start gap-3">
                    {mode==='good' ? <CheckCircle className="text-green-500 shrink-0" size={16}/> : <AlertTriangle className="text-red-500 shrink-0" size={16}/>}
                    <div>
                        <span className="text-sm font-bold text-slate-200">Contenido:</span>
                        <p className="text-xs text-slate-400 mt-1">
                            {mode==='good' ? "Logros (Métricas, %, €). Ej: 'Reduje tiempo entrega un 20%'." : "Tareas (Lista de la compra). Ej: 'Hacer informes y análisis'."}
                        </p>
                    </div>
                </li>
            </ul>
        </Card>

        <Card className="bg-slate-950 border-dashed border-slate-800 flex items-center justify-center">
            <div className="text-center">
                 <h3 className="text-xs uppercase text-slate-500 font-bold mb-1">Junior Insight</h3>
                 <p className="text-sm text-slate-300">
                     ¿Sin experiencia? Usa tus <span className="text-blue-400">Proyectos de Máster</span> como experiencia laboral. Ponle título al rol (ej. "Analista Junior - Proyecto Académico") y describe logros, no el temario.
                 </p>
            </div>
        </Card>
      </div>

      {/* Visualización del CV */}
      <div className="col-span-12 md:col-span-7 bg-slate-900 rounded-xl border border-slate-800 p-8 flex items-center justify-center relative overflow-hidden">
         {/* Background pattern */}
         <div className="absolute inset-0 opacity-10" style={{backgroundImage: 'radial-gradient(#475569 1px, transparent 1px)', backgroundSize: '20px 20px'}}></div>
         
         {/* CV Mockup */}
         <div className={`transition-all duration-500 bg-white shadow-2xl relative ${mode==='good' ? 'w-[300px] h-[420px]' : 'w-[300px] h-[550px] translate-y-10'}`}>
             {/* Header */}
             <div className="h-12 bg-slate-200 m-4 mb-2"></div>
             {/* Lines */}
             <div className="space-y-2 p-4 pt-0">
                 <div className="h-2 bg-slate-100 w-full"></div>
                 <div className="h-2 bg-slate-100 w-3/4"></div>
                 <div className="h-2 bg-slate-100 w-5/6"></div>
                 <div className="h-8 bg-slate-50 w-full mt-4 border border-dashed border-slate-300"></div>
                 <div className="h-2 bg-slate-100 w-full"></div>
                 <div className="h-2 bg-slate-100 w-full"></div>
             </div>
             
             {/* The "Golden Rule" Overlay */}
             {mode === 'good' && (
                 <div className="absolute -right-4 -top-4 bg-green-500 text-white p-2 rounded-full shadow-lg animate-bounce">
                     <CheckCircle size={24} />
                 </div>
             )}
             {mode === 'bad' && (
                 <div className="absolute inset-0 bg-red-500/10 backdrop-blur-[1px] flex items-center justify-center">
                     <div className="bg-red-600 text-white px-4 py-2 rounded font-bold rotate-12 border-2 border-white">TOO LONG</div>
                 </div>
             )}
         </div>

         {/* Stats overlay */}
         <div className="absolute bottom-4 right-4 bg-slate-800/90 backdrop-blur p-3 rounded-lg border border-slate-700">
             <div className="text-[10px] text-slate-400 uppercase font-bold">Probabilidad de Lectura</div>
             <div className={`text-2xl font-mono font-bold ${mode==='good' ? 'text-green-400' : 'text-red-400'}`}>
                 {mode==='good' ? '95%' : '15%'}
             </div>
         </div>
      </div>
    </div>
  );
};

// 6. RECURSOS (Bento Grid denso)
const SlideResources = () => (
    <div className="h-full grid grid-cols-12 grid-rows-2 gap-4">
        <div className="col-span-12 md:col-span-6 md:row-span-2">
            <Card title="Portales Especializados (No uses Infojobs)" icon={Globe}>
                <div className="space-y-4 mt-2">
                    <div className="flex gap-4 items-start p-3 rounded bg-slate-950 border border-slate-800">
                        <div className="bg-purple-500/20 p-2 rounded text-purple-400 font-bold text-xs text-center min-w-[80px]">GRAD<br/>CRACKER</div>
                        <div>
                            <p className="text-sm font-bold text-slate-200">Para STEM & Data</p>
                            <p className="text-xs text-slate-500">Si buscas roles técnicos o de ingeniería, este es el estándar.</p>
                        </div>
                    </div>
                    <div className="flex gap-4 items-start p-3 rounded bg-slate-950 border border-slate-800">
                        <div className="bg-blue-500/20 p-2 rounded text-blue-400 font-bold text-xs text-center min-w-[80px]">GRADUATE<br/>SHIPS</div>
                        <div>
                            <p className="text-sm font-bold text-slate-200">Programas Europeos</p>
                            <p className="text-xs text-slate-500">Agregador de Graduate Programs en multinacionales.</p>
                        </div>
                    </div>
                    <div className="flex gap-4 items-start p-3 rounded bg-slate-950 border border-slate-800">
                        <div className="bg-blue-700/20 p-2 rounded text-blue-300 font-bold text-xs text-center min-w-[80px]">LINKEDIN</div>
                        <div>
                            <p className="text-sm font-bold text-slate-200">El Buscador Booleano</p>
                            <p className="text-xs text-slate-500">Usa: <code>"Graduate" AND ("Analyst" OR "Associate")</code> en la barra de búsqueda.</p>
                        </div>
                    </div>
                </div>
            </Card>
        </div>
        <div className="col-span-12 md:col-span-6 row-span-1">
            <Card title="Creadores de CV (ATS Friendly)" icon={Layout}>
                <div className="grid grid-cols-2 gap-3 h-full">
                    <button className="bg-slate-950 p-3 rounded border border-slate-800 hover:border-slate-600 flex flex-col justify-center text-center">
                        <span className="font-bold text-slate-200 text-sm">FlowCV</span>
                        <span className="text-[10px] text-green-500">Gratis & Top Tier</span>
                    </button>
                    <button className="bg-slate-950 p-3 rounded border border-slate-800 hover:border-slate-600 flex flex-col justify-center text-center">
                        <span className="font-bold text-slate-200 text-sm">Novorésumé</span>
                        <span className="text-[10px] text-blue-500">Corporativo</span>
                    </button>
                </div>
            </Card>
        </div>
        <div className="col-span-12 md:col-span-6 row-span-1">
            <Card title="El Consejo Final" className="bg-gradient-to-br from-slate-900 to-green-900/10 border-green-500/20">
                <div className="flex items-center gap-4 h-full">
                    <CheckCircle className="text-green-500 w-12 h-12" />
                    <p className="text-sm text-slate-300 italic">
                        "Tu primer trabajo no define tu carrera, pero define tu velocidad de aprendizaje. Busca jefes mentores, no solo sueldos altos."
                    </p>
                </div>
            </Card>
        </div>
    </div>
);

// --- APP ORCHESTRATOR ---

const App = () => {
  const [currentSlide, setCurrentSlide] = useState(0);
  const slides = [
    { component: <SlideIntro onStart={() => setCurrentSlide(1)} />, title: "Dashboard" },
    { component: <SlideMasterValue />, title: "ROI Máster" },
    { component: <SlidePaths />, title: "Rutas" },
    { component: <SlideFunnel />, title: "Estrategia" },
    { component: <SlideCV />, title: "Ingeniería CV" },
    { component: <SlideResources />, title: "Toolkit" }
  ];

  const nextSlide = () => setCurrentSlide(prev => Math.min(prev + 1, slides.length - 1));
  const prevSlide = () => setCurrentSlide(prev => Math.max(prev - 1, 0));

  return (
    <div className={`w-full h-screen ${THEME.bg} flex flex-col overflow-hidden font-sans text-slate-200`}>
      {/* Top Bar */}
      <div className="h-12 border-b border-slate-800 flex items-center justify-between px-6 bg-slate-950/80 backdrop-blur z-20">
        <div className="flex items-center gap-2">
          <GraduationCap className="text-blue-500" size={18} />
          <span className="font-bold text-sm tracking-tight">Career<span className="text-blue-500">Alpha</span> <span className="text-slate-600">v2.1</span></span>
        </div>
        <div className="text-[10px] uppercase font-bold text-slate-500 tracking-widest">
          {slides[currentSlide].title}
        </div>
      </div>

      {/* Main Content */}
      <main className="flex-1 p-4 md:p-6 lg:p-8 max-w-7xl mx-auto w-full h-full relative">
        {slides[currentSlide].component}
      </main>

      {/* Bottom Nav */}
      <div className="h-14 border-t border-slate-800 bg-slate-900/50 flex items-center justify-between px-6 z-20">
        <div className="flex gap-1">
           {slides.map((_, i) => (
               <div key={i} className={`h-1.5 w-6 rounded-full transition-all ${i === currentSlide ? 'bg-blue-500 w-12' : 'bg-slate-800'}`} />
           ))}
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" onClick={prevSlide} disabled={currentSlide === 0} className="px-3 py-1 text-xs">
            Anterior
          </Button>
          <Button variant="primary" onClick={nextSlide} disabled={currentSlide === slides.length - 1} className="px-3 py-1 text-xs">
            Siguiente
          </Button>
        </div>
      </div>
      
      <style>{`
        .animate-fade-in { animation: fadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards; opacity: 0; transform: scale(0.98); }
        @keyframes fadeIn { to { opacity: 1; transform: scale(1); } }
      `}</style>
    </div>
  );
};

export default App;