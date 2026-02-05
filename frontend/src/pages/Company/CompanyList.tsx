import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
    Building2,
    Plus,
    Search,
    MapPin,
    ArrowRight,
    Filter,
    MoreHorizontal,
    Loader2
} from 'lucide-react';
import { motion } from 'framer-motion';
import apiClient from '../../api/client';
import { Company } from '../../types';

const CompanyList: React.FC = () => {
    const [companies, setCompanies] = useState<Company[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        const fetchCompanies = async () => {
            try {
                const res = await apiClient.get('/companies/');
                setCompanies(res.data);
            } catch (err) {
                console.error('Failed to fetch companies', err);
            } finally {
                setLoading(false);
            }
        };
        fetchCompanies();
    }, []);

    const filteredCompanies = companies.filter(c =>
        c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.industry.toLowerCase().includes(searchTerm.toLowerCase())
    );

    if (loading) {
        return (
            <div className="max-w-7xl mx-auto px-4 py-12 flex items-center justify-center min-h-[60vh]">
                <Loader2 className="w-10 h-10 text-primary-600 animate-spin" />
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-10">
                <div>
                    <h1 className="text-3xl font-extrabold text-slate-900 font-display">Your Companies</h1>
                    <p className="text-slate-500">Manage your business profiles and access financial analysis</p>
                </div>
                <Link to="/companies/new" className="btn-primary flex items-center justify-center">
                    <Plus className="w-5 h-5 mr-2" /> Add New Company
                </Link>
            </div>

            {/* Search and Filter */}
            <div className="flex flex-col md:flex-row gap-4 mb-8">
                <div className="relative flex-grow">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
                    <input
                        type="text"
                        placeholder="Search by company name or industry..."
                        className="input-field pl-12"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
                <button className="btn-secondary flex items-center justify-center space-x-2">
                    <Filter size={18} />
                    <span>Filters</span>
                </button>
            </div>

            {/* Grid */}
            {filteredCompanies.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {filteredCompanies.map((company, index) => (
                        <motion.div
                            key={company.id}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.1 }}
                        >
                            <Link to={`/companies/${company.id}`} className="block group">
                                <div className="glass-card p-6 h-full flex flex-col border border-white/40">
                                    <div className="flex justify-between items-start mb-4">
                                        <div className="w-14 h-14 bg-gradient-to-br from-primary-500 to-primary-700 rounded-2xl flex items-center justify-center text-white text-xl font-bold shadow-lg shadow-primary-500/20 group-hover:scale-110 transition-transform">
                                            {company.name[0].toUpperCase()}
                                        </div>
                                        <button className="p-2 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 transition-colors">
                                            <MoreHorizontal size={20} />
                                        </button>
                                    </div>

                                    <h3 className="text-xl font-bold text-slate-900 mb-1 group-hover:text-primary-600 transition-colors">
                                        {company.name}
                                    </h3>

                                    <div className="flex items-center text-slate-500 text-sm mb-4">
                                        <MapPin size={14} className="mr-1" />
                                        {company.city}, {company.state}
                                    </div>

                                    <div className="mt-auto space-y-4">
                                        <div className="flex flex-wrap gap-2 text-xs font-semibold">
                                            <span className="px-2.5 py-1 bg-slate-100 text-slate-600 rounded-full">
                                                {company.industry}
                                            </span>
                                            <span className="px-2.5 py-1 bg-emerald-100 text-emerald-700 rounded-full">
                                                Active
                                            </span>
                                        </div>

                                        <div className="pt-4 border-t border-slate-100 flex items-center justify-between text-primary-600 font-bold text-sm">
                                            <span>View Analytics</span>
                                            <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
                                        </div>
                                    </div>
                                </div>
                            </Link>
                        </motion.div>
                    ))}
                </div>
            ) : (
                <div className="glass-panel py-20 text-center rounded-3xl border border-white/40">
                    <div className="max-w-md mx-auto">
                        <div className="w-20 h-20 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-6">
                            <Building2 className="w-10 h-10 text-slate-300" />
                        </div>
                        <h3 className="text-2xl font-bold text-slate-900 mb-2">No companies found</h3>
                        <p className="text-slate-500 mb-8">
                            {searchTerm ? "We couldn't find any results matching your search criteria." : "Get started by adding your first company profile."}
                        </p>
                        {!searchTerm && (
                            <Link to="/companies/new" className="btn-primary">
                                Add Company
                            </Link>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default CompanyList;
