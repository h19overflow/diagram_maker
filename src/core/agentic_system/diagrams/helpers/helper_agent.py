# from langchain_aws import ChatBedrockConverse
from src.core.agentic_system.respone_formats import HelperResponse
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_agent
from langchain_core.documents import Document
from typing import List
from logging import getLogger
from src.core.agentic_system.diagrams.helpers.consts import get_system_prompt, get_user_prompt_template

logger = getLogger(__name__)


def _format_documents_to_context(documents: List[Document]) -> str:
    """
    Format a list of documents into a context string.
    Concatenates all page_content and appends sources with page numbers at the end.

    Args:
        documents: List of Document objects

    Returns:
        Formatted context string with content and sources
    """
    if not documents:
        return ""

    # Concatenate all page_content with newline separators
    content_parts = [doc.page_content for doc in documents if doc.page_content]
    context_text = "\n\n".join(content_parts)

    # Extract page numbers from metadata
    page_numbers = []
    for doc in documents:
        if doc.metadata:
            # Try different possible keys for page number
            page = (
                doc.metadata.get("page") or
                doc.metadata.get("page_number") or
                doc.metadata.get("pagenumber")
            )
            if page is not None:
                try:
                    page_num = int(page)
                    if page_num not in page_numbers:
                        page_numbers.append(page_num)
                except (ValueError, TypeError):
                    pass

    # Sort page numbers and format sources
    if page_numbers:
        page_numbers.sort()
        sources_text = f"Sources: page {', page '.join(map(str, page_numbers))}"
        return f"{context_text}\n\n{sources_text}"

    return context_text


# def get_llm() -> ChatBedrockConverse:
#     """Get the LLM for the helper agent"""
#     try:
#         llm = ChatBedrockConverse(
#             model_id="amazon.nova-pro-v1:0",
#         )
#         return llm
#     except Exception as e:
#         logger.error(f"Error getting LLM for helper agent: {e}")
#         return None


def get_prompt():
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
            model='google_genai:gemini-2.5-flash-lite',
            tools=[],
            system_prompt=get_system_prompt(),
            response_format=HelperResponse,
        )
        return agent
    except Exception as e:
        logger.error(f"Error getting agent for helper agent: {e}")
        return None


def invoke_agent(input: str, context: List[Document] | str) -> HelperResponse:
    """
    Invoke the agent for the helper agent and return structured response.

    Args:
        input: The question/input to answer
        context: Either a list of Document objects or a string context

    Returns:
        HelperResponse object or None on error
    """
    try:
        agent = get_agent()
        if agent is None:
            raise ValueError("Failed to initialize agent")
        prompt_template = get_prompt()
        if prompt_template is None:
            raise ValueError("Failed to create prompt template")

        # Convert Document list to formatted string if needed
        if isinstance(context, list):
            context_str = _format_documents_to_context(context)
        else:
            context_str = context

        prompt = prompt_template.invoke({"context": context_str, "input": input})
        response = agent.invoke(prompt)

        # Extract structured_response from agent response (create_agent returns dict with messages and structured_response)
        if isinstance(response, dict):
            structured_response = response.get("structured_response")
        elif hasattr(response, "structured_response"):
            structured_response = response.structured_response
        else:
            structured_response = response

        return structured_response
    except Exception as e:
        logger.error(f"Error invoking agent for helper agent: {e}")
        return None


if __name__ == "__main__":
    input = "What is the main idea of the document?"
    context = "This is a document talking about humans in the world they are really cool "
    response = invoke_agent(input, context)
    print(response)
