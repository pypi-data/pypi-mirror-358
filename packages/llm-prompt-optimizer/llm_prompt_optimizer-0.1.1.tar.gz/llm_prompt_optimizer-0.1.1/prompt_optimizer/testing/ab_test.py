"""
A/B testing engine for prompt optimization.
"""

import asyncio
import logging
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from ..types import (
    Experiment,
    TestResult,
    AnalysisReport,
    SignificanceResult,
    TestStatus,
    ProviderType,
    PromptVariant,
)
from .statistical import StatisticalAnalyzer
from .randomization import TrafficSplitter
from .significance import SignificanceTester
from ..analytics.quality_scorer import QualityScorer
from ..core.metrics import MetricsTracker
from ..providers.base import BaseProvider


logger = logging.getLogger(__name__)


class ABTest:
    """
    A/B testing engine for prompt variants.
    
    Features:
    - Multi-variant testing (A/B/C/D/etc.)
    - Statistical significance calculation
    - Real-time monitoring and early stopping
    - Consistent user assignment
    - Performance tracking
    """
    
    def __init__(
        self,
        experiment: Experiment,
        providers: Dict[ProviderType, BaseProvider],
        quality_scorer: QualityScorer,
        metrics_tracker: MetricsTracker
    ):
        """Initialize the A/B test."""
        self.experiment = experiment
        self.providers = providers
        self.quality_scorer = quality_scorer
        self.metrics_tracker = metrics_tracker
        
        # Initialize components
        self.statistical_analyzer = StatisticalAnalyzer()
        self.traffic_splitter = TrafficSplitter(experiment.config.traffic_split)
        self.significance_tester = SignificanceTester()
        
        # Test state
        self.is_running = False
        self.results: List[TestResult] = []
        self.user_assignments: Dict[str, str] = {}  # user_id -> variant_name
        
        self.logger = logging.getLogger(__name__)
    
    async def start(self) -> None:
        """Start the A/B test."""
        self.is_running = True
        self.experiment.status = TestStatus.RUNNING
        self.experiment.started_at = datetime.utcnow()
        
        self.logger.info(f"Started A/B test for experiment {self.experiment.id}")
    
    async def stop(self) -> None:
        """Stop the A/B test."""
        self.is_running = False
        self.experiment.status = TestStatus.STOPPED
        self.experiment.completed_at = datetime.utcnow()
        
        self.logger.info(f"Stopped A/B test for experiment {self.experiment.id}")
    
    async def run_test(
        self, 
        input_data: Dict[str, Any], 
        user_id: Optional[str] = None
    ) -> TestResult:
        """
        Run a single test with the assigned variant.
        
        Args:
            input_data: Input data for the prompt
            user_id: Optional user ID for consistent assignment
            
        Returns:
            Test result with response and metrics
        """
        if not self.is_running:
            raise RuntimeError("A/B test is not running")
        
        # Generate user ID if not provided
        if user_id is None:
            user_id = str(uuid.uuid4())
        
        # Assign variant (consistent for same user)
        variant_name = self._assign_variant(user_id)
        variant = self._get_variant_by_name(variant_name)
        
        # Get provider
        provider = self.providers.get(self.experiment.config.provider)
        if not provider:
            raise ValueError(f"Provider {self.experiment.config.provider} not available")
        
        # Format prompt with input data
        formatted_prompt = self._format_prompt(variant.template, input_data)
        
        # Run inference
        start_time = datetime.utcnow()
        response = await provider.generate(
            prompt=formatted_prompt,
            model=self.experiment.config.model
        )
        end_time = datetime.utcnow()
        
        # Calculate metrics
        latency_ms = (end_time - start_time).total_seconds() * 1000
        cost_usd = self._calculate_cost(response, provider)
        tokens_used = response.get("tokens_used", 0)
        
        # Score response quality
        quality_score = await self.quality_scorer.score_response(
            prompt=formatted_prompt,
            response=response.get("text", ""),
            expected_output=input_data.get("expected_output")
        )
        
        # Create test result
        result = TestResult(
            experiment_id=self.experiment.id,
            variant_name=variant_name,
            user_id=user_id,
            input_data=input_data,
            response=response.get("text", ""),
            quality_score=quality_score.overall_score if quality_score else None,
            latency_ms=latency_ms,
            cost_usd=cost_usd,
            tokens_used=tokens_used,
            metadata={
                "provider": self.experiment.config.provider,
                "model": self.experiment.config.model,
                "prompt_template": variant.template,
            }
        )
        
        # Store result
        self.results.append(result)
        self.metrics_tracker.add_result(self.experiment.id, result)
        
        # Check for early stopping
        if self.experiment.config.early_stopping:
            await self._check_early_stopping()
        
        self.logger.debug(f"Test completed for user {user_id} with variant {variant_name}")
        return result
    
    def _assign_variant(self, user_id: str) -> str:
        """Assign a variant to a user (consistent assignment)."""
        if user_id in self.user_assignments:
            return self.user_assignments[user_id]
        
        # Use hash-based assignment for consistency
        variant_name = self.traffic_splitter.assign_variant(user_id)
        self.user_assignments[user_id] = variant_name
        
        return variant_name
    
    def _get_variant_by_name(self, variant_name: str) -> PromptVariant:
        """Get a variant by name."""
        for variant in self.experiment.variants:
            if variant.name == variant_name:
                return variant
        raise ValueError(f"Variant {variant_name} not found")
    
    def _format_prompt(self, template: str, input_data: Dict[str, Any]) -> str:
        """Format prompt template with input data."""
        try:
            return template.format(**input_data)
        except KeyError as e:
            raise ValueError(f"Missing required input field: {e}")
    
    def _calculate_cost(self, response: Dict[str, Any], provider: BaseProvider) -> float:
        """Calculate cost for the response."""
        tokens_used = response.get("tokens_used", 0)
        return provider.calculate_cost(tokens_used, self.experiment.config.model)
    
    async def _check_early_stopping(self) -> None:
        """Check if the test should stop early based on significance."""
        if len(self.results) < 50:  # Need minimum samples
            return
        
        analysis = await self.analyze_results()
        
        # Check if any variant is significantly better
        for significance_result in analysis.significance_results:
            if significance_result.is_significant and significance_result.p_value < 0.01:
                self.logger.info(f"Early stopping triggered: {significance_result.variant_a} vs {significance_result.variant_b}")
                await self.stop()
                break
    
    async def analyze_results(self) -> AnalysisReport:
        """
        Analyze test results with statistical significance.
        
        Returns:
            Complete analysis report
        """
        if not self.results:
            return AnalysisReport(
                experiment_id=self.experiment.id,
                status=self.experiment.status,
                total_samples=0,
                duration_days=0,
                confidence_level=0.0
            )
        
        # Group results by variant
        variant_results = {}
        for result in self.results:
            if result.variant_name not in variant_results:
                variant_results[result.variant_name] = []
            variant_results[result.variant_name].append(result)
        
        # Calculate significance between all pairs
        significance_results = []
        variant_names = list(variant_results.keys())
        
        for i in range(len(variant_names)):
            for j in range(i + 1, len(variant_names)):
                variant_a = variant_names[i]
                variant_b = variant_names[j]
                
                results_a = variant_results[variant_a]
                results_b = variant_results[variant_b]
                
                if len(results_a) < 10 or len(results_b) < 10:  # Need minimum samples
                    continue
                
                # Extract quality scores
                scores_a = [r.quality_score for r in results_a if r.quality_score is not None]
                scores_b = [r.quality_score for r in results_b if r.quality_score is not None]
                
                if not scores_a or not scores_b:
                    continue
                
                # Run significance test
                significance = self.significance_tester.test_significance(
                    scores_a, scores_b, self.experiment.config.significance_level
                )
                
                significance_results.append(significance)
        
        # Determine best variant
        best_variant = None
        if significance_results:
            # Find variant with most significant wins
            variant_wins: Dict[str, int] = {}
            for result in significance_results:
                if result.is_significant:
                    if result.p_value < 0.05:  # Significant improvement
                        variant_wins[result.variant_b] = variant_wins.get(result.variant_b, 0) + 1
            
            if variant_wins:
                best_variant = max(variant_wins.items(), key=lambda x: x[1])[0]
        
        # Calculate duration
        duration_days = 0
        if self.experiment.started_at:
            duration = datetime.utcnow() - self.experiment.started_at
            duration_days = duration.total_seconds() / (24 * 3600)
        
        # Calculate confidence level
        confidence_level = self._calculate_confidence_level()
        
        return AnalysisReport(
            experiment_id=self.experiment.id,
            status=self.experiment.status,
            best_variant=best_variant,
            confidence_level=confidence_level,
            total_samples=len(self.results),
            duration_days=duration_days,
            significance_results=significance_results,
            metrics_summary=self.metrics_tracker.get_experiment_metrics(self.experiment.id),
            recommendations=self._generate_recommendations()
        )
    
    def _calculate_confidence_level(self) -> float:
        """Calculate overall confidence level for the test."""
        if len(self.results) < 100:
            return 0.5  # Low confidence with few samples
        
        # Calculate based on sample size and significance results
        base_confidence = min(len(self.results) / 1000, 0.95)  # Cap at 95%
        
        # Adjust based on significance results
        significant_results = [r for r in self.results if r.quality_score is not None]
        if significant_results:
            quality_scores: List[float] = [r.quality_score for r in significant_results]  # type: ignore
            avg_quality = sum(quality_scores) / len(significant_results)
            quality_boost = avg_quality * 0.1  # Quality contributes to confidence
            base_confidence += quality_boost
        
        return min(base_confidence, 1.0)
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []
        
        if len(self.results) < 100:
            recommendations.append("Continue testing to reach minimum sample size")
        
        # Check for cost optimization opportunities
        cost_analysis = self.metrics_tracker.get_cost_analysis(self.experiment.id)
        if cost_analysis:
            total_cost = cost_analysis.get("total_cost_usd", 0)
            if total_cost > 10.0:  # High cost threshold
                recommendations.append("Consider cost optimization strategies")
        
        # Check for quality issues
        avg_quality = 0
        quality_results = [r for r in self.results if r.quality_score is not None]
        if quality_results:
            quality_scores: List[float] = [r.quality_score for r in quality_results]  # type: ignore
            avg_quality = sum(quality_scores) / len(quality_results)
            if avg_quality < 0.7:
                recommendations.append("Overall quality is low - consider prompt improvements")
        
        return recommendations
    
    def get_test_status(self) -> Dict[str, Any]:
        """Get current test status and statistics."""
        return {
            "experiment_id": self.experiment.id,
            "status": self.experiment.status,
            "is_running": self.is_running,
            "total_results": len(self.results),
            "user_assignments": len(self.user_assignments),
            "variants": [v.name for v in self.experiment.variants],
            "started_at": self.experiment.started_at,
            "metrics": self.metrics_tracker.get_experiment_metrics(self.experiment.id)
        } 