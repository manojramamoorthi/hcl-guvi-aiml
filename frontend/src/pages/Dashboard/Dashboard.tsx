import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Building2, TrendingUp, AlertTriangle, ArrowUpRight, ArrowDownRight, MoreVertical } from 'lucide-react';
import { motion } from 'framer-motion';
import apiClient from '../../api/client';
import { Company, HealthScore } from '../../types';

const Dashboard: React.FC = () => {
    const [companies, setCompanies] = useState<Company[]>([]);
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState({
        totalCompanies: 0,
        avgHealthScore: 0,
        activeAlerts: 0
    });

    useEffect(() => {
        const fetchDashboardData = async () => {
            try {
                const res = await apiClient.get('/companies/');
                setCompanies(res.data);

                // Mock some aggregate stats for now as the backend doesn't have an aggregate endpoint
                setStats({
                    totalCompanies: res.data.length,
                    avgHealthScore: 72,
                    activeAlerts: 3
                });
            } catch (err) {
                console.error('Failed to fetch dashboard data', err);
            } finally {
                setLoading(false);
            }
        };

        fetchDashboardData();
    }, []);

    if (loading) {
        return (
            <div className="max-w-7xl mx-auto px-4 py-12">
                <div className="animate-pulse space-y-8">
                    <div className="h-20 bg-slate-200 rounded-3xl w-1/3"></div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="h-32 bg-slate-100 rounded-3xl"></div>
                        <div className="h-32 bg-slate-100 rounded-3xl"></div>
                        <div className="h-32 bg-slate-100 rounded-3xl"></div>
                    </div>
                    <div className="h-64 bg-slate-50 rounded-3xl"></div>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-10">
                <div>
                    <h1 className="text-3xl font-extrabold text-slate-900 font-display">Dashboard Overview</h1>
                    <p className="text-slate-500">Monitor your business portfolio and financial health</p>
                </div>
                <Link to="/companies/new" className="btn-primary flex items-center justify-center">
                    <Plus className="w-5 h-5 mr-2" /> Add Company
                </Link>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
                <StatCard
                    label="Total Companies"
                    value={stats.totalCompanies.toString()}
                    icon={<Building2 className="text-primary-600" />}
                    trend="+1 this month"
                    isPositive={true}
                />
                <StatCard
                    label="Avg. Health Score"
                    value={`${stats.avgHealthScore}/100`}
                    icon={<TrendingUp className="text-emerald-600" />}
                    trend="Good"
                    isPositive={true}
                />
                <StatCard
                    label="Active Alerts"
                    value={stats.activeAlerts.toString()}
                    icon={<AlertTriangle className="text-amber-600" />}
                    trend="High priority"
                    isPositive={false}
                />
            </div>

            {/* Companies List */}
            <div className="glass-panel rounded-3xl overflow-hidden border border-white/40 mb-10">
                <div className="px-8 py-6 border-b border-slate-100 flex items-center justify-between">
                    <h3 className="text-xl font-bold text-slate-900">Your Companies</h3>
                    <Link to="/companies" className="text-primary-600 text-sm font-semibold hover:underline">View All</Link>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead>
                            <tr className="bg-slate-50/50 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider">
                                <th className="px-8 py-4">Company</th>
                                <th className="px-8 py-4">Industry</th>
                                <th className="px-8 py-4">Status</th>
                                <th className="px-8 py-4">Health Score</th>
                                <th className="px-8 py-4 text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                            {companies.length > 0 ? (
                                companies.slice(0, 5).map((company) => (
                                    <tr key={company.id} className="hover:bg-slate-50/30 transition-colors group">
                                        <td className="px-8 py-5">
                                            <div className="flex items-center">
                                                <div className="w-10 h-10 rounded-xl bg-primary-100 text-primary-600 flex items-center justify-center font-bold mr-3 group-hover:bg-primary-600 group-hover:text-white transition-colors">
                                                    {company.name[0].toUpperCase()}
                                                </div>
                                                <div>
                                                    <p className="font-bold text-slate-800">{company.name}</p>
                                                    <p className="text-xs text-slate-500">{company.city || 'India'}</p>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-8 py-5">
                                            <span className="text-sm text-slate-600">{company.industry}</span>
                                        </td>
                                        <td className="px-8 py-5">
                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">
                                                Active
                                            </span>
                                        </td>
                                        <td className="px-8 py-5">
                                            <div className="flex items-center space-x-2">
                                                <div className="w-full max-w-[100px] h-1.5 bg-slate-100 rounded-full overflow-hidden">
                                                    <div className="h-full bg-emerald-500 rounded-full" style={{ width: '75%' }}></div>
                                                </div>
                                                <span className="text-sm font-bold text-slate-700">75</span>
                                            </div>
                                        </td>
                                        <td className="px-8 py-5 text-right">
                                            <div className="flex items-center justify-end space-x-2">
                                                <Link to={`/companies/${company.id}`} className="p-2 text-slate-400 hover:text-primary-600 rounded-lg hover:bg-primary-50">
                                                    <Plus className="w-4 h-4 rotate-45" />
                                                </Link>
                                                <button className="p-2 text-slate-400 hover:text-slate-600">
                                                    <MoreVertical size={18} />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan={5} className="px-8 py-20 text-center">
                                        <div className="flex flex-col items-center">
                                            <Building2 className="w-12 h-12 text-slate-200 mb-4" />
                                            <p className="text-slate-500 font-medium">No companies added yet</p>
                                            <Link to="/companies/new" className="text-primary-600 mt-2 font-bold">Add your first company</Link>
                                        </div>
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

const StatCard = ({ label, value, icon, trend, isPositive }: any) => (
    <motion.div
        whileHover={{ y: -5 }}
        className="glass-card p-6 border border-white/50 shadow-sm"
    >
        <div className="flex justify-between items-start mb-4">
            <div className="p-3 rounded-2xl bg-white/60 shadow-inner">
                {React.cloneElement(icon, { size: 24 })}
            </div>
            <div className={`flex items-center text-xs font-bold px-2 py-1 rounded-lg ${isPositive ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'}`}>
                {isPositive ? <ArrowUpRight size={14} className="mr-1" /> : <ArrowDownRight size={14} className="mr-1" />}
                {trend}
            </div>
        </div>
        <h3 className="text-slate-500 text-sm font-medium">{label}</h3>
        <p className="text-3xl font-extrabold text-slate-900 mt-1 font-display">{value}</p>
    </motion.div>
);

export default Dashboard;
