import { useState, useMemo } from 'react';

export const useRegressionData = (count = 20) => {
    // Generamos datos estáticos (memoizados) para que no bailen en cada render
    const data = useMemo(() => {
        const points = [];
        // Modelo Real (Ground Truth): Precio = 50k + 2.5k * m2
        const trueSlope = 2.5;
        const trueIntercept = 50;

        for (let i = 0; i < count; i++) {
            // Area entre 50 y 200 m2
            const x = Math.floor(Math.random() * (150)) + 50;

            // Ruido aleatorio (algunos pisos son más caros/baratos de lo normal)
            const noise = (Math.random() - 0.5) * 100; // +/- 50k

            const y = trueIntercept + (x * trueSlope) + noise;

            points.push({
                id: i,
                x: x,      // Metros Cuadrados
                y: y,      // Precio (en Miles de Euros)
                trueY: trueIntercept + (x * trueSlope) // Para comparar
            });
        }
        return points.sort((a, b) => a.x - b.x);
    }, [count]);

    return { data };
};
