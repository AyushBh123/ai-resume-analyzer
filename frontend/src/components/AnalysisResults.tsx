/**
 * Analysis Results Component
 * 
 * Main component displaying complete resume analysis results
 * Includes scores, suggestions, keywords, and strengths/weaknesses
 */

import React from 'react';
import { CheckCircle, XCircle, Tag, TrendingUp, TrendingDown } from 'lucide-react';
import ScoreCard from './ScoreCard';
import SuggestionsList from './SuggestionsList';
import type { AnalysisResponse } from '../types/api';

interface AnalysisResultsProps {
  analysis: AnalysisResponse;
}

const AnalysisResults: React.FC<AnalysisResultsProps> = ({ analysis }) => {
  return (
    <div className="space-y-6">
      {/* Score Card */}
      <ScoreCard
        overallScore={analysis.overall_score}
        scoreBreakdown={analysis.score_breakdown}
      />

      {/* Strengths and Weaknesses */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Strengths */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
            <TrendingUp className="w-6 h-6 text-green-500" />
            Strengths
          </h3>
          {analysis.strengths.length > 0 ? (
            <ul className="space-y-2">
              {analysis.strengths.map((strength, index) => (
                <li key={index} className="flex items-start gap-2">
                  <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700">{strength}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500 italic">No specific strengths identified.</p>
          )}
        </div>

        {/* Weaknesses */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
            <TrendingDown className="w-6 h-6 text-red-500" />
            Areas for Improvement
          </h3>
          {analysis.weaknesses.length > 0 ? (
            <ul className="space-y-2">
              {analysis.weaknesses.map((weakness, index) => (
                <li key={index} className="flex items-start gap-2">
                  <XCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700">{weakness}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500 italic">No specific weaknesses identified.</p>
          )}
        </div>
      </div>

      {/* Keywords Analysis */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
          <Tag className="w-6 h-6 text-blue-500" />
          Keywords Analysis
        </h3>
        
        {analysis.keywords_found.length === 0 && analysis.keywords_missing.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-600 mb-2">
              <strong>No job description provided</strong>
            </p>
            <p className="text-gray-500 text-sm">
              Upload a job description to see keyword matching analysis and improve your resume's relevance to specific positions.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Found Keywords */}
            <div>
              <h4 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-500" />
                Keywords Found ({analysis.keywords_found.length})
              </h4>
              {analysis.keywords_found.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {analysis.keywords_found.map((keyword, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 italic text-sm">No matching keywords found in your resume.</p>
              )}
            </div>

            {/* Missing Keywords */}
            <div>
              <h4 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
                <XCircle className="w-5 h-5 text-red-500" />
                Missing Keywords ({analysis.keywords_missing.length})
              </h4>
              {analysis.keywords_missing.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {analysis.keywords_missing.map((keyword, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-medium"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 italic text-sm">Great! All important keywords are present in your resume.</p>
              )}
            </div>
          </div>
        )}
      </div>

      {/* ATS Compatibility */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4">ATS Compatibility</h3>
        
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">ATS Score</span>
            <span className="text-2xl font-bold" style={{ color: getATSColor(analysis.ats_compatibility.score) }}>
              {analysis.ats_compatibility.score}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="h-3 rounded-full transition-all duration-500"
              style={{
                width: `${analysis.ats_compatibility.score}%`,
                backgroundColor: getATSColor(analysis.ats_compatibility.score),
              }}
            />
          </div>
        </div>

        {analysis.ats_compatibility.issues.length > 0 && (
          <div className="mb-4">
            <h4 className="font-semibold text-gray-700 mb-2">Issues Detected:</h4>
            <ul className="space-y-1">
              {analysis.ats_compatibility.issues.map((issue, index) => (
                <li key={index} className="flex items-start gap-2 text-sm text-gray-600">
                  <XCircle className="w-4 h-4 text-red-500 flex-shrink-0 mt-0.5" />
                  {issue}
                </li>
              ))}
            </ul>
          </div>
        )}

        {analysis.ats_compatibility.recommendations.length > 0 && (
          <div>
            <h4 className="font-semibold text-gray-700 mb-2">Recommendations:</h4>
            <ul className="space-y-1">
              {analysis.ats_compatibility.recommendations.map((rec, index) => (
                <li key={index} className="flex items-start gap-2 text-sm text-gray-600">
                  <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
                  {rec}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Job Match (if available) */}
      {analysis.job_match && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4">Job Match Analysis</h3>
          
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">Overall Match</span>
              <span className="text-2xl font-bold" style={{ color: getATSColor(analysis.job_match.overall_match) }}>
                {analysis.job_match.overall_match}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="h-3 rounded-full transition-all duration-500"
                style={{
                  width: `${analysis.job_match.overall_match}%`,
                  backgroundColor: getATSColor(analysis.job_match.overall_match),
                }}
              />
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-4">
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Matched Skills:</h4>
              <div className="flex flex-wrap gap-2">
                {analysis.job_match.matched_skills.map((skill, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs font-medium"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Missing Skills:</h4>
              <div className="flex flex-wrap gap-2">
                {analysis.job_match.missing_skills.map((skill, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 bg-red-100 text-red-800 rounded text-xs font-medium"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {analysis.job_match.recommendations.length > 0 && (
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Recommendations:</h4>
              <ul className="space-y-1">
                {analysis.job_match.recommendations.map((rec, index) => (
                  <li key={index} className="flex items-start gap-2 text-sm text-gray-600">
                    <CheckCircle className="w-4 h-4 text-blue-500 flex-shrink-0 mt-0.5" />
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Suggestions */}
      <SuggestionsList suggestions={analysis.suggestions} />

      {/* Analysis Metadata */}
      <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-600">
        <p>
          <strong>Analysis completed:</strong> {new Date(analysis.analysis_timestamp).toLocaleString()}
        </p>
        <p>
          <strong>AI Provider:</strong> {analysis.provider_used}
        </p>
      </div>
    </div>
  );
};

// ============================================================================
// Helper Functions
// ============================================================================

function getATSColor(score: number): string {
  if (score >= 80) return '#10b981'; // green
  if (score >= 60) return '#f59e0b'; // amber
  if (score >= 40) return '#f97316'; // orange
  return '#ef4444'; // red
}

export default AnalysisResults;

// Made with Bob
