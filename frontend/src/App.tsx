import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Navbar from './components/layout/Navbar';

// Lazy load pages for better performance
const Landing = React.lazy(() => import('./pages/Landing/Landing'));
const Login = React.lazy(() => import('./pages/Auth/Login'));
const Register = React.lazy(() => import('./pages/Auth/Register'));
const Dashboard = React.lazy(() => import('./pages/Dashboard/Dashboard'));
const CompanyList = React.lazy(() => import('./pages/Company/CompanyList'));
const CompanyDetail = React.lazy(() => import('./pages/Company/CompanyDetail'));
const CompanyCreate = React.lazy(() => import('./pages/Company/CompanyCreate'));
const UploadData = React.lazy(() => import('./pages/Upload/UploadData'));

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const { user, loading } = useAuth();

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="w-12 h-12 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin"></div>
            </div>
        );
    }

    if (!user) return <Navigate to="/login" />;
    return <>{children}</>;
};

const AppContent: React.FC = () => {
    return (
        <div className="min-h-screen flex flex-col">
            <Navbar />
            <main className="flex-grow">
                <React.Suspense
                    fallback={
                        <div className="min-h-[60vh] flex items-center justify-center">
                            <div className="w-10 h-10 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin"></div>
                        </div>
                    }
                >
                    <Routes>
                        <Route path="/" element={<Landing />} />
                        <Route path="/login" element={<Login />} />
                        <Route path="/register" element={<Register />} />

                        <Route
                            path="/dashboard"
                            element={
                                <ProtectedRoute>
                                    <Dashboard />
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/companies"
                            element={
                                <ProtectedRoute>
                                    <CompanyList />
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/companies/new"
                            element={
                                <ProtectedRoute>
                                    <CompanyCreate />
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/companies/:id"
                            element={
                                <ProtectedRoute>
                                    <CompanyDetail />
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/upload/:companyId"
                            element={
                                <ProtectedRoute>
                                    <UploadData />
                                </ProtectedRoute>
                            }
                        />

                        <Route path="*" element={<Navigate to="/" />} />
                    </Routes>
                </React.Suspense>
            </main>
            <footer className="py-8 text-center text-slate-500 text-sm border-t border-slate-100">
                <p>© {new Date().getFullYear()} SME Financial Health Platform. All rights reserved.</p>
            </footer>
        </div>
    );
};

const App: React.FC = () => {
    return (
        <Router>
            <AuthProvider>
                <AppContent />
            </AuthProvider>
        </Router>
    );
};

export default App;
