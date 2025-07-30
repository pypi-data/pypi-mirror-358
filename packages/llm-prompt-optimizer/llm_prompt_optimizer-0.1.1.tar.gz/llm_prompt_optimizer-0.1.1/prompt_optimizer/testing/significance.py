"""
Statistical significance testing for A/B test results.
"""

import logging
from typing import List
from scipy import stats

from ..types import SignificanceResult


logger = logging.getLogger(__name__)


class SignificanceTester:
    """Performs statistical significance tests for A/B testing."""
    
    def __init__(self):
        """Initialize the significance tester."""
        self.logger = logging.getLogger(__name__)
    
    def test_significance(
        self, 
        group_a: List[float], 
        group_b: List[float], 
        alpha: float = 0.05
    ) -> SignificanceResult:
        """
        Test significance between two groups.
        
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
                power=0.5,
                sample_size=len(group_a) + len(group_b),
                variant_a="A",
                variant_b="B"
            )
        
        # Perform t-test
        t_stat, p_value = stats.ttest_ind(group_a, group_b, equal_var=False)
        
        # Calculate effect size
        effect_size = self._calculate_effect_size(group_a, group_b)
        
        # Calculate confidence interval
        ci = self._calculate_confidence_interval(group_a, group_b, alpha)
        
        return SignificanceResult(
            is_significant=p_value < alpha,
            p_value=p_value,
            confidence_interval=ci,
            effect_size=effect_size,
            power=0.8,
            sample_size=len(group_a) + len(group_b),
            variant_a="A",
            variant_b="B"
        )
    
    def _calculate_effect_size(self, group_a: List[float], group_b: List[float]) -> float:
        """Calculate Cohen's d effect size."""
        import numpy as np
        
        mean_a, mean_b = np.mean(group_a), np.mean(group_b)
        std_a, std_b = np.std(group_a, ddof=1), np.std(group_b, ddof=1)
        n_a, n_b = len(group_a), len(group_b)
        
        # Pooled standard deviation
        pooled_std = np.sqrt(((n_a - 1) * std_a**2 + (n_b - 1) * std_b**2) / (n_a + n_b - 2))
        
        if pooled_std == 0:
            return 0.0
        
        return (mean_b - mean_a) / pooled_std
    
    def _calculate_confidence_interval(
        self, 
        group_a: List[float], 
        group_b: List[float], 
        alpha: float
    ) -> tuple[float, float]:
        """Calculate confidence interval for the difference."""
        import numpy as np
        
        mean_a, mean_b = np.mean(group_a), np.mean(group_b)
        std_a, std_b = np.std(group_a, ddof=1), np.std(group_b, ddof=1)
        n_a, n_b = len(group_a), len(group_b)
        
        # Standard error of the difference
        se_diff = np.sqrt((std_a**2 / n_a) + (std_b**2 / n_b))
        
        # Confidence interval
        t_value = stats.t.ppf(1 - alpha/2, min(n_a, n_b) - 1)
        margin = t_value * se_diff
        
        diff = mean_b - mean_a
        return (diff - margin, diff + margin) 