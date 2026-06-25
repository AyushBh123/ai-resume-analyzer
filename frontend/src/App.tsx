/**
 * Main App Component
 * 
 * Root component orchestrating the entire resume analysis workflow
 * Manages state for file upload, analysis, and results display
 */

import { useState, useEffect } from 'react';
import { FileText, Settings, Sparkles } from 'lucide-react';
import FileUpload from './components/FileUpload';
import AnalysisResults from './components/AnalysisResults';
import { uploadAndAnalyze, checkHealth } from './services/api';
import type { AnalysisResponse, HealthResponse } from './types/api';

function App() {
  // State management
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState<string>('');
  const [selectedProvider, setSelectedProvider] = useState<'openai' | 'anthropic' | 'ollama'>('openai');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [availableProviders, setAvailableProviders] = useState<HealthResponse['providers'] | null>(null);
  const [showSettings, setShowSettings] = useState(false);

  // Check backend health and available providers on mount
  useEffect(() => {
    const checkBackendHealth = async () => {
      try {
        const health = await checkHealth();
        setAvailableProviders(health.providers);
        
        // Auto-select first available provider
        if (health.providers.openai?.available) {
          setSelectedProvider('openai');
        } else if (health.providers.anthropic?.available) {
          setSelectedProvider('anthropic');
        } else if (health.providers.ollama?.available) {
          setSelectedProvider('ollama');
        }
      } catch (err) {
        console.error('Backend health check failed:', err);
        setError('Unable to connect to backend. Please ensure the server is running.');
      }
    };

    checkBackendHealth();
  }, []);

  // Handle file selection
  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    setError(null);
    setAnalysisResult(null);
  };

  // Handle analysis
  const handleAnalyze = async () => {
    if (!selectedFile) {
      setError('Please select a resume file first.');
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      const result = await uploadAndAnalyze(
        selectedFile,
        jobDescription || undefined,
        selectedProvider
      );
      setAnalysisResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Reset to start over
  const handleReset = () => {
    setSelectedFile(null);
    setJobDescription('');
    setAnalysisResult(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-2 rounded-lg">
                <FileText className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">AI Resume Analyzer</h1>
                <p className="text-sm text-gray-500">Powered by AI • Get instant feedback</p>
              </div>
            </div>
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              title="Settings"
            >
              <Settings className="w-6 h-6 text-gray-600" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Settings Panel */}
        {showSettings && (
          <div className="mb-6 bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Settings</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  AI Provider
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {availableProviders && Object.entries(availableProviders).map(([key, value]) => (
                    <button
                      key={key}
                      onClick={() => setSelectedProvider(key as any)}
                      disabled={!value.available}
                      className={`
                        p-3 rounded-lg border-2 transition-all
                        ${selectedProvider === key
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                        }
                        ${!value.available ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
                      `}
                    >
                      <div className="font-semibold text-gray-800 capitalize">{key}</div>
                      <div className="text-xs text-gray-500 mt-1">
                        {value.available ? '✓ Available' : '✗ Not configured'}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {!analysisResult ? (
          /* Upload and Analysis Form */
          <div className="space-y-6">
            {/* File Upload */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">Upload Your Resume</h2>
              <FileUpload
                onFileSelect={handleFileSelect}
                isUploading={isAnalyzing}
                error={error}
              />
            </div>

            {/* Job Description (Optional) */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">
                Job Description (Optional)
              </h2>
              <p className="text-sm text-gray-600 mb-4">
                Paste the job description to get tailored suggestions and match analysis.
              </p>
              <textarea
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Paste job description here..."
                className="w-full h-40 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                disabled={isAnalyzing}
              />
            </div>

            {/* Analyze Button */}
            <div className="flex justify-center">
              <button
                onClick={handleAnalyze}
                disabled={!selectedFile || isAnalyzing}
                className={`
                  px-8 py-4 rounded-lg font-semibold text-lg
                  flex items-center gap-3 transition-all transform
                  ${!selectedFile || isAnalyzing
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:from-blue-600 hover:to-purple-700 hover:scale-105 shadow-lg'
                  }
                `}
              >
                {isAnalyzing ? (
                  <>
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-6 h-6" />
                    Analyze Resume
                  </>
                )}
              </button>
            </div>
          </div>
        ) : (
          /* Analysis Results */
          <div className="space-y-6">
            {/* Action Buttons */}
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-800">Analysis Results</h2>
              <button
                onClick={handleReset}
                className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                Analyze Another Resume
              </button>
            </div>

            {/* Results Display */}
            <AnalysisResults analysis={analysisResult} />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-500">
            AI Resume Analyzer • Built with React, TypeScript, and FastAPI
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;

// Made with Bob
