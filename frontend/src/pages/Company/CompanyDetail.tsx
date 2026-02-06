import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
    Building2,
    FileUp,
    BarChart3,
    Activity,
    TrendingUp,
    ShieldCheck,
    ArrowLeft,
    Calendar,
    Globe,
    Loader2,
    AlertCircle
} from 'lucide-react';
import { motion } from 'framer-motion';
import apiClient from '../../api/client';
import { Company, HealthScore } from '../../types';
import ChatInterface from '../../components/analysis/ChatInterface';

const CompanyDetail: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const [company, setCompany] = useState<Company | null>(null);
    const [healthScore, setHealthScore] = useState<HealthScore | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                const [compRes, healthRes] = await Promise.all([
                    apiClient.get(`/companies/${id}`),
                    apiClient.get(`/analysis/${id}/health-score`)
                ]);
                setCompany(compRes.data);
                setHealthScore(healthRes.data);
            } catch (err: any) {
                if (err.response?.status === 400 && err.response?.data?.detail.includes('statements required')) {
                    setCompany(err.response.data.company_data || null); // Note: Backend might not return company data in error
                    // If 400 due to no statements, we still want to show the company info at least
                    try {
                        const compRes = await apiClient.get(`/companies/${id}`);
                        setCompany(compRes.data);
                    } catch (e) { }
                } else {
                    setError('Failed to fetch company data. Please ensure you have uploaded financial statements.');
                }
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [id]);

    if (loading) {
        return (
            <div className="max-w-7xl mx-auto px-4 py-12 flex items-center justify-center min-h-[60vh]">
                <Loader2 className="w-10 h-10 text-primary-600 animate-spin" />
            </div>
        );
    }

    if (!company) {
        return (
            <div className="max-w-7xl mx-auto px-4 py-12 text-center">
                <h2 className="text-2xl font-bold text-slate-900">Company not found</h2>
                <Link to="/companies" className="text-primary-600 mt-4 inline-block font-bold">Back to Companies</Link>
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
            <Link to="/companies" className="inline-flex items-center text-slate-500 hover:text-primary-600 font-medium mb-8 transition-colors">
                <ArrowLeft size={18} className="mr-2" /> Back to All Companies
            </Link>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left Column - Info and Actions */}
                <div className="lg:col-span-1 space-y-6">
                    <div className="glass-panel p-8 rounded-3xl border border-white/40 shadow-xl">
                        <div className="flex items-center space-x-4 mb-6">
                            <div className="w-16 h-16 bg-primary-600 rounded-2xl flex items-center justify-center text-white text-2xl font-bold shadow-lg shadow-primary-500/30">
                                {company.name[0].toUpperCase()}
                            </div>
                            <div>
                                <h1 className="text-2xl font-bold text-slate-900 leading-tight">{company.name}</h1>
                                <p className="text-slate-500 text-sm flex items-center">
                                    <Activity size={14} className="mr-1 text-emerald-500" /> Active Profile
                                </p>
                            </div>
                        </div>

                        <div className="space-y-4 mb-8">
                            <InfoItem icon={<Building2 size={18} />} label="Industry" value={company.industry} />
                            <InfoItem icon={<Calendar size={18} />} label="Founded" value={company.founded_date ? new Date(company.founded_date).getFullYear().toString() : 'N/A'} />
                            <InfoItem icon={<Globe size={18} />} label="Website" value={company.website || 'Not specified'} isLink />
                        </div>

                        <div className="grid grid-cols-1 gap-3">
                            <Link to={`/upload/${company.id}`} className="btn-primary flex items-center justify-center py-3">
                                <FileUp size={18} className="mr-2" /> Upload Financials
                            </Link>
                            <button className="btn-secondary flex items-center justify-center py-3">
                                Edit Profile
                            </button>
                        </div>
                    </div>

                    {/* AI Insights Summary Card */}
                    {healthScore?.ai_insights && (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="bg-gradient-to-br from-indigo-600 to-violet-700 text-white p-8 rounded-3xl shadow-xl shadow-indigo-500/20 relative overflow-hidden"
                        >
                            <div className="absolute top-0 right-0 p-4 opacity-10">
                                <ShieldCheck size={120} />
                            </div>
                            <h3 className="text-xl font-bold mb-4 flex items-center">
                                <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center mr-3">
                                    <BarChart3 size={20} />
                                </div>
                                AI Deep Analysis
                            </h3>
                            <div className="prose prose-invert prose-sm">
                                <p className="text-indigo-50 leading-relaxed line-clamp-6 mb-6">
                                    {healthScore.ai_insights}
                                </p>
                            </div>
                            <div className="space-y-3">
                                <button
                                    onClick={() => alert('Full report view coming soon!')}
                                    className="w-full py-3 bg-white text-indigo-600 font-bold rounded-xl hover:bg-indigo-50 transition-all flex items-center justify-center"
                                >
                                    Full Analysis View
                                </button>
                                <button
                                    onClick={async () => {
                                        try {
                                            const res = await apiClient.get(`/analysis/${id}/report`);
                                            alert("Report generated successfully! Scroll down to see it (mockup for now)");
                                        } catch (e) {
                                            alert("Failed to generate report. Checks logs.");
                                        }
                                    }}
                                    className="w-full py-3 bg-indigo-500/30 text-white border border-indigo-400/30 font-bold rounded-xl hover:bg-indigo-500/40 transition-all"
                                >
                                    Generate Investor Report
                                </button>
                            </div>
                        </motion.div>
                    )}
                </div>


                {/* Right Column - Scores and Ratios */}
                <div className="lg:col-span-2 space-y-6">
                    {healthScore ? (
                        <>
                            {/* Health Score Main Card */}
                            <div className="glass-panel p-8 rounded-3xl border border-white/40 shadow-xl overflow-hidden relative">
                                <div className="absolute top-0 right-0 w-64 h-64 bg-primary-100/50 blur-[100px] rounded-full -mr-32 -mt-32 -z-10"></div>

                                <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
                                    <div>
                                        <h2 className="text-2xl font-bold text-slate-900">Financial Health Score</h2>
                                        <p className="text-slate-500">Comprehensive rating based on your latest statements</p>
                                    </div>
                                    <div className={`px-6 py-2 rounded-2xl text-2xl font-black ${healthScore.overall_score >= 80 ? 'bg-emerald-100 text-emerald-700' : healthScore.overall_score >= 60 ? 'bg-blue-100 text-blue-700' : 'bg-amber-100 text-amber-700'}`}>
                                        {healthScore.grade}
                                    </div>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
                                    <div className="relative w-48 h-48 mx-auto">
                                        <svg className="w-full h-full transform -rotate-90">
                                            <circle cx="96" cy="96" r="88" fill="transparent" stroke="#f1f5f9" strokeWidth="12" />
                                            <motion.circle
                                                cx="96" cy="96" r="88" fill="transparent"
                                                stroke={healthScore.overall_score >= 80 ? '#10b981' : healthScore.overall_score >= 60 ? '#3b82f6' : '#f59e0b'}
                                                strokeWidth="12"
                                                strokeDasharray={2 * Math.PI * 88}
                                                initial={{ strokeDashoffset: 2 * Math.PI * 88 }}
                                                animate={{ strokeDashoffset: 2 * Math.PI * 88 * (1 - healthScore.overall_score / 100) }}
                                                transition={{ duration: 1.5, ease: "easeOut" }}
                                                strokeLinecap="round"
                                            />
                                        </svg>
                                        <div className="absolute inset-0 flex flex-col items-center justify-center">
                                            <span className="text-5xl font-black text-slate-900">{healthScore.overall_score}</span>
                                            <span className="text-slate-400 font-bold text-sm">Target: 85+</span>
                                        </div>
                                    </div>

                                    <div className="space-y-4">
                                        {Object.entries(healthScore.score_breakdown).map(([key, val], idx) => {
                                            const maxMap: any = {
                                                liquidity: 25,
                                                profitability: 30,
                                                leverage: 20,
                                                efficiency: 15,
                                                cash_flow: 10
                                            };
                                            const max = maxMap[key] || 25;
                                            return (
                                                <div key={key}>
                                                    <div className="flex justify-between text-sm font-bold text-slate-700 mb-1 capitalize">
                                                        <span>{key.replace('_', ' ')}</span>
                                                        <span>{val}/{max}</span>
                                                    </div>
                                                    <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                                                        <motion.div
                                                            initial={{ width: 0 }}
                                                            animate={{ width: `${(val / max) * 100}%` }}
                                                            transition={{ duration: 1, delay: idx * 0.1 }}
                                                            className={`h-full rounded-full ${idx === 0 ? 'bg-emerald-500' : idx === 1 ? 'bg-blue-500' : idx === 2 ? 'bg-purple-500' : 'bg-amber-500'}`}
                                                        ></motion.div>
                                                    </div>
                                                </div>
                                            );
                                        })}
                                    </div>
                                </div>
                            </div>

                            {/* Ratios Grid */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <RatioCategoryCard title="Liquidity" ratios={healthScore.ratios.liquidity} color="emerald" />
                                <RatioCategoryCard title="Profitability" ratios={healthScore.ratios.profitability} color="blue" />
                            </div>
                        </>
                    ) : (
                        <div className="glass-panel p-12 rounded-3xl border border-dashed border-slate-300 text-center flex flex-col items-center">
                            <div className="w-16 h-16 bg-slate-50 text-slate-400 rounded-full flex items-center justify-center mb-6">
                                <TrendingUp size={32} />
                            </div>
                            <h2 className="text-2xl font-bold text-slate-900 mb-2">No Analysis Data Available</h2>
                            <p className="text-slate-500 max-w-md mx-auto mb-8">
                                Upload your company's Balance Sheet and P&L statement to unlock AI-powered health scoring and ratio analysis.
                            </p>
                            <Link to={`/upload/${company.id}`} className="btn-primary">
                                Upload Statements Now
                            </Link>
                        </div>
                    )}
                </div>
            </div>
            {company && <ChatInterface companyId={company.id.toString()} companyName={company.name} />}
        </div>
    );
};

const InfoItem = ({ icon, label, value, isLink }: any) => (
    <div className="flex items-center text-sm">
        <div className="w-8 h-8 rounded-lg bg-slate-50 text-slate-400 flex items-center justify-center mr-3">
            {icon}
        </div>
        <div className="flex-grow">
            <p className="text-slate-400 text-xs font-semibold uppercase tracking-wider">{label}</p>
            {isLink ? (
                <a href={value.startsWith('http') ? value : `https://${value}`} target="_blank" rel="noreferrer" className="text-primary-600 font-bold hover:underline">
                    {value}
                </a>
            ) : (
                <p className="text-slate-800 font-bold">{value}</p>
            )}
        </div>
    </div>
);

const RatioCategoryCard = ({ title, ratios, color }: any) => {
    const colorMap: any = {
        emerald: 'text-emerald-600 bg-emerald-50',
        blue: 'text-blue-600 bg-blue-50',
        amber: 'text-amber-600 bg-amber-50',
    };

    return (
        <div className="glass-panel p-6 rounded-2xl border border-white/40 shadow-lg">
            <h3 className="text-lg font-bold text-slate-900 mb-6 flex items-center">
                <span className={`w-2 h-6 rounded-full mr-3 ${color === 'emerald' ? 'bg-emerald-500' : 'bg-blue-500'}`}></span>
                {title} Ratios
            </h3>
            <div className="space-y-4">
                {Object.entries(ratios).map(([key, val]: any) => (
                    <div key={key} className="flex justify-between items-center bg-slate-50/50 p-3 rounded-xl border border-slate-100">
                        <span className="text-sm font-semibold text-slate-600 capitalize">{key.replace('_', ' ')}</span>
                        <span className="text-sm font-black text-slate-900">{(val as number).toFixed(2)}</span>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default CompanyDetail;
