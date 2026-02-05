"""
Audit logging for security and compliance
Tracks all sensitive operations and data access
"""
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import AuditLog, User


class AuditLogger:
    """Service for creating audit logs"""
    
    @staticmethod
    def log_event(
        db: Session,
        user_id: Optional[int],
        event_type: str,
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[dict] = None
    ) -> Optional[AuditLog]:
        """
        Create an audit log entry
        MODIFIED: Only logs to console (No DB storage)
        """
        from loguru import logger
        logger.info(f"AUDIT LOG: User {user_id} performed {action} on {resource_type or 'N/A'}:{resource_id or 'N/A'}. Details: {details}")
        return None
    
    @staticmethod
    def log_login(db: Session, user_id: int, ip_address: str, user_agent: str, success: bool):
        """Log user login attempt"""
        AuditLogger.log_event(
            db=db,
            user_id=user_id if success else None,
            event_type="login",
            action="success" if success else "failed",
            ip_address=ip_address,
            user_agent=user_agent,
            details={"success": success}
        )
    
    @staticmethod
    def log_logout(db: Session, user_id: int, ip_address: str, user_agent: str):
        """Log user logout"""
        AuditLogger.log_event(
            db=db,
            user_id=user_id,
            event_type="logout",
            action="logout",
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def log_data_access(
        db: Session,
        user_id: int,
        resource_type: str,
        resource_id: int,
        action: str = "read",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log access to sensitive data"""
        AuditLogger.log_event(
            db=db,
            user_id=user_id,
            event_type="data_access",
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def log_data_modification(
        db: Session,
        user_id: int,
        resource_type: str,
        resource_id: int,
        action: str,
        changes: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log data creation, update, or deletion"""
        AuditLogger.log_event(
            db=db,
            user_id=user_id,
            event_type="data_modify",
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details={"changes": changes} if changes else None
        )
    
    @staticmethod
    def log_security_event(
        db: Session,
        event_type: str,
        details: dict,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log security-related events"""
        AuditLogger.log_event(
            db=db,
            user_id=user_id,
            event_type=f"security_{event_type}",
            action=event_type,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details
        )
    
    @staticmethod
    def log_integration_event(
        db: Session,
        user_id: int,
        integration_type: str,
        action: str,
        details: Optional[dict] = None
    ):
        """Log API integration events"""
        AuditLogger.log_event(
            db=db,
            user_id=user_id,
            event_type="integration",
            action=action,
            resource_type=integration_type,
            details=details
        )


# Helper decorator for automatic audit logging
def audit_action(event_type: str, action: str, resource_type: str = None):
    """
    Decorator for automatic audit logging of function calls
    
    Usage:
        @audit_action("data_access", "read", "financial_statement")
        def get_financial_data(db, user, statement_id):
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extract db and user from args/kwargs
            db = kwargs.get('db') or (args[0] if len(args) > 0 else None)
            user = kwargs.get('user') or (args[1] if len(args) > 1 else None)
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Log the action
            if db and user:
                AuditLogger.log_event(
                    db=db,
                    user_id=user.id if hasattr(user, 'id') else None,
                    event_type=event_type,
                    action=action,
                    resource_type=resource_type
                )
            
            return result
        return wrapper
    return decorator
