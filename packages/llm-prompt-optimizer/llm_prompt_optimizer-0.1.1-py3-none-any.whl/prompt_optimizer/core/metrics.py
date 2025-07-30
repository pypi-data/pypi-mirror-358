"""
Metrics tracking and aggregation for prompt optimization.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

from ..types import (
    TestResult,
    MetricType,
    QualityScore,
)


logger = logging.getLogger(__name__)


class MetricsTracker:
    """
    Tracks and aggregates performance metrics across experiments.
    
    Features:
    - Real-time metric aggregation
    - Statistical analysis of metrics
    - Cost tracking and optimization
    - Performance trend analysis
    - Custom metric definitions
    """
    
    def __init__(self):
        """Initialize the metrics tracker."""
        self.metrics: Dict[str, List[TestResult]] = defaultdict(list)
        self.aggregated_metrics: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.logger = logging.getLogger(__name__)
    
    def add_result(self, experiment_id: str, result: TestResult) -> None:
        """
        Add a test result to the metrics tracker.
        
        Args:
            experiment_id: ID of the experiment
            result: Test result to track
        """
        self.metrics[experiment_id].append(result)
        self._update_aggregated_metrics(experiment_id)
        
        self.logger.debug(f"Added result for experiment {experiment_id}")
    
    def _update_aggregated_metrics(self, experiment_id: str) -> None:
        """Update aggregated metrics for an experiment."""
        results = self.metrics[experiment_id]
        if not results:
            return
        
        # Group by variant
        variant_results = defaultdict(list)
        for result in results:
            variant_results[result.variant_name].append(result)
        
        aggregated = {}
        
        for variant_name, variant_results_list in variant_results.items():
            aggregated[variant_name] = self._calculate_variant_metrics(variant_results_list)
        
        self.aggregated_metrics[experiment_id] = aggregated
    
    def _calculate_variant_metrics(self, results: List[TestResult]) -> Dict[str, Any]:
        """Calculate metrics for a specific variant."""
        if not results:
            return {}
        
        # Quality scores
        quality_scores = [r.quality_score for r in results if r.quality_score is not None]
        avg_quality = statistics.mean(quality_scores) if quality_scores else 0.0
        
        # Latency
        latencies = [r.latency_ms for r in results]
        avg_latency = statistics.mean(latencies)
        p95_latency = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies)
        
        # Cost
        costs = [r.cost_usd for r in results]
        total_cost = sum(costs)
        avg_cost = statistics.mean(costs)
        
        # Token usage
        tokens = [r.tokens_used for r in results]
        total_tokens = sum(tokens)
        avg_tokens = statistics.mean(tokens)
        
        # Sample count
        sample_count = len(results)
        
        return {
            "sample_count": sample_count,
            "avg_quality": avg_quality,
            "avg_latency_ms": avg_latency,
            "p95_latency_ms": p95_latency,
            "total_cost_usd": total_cost,
            "avg_cost_usd": avg_cost,
            "total_tokens": total_tokens,
            "avg_tokens": avg_tokens,
            "cost_per_token": total_cost / total_tokens if total_tokens > 0 else 0.0,
            "quality_per_dollar": avg_quality / avg_cost if avg_cost > 0 else 0.0,
        }
    
    def get_experiment_metrics(self, experiment_id: str) -> Dict[str, Any]:
        """Get aggregated metrics for an experiment."""
        return self.aggregated_metrics.get(experiment_id, {})
    
    def get_variant_metrics(self, experiment_id: str, variant_name: str) -> Dict[str, Any]:
        """Get metrics for a specific variant."""
        experiment_metrics = self.get_experiment_metrics(experiment_id)
        return experiment_metrics.get(variant_name, {})
    
    def compare_variants(self, experiment_id: str, variant_a: str, variant_b: str) -> Dict[str, Any]:
        """
        Compare metrics between two variants.
        
        Args:
            experiment_id: ID of the experiment
            variant_a: First variant name
            variant_b: Second variant name
            
        Returns:
            Comparison metrics
        """
        metrics_a = self.get_variant_metrics(experiment_id, variant_a)
        metrics_b = self.get_variant_metrics(experiment_id, variant_b)
        
        if not metrics_a or not metrics_b:
            return {}
        
        comparison = {}
        
        # Calculate relative improvements
        for metric in ["avg_quality", "avg_latency_ms", "avg_cost_usd", "avg_tokens"]:
            if metric in metrics_a and metric in metrics_b:
                value_a = metrics_a[metric]
                value_b = metrics_b[metric]
                
                if value_a != 0:
                    relative_change = (value_b - value_a) / value_a
                    comparison[f"{metric}_improvement"] = relative_change
        
        # Absolute differences
        comparison["quality_difference"] = metrics_b.get("avg_quality", 0) - metrics_a.get("avg_quality", 0)
        comparison["latency_difference_ms"] = metrics_b.get("avg_latency_ms", 0) - metrics_a.get("avg_latency_ms", 0)
        comparison["cost_difference_usd"] = metrics_b.get("avg_cost_usd", 0) - metrics_a.get("avg_cost_usd", 0)
        
        return comparison
    
    def get_cost_analysis(self, experiment_id: str) -> Dict[str, Any]:
        """Get detailed cost analysis for an experiment."""
        experiment_metrics = self.get_experiment_metrics(experiment_id)
        if not experiment_metrics:
            return {}
        
        total_cost = sum(variant.get("total_cost_usd", 0) for variant in experiment_metrics.values())
        total_tokens = sum(variant.get("total_tokens", 0) for variant in experiment_metrics.values())
        
        # Cost breakdown by variant
        cost_breakdown = {}
        for variant_name, metrics in experiment_metrics.items():
            cost_breakdown[variant_name] = {
                "total_cost": metrics.get("total_cost_usd", 0),
                "cost_percentage": (metrics.get("total_cost_usd", 0) / total_cost * 100) if total_cost > 0 else 0,
                "cost_per_token": metrics.get("cost_per_token", 0),
                "quality_per_dollar": metrics.get("quality_per_dollar", 0),
            }
        
        return {
            "total_cost_usd": total_cost,
            "total_tokens": total_tokens,
            "avg_cost_per_token": total_cost / total_tokens if total_tokens > 0 else 0,
            "cost_breakdown": cost_breakdown,
        }
    
    def get_performance_trends(self, experiment_id: str, days: int = 7) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get performance trends over time.
        
        Args:
            experiment_id: ID of the experiment
            days: Number of days to analyze
            
        Returns:
            Performance trends by variant
        """
        results = self.metrics.get(experiment_id, [])
        if not results:
            return {}
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_results = [r for r in results if r.timestamp >= cutoff_date]
        
        # Group by variant and date
        trends = defaultdict(lambda: defaultdict(list))
        
        for result in recent_results:
            date_key = result.timestamp.date().isoformat()
            trends[result.variant_name][date_key].append(result)
        
        # Calculate daily metrics
        daily_trends = {}
        for variant_name, daily_results in trends.items():
            daily_metrics = []
            for date, day_results in sorted(daily_results.items()):
                if day_results:
                    metrics = self._calculate_variant_metrics(day_results)
                    metrics["date"] = date
                    daily_metrics.append(metrics)
            daily_trends[variant_name] = daily_metrics
        
        return daily_trends
    
    def get_efficiency_metrics(self, experiment_id: str) -> Dict[str, Any]:
        """Get efficiency metrics (quality per cost, tokens per dollar, etc.)."""
        experiment_metrics = self.get_experiment_metrics(experiment_id)
        if not experiment_metrics:
            return {}
        
        efficiency_metrics = {}
        
        for variant_name, metrics in experiment_metrics.items():
            efficiency_metrics[variant_name] = {
                "quality_per_dollar": metrics.get("quality_per_dollar", 0),
                "quality_per_token": metrics.get("avg_quality", 0) / metrics.get("avg_tokens", 1) if metrics.get("avg_tokens", 0) > 0 else 0,
                "tokens_per_second": metrics.get("avg_tokens", 0) / (metrics.get("avg_latency_ms", 1) / 1000) if metrics.get("avg_latency_ms", 0) > 0 else 0,
                "cost_efficiency_score": metrics.get("quality_per_dollar", 0) * 100,  # Normalized score
            }
        
        return efficiency_metrics
    
    def clear_experiment_metrics(self, experiment_id: str) -> None:
        """Clear all metrics for an experiment."""
        if experiment_id in self.metrics:
            del self.metrics[experiment_id]
        if experiment_id in self.aggregated_metrics:
            del self.aggregated_metrics[experiment_id]
        
        self.logger.info(f"Cleared metrics for experiment {experiment_id}")
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """Get summary statistics across all experiments."""
        total_experiments = len(self.metrics)
        total_results = sum(len(results) for results in self.metrics.values())
        
        all_costs = []
        all_qualities = []
        all_latencies = []
        
        for experiment_results in self.metrics.values():
            for result in experiment_results:
                all_costs.append(result.cost_usd)
                if result.quality_score:
                    all_qualities.append(result.quality_score)
                all_latencies.append(result.latency_ms)
        
        return {
            "total_experiments": total_experiments,
            "total_results": total_results,
            "avg_cost_per_test": statistics.mean(all_costs) if all_costs else 0,
            "avg_quality_score": statistics.mean(all_qualities) if all_qualities else 0,
            "avg_latency_ms": statistics.mean(all_latencies) if all_latencies else 0,
            "total_cost_usd": sum(all_costs),
        } 