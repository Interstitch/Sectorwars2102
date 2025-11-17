import React from 'react';

interface TrustMeterProps {
  trustLevel: number; // 0.0 to 1.0
  guardName?: string;
}

/**
 * Trust Meter - Visual indicator of guard's current mood/trust level
 *
 * Shows real-time feedback on how the guard perceives the player's responses.
 * Color-coded from red (suspicious) to green (convinced).
 */
const TrustMeter: React.FC<TrustMeterProps> = ({ trustLevel, guardName }) => {
  // Clamp trust level between 0 and 1
  const clampedTrust = Math.max(0, Math.min(1, trustLevel));
  const percentage = Math.round(clampedTrust * 100);

  // Determine color based on trust level
  let color: string;
  let mood: string;
  let moodIcon: string;

  if (clampedTrust < 0.3) {
    color = '#e74c3c'; // Red
    mood = 'Very Suspicious';
    moodIcon = '😠';
  } else if (clampedTrust < 0.5) {
    color = '#e67e22'; // Orange
    mood = 'Skeptical';
    moodIcon = '🤨';
  } else if (clampedTrust < 0.7) {
    color = '#f39c12'; // Yellow
    mood = 'Neutral';
    moodIcon = '😐';
  } else if (clampedTrust < 0.85) {
    color = '#2ecc71'; // Green
    mood = 'Accepting';
    moodIcon = '🙂';
  } else {
    color = '#27ae60'; // Dark Green
    mood = 'Convinced';
    moodIcon = '😊';
  }

  return (
    <div style={{
      marginBottom: '20px',
      padding: '15px',
      background: 'rgba(0, 0, 0, 0.3)',
      borderRadius: '8px',
      border: '1px solid rgba(255, 255, 255, 0.1)'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '8px'
      }}>
        <div style={{ fontSize: '0.9em', color: '#aaa' }}>
          {guardName ? `${guardName}'s Assessment` : 'Guard Assessment'}
        </div>
        <div style={{ fontSize: '1.2em' }}>
          {moodIcon}
        </div>
      </div>

      {/* Trust bar */}
      <div style={{
        width: '100%',
        height: '12px',
        background: 'rgba(0, 0, 0, 0.5)',
        borderRadius: '6px',
        overflow: 'hidden',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        position: 'relative'
      }}>
        <div style={{
          width: `${percentage}%`,
          height: '100%',
          background: `linear-gradient(90deg, ${color}, ${color}dd)`,
          transition: 'width 0.5s ease-out, background 0.3s ease-out',
          boxShadow: `0 0 10px ${color}66`
        }} />
      </div>

      {/* Mood label */}
      <div style={{
        marginTop: '8px',
        fontSize: '0.85em',
        color: color,
        fontWeight: 'bold',
        textAlign: 'center',
        transition: 'color 0.3s ease-out'
      }}>
        {mood} ({percentage}%)
      </div>
    </div>
  );
};

export default TrustMeter;
