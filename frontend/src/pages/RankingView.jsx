import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import api from '../api';
import { AlertCircle } from 'lucide-react';

const RankingView = () => {
    const { id } = useParams();
    const [rankings, setRankings] = useState([]);

    useEffect(() => {
        fetchRankings();
    }, []);

    const fetchRankings = async () => {
        try {
            const response = await api.get(`/jobs/${id}/ranking/`);
            setRankings(response.data);
        } catch (err) {
            console.error(err);
        }
    };

    return (
        <div className="bg-white rounded-lg shadow border overflow-hidden">
            <div className="p-6 border-b">
                <h1 className="text-xl font-bold">Candidate Rankings</h1>
                <p className="text-sm text-gray-500">Sorted by Overall Score (High → Low)</p>
            </div>
            <table className="w-full text-left">
                <thead className="bg-gray-50 text-gray-500 text-sm">
                    <tr>
                        <th className="p-4 font-medium">Rank</th>
                        <th className="p-4 font-medium">Candidate</th>
                        <th className="p-4 font-medium">Score</th>
                        <th className="p-4 font-medium text-center">Flags</th>
                    </tr>
                </thead>
                <tbody className="divide-y">
                    {rankings.map((r) => (
                        <tr key={r.rank} className={r.cheating ? 'bg-red-50' : ''}>
                            <td className="p-4 font-bold text-gray-400">#{r.rank}</td>
                            <td className="p-4">
                                <div className="font-medium">{r.name}</div>
                                <div className="text-xs text-gray-400">{r.email}</div>
                            </td>
                            <td className="p-4 font-bold text-indigo-600">{r.score.toFixed(1)}%</td>
                            <td className="p-4">
                                <div className="flex justify-center">
                                    {r.cheating && (
                                        <div className="flex items-center text-red-600 text-xs font-bold">
                                            <AlertCircle className="w-4 h-4 mr-1" /> SUSPICIOUS
                                        </div>
                                    )}
                                </div>
                            </td>
                        </tr>
                    ))}
                    {rankings.length === 0 && (
                        <tr>
                            <td colSpan="4" className="p-8 text-center text-gray-400">No completed interviews yet.</td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>
    );
};

export default RankingView;
