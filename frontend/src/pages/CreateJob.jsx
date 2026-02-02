import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../api';
import { ChevronLeft, Save } from 'lucide-react';

const CreateJob = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        title: '',
        description: '',
        required_skills: '',
        experience_level: 'Entry Level',
        oral_question_count: 5,
        coding_question_count: 2,
        thinking_time: 1,
        recording_time: 3,
        coding_time: 60,
    });
    const [loading, setLoading] = useState(false);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData({ ...formData, [name]: value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            await api.post('/jobs/', formData);
            navigate('/dashboard');
        } catch (err) {
            console.error(err);
            alert('Error creating job');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            <div className="flex items-center space-x-2 text-sm text-gray-500">
                <Link to="/dashboard" className="hover:text-indigo-600 flex items-center">
                    <ChevronLeft className="w-4 h-4" />
                    Back to Dashboard
                </Link>
                <span>/</span>
                <span className="text-gray-900">Create Job</span>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8">
                <header className="mb-8 border-b border-gray-100 pb-4">
                    <h1 className="text-2xl font-bold text-gray-900">Create New Job Posting</h1>
                    <p className="text-gray-500 mt-1">Define role details and interview configuration.</p>
                </header>

                <form onSubmit={handleSubmit} className="space-y-8">
                    {/* Role Details */}
                    <section className="space-y-6">
                        <h2 className="text-lg font-semibold text-gray-800 flex items-center">
                            <span className="bg-indigo-100 text-indigo-600 text-xs px-2 py-1 rounded uppercase tracking-wide mr-2">Step 1</span>
                            Role Details
                        </h2>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="col-span-2">
                                <label className="block text-sm font-medium text-gray-700 mb-1">Job Title</label>
                                <input
                                    type="text"
                                    name="title"
                                    className="w-full border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                                    placeholder="e.g. Senior Frontend Engineer"
                                    onChange={handleChange}
                                    required
                                />
                            </div>

                            <div className="col-span-2">
                                <label className="block text-sm font-medium text-gray-700 mb-1">Job Description</label>
                                <textarea
                                    name="description"
                                    rows={4}
                                    className="w-full border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                                    placeholder="Enter detailed job description..."
                                    onChange={handleChange}
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Required Skills (Comma separated)</label>
                                <input
                                    type="text"
                                    name="required_skills"
                                    className="w-full border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                                    placeholder="e.g. React, Node.js, TypeScript"
                                    onChange={handleChange}
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Experience Level</label>
                                <select
                                    name="experience_level"
                                    className="w-full border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                                    onChange={handleChange}
                                    value={formData.experience_level}
                                >
                                    <option>Entry Level</option>
                                    <option>Mid Level</option>
                                    <option>Senior Level</option>
                                    <option>Lead / Manager</option>
                                </select>
                            </div>
                        </div>
                    </section>

                    {/* Config */}
                    <section className="space-y-6 pt-6 border-t border-gray-100">
                        <h2 className="text-lg font-semibold text-gray-800 flex items-center">
                            <span className="bg-indigo-100 text-indigo-600 text-xs px-2 py-1 rounded uppercase tracking-wide mr-2">Step 2</span>
                            Interview Configuration
                        </h2>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Oral Questions</label>
                                <input
                                    type="number"
                                    name="oral_question_count"
                                    value={formData.oral_question_count}
                                    className="w-full border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                                    onChange={handleChange}
                                />
                                <span className="text-xs text-gray-400">Number of AI generated questions</span>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Coding Questions</label>
                                <input
                                    type="number"
                                    name="coding_question_count"
                                    value={formData.coding_question_count}
                                    className="w-full border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                                    onChange={handleChange}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Coding Time (Min)</label>
                                <input
                                    type="number"
                                    name="coding_time"
                                    value={formData.coding_time}
                                    className="w-full border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                                    onChange={handleChange}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Thinking Time (Min)</label>
                                <input
                                    type="number"
                                    name="thinking_time"
                                    value={formData.thinking_time}
                                    className="w-full border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                                    onChange={handleChange}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Recording Time (Min)</label>
                                <input
                                    type="number"
                                    name="recording_time"
                                    value={formData.recording_time}
                                    className="w-full border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                                    onChange={handleChange}
                                />
                            </div>

                        </div>
                    </section>

                    <div className="pt-6 border-t border-gray-100">
                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-4 rounded-lg transition-colors flex items-center justify-center shadow-md hover:shadow-lg"
                        >
                            <Save className="w-5 h-5 mr-2" />
                            {loading ? 'Creating Job...' : 'Publish Job Posting'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default CreateJob;
