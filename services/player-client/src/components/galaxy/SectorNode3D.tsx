import { useRef, useState, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { Text, Sphere, Box, Cylinder } from '@react-three/drei';
import { Vector3, Color } from 'three';
import { useSpring, a } from 'react-spring';
import * as THREE from 'three';

import { Sector } from '../../contexts/GameContext';

interface SectorNode3DProps {
  sector: Sector;
  position: Vector3;
  isSelected: boolean;
  isCurrent: boolean;
  onClick: (sector: Sector) => void;
  lodLevel: {
    detail: 'high' | 'medium' | 'low';
    showLabels: boolean;
    showEffects: boolean;
  };
  playerCount: number;
}

// Animated Three.js components
const AnimatedGroup = a.group;

export default function SectorNode3D({
  sector,
  position,
  isSelected,
  isCurrent,
  onClick,
  lodLevel,
  playerCount
}: SectorNode3DProps) {
  const groupRef = useRef<THREE.Group>(null);
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);

  // Sector type visual configuration
  const sectorConfig = useMemo(() => {
    const configs = {
      'normal': {
        color: '#4488ff',
        emissive: '#001122',
        geometry: 'sphere',
        scale: 1.0,
        glow: false
      },
      'nebula': {
        color: '#ff6644',
        emissive: '#220011',
        geometry: 'sphere',
        scale: 1.2,
        glow: true
      },
      'asteroid': {
        color: '#888844',
        emissive: '#111100',
        geometry: 'box',
        scale: 0.8,
        glow: false
      },
      'blackhole': {
        color: '#220022',
        emissive: '#440044',
        geometry: 'sphere',
        scale: 1.5,
        glow: true
      },
      'star': {
        color: '#ffff44',
        emissive: '#444400',
        geometry: 'sphere',
        scale: 1.3,
        glow: true
      },
      'wormhole': {
        color: '#4444ff',
        emissive: '#000044',
        geometry: 'cylinder',
        scale: 1.0,
        glow: true
      }
    };
    
    return configs[sector.type as keyof typeof configs] || configs.normal;
  }, [sector.type]);

  // Activity-based color intensity
  const activityIntensity = useMemo(() => {
    if (playerCount === 0) return 0.3;
    if (playerCount <= 2) return 0.6;
    if (playerCount <= 5) return 0.8;
    return 1.0;
  }, [playerCount]);

  // Animation springs
  const { scale, opacity, rotationY } = useSpring({
    scale: isSelected ? 1.3 : isCurrent ? 1.1 : hovered ? 1.05 : 1.0,
    opacity: lodLevel.detail === 'low' ? 0.7 : 1.0,
    rotationY: isCurrent ? Math.PI * 2 : 0,
    config: { mass: 1, tension: 280, friction: 60 }
  });

  // Continuous rotation for active sectors
  useFrame((state) => {
    if (meshRef.current && (isCurrent || playerCount > 0)) {
      meshRef.current.rotation.x += 0.01;
      meshRef.current.rotation.z += 0.005;
    }
    
    // Glow effect for special sector types
    if (meshRef.current && sectorConfig.glow && lodLevel.showEffects) {
      const time = state.clock.getElapsedTime();
      const intensity = 0.5 + Math.sin(time * 2) * 0.3;
      (meshRef.current.material as THREE.MeshStandardMaterial).emissiveIntensity = intensity;
    }
  });

  // Handle click events
  const handleClick = (event: any) => {
    event.stopPropagation();
    onClick(sector);
  };

  // Handle hover events
  const handlePointerOver = (event: any) => {
    event.stopPropagation();
    setHovered(true);
    document.body.style.cursor = 'pointer';
  };

  const handlePointerOut = () => {
    setHovered(false);
    document.body.style.cursor = 'auto';
  };

  // Color calculation based on state and activity
  const finalColor = useMemo(() => {
    const baseColor = new Color(sectorConfig.color);
    
    if (isCurrent) {
      return baseColor.clone().lerp(new Color('#00ff00'), 0.3);
    } else if (isSelected) {
      return baseColor.clone().lerp(new Color('#ffff00'), 0.3);
    } else if (hovered) {
      return baseColor.clone().lerp(new Color('#ffffff'), 0.2);
    }
    
    // Adjust based on activity
    return baseColor.clone().multiplyScalar(0.5 + activityIntensity * 0.5);
  }, [sectorConfig.color, isCurrent, isSelected, hovered, activityIntensity]);

  const emissiveColor = useMemo(() => {
    const baseEmissive = new Color(sectorConfig.emissive);
    return baseEmissive.clone().multiplyScalar(activityIntensity);
  }, [sectorConfig.emissive, activityIntensity]);

  // Geometry based on sector type and LOD
  const renderGeometry = () => {
    const size = sectorConfig.scale * (lodLevel.detail === 'low' ? 0.5 : 1.0);
    
    const material = (
      <a.meshStandardMaterial
        color={finalColor}
        emissive={emissiveColor}
        emissiveIntensity={sectorConfig.glow ? 0.3 : 0.1}
        metalness={0.3}
        roughness={0.7}
        transparent={true}
        opacity={opacity}
      />
    );

    switch (sectorConfig.geometry) {
      case 'box':
        return (
          <Box args={[size * 2, size * 2, size * 2]}>
            {material}
          </Box>
        );
      case 'cylinder':
        return (
          <Cylinder args={[size, size, size * 3, 16]}>
            {material}
          </Cylinder>
        );
      default:
        return (
          <Sphere args={[size, lodLevel.detail === 'low' ? 8 : 16, lodLevel.detail === 'low' ? 6 : 12]}>
            {material}
          </Sphere>
        );
    }
  };

  // Player count indicator
  const renderPlayerIndicator = () => {
    if (playerCount === 0 || !lodLevel.showEffects) return null;
    
    return (
      <group position={[0, sectorConfig.scale + 1, 0]}>
        <Sphere args={[0.2, 8, 6]}>
          <meshBasicMaterial color="#00ff00" />
        </Sphere>
        {lodLevel.showLabels && (
          <Text
            position={[0, 0.5, 0]}
            fontSize={0.3}
            color="#ffffff"
            anchorX="center"
            anchorY="middle"
          >
            {playerCount}
          </Text>
        )}
      </group>
    );
  };

  // Sector label
  const renderLabel = () => {
    if (!lodLevel.showLabels || lodLevel.detail === 'low') return null;
    
    return (
      <Text
        position={[0, -sectorConfig.scale - 1, 0]}
        fontSize={0.4}
        color={isCurrent ? "#00ff00" : isSelected ? "#ffff00" : "#ffffff"}
        anchorX="center"
        anchorY="middle"
        maxWidth={8}
        textAlign="center"
      >
        {sector.name}
      </Text>
    );
  };

  // Connection indicators (special features)
  const renderFeatureIndicators = () => {
    if (!lodLevel.showEffects || lodLevel.detail === 'low') return null;
    
    const indicators = [];
    let offset = 0;
    
    // Show special features if any
    if (sector.special_features && sector.special_features.length > 0) {
      indicators.push(
        <group key="features" position={[sectorConfig.scale + 0.5 + offset, 0, 0]}>
          <Box args={[0.2, 0.2, 0.2]}>
            <meshBasicMaterial color="#ffaa00" />
          </Box>
        </group>
      );
    }
    
    return indicators;
  };

  return (
    <AnimatedGroup
      ref={groupRef}
      position={position.toArray()}
      scale={scale}
      rotation-y={rotationY}
      onClick={handleClick}
      onPointerOver={handlePointerOver}
      onPointerOut={handlePointerOut}
    >
      {/* Main sector geometry */}
      <mesh ref={meshRef}>
        {renderGeometry()}
      </mesh>
      
      {/* Player count indicator */}
      {renderPlayerIndicator()}
      
      {/* Sector label */}
      {renderLabel()}
      
      {/* Feature indicators */}
      {renderFeatureIndicators()}
      
      {/* Selection ring */}
      {(isSelected || isCurrent) && lodLevel.showEffects && (
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <ringGeometry args={[sectorConfig.scale + 0.5, sectorConfig.scale + 0.7, 32]} />
          <meshBasicMaterial 
            color={isCurrent ? "#00ff00" : "#ffff00"} 
            transparent 
            opacity={0.6}
            side={THREE.DoubleSide}
          />
        </mesh>
      )}
    </AnimatedGroup>
  );
}