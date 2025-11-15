import React, { useEffect, useRef, useState } from 'react';
import './sector-viewport.css';

interface SectorViewportProps {
  sectorType?: string;
  sectorName?: string;
  hazardLevel?: number;
  radiationLevel?: number;
  ports?: any[];
  planets?: any[];
  width?: number;
  height?: number;
}

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  size: number;
  opacity: number;
  color: string;
  life: number;
  maxLife: number;
}

const SectorViewport: React.FC<SectorViewportProps> = ({
  sectorType = 'normal',
  sectorName = 'Unknown Sector',
  hazardLevel = 0,
  radiationLevel = 0,
  ports = [],
  planets = [],
  width = 450,
  height = 300
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const particlesRef = useRef<Particle[]>([]);
  const animationFrameRef = useRef<number>();
  const [isAnimating, setIsAnimating] = useState(true);

  // Initialize particles based on sector type
  useEffect(() => {
    const particles: Particle[] = [];
    const particleCount = getParticleCount(sectorType, hazardLevel);

    for (let i = 0; i < particleCount; i++) {
      particles.push(createParticle(sectorType, width, height, radiationLevel));
    }

    particlesRef.current = particles;
  }, [sectorType, hazardLevel, radiationLevel, width, height]);

  // Animation loop
  useEffect(() => {
    if (!isAnimating) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const animate = () => {
      // Clear canvas with fade effect for trails
      ctx.fillStyle = 'rgba(5, 8, 16, 0.15)';
      ctx.fillRect(0, 0, width, height);

      // Draw starfield background
      drawStarfield(ctx, width, height);

      // Update and draw particles
      updateParticles(particlesRef.current, sectorType, width, height, radiationLevel);
      drawParticles(ctx, particlesRef.current);

      // Draw planets
      drawPlanets(ctx, planets, width, height);

      // Draw ports
      drawPorts(ctx, ports, width, height);

      // Draw sector-specific effects
      drawSectorEffects(ctx, sectorType, width, height, hazardLevel, radiationLevel);

      animationFrameRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [isAnimating, sectorType, hazardLevel, radiationLevel, ports, planets, width, height]);

  return (
    <div className="sector-viewport-container">
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        className="sector-viewport-canvas"
      />
      <div className="viewport-overlay">
        <div className="viewport-label">{sectorName}</div>
      </div>
    </div>
  );
};

// Helper functions

function getParticleCount(sectorType: string, hazardLevel: number): number {
  const baseCount = {
    'normal': 50,
    'nebula': 150,
    'asteroid_field': 80,
    'ice_field': 100,
    'radiation_zone': 120,
    'void': 20
  }[sectorType] || 50;

  return baseCount + (hazardLevel * 10);
}

function createParticle(
  sectorType: string,
  width: number,
  height: number,
  radiationLevel: number
): Particle {
  const colorSchemes = {
    'normal': ['#ffffff', '#c0c0c0', '#00d9ff'],
    'nebula': ['#c961de', '#9333ea', '#00d9ff', '#00ff41'],
    'asteroid_field': ['#8b4513', '#a0522d', '#696969'],
    'ice_field': ['#00d9ff', '#88ddff', '#ffffff'],
    'radiation_zone': ['#00ff41', '#ffff00', '#ff6b00'],
    'void': ['#1a1a2e', '#16213e', '#0f0f23']
  };

  const colors = colorSchemes[sectorType as keyof typeof colorSchemes] || colorSchemes['normal'];
  const color = colors[Math.floor(Math.random() * colors.length)];

  return {
    x: Math.random() * width,
    y: Math.random() * height,
    vx: (Math.random() - 0.5) * (sectorType === 'nebula' ? 0.5 : 0.2),
    vy: (Math.random() - 0.5) * (sectorType === 'nebula' ? 0.5 : 0.2),
    size: Math.random() * (sectorType === 'asteroid_field' ? 4 : 2) + 1,
    opacity: Math.random() * 0.5 + 0.3,
    color,
    life: 0,
    maxLife: Math.random() * 1000 + 500
  };
}

function updateParticles(
  particles: Particle[],
  sectorType: string,
  width: number,
  height: number,
  radiationLevel: number
) {
  particles.forEach(particle => {
    // Update position
    particle.x += particle.vx;
    particle.y += particle.vy;

    // Sector-specific behaviors
    if (sectorType === 'nebula') {
      // Swirling motion
      particle.vx += Math.sin(particle.life * 0.01) * 0.02;
      particle.vy += Math.cos(particle.life * 0.01) * 0.02;
    } else if (sectorType === 'radiation_zone') {
      // Pulsing motion
      particle.opacity = 0.3 + Math.sin(particle.life * 0.05) * 0.3;
    }

    // Wrap around edges
    if (particle.x < 0) particle.x = width;
    if (particle.x > width) particle.x = 0;
    if (particle.y < 0) particle.y = height;
    if (particle.y > height) particle.y = 0;

    // Update life
    particle.life += 1;
    if (particle.life > particle.maxLife) {
      particle.life = 0;
      particle.opacity = Math.random() * 0.5 + 0.3;
    }
  });
}

function drawParticles(ctx: CanvasRenderingContext2D, particles: Particle[]) {
  particles.forEach(particle => {
    ctx.globalAlpha = particle.opacity;
    ctx.fillStyle = particle.color;
    ctx.beginPath();
    ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
    ctx.fill();
  });
  ctx.globalAlpha = 1.0;
}

function drawStarfield(ctx: CanvasRenderingContext2D, width: number, height: number) {
  // Static background stars
  ctx.fillStyle = '#ffffff';
  for (let i = 0; i < 100; i++) {
    const x = (i * 137.508) % width; // Golden angle for distribution
    const y = (i * 73.123) % height;
    const size = Math.random() * 0.5 + 0.5;
    const alpha = Math.random() * 0.3 + 0.1;

    ctx.globalAlpha = alpha;
    ctx.beginPath();
    ctx.arc(x, y, size, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.globalAlpha = 1.0;
}

function drawPlanets(
  ctx: CanvasRenderingContext2D,
  planets: any[],
  width: number,
  height: number
) {
  if (!planets || planets.length === 0) return;

  planets.forEach((planet, index) => {
    // Position planets in consistent locations
    const x = width * 0.2 + (index * 100);
    const y = height * 0.3 + (Math.sin(index) * 50);
    const radius = 20 + (index * 5);

    // Planet body
    const gradient = ctx.createRadialGradient(x - radius * 0.3, y - radius * 0.3, radius * 0.1, x, y, radius);

    // Color based on planet type
    const planetColors = {
      'terran': { start: '#00ff41', mid: '#00d9ff', end: '#004d19' },
      'ice': { start: '#88ddff', mid: '#00d9ff', end: '#001a33' },
      'volcanic': { start: '#ff6b00', mid: '#ff0000', end: '#330000' },
      'gas_giant': { start: '#ffb000', mid: '#c961de', end: '#1a0033' },
      'barren': { start: '#8b4513', mid: '#696969', end: '#1a1a1a' }
    };

    const planetType = planet.type?.toLowerCase() || 'barren';
    const colors = planetColors[planetType as keyof typeof planetColors] || planetColors['barren'];

    gradient.addColorStop(0, colors.start);
    gradient.addColorStop(0.5, colors.mid);
    gradient.addColorStop(1, colors.end);

    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, Math.PI * 2);
    ctx.fill();

    // Atmosphere glow
    ctx.strokeStyle = colors.start;
    ctx.globalAlpha = 0.3;
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.arc(x, y, radius + 2, 0, Math.PI * 2);
    ctx.stroke();
    ctx.globalAlpha = 1.0;
  });
}

function drawPorts(
  ctx: CanvasRenderingContext2D,
  ports: any[],
  width: number,
  height: number
) {
  if (!ports || ports.length === 0) return;

  ports.forEach((port, index) => {
    // Position ports in upper area
    const x = width * 0.7 + (index * 80);
    const y = height * 0.25 + (Math.cos(index) * 30);
    const size = 15;

    // Port structure - hexagonal shape
    ctx.strokeStyle = '#00d9ff';
    ctx.fillStyle = 'rgba(0, 217, 255, 0.2)';
    ctx.lineWidth = 2;

    ctx.beginPath();
    for (let i = 0; i < 6; i++) {
      const angle = (Math.PI / 3) * i;
      const px = x + size * Math.cos(angle);
      const py = y + size * Math.sin(angle);
      if (i === 0) {
        ctx.moveTo(px, py);
      } else {
        ctx.lineTo(px, py);
      }
    }
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // Docking ring glow
    ctx.strokeStyle = '#00d9ff';
    ctx.globalAlpha = 0.5;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(x, y, size + 5, 0, Math.PI * 2);
    ctx.stroke();
    ctx.globalAlpha = 1.0;

    // Blinking light
    const blink = Math.sin(Date.now() * 0.005 + index) > 0.5;
    if (blink) {
      ctx.fillStyle = '#00ff41';
      ctx.beginPath();
      ctx.arc(x, y, 2, 0, Math.PI * 2);
      ctx.fill();
    }
  });
}

function drawSectorEffects(
  ctx: CanvasRenderingContext2D,
  sectorType: string,
  width: number,
  height: number,
  hazardLevel: number,
  radiationLevel: number
) {
  // Radiation glow overlay
  if (radiationLevel > 0) {
    ctx.fillStyle = `rgba(0, 255, 65, ${radiationLevel * 0.1})`;
    ctx.fillRect(0, 0, width, height);
  }

  // Hazard warning pulse
  if (hazardLevel > 5) {
    const pulse = Math.sin(Date.now() * 0.005) * 0.5 + 0.5;
    ctx.strokeStyle = `rgba(255, 107, 0, ${pulse * 0.3})`;
    ctx.lineWidth = 3;
    ctx.strokeRect(2, 2, width - 4, height - 4);
  }

  // Sector-specific overlays
  if (sectorType === 'void') {
    // Vignette effect for void sectors
    const gradient = ctx.createRadialGradient(width / 2, height / 2, 0, width / 2, height / 2, width / 2);
    gradient.addColorStop(0, 'rgba(5, 8, 16, 0)');
    gradient.addColorStop(1, 'rgba(5, 8, 16, 0.8)');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, width, height);
  }
}

export default SectorViewport;
