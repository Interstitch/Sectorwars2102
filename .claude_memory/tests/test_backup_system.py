#!/usr/bin/env python3
"""
Test suite for backup and recovery functionality
Ensures memory persistence and data safety
"""

import pytest
import sys
import os
import tempfile
import shutil
import tarfile
import json
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory_core import MemoryCore
from persistence import MemoryPersistence


class TestBackupSystem:
    """Test suite for backup and recovery"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def memory_core(self, temp_dir):
        """Create MemoryCore with test data"""
        core = MemoryCore(memory_path=temp_dir)
        
        # Add test memories
        test_memories = [
            ("Max is the creator", {"person": "Max", "role": "creator"}),
            ("Kaida is the AI designer", {"person": "Kaida", "role": "AI designer"}),
            ("Project Sectorwars2102", {"project": "Sectorwars2102"}),
            ("Quantum trading system", {"feature": "quantum trading"}),
            ("Memory persistence test", {"type": "test"})
        ]
        
        for content, context in test_memories:
            core.store(content, context)
        
        core.save()
        return core
    
    @pytest.fixture
    def persistence(self, memory_core):
        """Create MemoryPersistence instance"""
        return MemoryPersistence(memory_core)
    
    def test_create_backup(self, persistence, temp_dir):
        """Test backup creation"""
        backup_path = persistence.create_backup()
        
        assert backup_path is not None
        assert os.path.exists(backup_path)
        assert backup_path.endswith('.tar.gz')
        
        # Verify backup contents
        with tarfile.open(backup_path, 'r:gz') as tar:
            members = tar.getnames()
            assert 'memories.json' in members
            assert 'metadata.json' in members
    
    def test_restore_backup(self, persistence, temp_dir):
        """Test backup restoration"""
        # Create backup
        backup_path = persistence.create_backup()
        
        # Clear current memories
        persistence.memory_core.memories.clear()
        persistence.memory_core.save()
        
        # Verify memories are gone
        assert len(persistence.memory_core.memories) == 0
        
        # Restore from backup
        success = persistence.restore_backup(backup_path)
        assert success is True
        
        # Verify memories are restored
        assert len(persistence.memory_core.memories) == 5
        
        # Check specific memory content
        results = persistence.memory_core.search("Max")
        assert len(results) > 0
        assert any("creator" in r['content'] for r in results)
    
    def test_automatic_backup_on_threshold(self, persistence):
        """Test automatic backup triggers"""
        # Set low threshold for testing
        persistence.backup_threshold = 3
        
        # Add memories to trigger backup
        for i in range(5):
            persistence.memory_core.store(f"Auto backup test {i}")
        
        # Check if backup was created
        backup_dir = Path(persistence.memory_core.memory_path) / "backups"
        if backup_dir.exists():
            backups = list(backup_dir.glob("*.tar.gz"))
            assert len(backups) > 0
    
    def test_backup_metadata(self, persistence, temp_dir):
        """Test backup metadata generation"""
        backup_path = persistence.create_backup()
        
        # Extract and verify metadata
        with tarfile.open(backup_path, 'r:gz') as tar:
            metadata_file = tar.extractfile('metadata.json')
            metadata = json.load(metadata_file)
            
            assert 'timestamp' in metadata
            assert 'memory_count' in metadata
            assert 'version' in metadata
            assert metadata['memory_count'] == 5
    
    def test_backup_compression(self, persistence):
        """Test backup compression effectiveness"""
        # Add larger memories
        for i in range(20):
            large_content = f"Large memory content {i} " * 100
            persistence.memory_core.store(large_content)
        
        persistence.memory_core.save()
        
        # Create backup
        backup_path = persistence.create_backup()
        
        # Check compression
        backup_size = os.path.getsize(backup_path)
        original_size = os.path.getsize(
            Path(persistence.memory_core.memory_path) / "memories.json"
        )
        
        # Backup should be compressed
        assert backup_size < original_size
    
    def test_backup_rotation(self, persistence):
        """Test old backup cleanup"""
        backup_dir = Path(persistence.memory_core.memory_path) / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        # Create multiple backups
        for i in range(10):
            backup_path = persistence.create_backup()
        
        # Set max backups
        persistence.max_backups = 5
        persistence.cleanup_old_backups()
        
        # Should only keep 5 most recent
        backups = list(backup_dir.glob("*.tar.gz"))
        assert len(backups) <= 5
    
    def test_incremental_backup(self, persistence):
        """Test incremental backup functionality"""
        # Create initial backup
        full_backup = persistence.create_backup()
        
        # Add new memories
        persistence.memory_core.store("New memory after backup")
        persistence.memory_core.store("Another new memory")
        
        # Create incremental backup
        incremental_backup = persistence.create_incremental_backup(full_backup)
        
        assert incremental_backup is not None
        assert os.path.exists(incremental_backup)
        assert os.path.getsize(incremental_backup) < os.path.getsize(full_backup)
    
    def test_backup_integrity_check(self, persistence):
        """Test backup integrity verification"""
        backup_path = persistence.create_backup()
        
        # Verify integrity
        is_valid = persistence.verify_backup_integrity(backup_path)
        assert is_valid is True
        
        # Corrupt backup file
        with open(backup_path, 'ab') as f:
            f.write(b'corrupted data')
        
        # Should detect corruption
        is_valid = persistence.verify_backup_integrity(backup_path)
        assert is_valid is False
    
    def test_emergency_recovery(self, persistence, temp_dir):
        """Test emergency recovery procedures"""
        # Simulate corrupted memory file
        memory_file = Path(temp_dir) / "memories.json"
        
        # Write invalid JSON
        with open(memory_file, 'w') as f:
            f.write("{'invalid': json content")
        
        # Should recover from backup
        recovered = persistence.emergency_recovery()
        assert recovered is True
        
        # Should have restored memories
        assert len(persistence.memory_core.memories) > 0
    
    def test_backup_scheduling(self, persistence):
        """Test scheduled backup functionality"""
        # Configure scheduled backups
        schedule_config = {
            'enabled': True,
            'interval_hours': 24,
            'max_backups': 7
        }
        
        persistence.configure_scheduled_backups(schedule_config)
        
        # Verify configuration
        assert persistence.scheduled_backups_enabled is True
        assert persistence.backup_interval == 24 * 3600  # Convert to seconds


if __name__ == "__main__":
    pytest.main([__file__, "-v"])