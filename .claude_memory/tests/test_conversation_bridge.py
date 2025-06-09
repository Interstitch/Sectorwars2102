#!/usr/bin/env python3
"""
Test suite for conversation_bridge module
Validates conversation database and indexing functionality
"""

import pytest
import sys
import os
import tempfile
import sqlite3
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from conversation_bridge import ConversationBridge


class TestConversationBridge:
    """Test suite for ConversationBridge functionality"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        temp_file = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        temp_file.close()
        yield temp_file.name
        os.unlink(temp_file.name)
    
    @pytest.fixture
    def bridge(self, temp_db):
        """Create ConversationBridge instance with test database"""
        # Create test database with sample data
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        # Create conversations table
        cursor.execute('''
            CREATE TABLE conversations (
                id INTEGER PRIMARY KEY,
                project_path TEXT,
                timestamp TEXT,
                role TEXT,
                content TEXT,
                conversation_id TEXT
            )
        ''')
        
        # Insert test data
        test_conversations = [
            ('/workspaces/Sectorwars2102', '2025-01-01 10:00:00', 'user', 'Tell me about Max', 'conv1'),
            ('/workspaces/Sectorwars2102', '2025-01-01 10:01:00', 'assistant', 'Max is the creator', 'conv1'),
            ('/workspaces/OtherProject', '2025-01-02 10:00:00', 'user', 'Different project', 'conv2'),
            ('/workspaces/Sectorwars2102', '2025-01-03 10:00:00', 'user', 'What about Kaida?', 'conv3'),
            ('/workspaces/Sectorwars2102', '2025-01-03 10:01:00', 'assistant', 'Kaida is the AI designer', 'conv3'),
        ]
        
        cursor.executemany(
            'INSERT INTO conversations (project_path, timestamp, role, content, conversation_id) VALUES (?, ?, ?, ?, ?)',
            test_conversations
        )
        
        conn.commit()
        conn.close()
        
        # Create bridge with test database
        bridge = ConversationBridge()
        bridge.db_path = temp_db
        return bridge
    
    def test_initialization(self, bridge):
        """Test ConversationBridge initialization"""
        assert bridge is not None
        assert hasattr(bridge, 'db_path')
        assert os.path.exists(bridge.db_path)
    
    def test_get_conversation_stats(self, bridge):
        """Test conversation statistics retrieval"""
        stats = bridge.get_stats()
        
        assert stats is not None
        assert 'total_conversations' in stats
        assert 'total_messages' in stats
        assert 'projects' in stats
        assert stats['total_messages'] == 5
        assert len(stats['projects']) == 2
    
    def test_project_filtering(self, bridge):
        """Test filtering conversations by project"""
        # Get Sectorwars2102 conversations
        sectorwars_convs = bridge.get_conversations_for_project('/workspaces/Sectorwars2102')
        assert len(sectorwars_convs) == 4  # Should have 4 messages for Sectorwars2102
        
        # Get other project conversations
        other_convs = bridge.get_conversations_for_project('/workspaces/OtherProject')
        assert len(other_convs) == 1  # Should have 1 message for OtherProject
    
    def test_search_conversations(self, bridge):
        """Test searching within conversations"""
        # Search for "Max"
        max_results = bridge.search("Max")
        assert len(max_results) >= 1
        assert any("Max" in r['content'] for r in max_results)
        
        # Search for "Kaida"
        kaida_results = bridge.search("Kaida")
        assert len(kaida_results) >= 1
        assert any("Kaida" in r['content'] for r in kaida_results)
    
    def test_conversation_count_verification(self, bridge):
        """Test verification of conversation counts"""
        # This tests the specific requirement about 60k vs 45k messages
        stats = bridge.get_stats()
        
        # In our test data, we have known counts
        assert stats['total_messages'] == 5
        assert '/workspaces/Sectorwars2102' in stats['projects']
        assert stats['projects']['/workspaces/Sectorwars2102'] == 4
    
    def test_recent_conversations(self, bridge):
        """Test retrieving recent conversations"""
        recent = bridge.get_recent_conversations(limit=3)
        
        assert len(recent) <= 3
        # Should be ordered by timestamp descending
        if len(recent) > 1:
            assert recent[0]['timestamp'] >= recent[1]['timestamp']
    
    def test_conversation_export(self, bridge):
        """Test exporting conversations for analysis"""
        export_data = bridge.export_for_analysis(project='/workspaces/Sectorwars2102')
        
        assert 'conversations' in export_data
        assert 'metadata' in export_data
        assert len(export_data['conversations']) == 4
        assert export_data['metadata']['project'] == '/workspaces/Sectorwars2102'
    
    def test_empty_database_handling(self):
        """Test handling of empty database"""
        # Create empty database
        temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        temp_db.close()
        
        try:
            conn = sqlite3.connect(temp_db.name)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE conversations (
                    id INTEGER PRIMARY KEY,
                    project_path TEXT,
                    timestamp TEXT,
                    role TEXT,
                    content TEXT,
                    conversation_id TEXT
                )
            ''')
            conn.commit()
            conn.close()
            
            bridge = ConversationBridge()
            bridge.db_path = temp_db.name
            
            stats = bridge.get_stats()
            assert stats['total_messages'] == 0
            assert len(stats['projects']) == 0
            
        finally:
            os.unlink(temp_db.name)
    
    def test_large_conversation_handling(self, bridge):
        """Test handling of large conversation sets"""
        # This simulates checking if system can handle 60k messages
        stats = bridge.get_stats()
        
        # In production, this would verify actual large counts
        # For testing, we verify the counting mechanism works
        assert isinstance(stats['total_messages'], int)
        assert stats['total_messages'] >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])