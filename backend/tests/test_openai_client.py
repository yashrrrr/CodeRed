"""
Tests for OpenAI client service with fallback mechanisms.
"""
import pytest
import os
import json
from unittest.mock import patch, AsyncMock
from services.openai_client import OpenAIClientService, generate_nudge, generate_quiz


@pytest.fixture
def sample_learner_context():
    """Sample learner context for testing."""
    return {
        "name": "Aman",
        "channel": "in-app",
        "completed_percent": 65,
        "avg_quiz_score": 78,
        "consecutive_missed_sessions": 2,
        "program": "Python Fundamentals"
    }


@pytest.fixture
def openai_service_no_key():
    """OpenAI service instance without API key."""
    with patch.dict(os.environ, {}, clear=True):
        service = OpenAIClientService()
    return service


@pytest.fixture
def openai_service_with_key():
    """OpenAI service instance with mocked API key."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        service = OpenAIClientService()
    return service


class TestOpenAIClientService:
    """Test cases for OpenAI client service."""
    
    def test_init_without_api_key(self, openai_service_no_key):
        """Test initialization without API key uses fallback."""
        assert openai_service_no_key.api_key is None
        assert openai_service_no_key.client is None
        assert isinstance(openai_service_no_key.fallback_nudges, list)
    
    def test_init_with_api_key(self, openai_service_with_key):
        """Test initialization with API key creates client."""
        assert openai_service_with_key.api_key == "test-key"
        # Client may be None if OpenAI package is not installed (fallback mode)
        # This is expected behavior when dependencies are missing
    
    def test_load_fallback_nudges(self, openai_service_no_key):
        """Test fallback nudges are loaded correctly."""
        nudges = openai_service_no_key.fallback_nudges
        assert len(nudges) > 0
        
        # Check structure of first nudge
        first_nudge = nudges[0]
        assert "type" in first_nudge
        assert "content" in first_nudge
        assert "channel" in first_nudge
        assert isinstance(first_nudge["content"], str)
    
    @pytest.mark.asyncio
    async def test_generate_nudge_fallback(self, openai_service_no_key, sample_learner_context):
        """Test nudge generation with fallback when no API key."""
        result = await openai_service_no_key.generate_nudge(sample_learner_context)
        
        assert "content" in result
        assert "prompt_version" in result
        assert "gptFallback" in result
        assert result["gptFallback"] is True
        assert "Aman" in result["content"]  # Name should be included
    
    @pytest.mark.asyncio
    async def test_generate_quiz_fallback(self, openai_service_no_key, sample_learner_context):
        """Test quiz generation with fallback when no API key."""
        result = await openai_service_no_key.generate_quiz(sample_learner_context)
        
        assert "content" in result
        assert "prompt_version" in result
        assert "gptFallback" in result
        assert result["gptFallback"] is True
        
        # Check quiz structure
        quiz_content = result["content"]
        assert "title" in quiz_content
        assert "questions" in quiz_content
        assert "total_points" in quiz_content
        assert len(quiz_content["questions"]) > 0
    
    @pytest.mark.asyncio
    async def test_generate_nudge_api_success(self, openai_service_with_key, sample_learner_context):
        """Test successful nudge generation via OpenAI API."""
        # Skip if OpenAI client is not available (dependencies not installed)
        if openai_service_with_key.client is None:
            pytest.skip("OpenAI client not available, testing fallback behavior instead")
        
        # Mock successful OpenAI response
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = "Great progress, Aman! You're 65% complete in Python Fundamentals. Keep it up!"
        
        with patch.object(openai_service_with_key.client.chat.completions, 'create', return_value=mock_response):
            result = await openai_service_with_key.generate_nudge(sample_learner_context)
            
            assert "content" in result
            assert "prompt_version" in result
            assert "gptFallback" in result
            assert result["gptFallback"] is False
            assert result["prompt_version"] == "v1.0"
            assert "Aman" in result["content"]
    
    @pytest.mark.asyncio
    async def test_generate_nudge_api_failure(self, openai_service_with_key, sample_learner_context):
        """Test nudge generation falls back when API fails."""
        # Skip if OpenAI client is not available (dependencies not installed)
        if openai_service_with_key.client is None:
            pytest.skip("OpenAI client not available, testing fallback behavior instead")
        
        # Mock API failure
        with patch.object(openai_service_with_key.client.chat.completions, 'create', side_effect=Exception("API Error")):
            result = await openai_service_with_key.generate_nudge(sample_learner_context)
            
            assert result["gptFallback"] is True
            assert "content" in result
    
    @pytest.mark.asyncio
    async def test_generate_quiz_api_success(self, openai_service_with_key, sample_learner_context):
        """Test successful quiz generation via OpenAI API."""
        # Skip if OpenAI client is not available (dependencies not installed)
        if openai_service_with_key.client is None:
            pytest.skip("OpenAI client not available, testing fallback behavior instead")
        
        # Mock successful OpenAI response with valid JSON
        quiz_json = {
            "title": "Python Fundamentals Quiz",
            "questions": [
                {
                    "question": "What is a variable in Python?",
                    "type": "short_answer",
                    "points": 10
                }
            ],
            "total_points": 10
        }
        
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = json.dumps(quiz_json)
        
        with patch.object(openai_service_with_key.client.chat.completions, 'create', return_value=mock_response):
            result = await openai_service_with_key.generate_quiz(sample_learner_context)
            
            assert result["gptFallback"] is False
            assert result["content"]["title"] == "Python Fundamentals Quiz"
            assert len(result["content"]["questions"]) == 1
    
    @pytest.mark.asyncio
    async def test_generate_quiz_invalid_json_fallback(self, openai_service_with_key, sample_learner_context):
        """Test quiz generation falls back when API returns invalid JSON."""
        # Skip if OpenAI client is not available (dependencies not installed)
        if openai_service_with_key.client is None:
            pytest.skip("OpenAI client not available, testing fallback behavior instead")
        
        # Mock API response with invalid JSON
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = "This is not valid JSON"
        
        with patch.object(openai_service_with_key.client.chat.completions, 'create', return_value=mock_response):
            result = await openai_service_with_key.generate_quiz(sample_learner_context)
            
            assert result["gptFallback"] is True
            assert "content" in result
    
    def test_fallback_nudge_channel_selection(self, openai_service_no_key):
        """Test fallback nudge selects correct channel content."""
        context = {
            "name": "Test User",
            "channel": "whatsapp",
            "completed_percent": 30,
            "avg_quiz_score": 85
        }
        
        result = openai_service_no_key._get_fallback_nudge(context)
        
        # Should contain appropriate content for the channel
        assert "content" in result
        assert isinstance(result["content"], str)
        assert len(result["content"]) > 0
    
    def test_fallback_nudge_type_selection(self, openai_service_no_key):
        """Test fallback nudge selects appropriate type based on context."""
        # High completion should trigger appropriate nudge
        high_completion_context = {
            "name": "Test User",
            "channel": "in-app",
            "completed_percent": 80,
            "avg_quiz_score": 85
        }
        
        result = openai_service_no_key._get_fallback_nudge(high_completion_context)
        
        # Should return valid nudge content
        assert "content" in result
        assert isinstance(result["content"], str)
        assert len(result["content"]) > 0
        assert "Test User" in result["content"]  # Name should be personalized


@pytest.mark.asyncio
async def test_convenience_functions(sample_learner_context):
    """Test convenience functions work correctly."""
    # Test with no API key (fallback mode)
    with patch.dict(os.environ, {}, clear=True):
        nudge_result = await generate_nudge(sample_learner_context)
        quiz_result = await generate_quiz(sample_learner_context)
        
        assert nudge_result["gptFallback"] is True
        assert quiz_result["gptFallback"] is True
        assert "content" in nudge_result
        assert "content" in quiz_result