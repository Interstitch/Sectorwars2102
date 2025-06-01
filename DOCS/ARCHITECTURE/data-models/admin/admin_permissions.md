# Admin Permissions and Security Data Definition

## Overview

This document defines the comprehensive permission system for the Admin UI, including role-based access control, audit logging, and security monitoring systems.

## Data Models

### Admin Role System

```typescript
export enum AdminPermission {
  // Player Management
  PLAYER_VIEW = "PLAYER_VIEW",
  PLAYER_EDIT = "PLAYER_EDIT",
  PLAYER_DELETE = "PLAYER_DELETE",
  PLAYER_CREDITS = "PLAYER_CREDITS",
  PLAYER_TURNS = "PLAYER_TURNS",
  PLAYER_TELEPORT = "PLAYER_TELEPORT",
  PLAYER_BAN = "PLAYER_BAN",
  
  // Ship Management
  SHIP_VIEW = "SHIP_VIEW",
  SHIP_EDIT = "SHIP_EDIT",
  SHIP_CREATE = "SHIP_CREATE",
  SHIP_DELETE = "SHIP_DELETE",
  SHIP_TELEPORT = "SHIP_TELEPORT",
  SHIP_REPAIR = "SHIP_REPAIR",
  
  // Universe Management
  UNIVERSE_VIEW = "UNIVERSE_VIEW",
  UNIVERSE_EDIT = "UNIVERSE_EDIT",
  SECTOR_EDIT = "SECTOR_EDIT",
  WARP_MANAGE = "WARP_MANAGE",
  GALAXY_GENERATE = "GALAXY_GENERATE",
  
  // Economy Management
  ECONOMY_VIEW = "ECONOMY_VIEW",
  ECONOMY_INTERVENE = "ECONOMY_INTERVENE",
  MARKET_MANIPULATE = "MARKET_MANIPULATE",
  CREDIT_INJECT = "CREDIT_INJECT",
  
  // Combat Management
  COMBAT_VIEW = "COMBAT_VIEW",
  COMBAT_RESOLVE = "COMBAT_RESOLVE",
  COMBAT_REVERSE = "COMBAT_REVERSE",
  BALANCE_ADJUST = "BALANCE_ADJUST",
  
  // Team Management
  TEAM_VIEW = "TEAM_VIEW",
  TEAM_MANAGE = "TEAM_MANAGE",
  TEAM_DISBAND = "TEAM_DISBAND",
  ALLIANCE_MANAGE = "ALLIANCE_MANAGE",
  
  // Event Management
  EVENT_VIEW = "EVENT_VIEW",
  EVENT_CREATE = "EVENT_CREATE",
  EVENT_MANAGE = "EVENT_MANAGE",
  REWARD_DISTRIBUTE = "REWARD_DISTRIBUTE",
  
  // Analytics & Reporting
  ANALYTICS_VIEW = "ANALYTICS_VIEW",
  ANALYTICS_EXPORT = "ANALYTICS_EXPORT",
  REPORT_GENERATE = "REPORT_GENERATE",
  
  // System Administration
  ADMIN_MANAGE = "ADMIN_MANAGE",
  SECURITY_AUDIT = "SECURITY_AUDIT",
  SYSTEM_MONITOR = "SYSTEM_MONITOR",
  BACKUP_MANAGE = "BACKUP_MANAGE"
}

export interface AdminRole {
  id: string;
  name: string;
  description: string;
  permissions: AdminPermission[];
  restrictions: AdminRestriction[];
  created_at: Date;
  updated_at: Date;
  created_by: string;
}

export interface AdminRestriction {
  type: 'TIME_LIMIT' | 'IP_WHITELIST' | 'ACTION_LIMIT' | 'RESOURCE_LIMIT';
  parameters: {
    timeLimit?: {
      startHour: number;
      endHour: number;
      timezone: string;
    };
    ipWhitelist?: string[];
    actionLimit?: {
      action: AdminPermission;
      maxPerDay: number;
    };
    resourceLimit?: {
      resource: string;
      maxValue: number;
    };
  };
}

export interface AdminUser {
  id: string;
  username: string;
  email: string;
  roles: string[];
  is_active: boolean;
  last_login: Date;
  created_at: Date;
  mfa_enabled: boolean;
  ip_whitelist: string[];
}
```

## Audit Logging System

```typescript
export enum AdminActionType {
  // Player Actions
  PLAYER_CREDITS_ADJUSTED = "PLAYER_CREDITS_ADJUSTED",
  PLAYER_TURNS_ADJUSTED = "PLAYER_TURNS_ADJUSTED",
  PLAYER_TELEPORTED = "PLAYER_TELEPORTED",
  PLAYER_BANNED = "PLAYER_BANNED",
  PLAYER_REPUTATION_MODIFIED = "PLAYER_REPUTATION_MODIFIED",
  
  // Ship Actions
  SHIP_CREATED = "SHIP_CREATED",
  SHIP_DELETED = "SHIP_DELETED",
  SHIP_TELEPORTED = "SHIP_TELEPORTED",
  SHIP_REPAIRED = "SHIP_REPAIRED",
  SHIP_OWNERSHIP_CHANGED = "SHIP_OWNERSHIP_CHANGED",
  
  // Universe Actions
  SECTOR_MODIFIED = "SECTOR_MODIFIED",
  WARP_CONNECTION_ADDED = "WARP_CONNECTION_ADDED",
  WARP_CONNECTION_REMOVED = "WARP_CONNECTION_REMOVED",
  GALAXY_REGENERATED = "GALAXY_REGENERATED",
  
  // Economy Actions
  MARKET_INTERVENTION = "MARKET_INTERVENTION",
  PRICE_ADJUSTMENT = "PRICE_ADJUSTMENT",
  CREDIT_INJECTION = "CREDIT_INJECTION",
  
  // Combat Actions
  COMBAT_RESOLVED = "COMBAT_RESOLVED",
  COMBAT_REVERSED = "COMBAT_REVERSED",
  BALANCE_ADJUSTED = "BALANCE_ADJUSTED",
  
  // System Actions
  ADMIN_ROLE_ASSIGNED = "ADMIN_ROLE_ASSIGNED",
  SECURITY_ALERT_TRIGGERED = "SECURITY_ALERT_TRIGGERED",
  BACKUP_INITIATED = "BACKUP_INITIATED"
}

export interface AdminAction {
  id: string;
  admin_id: string;
  admin_username: string;
  action_type: AdminActionType;
  target_type: 'PLAYER' | 'SHIP' | 'SECTOR' | 'PORT' | 'PLANET' | 'TEAM' | 'SYSTEM';
  target_id: string;
  details: {
    before?: any;
    after?: any;
    reason?: string;
    parameters?: Record<string, any>;
  };
  ip_address: string;
  user_agent: string;
  timestamp: Date;
  success: boolean;
  error_message?: string;
}
```

## Security Monitoring

```typescript
export enum SecurityAlertType {
  SUSPICIOUS_LOGIN = "SUSPICIOUS_LOGIN",
  MULTIPLE_FAILED_LOGINS = "MULTIPLE_FAILED_LOGINS",
  UNUSUAL_ACTIVITY_PATTERN = "UNUSUAL_ACTIVITY_PATTERN",
  PRIVILEGE_ESCALATION_ATTEMPT = "PRIVILEGE_ESCALATION_ATTEMPT",
  BULK_OPERATION_DETECTED = "BULK_OPERATION_DETECTED",
  AFTER_HOURS_ACCESS = "AFTER_HOURS_ACCESS",
  UNAUTHORIZED_IP = "UNAUTHORIZED_IP",
  PERMISSION_VIOLATION = "PERMISSION_VIOLATION"
}

export interface SecurityAlert {
  id: string;
  alert_type: SecurityAlertType;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  admin_id: string;
  message: string;
  details: {
    ip_address?: string;
    attempted_action?: string;
    risk_score?: number;
    contextual_data?: Record<string, any>;
  };
  resolved: boolean;
  resolved_by?: string;
  resolved_at?: Date;
  resolution_notes?: string;
  created_at: Date;
}

export interface AccessControl {
  id: string;
  admin_id: string;
  rule_type: 'IP_RESTRICTION' | 'TIME_RESTRICTION' | 'ACTION_LIMIT' | 'MFA_REQUIRED';
  rule_config: {
    allowedIPs?: string[];
    allowedHours?: {
      start: number;
      end: number;
      timezone: string;
    };
    actionLimits?: {
      [key in AdminPermission]?: number;
    };
    mfaRequired?: AdminPermission[];
  };
  active: boolean;
  created_at: Date;
  expires_at?: Date;
}
```

## Predefined Admin Roles

### Super Administrator
```typescript
const SUPER_ADMIN_ROLE: AdminRole = {
  id: "super-admin",
  name: "Super Administrator",
  description: "Full system access with no restrictions",
  permissions: Object.values(AdminPermission),
  restrictions: [],
  created_at: new Date(),
  updated_at: new Date(),
  created_by: "system"
};
```

### Game Master
```typescript
const GAME_MASTER_ROLE: AdminRole = {
  id: "game-master",
  name: "Game Master",
  description: "Full game management access, limited system admin",
  permissions: [
    AdminPermission.PLAYER_VIEW,
    AdminPermission.PLAYER_EDIT,
    AdminPermission.PLAYER_CREDITS,
    AdminPermission.PLAYER_TURNS,
    AdminPermission.PLAYER_TELEPORT,
    AdminPermission.SHIP_VIEW,
    AdminPermission.SHIP_EDIT,
    AdminPermission.SHIP_CREATE,
    AdminPermission.SHIP_TELEPORT,
    AdminPermission.SHIP_REPAIR,
    AdminPermission.UNIVERSE_VIEW,
    AdminPermission.UNIVERSE_EDIT,
    AdminPermission.SECTOR_EDIT,
    AdminPermission.ECONOMY_VIEW,
    AdminPermission.ECONOMY_INTERVENE,
    AdminPermission.COMBAT_VIEW,
    AdminPermission.COMBAT_RESOLVE,
    AdminPermission.TEAM_VIEW,
    AdminPermission.TEAM_MANAGE,
    AdminPermission.EVENT_VIEW,
    AdminPermission.EVENT_CREATE,
    AdminPermission.EVENT_MANAGE,
    AdminPermission.ANALYTICS_VIEW,
    AdminPermission.ANALYTICS_EXPORT
  ],
  restrictions: [],
  created_at: new Date(),
  updated_at: new Date(),
  created_by: "system"
};
```

### Economy Manager
```typescript
const ECONOMY_MANAGER_ROLE: AdminRole = {
  id: "economy-manager",
  name: "Economy Manager",
  description: "Specialized in economic and market management",
  permissions: [
    AdminPermission.PLAYER_VIEW,
    AdminPermission.ECONOMY_VIEW,
    AdminPermission.ECONOMY_INTERVENE,
    AdminPermission.MARKET_MANIPULATE,
    AdminPermission.ANALYTICS_VIEW,
    AdminPermission.ANALYTICS_EXPORT,
    AdminPermission.REPORT_GENERATE
  ],
  restrictions: [
    {
      type: 'ACTION_LIMIT',
      parameters: {
        actionLimit: {
          action: AdminPermission.CREDIT_INJECT,
          maxPerDay: 5
        }
      }
    }
  ],
  created_at: new Date(),
  updated_at: new Date(),
  created_by: "system"
};
```

### Player Support
```typescript
const PLAYER_SUPPORT_ROLE: AdminRole = {
  id: "player-support",
  name: "Player Support",
  description: "Limited player assistance capabilities",
  permissions: [
    AdminPermission.PLAYER_VIEW,
    AdminPermission.PLAYER_CREDITS,
    AdminPermission.PLAYER_TURNS,
    AdminPermission.SHIP_VIEW,
    AdminPermission.SHIP_REPAIR,
    AdminPermission.UNIVERSE_VIEW,
    AdminPermission.ANALYTICS_VIEW
  ],
  restrictions: [
    {
      type: 'ACTION_LIMIT',
      parameters: {
        actionLimit: {
          action: AdminPermission.PLAYER_CREDITS,
          maxPerDay: 10
        }
      }
    },
    {
      type: 'TIME_LIMIT',
      parameters: {
        timeLimit: {
          startHour: 8,
          endHour: 18,
          timezone: 'UTC'
        }
      }
    }
  ],
  created_at: new Date(),
  updated_at: new Date(),
  created_by: "system"
};
```

### Read-Only Analyst
```typescript
const ANALYST_ROLE: AdminRole = {
  id: "analyst",
  name: "Read-Only Analyst",
  description: "Analytics and reporting access only",
  permissions: [
    AdminPermission.PLAYER_VIEW,
    AdminPermission.SHIP_VIEW,
    AdminPermission.UNIVERSE_VIEW,
    AdminPermission.ECONOMY_VIEW,
    AdminPermission.COMBAT_VIEW,
    AdminPermission.TEAM_VIEW,
    AdminPermission.EVENT_VIEW,
    AdminPermission.ANALYTICS_VIEW,
    AdminPermission.ANALYTICS_EXPORT,
    AdminPermission.REPORT_GENERATE
  ],
  restrictions: [],
  created_at: new Date(),
  updated_at: new Date(),
  created_by: "system"
};
```

## API Endpoints

### Admin Role Management
```typescript
GET /api/admin/roles                    // List all admin roles
POST /api/admin/roles                   // Create new admin role
PUT /api/admin/roles/{id}               // Update admin role
DELETE /api/admin/roles/{id}            // Delete admin role
GET /api/admin/users                    // List admin users
POST /api/admin/users/{id}/roles        // Assign role to user
DELETE /api/admin/users/{id}/roles/{roleId} // Remove role from user
```

### Audit and Security
```typescript
GET /api/admin/audit-log                // Retrieve audit log with filtering
POST /api/admin/audit-log/export        // Export audit log
GET /api/admin/security-alerts          // Get security alerts
PUT /api/admin/security-alerts/{id}/resolve // Resolve security alert
GET /api/admin/access-controls          // List access control rules
POST /api/admin/access-controls         // Create access control rule
```

### Permission Checking
```typescript
GET /api/admin/permissions/check        // Check if user has specific permission
GET /api/admin/permissions/user/{id}    // Get all permissions for user
POST /api/admin/permissions/validate    // Validate action against permissions
```

## Security Best Practices

### Implementation Requirements
1. **Multi-Factor Authentication**: Required for high-privilege roles
2. **IP Whitelisting**: Configurable per admin user
3. **Session Management**: Automatic timeout and refresh
4. **Audit Logging**: All actions logged with full context
5. **Permission Validation**: Every API call validates permissions
6. **Rate Limiting**: Prevent abuse of admin actions
7. **Encryption**: All sensitive data encrypted at rest
8. **Monitoring**: Real-time security alert system

### Database Security
```sql
-- Database indexes for performance
CREATE INDEX idx_admin_actions_admin_id ON admin_actions(admin_id);
CREATE INDEX idx_admin_actions_timestamp ON admin_actions(timestamp);
CREATE INDEX idx_admin_actions_action_type ON admin_actions(action_type);
CREATE INDEX idx_security_alerts_severity ON security_alerts(severity);
CREATE INDEX idx_security_alerts_created_at ON security_alerts(created_at);

-- Row-level security
ALTER TABLE admin_actions ENABLE ROW LEVEL SECURITY;
CREATE POLICY admin_actions_policy ON admin_actions
  FOR ALL TO authenticated_admin
  USING (admin_id = current_user_id());
```

This comprehensive permission system ensures secure, auditable, and granular access control for the Admin UI while maintaining flexibility for different administrative roles and responsibilities.