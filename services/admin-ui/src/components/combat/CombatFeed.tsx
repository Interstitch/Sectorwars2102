import React, { useEffect, useRef } from 'react';

interface CombatEvent {
  id: string;
  timestamp: string;
  type: 'player_vs_player' | 'player_vs_npc' | 'fleet_battle';
  attacker: string;
  defender: string;
  winner?: string;
  damageDealt: number;
  disputed?: boolean;
  sector: string;
}

interface CombatFeedProps {
  events: CombatEvent[];
  onDisputeClick?: (eventId: string) => void;
  onInterventionClick?: (eventId: string) => void;
}

export const CombatFeed: React.FC<CombatFeedProps> = ({
  events,
  onDisputeClick,
  onInterventionClick
}) => {
  const feedRef = useRef<HTMLDivElement>(null);
  const isAutoScrolling = useRef(true);

  useEffect(() => {
    // Auto-scroll to bottom when new events arrive
    if (feedRef.current && isAutoScrolling.current) {
      feedRef.current.scrollTop = feedRef.current.scrollHeight;
    }
  }, [events]);

  const handleScroll = () => {
    if (feedRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = feedRef.current;
      // Check if user has scrolled away from bottom
      isAutoScrolling.current = scrollHeight - scrollTop - clientHeight < 50;
    }
  };

  const formatDuration = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}m ${secs}s`;
  };

  const formatTimestamp = (timestamp: string): string => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  };

  const getResultColor = (winner: string): string => {
    switch (winner) {
      case 'attacker': return 'combat-winner-attacker';
      case 'defender': return 'combat-winner-defender';
      default: return 'combat-winner-draw';
    }
  };

  return (
    <div className="combat-feed">
      <div className="combat-feed-header">
        <h3>Live Combat Feed</h3>
        <span className="combat-count">{events.length} battles</span>
      </div>
      
      <div 
        className="combat-feed-scroll" 
        ref={feedRef}
        onScroll={handleScroll}
      >
        {events.map((event) => (
          <div key={event.id} className="combat-event">
            <div className="combat-event-header">
              <span className="combat-time">{formatTimestamp(event.timestamp)}</span>
              <span className={`combat-result ${getResultColor(event.result.winner)}`}>
                {event.result.winner === 'draw' ? 'DRAW' : `${event.result.winner.toUpperCase()} WINS`}
              </span>
            </div>
            
            <div className="combat-participants">
              <div className="combat-attacker">
                <span className="participant-name">{event.attacker.name}</span>
                <span className="participant-ship">({event.attacker.ship})</span>
                <span className="participant-faction">[{event.attacker.faction}]</span>
              </div>
              
              <div className="combat-vs">VS</div>
              
              <div className="combat-defender">
                <span className="participant-name">{event.defender.name}</span>
                <span className="participant-ship">({event.defender.ship})</span>
                <span className="participant-faction">[{event.defender.faction}]</span>
              </div>
            </div>
            
            <div className="combat-details">
              <div className="combat-location">
                <i className="icon-location"></i>
                {event.sector.name} ({event.sector.coordinates.x}, {event.sector.coordinates.y}, {event.sector.coordinates.z})
              </div>
              
              <div className="combat-stats">
                <span className="stat-item">
                  <i className="icon-damage"></i>
                  Damage: {event.result.damageDealt.toLocaleString()} / {event.result.damageReceived.toLocaleString()}
                </span>
                
                {(event.result.shipsDestroyed.attacker > 0 || event.result.shipsDestroyed.defender > 0) && (
                  <span className="stat-item">
                    <i className="icon-destroyed"></i>
                    Ships Lost: {event.result.shipsDestroyed.attacker} / {event.result.shipsDestroyed.defender}
                  </span>
                )}
                
                {event.result.lootValue > 0 && (
                  <span className="stat-item">
                    <i className="icon-loot"></i>
                    Loot: ${event.result.lootValue.toLocaleString()}
                  </span>
                )}
                
                <span className="stat-item">
                  <i className="icon-duration"></i>
                  Duration: {formatDuration(event.duration)}
                </span>
              </div>
            </div>
            
            <div className="combat-actions">
              {event.disputeStatus === 'pending' && (
                <span className="dispute-badge">DISPUTED</span>
              )}
              
              <button 
                className="btn-action btn-dispute"
                onClick={() => onDisputeClick?.(event.id)}
                title="View dispute details"
              >
                <i className="icon-dispute"></i>
                Dispute
              </button>
              
              <button 
                className="btn-action btn-intervene"
                onClick={() => onInterventionClick?.(event.id)}
                title="Admin intervention"
              >
                <i className="icon-intervene"></i>
                Intervene
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};