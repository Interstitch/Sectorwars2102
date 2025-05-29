import React, { useState, useMemo, useCallback } from 'react';
import { Ship } from '../../types/game';
import { InputValidator } from '../../utils/security/inputValidation';
import './insurance-manager.css';

interface InsurancePolicy {
  id: string;
  name: string;
  tier: 'basic' | 'standard' | 'premium' | 'elite';
  coverage: number; // Percentage of ship value covered
  premium: number; // Monthly cost
  deductible: number; // Amount player pays on claim
  benefits: string[];
  restrictions: string[];
  active: boolean;
  expiresAt?: string;
}

interface InsuranceClaim {
  id: string;
  date: string;
  type: 'combat' | 'collision' | 'theft' | 'malfunction';
  description: string;
  damageAmount: number;
  claimAmount: number;
  status: 'pending' | 'approved' | 'denied' | 'paid';
  policyId: string;
}

interface InsuranceManagerProps {
  ship: Ship;
  shipValue: number;
  playerCredits: number;
  currentPolicy?: InsurancePolicy;
  claimHistory?: InsuranceClaim[];
  onPurchasePolicy?: (policy: InsurancePolicy) => void;
  onCancelPolicy?: () => void;
  onFileClaim?: (claim: Partial<InsuranceClaim>) => void;
}

const INSURANCE_POLICIES: InsurancePolicy[] = [
  {
    id: 'basic',
    name: 'Basic Protection',
    tier: 'basic',
    coverage: 50,
    premium: 500,
    deductible: 5000,
    benefits: [
      'Combat damage coverage',
      'Emergency towing',
      'Basic parts replacement'
    ],
    restrictions: [
      'No coverage in hostile sectors',
      'Limited to 1 claim per month',
      'Does not cover modifications'
    ],
    active: false
  },
  {
    id: 'standard',
    name: 'Standard Coverage',
    tier: 'standard',
    coverage: 75,
    premium: 1200,
    deductible: 2500,
    benefits: [
      'All Basic benefits',
      'Theft protection',
      'Modification coverage (50%)',
      'Priority repairs'
    ],
    restrictions: [
      'Limited hostile sector coverage',
      'Up to 2 claims per month',
      'Pre-authorization required for major repairs'
    ],
    active: false
  },
  {
    id: 'premium',
    name: 'Premium Shield',
    tier: 'premium',
    coverage: 90,
    premium: 2500,
    deductible: 1000,
    benefits: [
      'All Standard benefits',
      'Full hostile sector coverage',
      'Modification coverage (100%)',
      'Rental ship during repairs',
      'Legal assistance'
    ],
    restrictions: [
      'Up to 3 claims per month',
      'Excludes intentional damage'
    ],
    active: false
  },
  {
    id: 'elite',
    name: 'Elite Guarantee',
    tier: 'elite',
    coverage: 100,
    premium: 5000,
    deductible: 0,
    benefits: [
      'All Premium benefits',
      'Zero deductible',
      'Unlimited claims',
      'New ship replacement option',
      'Personal claims adjuster',
      'Preventive maintenance included'
    ],
    restrictions: [
      'Background check required',
      'Minimum 6-month commitment'
    ],
    active: false
  }
];

const InsuranceManager: React.FC<InsuranceManagerProps> = ({
  ship,
  shipValue,
  playerCredits,
  currentPolicy,
  claimHistory = [],
  onPurchasePolicy,
  onCancelPolicy,
  onFileClaim
}) => {
  const [selectedPolicy, setSelectedPolicy] = useState<string | null>(currentPolicy?.id || null);
  const [showClaimForm, setShowClaimForm] = useState(false);
  const [claimType, setClaimType] = useState<InsuranceClaim['type']>('combat');
  const [claimDescription, setClaimDescription] = useState('');
  const [estimatedDamage, setEstimatedDamage] = useState(0);
  const [lastAction, setLastAction] = useState<number>(0);

  // Rate limiting
  const RATE_LIMIT_MS = 1000;
  const canPerformAction = useCallback(() => {
    const now = Date.now();
    if (now - lastAction < RATE_LIMIT_MS) {
      return false;
    }
    setLastAction(now);
    return true;
  }, [lastAction]);

  // Calculate claim statistics
  const claimStats = useMemo(() => {
    const totalClaims = claimHistory.length;
    const approvedClaims = claimHistory.filter(c => c.status === 'approved' || c.status === 'paid').length;
    const totalPaid = claimHistory
      .filter(c => c.status === 'paid')
      .reduce((sum, c) => sum + c.claimAmount, 0);
    const averageClaim = totalPaid / (approvedClaims || 1);
    
    return {
      totalClaims,
      approvedClaims,
      totalPaid,
      averageClaim,
      approvalRate: totalClaims > 0 ? (approvedClaims / totalClaims) * 100 : 0
    };
  }, [claimHistory]);

  // Calculate potential claim amount
  const potentialClaimAmount = useMemo(() => {
    if (!currentPolicy || !estimatedDamage) return 0;
    
    const coveredAmount = (estimatedDamage * currentPolicy.coverage) / 100;
    const afterDeductible = Math.max(0, coveredAmount - currentPolicy.deductible);
    return Math.min(afterDeductible, shipValue);
  }, [currentPolicy, estimatedDamage, shipValue]);

  const purchasePolicy = useCallback((policy: InsurancePolicy) => {
    if (!canPerformAction() || !onPurchasePolicy) return;

    if (policy.premium > playerCredits) {
      alert('Insufficient credits for this policy!');
      return;
    }

    if (currentPolicy && currentPolicy.tier === 'elite' && policy.tier !== 'elite') {
      if (!window.confirm('Downgrading from Elite will result in loss of benefits. Continue?')) {
        return;
      }
    }

    onPurchasePolicy(policy);
    setSelectedPolicy(policy.id);
  }, [canPerformAction, onPurchasePolicy, playerCredits, currentPolicy]);

  const cancelPolicy = useCallback(() => {
    if (!canPerformAction() || !onCancelPolicy || !currentPolicy) return;

    if (!window.confirm('Are you sure you want to cancel your insurance? You will lose all coverage immediately.')) {
      return;
    }

    onCancelPolicy();
    setSelectedPolicy(null);
  }, [canPerformAction, onCancelPolicy, currentPolicy]);

  const fileClaim = useCallback(() => {
    if (!canPerformAction() || !onFileClaim || !currentPolicy) return;

    const sanitizedDescription = InputValidator.sanitizeText(claimDescription);
    if (!sanitizedDescription || sanitizedDescription.length < 10) {
      alert('Please provide a detailed description (at least 10 characters)');
      return;
    }

    if (estimatedDamage <= 0) {
      alert('Please enter a valid damage estimate');
      return;
    }

    const newClaim: Partial<InsuranceClaim> = {
      date: new Date().toISOString(),
      type: claimType,
      description: sanitizedDescription,
      damageAmount: estimatedDamage,
      claimAmount: potentialClaimAmount,
      status: 'pending',
      policyId: currentPolicy.id
    };

    onFileClaim(newClaim);
    setShowClaimForm(false);
    setClaimDescription('');
    setEstimatedDamage(0);
  }, [canPerformAction, onFileClaim, currentPolicy, claimType, claimDescription, 
      estimatedDamage, potentialClaimAmount]);

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'basic': return '#888888';
      case 'standard': return '#4a9eff';
      case 'premium': return '#ff44ff';
      case 'elite': return '#ffaa44';
      default: return '#ffffff';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return '#44ff44';
      case 'paid': return '#44ff44';
      case 'pending': return '#ffaa44';
      case 'denied': return '#ff4444';
      default: return '#ffffff';
    }
  };

  return (
    <div className="insurance-manager">
      <div className="manager-header">
        <h3>Ship Insurance</h3>
        <div className="ship-info">
          <span className="ship-name">{ship.name}</span>
          <span className="ship-value">Value: {shipValue.toLocaleString()} cr</span>
        </div>
      </div>

      {currentPolicy && (
        <div className="current-policy">
          <div className="policy-header">
            <h4>Current Policy</h4>
            <span 
              className="policy-tier"
              style={{ backgroundColor: getTierColor(currentPolicy.tier) }}
            >
              {currentPolicy.tier.toUpperCase()}
            </span>
          </div>
          
          <div className="policy-details">
            <div className="detail-item">
              <label>Coverage:</label>
              <span>{currentPolicy.coverage}% of ship value</span>
            </div>
            <div className="detail-item">
              <label>Premium:</label>
              <span>{currentPolicy.premium.toLocaleString()} cr/month</span>
            </div>
            <div className="detail-item">
              <label>Deductible:</label>
              <span>{currentPolicy.deductible.toLocaleString()} cr</span>
            </div>
            <div className="detail-item">
              <label>Max Payout:</label>
              <span>{((shipValue * currentPolicy.coverage) / 100).toLocaleString()} cr</span>
            </div>
          </div>
          
          <div className="policy-actions">
            <button 
              className="file-claim-btn"
              onClick={() => setShowClaimForm(true)}
            >
              File Claim
            </button>
            {onCancelPolicy && (
              <button 
                className="cancel-policy-btn"
                onClick={cancelPolicy}
              >
                Cancel Policy
              </button>
            )}
          </div>
        </div>
      )}

      <div className="available-policies">
        <h4>Available Policies</h4>
        <div className="policies-grid">
          {INSURANCE_POLICIES.map(policy => {
            const isCurrentPolicy = currentPolicy?.id === policy.id;
            const canAfford = policy.premium <= playerCredits;
            
            return (
              <div 
                key={policy.id}
                className={`policy-card ${policy.tier} ${isCurrentPolicy ? 'current' : ''} ${!canAfford ? 'unaffordable' : ''}`}
              >
                <div className="policy-card-header">
                  <h5>{policy.name}</h5>
                  <span 
                    className="tier-badge"
                    style={{ backgroundColor: getTierColor(policy.tier) }}
                  >
                    {policy.tier.toUpperCase()}
                  </span>
                </div>
                
                <div className="policy-stats">
                  <div className="stat">
                    <span className="stat-value">{policy.coverage}%</span>
                    <span className="stat-label">Coverage</span>
                  </div>
                  <div className="stat">
                    <span className="stat-value">{policy.premium.toLocaleString()}</span>
                    <span className="stat-label">cr/month</span>
                  </div>
                  <div className="stat">
                    <span className="stat-value">{policy.deductible.toLocaleString()}</span>
                    <span className="stat-label">Deductible</span>
                  </div>
                </div>
                
                <div className="policy-benefits">
                  <h6>Benefits:</h6>
                  <ul>
                    {policy.benefits.map((benefit, index) => (
                      <li key={index}>{benefit}</li>
                    ))}
                  </ul>
                </div>
                
                <div className="policy-restrictions">
                  <h6>Restrictions:</h6>
                  <ul>
                    {policy.restrictions.map((restriction, index) => (
                      <li key={index}>{restriction}</li>
                    ))}
                  </ul>
                </div>
                
                {!isCurrentPolicy && onPurchasePolicy && (
                  <button 
                    className="purchase-btn"
                    onClick={() => purchasePolicy(policy)}
                    disabled={!canAfford}
                  >
                    {canAfford ? 'Purchase' : 'Insufficient Credits'}
                  </button>
                )}
                
                {isCurrentPolicy && (
                  <div className="current-indicator">✓ Current Policy</div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {claimHistory.length > 0 && (
        <div className="claim-history">
          <h4>Claim History</h4>
          
          <div className="claim-stats">
            <div className="stat-card">
              <span className="stat-value">{claimStats.totalClaims}</span>
              <span className="stat-label">Total Claims</span>
            </div>
            <div className="stat-card">
              <span className="stat-value">{claimStats.approvalRate.toFixed(0)}%</span>
              <span className="stat-label">Approval Rate</span>
            </div>
            <div className="stat-card">
              <span className="stat-value">{claimStats.totalPaid.toLocaleString()}</span>
              <span className="stat-label">Total Paid</span>
            </div>
            <div className="stat-card">
              <span className="stat-value">{claimStats.averageClaim.toLocaleString()}</span>
              <span className="stat-label">Avg Claim</span>
            </div>
          </div>
          
          <div className="claims-list">
            {claimHistory.slice(0, 5).map(claim => (
              <div key={claim.id} className="claim-item">
                <div className="claim-date">
                  {new Date(claim.date).toLocaleDateString()}
                </div>
                <div className="claim-info">
                  <div className="claim-type">{claim.type}</div>
                  <div className="claim-description">{claim.description}</div>
                </div>
                <div className="claim-amounts">
                  <span className="damage-amount">
                    Damage: {claim.damageAmount.toLocaleString()} cr
                  </span>
                  <span className="claim-amount">
                    Claim: {claim.claimAmount.toLocaleString()} cr
                  </span>
                </div>
                <div 
                  className="claim-status"
                  style={{ color: getStatusColor(claim.status) }}
                >
                  {claim.status.toUpperCase()}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {showClaimForm && currentPolicy && (
        <div className="claim-form-overlay">
          <div className="claim-form">
            <h4>File Insurance Claim</h4>
            
            <div className="form-group">
              <label>Claim Type</label>
              <select 
                value={claimType}
                onChange={(e) => setClaimType(e.target.value as InsuranceClaim['type'])}
              >
                <option value="combat">Combat Damage</option>
                <option value="collision">Collision</option>
                <option value="theft">Theft</option>
                <option value="malfunction">System Malfunction</option>
              </select>
            </div>
            
            <div className="form-group">
              <label>Description</label>
              <textarea
                value={claimDescription}
                onChange={(e) => setClaimDescription(e.target.value)}
                placeholder="Provide detailed description of the incident..."
                rows={4}
                maxLength={500}
              />
            </div>
            
            <div className="form-group">
              <label>Estimated Damage (credits)</label>
              <input
                type="number"
                value={estimatedDamage}
                onChange={(e) => setEstimatedDamage(Math.max(0, parseInt(e.target.value) || 0))}
                min="0"
                max={shipValue}
              />
            </div>
            
            <div className="claim-calculation">
              <div className="calc-row">
                <span>Damage Amount:</span>
                <span>{estimatedDamage.toLocaleString()} cr</span>
              </div>
              <div className="calc-row">
                <span>Coverage ({currentPolicy.coverage}%):</span>
                <span>{((estimatedDamage * currentPolicy.coverage) / 100).toLocaleString()} cr</span>
              </div>
              <div className="calc-row">
                <span>Deductible:</span>
                <span>-{currentPolicy.deductible.toLocaleString()} cr</span>
              </div>
              <div className="calc-row total">
                <span>Estimated Payout:</span>
                <span>{potentialClaimAmount.toLocaleString()} cr</span>
              </div>
            </div>
            
            <div className="form-actions">
              <button 
                className="submit-claim-btn"
                onClick={fileClaim}
                disabled={!claimDescription || estimatedDamage <= 0}
              >
                Submit Claim
              </button>
              <button 
                className="cancel-btn"
                onClick={() => {
                  setShowClaimForm(false);
                  setClaimDescription('');
                  setEstimatedDamage(0);
                }}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default InsuranceManager;