import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Dashboard from './pages/Dashboard';
import UploadPage from './pages/UploadPage';
import FileDetail from './pages/FileDetail';
import FullMap from './pages/FullMap';
import FeatureExplorer from './pages/FeatureExplorer';

export function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <div className="app-container">
          <Navbar />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/upload" element={<UploadPage />} />
              <Route path="/files/:id" element={<FileDetail />} />
              <Route path="/files/:id/map" element={<FullMap />} />
              <Route path="/files/:id/features" element={<FeatureExplorer />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
