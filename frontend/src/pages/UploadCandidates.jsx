import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api';

const UploadCandidates = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [manualData, setManualData] = useState({ name: '', email: '' });
    const [resumeFile, setResumeFile] = useState(null);
    const [bulkFile, setBulkFile] = useState(null);
    const [uploading, setUploading] = useState(false);

    const handleManualSubmit = async (e) => {
        e.preventDefault();
        setUploading(true);
        const formData = new FormData();
        formData.append('name', manualData.name);
        formData.append('email', manualData.email);
        if (resumeFile) {
            formData.append('resume_file', resumeFile);
        }

        try {
            await api.post(`/jobs/${id}/upload_candidates/`, formData);
            alert('Candidate added successfully!');
            navigate(`/job/${id}/status`);
        } catch (err) {
            alert('Error adding candidate');
        } finally {
            setUploading(false);
        }
    };

    const handleBulkSubmit = async (e) => {
        e.preventDefault();
        setUploading(true);
        const formData = new FormData();
        formData.append('file', bulkFile);

        try {
            const response = await api.post(`/jobs/${id}/upload_candidates/`, formData);
            alert(`Upload complete! Success: ${response.data.success.length}, Errors: ${response.data.errors.length}`);
            navigate(`/job/${id}/status`);
        } catch (err) {
            alert('Error uploading bulk file');
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto space-y-8">
            <h1 className="text-2xl font-bold">Add Candidates to Job</h1>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="bg-white p-6 rounded-lg shadow-sm border">
                    <h2 className="text-lg font-bold mb-4">Manual Add</h2>
                    <form onSubmit={handleManualSubmit} className="space-y-4">
                        <input
                            type="text"
                            placeholder="Full Name"
                            className="w-full border p-2 rounded"
                            onChange={(e) => setManualData({ ...manualData, name: e.target.value })}
                            required
                        />
                        <input
                            type="email"
                            placeholder="Email Address"
                            className="w-full border p-2 rounded"
                            onChange={(e) => setManualData({ ...manualData, email: e.target.value })}
                            required
                        />
                        <div>
                            <label className="text-sm text-gray-500">Resume PDF</label>
                            <input
                                type="file"
                                className="w-full border p-2 rounded"
                                onChange={(e) => setResumeFile(e.target.files[0])}
                            />
                        </div>
                        <button
                            disabled={uploading}
                            className="w-full bg-indigo-600 text-white p-2 rounded hover:bg-indigo-700 disabled:bg-gray-400"
                        >
                            {uploading ? 'Uploading...' : 'Add Candidate'}
                        </button>
                    </form>
                </div>

                <div className="bg-white p-6 rounded-lg shadow-sm border">
                    <h2 className="text-lg font-bold mb-4">Bulk Upload (CSV)</h2>
                    <form onSubmit={handleBulkSubmit} className="space-y-4">
                        <div>
                            <label className="text-sm text-gray-500">CSV File (Candidate Name, Candidate Email, Resume Link columns)</label>
                            <input
                                type="file"
                                className="w-full border p-2 rounded"
                                onChange={(e) => setBulkFile(e.target.files[0])}
                                required
                            />
                        </div>
                        <button
                            disabled={uploading}
                            className="w-full bg-green-600 text-white p-2 rounded hover:bg-green-700 disabled:bg-gray-400"
                        >
                            {uploading ? 'Uploading...' : 'Upload CSV'}
                        </button>
                        <p className="text-xs text-gray-400 mt-2">
                            Note: The CSV should have headers: <strong>Candidate Name</strong>, <strong>Candidate Email</strong>, and <strong>Resume Link</strong>.
                        </p>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default UploadCandidates;
