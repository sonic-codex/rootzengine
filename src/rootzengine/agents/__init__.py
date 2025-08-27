"""
AI Bandmate Agents Module

This module contains the standardized channel mapping and agent profiles
for the RootzEngine AI bandmate system.
"""

from .channel_mapping import (
    ReggaeChannelMapping,
    AgentProfile,
    AgentRole,
    InteractionType,
    SpectrotoneProfile,
    PlayingCharacteristics,
    get_channel_mapping,
    map_audio_stem_to_channel,
    create_agent_midi_template,
    reggae_channel_mapping
)

__all__ = [
    "ReggaeChannelMapping",
    "AgentProfile", 
    "AgentRole",
    "InteractionType",
    "SpectrotoneProfile",
    "PlayingCharacteristics",
    "get_channel_mapping",
    "map_audio_stem_to_channel",
    "create_agent_midi_template",
    "reggae_channel_mapping"
]