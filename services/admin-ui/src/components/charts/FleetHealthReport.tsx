import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import './charts.css';

interface CriticalIssue {
  shipId: string;
  shipName: string;
  severity: 'high' | 'critical';
  description: string;
  recommendedAction: string;
}

interface FleetHealthReport {
  totalShips: number;
  byStatus: {
    active: number;
    docked: number;
    maintenance: number;
    destroyed: number;
  };
  byCondition: {
    excellent: number;
    good: number;
    fair: number;
    poor: number;
    critical: number;
  };
  maintenanceNeeded: number;
  criticalIssues: CriticalIssue[];
}

interface FleetHealthReportProps {
  report: FleetHealthReport;
}

const FleetHealthReport: React.FC<FleetHealthReportProps> = ({ report }) => {
  const statusChartRef = useRef<SVGSVGElement>(null);
  const conditionChartRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (report && statusChartRef.current) {
      drawStatusChart();
    }
  }, [report]);

  useEffect(() => {
    if (report && conditionChartRef.current) {
      drawConditionChart();
    }
  }, [report]);

  const drawStatusChart = () => {
    const data = Object.entries(report.byStatus).map(([status, count]) => ({
      status,
      count
    }));

    // Clear previous chart
    d3.select(statusChartRef.current).selectAll('*').remove();

    const width = 300;
    const height = 300;
    const margin = 40;
    const radius = Math.min(width, height) / 2 - margin;

    const svg = d3.select(statusChartRef.current)
      .attr('width', width)
      .attr('height', height);

    const g = svg.append('g')
      .attr('transform', `translate(${width / 2}, ${height / 2})`);

    const color = d3.scaleOrdinal()
      .domain(['active', 'docked', 'maintenance', 'destroyed'])
      .range(['#4ECDC4', '#85C1E2', '#F7DC6F', '#FF6B6B']);

    const pie = d3.pie<any>()
      .value(d => d.count);

    const arc = d3.arc<any>()
      .innerRadius(0)
      .outerRadius(radius);

    const arcs = g.selectAll('arc')
      .data(pie(data))
      .enter()
      .append('g');

    arcs.append('path')
      .attr('d', arc)
      .attr('fill', d => color(d.data.status) as string)
      .style('stroke', 'white')
      .style('stroke-width', 2)
      .on('mouseover', function(event, d) {
        const tooltip = d3.select('body').append('div')
          .attr('class', 'chart-tooltip')
          .style('opacity', 0);

        tooltip.transition()
          .duration(200)
          .style('opacity', .9);
        
        tooltip.html(`${d.data.status}: ${d.data.count} ships`)
          .style('left', (event.pageX + 10) + 'px')
          .style('top', (event.pageY - 28) + 'px');
      })
      .on('mouseout', function() {
        d3.selectAll('.chart-tooltip').remove();
      });

    // Add labels
    arcs.append('text')
      .attr('transform', d => `translate(${arc.centroid(d)})`)
      .attr('text-anchor', 'middle')
      .text(d => d.data.count > 0 ? d.data.count : '')
      .style('fill', 'white')
      .style('font-weight', 'bold')
      .style('font-size', '14px');

    // Legend
    const legend = svg.append('g')
      .attr('transform', `translate(${width - 100}, 20)`);

    const legendItems = legend.selectAll('.legend-item')
      .data(data)
      .enter()
      .append('g')
      .attr('class', 'legend-item')
      .attr('transform', (d, i) => `translate(0, ${i * 20})`);

    legendItems.append('rect')
      .attr('width', 15)
      .attr('height', 15)
      .attr('fill', d => color(d.status) as string);

    legendItems.append('text')
      .attr('x', 20)
      .attr('y', 12)
      .text(d => d.status)
      .style('font-size', '12px')
      .style('fill', 'var(--text-secondary)');
  };

  const drawConditionChart = () => {
    const data = [
      { condition: 'Excellent', count: report.byCondition.excellent, color: '#4ECDC4' },
      { condition: 'Good', count: report.byCondition.good, color: '#85C1E2' },
      { condition: 'Fair', count: report.byCondition.fair, color: '#F7DC6F' },
      { condition: 'Poor', count: report.byCondition.poor, color: '#FF8C42' },
      { condition: 'Critical', count: report.byCondition.critical, color: '#FF6B6B' }
    ];

    // Clear previous chart
    d3.select(conditionChartRef.current).selectAll('*').remove();

    const margin = { top: 20, right: 30, bottom: 60, left: 60 };
    const width = 400 - margin.left - margin.right;
    const height = 300 - margin.top - margin.bottom;

    const svg = d3.select(conditionChartRef.current)
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom);

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const x = d3.scaleBand()
      .domain(data.map(d => d.condition))
      .range([0, width])
      .padding(0.1);

    const y = d3.scaleLinear()
      .domain([0, d3.max(data, d => d.count) as number])
      .nice()
      .range([height, 0]);

    // X axis
    g.append('g')
      .attr('class', 'axis axis-x')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x))
      .selectAll('text')
      .style('text-anchor', 'end')
      .attr('dx', '-.8em')
      .attr('dy', '.15em')
      .attr('transform', 'rotate(-45)');

    // Y axis
    g.append('g')
      .attr('class', 'axis axis-y')
      .call(d3.axisLeft(y).ticks(5));

    // Y axis label
    g.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', 0 - margin.left)
      .attr('x', 0 - (height / 2))
      .attr('dy', '1em')
      .style('text-anchor', 'middle')
      .style('fill', 'var(--text-secondary)')
      .style('font-size', '12px')
      .text('Number of Ships');

    // Bars
    g.selectAll('.bar')
      .data(data)
      .enter().append('rect')
      .attr('class', 'bar')
      .attr('x', d => x(d.condition) as number)
      .attr('y', d => y(d.count))
      .attr('width', x.bandwidth())
      .attr('height', d => height - y(d.count))
      .attr('fill', d => d.color)
      .on('mouseover', function(event, d) {
        const tooltip = d3.select('body').append('div')
          .attr('class', 'chart-tooltip')
          .style('opacity', 0);

        tooltip.transition()
          .duration(200)
          .style('opacity', .9);
        
        const percentage = ((d.count / report.totalShips) * 100).toFixed(1);
        tooltip.html(`${d.condition}: ${d.count} ships (${percentage}%)`)
          .style('left', (event.pageX + 10) + 'px')
          .style('top', (event.pageY - 28) + 'px');
      })
      .on('mouseout', function() {
        d3.selectAll('.chart-tooltip').remove();
      });

    // Value labels on bars
    g.selectAll('.text')
      .data(data)
      .enter().append('text')
      .attr('x', d => (x(d.condition) as number) + x.bandwidth() / 2)
      .attr('y', d => y(d.count) - 5)
      .attr('text-anchor', 'middle')
      .text(d => d.count > 0 ? d.count : '')
      .style('fill', 'var(--text-primary)')
      .style('font-size', '12px')
      .style('font-weight', 'bold');
  };

  return (
    <div className="fleet-health-report">
      <div className="report-header">
        <h3>Fleet Health Analysis</h3>
        <div className="report-summary">
          <div className="summary-item">
            <span className="summary-label">Total Ships:</span>
            <span className="summary-value">{report.totalShips}</span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Maintenance Needed:</span>
            <span className="summary-value warning">{report.maintenanceNeeded}</span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Critical Issues:</span>
            <span className="summary-value critical">{report.criticalIssues.length}</span>
          </div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-container">
          <h4>Fleet Status Distribution</h4>
          <svg ref={statusChartRef}></svg>
        </div>
        
        <div className="chart-container">
          <h4>Ship Condition Analysis</h4>
          <svg ref={conditionChartRef}></svg>
        </div>
      </div>

      {report.criticalIssues.length > 0 && (
        <div className="critical-issues">
          <h4>⚠️ Critical Issues Requiring Attention</h4>
          <div className="issues-list">
            {report.criticalIssues.slice(0, 5).map((issue, idx) => (
              <div key={idx} className={`issue-card severity-${issue.severity}`}>
                <div className="issue-header">
                  <span className="ship-name">{issue.shipName}</span>
                  <span className={`severity-badge ${issue.severity}`}>
                    {issue.severity.toUpperCase()}
                  </span>
                </div>
                <div className="issue-details">
                  <p className="issue-description">{issue.description}</p>
                  <p className="recommended-action">
                    <strong>Recommended:</strong> {issue.recommendedAction}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default FleetHealthReport;