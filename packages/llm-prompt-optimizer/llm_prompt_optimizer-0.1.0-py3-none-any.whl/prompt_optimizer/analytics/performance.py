"""
Performance analytics for prompt optimization.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import statistics

from ..types import TestResult


logger = logging.getLogger(__name__)


class PerformanceAnalyzer:
    """
    Analyzes performance metrics for prompt optimization.
    
    Features:
    - Latency analysis
    - Throughput tracking
    - Performance benchmarking
    - Bottleneck identification
    - Performance optimization recommendations
    """
    
    def __init__(self):
        """Initialize the performance analyzer."""
        self.logger = logging.getLogger(__name__)
        
        # Performance thresholds
        self.latency_threshold_ms = 2000  # 2 seconds
        self.throughput_threshold_rps = 10  # 10 requests per second
        
    def analyze_latency(
        self, 
        results: List[TestResult],
        group_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze latency performance.
        
        Args:
            results: List of test results
            group_by: Group by field (e.g., 'variant_name', 'provider')
            
        Returns:
            Latency analysis results
        """
        if not results:
            return {
                "avg_latency": 0.0,
                "p50_latency": 0.0,
                "p95_latency": 0.0,
                "p99_latency": 0.0,
                "min_latency": 0.0,
                "max_latency": 0.0,
                "latency_distribution": {},
                "performance_issues": []
            }
        
        latencies = [r.latency_ms for r in results]
        
        # Basic statistics
        avg_latency = statistics.mean(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        
        # Percentiles
        sorted_latencies = sorted(latencies)
        p50_latency = statistics.median(sorted_latencies)
        p95_latency = sorted_latencies[int(len(sorted_latencies) * 0.95)]
        p99_latency = sorted_latencies[int(len(sorted_latencies) * 0.99)]
        
        # Group analysis
        latency_distribution = {}
        if group_by:
            groups = {}
            for result in results:
                group_value = getattr(result, group_by, "unknown")
                if group_value not in groups:
                    groups[group_value] = []
                groups[group_value].append(result.latency_ms)
            
            for group, group_latencies in groups.items():
                latency_distribution[group] = {
                    "avg": statistics.mean(group_latencies),
                    "p95": sorted(group_latencies)[int(len(group_latencies) * 0.95)],
                    "count": len(group_latencies)
                }
        
        # Performance issues
        performance_issues = []
        if avg_latency > self.latency_threshold_ms:
            performance_issues.append(f"Average latency ({avg_latency:.1f}ms) exceeds threshold ({self.latency_threshold_ms}ms)")
        
        if p95_latency > self.latency_threshold_ms * 2:
            performance_issues.append(f"95th percentile latency ({p95_latency:.1f}ms) is very high")
        
        return {
            "avg_latency": avg_latency,
            "p50_latency": p50_latency,
            "p95_latency": p95_latency,
            "p99_latency": p99_latency,
            "min_latency": min_latency,
            "max_latency": max_latency,
            "latency_distribution": latency_distribution,
            "performance_issues": performance_issues
        }
    
    def analyze_throughput(
        self, 
        results: List[TestResult],
        time_window_minutes: int = 60
    ) -> Dict[str, Any]:
        """
        Analyze throughput performance.
        
        Args:
            results: List of test results
            time_window_minutes: Time window for throughput calculation
            
        Returns:
            Throughput analysis results
        """
        if not results:
            return {
                "requests_per_second": 0.0,
                "requests_per_minute": 0.0,
                "total_requests": 0,
                "time_span_minutes": 0,
                "throughput_trend": "no_data"
            }
        
        # Sort by timestamp (use current time if timestamp not available)
        current_time = datetime.utcnow()
        
        def get_timestamp(result):
            return getattr(result, 'timestamp', current_time)
        
        sorted_results = sorted(results, key=get_timestamp)
        
        # Calculate time span
        start_time = get_timestamp(sorted_results[0])
        end_time = get_timestamp(sorted_results[-1])
        time_span = (end_time - start_time).total_seconds() / 60  # minutes
        
        total_requests = len(results)
        requests_per_minute = total_requests / time_span if time_span > 0 else 0
        requests_per_second = requests_per_minute / 60
        
        # Analyze throughput trend
        throughput_trend = self._analyze_throughput_trend(sorted_results, time_window_minutes)
        
        return {
            "requests_per_second": requests_per_second,
            "requests_per_minute": requests_per_minute,
            "total_requests": total_requests,
            "time_span_minutes": time_span,
            "throughput_trend": throughput_trend
        }
    
    def analyze_token_efficiency(
        self, 
        results: List[TestResult]
    ) -> Dict[str, Any]:
        """
        Analyze token usage efficiency.
        
        Args:
            results: List of test results
            
        Returns:
            Token efficiency analysis
        """
        if not results:
            return {
                "avg_tokens_per_request": 0,
                "tokens_per_quality_point": 0.0,
                "efficiency_score": 0.0,
                "optimization_opportunities": []
            }
        
        # Calculate token statistics
        total_tokens = sum(r.tokens_used for r in results)
        avg_tokens_per_request = total_tokens / len(results)
        
        # Calculate quality-weighted token efficiency
        quality_results = [r for r in results if r.quality_score is not None]
        if quality_results:
            total_quality = sum(r.quality_score for r in quality_results if r.quality_score is not None)
            tokens_per_quality_point = total_tokens / total_quality if total_quality > 0 else 0
        else:
            tokens_per_quality_point = 0
        
        # Calculate efficiency score (lower tokens = higher efficiency)
        max_reasonable_tokens = 1000  # Threshold for "reasonable" token usage
        efficiency_score = max(0, 1 - (avg_tokens_per_request / max_reasonable_tokens))
        
        # Identify optimization opportunities
        optimization_opportunities = []
        if avg_tokens_per_request > 500:
            optimization_opportunities.append("Consider shorter prompts to reduce token usage")
        
        if tokens_per_quality_point > 1000:
            optimization_opportunities.append("Token usage is high relative to quality - consider optimization")
        
        return {
            "avg_tokens_per_request": avg_tokens_per_request,
            "tokens_per_quality_point": tokens_per_quality_point,
            "efficiency_score": efficiency_score,
            "optimization_opportunities": optimization_opportunities
        }
    
    def benchmark_performance(
        self, 
        results: List[TestResult],
        baseline_results: Optional[List[TestResult]] = None
    ) -> Dict[str, Any]:
        """
        Benchmark performance against baseline.
        
        Args:
            results: Current test results
            baseline_results: Baseline results for comparison
            
        Returns:
            Benchmark analysis results
        """
        if not results:
            return {
                "current_performance": {},
                "baseline_performance": {},
                "improvements": {},
                "regressions": {}
            }
        
        # Analyze current performance
        current_latency = self.analyze_latency(results)
        current_throughput = self.analyze_throughput(results)
        current_efficiency = self.analyze_token_efficiency(results)
        
        current_performance = {
            "latency": current_latency,
            "throughput": current_throughput,
            "efficiency": current_efficiency
        }
        
        if not baseline_results:
            return {
                "current_performance": current_performance,
                "baseline_performance": {},
                "improvements": {},
                "regressions": {}
            }
        
        # Analyze baseline performance
        baseline_latency = self.analyze_latency(baseline_results)
        baseline_throughput = self.analyze_throughput(baseline_results)
        baseline_efficiency = self.analyze_token_efficiency(baseline_results)
        
        baseline_performance = {
            "latency": baseline_latency,
            "throughput": baseline_throughput,
            "efficiency": baseline_efficiency
        }
        
        # Calculate improvements and regressions
        improvements = []
        regressions = []
        
        # Latency comparison
        if current_latency["avg_latency"] < baseline_latency["avg_latency"]:
            improvement = (baseline_latency["avg_latency"] - current_latency["avg_latency"]) / baseline_latency["avg_latency"] * 100
            improvements.append(f"Latency improved by {improvement:.1f}%")
        else:
            regression = (current_latency["avg_latency"] - baseline_latency["avg_latency"]) / baseline_latency["avg_latency"] * 100
            regressions.append(f"Latency regressed by {regression:.1f}%")
        
        # Throughput comparison
        if current_throughput["requests_per_second"] > baseline_throughput["requests_per_second"]:
            improvement = (current_throughput["requests_per_second"] - baseline_throughput["requests_per_second"]) / baseline_throughput["requests_per_second"] * 100
            improvements.append(f"Throughput improved by {improvement:.1f}%")
        else:
            regression = (baseline_throughput["requests_per_second"] - current_throughput["requests_per_second"]) / baseline_throughput["requests_per_second"] * 100
            regressions.append(f"Throughput regressed by {regression:.1f}%")
        
        # Efficiency comparison
        if current_efficiency["efficiency_score"] > baseline_efficiency["efficiency_score"]:
            improvement = (current_efficiency["efficiency_score"] - baseline_efficiency["efficiency_score"]) / baseline_efficiency["efficiency_score"] * 100
            improvements.append(f"Efficiency improved by {improvement:.1f}%")
        else:
            regression = (baseline_efficiency["efficiency_score"] - current_efficiency["efficiency_score"]) / baseline_efficiency["efficiency_score"] * 100
            regressions.append(f"Efficiency regressed by {regression:.1f}%")
        
        return {
            "current_performance": current_performance,
            "baseline_performance": baseline_performance,
            "improvements": improvements,
            "regressions": regressions
        }
    
    def identify_bottlenecks(self, results: List[TestResult]) -> List[str]:
        """
        Identify performance bottlenecks.
        
        Args:
            results: List of test results
            
        Returns:
            List of identified bottlenecks
        """
        bottlenecks = []
        
        if not results:
            return ["No data available for bottleneck analysis"]
        
        # Analyze latency
        latency_analysis = self.analyze_latency(results)
        if latency_analysis["performance_issues"]:
            bottlenecks.extend(latency_analysis["performance_issues"])
        
        # Analyze throughput
        throughput_analysis = self.analyze_throughput(results)
        if throughput_analysis["requests_per_second"] < self.throughput_threshold_rps:
            bottlenecks.append(f"Low throughput: {throughput_analysis['requests_per_second']:.1f} RPS")
        
        # Analyze token efficiency
        efficiency_analysis = self.analyze_token_efficiency(results)
        if efficiency_analysis["efficiency_score"] < 0.5:
            bottlenecks.append("Low token efficiency - consider prompt optimization")
        
        # Check for provider-specific issues
        provider_latencies = {}
        for result in results:
            provider = result.metadata.get("provider", "unknown")
            if provider not in provider_latencies:
                provider_latencies[provider] = []
            provider_latencies[provider].append(result.latency_ms)
        
        for provider, latencies in provider_latencies.items():
            avg_latency = statistics.mean(latencies)
            if avg_latency > self.latency_threshold_ms:
                bottlenecks.append(f"High latency for {provider}: {avg_latency:.1f}ms")
        
        return bottlenecks
    
    def _analyze_throughput_trend(
        self, 
        sorted_results: List[TestResult], 
        time_window_minutes: int
    ) -> str:
        """Analyze throughput trend over time."""
        if len(sorted_results) < 2:
            return "insufficient_data"
        
        # Split into time windows
        start_time = sorted_results[0].timestamp
        window_size = timedelta(minutes=time_window_minutes)
        
        windows = {}
        for result in sorted_results:
            window_start = start_time + ((result.timestamp - start_time) // window_size) * window_size
            if window_start not in windows:
                windows[window_start] = 0
            windows[window_start] += 1
        
        if len(windows) < 2:
            return "insufficient_data"
        
        # Calculate trend
        window_counts = list(windows.values())
        first_half = window_counts[:len(window_counts)//2]
        second_half = window_counts[len(window_counts)//2:]
        
        if not first_half or not second_half:
            return "insufficient_data"
        
        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)
        
        if second_avg > first_avg * 1.1:
            return "increasing"
        elif second_avg < first_avg * 0.9:
            return "decreasing"
        else:
            return "stable" 