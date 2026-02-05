import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
    Building2,
    ArrowLeft,
    Save,
    MapPin,
    Calendar,
    Globe,
    Users,
    Briefcase,
    Hash,
    Shield,
    Loader2
} from 'lucide-react';
import { motion } from 'framer-motion';
import apiClient from '../../api/client';

const CompanyCreate: React.FC = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const [formData, setFormData] = useState({
        name: '',
        registration_number: '',
        pan: '',
        gstin: '',
        industry: 'Manufacturing',
        sub_industry: '',
        founded_date: '',
        employee_count: 0,
        annual_revenue: 0,
        website: '',
        address_line1: '',
        address_line2: '',
        city: '',
        state: '',
        pincode: '',
        country: 'India'
    });

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value, type } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'number' ? parseFloat(value) : value
        }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            // Clean data before sending
            const submitData = { ...formData };
            if (!submitData.founded_date) delete (submitData as any).founded_date;
            if (!submitData.employee_count) (submitData as any).employee_count = 0;
            if (!submitData.annual_revenue) (submitData as any).annual_revenue = 0;

            const res = await apiClient.post('/companies/', submitData);
            navigate(`/companies/${res.data.id}`);
        } catch (err: any) {
            console.error('Failed to create company', err);
            setError(err.response?.data?.detail || 'Failed to create company. Please check your inputs.');
        } finally {
            setLoading(false);
        }
    };

    const industries = [
        "Manufacturing", "Retail", "Agriculture", "Services", "Logistics",
        "E-commerce", "Healthcare", "Education", "Hospitality", "Construction",
        "IT & Software", "Other"
    ];

    return (
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
            <Link to="/companies" className="inline-flex items-center text-slate-500 hover:text-primary-600 font-medium mb-8 transition-colors">
                <ArrowLeft size={18} className="mr-2" /> Back to All Companies
            </Link>

            <div className="mb-10 text-center">
                <div className="w-16 h-16 bg-primary-100 text-primary-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <Building2 size={32} />
                </div>
                <h1 className="text-3xl font-extrabold text-slate-900 font-display">Add Your Company</h1>
                <p className="text-slate-500 mt-2">Fill in your business details to start your financial analysis</p>
            </div>

            {error && (
                <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl flex items-center"
                >
                    <Shield className="w-5 h-5 mr-3 shrink-0" />
                    <p className="text-sm font-medium">{error}</p>
                </motion.div>
            )}

            <form onSubmit={handleSubmit} className="space-y-8">
                {/* Basic Information Section */}
                <div className="glass-panel p-8 rounded-3xl border border-white/40 shadow-xl">
                    <h2 className="text-xl font-bold text-slate-900 mb-6 flex items-center">
                        <span className="w-1.5 h-6 bg-primary-500 rounded-full mr-3"></span>
                        Basic Information
                    </h2>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="col-span-1 md:col-span-2">
                            <label className="block text-sm font-bold text-slate-700 mb-2">Company Name *</label>
                            <div className="relative">
                                <Building2 className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
                                <input
                                    type="text"
                                    name="name"
                                    required
                                    className="input-field pl-12"
                                    placeholder="e.g. Acme Corporation Pvt Ltd"
                                    value={formData.name}
                                    onChange={handleChange}
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-bold text-slate-700 mb-2">Industry *</label>
                            <div className="relative">
                                <Briefcase className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
                                <select
                                    name="industry"
                                    required
                                    className="input-field pl-12 appearance-none"
                                    value={formData.industry}
                                    onChange={handleChange}
                                >
                                    {industries.map(ind => (
                                        <option key={ind} value={ind}>{ind}</option>
                                    ))}
                                </select>
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-bold text-slate-700 mb-2">Sub-Industry</label>
                            <input
                                type="text"
                                name="sub_industry"
                                className="input-field"
                                placeholder="e.g. Automotive Parts"
                                value={formData.sub_industry}
                                onChange={handleChange}
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-bold text-slate-700 mb-2">Founded Date</label>
                            <div className="relative">
                                <Calendar className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
                                <input
                                    type="date"
                                    name="founded_date"
                                    className="input-field pl-12"
                                    value={formData.founded_date}
                                    onChange={handleChange}
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-bold text-slate-700 mb-2">Website</label>
                            <div className="relative">
                                <Globe className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
                                <input
                                    type="url"
                                    name="website"
                                    className="input-field pl-12"
                                    placeholder="https://acme.inc"
                                    value={formData.website}
                                    onChange={handleChange}
                                />
                            </div>
                        </div>
                    </div>
                </div>

                {/* Registration Details */}
                <div className="glass-panel p-8 rounded-3xl border border-white/40 shadow-xl">
                    <h2 className="text-xl font-bold text-slate-900 mb-6 flex items-center">
                        <span className="w-1.5 h-6 bg-indigo-500 rounded-full mr-3"></span>
                        Registration & Tax
                    </h2>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div>
                            <label className="block text-sm font-bold text-slate-700 mb-2">Registration Number</label>
                            <div className="relative">
                                <Hash className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
                                <input
                                    type="text"
                                    name="registration_number"
                                    className="input-field pl-12"
                                    placeholder="CIN / Registration"
                                    value={formData.registration_number}
                                    onChange={handleChange}
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-bold text-slate-700 mb-2">PAN</label>
                            <input
                                type="text"
                                name="pan"
                                className="input-field uppercase"
                                placeholder="Business PAN"
                                value={formData.pan}
                                onChange={handleChange}
                                maxLength={10}
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-bold text-slate-700 mb-2">GSTIN</label>
                            <input
                                type="text"
                                name="gstin"
                                className="input-field uppercase"
                                placeholder="GST Number"
                                value={formData.gstin}
                                onChange={handleChange}
                                maxLength={15}
                            />
                        </div>
                    </div>
                </div>

                {/* Address & Scale */}
                <div className="glass-panel p-8 rounded-3xl border border-white/40 shadow-xl">
                    <h2 className="text-xl font-bold text-slate-900 mb-6 flex items-center">
                        <span className="w-1.5 h-6 bg-emerald-500 rounded-full mr-3"></span>
                        Location & Scale
                    </h2>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="col-span-1 md:col-span-2">
                            <label className="block text-sm font-bold text-slate-700 mb-2">Address Line 1</label>
                            <div className="relative">
                                <MapPin className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
                                <input
                                    type="text"
                                    name="address_line1"
                                    className="input-field pl-12"
                                    placeholder="Street address, P.O. box"
                                    value={formData.address_line1}
                                    onChange={handleChange}
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-bold text-slate-700 mb-2">City</label>
                            <input
                                type="text"
                                name="city"
                                className="input-field"
                                value={formData.city}
                                onChange={handleChange}
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-bold text-slate-700 mb-2">State</label>
                            <input
                                type="text"
                                name="state"
                                className="input-field"
                                value={formData.state}
                                onChange={handleChange}
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-bold text-slate-700 mb-2">Employee Count</label>
                            <div className="relative">
                                <Users className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
                                <input
                                    type="number"
                                    name="employee_count"
                                    className="input-field pl-12"
                                    value={formData.employee_count}
                                    onChange={handleChange}
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-bold text-slate-700 mb-2">Annual Revenue (₹)</label>
                            <input
                                type="number"
                                name="annual_revenue"
                                className="input-field"
                                placeholder="In Lakhs/Crores"
                                value={formData.annual_revenue}
                                onChange={handleChange}
                            />
                        </div>
                    </div>
                </div>

                <div className="flex justify-end gap-4">
                    <button
                        type="button"
                        onClick={() => navigate('/companies')}
                        className="btn-secondary px-8"
                    >
                        Cancel
                    </button>
                    <button
                        type="submit"
                        disabled={loading}
                        className="btn-primary px-12 flex items-center justify-center min-w-[160px]"
                    >
                        {loading ? (
                            <Loader2 className="w-5 h-5 animate-spin" />
                        ) : (
                            <>
                                <Save className="w-5 h-5 mr-2" /> Create Company
                            </>
                        )}
                    </button>
                </div>
            </form>
        </div>
    );
};

export default CompanyCreate;
