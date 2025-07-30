"""
Cost tracking and analysis for prompt optimization.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from ..types import TestResult, ProviderType


logger = logging.getLogger(__name__)


class CostTracker:
    """
    Tracks and analyzes costs across experiments and providers.
    
    Features:
    - Real-time cost tracking
    - Cost comparison between providers
    - Budget management
    - Cost optimization recommendations
    - ROI calculations
    """
    
    def __init__(self):
        """Initialize the cost tracker."""
        self.costs: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.budgets: Dict[str, float] = {}
        self.logger = logging.getLogger(__name__)
        
        # Provider cost benchmarks
        self.provider_costs = {
            ProviderType.OPENAI: {
                "gpt-3.5-turbo": 0.002,
                "gpt-4": 0.03,
                "gpt-4-turbo": 0.01,
            },
            ProviderType.ANTHROPIC: {
                "claude-3-haiku": 0.00025,
                "claude-3-sonnet": 0.003,
                "claude-3-opus": 0.015,
            },
            ProviderType.GOOGLE: {
                "gemini-pro": 0.0005,
                "text-bison": 0.001,
            },
            ProviderType.HUGGINGFACE: {
                "default": 0.0,  # Free tier
            }
        }
    
    def add_cost(
        self,
        experiment_id: str,
        provider: ProviderType,
        model: str,
        tokens_used: int,
        cost_usd: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a cost entry.
        
        Args:
            experiment_id: ID of the experiment
            provider: Provider used
            model: Model used
            tokens_used: Number of tokens used
            cost_usd: Cost in USD
            metadata: Additional metadata
        """
        cost_entry = {
            "timestamp": datetime.utcnow(),
            "provider": provider,
            "model": model,
            "tokens_used": tokens_used,
            "cost_usd": cost_usd,
            "cost_per_token": cost_usd / tokens_used if tokens_used > 0 else 0,
            "metadata": metadata or {}
        }
        
        self.costs[experiment_id].append(cost_entry)
        self.logger.debug(f"Added cost entry for experiment {experiment_id}: ${cost_usd:.4f}")
    
    def get_experiment_costs(self, experiment_id: str) -> Dict[str, Any]:
        """
        Get cost summary for an experiment.
        
        Args:
            experiment_id: ID of the experiment
            
        Returns:
            Cost summary dictionary
        """
        if experiment_id not in self.costs:
            return {
                "total_cost": 0.0,
                "total_tokens": 0,
                "cost_per_token": 0.0,
                "provider_breakdown": {},
                "model_breakdown": {},
                "daily_costs": {},
            }
        
        cost_entries = self.costs[experiment_id]
        
        # Calculate totals
        total_cost = sum(entry["cost_usd"] for entry in cost_entries)
        total_tokens = sum(entry["tokens_used"] for entry in cost_entries)
        cost_per_token = total_cost / total_tokens if total_tokens > 0 else 0.0
        
        # Provider breakdown
        provider_breakdown = defaultdict(lambda: {"cost": 0.0, "tokens": 0, "count": 0})
        for entry in cost_entries:
            provider = entry["provider"].value
            provider_breakdown[provider]["cost"] += entry["cost_usd"]
            provider_breakdown[provider]["tokens"] += entry["tokens_used"]
            provider_breakdown[provider]["count"] += 1
        
        # Model breakdown
        model_breakdown = defaultdict(lambda: {"cost": 0.0, "tokens": 0, "count": 0})
        for entry in cost_entries:
            model = entry["model"]
            model_breakdown[model]["cost"] += entry["cost_usd"]
            model_breakdown[model]["tokens"] += entry["tokens_used"]
            model_breakdown[model]["count"] += 1
        
        # Daily costs
        daily_costs = defaultdict(float)
        for entry in cost_entries:
            date = entry["timestamp"].date().isoformat()
            daily_costs[date] += entry["cost_usd"]
        
        return {
            "total_cost": total_cost,
            "total_tokens": total_tokens,
            "cost_per_token": cost_per_token,
            "provider_breakdown": dict(provider_breakdown),
            "model_breakdown": dict(model_breakdown),
            "daily_costs": dict(daily_costs),
        }
    
    def compare_provider_costs(self, experiment_ids: List[str]) -> Dict[str, Any]:
        """
        Compare costs across different providers.
        
        Args:
            experiment_ids: List of experiment IDs to compare
            
        Returns:
            Provider comparison data
        """
        provider_stats = defaultdict(lambda: {
            "total_cost": 0.0,
            "total_tokens": 0,
            "experiment_count": 0,
            "avg_cost_per_token": 0.0
        })
        
        for experiment_id in experiment_ids:
            cost_summary = self.get_experiment_costs(experiment_id)
            
            for provider, stats in cost_summary["provider_breakdown"].items():
                provider_stats[provider]["total_cost"] += stats["cost"]
                provider_stats[provider]["total_tokens"] += stats["tokens"]
                provider_stats[provider]["experiment_count"] += 1
        
        # Calculate averages
        for provider, stats in provider_stats.items():
            if stats["total_tokens"] > 0:
                stats["avg_cost_per_token"] = stats["total_cost"] / stats["total_tokens"]
        
        return dict(provider_stats)
    
    def set_budget(self, experiment_id: str, budget_usd: float) -> None:
        """
        Set a budget for an experiment.
        
        Args:
            experiment_id: ID of the experiment
            budget_usd: Budget in USD
        """
        self.budgets[experiment_id] = budget_usd
        self.logger.info(f"Set budget for experiment {experiment_id}: ${budget_usd}")
    
    def check_budget_status(self, experiment_id: str) -> Dict[str, Any]:
        """
        Check budget status for an experiment.
        
        Args:
            experiment_id: ID of the experiment
            
        Returns:
            Budget status information
        """
        current_costs = self.get_experiment_costs(experiment_id)
        total_cost = current_costs["total_cost"]
        budget = self.budgets.get(experiment_id, float('inf'))
        
        return {
            "experiment_id": experiment_id,
            "total_cost": total_cost,
            "budget": budget,
            "remaining_budget": budget - total_cost,
            "budget_utilized": (total_cost / budget * 100) if budget > 0 else 0,
            "over_budget": total_cost > budget,
        }
    
    def get_cost_optimization_recommendations(
        self, 
        experiment_id: str
    ) -> List[str]:
        """
        Get cost optimization recommendations.
        
        Args:
            experiment_id: ID of the experiment
            
        Returns:
            List of recommendations
        """
        recommendations = []
        cost_summary = self.get_experiment_costs(experiment_id)
        
        if not cost_summary["total_cost"]:
            return ["No cost data available"]
        
        # Check for expensive models
        for model, stats in cost_summary["model_breakdown"].items():
            cost_per_token = stats["cost"] / stats["tokens"] if stats["tokens"] > 0 else 0
            if cost_per_token > 0.01:  # Expensive threshold
                recommendations.append(f"Consider using cheaper model instead of {model}")
        
        # Check for high token usage
        if cost_summary["total_tokens"] > 10000:
            recommendations.append("Consider optimizing prompts to reduce token usage")
        
        # Check for provider costs
        for provider, stats in cost_summary["provider_breakdown"].items():
            if provider == ProviderType.OPENAI.value and stats["cost"] > 5.0:
                recommendations.append("Consider using Anthropic or Google for cost savings")
        
        # Check budget utilization
        budget_status = self.check_budget_status(experiment_id)
        if budget_status["budget_utilized"] > 80:
            recommendations.append("Approaching budget limit - consider cost optimization")
        
        return recommendations
    
    def calculate_roi(
        self, 
        experiment_id: str, 
        quality_improvement: float,
        business_value_per_improvement: float
    ) -> Dict[str, Any]:
        """
        Calculate ROI for an experiment.
        
        Args:
            experiment_id: ID of the experiment
            quality_improvement: Quality improvement percentage
            business_value_per_improvement: Business value per 1% improvement
            
        Returns:
            ROI calculation results
        """
        cost_summary = self.get_experiment_costs(experiment_id)
        total_cost = cost_summary["total_cost"]
        
        if total_cost == 0:
            return {
                "roi": float('inf'),
                "total_cost": 0.0,
                "business_value": 0.0,
                "net_benefit": 0.0,
                "payback_period": 0.0
            }
        
        # Calculate business value
        business_value = quality_improvement * business_value_per_improvement
        
        # Calculate ROI
        net_benefit = business_value - total_cost
        roi = (net_benefit / total_cost * 100) if total_cost > 0 else 0
        
        # Calculate payback period (assuming daily value)
        daily_value = business_value / 365  # Assuming annual value
        payback_period = total_cost / daily_value if daily_value > 0 else float('inf')
        
        return {
            "roi": roi,
            "total_cost": total_cost,
            "business_value": business_value,
            "net_benefit": net_benefit,
            "payback_period": payback_period,
            "quality_improvement": quality_improvement
        }
    
    def get_cost_trends(self, experiment_id: str, days: int = 7) -> Dict[str, Any]:
        """
        Get cost trends over time.
        
        Args:
            experiment_id: ID of the experiment
            days: Number of days to analyze
            
        Returns:
            Cost trend data
        """
        if experiment_id not in self.costs:
            return {"daily_costs": {}, "trend": "no_data"}
        
        cost_entries = self.costs[experiment_id]
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Filter recent entries
        recent_entries = [
            entry for entry in cost_entries 
            if entry["timestamp"] >= cutoff_date
        ]
        
        # Group by date
        daily_costs = defaultdict(float)
        for entry in recent_entries:
            date = entry["timestamp"].date().isoformat()
            daily_costs[date] += entry["cost_usd"]
        
        # Calculate trend
        if len(daily_costs) >= 2:
            dates = sorted(daily_costs.keys())
            first_cost = daily_costs[dates[0]]
            last_cost = daily_costs[dates[-1]]
            
            if first_cost == 0:
                trend = "increasing" if last_cost > 0 else "stable"
            else:
                change = (last_cost - first_cost) / first_cost
                if change > 0.1:
                    trend = "increasing"
                elif change < -0.1:
                    trend = "decreasing"
                else:
                    trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "daily_costs": dict(daily_costs),
            "trend": trend,
            "total_period_cost": sum(daily_costs.values())
        } 