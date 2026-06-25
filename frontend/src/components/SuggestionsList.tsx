/**
 * Suggestions List Component
 * 
 * Displays improvement suggestions categorized by priority
 * with expandable details
 */

import React, { useState } from 'react';
import { ChevronDown, ChevronUp, AlertCircle, Info, CheckCircle } from 'lucide-react';
import type { Suggestion } from '../types/api';

interface SuggestionsListProps {
  suggestions: Suggestion[];
}

const SuggestionsList: React.FC<SuggestionsListProps> = ({ suggestions }) => {
  const [expandedIds, setExpandedIds] = useState<Set<number>>(new Set());

  // Group suggestions by priority
  const groupedSuggestions = {
    high: suggestions.filter((s) => s.priority === 'high'),
    medium: suggestions.filter((s) => s.priority === 'medium'),
    low: suggestions.filter((s) => s.priority === 'low'),
  };

  const toggleExpand = (index: number) => {
    const newExpanded = new Set(expandedIds);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedIds(newExpanded);
  };

  const renderSuggestionGroup = (
    title: string,
    items: Suggestion[],
    priority: 'high' | 'medium' | 'low',
    startIndex: number
  ) => {
    if (items.length === 0) return null;

    const { icon: Icon, bgColor, borderColor, textColor } = getPriorityStyles(priority);

    return (
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
          <Icon className={`w-5 h-5 ${textColor}`} />
          {title}
          <span className={`ml-2 px-2 py-0.5 rounded-full text-xs font-medium ${bgColor} ${textColor}`}>
            {items.length}
          </span>
        </h3>
        <div className="space-y-3">
          {items.map((suggestion, idx) => {
            const globalIndex = startIndex + idx;
            const isExpanded = expandedIds.has(globalIndex);

            return (
              <div
                key={globalIndex}
                className={`border-l-4 ${borderColor} bg-white rounded-lg shadow-sm overflow-hidden transition-all`}
              >
                <button
                  onClick={() => toggleExpand(globalIndex)}
                  className="w-full p-4 text-left hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`px-2 py-0.5 rounded text-xs font-semibold ${bgColor} ${textColor}`}>
                          {suggestion.category}
                        </span>
                      </div>
                      <h4 className="font-semibold text-gray-800">{suggestion.title}</h4>
                      {!isExpanded && (
                        <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                          {suggestion.description}
                        </p>
                      )}
                    </div>
                    {isExpanded ? (
                      <ChevronUp className="w-5 h-5 text-gray-400 flex-shrink-0" />
                    ) : (
                      <ChevronDown className="w-5 h-5 text-gray-400 flex-shrink-0" />
                    )}
                  </div>
                </button>

                {isExpanded && (
                  <div className="px-4 pb-4 border-t border-gray-100">
                    <div className="mt-3 space-y-3">
                      <div>
                        <p className="text-sm font-medium text-gray-700 mb-1">Description:</p>
                        <p className="text-sm text-gray-600">{suggestion.description}</p>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-700 mb-1">Impact:</p>
                        <p className="text-sm text-gray-600">{suggestion.impact}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  if (suggestions.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="text-center py-8">
          <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-800 mb-2">
            Excellent Work!
          </h3>
          <p className="text-gray-600">
            Your resume looks great! No major improvements needed at this time.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Improvement Suggestions</h2>

      {/* Summary */}
      <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <div className="flex items-start gap-3">
          <Info className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm text-blue-800">
              We found <strong>{suggestions.length}</strong> suggestions to improve your resume.
              Focus on high-priority items first for maximum impact.
            </p>
          </div>
        </div>
      </div>

      {/* Grouped Suggestions */}
      {renderSuggestionGroup(
        'High Priority',
        groupedSuggestions.high,
        'high',
        0
      )}
      {renderSuggestionGroup(
        'Medium Priority',
        groupedSuggestions.medium,
        'medium',
        groupedSuggestions.high.length
      )}
      {renderSuggestionGroup(
        'Low Priority',
        groupedSuggestions.low,
        'low',
        groupedSuggestions.high.length + groupedSuggestions.medium.length
      )}
    </div>
  );
};

// ============================================================================
// Helper Functions
// ============================================================================

function getPriorityStyles(priority: 'high' | 'medium' | 'low') {
  switch (priority) {
    case 'high':
      return {
        icon: AlertCircle,
        bgColor: 'bg-red-100',
        borderColor: 'border-red-500',
        textColor: 'text-red-700',
      };
    case 'medium':
      return {
        icon: Info,
        bgColor: 'bg-amber-100',
        borderColor: 'border-amber-500',
        textColor: 'text-amber-700',
      };
    case 'low':
      return {
        icon: CheckCircle,
        bgColor: 'bg-blue-100',
        borderColor: 'border-blue-500',
        textColor: 'text-blue-700',
      };
  }
}

export default SuggestionsList;

// Made with Bob
