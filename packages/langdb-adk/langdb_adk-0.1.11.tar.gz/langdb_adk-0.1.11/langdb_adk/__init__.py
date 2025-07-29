"""LangDB package for Google ADK integration."""

# Import feature flags
from .feature_flags import (
    get_available_features, 
    is_feature_available,
    FEATURE_ADK, 
    FEATURE_AGNO, 
    FEATURE_CREWAI, 
    FEATURE_LANGCHAIN, 
    FEATURE_OPENAI
)

# Initialize available imports and __all__ list
__all__ = [
    "get_available_features",
    "is_feature_available",
    "FEATURE_ADK",
    "FEATURE_AGNO",
    "FEATURE_CREWAI",
    "FEATURE_LANGCHAIN",
    "FEATURE_OPENAI"
]

# Conditionally import client libraries based on available features

# Core imports are always available

# ADK client
if is_feature_available(FEATURE_ADK):
    try:
        from .adk.agent import init_langdb_adk_agent
        from .adk.tracing import init_langdb_adk_tracing
        __all__.extend(["init_langdb_adk_agent", "init_langdb_adk_tracing"])
    except ImportError:
        pass

# Agno client
if is_feature_available(FEATURE_AGNO):
    try:
        from .agno.tracing import init_langdb_agno_tracing
        __all__.append("init_langdb_agno_tracing")
    except ImportError:
        pass

# CrewAI client
if is_feature_available(FEATURE_CREWAI):
    try:
        from .crewai.tracing import init_langdb_crewai_tracing
        __all__.append("init_langdb_crewai_tracing")
    except ImportError:
        pass

# Langchain client
if is_feature_available(FEATURE_LANGCHAIN):
    try:
        from .langchain.tracing import init_langdb_langchain_tracing
        __all__.append("init_langdb_langchain_tracing")
    except ImportError:
        pass

# OpenAI client
if is_feature_available(FEATURE_OPENAI):
    try:
        from .openai.tracing import init_langdb_openai_tracing
        __all__.append("init_langdb_openai_tracing")
    except ImportError:
        pass
