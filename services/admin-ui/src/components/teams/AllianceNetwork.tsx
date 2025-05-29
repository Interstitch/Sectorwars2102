import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface TeamMember {
  playerId: string;
  playerName: string;
  role: 'leader' | 'officer' | 'member';
  joinedAt: string;
}

interface Team {
  id: string;
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

interface Alliance {
  id: string;
  team1Id: string;
  team2Id: string;
  type: 'alliance' | 'trade' | 'non-aggression';
  status: 'active' | 'expired' | 'broken';
  createdAt: string;
  expiresAt?: string;
}

interface AllianceNetworkProps {
  teams: Team[];
  alliances: Alliance[];
  width?: number;
  height?: number;
}

interface NetworkNode {
  id: string;
  name: string;
  tag: string;
  size: number;
  x?: number;
  y?: number;
  fx?: number | null;
  fy?: number | null;
}

interface NetworkLink {
  source: string | NetworkNode;
  target: string | NetworkNode;
  type: string;
  status: string;
}

export const AllianceNetwork: React.FC<AllianceNetworkProps> = ({
  teams,
  alliances,
  width = 1200,
  height = 600
}) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || teams.length === 0) return;

    // Clear previous chart
    d3.select(svgRef.current).selectAll('*').remove();

    // Create nodes from teams
    const nodes: NetworkNode[] = teams.map(team => ({
      id: team.id,
      name: team.name,
      tag: team.tag,
      size: Math.sqrt(team.totalAssets / 10000) * 5 + 10
    }));

    // Create links from alliances
    const links: NetworkLink[] = alliances
      .filter(alliance => alliance.status === 'active')
      .map(alliance => ({
        source: alliance.team1Id,
        target: alliance.team2Id,
        type: alliance.type,
        status: alliance.status
      }));

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    // Create simulation
    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id((d: any) => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius((d: any) => d.size + 5));

    // Add link lines
    const link = svg.append('g')
      .attr('class', 'links')
      .selectAll('line')
      .data(links)
      .enter().append('line')
      .attr('stroke', (d: NetworkLink) => {
        if (d.type === 'alliance') return '#e63946';
        if (d.type === 'trade') return '#06ffa5';
        return '#999';
      })
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', 2);

    // Add nodes
    const node = svg.append('g')
      .attr('class', 'nodes')
      .selectAll('g')
      .data(nodes)
      .enter().append('g')
      .call(d3.drag<any, NetworkNode>()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended) as any);

    node.append('circle')
      .attr('r', (d: NetworkNode) => d.size)
      .attr('fill', '#2563eb')
      .attr('stroke', '#fff')
      .attr('stroke-width', 2);

    node.append('text')
      .text((d: NetworkNode) => d.tag)
      .attr('text-anchor', 'middle')
      .attr('dy', '.35em')
      .attr('fill', 'white')
      .style('font-size', '12px')
      .style('font-weight', 'bold')
      .style('pointer-events', 'none');

    // Add tooltip
    const tooltip = d3.select('body').append('div')
      .attr('class', 'network-tooltip')
      .style('opacity', 0)
      .style('position', 'absolute')
      .style('background', 'rgba(0, 0, 0, 0.8)')
      .style('color', 'white')
      .style('padding', '10px')
      .style('border-radius', '4px')
      .style('pointer-events', 'none');

    node.on('mouseover', function(event: any, d: any) {
      const team = teams.find(t => t.id === d.id);
      if (team) {
        tooltip.transition().duration(200).style('opacity', 0.9);
        tooltip.html(`
          <div><strong>${team.name}</strong></div>
          <div>Leader: ${team.leaderName}</div>
          <div>Members: ${team.members.length}</div>
          <div>Assets: $${team.totalAssets.toLocaleString()}</div>
        `)
          .style('left', (event.pageX + 10) + 'px')
          .style('top', (event.pageY - 28) + 'px');
      }
    })
    .on('mouseout', function() {
      tooltip.transition().duration(500).style('opacity', 0);
    });

    // Update positions on each tick
    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      node
        .attr('transform', (d: any) => `translate(${d.x},${d.y})`);
    });

    function dragstarted(event: any, d: NetworkNode) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event: any, d: NetworkNode) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event: any, d: NetworkNode) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }

    // Cleanup on unmount
    return () => {
      simulation.stop();
      d3.selectAll('.network-tooltip').remove();
    };
  }, [teams, alliances, width, height]);

  return (
    <div className="alliance-network">
      <svg ref={svgRef}></svg>
      <div className="network-legend">
        <div className="legend-item">
          <span className="legend-line alliance"></span>
          <span>Military Alliance</span>
        </div>
        <div className="legend-item">
          <span className="legend-line trade"></span>
          <span>Trade Agreement</span>
        </div>
        <div className="legend-item">
          <span className="legend-line non-aggression"></span>
          <span>Non-Aggression Pact</span>
        </div>
      </div>
    </div>
  );
};