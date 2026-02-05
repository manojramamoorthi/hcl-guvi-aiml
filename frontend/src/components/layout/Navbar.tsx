import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { LayoutDashboard, LogOut, Building2, FileUp, PieChart, Menu, X } from 'lucide-react';

const Navbar: React.FC = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const [isOpen, setIsOpen] = React.useState(false);

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <nav className="sticky top-0 z-50 glass-panel border-b border-white/20">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16">
                    <div className="flex items-center">
                        <Link to="/" className="flex items-center space-x-2">
                            <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center shadow-lg shadow-primary-500/30">
                                <PieChart className="w-5 h-5 text-white" />
                            </div>
                            <span className="text-xl font-bold font-display tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-primary-600 to-primary-800">
                                SME <span className="text-slate-900">Finance</span>
                            </span>
                        </Link>
                    </div>

                    {/* Desktop Menu */}
                    <div className="hidden md:flex items-center space-x-4">
                        {user ? (
                            <>
                                <NavLink to="/dashboard" icon={<LayoutDashboard size={18} />} label="Dashboard" />
                                <NavLink to="/companies" icon={<Building2 size={18} />} label="Companies" />
                                <div className="h-6 w-px bg-slate-200 mx-2" />
                                <div className="flex items-center space-x-3">
                                    <div className="text-right">
                                        <p className="text-sm font-medium text-slate-900">{user.full_name}</p>
                                        <p className="text-xs text-slate-500">{user.email}</p>
                                    </div>
                                    <button
                                        onClick={handleLogout}
                                        className="p-2 text-slate-400 hover:text-danger-600 transition-colors rounded-lg hover:bg-danger-50"
                                    >
                                        <LogOut size={20} />
                                    </button>
                                </div>
                            </>
                        ) : (
                            <div className="flex items-center space-x-3">
                                <Link to="/login" className="text-slate-600 hover:text-primary-600 font-medium px-4 py-2 transition-colors">
                                    Login
                                </Link>
                                <Link to="/register" className="btn-primary">
                                    Get Started
                                </Link>
                            </div>
                        )}
                    </div>

                    {/* Mobile menu button */}
                    <div className="md:hidden flex items-center">
                        <button
                            onClick={() => setIsOpen(!isOpen)}
                            className="p-2 rounded-lg text-slate-600 hover:bg-white/50"
                        >
                            {isOpen ? <X size={24} /> : <Menu size={24} />}
                        </button>
                    </div>
                </div>
            </div>

            {/* Mobile Menu */}
            {isOpen && (
                <div className="md:hidden glass-panel border-t border-white/10 p-4 space-y-2 animate-in slide-in-from-top duration-300">
                    {user ? (
                        <>
                            <MobileNavLink to="/dashboard" label="Dashboard" onClick={() => setIsOpen(false)} />
                            <MobileNavLink to="/companies" label="Companies" onClick={() => setIsOpen(false)} />
                            <button
                                onClick={handleLogout}
                                className="w-full flex items-center px-4 py-3 text-danger-600 font-medium hover:bg-danger-50 rounded-xl transition-colors"
                            >
                                <LogOut size={18} className="mr-3" /> Logout
                            </button>
                        </>
                    ) : (
                        <div className="grid grid-cols-1 gap-2 pt-2">
                            <Link
                                to="/login"
                                onClick={() => setIsOpen(false)}
                                className="w-full text-center py-3 text-slate-600 font-medium hover:bg-white/50 rounded-xl"
                            >
                                Login
                            </Link>
                            <Link
                                to="/register"
                                onClick={() => setIsOpen(false)}
                                className="w-full btn-primary text-center py-3"
                            >
                                Get Started
                            </Link>
                        </div>
                    )}
                </div>
            )}
        </nav>
    );
};

const NavLink: React.FC<{ to: string; icon: React.ReactNode; label: string }> = ({ to, icon, label }) => (
    <Link
        to={to}
        className="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-slate-600 hover:text-primary-600 hover:bg-primary-50/50 rounded-xl transition-all"
    >
        {icon}
        <span>{label}</span>
    </Link>
);

const MobileNavLink: React.FC<{ to: string; label: string; onClick: () => void }> = ({ to, label, onClick }) => (
    <Link
        to={to}
        onClick={onClick}
        className="block px-4 py-3 text-slate-600 font-medium hover:bg-primary-50 rounded-xl transition-colors"
    >
        {label}
    </Link>
);

export default Navbar;
