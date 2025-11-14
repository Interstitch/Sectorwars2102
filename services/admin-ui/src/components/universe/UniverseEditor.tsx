import React, { useRef, useEffect, useState } from 'react';
import * as d3 from 'd3';
import { useAdmin, SectorData } from '../../contexts/AdminContext';
import './universe-editor.css';

// Type definitions for the interactive universe map
interface SectorNode {
  id: number;
  name: string;
  type: string;
  x: number;
  y: number;
  connections: number[];
  region_id: string;
  cluster_id: string;
  hazard_level: number;
  has_port: boolean;
  has_planet: boolean;
  has_warp_tunnel: boolean;
  resource_richness: string;
}

interface LinkData {
  source: number;
  target: number;
  is_warp_tunnel: boolean;
}

interface MapData {
  sectors: SectorNode[];
  links: LinkData[];
}

const UniverseEditor: React.FC = () => {
  const { galaxyState, zones, clusters, sectors, loadSectors } = useAdmin();
  const svgRef = useRef<SVGSVGElement | null>(null);
  const [mapData, setMapData] = useState<MapData | null>(null);
  const [selectedSector, setSelectedSector] = useState<SectorNode | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Filter controls
  const [selectedRegion, setSelectedRegion] = useState<string | null>(null);
  const [selectedCluster, setSelectedCluster] = useState<string | null>(null);
  
  // Fetch universe map data
  useEffect(() => {
    const loadData = async () => {
      if (!galaxyState) {
        setMapData(null);
        setLoading(false);
        return;
      }
      
      setLoading(true);
      setError(null);
      
      try {
        // Load real sector data from the API
        await loadSectors();
      } catch (err) {
        console.error('Error fetching map data:', err);
        setError('Failed to load universe map data');
      } finally {
        setLoading(false);
      }
    };
    
    loadData();
  }, [galaxyState, selectedRegion, selectedCluster, loadSectors]);
  
  // When sectors update, convert to map data
  useEffect(() => {
    if (sectors && sectors.length > 0) {
      // Convert API data to MapData format
      const mapData: MapData = convertSectorDataToMapData(sectors);
      setMapData(mapData);
    } else if (!sectors || sectors.length === 0) {
      // Fall back to sample data if no real data available
      const sampleData: MapData = generateSampleData();
      setMapData(sampleData);
    }
  }, [sectors]);
  
  // Convert sector data from API to MapData format
  const convertSectorDataToMapData = (sectorsData: SectorData[]): MapData => {
    const sectorNodes: SectorNode[] = [];
    const links: LinkData[] = [];
    
    // Convert sectors to nodes
    for (const sector of sectorsData) {
      sectorNodes.push({
        id: sector.sector_id,
        name: sector.name,
        type: sector.type.toLowerCase(),
        x: sector.x_coord * 50 + 500, // Scale coordinates for visualization
        y: sector.y_coord * 50 + 500,
        connections: [], // Will be populated based on warp tunnels
        region_id: sector.cluster_id, // Use cluster_id as region for now
        cluster_id: sector.cluster_id,
        hazard_level: sector.hazard_level,
        has_port: sector.has_port,
        has_planet: sector.has_planet,
        has_warp_tunnel: sector.has_warp_tunnel,
        resource_richness: sector.resource_richness
      });
    }
    
    // Create basic connections between nearby sectors
    for (let i = 0; i < sectorNodes.length; i++) {
      const sector = sectorNodes[i];
      
      // Find nearby sectors and create connections
      for (let j = i + 1; j < Math.min(i + 4, sectorNodes.length); j++) {
        const targetSector = sectorNodes[j];
        const distance = Math.sqrt(
          Math.pow(sector.x - targetSector.x, 2) + 
          Math.pow(sector.y - targetSector.y, 2)
        );
        
        // Create connection if sectors are close enough
        if (distance < 150) {
          links.push({
            source: sector.id,
            target: targetSector.id,
            is_warp_tunnel: sector.has_warp_tunnel && targetSector.has_warp_tunnel && Math.random() > 0.7
          });
        }
      }
    }
    
    return { sectors: sectorNodes, links };
  };
  
  // Function to generate sample data for preview
  const generateSampleData = (): MapData => {
    const numSectors = 80;
    const sectorNodes: SectorNode[] = [];
    const links: LinkData[] = [];
    
    // Generate sectors arranged in a spiral
    for (let i = 0; i < numSectors; i++) {
      // Calculate position in a spiral pattern
      const angle = 0.1 * i;
      const radius = 5 * Math.sqrt(i);
      const x = radius * Math.cos(angle) + 500;
      const y = radius * Math.sin(angle) + 500;
      
      // Assign to random region/cluster
      const regionId = zones.length > 0 
        ? zones[Math.floor(Math.random() * zones.length)].id 
        : 'region-1';
      
      const clusterId = clusters.length > 0
        ? clusters[Math.floor(Math.random() * clusters.length)].id
        : 'cluster-1';
      
      // Create sector node
      sectorNodes.push({
        id: i + 1,
        name: `Sector ${i + 1}`,
        type: ['normal', 'nebula', 'asteroid_field', 'black_hole'][Math.floor(Math.random() * 4)],
        x,
        y,
        connections: [],
        region_id: regionId,
        cluster_id: clusterId,
        hazard_level: Math.random() * 10,
        has_port: Math.random() > 0.7,
        has_planet: Math.random() > 0.6,
        has_warp_tunnel: Math.random() > 0.8,
        resource_richness: ['poor', 'average', 'rich', 'abundant'][Math.floor(Math.random() * 4)]
      });
    }
    
    // Generate connections
    for (let i = 0; i < numSectors; i++) {
      const numConnections = Math.floor(Math.random() * 3) + 1;
      for (let j = 0; j < numConnections; j++) {
        const targetIndex = Math.floor(Math.random() * numSectors);
        if (targetIndex !== i) {
          sectorNodes[i].connections.push(targetIndex);
          links.push({
            source: i + 1,
            target: targetIndex + 1,
            is_warp_tunnel: Math.random() > 0.7
          });
        }
      }
    }
    
    return { sectors: sectorNodes, links };
  };
  
  // D3 visualization setup
  useEffect(() => {
    if (!svgRef.current || !mapData || loading) return;
    
    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove(); // Clear existing content
    
    // const width = 1000;
    // const height = 800;
    
    // Set up zoom behavior
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.5, 4])
      .on('zoom', (event) => {
        container.attr('transform', event.transform);
      });
    
    svg.call(zoom);
    
    // Create container for zoomable content
    const container = svg.append('g');
    
    // Create links
    container.append('g')
      .attr('class', 'links')
      .selectAll('line')
      .data(mapData.links)
      .enter()
      .append('line')
      .attr('class', d => d.is_warp_tunnel ? 'warp-tunnel' : 'normal-link')
      .attr('x1', d => {
        const source = mapData.sectors.find(s => s.id === d.source);
        return source ? source.x : 0;
      })
      .attr('y1', d => {
        const source = mapData.sectors.find(s => s.id === d.source);
        return source ? source.y : 0;
      })
      .attr('x2', d => {
        const target = mapData.sectors.find(s => s.id === d.target);
        return target ? target.x : 0;
      })
      .attr('y2', d => {
        const target = mapData.sectors.find(s => s.id === d.target);
        return target ? target.y : 0;
      });
    
    // Create sector nodes
    const node = container.append('g')
      .attr('class', 'nodes')
      .selectAll('g')
      .data(mapData.sectors)
      .enter()
      .append('g')
      .attr('class', 'sector-node')
      .attr('transform', d => `translate(${d.x}, ${d.y})`)
      .on('click', (_event, d) => {
        setSelectedSector(d);
      });
    
    // Add circles for sectors
    node.append('circle')
      .attr('r', 8)
      .attr('class', d => `sector-${d.type}`)
      .attr('fill', d => {
        // Color based on sector type
        const colorMap: { [key: string]: string } = {
          normal: '#4a90e2',
          nebula: '#e74c3c',
          asteroid_field: '#f39c12',
          black_hole: '#9b59b6'
        };
        return colorMap[d.type] || '#4a90e2';
      });
    
    // Add special indicators
    node.filter(d => d.has_port)
      .append('circle')
      .attr('r', 3)
      .attr('cx', 10)
      .attr('cy', -10)
      .attr('class', 'port-indicator');
    
    node.filter(d => d.has_planet)
      .append('circle')
      .attr('r', 3)
      .attr('cx', -10)
      .attr('cy', -10)
      .attr('class', 'planet-indicator');
    
    // Add labels
    node.append('text')
      .attr('dy', 20)
      .attr('text-anchor', 'middle')
      .attr('class', 'sector-label')
      .text(d => `S${d.id}`);
    
    // Add tooltip
    const tooltip = d3.select('body').append('div')
      .attr('class', 'universe-tooltip')
      .style('opacity', 0);
    
    node.on('mouseover', (event, d) => {
      tooltip.transition()
        .duration(200)
        .style('opacity', .9);
      tooltip.html(`
        <strong>${d.name}</strong><br/>
        Type: ${d.type}<br/>
        Hazard Level: ${d.hazard_level.toFixed(1)}<br/>
        Resources: ${d.resource_richness}<br/>
        ${d.has_port ? '✓ Has Port<br/>' : ''}
        ${d.has_planet ? '✓ Has Planet<br/>' : ''}
        ${d.has_warp_tunnel ? '✓ Has Warp Tunnel' : ''}
      `)
        .style('left', (event.pageX + 10) + 'px')
        .style('top', (event.pageY - 28) + 'px');
    })
    .on('mouseout', () => {
      tooltip.transition()
        .duration(500)
        .style('opacity', 0);
    });
    
    // Clean up tooltip on unmount
    return () => {
      d3.select('body').selectAll('.universe-tooltip').remove();
    };
  }, [mapData, loading]);
  
  return (
    <div className="universe-editor">
      <div className="editor-controls">
        <h3>Universe Map</h3>
        
        <div className="filter-controls">
          <label>
            Region:
            <select 
              value={selectedRegion || ''} 
              onChange={(e) => setSelectedRegion(e.target.value || null)}
            >
              <option value="">All Regions</option>
              {zones.map(region => (
                <option key={region.id} value={region.id}>
                  {region.name}
                </option>
              ))}
            </select>
          </label>
          
          <label>
            Cluster:
            <select 
              value={selectedCluster || ''} 
              onChange={(e) => setSelectedCluster(e.target.value || null)}
              disabled={!selectedRegion}
            >
              <option value="">All Clusters</option>
              {clusters
                .filter(cluster => !selectedRegion || cluster.region_id === selectedRegion)
                .map(cluster => (
                  <option key={cluster.id} value={cluster.id}>
                    {cluster.name}
                  </option>
                ))}
            </select>
          </label>
        </div>
        
        {selectedSector && (
          <div className="sector-details">
            <h4>{selectedSector.name}</h4>
            <p>Type: {selectedSector.type}</p>
            <p>Hazard Level: {selectedSector.hazard_level.toFixed(1)}</p>
            <p>Resources: {selectedSector.resource_richness}</p>
            {selectedSector.has_port && <p>✓ Has Port</p>}
            {selectedSector.has_planet && <p>✓ Has Planet</p>}
            {selectedSector.has_warp_tunnel && <p>✓ Has Warp Tunnel</p>}
          </div>
        )}
      </div>
      
      <div className="map-container">
        {loading && <div className="loading">Loading universe map...</div>}
        {error && <div className="error">{error}</div>}
        {!loading && !error && (
          <svg 
            ref={svgRef} 
            width="1000" 
            height="800"
            className="universe-map"
          />
        )}
      </div>
      
      <div className="map-legend">
        <h4>Legend</h4>
        <div className="legend-item">
          <span className="legend-color normal"></span> Normal Sector
        </div>
        <div className="legend-item">
          <span className="legend-color nebula"></span> Nebula
        </div>
        <div className="legend-item">
          <span className="legend-color asteroid"></span> Asteroid Field
        </div>
        <div className="legend-item">
          <span className="legend-color black-hole"></span> Black Hole
        </div>
        <div className="legend-item">
          <span className="legend-indicator port"></span> Port
        </div>
        <div className="legend-item">
          <span className="legend-indicator planet"></span> Planet
        </div>
        <div className="legend-item">
          <span className="legend-line warp"></span> Warp Tunnel
        </div>
      </div>
    </div>
  );
};

export default UniverseEditor;