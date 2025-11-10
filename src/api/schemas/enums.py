from enum import Enum


class DiagramType(str, Enum):
    flowchart = "flowchart"
    sequence = "sequence"
    concept = "concept"
    erd = "erd"
    timeline = "timeline"


class LayoutStyle(str, Enum):
    compact = "compact"
    spacious = "spacious"
    orthogonal = "orthogonal"


class Complexity(str, Enum):
    simple = "simple"
    medium = "medium"
    complex = "complex"

