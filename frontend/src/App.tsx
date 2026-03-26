import { Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import EvaluationTool from './pages/EvaluationTool';
import DatasetExplorer from './pages/DatasetExplorer';
import Analytics from './pages/Analytics';

export default function App() {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main style={{ marginLeft: '220px' }} className="flex-1 min-w-0">
        <div className="max-w-[1200px] mx-auto px-8 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/evaluate" element={<EvaluationTool />} />
            <Route path="/dataset" element={<DatasetExplorer />} />
            <Route path="/analytics" element={<Analytics />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}
