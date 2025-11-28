# backend/agents/ungrounded_seed/ungrounded_agent.py

"""Creative content ideation agent (not grounded in news or trends)."""

from pathlib import Path
from typing import Dict, Any, List, Literal
from pydantic import BaseModel, Field
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

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

    Uses a two-phase approach:
    1. Optional exploration phase with tools
    2. Direct structured output generation
    """

    def __init__(self, business_asset_id: str):
        self.business_asset_id = business_asset_id
        self.repo = UngroundedSeedRepository()

        # Load prompts
        prompt_path = Path(__file__).parent / "prompts" / "ungrounded_seed.txt"
        self.agent_prompt = prompt_path.read_text()
        self.global_prompt = get_global_system_prompt(self.business_asset_id)

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=settings.default_model_name,
            api_key=settings.get_model_api_key(),
            temperature=0.9,  # High temperature for creativity
        )

        # Create tools (only knowledge base access)
        self.tools = create_knowledge_base_tools()

    async def generate_ideas(self, count: int = 1) -> List[Dict[str, Any]]:
        """
        Generate creative content ideas using a two-phase approach.

        Phase 1: Optional exploration with tools (max 3 iterations)
        Phase 2: Direct structured output generation

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

                # PHASE 1: Exploration with tools (optional, limited)
                exploration_agent = create_agent(
                    model=self.llm,
                    tools=self.tools,
                    system_prompt=f"{self.global_prompt}\n\n{self.agent_prompt}",
                )

                exploration_prompt = """Briefly review existing content if helpful (max 2 tool calls).
Then describe your content idea in natural language. You don't need to format it yet - just describe:
- What the content is about
- Why it would be engaging
- What format would work best

After checking tools (or if you don't need tools), provide your raw idea description."""

                exploration_result = await exploration_agent.ainvoke(
                    {"messages": [("human", exploration_prompt)]},
                    config={"verbose": True, "max_iterations": 3}
                )

                logger.info("Exploration phase complete, generating structured output")

                # PHASE 2: Direct structured output (no agent, no tools)
                structured_llm = self.llm.with_structured_output(UngroundedSeedOutput)

                # Get the conversation history from exploration
                messages = exploration_result.get("messages", [])
                messages.append((
                    "human",
                    """Now provide the final structured content idea with all details in the required format:
- idea: Clear, concise description (1-2 sentences)
- format: One of: image, video, carousel, reel, story, text
- details: Detailed creative direction and execution notes (2-3 paragraphs)"""
                ))

                structured_output = await structured_llm.ainvoke(messages)

                if structured_output:
                    # Save directly to database
                    ungrounded_seed = UngroundedSeed(
                        business_asset_id=self.business_asset_id,
                        idea=structured_output.idea,
                        format=structured_output.format,
                        details=structured_output.details,
                        created_by=settings.default_model_name
                    )

                    created_seed = await self.repo.create(ungrounded_seed)
                    logger.info("Ungrounded seed saved", seed_id=str(created_seed.id))
                    seeds.append(created_seed.model_dump(mode="json"))
                else:
                    logger.warning("Failed to generate structured output")

            except Exception as e:
                logger.error(f"Error generating idea {i+1}", error=str(e), exc_info=True)

        logger.info("Ungrounded seed generation complete", seeds_created=len(seeds))
        return seeds

async def run_ungrounded_generation(business_asset_id: str, count: int = 1) -> List[Dict[str, Any]]:
    """
    CLI entry point for ungrounded seed generation.

    Args:
        business_asset_id: Business asset ID for multi-tenancy
        count: Number of ideas to generate

    Returns:
        List of created ungrounded seeds
    """
    agent = UngroundedSeedAgent(business_asset_id)
    return await agent.generate_ideas(count)
