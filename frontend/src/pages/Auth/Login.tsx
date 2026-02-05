import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Mail, Lock, Loader2, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';

const Login: React.FC = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSubmitting(true);
        setError('');

        try {
            const formData = new FormData();
            formData.append('username', email); // FastAPI OAuth2 uses 'username' field
            formData.append('password', password);

            await login(formData);
            navigate('/dashboard');
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Invalid email or password');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="min-h-[80vh] flex items-center justify-center px-4 py-12">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="max-w-md w-full"
            >
                <div className="text-center mb-10">
                    <h2 className="text-3xl font-extrabold text-slate-900 font-display">Welcome Back</h2>
                    <p className="mt-2 text-slate-600">Enter your credentials to access your account</p>
                </div>

                <div className="glass-panel p-8 rounded-3xl shadow-2xl border border-white/40">
                    {error && (
                        <div className="mb-6 p-4 bg-danger-50 border border-danger-100 text-danger-600 text-sm rounded-xl">
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div>
                            <label className="block text-sm font-semibold text-slate-700 mb-1.5 ml-1">Email address</label>
                            <div className="relative">
                                <input
                                    type="email"
                                    required
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="input-field pl-11"
                                    placeholder="name@company.com"
                                />
                                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
                            </div>
                        </div>

                        <div>
                            <div className="flex justify-between mb-1.5 ml-1">
                                <label className="text-sm font-semibold text-slate-700">Password</label>
                                <a href="#" className="text-sm text-primary-600 hover:text-primary-700 font-medium">Forgot?</a>
                            </div>
                            <div className="relative">
                                <input
                                    type="password"
                                    required
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="input-field pl-11"
                                    placeholder="••••••••"
                                />
                                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={isSubmitting}
                            className="w-full btn-primary py-3.5 text-lg flex items-center justify-center"
                        >
                            {isSubmitting ? (
                                <Loader2 className="w-6 h-6 animate-spin" />
                            ) : (
                                <>Sign In <ArrowRight className="ml-2 w-5 h-5" /></>
                            )}
                        </button>
                    </form>

                    <p className="mt-8 text-center text-slate-600">
                        Don't have an account?{' '}
                        <Link to="/register" className="text-primary-600 font-bold hover:text-primary-700 transition-colors">
                            Create one for free
                        </Link>
                    </p>
                </div>
            </motion.div>
        </div>
    );
};

export default Login;
