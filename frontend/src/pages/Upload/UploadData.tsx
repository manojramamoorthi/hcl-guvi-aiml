import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
    FileUp,
    CheckCircle2,
    AlertCircle,
    Loader2,
    ArrowLeft,
    FileSpreadsheet,
    ArrowRight
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import apiClient from '../../api/client';
import { getErrorMessage } from '../../utils/errorUtils';

const UploadData: React.FC = () => {
    const { companyId } = useParams<{ companyId: string }>();
    const navigate = useNavigate();

    const [statementType, setStatementType] = useState('balance_sheet');
    const [periodStart, setPeriodStart] = useState('2023-04-01');
    const [periodEnd, setPeriodEnd] = useState('2024-03-31');
    const [file, setFile] = useState<File | null>(null);

    const [isUploading, setIsUploading] = useState(false);
    const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle');
    const [errorMessage, setErrorMessage] = useState('');

    const [uploadResponse, setUploadResponse] = useState<any>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
            setUploadStatus('idle');
            setUploadResponse(null);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!file) return;

        setIsUploading(true);
        setUploadStatus('idle');
        setErrorMessage('');

        const formData = new FormData();
        formData.append('file', file);
        // Add other fields to formData too
        formData.append('statement_type', statementType);
        formData.append('period_start', new Date(periodStart).toISOString());
        formData.append('period_end', new Date(periodEnd).toISOString());

        try {
            const response = await apiClient.post(`/upload/${companyId}/financial-statement`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
                params: {
                    statement_type: statementType,
                    period_start: new Date(periodStart).toISOString(),
                    period_end: new Date(periodEnd).toISOString(),
                }
            });
            setUploadResponse(response.data);
            setUploadStatus('success');
            // Remove automatic redirection to allow user to see the summary
        } catch (err: any) {
            setUploadStatus('error');
            setErrorMessage(getErrorMessage(err));
        } finally {
            setIsUploading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto px-4 py-12">
            <Link to={`/companies/${companyId}`} className="inline-flex items-center text-slate-500 hover:text-primary-600 font-medium mb-8 transition-colors">
                <ArrowLeft size={18} className="mr-2" /> Back to Company Profile
            </Link>

            <div className="text-center mb-10">
                <h1 className="text-4xl font-extrabold text-slate-900 font-display">Upload Financials</h1>
                <p className="text-slate-500 mt-2">Upload your financial statements to generate AI insights</p>
            </div>

            <div className="glass-panel p-8 rounded-3xl border border-white/40 shadow-2xl overflow-hidden relative min-h-[500px]">
                {/* Success State Overlay */}
                <AnimatePresence>
                    {uploadStatus === 'success' && (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="absolute inset-0 bg-white/98 z-20 flex flex-col items-center justify-center p-8 text-center"
                        >
                            <div className="w-20 h-20 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mb-6">
                                <CheckCircle2 size={48} />
                            </div>
                            <h2 className="text-3xl font-bold text-slate-900 mb-2">Upload Successful!</h2>
                            <p className="text-slate-500 mb-8 font-medium">Your data has been parsed and is ready for analysis.</p>

                            {uploadResponse?.data_summary && (
                                <div className="w-full max-w-md bg-slate-50 rounded-2xl p-6 mb-8 text-left border border-slate-100">
                                    <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">Processing Summary</h3>
                                    <div className="space-y-3">
                                        <div className="flex justify-between">
                                            <span className="text-slate-500 text-sm">Statement Type</span>
                                            <span className="text-slate-900 font-bold text-sm capitalize">{uploadResponse.data_summary.statement_type?.replace('_', ' ')}</span>
                                        </div>
                                        {uploadResponse.data_summary.total_assets !== null && (
                                            <div className="flex justify-between">
                                                <span className="text-slate-500 text-sm">Total Assets</span>
                                                <span className="text-slate-900 font-bold text-sm">₹{uploadResponse.data_summary.total_assets.toLocaleString()}</span>
                                            </div>
                                        )}
                                        {uploadResponse.data_summary.total_liabilities !== null && (
                                            <div className="flex justify-between">
                                                <span className="text-slate-500 text-sm">Total Liabilities</span>
                                                <span className="text-slate-900 font-bold text-sm">₹{uploadResponse.data_summary.total_liabilities.toLocaleString()}</span>
                                            </div>
                                        )}
                                        {uploadResponse.data_summary.total_revenue !== null && (
                                            <div className="flex justify-between">
                                                <span className="text-slate-500 text-sm">Total Revenue</span>
                                                <span className="text-slate-900 font-bold text-sm">₹{uploadResponse.data_summary.total_revenue.toLocaleString()}</span>
                                            </div>
                                        )}
                                        <div className="flex justify-between">
                                            <span className="text-slate-500 text-sm">Period</span>
                                            <span className="text-slate-900 font-bold text-sm">{uploadResponse.data_summary.period}</span>
                                        </div>
                                    </div>
                                </div>
                            )}

                            <div className="flex flex-col sm:flex-row gap-4 w-full max-w-md">
                                <button
                                    onClick={() => navigate(`/companies/${companyId}`)}
                                    className="flex-1 px-6 py-3 bg-white border border-slate-200 text-slate-700 font-bold rounded-xl hover:bg-slate-50 transition-colors"
                                >
                                    Back to Profile
                                </button>
                                <button
                                    onClick={() => navigate(`/companies/${companyId}`)} // Redirection to companies list or specific company profile which has the dashboard
                                    className="flex-1 px-6 py-3 bg-primary-600 text-white font-bold rounded-xl hover:bg-primary-700 shadow-lg shadow-primary-600/20 transition-all flex items-center justify-center"
                                >
                                    View Analysis <ArrowRight size={18} className="ml-2" />
                                </button>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>


                <form onSubmit={handleSubmit} className="space-y-8">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <div className="space-y-6">
                            <div>
                                <label className="block text-sm font-semibold text-slate-700 mb-2">Statement Type</label>
                                <div className="grid grid-cols-1 gap-2">
                                    <TypeOption
                                        active={true}
                                        onClick={() => setStatementType('balance_sheet')}
                                        icon={<FileSpreadsheet size={18} />}
                                        label="Balance Sheet"
                                    />
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-semibold text-slate-700 mb-2">Reporting Period</label>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <span className="text-xs font-bold text-slate-400 uppercase">From</span>
                                        <input
                                            type="date"
                                            className="input-field mt-1"
                                            value={periodStart}
                                            onChange={(e) => setPeriodStart(e.target.value)}
                                        />
                                    </div>
                                    <div>
                                        <span className="text-xs font-bold text-slate-400 uppercase">To</span>
                                        <input
                                            type="date"
                                            className="input-field mt-1"
                                            value={periodEnd}
                                            onChange={(e) => setPeriodEnd(e.target.value)}
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="flex flex-col">
                            <label className="block text-sm font-semibold text-slate-700 mb-2">Upload File</label>
                            <div
                                className={`flex-grow border-2 border-dashed rounded-2xl flex flex-col items-center justify-center p-8 transition-all relative ${file ? 'border-primary-500 bg-primary-50/20' : 'border-slate-200 hover:border-primary-400'}`}
                            >
                                <input
                                    type="file"
                                    className="absolute inset-0 opacity-0 cursor-pointer"
                                    onChange={handleFileChange}
                                    accept=".csv,.xlsx,.xls,.pdf"
                                />
                                <div className={`w-14 h-14 rounded-full flex items-center justify-center mb-4 ${file ? 'bg-primary-500 text-white' : 'bg-slate-100 text-slate-400'}`}>
                                    <FileUp size={28} />
                                </div>
                                {file ? (
                                    <div className="text-center">
                                        <p className="font-bold text-slate-900 max-w-[200px] truncate">{file.name}</p>
                                        <p className="text-sm text-slate-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                                        <button type="button" className="text-primary-600 font-bold text-xs mt-2 underline">Change File</button>
                                    </div>
                                ) : (
                                    <div className="text-center">
                                        <p className="font-bold text-slate-900">Click or drag to upload</p>
                                        <p className="text-sm text-slate-400">PDF, Excel, or CSV (max 10MB)</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>

                    {uploadStatus === 'error' && (
                        <div className="p-4 bg-danger-50 border border-danger-100 rounded-2xl flex items-center text-danger-700 text-sm">
                            <AlertCircle className="mr-3 flex-shrink-0" size={20} />
                            {errorMessage}
                        </div>
                    )}

                    <div className="pt-4">
                        <button
                            type="submit"
                            disabled={!file || isUploading}
                            className="w-full btn-primary py-4 text-lg flex items-center justify-center shadow-xl shadow-primary-500/30"
                        >
                            {isUploading ? (
                                <>
                                    <Loader2 className="w-6 h-6 animate-spin mr-3" />
                                    Processing Statement...
                                </>
                            ) : (
                                <>
                                    Confirm and Process <ArrowRight className="ml-2 w-5 h-5" />
                                </>
                            )}
                        </button>
                    </div>
                </form>
            </div>

            <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="flex items-center space-x-3 text-sm text-slate-500">
                    <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center flex-shrink-0">1</div>
                    <p>Upload your data securely</p>
                </div>
                <div className="flex items-center space-x-3 text-sm text-slate-500">
                    <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center flex-shrink-0">2</div>
                    <p>AI parses and structures entries</p>
                </div>
                <div className="flex items-center space-x-3 text-sm text-slate-500">
                    <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center flex-shrink-0">3</div>
                    <p>View health insights instantly</p>
                </div>
            </div>
        </div>
    );
};

const TypeOption = ({ active, onClick, icon, label }: any) => (
    <button
        type="button"
        onClick={onClick}
        className={`flex items-center space-x-3 p-4 rounded-xl border-2 transition-all ${active ? 'border-primary-500 bg-primary-50/50 text-primary-700 shadow-sm' : 'border-slate-100 hover:border-slate-200 text-slate-600'}`}
    >
        <div className={`${active ? 'text-primary-600' : 'text-slate-400'}`}>
            {icon}
        </div>
        <span className="font-bold">{label}</span>
    </button>
);

export default UploadData;
