import { useMemo } from 'react';
import { Line } from '@react-three/drei';
import { Vector3 } from 'three';

interface ConnectionPath3DProps {
  start: Vector3;
  end: Vector3;
  type: 'warp' | 'tunnel';
  lodLevel: {
    detail: 'high' | 'medium' | 'low';
    showLabels: boolean;
    showEffects: boolean;
  };
}

export default function ConnectionPath3D({ start, end, type, lodLevel }: ConnectionPath3DProps) {
  // Generate curve points for the connection
  const points = useMemo(() => {
    if (lodLevel.detail === 'low') {
      // Simple straight line for low detail
      return [start, end];
    }
    
    // Curved path for better visual appeal
    const midPoint = start.clone().lerp(end, 0.5);
    const distance = start.distanceTo(end);
    
    // Add some curve variation
    const curve = new Vector3(
      (Math.random() - 0.5) * distance * 0.2,
      (Math.random() - 0.5) * distance * 0.2,
      (Math.random() - 0.5) * distance * 0.2
    );
    
    midPoint.add(curve);
    
    return [start, midPoint, end];
  }, [start, end, lodLevel.detail]);

  const color = type === 'tunnel' ? '#ff4444' : '#4488ff';
  const lineWidth = type === 'tunnel' ? 3 : 1;

  if (lodLevel.detail === 'low' && start.distanceTo(end) > 50) {
    return null; // Don't render distant connections in low detail
  }

  return (
    <Line
      points={points}
      color={color}
      lineWidth={lineWidth}
      transparent
      opacity={0.6}
    />
  );
}