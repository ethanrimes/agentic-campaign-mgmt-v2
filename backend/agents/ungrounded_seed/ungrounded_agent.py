# backend/agents/ungrounded_seed/ungrounded_agent.py

"""Creative content ideation agent (not grounded in news or trends)."""

from pathlib import Path
from typing import Dict, Any, List
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from backend.config.settings import settings
from backend.config.prompts import get_global_system_prompt
from backend.tools import create_knowledge_base_tools
from backend.database.repositories.ungrounded_seeds import UngroundedSeedsRepository
from backend.models.seeds import UngroundedSeed
from backend.utils import get_logger

logger = get_logger(__name__)


class UngroundedSeedAgent:
    """
    Agent for generating creative, ungrounded content ideas.

    Creates original content concepts not based on news or social media trends.
    """

    def __init__(self):
        self.repo = UngroundedSeedsRepository()

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

        # Create agent prompt template
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", f"{self.global_prompt}\n\n{self.agent_prompt}"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # Create agent
        self.agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt_template
        )

        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=10,
            return_intermediate_steps=True
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

                # Run agent
                result = await self.agent_executor.ainvoke({
                    "input": f"""Generate a creative, original content idea for our social media.

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
                })

                # Extract the output
                output = result["output"]

                # Parse and save ungrounded seed
                seed = await self._parse_and_save_seed(output)

                if seed:
                    seeds.append(seed)
                    logger.info("Ungrounded seed created", seed_id=seed["id"])

            except Exception as e:
                logger.error(f"Error generating idea {i+1}", error=str(e))

        logger.info("Ungrounded seed generation complete", seeds_created=len(seeds))
        return seeds

    async def _parse_and_save_seed(self, agent_output: str) -> Dict[str, Any]:
        """Parse agent output and save ungrounded seed."""
        # Use LLM to extract structured data from agent output
        structured_data = await self._extract_structured_seed(agent_output)

        # Save to database
        ungrounded_seed = UngroundedSeed(
            idea=structured_data.get("idea", agent_output[:200]),
            format=structured_data.get("format", "text"),
            details=structured_data.get("details", agent_output),
            created_by=settings.default_model_name
        )

        # Save to database (note: create is synchronous, not async)
        created_seed = self.repo.create(ungrounded_seed)

        logger.info("Ungrounded seed saved", seed_id=str(created_seed.id))

        return created_seed.model_dump(mode="json")

    async def _extract_structured_seed(self, agent_output: str) -> Dict[str, Any]:
        """Use LLM to extract structured seed data from agent output."""
        extraction_prompt = f"""Extract structured content idea information from the following creative concept.

Content Idea:
{agent_output}

Provide a JSON response with:
{{
  "idea": "Clear, concise description of the content concept (1-2 sentences)",
  "format": "The medium (must be one of: image, video, carousel, reel, story, text)",
  "details": "Detailed creative direction and execution notes (2-3 paragraphs)"
}}

Make sure:
- The idea is concise and captures the core concept
- The format is a single, specific medium (not multiple)
- The details provide actionable creative direction
"""

        extraction_llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=settings.openai_api_key,
            temperature=0.3
        )

        messages = [
            {"role": "system", "content": "You are a data extraction assistant. Extract structured information from text."},
            {"role": "user", "content": extraction_prompt}
        ]

        response = await extraction_llm.ainvoke(messages)

        # Parse JSON
        import json
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            logger.warning("Failed to parse extraction response")
            return {
                "idea": agent_output[:200],
                "format": "text",
                "details": agent_output
            }


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
