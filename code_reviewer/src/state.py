"""Contains states used by agents throughout codebase."""

from typing import Dict, List, Optional, TypedDict


class AgentReport(TypedDict):
    """Report from a single specialized agent."""

    agent_name: str
    analysis: str


class PartitionReport(TypedDict):
    """Synthesized report for a single partition/module."""

    partition_id: str
    files: List[str]
    synthesized_analysis: str
    agent_reports: List[AgentReport]


class CodebaseState(TypedDict):
    """The central state for our agentic system."""

    project_path: str
    # Master Coordinator populates this
    partitions: Optional[
        Dict[str, List[str]]
    ]  # e.g., {"module1": ["/path/to/file1.py"]}

    # Sub-Coordinators populate this
    partition_reports: List[PartitionReport]

    # Master Coordinator populates this at the end
    final_report: Optional[str]

    # A scratchpad for inter-node communication
    current_partition_id: Optional[str]
