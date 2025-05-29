"""
Audit Log model for security and compliance tracking
"""

from sqlalchemy import Column, String, DateTime, Integer, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from src.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Request information
    method = Column(String(10), nullable=False)
    path = Column(String(255), nullable=False, index=True)
    status_code = Column(Integer)
    duration_ms = Column(Integer)
    
    # User information
    user_id = Column(UUID(as_uuid=True), index=True)  # Can be null for unauthenticated requests
    user_type = Column(String(20))  # 'admin', 'player', 'anonymous'
    client_ip = Column(String(45), nullable=False)  # Support IPv6
    user_agent = Column(Text)
    
    # Action details
    action = Column(String(100), index=True)  # e.g., 'login', 'logout', 'economy_intervention'
    resource_type = Column(String(50))  # e.g., 'auth', 'ship', 'economy', 'message'
    resource_id = Column(UUID(as_uuid=True))  # ID of affected resource
    
    # Additional context
    query_params = Column(JSON)
    request_body = Column(JSON)  # Sanitized request body (no passwords)
    response_summary = Column(Text)  # Brief summary of response
    
    # Security information
    security_flags = Column(JSON)  # Any security warnings or flags
    violation_detected = Column(String(100))  # Type of violation if any
    
    # Indexing for common queries
    __table_args__ = (
        # Composite index for user activity queries
        {"schema": None},
    )
    
    def __repr__(self):
        return f"<AuditLog {self.id} {self.action} by {self.user_id or 'anonymous'} at {self.timestamp}>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "method": self.method,
            "path": self.path,
            "status_code": self.status_code,
            "duration_ms": self.duration_ms,
            "user_id": str(self.user_id) if self.user_id else None,
            "user_type": self.user_type,
            "client_ip": self.client_ip,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": str(self.resource_id) if self.resource_id else None,
            "security_flags": self.security_flags,
            "violation_detected": self.violation_detected
        }