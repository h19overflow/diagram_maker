from langchain_aws import ChatBedrockConverse
from src.core.agentic_system.respone_formats import HelperResponse
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_agent
from logging import getLogger
from src.core.agentic_system.helpers.consts import get_system_prompt, get_user_prompt_template

logger = getLogger(__name__)


def get_llm() -> ChatBedrockConverse:
    """Get the LLM for the helper agent"""
    try:
        llm = ChatBedrockConverse(
            model_id="amazon.nova-pro-v1:0",
        )
        return llm
    except Exception as e:
        logger.error(f"Error getting LLM for helper agent: {e}")
        return None


def get_prompt(input: str, context: str):
    """Get the prompt for the helper agent"""
    try:
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    get_system_prompt(),
                ),
                (
                    "user",
                    get_user_prompt_template(),
                ),
            ]
        )
        return prompt
    except Exception as e:
        logger.error(f"Error getting prompt for helper agent: {e}")
        return None


def get_agent():
    """Get the agent for the helper agent"""
    try:
        agent = create_agent(
            model=get_llm(),
            tools=[],
            system_prompt=get_system_prompt(),
            response_format=HelperResponse,
        )
        return agent
    except Exception as e:
        logger.error(f"Error getting agent for helper agent: {e}")
        return None


def invoke_agent(input: str, context: str) -> HelperResponse:
    """Invoke the agent for the helper agent and return structured response"""
    try:
        agent = get_agent()
        if agent is None:
            raise ValueError("Failed to initialize agent")
        prompt_template = get_prompt(input, context)
        if prompt_template is None:
            raise ValueError("Failed to create prompt template")
        prompt = prompt_template.invoke({"context": context, "input": input})
        response = agent.invoke(prompt)
        return response
    except Exception as e:
        logger.error(f"Error invoking agent for helper agent: {e}")
        return None


if __name__ == "__main__":
    input = "What is the main idea of the document?"
    context = "This is a document talking about humans in the world they are really cool "
    response = invoke_agent(input, context)
    print(response)
