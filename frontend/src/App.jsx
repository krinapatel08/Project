import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate, useLocation } from 'react-router-dom';
import { LayoutDashboard, PlusCircle, LogOut } from 'lucide-react';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import CreateJob from './pages/CreateJob';
import UploadCandidates from './pages/UploadCandidates';
import InterviewStatus from './pages/InterviewStatus';
import RankingView from './pages/RankingView';
import CandidateDetail from './pages/CandidateDetail';

function NavBar({ logout }) {
  const location = useLocation();

  const isActive = (path) => location.pathname === path ? "text-indigo-600 bg-indigo-50" : "text-gray-600 hover:text-indigo-600 hover:bg-gray-50";

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <span className="text-xl font-bold text-indigo-600">SmartHR</span>
            </div>
            <div className="hidden sm:ml-6 sm:flex sm:space-x-4">
              <Link to="/dashboard" className={`px-3 py-2 rounded-md text-sm font-medium flex items-center ${isActive('/dashboard')}`}>
                <LayoutDashboard className="w-4 h-4 mr-2" />
                Dashboard
              </Link>
              <Link to="/create-job" className={`px-3 py-2 rounded-md text-sm font-medium flex items-center ${isActive('/create-job')}`}>
                <PlusCircle className="w-4 h-4 mr-2" />
                Create Job
              </Link>
            </div>
          </div>
          <div className="flex items-center">
            <button
              onClick={logout}
              className="ml-4 px-3 py-2 rounded-md text-sm font-medium text-gray-500 hover:text-red-600 hover:bg-red-50 transition-colors flex items-center"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}

function App() {
  const [isAuthenticated, setIsAuthenticated] = React.useState(!!localStorage.getItem('isLoggedIn'));

  const logout = () => {
    localStorage.removeItem('isLoggedIn');
    setIsAuthenticated(false);
  };

  return (
    <Router>
      <div className="min-h-screen bg-gray-50 font-sans">
        {isAuthenticated && <NavBar logout={logout} />}

        <main className={isAuthenticated ? "max-w-7xl mx-auto py-6 sm:px-6 lg:px-8" : ""}>
          <Routes>
            <Route path="/login" element={<Login onLogin={() => setIsAuthenticated(true)} />} />
            <Route path="/dashboard" element={isAuthenticated ? <Dashboard /> : <Navigate to="/login" />} />
            <Route path="/create-job" element={isAuthenticated ? <CreateJob /> : <Navigate to="/login" />} />
            <Route path="/job/:id/upload" element={isAuthenticated ? <UploadCandidates /> : <Navigate to="/login" />} />
            <Route path="/job/:id/status" element={isAuthenticated ? <InterviewStatus /> : <Navigate to="/login" />} />
            <Route path="/job/:id/ranking" element={isAuthenticated ? <RankingView /> : <Navigate to="/login" />} />
            <Route path="/candidate/:id" element={isAuthenticated ? <CandidateDetail /> : <Navigate to="/login" />} />
            <Route path="/" element={<Navigate to="/dashboard" />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
