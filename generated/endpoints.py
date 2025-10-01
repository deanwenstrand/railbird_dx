# AUTO-GENERATED FILE - DO NOT EDIT MANUALLY
# Generated from PlayScript endpoint definitions

from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any, Optional
from core.web.database import get_db
import logging

logger = logging.getLogger(__name__)

try:
    from .security.guards import require_permission  # type: ignore
except Exception:
    # Fail-secure: when security guards are unavailable, deny all protected requests
    def require_permission(object_name: str, action: str):  # type: ignore
        def _deny():
            raise HTTPException(status_code=503, detail="Security guards not available")
        return _deny


# Generated endpoint functions




# Router setup
router = APIRouter()

# Route registrations



