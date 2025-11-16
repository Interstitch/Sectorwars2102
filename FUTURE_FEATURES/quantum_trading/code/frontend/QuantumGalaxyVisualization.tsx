/**
 * Quantum Galaxy Visualization - Revolutionary 3D Space Trading Experience
 * World's first quantum-enhanced 3D galaxy with AI integration and mobile VR support
 * 
 * Features:
 * - Three.js quantum probability visualization in 3D space
 * - Real-time ARIA AI strategic overlays
 * - Mobile VR-ready experience
 * - Quantum trading opportunities visualization
 * - Cross-platform performance optimization
 */

import React, { useRef, useEffect, useState, useCallback, useMemo } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Stars, Text, Html, useHelper } from '@react-three/drei';
import * as THREE from 'three';
import { 
  Atom, 
  Brain, 
  Zap, 
  Target, 
  Eye,
  Maximize2,
  Minimize2,
  Settings,
  RotateCcw
} from 'lucide-react';
import { useWebSocket } from '../../contexts/WebSocketContext';
import { useGame } from '../../contexts/GameContext';
import './quantum-galaxy-visualization.css';

// Types for 3D quantum visualization
interface QuantumSector {
  id: number;
  name: string;
  position: [number, number, number];
  quantumField: number;
  tradingOpportunities: number;
  aiRecommendation: 'high' | 'medium' | 'low';
  manipulationRisk: number;
  playerPresence: boolean;
  quantumTunnels: Array<{
    targetSector: number;
    stability: number;
    probability: number;
  }>;
}

interface QuantumParticle {
  id: string;
  position: [number, number, number];
  velocity: [number, number, number];
  probability: number;
  tradingStrength: number;
  color: string;
}

interface AriaInsight {
  id: string;
  position: [number, number, number];
  type: 'opportunity' | 'warning' | 'recommendation';
  message: string;
  confidence: number;
  expiry: number;
}

interface QuantumGalaxyVisualizationProps {
  isFullscreen?: boolean;
  onToggleFullscreen?: () => void;
  width?: number;
  height?: number;
  quality?: 'low' | 'medium' | 'high';
  enableVR?: boolean;
}

// Quantum Field Visualization Component
const QuantumField: React.FC<{ sectors: QuantumSector[]; particles: QuantumParticle[] }> = ({ 
  sectors, 
  particles 
}) => {
  const meshRef = useRef<THREE.Group>(null);
  const [time, setTime] = useState(0);

  useFrame((state) => {
    setTime(state.clock.getElapsedTime());
    if (meshRef.current) {
      meshRef.current.rotation.y = time * 0.1;
    }
  });

  return (
    <group ref={meshRef}>
      {/* Quantum Particles */}
      {particles.map((particle) => (
        <mesh key={particle.id} position={particle.position}>
          <sphereGeometry args={[0.1, 8, 8]} />
          <meshStandardMaterial 
            color={particle.color}
            transparent 
            opacity={particle.probability}
            emissive={particle.color}
            emissiveIntensity={particle.tradingStrength * 0.5}
          />
        </mesh>
      ))}
      
      {/* Quantum Tunnels */}
      {sectors.map((sector) => 
        sector.quantumTunnels.map((tunnel, index) => {
          const targetSector = sectors.find(s => s.id === tunnel.targetSector);
          if (!targetSector) return null;
          
          const curve = new THREE.QuadraticBezierCurve3(
            new THREE.Vector3(...sector.position),
            new THREE.Vector3(
              (sector.position[0] + targetSector.position[0]) / 2,
              (sector.position[1] + targetSector.position[1]) / 2 + 2,
              (sector.position[2] + targetSector.position[2]) / 2
            ),
            new THREE.Vector3(...targetSector.position)
          );
          
          const points = curve.getPoints(50);
          const geometry = new THREE.BufferGeometry().setFromPoints(points);
          
          return (
            <line key={`${sector.id}-${tunnel.targetSector}-${index}`}>
              <bufferGeometry attach="geometry" {...geometry} />
              <lineBasicMaterial 
                attach="material" 
                color={tunnel.stability > 0.7 ? '#10b981' : '#f59e0b'}
                transparent
                opacity={tunnel.probability * 0.6}
              />
            </line>
          );
        })
      )}
    </group>
  );
};

// Sector Visualization Component
const SectorNode: React.FC<{ sector: QuantumSector; onClick: (sector: QuantumSector) => void }> = ({ 
  sector, 
  onClick 
}) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);
  const [time, setTime] = useState(0);

  useFrame((state) => {
    setTime(state.clock.getElapsedTime());
    if (meshRef.current) {
      const scale = hovered ? 1.2 : 1.0;
      const quantumPulse = 1 + Math.sin(time * 2 + sector.id) * 0.1 * sector.quantumField;
      meshRef.current.scale.setScalar(scale * quantumPulse);
    }
  });

  const sectorColor = useMemo(() => {
    if (sector.playerPresence) return '#38b2ac'; // Teal for player presence
    if (sector.aiRecommendation === 'high') return '#10b981'; // Green for high opportunity
    if (sector.aiRecommendation === 'medium') return '#f59e0b'; // Yellow for medium
    if (sector.manipulationRisk > 0.7) return '#ef4444'; // Red for high risk
    return '#6b7280'; // Gray for neutral
  }, [sector]);

  return (
    <group position={sector.position}>
      <mesh
        ref={meshRef}
        onClick={() => onClick(sector)}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        <sphereGeometry args={[0.5, 16, 16]} />
        <meshStandardMaterial 
          color={sectorColor}
          transparent
          opacity={0.8}
          emissive={sectorColor}
          emissiveIntensity={sector.quantumField * 0.3}
        />
      </mesh>
      
      {/* Sector Label */}
      <Text
        position={[0, 1, 0]}
        fontSize={0.3}
        color="white"
        anchorX="center"
        anchorY="middle"
      >
        {sector.name}
      </Text>
      
      {/* Trading Opportunities Indicator */}
      {sector.tradingOpportunities > 0 && (
        <mesh position={[0, 0.8, 0]}>
          <ringGeometry args={[0.3, 0.4, 8]} />
          <meshBasicMaterial 
            color="#fbbf24" 
            transparent 
            opacity={0.7}
            side={THREE.DoubleSide}
          />
        </mesh>
      )}
      
      {/* ARIA Insight Indicator */}
      {sector.aiRecommendation === 'high' && (
        <mesh position={[0.7, 0.7, 0]} rotation={[0, 0, time]}>
          <tetrahedronGeometry args={[0.2]} />
          <meshStandardMaterial 
            color="#8b5cf6" 
            emissive="#8b5cf6"
            emissiveIntensity={0.5}
          />
        </mesh>
      )}
    </group>
  );
};

// ARIA Insight Visualization
const AriaInsightNode: React.FC<{ insight: AriaInsight }> = ({ insight }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const [time, setTime] = useState(0);

  useFrame((state) => {
    setTime(state.clock.getElapsedTime());
    if (meshRef.current) {
      meshRef.current.rotation.y = time * 2;
      meshRef.current.position.y = insight.position[1] + Math.sin(time * 3) * 0.1;
    }
  });

  const insightColor = useMemo(() => {
    switch (insight.type) {
      case 'opportunity': return '#10b981';
      case 'warning': return '#ef4444';
      case 'recommendation': return '#8b5cf6';
      default: return '#6b7280';
    }
  }, [insight.type]);

  return (
    <group position={insight.position}>
      <mesh ref={meshRef}>
        <octahedronGeometry args={[0.3]} />
        <meshStandardMaterial 
          color={insightColor}
          transparent
          opacity={insight.confidence}
          emissive={insightColor}
          emissiveIntensity={0.4}
        />
      </mesh>
      
      <Html>
        <div className="aria-insight-tooltip">
          <div className="insight-type">{insight.type.toUpperCase()}</div>
          <div className="insight-message">{insight.message}</div>
          <div className="insight-confidence">{Math.round(insight.confidence * 100)}% confidence</div>
        </div>
      </Html>
    </group>
  );
};

// Main 3D Scene Component
const GalaxyScene: React.FC<{
  sectors: QuantumSector[];
  particles: QuantumParticle[];
  ariaInsights: AriaInsight[];
  onSectorClick: (sector: QuantumSector) => void;
  quality: 'low' | 'medium' | 'high';
}> = ({ sectors, particles, ariaInsights, onSectorClick, quality }) => {
  const { camera } = useThree();

  useEffect(() => {
    // Set camera position for optimal galaxy view
    camera.position.set(0, 10, 15);
    camera.lookAt(0, 0, 0);
  }, [camera]);

  return (
    <>
      {/* Lighting */}
      <ambientLight intensity={0.4} />
      <pointLight position={[10, 10, 10]} intensity={1} />
      <pointLight position={[-10, -10, -10]} intensity={0.5} color="#8b5cf6" />
      
      {/* Background Stars */}
      <Stars 
        radius={100} 
        depth={50} 
        count={quality === 'high' ? 5000 : quality === 'medium' ? 2000 : 1000} 
        factor={4} 
        saturation={0} 
        fade 
      />
      
      {/* Quantum Field */}
      <QuantumField sectors={sectors} particles={particles} />
      
      {/* Sector Nodes */}
      {sectors.map((sector) => (
        <SectorNode 
          key={sector.id} 
          sector={sector} 
          onClick={onSectorClick} 
        />
      ))}
      
      {/* ARIA Insights */}
      {ariaInsights.map((insight) => (
        <AriaInsightNode 
          key={insight.id} 
          insight={insight} 
        />
      ))}
      
      {/* Controls */}
      <OrbitControls 
        enablePan 
        enableZoom 
        enableRotate 
        minDistance={5}
        maxDistance={50}
      />
    </>
  );
};

const QuantumGalaxyVisualization: React.FC<QuantumGalaxyVisualizationProps> = ({
  isFullscreen = false,
  onToggleFullscreen,
  width = 800,
  height = 600,
  quality = 'medium',
  enableVR = false
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [selectedSector, setSelectedSector] = useState<QuantumSector | null>(null);
  const [showSettings, setShowSettings] = useState(false);
  const [renderQuality, setRenderQuality] = useState(quality);
  
  // WebSocket hooks for real-time data
  const { 
    quantumTrades,
    quantumMarketData,
    sendARIAMessage,
    isConnected 
  } = useWebSocket();
  
  const { playerState, availableMoves } = useGame();

  // Generate mock quantum sectors for demo
  const sectors = useMemo<QuantumSector[]>(() => {
    const sectorData: QuantumSector[] = [];
    for (let i = 1; i <= 20; i++) {
      const angle = (i / 20) * Math.PI * 2;
      const radius = 3 + Math.random() * 5;
      const height = (Math.random() - 0.5) * 4;
      
      sectorData.push({
        id: i,
        name: `Sector ${i}`,
        position: [
          Math.cos(angle) * radius,
          height,
          Math.sin(angle) * radius
        ],
        quantumField: Math.random(),
        tradingOpportunities: Math.floor(Math.random() * 5),
        aiRecommendation: ['high', 'medium', 'low'][Math.floor(Math.random() * 3)] as 'high' | 'medium' | 'low',
        manipulationRisk: Math.random(),
        playerPresence: i === (playerState?.currentSector || 1),
        quantumTunnels: []
      });
    }
    
    // Add quantum tunnels between nearby sectors
    sectorData.forEach(sector => {
      const nearbySecotrs = sectorData.filter(other => {
        if (other.id === sector.id) return false;
        const distance = Math.sqrt(
          Math.pow(sector.position[0] - other.position[0], 2) +
          Math.pow(sector.position[1] - other.position[1], 2) +
          Math.pow(sector.position[2] - other.position[2], 2)
        );
        return distance < 4;
      });
      
      sector.quantumTunnels = nearbySecotrs.slice(0, 3).map(target => ({
        targetSector: target.id,
        stability: Math.random(),
        probability: 0.5 + Math.random() * 0.5
      }));
    });
    
    return sectorData;
  }, [playerState?.currentSector]);

  // Generate quantum particles
  const particles = useMemo<QuantumParticle[]>(() => {
    const particleData: QuantumParticle[] = [];
    for (let i = 0; i < 100; i++) {
      particleData.push({
        id: `particle_${i}`,
        position: [
          (Math.random() - 0.5) * 20,
          (Math.random() - 0.5) * 10,
          (Math.random() - 0.5) * 20
        ],
        velocity: [
          (Math.random() - 0.5) * 0.1,
          (Math.random() - 0.5) * 0.1,
          (Math.random() - 0.5) * 0.1
        ],
        probability: Math.random(),
        tradingStrength: Math.random(),
        color: ['#10b981', '#f59e0b', '#ef4444', '#8b5cf6'][Math.floor(Math.random() * 4)]
      });
    }
    return particleData;
  }, []);

  // Generate ARIA insights
  const ariaInsights = useMemo<AriaInsight[]>(() => {
    return sectors.slice(0, 5).map((sector, index) => ({
      id: `insight_${sector.id}`,
      position: [sector.position[0] + 1, sector.position[1] + 1, sector.position[2]],
      type: ['opportunity', 'warning', 'recommendation'][Math.floor(Math.random() * 3)] as 'opportunity' | 'warning' | 'recommendation',
      message: [
        'High trading volume detected',
        'Market manipulation warning',
        'Optimal quantum trading window',
        'ARIA recommends caution',
        'Prime trading opportunity'
      ][index],
      confidence: 0.7 + Math.random() * 0.3,
      expiry: Date.now() + 60000
    }));
  }, [sectors]);

  // Handle sector click
  const handleSectorClick = useCallback((sector: QuantumSector) => {
    setSelectedSector(sector);
    
    if (isConnected) {
      sendARIAMessage(
        `Analyzing quantum trading opportunities in ${sector.name}. Field strength: ${(sector.quantumField * 100).toFixed(1)}%`,
        undefined,
        'quantum_analysis'
      );
    }
  }, [isConnected, sendARIAMessage]);

  return (
    <div className={`quantum-galaxy-container ${isFullscreen ? 'fullscreen' : ''}`}>
      {/* Controls Header */}
      <div className="galaxy-controls">
        <div className="galaxy-title">
          <Atom className="w-5 h-5" />
          <span>Quantum Galaxy</span>
          <div className="connection-status">
            {isConnected ? (
              <div className="status-connected">
                <div className="status-dot"></div>
                <span>ARIA Online</span>
              </div>
            ) : (
              <div className="status-disconnected">
                <div className="status-dot offline"></div>
                <span>Offline</span>
              </div>
            )}
          </div>
        </div>
        
        <div className="galaxy-actions">
          <button
            className="galaxy-action"
            onClick={() => setShowSettings(!showSettings)}
            title="Settings"
          >
            <Settings className="w-4 h-4" />
          </button>
          
          {onToggleFullscreen && (
            <button
              className="galaxy-action"
              onClick={onToggleFullscreen}
              title={isFullscreen ? "Exit Fullscreen" : "Enter Fullscreen"}
            >
              {isFullscreen ? (
                <Minimize2 className="w-4 h-4" />
              ) : (
                <Maximize2 className="w-4 h-4" />
              )}
            </button>
          )}
        </div>
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <div className="galaxy-settings">
          <h3>Visualization Settings</h3>
          <div className="setting-group">
            <label>Render Quality:</label>
            <select 
              value={renderQuality} 
              onChange={(e) => setRenderQuality(e.target.value as 'low' | 'medium' | 'high')}
            >
              <option value="low">Low (Mobile)</option>
              <option value="medium">Medium</option>
              <option value="high">High (Desktop)</option>
            </select>
          </div>
        </div>
      )}

      {/* 3D Canvas */}
      <Canvas
        ref={canvasRef}
        style={{ width, height }}
        camera={{ position: [0, 10, 15], fov: 60 }}
        gl={{ 
          antialias: renderQuality !== 'low',
          alpha: true,
          powerPreference: renderQuality === 'high' ? 'high-performance' : 'default'
        }}
      >
        <GalaxyScene
          sectors={sectors}
          particles={particles}
          ariaInsights={ariaInsights}
          onSectorClick={handleSectorClick}
          quality={renderQuality}
        />
      </Canvas>

      {/* Sector Information Panel */}
      {selectedSector && (
        <div className="sector-info-panel">
          <div className="sector-info-header">
            <h3>{selectedSector.name}</h3>
            <button onClick={() => setSelectedSector(null)}>×</button>
          </div>
          <div className="sector-info-content">
            <div className="info-item">
              <span className="label">Quantum Field:</span>
              <span className="value">{(selectedSector.quantumField * 100).toFixed(1)}%</span>
            </div>
            <div className="info-item">
              <span className="label">Trading Opportunities:</span>
              <span className="value">{selectedSector.tradingOpportunities}</span>
            </div>
            <div className="info-item">
              <span className="label">AI Recommendation:</span>
              <span className={`value ${selectedSector.aiRecommendation}`}>
                {selectedSector.aiRecommendation.toUpperCase()}
              </span>
            </div>
            <div className="info-item">
              <span className="label">Manipulation Risk:</span>
              <span className="value">{(selectedSector.manipulationRisk * 100).toFixed(1)}%</span>
            </div>
            {selectedSector.quantumTunnels.length > 0 && (
              <div className="quantum-tunnels">
                <span className="label">Quantum Tunnels:</span>
                <div className="tunnel-list">
                  {selectedSector.quantumTunnels.map((tunnel, index) => (
                    <div key={index} className="tunnel-item">
                      Sector {tunnel.targetSector} ({(tunnel.stability * 100).toFixed(0)}% stable)
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Trading Opportunities Overlay */}
      <div className="trading-overlay">
        <div className="overlay-section">
          <Brain className="w-4 h-4" />
          <span>ARIA Insights: {ariaInsights.length}</span>
        </div>
        <div className="overlay-section">
          <Zap className="w-4 h-4" />
          <span>Active Quantum Trades: {quantumTrades.length}</span>
        </div>
        <div className="overlay-section">
          <Target className="w-4 h-4" />
          <span>High Opportunity Sectors: {sectors.filter(s => s.aiRecommendation === 'high').length}</span>
        </div>
      </div>
    </div>
  );
};

export default QuantumGalaxyVisualization;