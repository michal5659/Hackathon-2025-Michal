"""
Test suite for Classification Agent
"""
import pytest
from agents.classification_agent import ClassificationAgent


class TestClassificationAgent:
    """Test cases for Classification Agent"""
    
    @pytest.fixture
    def agent(self):
        """Create a classification agent instance"""
        return ClassificationAgent()
    
    @pytest.fixture
    def sample_message(self):
        """Sample message for testing"""
        return {
            'message_id': 'test-001',
            'channel': 'email',
            'sender': 'customer@example.com',
            'content': 'I would like to check the status of my claim #CLM-12345',
            'timestamp': '2025-11-03T10:00:00',
            'metadata': {}
        }
    
    def test_agent_initialization(self, agent):
        """Test that agent initializes correctly"""
        assert agent is not None
        assert agent.llm is not None
        assert agent.agent is not None
    
    def test_classify_message(self, agent, sample_message):
        """Test message classification"""
        result = agent.classify_message(sample_message)
        
        assert result is not None
        assert 'action_id' in result
        assert 'category' in result
        assert 'ivo_attributes' in result
        assert 'confidence' in result
    
    def test_fallback_classification(self, agent, sample_message):
        """Test fallback classification"""
        fallback = agent._get_fallback_classification(sample_message)
        
        assert fallback['action_id'] == 'general_inquiry'
        assert fallback['confidence'] == 0.5
        assert 'ivo_attributes' in fallback


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
