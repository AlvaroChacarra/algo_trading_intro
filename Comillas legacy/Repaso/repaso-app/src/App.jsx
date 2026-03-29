import React, { useState, useEffect, useRef } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area, ReferenceLine, ComposedChart 
} from 'recharts';
import { 
  ArrowRight, ArrowLeft, Play, Pause, RefreshCw, TrendingUp, BarChart3, Zap, Cpu, Layers, Target, Activity, DollarSign, Scale, AlertTriangle, Lightbulb, Eye, Anchor, BookOpen, GitBranch, Users, History, Rocket, Bot, Brain, Code, Sparkles, ClipboardCheck, FileCode, Database, CheckCircle, Key, Lock, Boxes, PlayCircle 
} from 'lucide-react';

// --- UTILIDADES GLOBALES ---
const formatNumber = (num) => num.toFixed(2);
const formatVol = (num) => Math.floor(num).toLocaleString();
const generateId = () => Math.random().toString(36).substr(2, 9);
const roundToTick = (price) => Math.round(price * 20) / 20;

// Generador Gaussiano (Box-Muller) para movimiento Browniano realista
const randn_bm = () => {
    let u = 0, v = 0;
    while(u === 0) u = Math.random();
    while(v === 0) v = Math.random();
    return Math.sqrt( -2.0 * Math.log( u ) ) * Math.cos( 2.0 * Math.PI * v );
};

const generateBook = (midPrice, levels = 20, spread = 0.5) => {
  const bids = [];
  const asks = [];
  const startBid = roundToTick(midPrice - (spread/2));
  const startAsk = roundToTick(midPrice + (spread/2));
  for (let i = 0; i < levels; i++) {
    const vol = Math.floor(50 + (i * i * 10) + Math.random() * 50);
    bids.push({ id: `b-${i}`, price: parseFloat((startBid - (i * 0.05)).toFixed(2)), size: vol });
    asks.push({ id: `a-${i}`, price: parseFloat((startAsk + (i * 0.05)).toFixed(2)), size: vol });
  }
  return { bids, asks };
};

// --- COMPONENTES UI GENÉRICOS ---
const Card = ({ children, className = "" }) => (
  <div className={`bg-slate-900 border border-slate-800 rounded-lg shadow-xl overflow-hidden ${className}`}>
    {children}
  </div>
);

const Badge = ({ children, color }) => (
  <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${color}`}>
    {children}
  </span>
);

// ----------------------------------------------------------------------
// SLIDE RECAP (DISEÑO OPTIMIZADO: 3 FILAS)
// ----------------------------------------------------------------------
const RecapSlide = ({ title, subtitle, columns }) => {
  return (
    <div className="flex flex-col h-full bg-black text-slate-300 p-10 gap-8 font-sans">
        <div className="border-b border-slate-800 pb-6 flex items-center gap-6 shrink-0">
            <div className="p-4 bg-yellow-900/20 rounded-2xl border border-yellow-700/50 shadow-[0_0_15px_rgba(234,179,8,0.2)]">
                <BookOpen size={48} className="text-yellow-500" />
            </div>
            <div>
                <h2 className="text-5xl font-extrabold text-white tracking-tight">{title}</h2>
                <p className="text-2xl text-slate-500 mt-2 font-light">{subtitle}</p>
            </div>
        </div>

        <div className="flex flex-col gap-6 flex-1 justify-center min-h-0">
            {columns.map((col, idx) => (
                <div key={idx} className="flex-1 bg-slate-900/40 p-8 rounded-2xl border border-slate-800 hover:border-slate-600 hover:bg-slate-800/60 transition-all duration-300 flex items-center gap-10 shadow-lg group">
                    <div className={`p-6 rounded-3xl bg-opacity-20 shrink-0 ${col.colorBg} transition-transform group-hover:scale-110 duration-500`}>
                        <col.icon size={48} className={col.colorText} />
                    </div>
                    <div className="flex-1 flex flex-col justify-center h-full space-y-4">
                        <h3 className="text-3xl font-bold text-slate-100 tracking-wide border-b border-slate-700/50 pb-2 w-fit">
                            {col.title}
                        </h3>
                        <div className="space-y-3">
                            {col.points.map((p, pIdx) => (
                                <div key={pIdx} className="text-xl leading-relaxed text-slate-400">
                                    {p.highlight && (
                                        <span className={`font-bold mr-3 ${col.colorText} brightness-125`}>
                                            {p.highlight}:
                                        </span>
                                    )}
                                    <span className="text-slate-300 font-light">
                                        {p.text}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            ))}
        </div>
    </div>
  );
};

// ----------------------------------------------------------------------
// SLIDE 1: TRADING TERMINAL (LOB)
// ----------------------------------------------------------------------
const OrderBookSlide = () => {
  const [bids, setBids] = useState([]);
  const [asks, setAsks] = useState([]);
  const [trades, setTrades] = useState([]);
  const [priceHistory, setPriceHistory] = useState([]); 
  const [tick, setTick] = useState(0);
  const [isSimulating, setIsSimulating] = useState(false);
  const [orderType, setOrderType] = useState('LIMIT');
  const [side, setSide] = useState('BUY');
  const [price, setPrice] = useState(100.00);
  const [size, setSize] = useState(50);

  useEffect(() => {
    const { bids: initBids, asks: initAsks } = generateBook(100.00, 20);
    setBids(initBids);
    setAsks(initAsks);
    const initialMid = (initBids[0].price + initAsks[0].price) / 2;
    setPriceHistory([{ t: 0, bid: initBids[0].price, ask: initAsks[0].price, mid: initialMid, last: null }]);
  }, []);

  const maxVol = Math.max(...bids.map(b => b.size), ...asks.map(a => a.size), 500);

  const processOrder = (incomingOrderType, incomingSide, incomingPrice, incomingSize) => {
    let remainingSize = parseInt(incomingSize);
    let executionPrice = parseFloat(incomingPrice);
    const newTrades = [];
    let lastTradePrice = null;
    let currentBids = [...bids].sort((a, b) => b.price - a.price);
    let currentAsks = [...asks].sort((a, b) => a.price - b.price);

    if (incomingSide === 'BUY') {
      while (remainingSize > 0 && currentAsks.length > 0) {
        const bestAsk = currentAsks[0];
        if (incomingOrderType === 'LIMIT' && bestAsk.price > executionPrice) break;
        const tradeSize = Math.min(remainingSize, bestAsk.size);
        const tradePrice = bestAsk.price;
        lastTradePrice = tradePrice;
        newTrades.unshift({ id: generateId(), price: tradePrice, size: tradeSize, side: 'BUY', time: new Date().toLocaleTimeString().split(' ')[0] });
        remainingSize -= tradeSize;
        bestAsk.size -= tradeSize;
        if (bestAsk.size === 0) currentAsks.shift();
      }
      if (remainingSize > 0 && incomingOrderType === 'LIMIT') {
        const finalPrice = roundToTick(executionPrice);
        const existing = currentBids.find(b => Math.abs(b.price - finalPrice) < 0.001);
        if (existing) existing.size += remainingSize;
        else currentBids.push({ id: generateId(), price: finalPrice, size: remainingSize });
      }
    } else {
      while (remainingSize > 0 && currentBids.length > 0) {
        const bestBid = currentBids[0];
        if (incomingOrderType === 'LIMIT' && bestBid.price < executionPrice) break;
        const tradeSize = Math.min(remainingSize, bestBid.size);
        const tradePrice = bestBid.price;
        lastTradePrice = tradePrice;
        newTrades.unshift({ id: generateId(), price: tradePrice, size: tradeSize, side: 'SELL', time: new Date().toLocaleTimeString().split(' ')[0] });
        remainingSize -= tradeSize;
        bestBid.size -= tradeSize;
        if (bestBid.size === 0) currentBids.shift();
      }
      if (remainingSize > 0 && incomingOrderType === 'LIMIT') {
        const finalPrice = roundToTick(executionPrice);
        const existing = currentAsks.find(a => Math.abs(a.price - finalPrice) < 0.001);
        if (existing) existing.size += remainingSize;
        else currentAsks.push({ id: generateId(), price: finalPrice, size: remainingSize });
      }
    }

    currentAsks.sort((a, b) => a.price - b.price);
    currentBids.sort((a, b) => b.price - a.price);
    setAsks(currentAsks);
    setBids(currentBids);
    setTrades(prev => [...newTrades, ...prev].slice(0, 50));

    const newBestBid = currentBids.length > 0 ? currentBids[0].price : null;
    const newBestAsk = currentAsks.length > 0 ? currentAsks[0].price : null;
    let newMid = lastTradePrice;
    if (newBestBid && newBestAsk) newMid = (newBestBid + newBestAsk) / 2;

    if (newMid) {
        setTick(t => t + 1);
        setPriceHistory(prev => {
        const prevLast = prev.length > 0 ? prev[prev.length - 1].last : null;
        const newHistory = [...prev, { t: tick + 1, bid: newBestBid, ask: newBestAsk, mid: newMid, last: lastTradePrice || prevLast }];
        if (newHistory.length > 50) newHistory.shift(); 
        return newHistory;
        });
    }
  };

  const handleManualSubmit = (e) => { e.preventDefault(); processOrder(orderType, side, price, size); };

  useEffect(() => {
    if (!isSimulating) return;
    const timeout = setTimeout(() => {
        const actionType = Math.random() > 0.7 ? 'MARKET' : 'LIMIT';
        const simSide = Math.random() > 0.5 ? 'BUY' : 'SELL';
        const bestBid = bids.length > 0 ? bids[0].price : 100;
        const bestAsk = asks.length > 0 ? asks[0].price : 100;
        
        if (actionType === 'MARKET') {
            const simSize = Math.floor(Math.random() * 30) + 5;
            processOrder('MARKET', simSide, 0, simSize); 
        } else {
            let simPrice;
            if (simSide === 'BUY') {
                const r = Math.random();
                if (r < 0.4) simPrice = bestBid;
                else if (r < 0.7) simPrice = bestBid + 0.05;
                else simPrice = bestBid - 0.05;
                if (simPrice >= bestAsk) simPrice = bestBid; 
            } else {
                const r = Math.random();
                if (r < 0.4) simPrice = bestAsk;
                else if (r < 0.7) simPrice = bestAsk - 0.05;
                else simPrice = bestAsk + 0.05;
                if (simPrice <= bestBid) simPrice = bestAsk;
            }
            simPrice = roundToTick(simPrice);
            const simSize = Math.floor(Math.random() * 80) + 10;
            processOrder('LIMIT', simSide, simPrice, simSize);
        }
    }, 300);
    return () => clearTimeout(timeout);
  }, [isSimulating, bids, asks, tick]); 

  const bestBid = bids.length > 0 ? bids[0].price : 0;
  const bestAsk = asks.length > 0 ? asks[0].price : 0;
  const spread = bestAsk - bestBid;
  const midPrice = (bestBid + bestAsk) / 2;

  return (
    <div className="flex flex-col h-full bg-black text-slate-300 p-4 gap-4 font-mono text-sm">
      <div className="flex justify-between items-center bg-slate-900 p-3 rounded border border-slate-800">
        <div className="flex items-center gap-4">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <BarChart3 className="text-blue-500" />
                MARKET<span className="text-blue-500">PRO</span>
            </h2>
            <div className="h-6 w-px bg-slate-700"></div>
            <div className="flex gap-4 text-xs">
                <div>
                    <span className="text-slate-500 block">SPREAD</span>
                    <span className={`${spread < 0.2 ? 'text-green-500' : 'text-yellow-500'} font-bold`}>{spread > 0 ? spread.toFixed(2) : 'LOCKED'}</span>
                </div>
                 <div>
                    <span className="text-slate-500 block">MID PRICE</span>
                    <span className="text-blue-400 font-bold">{midPrice.toFixed(2)}</span>
                </div>
            </div>
        </div>
        <button onClick={() => setIsSimulating(!isSimulating)} className={`flex items-center gap-2 px-4 py-1.5 rounded text-xs font-bold transition-all border ${isSimulating ? 'bg-orange-500/20 border-orange-500 text-orange-400 animate-pulse' : 'bg-slate-800 border-slate-700 text-slate-400 hover:text-white'}`}>
            {isSimulating ? <><Cpu size={14} className="animate-spin"/> ALGO RUNNING</> : <><Play size={14}/> START SIM</>}
        </button>
      </div>
      <div className="grid grid-cols-12 grid-rows-6 gap-4 flex-1 min-h-0">
        <Card className="col-span-8 row-span-3 p-2 relative group">
            <ResponsiveContainer width="100%" height="100%">
                <LineChart data={priceHistory}>
                    <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" vertical={false} />
                    <YAxis domain={['dataMin - 0.2', 'dataMax + 0.2']} orientation="right" tick={{fill: '#64748b', fontSize: 10}} width={40} axisLine={false} tickLine={false} />
                    <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff', fontSize: '12px' }} itemStyle={{ padding: 0 }} />
                    <Legend wrapperStyle={{ fontSize: '10px', paddingTop: '0px' }} />
                    <Line name="Bid" type="stepAfter" dataKey="bid" stroke="#22c55e" strokeWidth={1} dot={false} isAnimationActive={false} />
                    <Line name="Ask" type="stepAfter" dataKey="ask" stroke="#ef4444" strokeWidth={1} dot={false} isAnimationActive={false} />
                    <Line name="Mid Price" type="monotone" dataKey="mid" stroke="#3b82f6" strokeWidth={2} dot={false} isAnimationActive={false} />
                    <Line name="Last Trade" type="monotone" dataKey="last" stroke="#f59e0b" strokeWidth={0} dot={{ r: 3, fill: '#f59e0b' }} isAnimationActive={false} />
                </LineChart>
            </ResponsiveContainer>
        </Card>
        <Card className="col-span-4 row-span-3 p-4 flex flex-col justify-between bg-slate-800/50">
            <div>
                <h3 className="text-white font-bold mb-4 flex items-center gap-2 text-sm border-b border-slate-700 pb-2"><Zap size={14} className="text-yellow-500"/> QUICK TRADE</h3>
                <form onSubmit={handleManualSubmit} className="space-y-3">
                    <div className="grid grid-cols-2 gap-2">
                         <button type="button" onClick={() => setSide('BUY')} className={`py-2 text-xs font-bold rounded ${side === 'BUY' ? 'bg-green-600 text-white' : 'bg-slate-700 text-slate-400'}`}>BUY</button>
                         <button type="button" onClick={() => setSide('SELL')} className={`py-2 text-xs font-bold rounded ${side === 'SELL' ? 'bg-red-600 text-white' : 'bg-slate-700 text-slate-400'}`}>SELL</button>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                         <button type="button" onClick={() => setOrderType('LIMIT')} className={`py-1 text-[10px] font-bold rounded border ${orderType === 'LIMIT' ? 'border-blue-500 text-blue-400' : 'border-slate-600 text-slate-500'}`}>LIMIT</button>
                         <button type="button" onClick={() => setOrderType('MARKET')} className={`py-1 text-[10px] font-bold rounded border ${orderType === 'MARKET' ? 'border-blue-500 text-blue-400' : 'border-slate-600 text-slate-500'}`}>MARKET</button>
                    </div>
                    <div className="space-y-1">
                        <label className="text-[10px] text-slate-500">PRICE (Tick 0.05)</label>
                        <input type="number" step="0.05" value={orderType === 'MARKET' ? 0 : price} onChange={e => setPrice(e.target.value)} disabled={orderType === 'MARKET'} className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-right text-white focus:border-blue-500 outline-none" placeholder="MKT" />
                    </div>
                    <div className="space-y-1">
                        <label className="text-[10px] text-slate-500">SIZE</label>
                        <input type="number" min="1" value={size} onChange={e => setSize(e.target.value)} className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-right text-white focus:border-blue-500 outline-none" />
                    </div>
                </form>
            </div>
            <button onClick={handleManualSubmit} className={`w-full py-3 rounded font-bold text-sm shadow-lg transition-transform active:scale-95 ${side === 'BUY' ? 'bg-green-600 hover:bg-green-500 text-white' : 'bg-red-600 hover:bg-red-500 text-white'}`}>PLACE {side} ORDER</button>
        </Card>
        <Card className="col-span-8 row-span-3 flex flex-row relative">
             <div className="absolute top-2 left-2 z-20 flex gap-2"><Badge color="bg-slate-800 text-slate-500">LOB DEPTH: {bids.length + asks.length}</Badge></div>
            <div className="flex-1 flex flex-col border-r border-slate-800">
                <div className="flex justify-between px-3 py-1 bg-slate-900/80 text-[10px] text-slate-500 font-bold mt-6"><span>VOL</span><span>BID</span></div>
                <div className="flex-1 overflow-y-auto no-scrollbar relative">
                    {bids.map((bid) => {
                        const widthPct = Math.min((bid.size / maxVol) * 100, 100);
                        return (
                            <div key={bid.id} className="flex justify-between items-center px-3 py-0.5 relative group hover:bg-slate-800 cursor-pointer text-xs h-5">
                                <div className="absolute right-0 top-0 bottom-0 bg-green-900/20 transition-all duration-300" style={{ width: `${widthPct}%` }}></div>
                                <span className="text-slate-400 relative z-10 font-mono text-[10px]">{formatVol(bid.size)}</span>
                                <span className="text-green-500 relative z-10 font-bold font-mono">{formatNumber(bid.price)}</span>
                            </div>
                        );
                    })}
                </div>
            </div>
            <div className="flex-1 flex flex-col">
                <div className="flex justify-between px-3 py-1 bg-slate-900/80 text-[10px] text-slate-500 font-bold mt-6"><span>ASK</span><span>VOL</span></div>
                <div className="flex-1 overflow-y-auto no-scrollbar relative">
                     {asks.map((ask) => {
                        const widthPct = Math.min((ask.size / maxVol) * 100, 100);
                        return (
                            <div key={ask.id} className="flex justify-between items-center px-3 py-0.5 relative group hover:bg-slate-800 cursor-pointer text-xs h-5">
                                <div className="absolute left-0 top-0 bottom-0 bg-red-900/20 transition-all duration-300" style={{ width: `${widthPct}%` }}></div>
                                <span className="text-red-500 relative z-10 font-bold font-mono">{formatNumber(ask.price)}</span>
                                <span className="text-slate-400 relative z-10 font-mono text-[10px]">{formatVol(ask.size)}</span>
                            </div>
                        );
                    })}
                </div>
            </div>
        </Card>
        <Card className="col-span-4 row-span-3 flex flex-col">
             <div className="px-3 py-2 bg-slate-800/50 text-[10px] font-bold text-slate-500 border-b border-slate-700 flex justify-between"><span>TIME</span><span>PRICE</span><span>QTY</span></div>
            <div className="flex-1 overflow-y-auto p-2 space-y-0.5 font-mono text-xs">
                {trades.map((trade) => (
                    <div key={trade.id} className="flex justify-between items-center hover:bg-slate-800 px-1 rounded animate-fadeIn">
                        <span className="text-slate-500">{trade.time}</span>
                        <span className={trade.side === 'BUY' ? 'text-green-500' : 'text-red-500'}>{formatNumber(trade.price)}</span>
                        <span className="text-slate-300">{trade.size}</span>
                    </div>
                ))}
            </div>
        </Card>
      </div>
    </div>
  );
};


// ----------------------------------------------------------------------
// SLIDE 3: KALMAN FILTER (COMPUESTO Y OPTIMIZADO)
// ----------------------------------------------------------------------
const KalmanSlide = () => {
  const [data, setData] = useState([]);
  const [truePrice, setTruePrice] = useState(100);
  const [estimate, setEstimate] = useState(100);
  const [errorCovariance, setErrorCovariance] = useState(1);
  const [isRunning, setIsRunning] = useState(false);
  const [mseMid, setMseMid] = useState(0);
  const [mseKalman, setMseKalman] = useState(0);
  const intervalRef = useRef(null);

  const Q = 0.05; 
  const NOISE_MID = 2.0; 
  const NOISE_TRADE = 0.2; 

  const simulationStep = (forceTrade = false) => {
    const volatility = 0.08; 
    const drift = randn_bm() * volatility;
    const newTruePrice = truePrice + drift;
    
    const midNoise = (Math.random() - 0.5) * NOISE_MID;
    const midPrice = newTruePrice + midNoise;

    const halfSpread = 0.5 + Math.random() * 0.5;
    const ask = midPrice + halfSpread;
    const bid = midPrice - halfSpread;
    
    let measurement, R, eventType;

    if (forceTrade) {
      const tradeNoise = (Math.random() - 0.5) * NOISE_TRADE; 
      measurement = newTruePrice + tradeNoise; 
      R = 0.1; 
      eventType = 'TRADE';
    } else {
      measurement = midPrice;
      R = 5.0; 
      eventType = 'QUOTE';
    }

    let predEstimate = estimate;
    let predError = errorCovariance + Q;

    const K = predError / (predError + R);
    const newEstimate = predEstimate + K * (measurement - predEstimate);
    const newErrorCovariance = (1 - K) * predError;

    const errMid = Math.pow(midPrice - newTruePrice, 2);
    const errKalman = Math.pow(newEstimate - newTruePrice, 2);

    setTruePrice(newTruePrice);
    setEstimate(newEstimate);
    setErrorCovariance(newErrorCovariance);
    setMseMid(prev => (prev * 0.95) + (errMid * 0.05)); 
    setMseKalman(prev => (prev * 0.95) + (errKalman * 0.05));

    setData(prev => {
      const newData = [...prev, {
        step: prev.length,
        TruePrice: newTruePrice,
        Measurement: measurement,
        MidPrice: midPrice,
        Kalman: newEstimate,
        Bid: bid,
        Ask: ask,
        BidAskRange: [bid, ask],
        EventType: eventType,
        K: K,
        id: generateId()
      }];
      if (newData.length > 60) newData.shift();
      return newData;
    });
  };

  useEffect(() => {
    if (isRunning) {
      intervalRef.current = setInterval(() => simulationStep(), 400); 
    } else {
      clearInterval(intervalRef.current);
    }
    return () => clearInterval(intervalRef.current);
  }, [isRunning, truePrice, estimate, errorCovariance]);

  const handleTrade = () => simulationStep(true);

  return (
    <div className="flex flex-col h-full bg-black text-slate-300 p-4 gap-4 font-mono text-sm">
       <div className="flex justify-between items-center bg-slate-900 p-3 rounded border border-slate-800">
         <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <Target className="text-purple-500" />
                SIGNAL<span className="text-purple-500">LAB</span>
                <span className="text-xs text-slate-500 ml-2 font-normal">LATENT PRICE ESTIMATION</span>
            </h2>
         </div>
         <div className="flex gap-2">
           <button onClick={() => setIsRunning(!isRunning)} className={`flex items-center gap-2 px-3 py-1 rounded text-xs font-bold ${isRunning ? 'bg-orange-600 text-white' : 'bg-green-600 text-white'}`}>
             {isRunning ? <><Pause size={12}/> PAUSE</> : <><Play size={12}/> AUTO SIM</>}
           </button>
           <button onClick={() => { setData([]); setTruePrice(100); setEstimate(100); }} className="p-1 bg-slate-800 rounded hover:bg-slate-700 text-slate-400">
             <RefreshCw size={14}/>
           </button>
         </div>
       </div>

       <div className="flex flex-col lg:flex-row h-full gap-4 min-h-0 flex-1">
          <Card className="flex-1 p-2 relative">
             <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={data}>
                  <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" opacity={0.5} />
                  <XAxis dataKey="step" hide />
                  <YAxis domain={['dataMin - 0.2', 'dataMax + 0.2']} tick={{fill: '#64748b', fontSize: 10}} width={40} axisLine={false} tickLine={false} />
                  <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff', fontSize: '12px' }} labelStyle={{ display: 'none' }} />
                  <Legend wrapperStyle={{ fontSize: '10px', paddingTop: '10px' }} />
                  <Area type="monotone" dataKey="BidAskRange" stroke="none" fill="#64748b" fillOpacity={0.15} name="Bid-Ask Spread" isAnimationActive={false} />
                  <Line type="monotone" dataKey="TruePrice" stroke="#10b981" strokeWidth={2} dot={false} strokeDasharray="5 5" name="Latent Price (True)" isAnimationActive={false} />
                  <Line type="monotone" dataKey="MidPrice" stroke="#475569" strokeWidth={1.5} dot={false} name="Mid Price (Noisy)" isAnimationActive={false} opacity={0.7} />
                  <Line type="monotone" dataKey="Kalman" stroke="#a855f7" strokeWidth={3} dot={false} name="Kalman Filter" isAnimationActive={false} />
                  <Line type="monotone" dataKey="Measurement" stroke="#f59e0b" strokeWidth={0} dot={(props) => {
                      if (props.payload.EventType !== 'TRADE') return null;
                      return <circle key={props.payload.id} cx={props.cx} cy={props.cy} r={5} fill="#f59e0b" stroke="#000" strokeWidth={1} />;
                  }} name="Trade Exec" isAnimationActive={false} />
                </ComposedChart>
             </ResponsiveContainer>
             
             <div className="absolute top-4 left-4 bg-black/80 p-2 rounded border border-slate-700 backdrop-blur-sm pointer-events-none">
                <div className="flex gap-4 text-[10px]">
                    <div className="flex flex-col">
                        <span className="text-slate-500">TRUE PRICE</span>
                        <span className="text-emerald-500 font-bold font-mono">{data.length > 0 ? data[data.length-1].TruePrice.toFixed(2) : '--'}</span>
                    </div>
                    <div className="flex flex-col">
                        <span className="text-slate-500">KALMAN EST.</span>
                        <span className="text-purple-500 font-bold font-mono">{data.length > 0 ? data[data.length-1].Kalman.toFixed(2) : '--'}</span>
                    </div>
                </div>
             </div>
          </Card>

          <div className="w-full lg:w-64 flex flex-col gap-3">
             <Card className="p-3 bg-slate-800/50">
                <h3 className="text-xs font-bold text-slate-400 mb-2 uppercase border-b border-slate-700 pb-2">Simulation Actions</h3>
                <p className="text-[10px] text-slate-500 mb-3">
                   Inject a "Trade" event. Trades occur closer to the True Price than the standard Quote/Mid price, providing high-quality information.
                </p>
                <button onClick={handleTrade} className="w-full py-3 bg-amber-600 hover:bg-amber-500 text-white rounded text-xs font-bold shadow-lg shadow-amber-900/20 active:scale-95 transition-transform flex items-center justify-center gap-2">
                   <Zap size={14} className="fill-white"/> EXECUTE TRADE
                </button>
             </Card>
             
             <Card className="p-3 flex-1 bg-slate-800/30 flex flex-col">
                <h3 className="text-xs font-bold text-slate-400 mb-2 uppercase border-b border-slate-700 pb-2">Performance Metrics (MSE)</h3>
                <div className="space-y-4 mt-2 flex-1">
                    <div>
                        <div className="flex justify-between text-[10px] text-slate-400 mb-1">
                            <span>MID PRICE ERROR</span>
                            <span>{mseMid.toFixed(4)}</span>
                        </div>
                        <div className="w-full bg-slate-700 h-1.5 rounded-full overflow-hidden">
                            <div className="bg-slate-400 h-full transition-all duration-300" style={{ width: `${Math.min(mseMid * 20, 100)}%` }}></div>
                        </div>
                    </div>

                    <div>
                        <div className="flex justify-between text-[10px] text-purple-300 mb-1">
                            <span>KALMAN ERROR</span>
                            <span className="font-bold">{mseKalman.toFixed(4)}</span>
                        </div>
                        <div className="w-full bg-slate-700 h-1.5 rounded-full overflow-hidden">
                            <div className="bg-purple-500 h-full transition-all duration-300" style={{ width: `${Math.min(mseKalman * 20, 100)}%` }}></div>
                        </div>
                    </div>
                    
                    <div className="mt-4 p-2 bg-green-900/20 border border-green-900/50 rounded text-[10px] text-green-400 text-center">
                        IMPROVEMENT: <span className="font-bold">{mseMid > 0 ? ((1 - (mseKalman/mseMid)) * 100).toFixed(1) : 0}%</span>
                    </div>
                </div>
             </Card>
          </div>
       </div>
    </div>
  );
};

// ----------------------------------------------------------------------
// SLIDE 4: MARKET MAKING (COMPETITIVO)
// ----------------------------------------------------------------------
const MarketMakingSlide = () => {
  const [history, setHistory] = useState([]);
  const [midPrice, setMidPrice] = useState(100);
  const [isRunning, setIsRunning] = useState(false);
  const [trend, setTrend] = useState(0); 
  
  const [invNaive, setInvNaive] = useState(0);
  const [cashNaive, setCashNaive] = useState(0);
  const [invAS, setInvAS] = useState(0);
  const [cashAS, setCashAS] = useState(0);
  
  const [gamma, setGamma] = useState(0.5); 
  const sigma = 0.5; 
  const spread = 0.5; 

  const intervalRef = useRef(null);

  const stepSimulation = () => {
    // Dinámica de Mercado
    const drift = trend * 0.1; 
    const noise = randn_bm() * 0.1;
    const newMid = midPrice + drift + noise;
    
    // Cotizaciones
    const bidNaive = newMid - spread/2;
    const askNaive = newMid + spread/2;
    
    const resPriceAS = newMid - (invAS * gamma * (sigma * sigma));
    const bidAS = resPriceAS - spread/2;
    const askAS = resPriceAS + spread/2;

    // Flujo de Órdenes (BEST EXECUTION)
    let buyProb = 0.5;
    if (trend > 0) buyProb = 0.8;
    if (trend < 0) buyProb = 0.2;
    
    const isBuyOrder = Math.random() < buyProb;
    
    if (isBuyOrder) { // Taker BUY (Hits ASK)
        if (askAS < askNaive) {
            setInvAS(q => q - 1); setCashAS(c => c + askAS);
        } else if (askNaive < askAS) {
            setInvNaive(q => q - 1); setCashNaive(c => c + askNaive);
        } else {
            setInvAS(q => q - 1); setCashAS(c => c + askAS);
            setInvNaive(q => q - 1); setCashNaive(c => c + askNaive);
        }
    } else { // Taker SELL (Hits BID)
        if (bidAS > bidNaive) {
            setInvAS(q => q + 1); setCashAS(c => c - bidAS);
        } else if (bidNaive > bidAS) {
            setInvNaive(q => q + 1); setCashNaive(c => c - bidNaive);
        } else {
            setInvAS(q => q + 1); setCashAS(c => c - bidAS);
            setInvNaive(q => q + 1); setCashNaive(c => c - bidNaive);
        }
    }

    const pnlNaive = cashNaive + (invNaive * newMid);
    const pnlAS = cashAS + (invAS * newMid);

    setMidPrice(newMid);

    setHistory(prev => {
        const newData = [...prev, {
            step: prev.length,
            MidPrice: newMid,
            ResPriceAS: resPriceAS,
            InvNaive: invNaive,
            InvAS: invAS,
            PnLNaive: pnlNaive,
            PnLAS: pnlAS
        }];
        if (newData.length > 100) newData.shift();
        return newData;
    });
  };

  useEffect(() => {
    if (isRunning) {
      intervalRef.current = setInterval(stepSimulation, 100);
    } else {
      clearInterval(intervalRef.current);
    }
    return () => clearInterval(intervalRef.current);
  }, [isRunning, midPrice, trend, gamma, invNaive, invAS]); 

  const resetSim = () => {
    setHistory([]);
    setMidPrice(100);
    setInvNaive(0); setCashNaive(0);
    setInvAS(0); setCashAS(0);
    setTrend(0);
  };

  return (
    <div className="flex flex-col h-full bg-black text-slate-300 p-4 gap-4 font-mono text-sm">
        <div className="flex justify-between items-center bg-slate-900 p-3 rounded border border-slate-800">
         <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <Scale className="text-blue-500" />
                MM<span className="text-blue-500">ARENA</span>
                <span className="text-xs text-slate-500 ml-2 font-normal">NAIVE VS AVELLANEDA-STOIKOV</span>
            </h2>
         </div>
         <div className="flex gap-4 items-center">
           <div className="flex items-center gap-2 bg-slate-800 px-3 py-1 rounded">
                <span className="text-[10px] text-slate-400">RISK AVERSION (γ)</span>
                <input 
                    type="range" min="0.1" max="2.0" step="0.1" 
                    value={gamma} onChange={(e) => setGamma(parseFloat(e.target.value))}
                    className="w-24 h-1 bg-blue-900 rounded-lg appearance-none cursor-pointer"
                />
                <span className="text-blue-400 font-bold">{gamma.toFixed(1)}</span>
           </div>
           <div className="h-6 w-px bg-slate-700"></div>
           <button onClick={() => setIsRunning(!isRunning)} className={`flex items-center gap-2 px-3 py-1 rounded text-xs font-bold ${isRunning ? 'bg-orange-600 text-white' : 'bg-green-600 text-white'}`}>
             {isRunning ? <><Pause size={12}/> PAUSE</> : <><Play size={12}/> SIMULATE</>}
           </button>
           <button onClick={resetSim} className="p-1 bg-slate-800 rounded hover:bg-slate-700 text-slate-400">
             <RefreshCw size={14}/>
           </button>
         </div>
       </div>

       <div className="flex-1 grid grid-cols-12 grid-rows-12 gap-4 min-h-0">
            {/* TOP CHART: PRICES */}
            <Card className="col-span-12 row-span-6 p-2 relative">
                <div className="absolute top-2 left-3 z-10 text-[10px] font-bold text-slate-500">MARKET PRICE VS RESERVATION PRICE</div>
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={history}>
                        <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" opacity={0.5} />
                        <YAxis domain={['auto', 'auto']} hide />
                        <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff' }} labelStyle={{ display: 'none' }} />
                        <Legend wrapperStyle={{ fontSize: '10px', top: 0 }} />
                        <Line type="monotone" dataKey="MidPrice" stroke="#64748b" strokeWidth={2} dot={false} name="Market Mid Price" isAnimationActive={false} />
                        <Line type="monotone" dataKey="ResPriceAS" stroke="#3b82f6" strokeWidth={2} dot={false} name="AS Reservation Price" isAnimationActive={false} />
                    </LineChart>
                </ResponsiveContainer>
            </Card>

            {/* BOTTOM LEFT: INVENTORY */}
            <Card className="col-span-6 row-span-6 p-2 relative">
                <div className="absolute top-2 left-3 z-10 text-[10px] font-bold text-slate-500">INVENTORY EXPOSURE (q)</div>
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={history}>
                        <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" opacity={0.5} />
                        {/* DOMAIN AUTO PARA VER EXPLOSION DE NAIVE */}
                        <YAxis domain={['auto', 'auto']} hide />
                        <ReferenceLine y={0} stroke="#475569" strokeDasharray="3 3" />
                        <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff' }} labelStyle={{ display: 'none' }} />
                        <Legend wrapperStyle={{ fontSize: '10px', top: 0 }} />
                        <Line type="monotone" dataKey="InvNaive" stroke="#ef4444" strokeWidth={2} dot={false} name="Naive Inventory" isAnimationActive={false} />
                        <Line type="monotone" dataKey="InvAS" stroke="#3b82f6" strokeWidth={2} dot={false} name="AS Inventory" isAnimationActive={false} />
                    </LineChart>
                </ResponsiveContainer>
            </Card>

            {/* BOTTOM RIGHT: PnL & CONTROLS */}
            <div className="col-span-6 row-span-6 flex flex-col gap-4">
                <Card className="flex-1 p-2 relative">
                    <div className="absolute top-2 left-3 z-10 text-[10px] font-bold text-slate-500">CUMULATIVE PnL</div>
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={history}>
                            <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" opacity={0.5} />
                            <YAxis hide />
                            <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff' }} labelStyle={{ display: 'none' }} />
                            <Legend wrapperStyle={{ fontSize: '10px', top: 0 }} />
                            <Line type="monotone" dataKey="PnLNaive" stroke="#ef4444" strokeWidth={2} dot={false} name="Naive PnL" isAnimationActive={false} />
                            <Line type="monotone" dataKey="PnLAS" stroke="#10b981" strokeWidth={2} dot={false} name="AS PnL" isAnimationActive={false} />
                        </LineChart>
                    </ResponsiveContainer>
                </Card>

                {/* TREND CONTROLS */}
                <Card className="h-16 flex items-center justify-between px-4 bg-slate-800/50">
                    <span className="text-[10px] font-bold text-slate-400">INJECT MARKET TREND</span>
                    <div className="flex gap-2">
                        <button 
                            onMouseDown={() => setTrend(-1)} onMouseUp={() => setTrend(0)} onMouseLeave={() => setTrend(0)}
                            className="px-4 py-2 bg-red-900/50 border border-red-700 hover:bg-red-800 text-red-200 rounded text-xs font-bold active:scale-95 transition-transform"
                        >
                            BEAR SHOCK
                        </button>
                        <button 
                            onMouseDown={() => setTrend(1)} onMouseUp={() => setTrend(0)} onMouseLeave={() => setTrend(0)}
                            className="px-4 py-2 bg-green-900/50 border border-green-700 hover:bg-green-800 text-green-200 rounded text-xs font-bold active:scale-95 transition-transform"
                        >
                            BULL SHOCK
                        </button>
                    </div>
                </Card>
            </div>
       </div>
    </div>
  );
};

// ----------------------------------------------------------------------
// SLIDE PORTADA: TÍTULO PRINCIPAL
// ----------------------------------------------------------------------
const TitleSlide = () => {
  const [particles, setParticles] = useState([]);
  
  useEffect(() => {
    // Generar partículas animadas
    const newParticles = Array.from({ length: 50 }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: Math.random() * 4 + 1,
      duration: Math.random() * 20 + 10,
      delay: Math.random() * 5
    }));
    setParticles(newParticles);
  }, []);

  return (
    <div className="relative flex flex-col items-center justify-center h-full bg-black overflow-hidden">
      {/* Fondo con gradiente animado */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-950 via-slate-900 to-black"></div>
      
      {/* Grid de fondo */}
      <div className="absolute inset-0 opacity-20" 
           style={{
             backgroundImage: 'linear-gradient(rgba(59, 130, 246, 0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(59, 130, 246, 0.1) 1px, transparent 1px)',
             backgroundSize: '50px 50px'
           }}>
      </div>
      
      {/* Círculos de fondo decorativos */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse"></div>
      <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
      <div className="absolute top-1/2 left-1/2 w-64 h-64 bg-cyan-500/5 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }}></div>
      
      {/* Partículas flotantes */}
      {particles.map((p) => (
        <div
          key={p.id}
          className="absolute rounded-full bg-blue-400/30"
          style={{
            left: `${p.x}%`,
            top: `${p.y}%`,
            width: `${p.size}px`,
            height: `${p.size}px`,
            animation: `float ${p.duration}s ease-in-out infinite`,
            animationDelay: `${p.delay}s`
          }}
        />
      ))}
      
      {/* Contenido principal */}
      <div className="relative z-10 text-center px-8">
        {/* Badge superior */}
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500/10 border border-blue-500/30 rounded-full mb-8 backdrop-blur-sm">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span className="text-blue-400 text-sm font-mono tracking-wider">ICAI • ALGORITHMIC TRADING</span>
        </div>
        
        {/* Título principal */}
        <h1 className="text-7xl md:text-8xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white via-blue-100 to-blue-300 mb-6 tracking-tight">
          Repaso de
        </h1>
        <h1 className="text-7xl md:text-9xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-cyan-400 to-purple-500 mb-8 tracking-tight">
          Práctica Final
        </h1>
        
        {/* Línea decorativa */}
        <div className="flex items-center justify-center gap-4 mb-10">
          <div className="h-px w-24 bg-gradient-to-r from-transparent to-blue-500"></div>
          <div className="flex gap-2">
            <TrendingUp className="text-blue-500" size={24} />
            <BarChart3 className="text-cyan-500" size={24} />
            <Cpu className="text-purple-500" size={24} />
          </div>
          <div className="h-px w-24 bg-gradient-to-l from-transparent to-purple-500"></div>
        </div>
        
        {/* Subtítulo */}
        <p className="text-xl md:text-2xl text-slate-400 font-light max-w-2xl mx-auto leading-relaxed">
          Microestructura de Mercados • Filtro de Kalman • Market Making
        </p>
        
        {/* Footer con instrucciones */}
        <div className="mt-16 flex items-center justify-center gap-3 text-slate-600">
          <ArrowLeft size={16} />
          <span className="text-sm font-mono">Usa las flechas para navegar</span>
          <ArrowRight size={16} />
        </div>
      </div>
      
      {/* Decoración inferior */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-blue-950/20 to-transparent"></div>
      
      {/* Estilos de animación */}
      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0) translateX(0); opacity: 0.3; }
          25% { transform: translateY(-20px) translateX(10px); opacity: 0.6; }
          50% { transform: translateY(-10px) translateX(-10px); opacity: 0.4; }
          75% { transform: translateY(-30px) translateX(5px); opacity: 0.5; }
        }
      `}</style>
    </div>
  );
};

// --- APP SHELL ---
const App = () => {
  const [currentSlide, setCurrentSlide] = useState(0);

  const slides = [
    { type: 'component', component: <TitleSlide /> },
    { type: 'component', component: <OrderBookSlide /> },
    { 
      type: 'insight', 
      title: "Microestructura: Key Takeaways", 
      subtitle: "Repaso conceptual post-simulación del Order Book",
      columns: [
        { 
            title: "Mecánica Visible", 
            icon: Layers, 
            colorBg: 'bg-blue-900', 
            colorText: 'text-blue-400',
            points: [
                { highlight: "Limit vs Market Orders", text: "El LOB (Limit Order Book) es una estructura pasiva construida por Limit Orders. Las Market Orders son la fuerza activa que consume esa liquidez." },
                { highlight: "Las Cartas sobre la Mesa", text: "Lo que ves en pantalla es solo la liquidez 'anunciada'. Es la información pública e inmediata, pero no la totalidad del mercado." }
            ] 
        },
        { 
            title: "La Entelequia del Precio", 
            icon: AlertTriangle, 
            colorBg: 'bg-yellow-900', 
            colorText: 'text-yellow-400',
            points: [
                { highlight: "Precio ≠ Determinista", text: "El 'precio real' no existe como un número fijo; es una variable latente y estocástica." },
                { highlight: "Solo existe Bid & Ask", text: "La única realidad tangible son las intenciones de compra (Bid) y venta (Ask). Los 'precios indicativos' son meras construcciones teóricas." }
            ] 
        },
        { 
            title: "La Realidad Oculta", 
            icon: Eye, 
            colorBg: 'bg-emerald-900', 
            colorText: 'text-emerald-400',
            points: [
                { highlight: "Asimetría de Información", text: "Los agentes operan con inventarios y posiciones ocultas que no se reflejan en el LOB." },
                { highlight: "El Negocio de la Incertidumbre", text: "En momentos de estrés, el precio se disloca del valor. Los Market Makers viven de gestionar este riesgo (spread) eficientemente." }
            ] 
        }
      ]
    },
    { type: 'component', component: <KalmanSlide /> },
    { 
      type: 'insight', 
      title: "El Filtro de Kalman: Key Takeaways", 
      subtitle: "Inferencias Bayesianas en tiempo real para descubrimiento de precios",
      columns: [
        { 
            title: "La Variable Latente", 
            icon: Target, 
            colorBg: 'bg-emerald-900', 
            colorText: 'text-emerald-400',
            points: [
                { highlight: "El Fantasma en la Máquina", text: "El 'Precio Verdadero' es un estado oculto que no podemos observar directamente. Solo tenemos acceso a mediciones imperfectas y ruidosas (Trades, Quotes)." },
                { highlight: "Incertidumbre Inherente", text: "Cualquier precio en pantalla es solo una aproximación probabilística del valor real del activo en ese instante." }
            ] 
        },
        { 
            title: "Actualización de Creencias", 
            icon: RefreshCw, 
            colorBg: 'bg-purple-900', 
            colorText: 'text-purple-400',
            points: [
                { highlight: "Lógica Bayesiana", text: "El algoritmo mezcla su 'Prior' (predicción basada en el pasado) con el 'Likelihood' (el nuevo dato recibido) para generar un 'Posterior' refinado." },
                { highlight: "Ganancia de Kalman (K)", text: "Es el índice de confianza dinámico. Si el dato es preciso (ej. alto volumen), K aumenta y el modelo se adapta rápido. Si es ruidoso, K baja y el modelo confía en su inercia." }
            ] 
        },
        { 
            title: "Señal entre el Ruido", 
            icon: Activity, 
            colorBg: 'bg-orange-900', 
            colorText: 'text-orange-400',
            points: [
                { highlight: "Filtrado de Microestructura", text: "El mercado está lleno de 'jitter' (ruido de alta frecuencia) que no representa valor. El filtro limpia este ruido para revelar la tendencia subyacente." },
                { highlight: "Estabilidad Operativa", text: "Permite a los algoritmos distinguir entre un cambio real de precio y una fluctuación irrelevante, evitando operaciones falsas." }
            ] 
        }
      ]
    },
    { type: 'component', component: <MarketMakingSlide /> },
    { 
      type: 'insight', 
      title: "Market Making: Key Takeaways", 
      subtitle: "Estrategias de Inventario y Realidad Institucional",
      columns: [
        { 
            title: "El Negocio de la Inmediatez", 
            icon: DollarSign, 
            colorBg: 'bg-blue-900', 
            colorText: 'text-blue-400',
            points: [
                { highlight: "Vendedores de Tiempo", text: "Los Market Makers proveen liquidez inmediata a los traders impacientes (Takers) a cambio del Spread. Su negocio no es predecir el futuro, sino gestionar el presente." },
                { highlight: "El Coste del Riesgo", text: "Mantener una orden en el libro implica un riesgo de selección adversa. El spread es la prima que cobran por asumir ese riesgo." }
            ] 
        },
        { 
            title: "Naive vs. Avellaneda-Stoikov", 
            icon: Cpu, 
            colorBg: 'bg-red-900', 
            colorText: 'text-red-400',
            points: [
                { highlight: "La Trampa de la Simetría", text: "Un Maker 'Naive' (ingenuo) cotiza simétricamente. En tendencias fuertes, acumula inventario tóxico y quiebra." },
                { highlight: "Gestión Dinámica (AS)", text: "El modelo Avellaneda-Stoikov ajusta sus precios (skewing) según su inventario. Si tiene mucho stock, baja precios para vender rápido, protegiendo su PnL." }
            ] 
        },
        { 
            title: "Los Gigantes del Mercado", 
            icon: Anchor, 
            colorBg: 'bg-indigo-900', 
            colorText: 'text-indigo-400',
            points: [
                { highlight: "No es para Individuos", text: "El Market Making moderno es un juego de HFTs e Instituciones masivas con latencias de nanosegundos." },
                { highlight: "La Mano Invisible", text: "Estos actores mueven el mercado basándose en sus necesidades de inventario y cobertura de riesgo, creando la liquidez que todos damos por sentada." }
            ] 
        }
      ]
    },
    // --- SLIDE: GITHUB ---
    { 
      type: 'insight', 
      title: "GitHub: Control de Versiones Colaborativo", 
      subtitle: "La columna vertebral del desarrollo moderno de software",
      columns: [
        { 
            title: "Adiós al Caos de Emails", 
            icon: GitBranch, 
            colorBg: 'bg-gray-800', 
            colorText: 'text-gray-300',
            points: [
                { highlight: "Repositorio Centralizado", text: "Todo el código vive en un solo lugar accesible para todo el equipo. No más 'v2_final_FINAL.zip' por email." },
                { highlight: "Historial Completo", text: "Cada cambio queda registrado con autor, fecha y descripción. Puedes ver exactamente quién hizo qué y cuándo." },
                { highlight: "Branches (Ramas)", text: "Cada desarrollador trabaja en su propia 'copia' sin afectar al código principal. Cuando está listo, se fusiona (merge)." }
            ] 
        },
        { 
            title: "Colaboración Sin Fricción", 
            icon: Users, 
            colorBg: 'bg-green-900', 
            colorText: 'text-green-400',
            points: [
                { highlight: "Pull Requests", text: "Propuestas de cambio que pueden ser revisadas, comentadas y aprobadas antes de integrarse. Code review profesional." },
                { highlight: "Resolución de Conflictos", text: "Si dos personas editan lo mismo, Git detecta el conflicto y te ayuda a resolverlo de forma ordenada." },
                { highlight: "Sincronización Instantánea", text: "Con comandos simples (git pull, git push) te traes los cambios de tus compañeros o subes los tuyos." }
            ] 
        },
        { 
            title: "Red de Seguridad", 
            icon: History, 
            colorBg: 'bg-blue-900', 
            colorText: 'text-blue-400',
            points: [
                { highlight: "Rollback Inmediato", text: "¿Algo se rompió? Con un comando vuelves a cualquier versión anterior. Es como un 'Ctrl+Z' infinito para todo el proyecto." },
                { highlight: "CI/CD Integrado", text: "GitHub Actions permite automatizar tests, builds y despliegues. Cada push puede validarse automáticamente." },
                { highlight: "Estándar de la Industria", text: "El 90% de empresas tech usan Git. Dominarlo es requisito mínimo para cualquier rol de desarrollo." }
            ] 
        }
      ]
    },
    // --- SLIDE: IDE CON MODO AGENTE ---
    { 
      type: 'insight', 
      title: "IDE con Modo Agente: Tu Ventaja Competitiva", 
      subtitle: "El salto de productividad más grande desde el autocompletado",
      columns: [
        { 
            title: "La Nueva Era del Desarrollo", 
            icon: Bot, 
            colorBg: 'bg-purple-900', 
            colorText: 'text-purple-400',
            points: [
                { highlight: "Programación Asistida por IA", text: "Un 'copiloto' inteligente que entiende tu código, sugiere soluciones y puede escribir funciones completas por ti." },
                { highlight: "Conversación Natural", text: "Describes lo que quieres en español/inglés y el agente genera el código. 'Crea una función que ordene este array por fecha'." },
                { highlight: "Contexto del Proyecto", text: "El agente lee tu codebase completo y entiende la arquitectura, dependencias y estilo de código existente." }
            ] 
        },
        { 
            title: "Los Mejores Modelos (2025)", 
            icon: Brain, 
            colorBg: 'bg-cyan-900', 
            colorText: 'text-cyan-400',
            points: [
                { highlight: "Claude Opus 4.5", text: "El más potente de Anthropic. Excelente razonamiento, código limpio y capacidad de manejar proyectos complejos." },
                { highlight: "Gemini 3.0 Pro", text: "De Google. Ventana de contexto masiva (1M tokens), ideal para analizar codebases grandes de un vistazo." },
                { highlight: "OpenAI 5.1 / Codex", text: "Modelos especializados en código con capacidad de razonamiento paso a paso ('chain of thought')." }
            ] 
        },
        { 
            title: "Tu Edge en el Mercado Laboral", 
            icon: Rocket, 
            colorBg: 'bg-orange-900', 
            colorText: 'text-orange-400',
            points: [
                { highlight: "10x Developer", text: "La gente en el mercado laboral aún programa 'a mano'. Vosotros entráis con un multiplicador de productividad brutal." },
                { highlight: "Aprender Más Rápido", text: "El agente explica código, sugiere mejoras y te enseña buenas prácticas en tiempo real. Es un tutor 24/7." },
                { highlight: "El Futuro es Ahora", text: "En 2-3 años esto será estándar. Los que lo dominen ahora liderarán equipos. Los que no, se quedarán atrás." }
            ] 
        }
      ]
    },
    // --- SLIDE: REPASO PRÁCTICA FINAL ---
    { 
      type: 'insight', 
      title: "Requisitos para Superar la Práctica", 
      subtitle: "La práctica será APROBADA si se cumplen TODOS los siguientes requisitos",
      columns: [
        { 
            title: "Control de Versiones & Código", 
            icon: GitBranch, 
            colorBg: 'bg-gray-800', 
            colorText: 'text-gray-300',
            points: [
                { highlight: "Utilizar GitHub", text: "El proyecto debe estar versionado en un repositorio de GitHub. Commits claros y descriptivos. Historial de cambios visible." },
                { highlight: "Programación Orientada a Objetos (OOP)", text: "Uso obligatorio de clases, herencia, encapsulación. Código modular y reutilizable. Separación clara de responsabilidades." }
            ] 
        },
        { 
            title: "Seguridad y Conexión API", 
            icon: Key, 
            colorBg: 'bg-amber-900', 
            colorText: 'text-amber-400',
            points: [
                { highlight: "Claves Públicas y Privadas", text: "Demostrar entendimiento de cómo funcionan las API keys. Diferencia entre clave pública (identificación) y privada (autenticación/firma)." },
                { highlight: "Gestión Segura", text: "Las claves NUNCA se suben a GitHub. Uso de variables de entorno (.env). Entender riesgos de exposición de credenciales." }
            ] 
        },
        { 
            title: "Algoritmo de Trading Funcional", 
            icon: PlayCircle, 
            colorBg: 'bg-green-900', 
            colorText: 'text-green-400',
            points: [
                { highlight: "Trading en VIVO", text: "El algoritmo debe ejecutarse en tiempo real conectado a un exchange (paper trading o real). No simulaciones locales." },
                { highlight: "Demostración Funcional", text: "Evidencia clara de que el bot opera: logs de órdenes, capturas de trades ejecutados, o demo en vivo durante la evaluación." }
            ] 
        }
      ]
    }
  ];

  const nextSlide = () => setCurrentSlide(prev => Math.min(prev + 1, slides.length - 1));
  const prevSlide = () => setCurrentSlide(prev => Math.max(prev - 1, 0));

  // Key press navigation
  useEffect(() => {
      const handleKeyDown = (e) => {
          if (e.key === 'ArrowRight') nextSlide();
          if (e.key === 'ArrowLeft') prevSlide();
      };
      window.addEventListener('keydown', handleKeyDown);
      return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <div className="w-full h-screen bg-black flex flex-col overflow-hidden font-sans">
        <div className="flex-1 w-full relative">
            <div className="absolute inset-0 p-4">
                {slides[currentSlide].type === 'component' ? (
                    slides[currentSlide].component
                ) : (
                    <RecapSlide {...slides[currentSlide]} />
                )}
            </div>
        </div>

        <div className="h-12 bg-slate-900 border-t border-slate-800 flex items-center justify-between px-6 z-50">
            <div className="text-xs text-slate-500 font-mono">SESSION: {generateId().toUpperCase()}</div>
            <div className="flex items-center gap-4">
                <button onClick={prevSlide} disabled={currentSlide === 0} className={`p-1 rounded hover:bg-slate-800 ${currentSlide === 0 ? 'text-slate-700' : 'text-blue-500'}`}>
                    <ArrowLeft size={16} />
                </button>
                
                <div className="flex gap-1">
                    {slides.map((_, idx) => (
                        <div 
                            key={idx} 
                            className={`h-1.5 w-1.5 rounded-full transition-all duration-300 ${currentSlide === idx ? 'bg-blue-500 w-3' : 'bg-slate-700'}`}
                        ></div>
                    ))}
                </div>

                <button onClick={nextSlide} disabled={currentSlide === slides.length - 1} className={`p-1 rounded hover:bg-slate-800 ${currentSlide === slides.length - 1 ? 'text-slate-700' : 'text-blue-500'}`}>
                    <ArrowRight size={16} />
                </button>
            </div>
            <div className="text-xs text-slate-500 font-mono">SLIDE {currentSlide + 1}/{slides.length}</div>
        </div>
    </div>
  );
};

export default App;