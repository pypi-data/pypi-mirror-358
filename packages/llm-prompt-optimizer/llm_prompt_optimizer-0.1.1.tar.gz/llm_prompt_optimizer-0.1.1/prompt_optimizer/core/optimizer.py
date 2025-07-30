"""
Main PromptOptimizer class that orchestrates A/B testing, optimization, and analytics.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from ..types import (
    OptimizerConfig,
    Experiment,
    ExperimentConfig,
    PromptVariant,
    TestResult,
    AnalysisReport,
    OptimizationConfig,
    OptimizedPrompt,
    ProviderType,
    TestStatus,
)
from .experiment import ExperimentManager
from .prompt import PromptVersionControl
from .metrics import MetricsTracker
from ..testing.ab_test import ABTest
from ..analytics.quality_scorer import QualityScorer
from ..optimization.genetic import GeneticOptimizer
from ..storage.database import DatabaseManager
from ..providers.base import BaseProvider
from ..providers.openai import OpenAIProvider
from ..providers.anthropic import AnthropicProvider


logger = logging.getLogger(__name__)


class PromptOptimizer:
    """
    Main class for prompt optimization and A/B testing.
    
    This class provides a unified interface for:
    - Creating and managing A/B test experiments
    - Running tests across multiple LLM providers
    - Analyzing results with statistical rigor
    - Optimizing prompts using genetic algorithms
    - Tracking performance metrics and costs
    """
    
    def __init__(self, config: OptimizerConfig):
        """Initialize the PromptOptimizer with configuration."""
        self.config = config
        self.experiment_manager = ExperimentManager()
        self.version_control = PromptVersionControl()
        self.metrics_tracker = MetricsTracker()
        self.quality_scorer = QualityScorer()
        self.genetic_optimizer = GeneticOptimizer()
        self.database = DatabaseManager(config.database_url)
        
        # Initialize providers
        self.providers: Dict[ProviderType, BaseProvider] = {}
        self._initialize_providers()
        
        # Active experiments
        self.active_experiments: Dict[str, ABTest] = {}
        
        logger.info(f"PromptOptimizer initialized with config: {config}")
    
    def _initialize_providers(self) -> None:
        """Initialize LLM providers based on configuration."""
        api_keys = self.config.api_keys
        
        if ProviderType.OPENAI in api_keys:
            self.providers[ProviderType.OPENAI] = OpenAIProvider(
                api_key=api_keys[ProviderType.OPENAI]
            )
        
        if ProviderType.ANTHROPIC in api_keys:
            self.providers[ProviderType.ANTHROPIC] = AnthropicProvider(
                api_key=api_keys[ProviderType.ANTHROPIC]
            )
        
        # Add more providers as needed
        logger.info(f"Initialized {len(self.providers)} providers")
    
    async def create_experiment(
        self, 
        name: str, 
        variants: List[PromptVariant], 
        config: ExperimentConfig
    ) -> Experiment:
        """
        Create a new A/B test experiment.
        
        Args:
            name: Name of the experiment
            variants: List of prompt variants to test
            config: Experiment configuration
            
        Returns:
            Created experiment object
        """
        experiment_id = str(uuid.uuid4())
        
        experiment = Experiment(
            id=experiment_id,
            name=name,
            variants=variants,
            config=config,
            status=TestStatus.DRAFT
        )
        
        # Store experiment
        self.database.save_experiment(experiment)
        
        # Create A/B test instance
        ab_test = ABTest(
            experiment=experiment,
            providers=self.providers,
            quality_scorer=self.quality_scorer,
            metrics_tracker=self.metrics_tracker
        )
        
        self.active_experiments[experiment_id] = ab_test
        
        logger.info(f"Created experiment '{name}' with ID {experiment_id}")
        return experiment
    
    async def start_experiment(self, experiment_id: str) -> None:
        """Start an experiment and begin collecting data."""
        if experiment_id not in self.active_experiments:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        ab_test = self.active_experiments[experiment_id]
        await ab_test.start()
        
        # Update experiment status
        experiment = ab_test.experiment
        experiment.status = TestStatus.RUNNING
        experiment.started_at = datetime.utcnow()
        self.database.update_experiment(experiment)
        
        logger.info(f"Started experiment {experiment_id}")
    
    async def run_test(
        self, 
        experiment_id: str, 
        input_data: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> TestResult:
        """
        Run a single test for an experiment.
        
        Args:
            experiment_id: ID of the experiment
            input_data: Input data for the prompt
            user_id: Optional user ID for consistent assignment
            
        Returns:
            Test result with response and metrics
        """
        if experiment_id not in self.active_experiments:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        ab_test = self.active_experiments[experiment_id]
        result = await ab_test.run_test(input_data, user_id)
        
        # Store result
        self.database.save_test_result(result)
        
        return result
    
    async def test_prompt(
        self, 
        experiment_id: str, 
        user_id: str, 
        input_data: Dict[str, Any]
    ) -> TestResult:
        """
        Test a prompt for a specific experiment and user.
        
        Args:
            experiment_id: ID of the experiment
            user_id: User ID for consistent assignment
            input_data: Input data for the prompt
            
        Returns:
            Test result with response and metrics
        """
        return await self.run_test(experiment_id, input_data, user_id)
    
    async def analyze_experiment(self, experiment_id: str) -> AnalysisReport:
        """
        Analyze an experiment and return the analysis report.
        
        Args:
            experiment_id: ID of the experiment to analyze
            
        Returns:
            Analysis report with statistical significance
        """
        return await self.analyze_results(experiment_id)
    
    async def analyze_results(self, experiment_id: str) -> AnalysisReport:
        """
        Analyze results of an experiment with statistical significance.
        
        Args:
            experiment_id: ID of the experiment to analyze
            
        Returns:
            Complete analysis report
        """
        if experiment_id not in self.active_experiments:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        ab_test = self.active_experiments[experiment_id]
        analysis = await ab_test.analyze_results()
        
        # Store analysis
        self.database.save_analysis_report(analysis.dict())
        
        return analysis
    
    async def get_best_variant(self, experiment_id: str) -> Optional[PromptVariant]:
        """
        Get the best performing variant from an experiment.
        
        Args:
            experiment_id: ID of the experiment
            
        Returns:
            Best performing variant or None
        """
        if experiment_id not in self.active_experiments:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        ab_test = self.active_experiments[experiment_id]
        return await ab_test.get_best_variant()
    
    async def optimize_prompt(
        self, 
        base_prompt: str, 
        optimization_config: OptimizationConfig
    ) -> OptimizedPrompt:
        """
        Optimize a prompt using genetic algorithms.
        
        Args:
            base_prompt: Original prompt to optimize
            optimization_config: Optimization configuration
            
        Returns:
            Optimized prompt with improvement metrics
        """
        # Use the genetic optimizer to improve the prompt
        optimized_prompt = await self.genetic_optimizer.optimize(
            base_prompt=base_prompt,
            config=optimization_config,
            providers=self.providers,
            quality_scorer=self.quality_scorer
        )
        
        # Store optimization result
        self.database.save_optimized_prompt(optimized_prompt.dict())
        
        return optimized_prompt
    
    async def stop_experiment(self, experiment_id: str) -> None:
        """Stop an experiment and finalize results."""
        if experiment_id not in self.active_experiments:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        ab_test = self.active_experiments[experiment_id]
        await ab_test.stop()
        
        # Update experiment status
        experiment = ab_test.experiment
        experiment.status = TestStatus.COMPLETED
        experiment.completed_at = datetime.utcnow()
        self.database.update_experiment(experiment)
        
        # Remove from active experiments
        del self.active_experiments[experiment_id]
        
        logger.info(f"Stopped experiment {experiment_id}")
    
    async def get_experiment_status(self, experiment_id: str) -> TestStatus:
        """Get the current status of an experiment."""
        if experiment_id not in self.active_experiments:
            return TestStatus.UNKNOWN
        
        return self.active_experiments[experiment_id].experiment.status
    
    async def list_experiments(self) -> List[Experiment]:
        """List all experiments."""
        return list(self.active_experiments.values())
    
    async def get_experiment_results(self, experiment_id: str) -> List[TestResult]:
        """Get all results for an experiment."""
        if experiment_id not in self.active_experiments:
            return []
        
        return self.active_experiments[experiment_id].get_results()
    
    async def export_results(
        self, 
        experiment_id: str, 
        format: str = "csv"
    ) -> str:
        """
        Export experiment results to a file.
        
        Args:
            experiment_id: ID of the experiment
            format: Export format (csv, json, excel)
            
        Returns:
            Path to exported file
        """
        results = await self.get_experiment_results(experiment_id)
        return await self.database.export_results(results, format)
    
    async def cleanup(self) -> None:
        """Clean up resources and close connections."""
        # Stop all active experiments
        for experiment_id in list(self.active_experiments.keys()):
            await self.stop_experiment(experiment_id)
        
        # Close database connections
        await self.database.close()
        
        logger.info("PromptOptimizer cleanup completed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        asyncio.create_task(self.cleanup()) 