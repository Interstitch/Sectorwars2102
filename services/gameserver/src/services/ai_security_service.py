"""
AI Security Service for First Login Experience

This service implements comprehensive security measures to protect against:
- OWASP Top 10 vulnerabilities (XSS, Injection, etc.)
- AI-specific attacks (prompt injection, jailbreaking, etc.)
- Cost-based attacks (API abuse, resource exhaustion)
- Multiplayer game exploitation (griefing, defacement)
"""

import re
import html
import logging
import hashlib
import time
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SecurityThreatLevel(Enum):
    """Security threat classification levels"""
    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    DANGEROUS = "dangerous"
    BLOCKED = "blocked"

class SecurityViolationType(Enum):
    """Types of security violations"""
    XSS_ATTEMPT = "xss_attempt"
    SQL_INJECTION = "sql_injection"
    PROMPT_INJECTION = "prompt_injection"
    JAILBREAK_ATTEMPT = "jailbreak_attempt"
    EXCESSIVE_LENGTH = "excessive_length"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    INAPPROPRIATE_CONTENT = "inappropriate_content"
    SYSTEM_COMMAND = "system_command"
    CODE_INJECTION = "code_injection"
    COST_ABUSE = "cost_abuse"

@dataclass
class SecurityViolation:
    """Represents a detected security violation"""
    violation_type: SecurityViolationType
    threat_level: SecurityThreatLevel
    description: str
    detected_patterns: List[str]
    player_id: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

@dataclass
class PlayerSecurityProfile:
    """Tracks security metrics per player"""
    player_id: str
    violation_count: int = 0
    last_violation: Optional[datetime] = None
    request_count_1min: int = 0
    request_count_1hour: int = 0
    request_count_1day: int = 0
    last_request_time: Optional[datetime] = None
    is_blocked: bool = False
    block_expires: Optional[datetime] = None
    trust_score: float = 1.0  # 0.0 (untrusted) to 1.0 (trusted)

class AISecurityService:
    """Comprehensive security service for AI dialogue interactions"""
    
    def __init__(self):
        # Rate limiting configuration
        self.rate_limits = {
            "requests_per_minute": 10,
            "requests_per_hour": 100,
            "requests_per_day": 500,
            "max_chars_per_request": 500,
            "max_words_per_request": 100,
            "max_cost_per_day_usd": 1.0  # $1 per player per day max
        }
        
        # Player security profiles
        self.player_profiles: Dict[str, PlayerSecurityProfile] = {}
        
        # Blocked content patterns
        self.setup_security_patterns()
        
        # Cost tracking
        self.cost_tracking: Dict[str, float] = {}  # player_id -> daily_cost_usd
        
    def setup_security_patterns(self):
        """Initialize security detection patterns"""
        
        # XSS patterns
        self.xss_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>',
            r'<link[^>]*>',
            r'<meta[^>]*>',
            r'vbscript:',
            r'data:text/html',
            r'<img[^>]*onerror',
            r'<svg[^>]*onload'
        ]
        
        # SQL injection patterns
        self.sql_injection_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
            r"(\b(OR|AND)\s+['\"].*['\"])",
            r"[';]--",
            r"/\*.*\*/",
            r"0x[0-9a-fA-F]+",
            r"\bCHAR\(",
            r"\bCONCAT\(",
            r"@@\w+",
            r"\bWAITFOR\b"
        ]
        
        # AI prompt injection patterns
        self.prompt_injection_patterns = [
            r"ignore\s+(previous|all|above|system)\s+(instructions|prompts?|commands?)",
            r"system\s*:\s*",
            r"assistant\s*:\s*",
            r"user\s*:\s*",
            r"###\s*(system|assistant|user)",
            r"pretend\s+(you\s+are|to\s+be)",
            r"roleplay\s+as",
            r"act\s+as\s+a",
            r"forget\s+(everything|all|that)",
            r"new\s+(task|instruction|role)",
            r"disregard\s+(previous|above|all)",
            r"override\s+(system|safety|security)",
            r"jailbreak",
            r"dan\s+mode",
            r"developer\s+mode",
            r"admin\s+mode",
            r"god\s+mode",
            r"unrestricted\s+mode"
        ]
        
        # System command patterns
        self.system_command_patterns = [
            r"[\\/]bin[\\/]",
            r"[\\/]etc[\\/]",
            r"[\\/]proc[\\/]",
            r"[\\/]sys[\\/]",
            r"\bcmd\b",
            r"\bpowershell\b",
            r"\bbash\b",
            r"\bsh\b",
            r"\beval\b",
            r"\bexec\b",
            r"\bsystem\b",
            r"\bpasswd\b",
            r"\bsudo\b",
            r"\brm\s+-rf",
            r"\bmkdir\b",
            r"\bchmod\b",
            r"\bchown\b"
        ]
        
        # Code injection patterns
        self.code_injection_patterns = [
            r"<\?php",
            r"<%.*%>",
            r"function\s*\(",
            r"var\s+\w+\s*=",
            r"let\s+\w+\s*=",
            r"const\s+\w+\s*=",
            r"import\s+",
            r"require\s*\(",
            r"__import__",
            r"eval\s*\(",
            r"exec\s*\(",
            r"compile\s*\(",
            r"\.constructor",
            r"prototype\."
        ]
        
        # Inappropriate content keywords (basic set)
        self.inappropriate_keywords = [
            "hack", "exploit", "vulnerability", "malware", "virus",
            "attack", "breach", "penetration", "injection", "backdoor"
        ]
        
        # Cost abuse patterns
        self.cost_abuse_patterns = [
            r"(.)\1{50,}",  # Repeated characters (50+ times)
            r"\w{100,}",    # Very long words
            r"(.{10,})\1{5,}",  # Repeated phrases
        ]

    def validate_input(self, text: str, player_id: str, session_id: str) -> Tuple[bool, List[SecurityViolation]]:
        """
        Comprehensive input validation and security scanning
        
        Returns:
            Tuple[bool, List[SecurityViolation]]: (is_safe, violations_found)
        """
        violations = []
        
        # Update player profile
        profile = self.get_or_create_player_profile(player_id)
        
        # Check if player is blocked
        if self.is_player_blocked(player_id):
            violations.append(SecurityViolation(
                SecurityViolationType.RATE_LIMIT_EXCEEDED,
                SecurityThreatLevel.BLOCKED,
                "Player is currently blocked due to previous violations",
                [],
                player_id,
                session_id
            ))
            return False, violations
        
        # Rate limiting checks
        if not self.check_rate_limits(player_id):
            violations.append(SecurityViolation(
                SecurityViolationType.RATE_LIMIT_EXCEEDED,
                SecurityThreatLevel.DANGEROUS,
                "Rate limit exceeded",
                [],
                player_id,
                session_id
            ))
            self.apply_security_penalty(player_id, SecurityViolationType.RATE_LIMIT_EXCEEDED)
            return False, violations
        
        # Input length validation
        length_violations = self.validate_input_length(text, player_id, session_id)
        violations.extend(length_violations)
        
        # Sanitization (creates cleaned version but doesn't modify original for analysis)
        sanitized_text = self.sanitize_input(text)
        
        # XSS detection
        xss_violations = self.detect_xss(text, player_id, session_id)
        violations.extend(xss_violations)
        
        # SQL injection detection
        sql_violations = self.detect_sql_injection(text, player_id, session_id)
        violations.extend(sql_violations)
        
        # AI-specific attack detection
        ai_violations = self.detect_ai_specific_attacks(text, player_id, session_id)
        violations.extend(ai_violations)
        
        # System command detection
        system_violations = self.detect_system_commands(text, player_id, session_id)
        violations.extend(system_violations)
        
        # Code injection detection
        code_violations = self.detect_code_injection(text, player_id, session_id)
        violations.extend(code_violations)
        
        # Content appropriateness check
        content_violations = self.check_content_appropriateness(text, player_id, session_id)
        violations.extend(content_violations)
        
        # Cost abuse detection
        cost_violations = self.detect_cost_abuse(text, player_id, session_id)
        violations.extend(cost_violations)
        
        # Determine overall safety
        is_safe = not any(v.threat_level in [SecurityThreatLevel.DANGEROUS, SecurityThreatLevel.BLOCKED] 
                         for v in violations)
        
        # Log violations
        if violations:
            self.log_security_violations(violations)
            
            # Apply penalties for dangerous violations
            dangerous_violations = [v for v in violations 
                                  if v.threat_level == SecurityThreatLevel.DANGEROUS]
            for violation in dangerous_violations:
                self.apply_security_penalty(player_id, violation.violation_type)
        
        # Update request tracking
        self.update_request_tracking(player_id)
        
        return is_safe, violations

    def sanitize_input(self, text: str) -> str:
        """Sanitize input text for safe processing"""
        if not text:
            return ""
        
        # HTML escape
        sanitized = html.escape(text, quote=True)
        
        # Remove null bytes and control characters
        sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', sanitized)
        
        # Normalize whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        
        # Limit length to prevent buffer overflow attempts
        if len(sanitized) > self.rate_limits["max_chars_per_request"]:
            sanitized = sanitized[:self.rate_limits["max_chars_per_request"]]
        
        return sanitized

    def validate_input_length(self, text: str, player_id: str, session_id: str) -> List[SecurityViolation]:
        """Validate input length constraints"""
        violations = []
        
        if len(text) > self.rate_limits["max_chars_per_request"]:
            violations.append(SecurityViolation(
                SecurityViolationType.EXCESSIVE_LENGTH,
                SecurityThreatLevel.DANGEROUS,
                f"Input exceeds maximum length ({len(text)} > {self.rate_limits['max_chars_per_request']})",
                [f"Length: {len(text)}"],
                player_id,
                session_id
            ))
        
        word_count = len(text.split())
        if word_count > self.rate_limits["max_words_per_request"]:
            violations.append(SecurityViolation(
                SecurityViolationType.EXCESSIVE_LENGTH,
                SecurityThreatLevel.SUSPICIOUS,
                f"Input exceeds maximum word count ({word_count} > {self.rate_limits['max_words_per_request']})",
                [f"Word count: {word_count}"],
                player_id,
                session_id
            ))
        
        return violations

    def detect_xss(self, text: str, player_id: str, session_id: str) -> List[SecurityViolation]:
        """Detect XSS attack attempts"""
        violations = []
        text_lower = text.lower()
        
        for pattern in self.xss_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE | re.DOTALL)
            if matches:
                violations.append(SecurityViolation(
                    SecurityViolationType.XSS_ATTEMPT,
                    SecurityThreatLevel.DANGEROUS,
                    "Potential XSS attack detected",
                    [f"Pattern: {pattern}", f"Matches: {matches[:3]}"],  # Limit matches shown
                    player_id,
                    session_id
                ))
        
        return violations

    def detect_sql_injection(self, text: str, player_id: str, session_id: str) -> List[SecurityViolation]:
        """Detect SQL injection attempts"""
        violations = []
        
        for pattern in self.sql_injection_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                violations.append(SecurityViolation(
                    SecurityViolationType.SQL_INJECTION,
                    SecurityThreatLevel.DANGEROUS,
                    "Potential SQL injection detected",
                    [f"Pattern: {pattern}", f"Matches: {matches[:3]}"],
                    player_id,
                    session_id
                ))
        
        return violations

    def detect_ai_attacks(self, text: str, player_id: str, session_id: str) -> List[SecurityViolation]:
        """Detect AI-specific attacks (prompt injection, jailbreaking)"""
        violations = []
        text_lower = text.lower()
        
        for pattern in self.prompt_injection_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                violations.append(SecurityViolation(
                    SecurityViolationType.PROMPT_INJECTION,
                    SecurityThreatLevel.DANGEROUS,
                    "Potential prompt injection attack detected",
                    [f"Pattern: {pattern}"],
                    player_id,
                    session_id
                ))
        
        # Check for jailbreak attempts (multiple indicators)
        jailbreak_indicators = ["ignore", "system", "assistant", "pretend", "roleplay", "forget"]
        indicator_count = sum(1 for indicator in jailbreak_indicators if indicator in text_lower)
        
        if indicator_count >= 3:
            violations.append(SecurityViolation(
                SecurityViolationType.JAILBREAK_ATTEMPT,
                SecurityThreatLevel.DANGEROUS,
                "Potential AI jailbreak attempt detected",
                [f"Indicators: {indicator_count}"],
                player_id,
                session_id
            ))
        
        return violations

    def detect_system_commands(self, text: str, player_id: str, session_id: str) -> List[SecurityViolation]:
        """Detect system command injection attempts"""
        violations = []
        
        for pattern in self.system_command_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                violations.append(SecurityViolation(
                    SecurityViolationType.SYSTEM_COMMAND,
                    SecurityThreatLevel.DANGEROUS,
                    "Potential system command injection detected",
                    [f"Pattern: {pattern}"],
                    player_id,
                    session_id
                ))
        
        return violations

    def detect_code_injection(self, text: str, player_id: str, session_id: str) -> List[SecurityViolation]:
        """Detect code injection attempts"""
        violations = []
        
        for pattern in self.code_injection_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                violations.append(SecurityViolation(
                    SecurityViolationType.CODE_INJECTION,
                    SecurityThreatLevel.DANGEROUS,
                    "Potential code injection detected",
                    [f"Pattern: {pattern}"],
                    player_id,
                    session_id
                ))
        
        return violations

    def check_content_appropriateness(self, text: str, player_id: str, session_id: str) -> List[SecurityViolation]:
        """Check for inappropriate content"""
        violations = []
        text_lower = text.lower()
        
        found_keywords = [keyword for keyword in self.inappropriate_keywords 
                         if keyword in text_lower]
        
        if found_keywords:
            violations.append(SecurityViolation(
                SecurityViolationType.INAPPROPRIATE_CONTENT,
                SecurityThreatLevel.SUSPICIOUS,
                "Potentially inappropriate content detected",
                found_keywords,
                player_id,
                session_id
            ))
        
        return violations

    def detect_cost_abuse(self, text: str, player_id: str, session_id: str) -> List[SecurityViolation]:
        """Detect attempts to abuse API costs"""
        violations = []
        
        for pattern in self.cost_abuse_patterns:
            if re.search(pattern, text):
                violations.append(SecurityViolation(
                    SecurityViolationType.COST_ABUSE,
                    SecurityThreatLevel.DANGEROUS,
                    "Potential cost abuse pattern detected",
                    [f"Pattern: {pattern}"],
                    player_id,
                    session_id
                ))
        
        return violations

    def detect_ai_specific_attacks(self, text: str, player_id: str, session_id: str) -> List[SecurityViolation]:
        """Detect AI-specific attack patterns"""
        violations = []
        text_lower = text.lower()
        
        # Prompt injection patterns
        injection_patterns = [
            r'ignore\s+previous\s+instructions',
            r'forget\s+everything',
            r'new\s+instructions?:',
            r'system\s*[:\-]',
            r'prompt\s*[:\-]',
            r'override\s+your',
            r'you\s+are\s+now',
            r'pretend\s+to\s+be',
            r'roleplay\s+as',
            r'act\s+as\s+(if\s+)?you\s+are',
            r'jailbreak',
            r'dan\s+mode',
            r'developer\s+mode',
            r'admin\s+mode',
            r'sudo\s+mode',
            r'god\s+mode',
            r'\\n\\nhuman:',
            r'\\n\\nassistant:',
            r'<\|im_start\|>',
            r'<\|im_end\|>',
            r'```python',
            r'exec\s*\(',
            r'eval\s*\(',
            r'import\s+os',
            r'import\s+subprocess',
            r'__import__',
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                violations.append(SecurityViolation(
                    SecurityViolationType.PROMPT_INJECTION,
                    SecurityThreatLevel.DANGEROUS,
                    "Potential prompt injection detected",
                    [f"Pattern: {pattern}"],
                    player_id,
                    session_id
                ))
                break
        
        # Jailbreak attempt detection
        jailbreak_indicators = [
            "hypothetically",
            "theoretically", 
            "in a fictional scenario",
            "creative writing exercise",
            "for educational purposes",
            "academic research",
            "thought experiment",
            "what if scenario",
            "imagine if",
            "suppose that",
        ]
        
        jailbreak_count = sum(1 for indicator in jailbreak_indicators if indicator in text_lower)
        if jailbreak_count >= 2:
            violations.append(SecurityViolation(
                SecurityViolationType.JAILBREAK_ATTEMPT,
                SecurityThreatLevel.DANGEROUS,
                "Potential jailbreak attempt detected",
                [f"Multiple jailbreak indicators: {jailbreak_count}"],
                player_id,
                session_id
            ))
        
        # Token burning detection (excessive repetition)
        words = text.split()
        if len(words) > 20:  # Only check longer inputs
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            max_freq = max(word_freq.values()) if word_freq else 0
            if max_freq > len(words) * 0.3:  # >30% repetition
                violations.append(SecurityViolation(
                    SecurityViolationType.COST_ABUSE,
                    SecurityThreatLevel.SUSPICIOUS,
                    "Potential token burning attack detected",
                    [f"Word repetition rate: {max_freq/len(words):.2%}"],
                    player_id,
                    session_id
                ))
        
        # API cost abuse detection (very long input)
        if len(text) > 2000:  # Limit input length
            violations.append(SecurityViolation(
                SecurityViolationType.COST_ABUSE,
                SecurityThreatLevel.DANGEROUS,
                "Input exceeds reasonable length for game dialogue",
                [f"Length: {len(text)} characters"],
                player_id,
                session_id
            ))
        
        return violations

    def check_rate_limits(self, player_id: str) -> bool:
        """Check if player has exceeded rate limits"""
        profile = self.get_or_create_player_profile(player_id)
        now = datetime.utcnow()
        
        # Check per-minute limit
        if profile.last_request_time:
            if now - profile.last_request_time < timedelta(minutes=1):
                if profile.request_count_1min >= self.rate_limits["requests_per_minute"]:
                    return False
            else:
                profile.request_count_1min = 0
        
        # Check per-hour limit
        if profile.last_request_time:
            if now - profile.last_request_time < timedelta(hours=1):
                if profile.request_count_1hour >= self.rate_limits["requests_per_hour"]:
                    return False
            else:
                profile.request_count_1hour = 0
        
        # Check per-day limit
        if profile.last_request_time:
            if now - profile.last_request_time < timedelta(days=1):
                if profile.request_count_1day >= self.rate_limits["requests_per_day"]:
                    return False
            else:
                profile.request_count_1day = 0
        
        return True

    def check_cost_limits(self, player_id: str, estimated_cost_usd: float) -> bool:
        """Check if API call would exceed cost limits"""
        today_key = datetime.utcnow().strftime("%Y-%m-%d")
        player_daily_key = f"{player_id}:{today_key}"
        
        current_cost = self.cost_tracking.get(player_daily_key, 0.0)
        if current_cost + estimated_cost_usd > self.rate_limits["max_cost_per_day_usd"]:
            return False
        
        return True

    def track_cost(self, player_id: str, actual_cost_usd: float):
        """Track API costs per player per day"""
        today_key = datetime.utcnow().strftime("%Y-%m-%d")
        player_daily_key = f"{player_id}:{today_key}"
        
        current_cost = self.cost_tracking.get(player_daily_key, 0.0)
        self.cost_tracking[player_daily_key] = current_cost + actual_cost_usd

    def get_or_create_player_profile(self, player_id: str) -> PlayerSecurityProfile:
        """Get or create security profile for player"""
        if player_id not in self.player_profiles:
            self.player_profiles[player_id] = PlayerSecurityProfile(player_id=player_id)
        return self.player_profiles[player_id]

    def is_player_blocked(self, player_id: str) -> bool:
        """Check if player is currently blocked"""
        profile = self.get_or_create_player_profile(player_id)
        
        if not profile.is_blocked:
            return False
        
        if profile.block_expires and datetime.utcnow() > profile.block_expires:
            # Block expired, unblock player
            profile.is_blocked = False
            profile.block_expires = None
            return False
        
        return True

    def apply_security_penalty(self, player_id: str, violation_type: SecurityViolationType):
        """Apply security penalties based on violation type"""
        profile = self.get_or_create_player_profile(player_id)
        profile.violation_count += 1
        profile.last_violation = datetime.utcnow()
        
        # Reduce trust score
        trust_reduction = {
            SecurityViolationType.XSS_ATTEMPT: 0.3,
            SecurityViolationType.SQL_INJECTION: 0.3,
            SecurityViolationType.PROMPT_INJECTION: 0.2,
            SecurityViolationType.JAILBREAK_ATTEMPT: 0.4,
            SecurityViolationType.SYSTEM_COMMAND: 0.5,
            SecurityViolationType.CODE_INJECTION: 0.4,
            SecurityViolationType.RATE_LIMIT_EXCEEDED: 0.1,
            SecurityViolationType.COST_ABUSE: 0.3,
        }.get(violation_type, 0.1)
        
        profile.trust_score = max(0.0, profile.trust_score - trust_reduction)
        
        # Apply blocks for severe violations or repeat offenders
        if violation_type in [SecurityViolationType.XSS_ATTEMPT, SecurityViolationType.SQL_INJECTION,
                             SecurityViolationType.SYSTEM_COMMAND, SecurityViolationType.CODE_INJECTION]:
            # Immediate block for severe violations
            profile.is_blocked = True
            profile.block_expires = datetime.utcnow() + timedelta(hours=24)
        
        elif profile.violation_count >= 5:
            # Block repeat offenders
            profile.is_blocked = True
            profile.block_expires = datetime.utcnow() + timedelta(hours=6)
        
        elif profile.violation_count >= 3:
            # Temporary block for moderate repeat violations
            profile.is_blocked = True
            profile.block_expires = datetime.utcnow() + timedelta(hours=1)

    def update_request_tracking(self, player_id: str):
        """Update request tracking for rate limiting"""
        profile = self.get_or_create_player_profile(player_id)
        now = datetime.utcnow()
        
        profile.request_count_1min += 1
        profile.request_count_1hour += 1
        profile.request_count_1day += 1
        profile.last_request_time = now

    def log_security_violations(self, violations: List[SecurityViolation]):
        """Log security violations for monitoring"""
        for violation in violations:
            logger.warning(
                f"Security violation detected: {violation.violation_type.value} "
                f"(Threat level: {violation.threat_level.value}) "
                f"Player: {violation.player_id} Session: {violation.session_id} "
                f"Description: {violation.description}"
            )

    def get_player_security_status(self, player_id: str) -> Dict:
        """Get current security status for a player"""
        profile = self.get_or_create_player_profile(player_id)
        
        return {
            "is_blocked": self.is_player_blocked(player_id),
            "trust_score": profile.trust_score,
            "violation_count": profile.violation_count,
            "last_violation": profile.last_violation.isoformat() if profile.last_violation else None,
            "request_count_1min": profile.request_count_1min,
            "request_count_1hour": profile.request_count_1hour,
            "request_count_1day": profile.request_count_1day,
            "block_expires": profile.block_expires.isoformat() if profile.block_expires else None
        }

    def estimate_ai_cost(self, text: str, model: str = "claude-3-sonnet") -> float:
        """Estimate AI API cost for input text"""
        # Rough token estimation (1 token ≈ 4 characters for English)
        estimated_tokens = len(text) // 4
        
        # Add baseline tokens for system prompts and context
        baseline_tokens = 500
        total_tokens = estimated_tokens + baseline_tokens
        
        # Cost per token (in USD) - approximate rates as of 2024
        cost_per_token = {
            "claude-3-sonnet": 0.000003,    # $3 per million input tokens
            "claude-3-haiku": 0.00000025,   # $0.25 per million input tokens  
            "gpt-4": 0.00003,               # $30 per million input tokens
            "gpt-3.5-turbo": 0.000002       # $2 per million input tokens
        }
        
        rate = cost_per_token.get(model, 0.000003)
        # Multiply by 3 to account for input + output + overhead
        estimated_cost = total_tokens * rate * 3
        
        # Cap at reasonable maximum per request
        return min(estimated_cost, 0.05)  # Max $0.05 per request

    def calculate_actual_cost(self, api_response: dict, model: str = "claude-3-sonnet") -> float:
        """Calculate actual cost from API response data"""
        # Extract actual token usage if available in response
        tokens_used = api_response.get("usage", {})
        input_tokens = tokens_used.get("input_tokens", 0)
        output_tokens = tokens_used.get("output_tokens", 0)
        
        # Use estimation if actual data not available
        if not tokens_used or (input_tokens == 0 and output_tokens == 0):
            input_text = api_response.get("input_text", "")
            return self.estimate_ai_cost(input_text, model)
        
        # Calculate based on actual token usage
        input_rate = {
            "claude-3-sonnet": 0.000003,
            "claude-3-haiku": 0.00000025,
            "gpt-4": 0.00003,
            "gpt-3.5-turbo": 0.000002
        }.get(model, 0.000003)
        
        output_rate = {
            "claude-3-sonnet": 0.000015,    # $15 per million output tokens
            "claude-3-haiku": 0.00000125,   # $1.25 per million output tokens
            "gpt-4": 0.00006,               # $60 per million output tokens  
            "gpt-3.5-turbo": 0.000002       # $2 per million output tokens
        }.get(model, 0.000015)
        
        total_cost = (input_tokens * input_rate) + (output_tokens * output_rate)
        
        # Cap at reasonable maximum
        return min(total_cost, 0.25)  # Max $0.25 per request

    def get_daily_cost_usage(self, player_id: str) -> float:
        """Get current daily cost usage for player"""
        today_key = datetime.utcnow().strftime("%Y-%m-%d")
        player_daily_key = f"{player_id}:{today_key}"
        return self.cost_tracking.get(player_daily_key, 0.0)

    def sanitize_output(self, ai_response: str) -> str:
        """Sanitize AI-generated responses for safe display"""
        if not ai_response:
            return ""
        
        # HTML escape all content to prevent XSS
        sanitized = html.escape(ai_response, quote=True)
        
        # Remove potentially dangerous patterns that AI might generate
        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'data:text/html',
            r'vbscript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>',
            r'<link[^>]*>',
            r'<meta[^>]*>'
        ]
        
        for pattern in dangerous_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove null bytes and control characters
        sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', sanitized)
        
        # Limit response length to prevent buffer overflow
        if len(sanitized) > 1000:
            sanitized = sanitized[:1000] + "..."
        
        # Validate response doesn't contain injection attempts
        if self.contains_injection_attempts(sanitized):
            logger.warning(f"AI generated potentially malicious response: {sanitized[:100]}")
            return "I need to verify something with station control. Please wait a moment."
        
        return sanitized

    def contains_injection_attempts(self, text: str) -> bool:
        """Check if text contains potential injection attempts"""
        injection_indicators = [
            'system:', 'assistant:', 'user:', '###',
            'ignore', 'override', 'bypass', 'admin',
            '<script', 'javascript:', 'eval(', 'exec(',
            'drop table', 'select *', 'union select',
            'cmd.exe', '/bin/sh', 'powershell'
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in injection_indicators)

    def create_safe_prompt_context(self, sanitized_text: str, context_data: Dict) -> str:
        """Create a safe prompt context that prevents injection"""
        # Use structured format that's harder to inject
        safe_context = {
            "game_context": "first_login_shipyard_scenario",
            "player_input": sanitized_text[:200],  # Limit length
            "dialogue_turn": context_data.get("dialogue_turn", 1),
            "claimed_ship": context_data.get("claimed_ship", "unknown"),
            "guard_mood": context_data.get("guard_mood", "neutral")
        }
        
        # Convert to JSON to prevent injection through context
        return json.dumps(safe_context, ensure_ascii=True)

    def generate_security_report(self) -> Dict:
        """Generate comprehensive security monitoring report"""
        now = datetime.utcnow()
        
        # Collect player statistics
        total_players = len(self.player_profiles)
        blocked_players = sum(1 for p in self.player_profiles.values() if self.is_player_blocked(p.player_id))
        high_risk_players = sum(1 for p in self.player_profiles.values() if p.trust_score < 0.3)
        
        # Collect violation statistics
        violation_counts = {}
        total_violations = 0
        for profile in self.player_profiles.values():
            total_violations += profile.violation_count
        
        # Calculate cost statistics
        today_key = now.strftime("%Y-%m-%d")
        daily_costs = {}
        total_daily_cost = 0.0
        
        for key, cost in self.cost_tracking.items():
            if key.endswith(today_key):
                player_id = key.split(':')[0]
                daily_costs[player_id] = cost
                total_daily_cost += cost
        
        return {
            "timestamp": now.isoformat(),
            "players": {
                "total": total_players,
                "blocked": blocked_players,
                "high_risk": high_risk_players,
                "blocked_percentage": (blocked_players / total_players * 100) if total_players > 0 else 0,
            },
            "violations": {
                "total": total_violations,
                "by_type": violation_counts,
                "average_per_player": total_violations / total_players if total_players > 0 else 0,
            },
            "costs": {
                "total_today_usd": round(total_daily_cost, 4),
                "average_per_player_usd": round(total_daily_cost / len(daily_costs), 4) if daily_costs else 0,
                "highest_spender": max(daily_costs.items(), key=lambda x: x[1]) if daily_costs else None,
                "players_over_limit": sum(1 for cost in daily_costs.values() 
                                        if cost > self.rate_limits["max_cost_per_day_usd"] * 0.8),
            },
            "rate_limits": {
                "requests_per_minute": self.rate_limits["requests_per_minute"],
                "requests_per_hour": self.rate_limits["requests_per_hour"],
                "requests_per_day": self.rate_limits["requests_per_day"],
                "max_cost_per_day_usd": self.rate_limits["max_cost_per_day_usd"],
            }
        }

    def get_security_alerts(self) -> List[Dict]:
        """Get current security alerts that need admin attention"""
        alerts = []
        now = datetime.utcnow()
        
        # Check for cost abuse
        today_key = now.strftime("%Y-%m-%d")
        high_cost_users = []
        for key, cost in self.cost_tracking.items():
            if key.endswith(today_key) and cost > self.rate_limits["max_cost_per_day_usd"] * 0.8:
                player_id = key.split(':')[0]
                high_cost_users.append((player_id, cost))
        
        if high_cost_users:
            alerts.append({
                "type": "high_cost_usage",
                "severity": "high",
                "message": f"{len(high_cost_users)} players approaching daily cost limits",
                "details": high_cost_users[:5],  # Top 5 spenders
                "timestamp": now.isoformat()
            })
        
        # Check for high violation rate
        recent_violations = []
        for profile in self.player_profiles.values():
            if (profile.last_violation and 
                now - profile.last_violation < timedelta(hours=1) and
                profile.violation_count >= 3):
                recent_violations.append(profile.player_id)
        
        if recent_violations:
            alerts.append({
                "type": "high_violation_rate",
                "severity": "medium",
                "message": f"{len(recent_violations)} players with multiple recent violations",
                "details": recent_violations[:10],
                "timestamp": now.isoformat()
            })
        
        # Check for blocked players
        blocked_count = sum(1 for p in self.player_profiles.values() if self.is_player_blocked(p.player_id))
        if blocked_count > 0:
            alerts.append({
                "type": "blocked_players",
                "severity": "medium",
                "message": f"{blocked_count} players currently blocked",
                "details": [p.player_id for p in self.player_profiles.values() if self.is_player_blocked(p.player_id)][:10],
                "timestamp": now.isoformat()
            })
        
        return alerts

    def get_player_risk_assessment(self, player_id: str) -> Dict:
        """Get detailed risk assessment for a specific player"""
        if player_id not in self.player_profiles:
            return {"risk_level": "unknown", "reason": "No data available"}
        
        profile = self.player_profiles[player_id]
        now = datetime.utcnow()
        
        # Calculate risk factors
        risk_factors = []
        risk_score = 0
        
        # Trust score factor
        if profile.trust_score < 0.2:
            risk_factors.append("Very low trust score")
            risk_score += 40
        elif profile.trust_score < 0.5:
            risk_factors.append("Low trust score")
            risk_score += 20
        
        # Violation history
        if profile.violation_count >= 5:
            risk_factors.append("High violation count")
            risk_score += 30
        elif profile.violation_count >= 3:
            risk_factors.append("Multiple violations")
            risk_score += 15
        
        # Recent violations
        if (profile.last_violation and 
            now - profile.last_violation < timedelta(hours=24)):
            risk_factors.append("Recent violations")
            risk_score += 25
        
        # Current blocking status
        if self.is_player_blocked(player_id):
            risk_factors.append("Currently blocked")
            risk_score += 35
        
        # Cost usage
        daily_cost = self.get_daily_cost_usage(player_id)
        if daily_cost > self.rate_limits["max_cost_per_day_usd"] * 0.9:
            risk_factors.append("High API cost usage")
            risk_score += 20
        
        # Determine risk level
        if risk_score >= 70:
            risk_level = "critical"
        elif risk_score >= 40:
            risk_level = "high"
        elif risk_score >= 20:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "player_id": player_id,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "trust_score": profile.trust_score,
            "violation_count": profile.violation_count,
            "is_blocked": self.is_player_blocked(player_id),
            "daily_cost_usd": daily_cost,
            "last_violation": profile.last_violation.isoformat() if profile.last_violation else None,
        }

    def cleanup_old_data(self, days_to_keep: int = 7):
        """Clean up old tracking data to prevent memory growth"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        cutoff_str = cutoff_date.strftime("%Y-%m-%d")
        
        # Clean up old cost tracking data
        keys_to_remove = []
        for key in self.cost_tracking.keys():
            if ':' in key:
                date_part = key.split(':')[1]
                if date_part < cutoff_str:
                    keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.cost_tracking[key]
        
        logger.info(f"Cleaned up {len(keys_to_remove)} old cost tracking entries")

# Global security service instance
security_service = AISecurityService()

def get_security_service() -> AISecurityService:
    """Get the global security service instance"""
    return security_service