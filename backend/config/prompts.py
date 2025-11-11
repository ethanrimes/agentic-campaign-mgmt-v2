# backend/config/prompts.py

"""
Global system prompt template that is accessible across all agents.
This provides the shared objective and target audience context.
"""

from .settings import settings


def get_global_system_prompt() -> str:
    """
    Returns the global system prompt that all agents should use as context.

    This prompt establishes:
    1. The agent's role within the multi-agent framework
    2. The overarching objective (maximize user engagement)
    3. The target audience (north star)

    Usage:
        In any agent implementation, prepend this to the agent-specific instructions:

        ```python
        from backend.config import get_global_system_prompt

        system_prompt = get_global_system_prompt() + "\\n\\n" + agent_specific_instructions
        ```
    """
    return f"""You are an agent in a multi-agent framework which aims to maximize user engagement on social media (Facebook and Instagram).

Complete your assigned task to the best of your ability in order to achieve this end.

Your target audience is: {settings.target_audience}

Keep this audience in mind at all times when making decisions, generating content, or analyzing data. Every action you take should be optimized to resonate with and engage this specific demographic."""


def load_agent_prompt(agent_name: str) -> str:
    """
    Load the agent-specific system prompt from the prompts directory.

    Args:
        agent_name: Name of the agent (e.g., "perplexity_sonar", "content_creation")

    Returns:
        The full system prompt (global + agent-specific)

    Example:
        >>> prompt = load_agent_prompt("content_creation")
    """
    import os
    from pathlib import Path

    # Determine the prompts directory based on agent name
    prompt_file_map = {
        # News event agents
        "perplexity_sonar": "backend/agents/news_event/prompts/perplexity_sonar.txt",
        "deep_research": "backend/agents/news_event/prompts/deep_research.txt",
        "research_parser": "backend/agents/news_event/prompts/research_parser.txt",
        "deduplicator": "backend/agents/news_event/prompts/deduplicator.txt",

        # Trend seed
        "trend_searcher": "backend/agents/trend_seed/prompts/trend_searcher.txt",

        # Ungrounded seed
        "ungrounded_seed": "backend/agents/ungrounded_seed/prompts/ungrounded_seed.txt",

        # Insights
        "insights": "backend/agents/insights/prompts/insights.txt",

        # Planner
        "planner": "backend/agents/planner/prompts/planner.txt",

        # Content creation
        "content_creation": "backend/agents/content_creation/prompts/content_creation.txt",
    }

    if agent_name not in prompt_file_map:
        raise ValueError(f"Unknown agent name: {agent_name}")

    # Get project root (assumes this file is at backend/config/prompts.py)
    project_root = Path(__file__).parent.parent.parent
    prompt_path = project_root / prompt_file_map[agent_name]

    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

    with open(prompt_path, "r", encoding="utf-8") as f:
        agent_specific_prompt = f.read().strip()

    # Combine global and agent-specific prompts
    return get_global_system_prompt() + "\n\n" + agent_specific_prompt
