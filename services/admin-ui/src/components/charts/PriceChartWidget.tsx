import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import './charts.css';

interface Commodity {
  name: string;
  buyPrice: number;
  sellPrice: number;
  supply: number;
  demand: number;
}

interface MarketData {
  stationId: string;
  stationName: string;
  sectorId: string;
  commodities: Commodity[];
}

interface PriceChartWidgetProps {
  marketData: MarketData[];
  selectedCommodity: string | null;
}

const PriceChartWidget: React.FC<PriceChartWidgetProps> = ({ marketData, selectedCommodity }) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!marketData.length || !svgRef.current) return;

    // Clear previous chart
    d3.select(svgRef.current).selectAll('*').remove();

    // Dimensions
    const margin = { top: 20, right: 30, bottom: 40, left: 60 };
    const width = 800 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    // Create SVG
    const svg = d3.select(svgRef.current)
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom);

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Process data
    const commodities = selectedCommodity 
      ? [selectedCommodity]
      : ['Fuel', 'Minerals', 'Food', 'Electronics', 'Weapons', 'Medical'];

    const priceData = commodities.map(commodity => {
      const prices = marketData.flatMap(port => {
        const item = port.commodities.find(c => c.name === commodity);
        return item ? [{
          commodity,
          port: port.stationName,
          buyPrice: item.buyPrice,
          sellPrice: item.sellPrice,
          avgPrice: (item.buyPrice + item.sellPrice) / 2
        }] : [];
      });
      return { commodity, prices };
    });

    // Scales
    const x0 = d3.scaleBand()
      .domain(marketData.map(d => d.stationName))
      .rangeRound([0, width])
      .paddingInner(0.1);

    const x1 = d3.scaleBand()
      .domain(commodities)
      .rangeRound([0, x0.bandwidth()])
      .padding(0.05);

    const y = d3.scaleLinear()
      .domain([0, d3.max(priceData.flatMap(d => d.prices.map(p => p.buyPrice))) as number])
      .nice()
      .rangeRound([height, 0]);

    const color = d3.scaleOrdinal()
      .domain(commodities)
      .range(['#FF6B6B', '#4ECDC4', '#45B7D1', '#F7DC6F', '#BB8FCE', '#85C1E2']);

    // Axes
    g.append('g')
      .attr('class', 'axis axis-x')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x0))
      .selectAll('text')
      .style('text-anchor', 'end')
      .attr('dx', '-.8em')
      .attr('dy', '.15em')
      .attr('transform', 'rotate(-45)');

    g.append('g')
      .attr('class', 'axis axis-y')
      .call(d3.axisLeft(y).ticks(10))
      .append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', 6)
      .attr('dy', '0.71em')
      .attr('text-anchor', 'end')
      .text('Price (Credits)');

    // Bars
    const portGroups = g.append('g')
      .selectAll('g')
      .data(marketData)
      .enter().append('g')
      .attr('transform', d => `translate(${x0(d.stationName)},0)`);

    portGroups.selectAll('rect')
      .data(d => commodities.map(commodity => {
        const item = d.commodities.find(c => c.name === commodity);
        return {
          commodity,
          price: item ? item.buyPrice : 0
        };
      }))
      .enter().append('rect')
      .attr('x', d => x1(d.commodity) as number)
      .attr('y', d => y(d.price))
      .attr('width', x1.bandwidth())
      .attr('height', d => height - y(d.price))
      .attr('fill', d => color(d.commodity) as string)
      .on('mouseover', function(event, d) {
        // Tooltip
        const tooltip = d3.select('body').append('div')
          .attr('class', 'chart-tooltip')
          .style('opacity', 0);

        tooltip.transition()
          .duration(200)
          .style('opacity', .9);
        
        tooltip.html(`${d.commodity}: ${d.price} CR`)
          .style('left', (event.pageX + 10) + 'px')
          .style('top', (event.pageY - 28) + 'px');
      })
      .on('mouseout', function() {
        d3.selectAll('.chart-tooltip').remove();
      });

    // Legend
    const legend = g.append('g')
      .attr('font-family', 'sans-serif')
      .attr('font-size', 10)
      .attr('text-anchor', 'end')
      .selectAll('g')
      .data(commodities.slice().reverse())
      .enter().append('g')
      .attr('transform', (d, i) => `translate(0,${i * 20})`);

    legend.append('rect')
      .attr('x', width - 19)
      .attr('width', 19)
      .attr('height', 19)
      .attr('fill', color as any);

    legend.append('text')
      .attr('x', width - 24)
      .attr('y', 9.5)
      .attr('dy', '0.32em')
      .text(d => d);

  }, [marketData, selectedCommodity]);

  return (
    <div className="price-chart-widget">
      <svg ref={svgRef}></svg>
    </div>
  );
};

export default PriceChartWidget;