/**
 * API Type Definitions
 * 
 * TypeScript interfaces matching the backend Pydantic models
 * for type-safe API communication
 */

// ============================================================================
// Resume Data Types
// ============================================================================

export interface ContactInfo {
  name?: string;
  email?: string;
  phone?: string;
  location?: string;
  linkedin?: string;
  github?: string;
  portfolio?: string;
}

export interface WorkExperience {
  company: string;
  position: string;
  start_date?: string;
  end_date?: string;
  location?: string;
  description?: string;
  achievements?: string[];
}

export interface Education {
  institution: string;
  degree: string;
  field_of_study?: string;
  start_date?: string;
  end_date?: string;
  gpa?: string;
  location?: string;
}

export interface Certification {
  name: string;
  issuer: string;
  date?: string;
  expiry_date?: string;
  credential_id?: string;
}

export interface ResumeData {
  contact_info: ContactInfo;
  summary?: string;
  work_experience: WorkExperience[];
  education: Education[];
  skills: {
    technical?: string[];
    soft?: string[];
    languages?: string[];
    tools?: string[];
  };
  certifications?: Certification[];
  projects?: Array<{
    name: string;
    description?: string;
    technologies?: string[];
    url?: string;
  }>;
}

// ============================================================================
// Analysis Types
// ============================================================================

export interface ScoreBreakdown {
  content_quality: number;
  keyword_optimization: number;
  formatting: number;
  experience_relevance: number;
  skills_match: number;
  ats_compatibility: number;
}

export interface Suggestion {
  category: string;
  priority: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  impact: string;
}

export interface ATSCompatibility {
  score: number;
  issues: string[];
  recommendations: string[];
}

export interface JobMatch {
  overall_match: number;
  matched_skills: string[];
  missing_skills: string[];
  keyword_overlap: number;
  experience_alignment: number;
  recommendations: string[];
}

export interface AnalysisResponse {
  overall_score: number;
  score_breakdown: ScoreBreakdown;
  resume_data: ResumeData;
  suggestions: Suggestion[];
  ats_compatibility: ATSCompatibility;
  job_match?: JobMatch;
  strengths: string[];
  weaknesses: string[];
  keywords_found: string[];
  keywords_missing: string[];
  analysis_timestamp: string;
  provider_used: string;
}

// ============================================================================
// API Request/Response Types
// ============================================================================

export interface UploadResponse {
  file_id: string;
  filename: string;
  file_size: number;
  file_type: string;
  upload_timestamp: string;
}

export interface AnalysisRequest {
  file_id?: string;
  resume_text?: string;
  job_description?: string;
  provider?: 'openai' | 'anthropic' | 'ollama';
  model?: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  providers: {
    [key: string]: {
      available: boolean;
      models?: string[];
    };
  };
}

export interface ErrorResponse {
  detail: string;
  error_code?: string;
}

// ============================================================================
// UI State Types
// ============================================================================

export interface AnalysisState {
  isAnalyzing: boolean;
  result: AnalysisResponse | null;
  error: string | null;
}

export interface UploadState {
  isUploading: boolean;
  uploadedFile: UploadResponse | null;
  error: string | null;
}

// Made with Bob
