# Security Operations Guide

**Document Version**: 1.0  
**Last Updated**: 2025-05-24  
**Target Audience**: System Administrators, DevOps Engineers  

## Overview

This guide provides operational procedures for managing the AI Security System in Sectorwars2102. It covers monitoring, incident response, maintenance, and troubleshooting procedures.

## Daily Operations

### Morning Security Check (5 minutes)

1. **Review Security Dashboard**
   ```bash
   curl -H "Authorization: Bearer $ADMIN_TOKEN" \
        "$GAMESERVER_URL/admin/security/report"
   ```

2. **Check Active Alerts**
   ```bash
   curl -H "Authorization: Bearer $ADMIN_TOKEN" \
        "$GAMESERVER_URL/admin/security/alerts"
   ```

3. **Monitor Key Metrics**
   - Players blocked: Should be <5% of active players
   - Daily API costs: Monitor trends and spikes
   - Violation patterns: Look for coordinated attacks

### Weekly Maintenance (15 minutes)

1. **Clean Old Security Data**
   ```bash
   curl -X POST -H "Authorization: Bearer $ADMIN_TOKEN" \
        "$GAMESERVER_URL/admin/security/cleanup?days_to_keep=7"
   ```

2. **Review High-Risk Players**
   - Check players with trust scores <0.3
   - Investigate repeat offenders
   - Consider trust score resets for reformed players

3. **Analyze Security Trends**
   - Review violation types and frequency
   - Check for new attack patterns
   - Update security rules if needed

## Security Incident Response

### Automated Response (Immediate)

The security system automatically handles most threats:

- **XSS/SQL Injection**: Immediate 24-hour block
- **Prompt Injection**: Dangerous threat level, trust score reduction
- **Cost Abuse**: Rate limiting and cost controls
- **Jailbreak Attempts**: Progressive blocking based on severity

### Manual Investigation Required

#### High Cost Usage Alert
```bash
# Get detailed cost breakdown for player
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
     "$GAMESERVER_URL/admin/security/player/{player_id}/status"

# If legitimate usage, temporarily increase limit
curl -X POST -H "Authorization: Bearer $ADMIN_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"action": "reset_violations", "reason": "Legitimate high usage verified"}' \
     "$GAMESERVER_URL/admin/security/player/{player_id}/action"
```

#### Coordinated Attack Pattern
```bash
# Block multiple players if coordinated attack detected
for player_id in $SUSPICIOUS_PLAYERS; do
  curl -X POST -H "Authorization: Bearer $ADMIN_TOKEN" \
       -H "Content-Type: application/json" \
       -d '{"action": "block", "duration_hours": 72, "reason": "Coordinated attack investigation"}' \
       "$GAMESERVER_URL/admin/security/player/$player_id/action"
done
```

#### False Positive Investigation
```bash
# Review player's full security history
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
     "$GAMESERVER_URL/admin/security/player/{player_id}/risk"

# If false positive confirmed, reset penalties
curl -X POST -H "Authorization: Bearer $ADMIN_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"action": "reset_trust", "reason": "False positive confirmed"}' \
     "$GAMESERVER_URL/admin/security/player/{player_id}/action"
```

## Security Alert Procedures

### Alert Priority Levels

#### HIGH Priority (Immediate Response Required)
- **Multiple players approaching cost limits**
- **Coordinated attack patterns**
- **System security service failures**

**Response Time**: 5 minutes  
**Actions**: Investigate, block if necessary, escalate if needed

#### MEDIUM Priority (Response within 1 hour)
- **Individual high violation rates**
- **Unusual cost usage patterns**
- **Multiple players currently blocked**

**Response Time**: 1 hour  
**Actions**: Review and investigate, take action if warranted

#### LOW Priority (Response within 24 hours)
- **Single player violations**
- **Normal security events**
- **Routine blocking/unblocking**

**Response Time**: 24 hours  
**Actions**: Log and monitor, no immediate action required

### Alert Response Checklist

```markdown
□ Acknowledge alert receipt
□ Assess threat level and impact
□ Review affected player(s) history
□ Determine if automated response is appropriate
□ Take manual action if required
□ Document incident and resolution
□ Monitor for recurrence
```

## Monitoring & Metrics

### Key Performance Indicators

#### Security Health Metrics
- **Attack Detection Rate**: Should be >99%
- **False Positive Rate**: Should be <1%
- **Response Time**: Automated <1ms, Manual <5min
- **System Uptime**: Should be >99.9%

#### Player Protection Metrics
- **Blocked Players**: <5% of active player base
- **Trust Score Distribution**: Most players >0.7
- **Cost Control**: <1% of players near daily limits
- **Legitimate Access**: >95% success rate for normal usage

#### Financial Protection Metrics
- **Daily API Costs**: Track trends and budget compliance
- **Cost Per Player**: Monitor for abuse patterns
- **Budget Utilization**: Should be predictable and controlled

### Monitoring Tools

#### Security Dashboard URLs
```bash
# Main security dashboard
https://admin-ui.sectorwars2102.com/security

# Real-time alerts
https://admin-ui.sectorwars2102.com/security/alerts

# Player risk assessment
https://admin-ui.sectorwars2102.com/security/players
```

#### API Endpoints for Monitoring Scripts
```bash
# Health check
GET /admin/security/report

# Alert status  
GET /admin/security/alerts

# Player statistics
GET /admin/players?security_stats=true
```

## Troubleshooting Guide

### Common Issues

#### Issue: High False Positive Rate
**Symptoms**: Legitimate players being blocked
**Diagnosis**: Review violation patterns and player feedback
**Solution**: 
```bash
# Review recent violations
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
     "$GAMESERVER_URL/admin/security/report" | jq '.violations.by_type'

# Adjust detection patterns if needed (requires code deployment)
# Reset affected players
curl -X POST -H "Authorization: Bearer $ADMIN_TOKEN" \
     -d '{"action": "reset_violations"}' \
     "$GAMESERVER_URL/admin/security/player/{player_id}/action"
```

#### Issue: Cost Limits Too Restrictive
**Symptoms**: Many legitimate players hitting daily limits
**Diagnosis**: Review cost usage patterns
**Solution**:
```bash
# Analyze cost usage distribution
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
     "$GAMESERVER_URL/admin/security/report" | jq '.costs'

# If limits too low, update configuration and restart service
# Temporarily increase limits for affected players
```

#### Issue: Security Service Performance Degradation
**Symptoms**: Slow response times, request timeouts
**Diagnosis**: Check system resources and violation volume
**Solution**:
```bash
# Check security service memory usage
docker stats gameserver

# Clean old security data
curl -X POST -H "Authorization: Bearer $ADMIN_TOKEN" \
     "$GAMESERVER_URL/admin/security/cleanup?days_to_keep=3"

# Restart security service if needed
docker-compose restart gameserver
```

#### Issue: Coordinated Attack Overwhelming System
**Symptoms**: High violation volume, system slowdown
**Diagnosis**: Review attack patterns and sources
**Solution**:
```bash
# Identify attack sources
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
     "$GAMESERVER_URL/admin/security/alerts"

# Implement emergency blocking
# Consider IP-level blocking if available
# Scale up security service if needed
```

### Emergency Procedures

#### Security Service Failure
1. **Immediate**: Switch to fallback mode (disable AI features temporarily)
2. **Diagnosis**: Check logs and system health
3. **Recovery**: Restart service, verify functionality
4. **Monitoring**: Increased monitoring for 24 hours

#### Mass Account Compromise
1. **Immediate**: Block all affected accounts
2. **Investigation**: Analyze attack vector and scope
3. **Containment**: Implement additional security measures
4. **Recovery**: Reset affected accounts after security verification

## Configuration Management

### Security Configuration Files
```bash
# Main security service configuration
services/gameserver/src/services/ai_security_service.py

# Rate limiting settings
services/gameserver/src/core/config.py

# Admin security routes
services/gameserver/src/api/routes/admin_comprehensive.py
```

### Environment-Specific Settings

#### Production Environment
```bash
AI_SECURITY_RATE_LIMIT_PER_MINUTE=10
AI_SECURITY_RATE_LIMIT_PER_HOUR=60
AI_SECURITY_RATE_LIMIT_PER_DAY=500
AI_SECURITY_MAX_COST_PER_DAY=2.00
AI_SECURITY_STRICT_MODE=true
```

#### Development Environment
```bash
AI_SECURITY_RATE_LIMIT_PER_MINUTE=100
AI_SECURITY_RATE_LIMIT_PER_HOUR=600
AI_SECURITY_RATE_LIMIT_PER_DAY=5000
AI_SECURITY_MAX_COST_PER_DAY=20.00
AI_SECURITY_STRICT_MODE=false
```

#### Testing Environment
```bash
AI_SECURITY_RATE_LIMIT_PER_MINUTE=1000
AI_SECURITY_RATE_LIMIT_PER_HOUR=10000
AI_SECURITY_RATE_LIMIT_PER_DAY=50000
AI_SECURITY_MAX_COST_PER_DAY=100.00
AI_SECURITY_STRICT_MODE=false
```

## Log Analysis

### Security Log Locations
```bash
# Security violations log
docker logs gameserver | grep "Security violation detected"

# Cost tracking log
docker logs gameserver | grep "cost tracking"

# Rate limiting log  
docker logs gameserver | grep "rate limit"

# Admin actions log
docker logs gameserver | grep "Admin.*security action"
```

### Log Analysis Scripts
```bash
# Find top violators
docker logs gameserver | grep "Security violation" | \
  awk '{print $8}' | sort | uniq -c | sort -nr | head -10

# Cost usage analysis
docker logs gameserver | grep "cost tracking" | \
  awk '{print $8, $10}' | sort | uniq -c

# Attack pattern analysis
docker logs gameserver | grep "Security violation" | \
  awk '{print $6}' | sort | uniq -c | sort -nr
```

## Backup & Recovery

### Security Data Backup
```bash
# Export current security profiles (manual process)
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
     "$GAMESERVER_URL/admin/security/report" > security_backup_$(date +%Y%m%d).json
```

### Security Configuration Backup
```bash
# Backup security service configuration
cp services/gameserver/src/services/ai_security_service.py \
   backups/ai_security_service_$(date +%Y%m%d).py
```

### Recovery Procedures
1. **Restore configuration files from backup**
2. **Restart security service**
3. **Verify security functionality with test attacks**
4. **Monitor for proper operation**

## Contact Information

### Security Team Contacts
- **Primary**: security@sectorwars2102.com
- **Secondary**: admin@sectorwars2102.com
- **Emergency**: +1-XXX-XXX-XXXX

### Escalation Procedures
1. **Level 1**: Development team member
2. **Level 2**: Security team lead
3. **Level 3**: System administrator
4. **Level 4**: External security consultant

---

**Remember**: When in doubt, err on the side of caution. It's better to temporarily block a legitimate user than to allow a security breach.

**Documentation Updates**: This guide should be updated whenever security procedures change or new threats are identified.