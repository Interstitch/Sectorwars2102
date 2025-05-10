
function initializeUniverse(sectors) {
    console.log('Initializing universe with sectors:', sectors);
    
    if (!sectors || Object.keys(sectors).length === 0) {
        console.error('No sectors data available');
        return;
    }
    
    const container = document.getElementById('universe-map');
    if (!container) {
        console.error('Universe map container not found');
        return;
    }

    // Clear existing content
    container.innerHTML = '';
    
    const width = container.clientWidth;
    const height = container.clientHeight;
    
    const svg = d3.select('#universe-map')
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .attr('class', 'universe-svg');

    // Create container for zoom
    const g = svg.append('g')
        .attr('class', 'universe-container');

    // Process data
    const nodes = Object.entries(sectors).map(([id, data]) => ({
        id: parseInt(id),
        ...data,
        x: Math.random() * width,
        y: Math.random() * height
    }));

    const links = [];
    nodes.forEach(node => {
        if (node.links) {
            node.links.forEach(targetId => {
                if (sectors[targetId]) {
                    links.push({
                        source: node.id,
                        target: targetId
                    });
                }
            });
        }
    });

    // Draw links
    const link = g.selectAll('.sector-link')
        .data(links)
        .join('line')
        .attr('class', 'sector-link')
        .attr('stroke', '#666')
        .attr('stroke-width', 2);

    // Draw nodes
    const node = g.selectAll('.sector-node')
        .data(nodes)
        .join('g')
        .attr('class', 'sector-node')
        .attr('data-sector-id', d => d.id);

    node.append('circle')
        .attr('r', 20)
        .attr('fill', d => d.has_planet ? '#4CAF50' : '#666')
        .attr('stroke', '#fff')
        .attr('stroke-width', 2);

    node.append('text')
        .text(d => d.id)
        .attr('text-anchor', 'middle')
        .attr('dy', '.3em')
        .attr('fill', 'white')
        .attr('pointer-events', 'none');

    // Force simulation
    const simulation = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(links).id(d => d.id).distance(100))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(30));

    // Add zoom behavior
    const zoom = d3.zoom()
        .scaleExtent([0.1, 4])
        .on('zoom', (event) => {
            g.attr('transform', event.transform);
        });

    svg.call(zoom);

    // Add click handler
    node.on('click', function(event, d) {
        event.preventDefault();
        event.stopPropagation();
        if (typeof initializeSectorPopup === 'function') {
            initializeSectorPopup(event, d);
        }
    });

    // Update positions on simulation tick
    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);

        node.attr('transform', d => `translate(${d.x},${d.y})`);
    });

    // Add drag behavior
    node.call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended));

    function dragstarted(event) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
    }

    function dragged(event) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
    }

    function dragended(event) {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
    }
}
