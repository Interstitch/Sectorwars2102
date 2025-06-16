#!/usr/bin/env python3
"""
🔧 UTILS - Shared Utilities
==========================

Common functions used across the memory system.

Created: 2025-06-08
Version: 2.0 (The Great Consolidation)
"""

import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional

def generate_id(content: str, timestamp: Optional[datetime] = None) -> str:
    """Generate unique ID for content"""
    if timestamp is None:
        timestamp = datetime.now()
    
    seed = f"{content}{timestamp.isoformat()}"
    return hashlib.sha256(seed.encode()).hexdigest()[:16]

def safe_json_loads(data: str) -> Optional[Dict[str, Any]]:
    """Safely parse JSON with error handling"""
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return None

def ensure_directory(path: Path) -> Path:
    """Ensure directory exists"""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path

def format_timestamp(dt: datetime) -> str:
    """Format datetime for display"""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def truncate_text(text: str, max_length: int = 80) -> str:
    """Truncate text with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def calculate_checksum(file_path: Path) -> str:
    """Calculate file checksum"""
    if not file_path.exists():
        return ""
    
    hasher = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            # Read in chunks for large files
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
    except:
        return ""