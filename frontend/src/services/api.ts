/**
 * API Service
 * 
 * Centralized service for all backend API communications
 * Uses axios for HTTP requests with proper error handling
 */

import axios, { AxiosError } from 'axios';
import type {
  AnalysisRequest,
  AnalysisResponse,
  UploadResponse,
  HealthResponse,
  ErrorResponse,
} from '../types/api';

// ============================================================================
// Configuration
// ============================================================================

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_PREFIX = '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes for AI analysis
  headers: {
    'Content-Type': 'application/json',
  },
});

// ============================================================================
// Error Handling
// ============================================================================

/**
 * Extract error message from API response
 */
const getErrorMessage = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ErrorResponse>;
    
    if (axiosError.response?.data?.detail) {
      return axiosError.response.data.detail;
    }
    
    if (axiosError.message) {
      return axiosError.message;
    }
  }
  
  if (error instanceof Error) {
    return error.message;
  }
  
  return 'An unexpected error occurred';
};

// ============================================================================
// API Methods
// ============================================================================

/**
 * Health Check
 * Check if the backend is running and which providers are available
 */
export const checkHealth = async (): Promise<HealthResponse> => {
  try {
    const response = await api.get<HealthResponse>(`${API_PREFIX}/health`);
    return response.data;
  } catch (error) {
    throw new Error(`Health check failed: ${getErrorMessage(error)}`);
  }
};

/**
 * Upload Resume File
 * Upload a PDF or DOCX file to the backend
 */
export const uploadResume = async (file: File): Promise<UploadResponse> => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post<UploadResponse>(`${API_PREFIX}/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  } catch (error) {
    throw new Error(`Upload failed: ${getErrorMessage(error)}`);
  }
};

/**
 * Analyze Resume
 * Send resume for AI-powered analysis
 */
export const analyzeResume = async (
  request: AnalysisRequest
): Promise<AnalysisResponse> => {
  try {
    const response = await api.post<AnalysisResponse>(`${API_PREFIX}/analyze`, request);
    return response.data;
  } catch (error) {
    throw new Error(`Analysis failed: ${getErrorMessage(error)}`);
  }
};

/**
 * Get Provider Status
 * Check which AI providers are available
 */
export const getProviderStatus = async (): Promise<HealthResponse['providers']> => {
  try {
    const health = await checkHealth();
    return health.providers;
  } catch (error) {
    throw new Error(`Failed to get provider status: ${getErrorMessage(error)}`);
  }
};

// ============================================================================
// Convenience Methods
// ============================================================================

/**
 * Upload and Analyze
 * Combined method to upload a file and immediately analyze it
 */
export const uploadAndAnalyze = async (
  file: File,
  jobDescription?: string,
  provider?: 'openai' | 'anthropic' | 'ollama'
): Promise<AnalysisResponse> => {
  try {
    // Send file directly to analyze endpoint with multipart/form-data
    const formData = new FormData();
    formData.append('file', file);
    
    if (jobDescription) {
      formData.append('job_description', jobDescription);
    }
    
    if (provider) {
      formData.append('provider', provider);
    }
    
    // Add default options
    formData.append('include_ats_check', 'true');
    formData.append('include_keyword_analysis', 'true');
    formData.append('include_suggestions', 'true');

    const response = await api.post<AnalysisResponse>(
      `${API_PREFIX}/analyze`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    
    return response.data;
  } catch (error) {
    throw new Error(`Upload and analyze failed: ${getErrorMessage(error)}`);
  }
};

/**
 * Analyze Text
 * Analyze resume text directly without file upload
 */
export const analyzeText = async (
  resumeText: string,
  jobDescription?: string,
  provider?: 'openai' | 'anthropic' | 'ollama'
): Promise<AnalysisResponse> => {
  try {
    const analysisRequest: AnalysisRequest = {
      resume_text: resumeText,
      job_description: jobDescription,
      provider: provider,
    };

    const analysisResult = await analyzeResume(analysisRequest);
    return analysisResult;
  } catch (error) {
    throw new Error(`Text analysis failed: ${getErrorMessage(error)}`);
  }
};

// ============================================================================
// Export
// ============================================================================

export default {
  checkHealth,
  uploadResume,
  analyzeResume,
  getProviderStatus,
  uploadAndAnalyze,
  analyzeText,
};

// Made with Bob
