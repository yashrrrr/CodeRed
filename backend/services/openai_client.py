"""
OpenAI client service with fallback mechanisms for nudge and quiz generation.
"""
import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import httpx
    from openai import AsyncOpenAI
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    httpx = None
    AsyncOpenAI = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenAIClientService:
    """OpenAI client with fallback to local templates when API is unavailable."""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        self.fallback_nudges = self._load_fallback_nudges()
        
        if self.api_key and DEPENDENCIES_AVAILABLE:
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                http_client=httpx.AsyncClient(timeout=8.0)
            )
            logger.info("OpenAI client initialized with API key")
        else:
            if not DEPENDENCIES_AVAILABLE:
                logger.warning("OpenAI dependencies not available, using fallback content")
            elif not self.api_key:
                logger.warning("OpenAI API key not found, will use fallback content")
            else:
                logger.warning("Using fallback content")
    
    def _load_fallback_nudges(self) -> list:
        """Load fallback nudges from JSON file."""
        try:
            fallback_path = Path(__file__).parent.parent.parent / "prompts" / "fallback_nudges.json"
            with open(fallback_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load fallback nudges: {e}")
            return []
    
    def _get_fallback_nudge(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback nudge content based on learner context."""
        if not self.fallback_nudges:
            return {
                "content": f"Hi {context.get('name', 'there')}! Time to continue your learning journey.",
                "prompt_version": "fallback_v1.0",
                "gptFallback": True
            }
        
        # Select appropriate fallback based on context
        nudge_type = "engagement"  # default
        
        # Determine nudge type based on context
        completion = context.get('completed_percent', 0)
        if completion > 50:
            nudge_type = "completion_boost"
        elif context.get('avg_quiz_score', 100) < 70:
            nudge_type = "quiz_reminder"
        
        # Find matching fallback template
        template = None
        for nudge in self.fallback_nudges:
            if nudge.get('type') == nudge_type:
                template = nudge
                break
        
        if not template:
            template = self.fallback_nudges[0]  # Use first as default
        
        # Get content for specified channel
        channel = context.get('channel', 'in-app')
        
        # Find template matching the requested channel
        channel_template = None
        for nudge in self.fallback_nudges:
            if nudge.get('channel') == channel and nudge.get('type') == nudge_type:
                channel_template = nudge
                break
        
        # If no channel-specific template found, use any template with matching type
        if not channel_template:
            for nudge in self.fallback_nudges:
                if nudge.get('type') == nudge_type:
                    channel_template = nudge
                    break
        
        # If still no template, use the first available
        if not channel_template:
            channel_template = self.fallback_nudges[0]
        
        content_template = channel_template['content']
        
        # Format content with learner data
        try:
            content = content_template.format(
                name=context.get('name', 'there'),
                completion=context.get('completed_percent', 0)
            )
        except (KeyError, ValueError) as e:
            logger.warning(f"Template formatting error: {e}")
            # Simple replacement if format fails
            content = content_template.replace('{name}', context.get('name', 'there'))
            content = content.replace('{completion}', str(context.get('completed_percent', 0)))
        
        return {
            "content": content,
            "prompt_version": "fallback_v1.0",
            "gptFallback": True
        }
    
    def _get_fallback_quiz(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback quiz content."""
        program = context.get('program', 'your course')
        
        return {
            "content": {
                "title": f"Knowledge Check: {program}",
                "questions": [
                    {
                        "question": f"What is the most important concept you've learned in {program} so far?",
                        "type": "open_ended",
                        "points": 10
                    },
                    {
                        "question": f"How would you apply the concepts from {program} in a real-world scenario?",
                        "type": "open_ended", 
                        "points": 10
                    },
                    {
                        "question": f"What aspect of {program} would you like to explore further?",
                        "type": "open_ended",
                        "points": 5
                    }
                ],
                "total_points": 25
            },
            "prompt_version": "fallback_v1.0",
            "gptFallback": True
        }
    
    async def generate_nudge(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate personalized nudge for a learner.
        
        Args:
            context: Dictionary containing learner data and nudge parameters
                - name: learner name
                - channel: delivery channel (in-app, whatsapp, email)
                - completed_percent: completion percentage
                - avg_quiz_score: average quiz score
                - consecutive_missed_sessions: missed sessions count
                - program: program name
        
        Returns:
            Dictionary with content, prompt_version, and gptFallback flag
        """
        # Use fallback if no API key or client
        if not self.client:
            logger.info("Using fallback nudge - no OpenAI client available")
            return self._get_fallback_nudge(context)
        
        try:
            # Prepare prompt for OpenAI
            channel = context.get('channel', 'in-app')
            name = context.get('name', 'there')
            program = context.get('program', 'the course')
            completion = context.get('completed_percent', 0)
            quiz_score = context.get('avg_quiz_score', 0)
            missed_sessions = context.get('consecutive_missed_sessions', 0)
            
            prompt = f"""Generate a personalized learning nudge for {name} who is enrolled in {program}.

Learner Context:
- Completion: {completion}%
- Average quiz score: {quiz_score}%
- Consecutive missed sessions: {missed_sessions}
- Delivery channel: {channel}

Requirements:
- Be encouraging and supportive
- Reference their specific progress
- Include a clear call to action
- Match the tone for {channel} channel
- Keep it concise but engaging
- Use their name naturally

Generate only the nudge content, no additional formatting or explanations."""

            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a supportive learning coach who creates personalized, encouraging messages for learners."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            # Extract content with defensive parsing
            content = ""
            if response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                if content:
                    content = content.strip()
            
            if not content:
                logger.warning("Empty response from OpenAI, using fallback")
                return self._get_fallback_nudge(context)
            
            return {
                "content": content,
                "prompt_version": "v1.0",
                "gptFallback": False
            }
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            return self._get_fallback_nudge(context)
    
    async def generate_quiz(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate quiz content for a learner.
        
        Args:
            context: Dictionary containing learner data
                - name: learner name
                - program: program name
                - completed_percent: completion percentage
                - recent_topics: list of recent topics (optional)
        
        Returns:
            Dictionary with quiz content, prompt_version, and gptFallback flag
        """
        # Use fallback if no API key or client
        if not self.client:
            logger.info("Using fallback quiz - no OpenAI client available")
            return self._get_fallback_quiz(context)
        
        try:
            name = context.get('name', 'there')
            program = context.get('program', 'the course')
            completion = context.get('completed_percent', 0)
            recent_topics = context.get('recent_topics', [])
            
            topics_context = ""
            if recent_topics:
                topics_context = f"Recent topics covered: {', '.join(recent_topics)}"
            
            prompt = f"""Create a quiz for {name} who is {completion}% through {program}.

Context:
{topics_context}

Requirements:
- Generate 3-5 questions appropriate for their progress level
- Mix of question types (multiple choice, short answer, scenario-based)
- Include point values for each question
- Questions should test understanding, not just memorization
- Make it engaging and relevant to {program}

Return the quiz in this JSON format:
{{
    "title": "Quiz title",
    "questions": [
        {{
            "question": "Question text",
            "type": "multiple_choice|short_answer|scenario",
            "options": ["A", "B", "C", "D"] (only for multiple choice),
            "points": 10
        }}
    ],
    "total_points": 50
}}"""

            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an educational content creator who designs effective quizzes. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.5
            )
            
            # Extract and parse content with defensive parsing
            content = ""
            if response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                if content:
                    content = content.strip()
            
            if not content:
                logger.warning("Empty response from OpenAI, using fallback")
                return self._get_fallback_quiz(context)
            
            # Try to parse JSON response
            try:
                quiz_data = json.loads(content)
                return {
                    "content": quiz_data,
                    "prompt_version": "v1.0",
                    "gptFallback": False
                }
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse OpenAI JSON response: {e}")
                return self._get_fallback_quiz(context)
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            return self._get_fallback_quiz(context)


# Global service instance
openai_service = OpenAIClientService()

# Convenience functions for easy import
async def generate_nudge(context: Dict[str, Any]) -> Dict[str, Any]:
    """Generate personalized nudge for a learner."""
    return await openai_service.generate_nudge(context)

async def generate_quiz(context: Dict[str, Any]) -> Dict[str, Any]:
    """Generate quiz content for a learner."""
    return await openai_service.generate_quiz(context)