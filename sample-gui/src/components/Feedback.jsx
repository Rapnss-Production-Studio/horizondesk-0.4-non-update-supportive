import React, { useEffect } from 'react';

const Feedback = ({ user }) => {
    useEffect(() => {
        // Load the Typeform embed script dynamically with explicit https
        const script = document.createElement('script');
        script.src = 'https://embed.typeform.com/next/embed.js';
        script.async = true;
        document.body.appendChild(script);

        return () => {
            if (document.body.contains(script)) {
                document.body.removeChild(script);
            }
        };
    }, []);

    return (
        <div style={{ padding: '0px 20px 40px 20px', maxWidth: '1000px', margin: '0 auto', height: 'calc(100vh - 120px)', minHeight: '600px' }}>
            <div 
                data-tf-live="01KKH7YJX0KHKTN8MD3ZHN696E" 
                style={{ width: '100%', height: '100%', border: 'none', borderRadius: '16px', overflow: 'hidden', background: 'var(--bg-panel)' }}
            ></div>
        </div>
    );
};

export default Feedback;
