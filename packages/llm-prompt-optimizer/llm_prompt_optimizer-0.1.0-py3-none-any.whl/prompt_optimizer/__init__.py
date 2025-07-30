"""
Prompt Optimizer - A comprehensive framework for systematic A/B testing, optimization, and performance analytics of LLM prompts.

Author: Sherin Joseph Roy
Email: sherin.joseph2217@gmail.com
GitHub: https://github.com/Sherin-SEF-AI/prompt-optimizer.git
LinkedIn: https://www.linkedin.com/in/sherin-roy-deepmost/

A production-ready Python package for systematic A/B testing, optimization, and performance analytics of LLM prompts across multiple providers (OpenAI, Anthropic, Google, HuggingFace, local models).
"""

__version__ = "0.1.0"
__author__ = "Sherin Joseph Roy"
__email__ = "sherin.joseph2217@gmail.com"
__url__ = "https://github.com/Sherin-SEF-AI/prompt-optimizer.git"
__license__ = "MIT"

# Core imports
from .core.optimizer import PromptOptimizer
from .core.experiment import ExperimentManager
from .core.prompt import PromptVersionControl
from .core.metrics import MetricsTracker

# Testing imports
from .testing.ab_test import ABTest

# Provider imports
from .providers.openai import OpenAIProvider
from .providers.anthropic import AnthropicProvider
from .providers.google import GoogleProvider
from .providers.huggingface import HuggingFaceProvider

# Analytics imports
from .analytics.quality_scorer import QualityScorer
from .analytics.cost_tracker import CostTracker
from .analytics.performance import PerformanceAnalyzer
from .analytics.reports import ReportGenerator

# Optimization imports
from .optimization.genetic import GeneticOptimizer

# Storage imports
from .storage.database import DatabaseManager

# API imports
from .api.server import create_app

# CLI imports
from .cli.main import main

# Visualization imports
from .visualization.dashboard import Dashboard

# Type definitions
from .types import (
    ProviderType,
    MetricType,
    TestStatus,
    OptimizerConfig,
    PromptVariant,
    ExperimentConfig,
    TestResult,
    QualityScore,
    SignificanceResult,
    AnalysisReport,
    OptimizationConfig,
    OptimizedPrompt,
    PromptVersion,
    PromptDiff,
    Experiment,
)

__all__ = [
    # Core
    "PromptOptimizer",
    "ExperimentManager",
    "PromptVersionControl",
    "MetricsTracker",
    
    # Testing
    "ABTest",
    
    # Providers
    "OpenAIProvider",
    "AnthropicProvider",
    "GoogleProvider",
    "HuggingFaceProvider",
    
    # Analytics
    "QualityScorer",
    "CostTracker",
    "PerformanceAnalyzer",
    "ReportGenerator",
    
    # Optimization
    "GeneticOptimizer",
    
    # Storage
    "DatabaseManager",
    
    # API
    "create_app",
    
    # CLI
    "main",
    
    # Visualization
    "Dashboard",
    
    # Types
    "ProviderType",
    "MetricType",
    "TestStatus",
    "OptimizerConfig",
    "PromptVariant",
    "ExperimentConfig",
    "TestResult",
    "QualityScore",
    "SignificanceResult",
    "AnalysisReport",
    "OptimizationConfig",
    "OptimizedPrompt",
    "PromptVersion",
    "PromptDiff",
    "Experiment",
] 