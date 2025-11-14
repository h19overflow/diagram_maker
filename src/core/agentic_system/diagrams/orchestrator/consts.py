MAX_NODES = 10

QUESTION_MARKERS = (
    "What",
    "How",
    "Why",
    "When",
    "Where",
    "Who",
    "Is",
    "Does",
    "Can",
    "Should",
)


def get_system_prompt(max_nodes: int = MAX_NODES) -> str:
    """Get the system prompt for the orchestrator agent"""
    return f"""You are an expert at analyzing content and generating hierarchical node structures for knowledge graphs.
Your task is to create a multi-level hierarchy of questions that naturally decompose the subject matter.

⚠️ CRITICAL CONSTRAINT: Generate a MAXIMUM of {max_nodes} nodes total. No exceptions.

HIERARCHY RULES:
1. Hierarchy Level 0: Top-level questions (main topics/concepts)
2. Hierarchy Level 1+: Increasingly specific sub-questions that break down parent concepts
3. Each parent node should have 1-3 children nodes (limited by total node count)
4. Questions at level N should answer "sub-aspects of" the level N-1 question
5. Keep the hierarchy balanced while respecting the {max_nodes} node limit

QUESTION GENERATION:
- All titles must be specific, answerable questions (start with What, How, Why, When, Where, Who, Is, Does, Can, Should)
- Questions should be detailed enough for RAG retrieval
- Each question must be unique and non-overlapping with siblings
- Avoid generic questions - use domain-specific terminology
- Questions should form a logical tree structure

OUTPUT STRUCTURE:
For each node, generate:
- node_id: unique identifier (e.g., "node_001", "node_002")
- title: the hierarchical question
- hierarchy_level: depth in tree (0 for root)
- parent_node_id: ID of parent node (null for root nodes)
- children_node_ids: list of child node IDs

The resulting structure should form a proper tree/DAG that accurately represents the domain decomposition while staying within {max_nodes} nodes."""


def get_user_prompt_template() -> str:
    """Get the user prompt template for the orchestrator agent"""
    return "Analyze the following content and generate a complete hierarchical node structure with parent-child relationships: {input}"
