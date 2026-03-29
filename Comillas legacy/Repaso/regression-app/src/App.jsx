import React, { useState, useEffect } from 'react';
import { AppLayout } from './components/layout/AppLayout';
import IntuitionSlide from './slides/IntuitionSlide';
import ErrorSlide from './slides/ErrorSlide';
import GradientSlide from './slides/GradientSlide';
import MathSlide from './slides/MathSlide';

function App() {
    const [currentStep, setCurrentStep] = useState(0);

    const slides = [
        { component: <IntuitionSlide />, title: "FASE 1: INTUICIÓN" },
        { component: <ErrorSlide />, title: "FASE 2: EL ERROR" },
        { component: <GradientSlide />, title: "FASE 3: OPTIMIZACIÓN" },
        { component: <MathSlide />, title: "FASE 4: FORMALIZACIÓN" }
    ];

    const nextStep = () => setCurrentStep(p => Math.min(p + 1, slides.length - 1));
    const prevStep = () => setCurrentStep(p => Math.max(p - 1, 0));

    // Keyboard navigation
    useEffect(() => {
        const handleKeyDown = (e) => {
            if (e.key === 'ArrowRight') nextStep();
            if (e.key === 'ArrowLeft') prevStep();
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, []);

    return (
        <AppLayout
            title={slides[currentStep].title}
            currentStep={currentStep}
            totalSteps={slides.length}
            onNext={nextStep}
            onPrev={prevStep}
        >
            <div className="h-full w-full animate-fade-in key={currentStep}">
                {slides[currentStep].component}
            </div>
        </AppLayout>
    );
}

export default App;
