# This file makes the 'agents' module a package
# and can be used to expose specific agents or functionalities.

# Import agents from their new organized locations
from .hello_langgraph.agent import HelloAgent
from .git_langgraph.agent import GitAgent
from .supervisor_langgraph.agent import (
    SupervisorAgent,
    SupervisorAgentInput,
    SupervisorAgentOutput,
)

# Maintain backward compatibility with old names
HelloLangGraphAgent = HelloAgent
GitAgent = GitAgent

# Export all agent classes
__all__ = [
    "HelloAgent",
    "GitAgent",
    "HelloLangGraphAgent",  # backward compatibility
    "GitAgent",             # backward compatibility
    "SupervisorAgent",
    "SupervisorAgentInput",
    "SupervisorAgentOutput",
]
