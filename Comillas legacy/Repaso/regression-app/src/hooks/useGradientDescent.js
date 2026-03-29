import { useState, useRef, useEffect, useCallback } from 'react';

export const useGradientDescent = (data, initialM = 0, initialB = 0, learningRate = 0.000001) => {
    const [params, setParams] = useState({ m: initialM, b: initialB });
    const [iteration, setIteration] = useState(0);
    const [costHistory, setCostHistory] = useState([]);
    const [isRunning, setIsRunning] = useState(false);
    const requestRef = useRef();

    const calculateCost = (m, b) => {
        let sumErrorSq = 0;
        for (let i = 0; i < data.length; i++) {
            const error = data[i].y - (b + m * data[i].x);
            sumErrorSq += error * error;
        }
        return sumErrorSq / data.length;
    };

    const step = useCallback(() => {
        setParams(prev => {
            let gradM = 0;
            let gradB = 0;
            const N = data.length;

            for (let i = 0; i < N; i++) {
                const x = data[i].x;
                const y = data[i].y;
                const pred = prev.b + (prev.m * x);
                const error = y - pred;

                // Derivadas (MSE)
                // dJ/dm = -2/N * sum(x * error)
                // dJ/db = -2/N * sum(error)
                gradM += -2 * x * error;
                gradB += -2 * error;
            }

            gradM /= N;
            gradB /= N;

            // Ajuste de Learning Rates (Heurística para datos no normalizados)
            // x ~ 100, entonces gradM es ~100 veces mayor que gradB
            // Necesitamos AlphaM mucho mas pequeño que AlphaB?
            // O al reves? 
            // Si Alpha es fijo, gradM oscilará. 
            // Vamos a usar un lr pequeño y boostear B.
            const newM = prev.m - (learningRate * gradM);
            const newB = prev.b - (learningRate * 2500 * gradB);

            const cost = calculateCost(newM, newB);

            // Efecto secundario en render (ok en eventos, cuidado en concurrent mode)
            // Lo ideal sería un useEffect que escuche cambios de params, pero para animación rapida esto vale.
            setCostHistory(h => {
                const newHist = [...h, { i: h.length, cost }];
                if (newHist.length > 100) return newHist.slice(-100);
                return newHist;
            });
            setIteration(i => i + 1);

            return { m: newM, b: newB };
        });
    }, [data, learningRate]);

    const animate = useCallback(() => {
        step();
        requestRef.current = requestAnimationFrame(animate);
    }, [step]);

    useEffect(() => {
        if (isRunning) {
            requestRef.current = requestAnimationFrame(animate);
        } else {
            cancelAnimationFrame(requestRef.current);
        }
        return () => cancelAnimationFrame(requestRef.current);
    }, [isRunning, animate]);

    const reset = () => {
        setParams({ m: initialM, b: initialB });
        setIteration(0);
        setCostHistory([]);
        setIsRunning(false);
    };

    return {
        slope: params.m,
        intercept: params.b,
        iteration,
        costHistory,
        isRunning,
        setIsRunning,
        step,
        reset
    };
};
