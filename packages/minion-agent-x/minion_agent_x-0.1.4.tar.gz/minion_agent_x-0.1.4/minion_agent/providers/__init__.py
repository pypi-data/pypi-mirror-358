"""
Minion-Manus providers module.

This module contains provider adapters for integrating with external frameworks.
"""

from minion_agent.providers.adapters import BaseSmolaAgentsModelAdapter, MinionProviderToSmolAdapter

__all__ = [
    "BaseSmolaAgentsModelAdapter",
    "MinionProviderToSmolAdapter",
] 