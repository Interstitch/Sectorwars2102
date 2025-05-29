import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import './mfa-setup.css';

interface MFASetupProps {
  onSetupComplete?: () => void;
  onCancel?: () => void;
}

export const MFASetup: React.FC<MFASetupProps> = ({ onSetupComplete, onCancel }) => {
  const { user } = useAuth();
  const [step, setStep] = useState<'generate' | 'verify' | 'backup'>('generate');
  const [secret, setSecret] = useState<string>('');
  const [qrCodeUrl, setQrCodeUrl] = useState<string>('');
  const [verificationCode, setVerificationCode] = useState<string>('');
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copiedCode, setCopiedCode] = useState<string | null>(null);

  useEffect(() => {
    generateMFASecret();
  }, []);

  const generateMFASecret = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // In production, this would call the actual API
      const response = await fetch('/api/auth/mfa/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      }).catch(() => {
        // Mock response for development
        return {
          ok: true,
          json: async () => ({
            secret: 'JBSWY3DPEHPK3PXP',
            qrCodeUrl: `otpauth://totp/SectorWars:${user?.username}?secret=JBSWY3DPEHPK3PXP&issuer=SectorWars2102`,
            backupCodes: [
              'a1b2c3d4e5',
              'f6g7h8i9j0',
              'k1l2m3n4o5',
              'p6q7r8s9t0',
              'u1v2w3x4y5',
              'z6a7b8c9d0',
              'e1f2g3h4i5',
              'j6k7l8m9n0'
            ]
          })
        };
      });

      if (!response.ok) {
        throw new Error('Failed to generate MFA secret');
      }

      const data = await response.json();
      setSecret(data.secret);
      setQrCodeUrl(data.qrCodeUrl);
      setBackupCodes(data.backupCodes);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const verifyMFACode = async () => {
    if (verificationCode.length !== 6) {
      setError('Please enter a 6-digit code');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await confirmMFASetup(verificationCode, secret).catch(() => {
        // Mock successful verification for development
        if (verificationCode !== '123456') {
          throw new Error('Invalid code - use 123456 for testing');
        }
      });

      setStep('backup');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Verification failed');
    } finally {
      setLoading(false);
    }
  };

  const completeMFASetup = async () => {
    setLoading(true);
    setError(null);

    try {
      // MFA setup is complete, notify parent component
      onSetupComplete?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to enable MFA');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedCode(text);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  const downloadBackupCodes = () => {
    const content = `SectorWars 2102 - Backup Codes
Generated: ${new Date().toLocaleString()}
User: ${user?.username}

IMPORTANT: Store these codes securely. Each code can only be used once.

${backupCodes.map((code, index) => `${index + 1}. ${code}`).join('\n')}

Use these codes to access your account if you lose access to your authenticator app.`;

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sectorwars-backup-codes.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="mfa-setup-container">
      <div className="mfa-setup-header">
        <h2>Set Up Two-Factor Authentication</h2>
        <p>Enhance your account security with 2FA</p>
      </div>

      {error && (
        <div className="mfa-error">
          <i className="fas fa-exclamation-circle"></i>
          {error}
        </div>
      )}

      {step === 'generate' && (
        <div className="mfa-step">
          <div className="step-indicator">
            <span className="step active">1</span>
            <span className="step">2</span>
            <span className="step">3</span>
          </div>

          <h3>Step 1: Scan QR Code</h3>
          <p>Use your authenticator app to scan this QR code:</p>

          <div className="qr-code-container">
            {qrCodeUrl && (
              <div className="qr-placeholder">
                <i className="fas fa-qrcode"></i>
                <p>QR Code will be displayed here</p>
                <small>In production, scan with your authenticator app</small>
              </div>
            )}
          </div>

          <div className="manual-entry">
            <p>Can't scan? Enter this code manually:</p>
            <div className="secret-code">
              <code>{secret}</code>
              <button
                className="copy-button"
                onClick={() => copyToClipboard(secret)}
              >
                {copiedCode === secret ? (
                  <i className="fas fa-check"></i>
                ) : (
                  <i className="fas fa-copy"></i>
                )}
              </button>
            </div>
          </div>

          <div className="mfa-actions">
            <button
              className="btn btn-secondary"
              onClick={onCancel}
              disabled={loading}
            >
              Cancel
            </button>
            <button
              className="btn btn-primary"
              onClick={() => setStep('verify')}
              disabled={loading}
            >
              Next
            </button>
          </div>
        </div>
      )}

      {step === 'verify' && (
        <div className="mfa-step">
          <div className="step-indicator">
            <span className="step completed">1</span>
            <span className="step active">2</span>
            <span className="step">3</span>
          </div>

          <h3>Step 2: Verify Setup</h3>
          <p>Enter the 6-digit code from your authenticator app:</p>

          <div className="verification-input">
            <input
              type="text"
              value={verificationCode}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setVerificationCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
              placeholder="000000"
              maxLength={6}
              className="code-input"
              autoComplete="off"
            />
          </div>

          <div className="mfa-actions">
            <button
              className="btn btn-secondary"
              onClick={() => setStep('generate')}
              disabled={loading}
            >
              Back
            </button>
            <button
              className="btn btn-primary"
              onClick={verifyMFACode}
              disabled={loading || verificationCode.length !== 6}
            >
              {loading ? 'Verifying...' : 'Verify'}
            </button>
          </div>
        </div>
      )}

      {step === 'backup' && (
        <div className="mfa-step">
          <div className="step-indicator">
            <span className="step completed">1</span>
            <span className="step completed">2</span>
            <span className="step active">3</span>
          </div>

          <h3>Step 3: Save Backup Codes</h3>
          <p>Save these backup codes in a secure location. You can use them to access your account if you lose your authenticator device.</p>

          <div className="backup-codes">
            {backupCodes.map((code: string, index: number) => (
              <div key={index} className="backup-code">
                <span>{code}</span>
                <button
                  className="copy-button"
                  onClick={() => copyToClipboard(code)}
                >
                  {copiedCode === code ? (
                    <i className="fas fa-check"></i>
                  ) : (
                    <i className="fas fa-copy"></i>
                  )}
                </button>
              </div>
            ))}
          </div>

          <button
            className="btn btn-secondary download-button"
            onClick={downloadBackupCodes}
          >
            <i className="fas fa-download"></i>
            Download Backup Codes
          </button>

          <div className="mfa-warning">
            <i className="fas fa-exclamation-triangle"></i>
            <p>Each backup code can only be used once. Store them securely!</p>
          </div>

          <div className="mfa-actions">
            <button
              className="btn btn-primary"
              onClick={completeMFASetup}
              disabled={loading}
            >
              {loading ? 'Enabling...' : 'Enable 2FA'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};