import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Mail, Lock, User, Phone, Loader2, ArrowRight, CheckCircle2 } from 'lucide-react';
import { motion } from 'framer-motion';

const Register: React.FC = () => {
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        full_name: '',
        phone: '',
        language_preference: 'en'
    });
    const [error, setError] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const { register } = useAuth();
    const navigate = useNavigate();

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSubmitting(true);
        setError('');

        try {
            await register(formData);
            navigate('/dashboard');
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Registration failed. Please try again.');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="min-h-[90vh] flex items-center justify-center px-4 py-12">
            <div className="max-w-5xl w-full grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">

                {/* Left Side - Info */}
                <motion.div
                    initial={{ opacity: 0, x: -30 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="hidden lg:block space-y-8"
                >
                    <h2 className="text-5xl font-extrabold text-slate-900 font-display leading-tight">
                        Join thousands of <br />
                        <span className="bg-clip-text text-transparent bg-gradient-to-r from-primary-600 to-indigo-600">
                            successful SMEs
                        </span>
                    </h2>

                    <div className="space-y-6">
                        <FeaturePoint
                            title="Instant Credit Insights"
                            desc="Get a comprehensive breakdown of your business creditworthiness in seconds."
                        />
                        <FeaturePoint
                            title="AI-Powered Recommendations"
                            desc="Personalized action plans to improve your financial stability and growth potential."
                        />
                        <FeaturePoint
                            title="Bank-Level Security"
                            desc="Your data is encrypted and protected by the highest industry standards."
                        />
                    </div>
                </motion.div>

                {/* Right Side - Form */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="w-full"
                >
                    <div className="glass-panel p-8 rounded-3xl shadow-2xl border border-white/40">
                        <div className="mb-8">
                            <h3 className="text-2xl font-bold text-slate-900 font-display">Create Your Account</h3>
                            <p className="text-slate-600">Start your financial health journey today</p>
                        </div>

                        {error && (
                            <div className="mb-6 p-4 bg-danger-50 border border-danger-100 text-danger-600 text-sm rounded-xl">
                                {error}
                            </div>
                        )}

                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-semibold text-slate-700 mb-1.5 ml-1">Full Name</label>
                                    <div className="relative">
                                        <input
                                            name="full_name"
                                            type="text"
                                            required
                                            value={formData.full_name}
                                            onChange={handleChange}
                                            className="input-field pl-11"
                                            placeholder="John Doe"
                                        />
                                        <User className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
                                    </div>
                                </div>
                                <div>
                                    <label className="block text-sm font-semibold text-slate-700 mb-1.5 ml-1">Phone Number</label>
                                    <div className="relative">
                                        <input
                                            name="phone"
                                            type="tel"
                                            value={formData.phone}
                                            onChange={handleChange}
                                            className="input-field pl-11"
                                            placeholder="+91 98765 43210"
                                        />
                                        <Phone className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
                                    </div>
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-semibold text-slate-700 mb-1.5 ml-1">Email address</label>
                                <div className="relative">
                                    <input
                                        name="email"
                                        type="email"
                                        required
                                        value={formData.email}
                                        onChange={handleChange}
                                        className="input-field pl-11"
                                        placeholder="name@company.com"
                                    />
                                    <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-semibold text-slate-700 mb-1.5 ml-1">Password</label>
                                <div className="relative">
                                    <input
                                        name="password"
                                        type="password"
                                        required
                                        value={formData.password}
                                        onChange={handleChange}
                                        className="input-field pl-11"
                                        placeholder="Min. 8 characters"
                                    />
                                    <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
                                </div>
                            </div>

                            <div className="pt-2">
                                <button
                                    type="submit"
                                    disabled={isSubmitting}
                                    className="w-full btn-primary py-3.5 text-lg flex items-center justify-center"
                                >
                                    {isSubmitting ? (
                                        <Loader2 className="w-6 h-6 animate-spin" />
                                    ) : (
                                        <>Create Account <ArrowRight className="ml-2 w-5 h-5" /></>
                                    )}
                                </button>
                            </div>
                        </form>

                        <p className="mt-8 text-center text-slate-600">
                            Already have an account?{' '}
                            <Link to="/login" className="text-primary-600 font-bold hover:text-primary-700 transition-colors">
                                Sign in
                            </Link>
                        </p>
                    </div>
                </motion.div>
            </div>
        </div>
    );
};

const FeaturePoint = ({ title, desc }: { title: string; desc: string }) => (
    <div className="flex items-start space-x-4">
        <div className="mt-1 w-6 h-6 rounded-full bg-emerald-100 flex items-center justify-center flex-shrink-0">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
        </div>
        <div>
            <h4 className="font-bold text-slate-800">{title}</h4>
            <p className="text-slate-500 text-sm">{desc}</p>
        </div>
    </div>
);

export default Register;
