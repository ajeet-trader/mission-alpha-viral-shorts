"""
CrewAI Multi-Agent Provider Plugin

Uses multiple specialized AI agents working together.
"""

from crewai import Agent, Task, Crew
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from app.core.interfaces import IAIProvider, ContentItem, ScriptResult
from app.core.logger import log_step, log_success, log_info
import logging

logger = logging.getLogger(__name__)


class CrewAIProvider(IAIProvider):
    """Multi-agent AI using CrewAI for collaborative script generation."""
    
    def __init__(self, config):
        self.config = config
        api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found")
        
        self.llm = ChatGoogleGenerativeAI(
            model=config.model,
            temperature=config.temperature,
            google_api_key=api_key
        )
        
        log_success(f"CrewAI initialized with {len(config.multi_agent.agents)} agents")
    
    async def generate_script(self, content: ContentItem, style: str = "hinglish") -> ScriptResult:
        """Generate script using multi-agent collaboration."""
        log_step("🤖 Multi-Agent Script Generation (CrewAI)", "3 agents collaborating...")
        
        # Define agents
        researcher = Agent(
            role="Content Analyzer",
            goal="Analyze content and identify viral potential",
            backstory="Expert at understanding what makes content go viral on Indian social media",
            llm=self.llm,
            verbose=True
        )
        
        scriptwriter = Agent(
            role="Hinglish Scriptwriter",
            goal="Write engaging 45-second scripts in Hinglish",
            backstory="Bilingual copywriter specialized in Indian audience engagement",
            llm=self.llm,
            verbose=True
        )
        
        critic = Agent(
            role="Quality Critic  ",
            goal="Ensure maximum engagement and viral potential",
            backstory="YouTube optimization expert with deep understanding of Shorts algorithm",
            llm=self.llm,
            verbose=True
        )
        
        # Define tasks
        analysis_task = Task(
            description=f"Analyze this content: {content.title}\n{content.body[:200]}\nIdentify key viral angles.",
            agent=researcher,
            expected_output="Viral angles and hook ideas"
        )
        
        writing_task = Task(
            description=f"Write a 45-second Hinglish script for YouTube Shorts about: {content.title}",
            agent=scriptwriter,
            expected_output="Complete script with hook, body, and CTA"
        )
        
        review_task = Task(
            description="Review the script and optimize for maximum engagement",
            agent=critic,
            expected_output="Final optimized script"
        )
        
        # Create crew
        log_info("👥 Agents: Researcher → Scriptwriter → Critic")
        crew = Crew(
            agents=[researcher, scriptwriter, critic],
            tasks=[analysis_task, writing_task, review_task],
            verbose=True
        )
        
        # Execute
        result = crew.kickoff()
        
        # Parse result
        script_text = str(result)
        
        # Simple parsing (can be improved)
        parts = script_text.split('\n\n')
        hook = parts[0] if len(parts) > 0 else script_text[:100]
        body = parts[1] if len(parts) > 1 else script_text[100:400]
        cta = parts[-1] if len(parts) > 2 else "Like and follow for more!"
        
        log_success("✓ Multi-agent script complete!")
        
        return ScriptResult(
            hook=hook,
            body=body,
            cta=cta,
            full_script=script_text,
            provider="crewai",
            metadata={
                "model": self.config.model,
                "agents_used": len(self.config.multi_agent.agents),
                "content_type": content.type
            }
        )
    
    def get_provider_name(self) -> str:
        return "CrewAI (Multi-Agent)"
