import React, { useState, useEffect } from 'react';
import { Check, Zap, Users, GraduationCap, Briefcase } from 'lucide-react';

const Plans = () => {
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        alert("DEBUG: Plans Component Mounted");
        console.log("Plans mounted");
        console.log("window.pywebview:", window.pywebview);
    }, []);

    const handlePayment = (amount) => {
        alert("DEBUG: handlePayment called");
        setLoading(true);
        console.log("Initiating payment...");
        if (window.pywebview?.api) {
            console.log("Calling backend create_payment...");
            window.pywebview.api.create_payment(amount, "inr").then((res) => {
                setLoading(false);
                console.log("Backend response:", res);
                if (res.success) {
                    console.log("Payment Invoice Opened:", res.url);
                    alert("Payment Page Opened in Browser!");
                } else {
                    alert("Backend Error: " + (res.error || "Unknown error"));
                }
            }).catch(err => {
                setLoading(false);
                alert("Bridge Error: " + err);
            });
        } else {
            alert("Error: pywebview API not found. Is the Python backend running?");
            setLoading(false);
        }
    };

    const tiers = [
        {
            name: "Free",
            price: "₹0",
            period: "Lifetime",
            features: ["25k tokens/day", "1 Active Agent", "Light Usage"],
            icon: Zap,
            cta: "Current Plan",
            disabled: true
        },
        {
            name: "Lite",
            price: "₹199",
            period: "/month",
            features: ["100k tokens/month", "1 Active Agent", "3 Projects", "Community Support"],
            icon: Users, // Placeholder
            cta: "Upgrade"
        },
        {
            name: "Student",
            price: "₹99",
            period: "/month",
            features: ["200k tokens/month", "2 Active Agents", "Edu Resources", "Verification Req."],
            icon: GraduationCap,
            cta: "Verify & Upgrade"
        },
        {
            name: "Solo Founder",
            price: "₹999",
            period: "/month",
            features: ["1M tokens/month", "10 Active Agents", "Analytics", "Priority Support"],
            icon: Briefcase,
            cta: "Upgrade",
            highlight: true
        },
        {
            name: "Corporate",
            price: "₹14,999",
            period: "/month",
            features: ["10M tokens/month", "Unlim. Agents", "SSO & Security", "Dedicated Manager"],
            icon: Users,
            cta: loading ? "Processing..." : "Start 1-Year Trial (₹2 verification)",
            action: () => handlePayment(2) // ₹2 verification
        }
    ];

    return (
        <div style={{ paddingBottom: '40px' }}>
            <div style={{ textAlign: 'center', marginBottom: '40px' }}>
                <h1 style={{ fontSize: '2.5rem', marginBottom: '10px' }}>Choose Your Plan</h1>
                <p style={{ color: 'var(--text-secondary)' }}>Powerful AI agents for every stage of your journey. <br /> Secure Crypto Payments via NowPayments.</p>
            </div>

            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
                gap: '20px',
                alignItems: 'start'
            }}>
                {tiers.map((tier, index) => {
                    const Icon = tier.icon;
                    return (
                        <div key={index} style={{
                            backgroundColor: 'var(--bg-panel)',
                            border: tier.highlight ? '2px solid var(--accent)' : '1px solid var(--border-subtle)',
                            borderRadius: '12px',
                            padding: '24px',
                            position: 'relative',
                            boxShadow: tier.highlight ? '0 8px 30px rgba(0,0,0,0.12)' : '0 1px 3px rgba(0,0,0,0.05)'
                        }}>
                            {tier.highlight && <div style={{
                                position: 'absolute', top: '-12px', left: '50%', transform: 'translateX(-50%)',
                                backgroundColor: 'var(--accent)', color: 'white', fontSize: '12px', fontWeight: 'bold',
                                padding: '4px 12px', borderRadius: '20px'
                            }}>MOST POPULAR</div>}

                            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
                                <div style={{
                                    width: '40px', height: '40px', borderRadius: '8px',
                                    background: 'var(--bg-app)', display: 'flex', alignItems: 'center', justifyContent: 'center',
                                    color: 'var(--accent)'
                                }}>
                                    <Icon size={20} />
                                </div>
                                <h3 style={{ margin: 0 }}>{tier.name}</h3>
                            </div>

                            <div style={{ marginBottom: '24px' }}>
                                <span style={{ fontSize: '2rem', fontWeight: 'bold' }}>{tier.price}</span>
                                <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>{tier.period}</span>
                            </div>

                            <ul style={{ listStyle: 'none', marginBottom: '24px' }}>
                                {tier.features.map((feat, i) => (
                                    <li key={i} style={{ display: 'flex', gap: '8px', marginBottom: '12px', fontSize: '14px', color: 'var(--text-secondary)' }}>
                                        <Check size={16} color="var(--accent)" /> {feat}
                                    </li>
                                ))}
                            </ul>

                            <button
                                onClick={tier.action}
                                disabled={tier.disabled || loading}
                                style={{
                                    width: '100%',
                                    padding: '12px',
                                    borderRadius: '8px',
                                    fontWeight: '600',
                                    backgroundColor: tier.highlight || tier.name === 'Corporate' ? 'var(--accent)' : 'var(--bg-app)',
                                    color: tier.highlight || tier.name === 'Corporate' ? 'white' : 'var(--text-main)',
                                    border: 'none',
                                    cursor: tier.disabled ? 'default' : 'pointer',
                                    opacity: tier.disabled || loading ? 0.6 : 1,
                                    transition: 'all 0.2s'
                                }}
                            >
                                {tier.cta}
                            </button>
                        </div>
                    )
                })}
            </div>
        </div>
    );
};

export default Plans;
