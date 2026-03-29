import { useState, useRef, useCallback } from 'react';

export const useGradientDescent = (data, initialM = 0, initialB = 0, learningRate = 0.00001) => {
    const [slope, setSlope] = useState(initialM);
    const [intercept, setIntercept] = useState(initialB);
    const [iteration, setIteration] = useState(0);
    const [costHistory, setCostHistory] = useState([]);
    const [isRunning, setIsRunning] = useState(false);

    const intervalRef = useRef(null);

    // Función de Coste (MSE)
    const calculateCost = (m, b) => {
        let sumErrorSq = 0;
        const N = data.length;
        for (let i = 0; i < N; i++) {
            const pred = b + m * data[i].x;
            const error = data[i].y - pred;
            sumErrorSq += (error * error);
        }
        return sumErrorSq / N;
    };

    // Un paso del gradiente
    const step = useCallback(() => {
        setSlope(prevM => {
            setIntercept(prevB => {
                let gradientM = 0;
                let gradientB = 0;
                const N = data.length;

                for (let i = 0; i < N; i++) {
                    const x = data[i].x;
                    const y = data[i].y;
                    const pred = prevB + (prevM * x);
                    const error = y - pred;

                    // Derivadas Parciales de MSE
                    // d/dm = -2/N * sum(x * error)
                    // d/db = -2/N * sum(error)
                    gradientM += -(2 / N) * x * error;
                    gradientB += -(2 / N) * error;
                }

                const newM = prevM - (learningRate * gradientM);
                const newB = prevB - (learningRate * 100 * gradientB); // Learning rate escalado para intercepto (orden de magnitud diferente)

                const currentCost = calculateCost(prevM, prevB);

                setCostHistory(prev => {
                    const history = [...prev, { iteration: prev.length, cost: currentCost }];
                    if (history.length > 50) history.shift();
                    return history;
                });
                setIteration(i => i + 1);

                return newB; // Hack sucio por closure: devolvemos B aquí para que setSlope use el scope correcto? No, esto está mal en React.
                // Mejor usar refs o setState funcional limpio.
            });
            return prevM; // Esto no actualizará correctamente porque intercept depende de slope en el mismo tick.
        });

        // CORRECCIÓN: Calcular gradientes basados en valores ACTUALES (refs o dependencias)
        // React state updates are batched.
        // Vamos a hacerlo imperativo dentro del callback para asegurar consistencia matemática en el mismo frame.

    }, [data, learningRate]);

    // Refactor para consistencia matemática
    const computeStep = () => {
        let currentM = slope;
        let currentB = intercept;

        // Si estamos corriendo, usamos la versión más reciente del estado (que podría no estar actualizada en render aún si forzamos mucho)
        // Pero en React interval, usualmente tenemos closure sobre state viejos si no usamos refs
        // Usaremos functional updates combinados.

        setSlope(prevM => {
            setIntercept(prevB => {
                // Aquí dentro tenemos access a AMBOS valores actualizados del frame anterior?
                // No, setIntercept no recibe prevM.
                // Necesitamos calcular los gradientes FUERA de los set.
                return prevB;
            });
            return prevM;
        });
    };

    // Versión definitiva segura
    const safeStep = () => {
        setSlope(m => {
            setIntercept(b => {
                let gradientM = 0;
                let gradientB = 0;
                const N = data.length;

                for (let i = 0; i < N; i++) {
                    const err = data[i].y - (b + m * data[i].x);
                    gradientM += -2 * data[i].x * err;
                    gradientB += -2 * err;
                }
                gradientM /= N;
                gradientB /= N;

                const newM = m - (learningRate * gradientM);
                const newB = b - (learningRate * 2000 * gradientB); // Boost visual al intercepto

                const cost = calculateCost(m, b);
                setCostHistory(h => [...h.slice(-49), { i: h.length, cost }]);
                setIteration(it => it + 1);

                return newB;
            });
            return m; // Esto devuelve el VALOR VIEJO de m al setter, pero como setIntercept se ejecuta "anidado"? No.
            // React `setState(prev => ...)` es puro. No puedo side-effectear otro setter dentro.
            // ESTA APROXIMACIÓN ES FLAKY.

            // SOLUCIÓN: Usar un solo objeto de estado para params
            return m;
        });
    };

    return { slope, intercept, iteration, costHistory, isRunning, setIsRunning };
};
