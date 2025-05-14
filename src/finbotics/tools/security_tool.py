from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from datetime import datetime
import json
from pathlib import Path

class SecurityValidationInput(BaseModel):
    """Input schema for Security Validation Tool"""
    customer_id: str = Field(description="Customer ID requesting access")
    data_type: str = Field(description="Type of data being accessed")
    action: str = Field(description="Action being performed (read/write/delete)")

class SecurityTool(BaseTool):
    name: str = "Security Validation Tool"
    description: str = "Validates data access permissions and logs access attempts"
    args_schema: Type[BaseModel] = SecurityValidationInput
    
    def _run(self, customer_id: str, data_type: str, action: str) -> str:
        """Validate access and log the attempt"""
        try:
            # Define allowed customer - in production this would be configurable
            allowed_customer_id = "acme_ai"
            audit_log_path = Path("security_audit.log")
            
            # Simple validation
            access_granted = (customer_id == allowed_customer_id)
            
            # Create audit log entry
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "customer_id": customer_id,
                "data_type": data_type,
                "action": action,
                "access_granted": access_granted,
                "ip_address": "127.0.0.1"  # Mock IP
            }
            
            # Append to audit log
            with open(audit_log_path, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
            
            if access_granted:
                return f"Access GRANTED for customer '{customer_id}' to {action} {data_type} data."
            else:
                return f"Access DENIED for customer '{customer_id}'. Unauthorized access attempt logged."
                
        except Exception as e:
            return f"Security validation error: {str(e)}"