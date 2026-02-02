import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../api';
import { ChevronLeft, RefreshCw, Eye } from 'lucide-react';

const InterviewStatus = () => {
    const { id } = useParams();
    const [candidates, setCandidates] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchStatus();
        const interval = setInterval(fetchStatus, 30000); // Poll every 30s
        return () => clearInterval(interval);
    }, []);

    const fetchStatus = async () => {
        try {
            const response = await api.get(`/jobs/${id}/status/`);
            setCandidates(response.data);
            setLoading(false);
        } catch (err) {
            console.error(err);
            setLoading(false);
        }
    };

    return (
        <div className="max-w-6xl mx-auto space-y-6">
            <div className="flex items-center space-x-2 text-sm text-gray-500">
                <Link to="/dashboard" className="hover:text-indigo-600 flex items-center">
                    <ChevronLeft className="w-4 h-4" />
                    Back to Dashboard
                </Link>
                <span>/</span>
                <span className="text-gray-900">Interview Status</span>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                <div className="p-6 border-b border-gray-100 flex justify-between items-center bg-gray-50">
                    <div>
                        <h1 className="text-xl font-bold text-gray-900">Candidate Status Board</h1>
                        <p className="text-sm text-gray-500">Real-time interview pipeline updates</p>
                    </div>
                    <button onClick={fetchStatus} className="p-2 text-gray-400 hover:text-indigo-600 hover:bg-white rounded-full transition-all">
                        <RefreshCw className="w-5 h-5" />
                    </button>
                </div>

                {loading ? (
                    <div className="p-12 flex justify-center">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                    </div>
                ) : candidates.length === 0 ? (
                    <div className="p-12 text-center text-gray-500">
                        No candidates found for this job. Upload candidates to get started.
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full text-left">
                            <thead className="bg-gray-50 text-gray-500 text-xs uppercase tracking-wider">
                                <tr>
                                    <th className="px-6 py-4 font-semibold">Candidate</th>
                                    <th className="px-6 py-4 font-semibold">Unique Interview Link</th>
                                    <th className="px-6 py-4 font-semibold">Status</th>
                                    <th className="px-6 py-4 font-semibold text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100 bg-white">
                                {candidates.map((c) => (
                                    <tr key={c.id} className="hover:bg-gray-50 transition-colors">
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="font-medium text-gray-900">{c.name}</div>
                                            <div className="text-xs text-gray-500">{c.email}</div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="flex items-center space-x-2">
                                                <input
                                                    readOnly
                                                    value={c.link}
                                                    className="text-xs bg-gray-50 border border-gray-200 text-gray-600 p-1.5 rounded w-64 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none select-all"
                                                />
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${c.status === 'COMPLETED' ? 'bg-green-100 text-green-800' :
                                                    c.status === 'IN_PROGRESS' ? 'bg-blue-100 text-blue-800' :
                                                        c.status === 'EXPIRED' ? 'bg-red-100 text-red-800' :
                                                            'bg-yellow-100 text-yellow-800'
                                                }`}>
                                                {c.status.replace('_', ' ')}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                            <Link to={`/candidate/${c.id}`} className="text-indigo-600 hover:text-indigo-900 hover:bg-indigo-50 px-3 py-1.5 rounded-md transition-colors inline-flex items-center">
                                                <Eye className="w-4 h-4 mr-1" /> View
                                            </Link>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
};

export default InterviewStatus;
