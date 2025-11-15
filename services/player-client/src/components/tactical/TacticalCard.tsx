import React, { ReactNode } from 'react';
import './tactical-card.css';

interface TacticalCardProps {
  title?: string;
  icon?: string;
  children: ReactNode;
  className?: string;
  collapsible?: boolean;
  defaultCollapsed?: boolean;
  glowColor?: 'cyan' | 'green' | 'red' | 'amber' | 'purple';
}

const TacticalCard: React.FC<TacticalCardProps> = ({
  title,
  icon,
  children,
  className = '',
  collapsible = false,
  defaultCollapsed = false,
  glowColor = 'cyan'
}) => {
  const [isCollapsed, setIsCollapsed] = React.useState(defaultCollapsed);

  const toggleCollapse = () => {
    if (collapsible) {
      setIsCollapsed(!isCollapsed);
    }
  };

  return (
    <div className={`tactical-card glow-${glowColor} ${className}`}>
      {title && (
        <div
          className={`tactical-card-header ${collapsible ? 'clickable' : ''}`}
          onClick={toggleCollapse}
        >
          {icon && <span className="tactical-card-icon">{icon}</span>}
          <h3 className="tactical-card-title">{title}</h3>
          {collapsible && (
            <span className="collapse-indicator">
              {isCollapsed ? '▼' : '▲'}
            </span>
          )}
        </div>
      )}
      <div className={`tactical-card-content ${isCollapsed ? 'collapsed' : ''}`}>
        {children}
      </div>
    </div>
  );
};

export default TacticalCard;
