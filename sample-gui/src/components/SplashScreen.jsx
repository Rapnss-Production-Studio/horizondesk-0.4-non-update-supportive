import React, { useRef, useEffect, useState } from 'react';

const SplashScreen = ({ onFinish }) => {
    const videoRef = useRef(null);
    const [opacity, setOpacity] = useState(1);

    useEffect(() => {
        // Check if seen before
        const hasSeen = localStorage.getItem('hasSeenIntro');
        if (hasSeen) {
            onFinish();
            return;
        }

        // Play video
        if (videoRef.current) {
            videoRef.current.play().catch(e => console.error("Autoplay failed", e));
        }
    }, []);

    const handleVideoEnd = () => {
        setOpacity(0);
        setTimeout(() => {
            localStorage.setItem('hasSeenIntro', 'true');
            onFinish();
        }, 1000); // Fade out duration
    };

    const handleSkip = () => {
        handleVideoEnd();
    };

    return (
        <div style={{
            position: 'relative',
            width: '100%',
            height: '100%',
            backgroundColor: 'var(--bg-app)', // Matches Home.jsx
            color: 'var(--text-main)',
            fontFamily: 'var(--font-sans)',
            zIndex: 10,
            opacity: opacity,
            transition: 'opacity 1s ease-out',
            display: opacity <= 0 ? 'none' : 'flex',
            justifyContent: 'center',
            alignItems: 'center'
        }}>
            <video
                ref={videoRef}
                src="./assets/intro.mp4"
                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                onEnded={handleVideoEnd}
                muted // Muted often required for autoplay, but desktop apps handles sound fine usually
            />
            <button
                onClick={handleSkip}
                style={{
                    position: 'absolute',
                    bottom: '20px',
                    right: '20px',
                    color: 'white',
                    background: 'rgba(0,0,0,0.5)',
                    padding: '8px 16px',
                    borderRadius: '4px',
                    border: '1px solid rgba(255,255,255,0.3)',
                    cursor: 'pointer'
                }}
            >
                Skip Intro
            </button>
        </div>
    );
};

export default SplashScreen;
