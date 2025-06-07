import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import './paypal-subscription.css';

interface SubscriptionPlan {
  id: string;
  name: string;
  description: string;
  price: string;
  features: string[];
}

interface UserSubscription {
  subscription_id: string;
  type: string;
  region_name?: string;
  status: string;
  amount: string;
}

interface PayPalSubscriptionProps {
  onSubscriptionCreated?: (subscriptionId: string) => void;
  onSubscriptionCancelled?: (subscriptionId: string) => void;
}

const PayPalSubscription: React.FC<PayPalSubscriptionProps> = ({
  onSubscriptionCreated,
  onSubscriptionCancelled
}) => {
  const { user, token } = useAuth();
  const [plans, setPlans] = useState<SubscriptionPlan[]>([]);
  const [userSubscriptions, setUserSubscriptions] = useState<UserSubscription[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [regionName, setRegionName] = useState('');
  const [regionNameAvailable, setRegionNameAvailable] = useState<boolean | null>(null);
  const [regionNameError, setRegionNameError] = useState<string | null>(null);

  useEffect(() => {
    loadPlans();
    if (user) {
      loadUserSubscriptions();
    }
  }, [user]);

  const loadPlans = async () => {
    try {
      const response = await fetch('/api/v1/paypal/plans');
      if (response.ok) {
        const data = await response.json();
        setPlans(data.plans);
      }
    } catch (err) {
      console.error('Failed to load subscription plans:', err);
    }
  };

  const loadUserSubscriptions = async () => {
    if (!token) return;

    try {
      const response = await fetch('/api/v1/paypal/subscriptions', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setUserSubscriptions(data.subscriptions);
      }
    } catch (err) {
      console.error('Failed to load user subscriptions:', err);
    }
  };

  const checkRegionNameAvailability = async (name: string) => {
    if (!name || name.length < 3) {
      setRegionNameAvailable(null);
      setRegionNameError(null);
      return;
    }

    try {
      const response = await fetch(`/api/v1/paypal/regions/available-names?name=${encodeURIComponent(name)}`);
      if (response.ok) {
        const data = await response.json();
        setRegionNameAvailable(data.available);
        setRegionNameError(data.available ? null : data.reason);
      }
    } catch (err) {
      console.error('Failed to check region name availability:', err);
      setRegionNameError('Failed to check availability');
    }
  };

  const handleRegionNameChange = (name: string) => {
    setRegionName(name);
    // Debounced availability check
    const timeoutId = setTimeout(() => {
      checkRegionNameAvailability(name);
    }, 500);
    return () => clearTimeout(timeoutId);
  };

  const createSubscription = async (subscriptionType: string) => {
    if (!token) {
      setError('Please log in to subscribe');
      return;
    }

    if (subscriptionType === 'regional_owner' && !regionName) {
      setError('Please enter a region name');
      return;
    }

    if (subscriptionType === 'regional_owner' && !regionNameAvailable) {
      setError('Please choose an available region name');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/paypal/subscriptions/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          subscription_type: subscriptionType,
          region_name: subscriptionType === 'regional_owner' ? regionName : undefined,
          return_url: `${window.location.origin}/subscription/success`,
          cancel_url: `${window.location.origin}/subscription/cancelled`
        })
      });

      if (response.ok) {
        const data = await response.json();
        
        // Redirect to PayPal approval URL
        if (data.approval_url) {
          window.location.href = data.approval_url;
        }
        
        onSubscriptionCreated?.(data.subscription_id);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to create subscription');
      }
    } catch (err) {
      setError('Network error. Please try again.');
      console.error('Subscription creation error:', err);
    } finally {
      setLoading(false);
    }
  };

  const cancelSubscription = async (subscriptionId: string) => {
    if (!token) return;

    if (!confirm('Are you sure you want to cancel this subscription? This action cannot be undone.')) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/v1/paypal/subscriptions/${subscriptionId}/cancel`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        await loadUserSubscriptions(); // Refresh the list
        onSubscriptionCancelled?.(subscriptionId);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to cancel subscription');
      }
    } catch (err) {
      setError('Network error. Please try again.');
      console.error('Subscription cancellation error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getSubscriptionStatusBadge = (status: string) => {
    const statusClasses = {
      ACTIVE: 'status-active',
      SUSPENDED: 'status-suspended',
      CANCELLED: 'status-cancelled',
      EXPIRED: 'status-expired'
    };
    
    return (
      <span className={`subscription-status ${statusClasses[status as keyof typeof statusClasses] || 'status-unknown'}`}>
        {status}
      </span>
    );
  };

  if (!user) {
    return (
      <div className="paypal-subscription-container">
        <p>Please log in to view subscription options.</p>
      </div>
    );
  }

  return (
    <div className="paypal-subscription-container">
      <h2>Subscription Management</h2>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* Current Subscriptions */}
      {userSubscriptions.length > 0 && (
        <div className="current-subscriptions">
          <h3>Your Active Subscriptions</h3>
          {userSubscriptions.map((subscription) => (
            <div key={subscription.subscription_id} className="subscription-card">
              <div className="subscription-info">
                <h4>
                  {subscription.type === 'galactic_citizen' ? 'Galactic Citizenship' : 'Regional Ownership'}
                  {subscription.region_name && ` - ${subscription.region_name}`}
                </h4>
                <p className="subscription-amount">{subscription.amount}</p>
                {getSubscriptionStatusBadge(subscription.status)}
              </div>
              <div className="subscription-actions">
                <button
                  onClick={() => cancelSubscription(subscription.subscription_id)}
                  className="cancel-button"
                  disabled={loading || subscription.status !== 'ACTIVE'}
                >
                  Cancel Subscription
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Available Plans */}
      <div className="subscription-plans">
        <h3>Available Subscription Plans</h3>
        {plans.map((plan) => (
          <div key={plan.id} className="plan-card">
            <div className="plan-header">
              <h4>{plan.name}</h4>
              <div className="plan-price">{plan.price}</div>
            </div>
            <p className="plan-description">{plan.description}</p>
            <ul className="plan-features">
              {plan.features.map((feature, index) => (
                <li key={index}>{feature}</li>
              ))}
            </ul>
            
            {plan.id === 'regional_owner' && (
              <div className="region-name-input">
                <label htmlFor="regionName">Choose your region name:</label>
                <input
                  id="regionName"
                  type="text"
                  value={regionName}
                  onChange={(e) => handleRegionNameChange(e.target.value)}
                  placeholder="my-awesome-region"
                  pattern="[a-zA-Z0-9_-]+"
                  title="Only letters, numbers, hyphens, and underscores allowed"
                />
                {regionNameError && (
                  <div className="region-name-error">{regionNameError}</div>
                )}
                {regionNameAvailable === true && (
                  <div className="region-name-success">✓ Region name available</div>
                )}
              </div>
            )}
            
            <button
              onClick={() => createSubscription(plan.id)}
              className="subscribe-button"
              disabled={
                loading || 
                userSubscriptions.some(sub => 
                  (plan.id === 'galactic_citizen' && sub.type === 'galactic_citizen') ||
                  (plan.id === 'regional_owner' && sub.type === 'regional_owner')
                ) ||
                (plan.id === 'regional_owner' && !regionNameAvailable)
              }
            >
              {loading ? 'Processing...' : 'Subscribe Now'}
            </button>
          </div>
        ))}
      </div>

      <div className="subscription-info">
        <h4>Important Information</h4>
        <ul>
          <li>All subscriptions are billed monthly through PayPal</li>
          <li>You can cancel your subscription at any time</li>
          <li>Galactic citizenship provides access to all regions and inter-regional travel</li>
          <li>Regional ownership includes all galactic citizen benefits</li>
          <li>Regions remain active as long as subscription is maintained</li>
        </ul>
      </div>
    </div>
  );
};

export default PayPalSubscription;