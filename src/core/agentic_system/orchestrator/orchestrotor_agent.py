from langchain_aws import ChatBedrockConverse
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_agent
from src.core.agentic_system.respone_formats import NodeTitles
import logging
from src.core.agentic_system.orchestrator.validate_structure import (
    validate_hierarchical_structure,
    validate_node_count,
)
from src.core.agentic_system.orchestrator.consts import MAX_NODES, get_system_prompt, get_user_prompt_template

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)




def get_llm() -> ChatBedrockConverse:
    """Get the LLM for the orchestrator agent"""
    try:
        llm = ChatBedrockConverse(
            model_id="amazon.nova-pro-v1:0",
        )
        return llm
    except Exception as e:
        logger.error(f"Error getting LLM for orchestrator agent: {e}")
        return None


def get_prompt(input: str):
    """Get the prompt for the orchestrator agent with hierarchical structure guidance"""

    try:
        prompt_invoked = ChatPromptTemplate.from_messages(
            [
                ("system", get_system_prompt(MAX_NODES)),
                ("user", get_user_prompt_template().format(input=input)),
            ]
        )
        prompt_invoked = prompt_invoked.invoke({"input": input})
        return prompt_invoked
    except Exception as e:
        logger.error(f"Error getting prompt for orchestrator agent: {e}")
        return None


def get_agent():
    """Get the agent for the orchestrator agent"""
    try:
        llm = get_llm()
        if llm is None:
            raise ValueError("Failed to initialize LLM")
        agent = create_agent(
            model=llm,
            tools=[],
            response_format=NodeTitles,
        )
        return agent
    except Exception as e:
        logger.error(f"Error getting agent for orchestrator agent: {e}")
        return None


def invoke_agent(input: str) -> NodeTitles:
    """Invoke the agent for the orchestrator agent and return structured hierarchical titles"""
    try:
        agent = get_agent()
        if agent is None:
            raise ValueError("Failed to initialize agent")

        logger.info(f"Invoking agent for input: {input}")
        prompt = get_prompt(input)

        if prompt is None:
            raise ValueError("Failed to generate prompt")

        logger.info("Prompt generated successfully")
        response = agent.invoke(prompt)

        # Validate hierarchical structure and node count
        if response and hasattr(response, "nodes"):
            node_count = len(response.nodes)
            logger.info(f"Validating hierarchical structure with {node_count} nodes")

            # Check node count limit
            if not validate_node_count(node_count):
                logger.error(
                    f"Response exceeds node limit. Maximum allowed: {MAX_NODES}"
                )

            # Validate structure
            if not validate_hierarchical_structure(response.nodes):
                logger.warning(
                    "Hierarchical structure validation found issues - reviewing output"
                )

            logger.info("Hierarchical structure validation completed")

        return response["structured_response"]
    except Exception as e:
        logger.error(f"Error invoking agent for orchestrator agent: {e}")
        return None


if __name__ == "__main__":
    input = "I want to create a diagram of the human body"
    response = invoke_agent(input)
    print(response["structured_response"])
