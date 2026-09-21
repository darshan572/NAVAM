import React from 'react';

interface PriorityScoreProps {
  score: number;
  ciLower: number;
  ciUpper: number;
  className?: string;
}

export const PriorityScore: React.FC<PriorityScoreProps> = ({ score, ciLower, ciUpper, className }) => {
  return (
    <span className={`font-medium ${className || ''}`}>
      {score} (90% CI: {ciLower}–{ciUpper})
    </span>
  );
};
