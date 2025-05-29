import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface TeamMember {
  playerId: string;
  playerName: string;
  role: 'leader' | 'officer' | 'member';
  joinedAt: string;
}

interface Team {
  teamId: string;
  name: string;
  tag: string;
  leaderId: string;
  leaderName: string;
  members: TeamMember[];
  totalAssets: number;
  avgLevel: number;
  territories: number;
  allianceId?: string;
  createdAt: string;
}

interface TeamStrengthChartProps {
  teams: Team[];
  width?: number;
  height?: number;
}

export const TeamStrengthChart: React.FC<TeamStrengthChartProps> = ({ 
  teams, 
  width = 1200, 
  height = 400 
}) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || teams.length === 0) return;

    // Clear previous chart
    d3.select(svgRef.current).selectAll('*').remove();

    // Sort teams by total assets and take top 10
    const topTeams = [...teams]
      .sort((a, b) => b.totalAssets - a.totalAssets)
      .slice(0, 10);

    const margin = { top: 40, right: 120, bottom: 60, left: 60 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Scales
    const xScale = d3.scaleBand()
      .domain(topTeams.map(t => t.tag))
      .range([0, innerWidth])
      .padding(0.1);

    const yScale = d3.scaleLinear()
      .domain([0, d3.max(topTeams, d => d.totalAssets) || 0])
      .nice()
      .range([innerHeight, 0]);

    const colorScale = d3.scaleOrdinal(d3.schemeCategory10);

    // Add X axis
    g.append('g')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(d3.axisBottom(xScale))
      .append('text')
      .attr('x', innerWidth / 2)
      .attr('y', 40)
      .attr('fill', 'currentColor')
      .style('text-anchor', 'middle')
      .text('Team Tag');

    // Add Y axis
    g.append('g')
      .call(d3.axisLeft(yScale).tickFormat(d => `$${(d as number) / 1000}k`))
      .append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', -40)
      .attr('x', -innerHeight / 2)
      .attr('fill', 'currentColor')
      .style('text-anchor', 'middle')
      .text('Total Assets');

    // Add bars
    const bars = g.selectAll('.bar')
      .data(topTeams)
      .enter().append('g')
      .attr('class', 'bar-group');

    bars.append('rect')
      .attr('class', 'bar')
      .attr('x', (d: Team) => xScale(d.tag) || 0)
      .attr('y', innerHeight)
      .attr('width', xScale.bandwidth())
      .attr('height', 0)
      .attr('fill', (d: Team, i: number) => colorScale(i.toString()))
      .transition()
      .duration(750)
      .attr('y', (d: Team) => yScale(d.totalAssets))
      .attr('height', (d: Team) => innerHeight - yScale(d.totalAssets));

    // Add value labels on bars
    bars.append('text')
      .attr('class', 'value-label')
      .attr('x', (d: Team) => (xScale(d.tag) || 0) + xScale.bandwidth() / 2)
      .attr('y', (d: Team) => yScale(d.totalAssets) - 5)
      .attr('text-anchor', 'middle')
      .attr('fill', 'currentColor')
      .style('font-size', '12px')
      .text((d: Team) => `$${(d.totalAssets / 1000).toFixed(0)}k`);

    // Add member count labels below bars
    bars.append('text')
      .attr('class', 'member-label')
      .attr('x', (d: Team) => (xScale(d.tag) || 0) + xScale.bandwidth() / 2)
      .attr('y', innerHeight + 25)
      .attr('text-anchor', 'middle')
      .attr('fill', '#666')
      .style('font-size', '10px')
      .text((d: Team) => `${d.members.length} members`);

    // Add tooltip
    const tooltip = d3.select('body').append('div')
      .attr('class', 'chart-tooltip')
      .style('opacity', 0)
      .style('position', 'absolute')
      .style('background', 'rgba(0, 0, 0, 0.8)')
      .style('color', 'white')
      .style('padding', '10px')
      .style('border-radius', '4px')
      .style('pointer-events', 'none');

    bars.selectAll('rect')
      .on('mouseover', function(event: any, d: any) {
        const team = d as Team;
        tooltip.transition().duration(200).style('opacity', 0.9);
        tooltip.html(`
          <div><strong>${team.name}</strong></div>
          <div>Leader: ${team.leaderName}</div>
          <div>Members: ${team.members.length}</div>
          <div>Avg Level: ${team.avgLevel}</div>
          <div>Total Assets: $${team.totalAssets.toLocaleString()}</div>
        `)
          .style('left', (event.pageX + 10) + 'px')
          .style('top', (event.pageY - 28) + 'px');
      })
      .on('mouseout', function() {
        tooltip.transition().duration(500).style('opacity', 0);
      });

    // Cleanup tooltip on unmount
    return () => {
      d3.selectAll('.chart-tooltip').remove();
    };
  }, [teams, width, height]);

  return (
    <div className="team-strength-chart">
      <svg ref={svgRef}></svg>
    </div>
  );
};