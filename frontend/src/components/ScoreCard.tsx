/**
 * Score Card Component
 * 
 * Displays overall score and breakdown with visual indicators
 * Uses Recharts for data visualization
 */

import {
  RadialBarChart,
  RadialBar,
  ResponsiveContainer,
  PolarAngleAxis,
} from 'recharts';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import type { ScoreBreakdown } from '../types/api';

interface ScoreCardProps {
  overallScore: number;
  scoreBreakdown: ScoreBreakdown;
}

const ScoreCard: React.FC<ScoreCardProps> = ({ overallScore, scoreBreakdown }) => {
  // Prepare data for radial chart
  const chartData = [
    {
      name: 'Overall',
      score: overallScore,
      fill: getScoreColor(overallScore),
    },
  ];

  // Prepare breakdown data
  const breakdownItems = [
    { label: 'Content Quality', value: scoreBreakdown.content_quality, key: 'content' },
    { label: 'Keyword Optimization', value: scoreBreakdown.keyword_optimization, key: 'keywords' },
    { label: 'Formatting', value: scoreBreakdown.formatting, key: 'format' },
    { label: 'Experience Relevance', value: scoreBreakdown.experience_relevance, key: 'experience' },
    { label: 'Skills Match', value: scoreBreakdown.skills_match, key: 'skills' },
    { label: 'ATS Compatibility', value: scoreBreakdown.ats_compatibility, key: 'ats' },
  ];

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Resume Score</h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Overall Score - Radial Chart */}
        <div className="flex flex-col items-center">
          <ResponsiveContainer width="100%" height={250}>
            <RadialBarChart
              cx="50%"
              cy="50%"
              innerRadius="60%"
              outerRadius="90%"
              data={chartData}
              startAngle={90}
              endAngle={-270}
            >
              <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
              <RadialBar
                background
                dataKey="score"
                cornerRadius={10}
                fill={chartData[0].fill}
              />
            </RadialBarChart>
          </ResponsiveContainer>
          
          <div className="text-center -mt-32 mb-20">
            <div className="text-5xl font-bold" style={{ color: getScoreColor(overallScore) }}>
              {overallScore}
            </div>
            <div className="text-gray-500 text-sm mt-1">out of 100</div>
            <div className="mt-2">
              <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold ${getScoreBadgeClass(overallScore)}`}>
                {getScoreLabel(overallScore)}
              </span>
            </div>
          </div>
        </div>

        {/* Score Breakdown */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Score Breakdown</h3>
          {breakdownItems.map((item) => (
            <div key={item.key} className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-gray-700">{item.label}</span>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold" style={{ color: getScoreColor(item.value) }}>
                    {item.value}
                  </span>
                  {getScoreIcon(item.value)}
                </div>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="h-2 rounded-full transition-all duration-500"
                  style={{
                    width: `${item.value}%`,
                    backgroundColor: getScoreColor(item.value),
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Score Interpretation */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <p className="text-sm text-gray-600">
          <strong>Score Interpretation:</strong> {getScoreInterpretation(overallScore)}
        </p>
      </div>
    </div>
  );
};

// ============================================================================
// Helper Functions
// ============================================================================

function getScoreColor(score: number): string {
  if (score >= 80) return '#10b981'; // green
  if (score >= 60) return '#f59e0b'; // amber
  if (score >= 40) return '#f97316'; // orange
  return '#ef4444'; // red
}

function getScoreLabel(score: number): string {
  if (score >= 80) return 'Excellent';
  if (score >= 60) return 'Good';
  if (score >= 40) return 'Fair';
  return 'Needs Improvement';
}

function getScoreBadgeClass(score: number): string {
  if (score >= 80) return 'bg-green-100 text-green-800';
  if (score >= 60) return 'bg-amber-100 text-amber-800';
  if (score >= 40) return 'bg-orange-100 text-orange-800';
  return 'bg-red-100 text-red-800';
}

function getScoreIcon(score: number): React.ReactElement {
  if (score >= 70) return <TrendingUp className="w-4 h-4 text-green-500" />;
  if (score >= 50) return <Minus className="w-4 h-4 text-amber-500" />;
  return <TrendingDown className="w-4 h-4 text-red-500" />;
}

function getScoreInterpretation(score: number): string {
  if (score >= 80) {
    return 'Your resume is in excellent shape! It demonstrates strong content, formatting, and ATS compatibility. Minor refinements could make it even better.';
  }
  if (score >= 60) {
    return 'Your resume is good but has room for improvement. Focus on the lower-scoring areas to enhance your chances with recruiters and ATS systems.';
  }
  if (score >= 40) {
    return 'Your resume needs significant improvements. Pay attention to content quality, keyword optimization, and formatting to increase your success rate.';
  }
  return 'Your resume requires major revisions. Consider restructuring content, improving formatting, and optimizing for ATS systems. Review the suggestions carefully.';
}

export default ScoreCard;

// Made with Bob
