import React from 'react';
import './charts.css';

interface MarketHealthIndicatorProps {
  value: number; // 0-100
}

const MarketHealthIndicator: React.FC<MarketHealthIndicatorProps> = ({ value }) => {
  const getHealthColor = (val: number) => {
    if (val >= 80) return '#4ECDC4'; // Healthy
    if (val >= 60) return '#F7DC6F'; // Warning
    if (val >= 40) return '#FF8C42'; // Caution
    return '#FF6B6B'; // Critical
  };

  const getHealthStatus = (val: number) => {
    if (val >= 80) return 'Healthy';
    if (val >= 60) return 'Stable';
    if (val >= 40) return 'Unstable';
    return 'Critical';
  };

  const radius = 50;
  const strokeWidth = 10;
  const normalizedRadius = radius - strokeWidth / 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset = circumference - (value / 100) * circumference;

  return (
    <div className="market-health-indicator">
      <svg height={radius * 2} width={radius * 2}>
        <circle
          stroke="#e0e0e0"
          fill="transparent"
          strokeWidth={strokeWidth}
          r={normalizedRadius}
          cx={radius}
          cy={radius}
        />
        <circle
          stroke={getHealthColor(value)}
          fill="transparent"
          strokeWidth={strokeWidth}
          strokeDasharray={circumference + ' ' + circumference}
          style={{ strokeDashoffset, transition: 'stroke-dashoffset 0.5s ease' }}
          strokeLinecap="round"
          transform={`rotate(-90 ${radius} ${radius})`}
          r={normalizedRadius}
          cx={radius}
          cy={radius}
        />
        <text
          x="50%"
          y="50%"
          dy=".3em"
          textAnchor="middle"
          className="health-value"
          style={{ fontSize: '20px', fontWeight: 'bold', fill: getHealthColor(value) }}
        >
          {value}%
        </text>
      </svg>
      <div className="health-status" style={{ color: getHealthColor(value) }}>
        {getHealthStatus(value)}
      </div>
    </div>
  );
};

export default MarketHealthIndicator;