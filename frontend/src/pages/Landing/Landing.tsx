import React from 'react';
import { Link } from 'react-router-dom';
import {
    Zap,
    ShieldCheck,
    BarChart3,
    Globe,
    ArrowRight,
    TrendingUp,
    Search,
    PieChart
} from 'lucide-react';
import { motion } from 'framer-motion';

const Landing: React.FC = () => {
    return (
        <div className="overflow-hidden">
            {/* Hero Section */}
            <section className="relative pt-20 pb-32 mb-12">
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full -z-10 pointer-events-none">
                    <div className="absolute top-[-10%] right-[-10%] w-[40%] h-[40%] bg-primary-200/20 blur-[120px] rounded-full" />
                    <div className="absolute bottom-[-10%] left-[-10%] w-[40%] h-[40%] bg-emerald-200/20 blur-[120px] rounded-full" />
                </div>

                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                        <motion.div
                            initial={{ opacity: 0, x: -50 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.8 }}
                        >
                            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-primary-50 border border-primary-100 text-primary-600 text-sm font-medium mb-6">
                                <span className="relative flex h-2 w-2">
                                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary-400 opacity-75"></span>
                                    <span className="relative inline-flex rounded-full h-2 w-2 bg-primary-500"></span>
                                </span>
                                <span>Powering SME Growth with AI</span>
                            </div>

                            <h1 className="text-5xl lg:text-7xl font-extrabold text-slate-900 leading-[1.1] mb-6">
                                Revolutionize Your <br />
                                <span className="bg-clip-text text-transparent bg-gradient-to-r from-primary-600 to-indigo-600">
                                    Financial Health
                                </span>
                            </h1>

                            <p className="text-xl text-slate-600 mb-10 max-w-lg leading-relaxed">
                                Empower your SME with AI-driven financial analysis, credit scoring, and actionable insights to drive sustainable growth.
                            </p>

                            <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4">
                                <Link to="/register" className="btn-primary py-4 px-8 text-lg flex items-center justify-center">
                                    Start Analysis Free <ArrowRight className="ml-2 w-5 h-5" />
                                </Link>
                                <Link to="/about" className="btn-secondary py-4 px-8 text-lg flex items-center justify-center">
                                    Learn How it Works
                                </Link>
                            </div>

                            <div className="mt-10 flex items-center space-x-8 text-slate-400">
                                <div className="flex flex-col">
                                    <span className="text-2xl font-bold text-slate-800">500+</span>
                                    <span className="text-sm">SMEs Empowered</span>
                                </div>
                                <div className="h-8 w-px bg-slate-200" />
                                <div className="flex flex-col">
                                    <span className="text-2xl font-bold text-slate-800">₹10Cr+</span>
                                    <span className="text-sm">Loans Unlocked</span>
                                </div>
                                <div className="h-8 w-px bg-slate-200" />
                                <div className="flex flex-col">
                                    <span className="text-2xl font-bold text-slate-800">98%</span>
                                    <span className="text-sm">Accuracy Rate</span>
                                </div>
                            </div>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, scale: 0.8 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ duration: 1, delay: 0.2 }}
                            className="relative"
                        >
                            <div className="relative z-10 glass-card p-2 transform rotate-1 hover:rotate-0 transition-transform duration-500">
                                <img
                                    src="https://w7.pngwing.com/pngs/576/642/png-transparent-data-analysis-analytics-management-big-data-data-processing-business-template-text-people.png"
                                    alt="Financial Dashboard Preview"
                                    className="rounded-xl shadow-2xl w-full h-auto"
                                />
                            </div>
                            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[120%] h-[120%] bg-gradient-to-tr from-primary-500/10 to-indigo-500/10 rounded-full blur-[80px] -z-10" />

                            {/* Floating elements */}
                            <div className="absolute -top-6 -right-6 glass-panel p-4 rounded-2xl shadow-xl animate-bounce delay-700">
                                <TrendingUp className="text-emerald-500 w-8 h-8" />
                            </div>
                            <div className="absolute -bottom-10 -left-6 glass-panel p-4 rounded-2xl shadow-xl animate-pulse">
                                <PieChart className="text-primary-500 w-8 h-8" />
                            </div>
                        </motion.div>
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section className="py-24 bg-white/50 relative">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center mb-20">
                        <h2 className="text-sm font-bold text-primary-600 uppercase tracking-wider mb-3">Core Capabilities</h2>
                        <h3 className="text-4xl font-bold text-slate-900 font-display">Designed for Modern Business Owners</h3>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                        <FeatureCard
                            icon={<Zap className="w-6 h-6" />}
                            title="Real-time Analysis"
                            description="Get instant insights from your financial statements with our advanced AI processing engine."
                        />
                        <FeatureCard
                            icon={<BarChart3 className="w-6 h-6" />}
                            title="Predictive Ratios"
                            description="Monitor 20+ key performance indicators to forecast your financial trajectory."
                        />
                        <FeatureCard
                            icon={<ShieldCheck className="w-6 h-6" />}
                            title="Credit Readiness"
                            description="Understand how lenders view your business and get tips to improve your score."
                        />
                        <FeatureCard
                            icon={<Globe className="w-6 h-6" />}
                            title="Multi-lingual Support"
                            description="Access your dashboard in English or Hindi, with more regional languages coming soon."
                        />
                    </div>
                </div>
            </section>
        </div>
    );
};

const FeatureCard: React.FC<{ icon: React.ReactNode; title: string; description: string }> = ({ icon, title, description }) => (
    <div className="glass-card p-8 group hover:-translate-y-2 transition-all duration-300">
        <div className="w-12 h-12 bg-primary-100 text-primary-600 rounded-xl flex items-center justify-center mb-6 group-hover:bg-primary-600 group-hover:text-white transition-colors duration-300">
            {icon}
        </div>
        <h4 className="text-xl font-bold text-slate-900 mb-3">{title}</h4>
        <p className="text-slate-600 leading-relaxed">{description}</p>
    </div>
);

export default Landing;
