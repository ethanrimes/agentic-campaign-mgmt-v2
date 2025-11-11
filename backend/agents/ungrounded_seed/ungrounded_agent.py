# backend/agents/ungrounded_seed/ungrounded_agent.py

"""Creative content ideation agent (not grounded in news or trends)."""

from pathlib import Path
from typing import Dict, Any, List, Literal
from pydantic import BaseModel, Field
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from backend.config.settings import settings
from backend.config.prompts import get_global_system_prompt
from backend.tools import create_knowledge_base_tools
from backend.database.repositories.ungrounded_seeds import UngroundedSeedRepository
from backend.models.seeds import UngroundedSeed
from backend.utils import get_logger

logger = get_logger(__name__)


class UngroundedSeedOutput(BaseModel):
    """A structured creative content idea."""
    idea: str = Field(..., description="Clear, concise description of the content concept (1-2 sentences)")
    format: Literal["image", "video", "carousel", "reel", "story", "text"] = Field(
        ...,
        description="The medium (must be one of: image, video, carousel, reel, story, text)"
    )
    details: str = Field(..., description="Detailed creative direction and execution notes (2-3 paragraphs)")


class UngroundedSeedAgent:
    """
    Agent for generating creative, ungrounded content ideas.

    Creates original content concepts not based on news or social media trends.
    """

    def __init__(self):
        self.repo = UngroundedSeedRepository()

        # Load prompts
        prompt_path = Path(__file__).parent / "prompts" / "ungrounded_seed.txt"
        self.agent_prompt = prompt_path.read_text()
        self.global_prompt = get_global_system_prompt()

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=settings.default_model_name,
            api_key=settings.get_model_api_key(),
            temperature=0.9,  # High temperature for creativity
        )

        # Create tools (only knowledge base access)
        self.tools = create_knowledge_base_tools()

        # Create agent
        self.agent_executor = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=f"{self.global_prompt}\n\n{self.agent_prompt}",
            response_format=ToolStrategy(UngroundedSeedOutput)
        )

    async def generate_ideas(self, count: int = 1) -> List[Dict[str, Any]]:
        """
        Generate creative content ideas.

        Args:
            count: Number of ideas to generate

        Returns:
            List of created ungrounded seeds
        """
        logger.info("Starting ungrounded seed generation", count=count)

        seeds = []

        for i in range(count):
            try:
                logger.info(f"Generating idea {i+1}/{count}")

                input_context = f"""Generate a creative, original content idea for our social media.

Instructions:
1. First, use your tools to review what content has been successful and what gaps exist
2. Then, create a completely original content concept
3. Make sure it's different from existing content seeds

Your idea should be:
- Creative and engaging
- Aligned with our target audience
- Executable with clear direction
- Varied in format (don't repeat the same format)

Provide a structured content idea with:
- A clear concept/idea description
- The intended format (image, video, carousel, reel, text, etc.)
- Detailed creative direction for execution
"""
                # Run agent
                config = {"verbose": True, "max_iterations": 10}
                result = await self.agent_executor.ainvoke(
                    {"messages": [("human", input_context)]},
                    config=config
                )

                # The agent's structured response is here
                structured_output: UngroundedSeedOutput = result.get("structured_response")

                if structured_output:
                    # Save directly to database
                    ungrounded_seed = UngroundedSeed(
                        idea=structured_output.idea,
                        format=structured_output.format,
                        details=structured_output.details,
                        created_by=settings.default_model_name
                    )

                    created_seed = self.repo.create(ungrounded_seed)
                    logger.info("Ungrounded seed saved", seed_id=str(created_seed.id))
                    seeds.append(created_seed.model_dump(mode="json"))
                else:
                    logger.warning("Agent did not return a structured response")

            except Exception as e:
                logger.error(f"Error generating idea {i+1}", error=str(e))

        logger.info("Ungrounded seed generation complete", seeds_created=len(seeds))
        return seeds


async def run_ungrounded_generation(count: int = 1) -> List[Dict[str, Any]]:
    """
    CLI entry point for ungrounded seed generation.

    Args:
        count: Number of ideas to generate

    Returns:
        List of created ungrounded seeds
    """
    agent = UngroundedSeedAgent()
    return await agent.generate_ideas(count)