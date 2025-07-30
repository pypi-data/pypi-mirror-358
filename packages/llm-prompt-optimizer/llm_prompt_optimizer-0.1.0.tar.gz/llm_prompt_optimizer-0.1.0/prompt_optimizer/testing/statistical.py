"""
Statistical analysis for A/B testing results.
"""

import logging
from typing import List, Dict, Any, Tuple
import numpy as np
from scipy import stats
from scipy.stats import ttest_ind, chi2_contingency, mannwhitneyu
import pandas as pd

from ..types import TestResult, SignificanceResult


logger = logging.getLogger(__name__)


class StatisticalAnalyzer:
    """
    Performs statistical analysis on A/B test results.
    
    Features:
    - T-test for continuous metrics
    - Chi-square test for categorical metrics
    - Mann-Whitney U test for non-parametric data
    - Confidence interval calculation
    - Effect size calculation
    - Power analysis
    """
    
    def __init__(self):
        """Initialize the statistical analyzer."""
        self.logger = logging.getLogger(__name__)
    
    def analyze_continuous_metric(
        self, 
        group_a: List[float], 
        group_b: List[float],
        alpha: float = 0.05
    ) -> SignificanceResult:
        """Analyze continuous metric differences between two groups."""
        if len(group_a) < 2 or len(group_b) < 2:
            return SignificanceResult(
                is_significant=False,
                p_value=1.0,
                confidence_interval=(0.0, 0.0),
                effect_size=0.0,
                power=0.5,
                sample_size=len(group_a) + len(group_b),
                variant_a="A",
                variant_b="B"
            )
        
        # Perform t-test
        t_stat, p_value = stats.ttest_ind(group_a, group_b, equal_var=False)
        
        # Calculate confidence interval
        mean_a, mean_b = np.mean(group_a), np.mean(group_b)
        std_a, std_b = np.std(group_a, ddof=1), np.std(group_b, ddof=1)
        n_a, n_b = len(group_a), len(group_b)
        
        # Standard error of the difference
        se_diff = np.sqrt((std_a**2 / n_a) + (std_b**2 / n_b))
        
        # Confidence interval
        ci_lower = (mean_b - mean_a) - stats.t.ppf(1 - alpha/2, min(n_a, n_b) - 1) * se_diff
        ci_upper = (mean_b - mean_a) + stats.t.ppf(1 - alpha/2, min(n_a, n_b) - 1) * se_diff
        
        # Calculate effect size (Cohen's d)
        pooled_std = np.sqrt(((n_a - 1) * std_a**2 + (n_b - 1) * std_b**2) / (n_a + n_b - 2))
        effect_size = (mean_b - mean_a) / pooled_std if pooled_std > 0 else 0.0
        
        return SignificanceResult(
            is_significant=p_value < alpha,
            p_value=p_value,
            confidence_interval=(ci_lower, ci_upper),
            effect_size=effect_size,
            power=0.8,  # Default power
            sample_size=len(group_a) + len(group_b),
            variant_a="A",
            variant_b="B"
        )
    
    def analyze_categorical_metric(
        self,
        group_a_successes: int,
        group_a_total: int,
        group_b_successes: int,
        group_b_total: int,
        alpha: float = 0.05
    ) -> SignificanceResult:
        """
        Analyze categorical metric differences (e.g., conversion rates).
        
        Args:
            group_a_successes: Number of successes in group A
            group_a_total: Total number in group A
            group_b_successes: Number of successes in group B
            group_b_total: Total number in group B
            alpha: Significance level
            
        Returns:
            Significance test result
        """
        if group_a_total == 0 or group_b_total == 0:
            return SignificanceResult(
                is_significant=False,
                p_value=1.0,
                confidence_interval=(0.0, 0.0),
                effect_size=0.0,
                power=0.0,
                sample_size=group_a_total + group_b_total,
                variant_a="A",
                variant_b="B"
            )
        
        # Create contingency table
        contingency_table = np.array([
            [group_a_successes, group_a_total - group_a_successes],
            [group_b_successes, group_b_total - group_b_successes]
        ])
        
        # Perform chi-square test
        chi2_stat, p_value, dof, expected = chi2_contingency(contingency_table)
        
        # Calculate proportions
        prop_a = group_a_successes / group_a_total
        prop_b = group_b_successes / group_b_total
        
        # Calculate confidence interval for difference
        se_diff = np.sqrt(
            (prop_a * (1 - prop_a) / group_a_total) + 
            (prop_b * (1 - prop_b) / group_b_total)
        )
        
        diff = prop_b - prop_a
        z_alpha = stats.norm.ppf(1 - alpha/2)
        ci_lower = diff - z_alpha * se_diff
        ci_upper = diff + z_alpha * se_diff
        
        # Calculate effect size (phi coefficient)
        effect_size = np.sqrt(chi2_stat / (group_a_total + group_b_total))
        
        # Calculate power
        power = self._calculate_power(group_a_total, group_b_total, effect_size, alpha)
        
        return SignificanceResult(
            is_significant=p_value < alpha,
            p_value=p_value,
            confidence_interval=(ci_lower, ci_upper),
            effect_size=effect_size,
            power=power,
            sample_size=group_a_total + group_b_total,
            variant_a="A",
            variant_b="B"
        )
    
    def analyze_non_parametric(
        self,
        group_a: List[float],
        group_b: List[float],
        alpha: float = 0.05
    ) -> SignificanceResult:
        """
        Analyze non-parametric differences using Mann-Whitney U test.
        
        Args:
            group_a: Values for group A
            group_b: Values for group B
            alpha: Significance level
            
        Returns:
            Significance test result
        """
        if len(group_a) < 2 or len(group_b) < 2:
            return SignificanceResult(
                is_significant=False,
                p_value=1.0,
                confidence_interval=(0.0, 0.0),
                effect_size=0.0,
                power=0.0,
                sample_size=len(group_a) + len(group_b),
                variant_a="A",
                variant_b="B"
            )
        
        # Perform Mann-Whitney U test
        u_stat, p_value = mannwhitneyu(group_a, group_b, alternative='two-sided')
        
        # Calculate effect size (rank-biserial correlation)
        n_a, n_b = len(group_a), len(group_b)
        effect_size = 1 - (2 * u_stat) / (n_a * n_b)
        
        # Calculate confidence interval (approximate)
        mean_a, mean_b = np.mean(group_a), np.mean(group_b)
        std_a, std_b = np.std(group_a, ddof=1), np.std(group_b, ddof=1)
        se_diff = np.sqrt((std_a**2 / n_a) + (std_b**2 / n_b))
        
        z_alpha = stats.norm.ppf(1 - alpha/2)
        ci_lower = (mean_b - mean_a) - z_alpha * se_diff
        ci_upper = (mean_b - mean_a) + z_alpha * se_diff
        
        # Calculate power
        power = self._calculate_power(n_a, n_b, abs(effect_size), alpha)
        
        return SignificanceResult(
            is_significant=p_value < alpha,
            p_value=p_value,
            confidence_interval=(ci_lower, ci_upper),
            effect_size=effect_size,
            power=power,
            sample_size=n_a + n_b,
            variant_a="A",
            variant_b="B"
        )
    
    def _calculate_power(
        self, 
        n_a: int, 
        n_b: int, 
        effect_size: float, 
        alpha: float
    ) -> float:
        """
        Calculate statistical power for the test.
        
        Args:
            n_a: Sample size for group A
            n_b: Sample size for group B
            effect_size: Effect size
            alpha: Significance level
            
        Returns:
            Statistical power
        """
        try:
            # Use scipy's power analysis
            from scipy.stats import norm
            
            # Calculate non-centrality parameter
            n_eff = (n_a * n_b) / (n_a + n_b)  # Effective sample size
            ncp = effect_size * np.sqrt(n_eff)
            
            # Calculate critical value
            z_crit = norm.ppf(1 - alpha/2)
            
            # Calculate power
            power = 1 - norm.cdf(z_crit - ncp) + norm.cdf(-z_crit - ncp)
            
            return min(power, 1.0)  # Cap at 1.0
        except Exception as e:
            self.logger.warning(f"Error calculating power: {e}")
            return 0.5  # Default power
    
    def calculate_sample_size(
        self,
        effect_size: float,
        alpha: float = 0.05,
        power: float = 0.8,
        ratio: float = 1.0
    ) -> int:
        """
        Calculate required sample size for a given effect size and power.
        
        Args:
            effect_size: Expected effect size
            alpha: Significance level
            power: Desired statistical power
            ratio: Ratio of group sizes (group_b / group_a)
            
        Returns:
            Required sample size per group
        """
        try:
            from scipy.stats import norm
            
            # Calculate critical values
            z_alpha = norm.ppf(1 - alpha/2)
            z_beta = norm.ppf(power)
            
            # Calculate sample size
            n = 2 * ((z_alpha + z_beta) / effect_size) ** 2
            
            # Adjust for unequal group sizes
            n_adjusted = n * (1 + ratio) ** 2 / (4 * ratio)
            
            return int(np.ceil(n_adjusted))
        except Exception as e:
            self.logger.warning(f"Error calculating sample size: {e}")
            return 100  # Default sample size
    
    def analyze_multiple_comparisons(
        self,
        groups: Dict[str, List[float]],
        alpha: float = 0.05,
        method: str = "bonferroni"
    ) -> List[SignificanceResult]:
        """
        Analyze multiple group comparisons with correction for multiple testing.
        
        Args:
            groups: Dictionary of group names to values
            alpha: Significance level
            method: Multiple comparison correction method
            
        Returns:
            List of significance test results
        """
        group_names = list(groups.keys())
        results = []
        
        # Perform all pairwise comparisons
        for i in range(len(group_names)):
            for j in range(i + 1, len(group_names)):
                group_a_name = group_names[i]
                group_b_name = group_names[j]
                
                result = self.analyze_continuous_metric(
                    groups[group_a_name],
                    groups[group_b_name],
                    alpha
                )
                
                # Update variant names
                result.variant_a = group_a_name
                result.variant_b = group_b_name
                
                results.append(result)
        
        # Apply multiple comparison correction
        if method == "bonferroni":
            num_comparisons = len(results)
            corrected_alpha = alpha / num_comparisons
            
            for result in results:
                result.is_significant = result.p_value < corrected_alpha
        
        return results
    
    def calculate_confidence_interval(
        self,
        data: List[float],
        confidence_level: float = 0.95
    ) -> Tuple[float, float]:
        """
        Calculate confidence interval for a dataset.
        
        Args:
            data: List of values
            confidence_level: Confidence level (e.g., 0.95 for 95%)
            
        Returns:
            Confidence interval (lower, upper)
        """
        if len(data) < 2:
            return (0.0, 0.0)
        
        mean = np.mean(data)
        std = np.std(data, ddof=1)
        n = len(data)
        
        # Calculate standard error
        se = std / np.sqrt(n)
        
        # Calculate confidence interval
        t_value = stats.t.ppf((1 + confidence_level) / 2, n - 1)
        margin_of_error = t_value * se
        
        return (mean - margin_of_error, mean + margin_of_error) 