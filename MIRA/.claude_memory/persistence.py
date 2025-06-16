#!/usr/bin/env python3
"""
💾 PERSISTENCE - Storage & Retrieval
===================================

Handles all persistent storage operations including
caching, state management, and video generation.

Created: 2025-06-08
Version: 2.0 (The Great Consolidation)
"""

import json
import pickle
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
import hashlib

from utils import ensure_directory, calculate_checksum

class PersistenceManager:
    """
    Manages all persistent storage for the memory system.
    Consolidates video/memvid, caching, and state serialization.
    """
    
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = Path(base_dir) if base_dir else Path.home() / ".claude_memory"
        
        # Storage locations
        self.state_dir = ensure_directory(self.base_dir / "state")
        self.cache_dir = ensure_directory(self.base_dir / "cache")
        self.video_dir = ensure_directory(self.base_dir / "videos")
        
        # Cache settings
        self.cache_ttl = 3600  # 1 hour
        self.max_cache_size = 100  # MB
        
        print("💾 Persistence manager initialized")
    
    def save_state(self, state_data: Dict[str, Any], name: str = "memory_state") -> bool:
        """Save state data to disk"""
        try:
            state_file = self.state_dir / f"{name}.pkl"
            
            # Add metadata
            state_data['_metadata'] = {
                'saved_at': datetime.now().isoformat(),
                'version': '2.0'
            }
            
            # Save with pickle for complex objects
            with open(state_file, 'wb') as f:
                pickle.dump(state_data, f)
            
            # Also save JSON version for debugging
            json_file = self.state_dir / f"{name}.json"
            try:
                # Convert non-serializable objects
                json_data = self._prepare_for_json(state_data)
                with open(json_file, 'w') as f:
                    json.dump(json_data, f, indent=2)
            except:
                pass  # JSON is optional
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving state: {e}")
            return False
    
    def load_state(self, name: str = "memory_state") -> Optional[Dict[str, Any]]:
        """Load state data from disk"""
        state_file = self.state_dir / f"{name}.pkl"
        
        if not state_file.exists():
            return None
        
        try:
            with open(state_file, 'rb') as f:
                state_data = pickle.load(f)
            
            return state_data
            
        except Exception as e:
            print(f"❌ Error loading state: {e}")
            
            # Try JSON fallback
            json_file = self.state_dir / f"{name}.json"
            if json_file.exists():
                try:
                    with open(json_file, 'r') as f:
                        return json.load(f)
                except:
                    pass
            
            return None
    
    def cache_set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set cache value"""
        if ttl is None:
            ttl = self.cache_ttl
        
        try:
            cache_key = hashlib.md5(key.encode()).hexdigest()
            cache_file = self.cache_dir / f"{cache_key}.cache"
            
            cache_data = {
                'key': key,
                'value': value,
                'expires': datetime.now().timestamp() + ttl
            }
            
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            
            return True
            
        except:
            return False
    
    def cache_get(self, key: str) -> Optional[Any]:
        """Get cache value"""
        try:
            cache_key = hashlib.md5(key.encode()).hexdigest()
            cache_file = self.cache_dir / f"{cache_key}.cache"
            
            if not cache_file.exists():
                return None
            
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            # Check expiration
            if datetime.now().timestamp() > cache_data.get('expires', 0):
                cache_file.unlink()  # Delete expired cache
                return None
            
            return cache_data.get('value')
            
        except:
            return None
    
    def clean_cache(self) -> int:
        """Clean expired cache entries"""
        cleaned = 0
        
        for cache_file in self.cache_dir.glob("*.cache"):
            try:
                with open(cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                
                if datetime.now().timestamp() > cache_data.get('expires', 0):
                    cache_file.unlink()
                    cleaned += 1
            except:
                # Remove corrupted cache files
                cache_file.unlink()
                cleaned += 1
        
        return cleaned
    
    async def generate_memory_video(self, memories: List[Dict[str, Any]], 
                                  output_name: str = "memory_journey") -> Optional[Path]:
        """
        Generate a video representation of memories.
        Simplified version - just creates a placeholder for now.
        """
        try:
            # In a real implementation, this would create actual video
            # For now, just create a metadata file
            
            video_file = self.video_dir / f"{output_name}.mp4"
            meta_file = self.video_dir / f"{output_name}.meta.json"
            
            metadata = {
                'created': datetime.now().isoformat(),
                'memory_count': len(memories),
                'duration': len(memories) * 2,  # 2 seconds per memory
                'status': 'placeholder'
            }
            
            with open(meta_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Touch the video file
            video_file.touch()
            
            print(f"🎬 Generated memory video: {video_file.name}")
            return video_file
            
        except Exception as e:
            print(f"❌ Error generating video: {e}")
            return None
    
    def _prepare_for_json(self, obj: Any) -> Any:
        """Prepare object for JSON serialization"""
        if isinstance(obj, dict):
            return {k: self._prepare_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._prepare_for_json(v) for v in obj]
        elif isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Path):
            return str(obj)
        elif hasattr(obj, 'tolist'):  # numpy arrays
            return obj.tolist()
        else:
            return str(obj)
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        stats = {
            'state_files': len(list(self.state_dir.glob("*"))),
            'cache_files': len(list(self.cache_dir.glob("*.cache"))),
            'video_files': len(list(self.video_dir.glob("*.mp4"))),
            'total_size_mb': 0
        }
        
        # Calculate total size
        total_size = 0
        for dir_path in [self.state_dir, self.cache_dir, self.video_dir]:
            for file_path in dir_path.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        
        stats['total_size_mb'] = round(total_size / (1024 * 1024), 2)
        
        return stats


# Test the module
if __name__ == "__main__":
    print("🧪 Testing Persistence Module")
    print("=" * 60)
    
    # Create instance
    persistence = PersistenceManager()
    
    # Test state save/load
    print("\n💾 Testing state persistence...")
    test_state = {
        'memories': ['memory1', 'memory2'],
        'metadata': {'created': datetime.now()}
    }
    
    if persistence.save_state(test_state, "test_state"):
        print("   ✅ State saved")
        
        loaded = persistence.load_state("test_state")
        if loaded:
            print("   ✅ State loaded")
            print(f"      Memories: {len(loaded.get('memories', []))}")
    
    # Test cache
    print("\n💾 Testing cache...")
    persistence.cache_set("test_key", {"data": "test_value"}, ttl=60)
    
    cached = persistence.cache_get("test_key")
    if cached:
        print("   ✅ Cache working")
        print(f"      Value: {cached}")
    
    # Test cleanup
    cleaned = persistence.clean_cache()
    print(f"   🧹 Cleaned {cleaned} expired entries")
    
    # Show stats
    print("\n📊 Storage Statistics:")
    stats = persistence.get_storage_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n✅ Persistence module ready!")