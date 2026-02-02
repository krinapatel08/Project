import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api';
import { Briefcase, Users, FileText, ChevronRight, Plus } from 'lucide-react';

function Dashboard() {
    const [jobs, setJobs] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.get('/jobs/')
            .then(res => {
                setJobs(res.data);
                setLoading(false);
            })
            .catch(err => {
                console.error("Error fetching jobs", err);
                setLoading(false);
            });
    }, []);

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            </div>
        );
    }

    // Dynamic stats from real data
    const activeJobs = jobs.length;
    const totalCandidates = jobs.reduce((acc, job) => acc + (job.candidates_count || 0), 0);
    const completedInterviews = jobs.reduce((acc, job) => acc + (job.completed_interviews_count || 0), 0);

    return (
        <div className="space-y-6">
            <header className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
                    <p className="text-gray-500">Overview of your recruitment pipeline</p>
                </div>
                <Link
                    to="/create-job"
                    className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg flex items-center shadow-md transition-all hover:shadow-lg"
                >
                    <Plus className="w-5 h-5 mr-1" />
                    Create New Job
                </Link>
            </header>

            {/* Stats Row */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center">
                    <div className="bg-blue-100 p-3 rounded-full mr-4">
                        <Briefcase className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                        <p className="text-sm text-gray-500 font-medium">Active Jobs</p>
                        <p className="text-2xl font-bold text-gray-900">{activeJobs}</p>
                    </div>
                </div>
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center">
                    <div className="bg-green-100 p-3 rounded-full mr-4">
                        <Users className="w-6 h-6 text-green-600" />
                    </div>
                    <div>
                        <p className="text-sm text-gray-500 font-medium">Total Candidates</p>
                        <p className="text-2xl font-bold text-gray-900">{totalCandidates}</p>
                    </div>
                </div>
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center">
                    <div className="bg-purple-100 p-3 rounded-full mr-4">
                        <FileText className="w-6 h-6 text-purple-600" />
                    </div>
                    <div>
                        <p className="text-sm text-gray-500 font-medium">Interviews Completed</p>
                        <p className="text-2xl font-bold text-gray-900">{completedInterviews}</p>
                    </div>
                </div>
            </div>

            {/* Job List */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-100">
                    <h3 className="text-lg font-semibold text-gray-900">Recent Job Postings</h3>
                </div>

                {jobs.length === 0 ? (
                    <div className="p-8 text-center text-gray-500">
                        No jobs found. Create your first job posting to get started.
                    </div>
                ) : (
                    <div className="divide-y divide-gray-100">
                        {jobs.map(job => (
                            <div key={job.id} className="p-6 hover:bg-gray-50 transition-colors flex flex-col md:flex-row md:items-center justify-between group">
                                <div className="mb-4 md:mb-0">
                                    <h4 className="text-lg font-bold text-indigo-900 mb-1">{job.title}</h4>
                                    <p className="text-sm text-gray-500 line-clamp-2 md:line-clamp-1 max-w-md">
                                        {job.description}
                                    </p>
                                    <div className="mt-2 flex space-x-2">
                                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                                            {job.experience_level}
                                        </span>
                                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-50 text-indigo-700">
                                            Created: {new Date(job.created_at).toLocaleDateString()}
                                        </span>
                                    </div>
                                </div>

                                <div className="flex space-x-3">
                                    <Link
                                        to={`/job/${job.id}/upload`}
                                        className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                                    >
                                        Add Candidates
                                    </Link>
                                    <Link
                                        to={`/job/${job.id}/status`}
                                        className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                                    >
                                        Status
                                    </Link>
                                    <Link
                                        to={`/job/${job.id}/ranking`}
                                        className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 shadow-sm"
                                    >
                                        Rankings
                                    </Link>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

export default Dashboard;
