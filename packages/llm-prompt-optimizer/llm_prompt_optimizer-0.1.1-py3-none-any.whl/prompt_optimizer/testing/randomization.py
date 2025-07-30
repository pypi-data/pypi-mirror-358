"""
Traffic splitting and randomization for A/B testing.
"""

import hashlib
import logging
from typing import Dict, List
import random


logger = logging.getLogger(__name__)


class TrafficSplitter:
    """
    Handles traffic splitting and consistent user assignment for A/B tests.
    
    Features:
    - Consistent user assignment using hash-based randomization
    - Support for multiple variants with custom traffic splits
    - Deterministic assignment for reproducible results
    """
    
    def __init__(self, traffic_split: Dict[str, float]):
        """
        Initialize traffic splitter.
        
        Args:
            traffic_split: Dictionary mapping variant names to traffic percentages
        """
        self.traffic_split = traffic_split
        self.variants = list(traffic_split.keys())
        self.percentages = list(traffic_split.values())
        
        # Validate traffic split
        total_percentage = sum(self.percentages)
        if abs(total_percentage - 1.0) > 0.001:
            raise ValueError(f"Traffic split percentages must sum to 1.0, got {total_percentage}")
        
        # Create cumulative distribution for assignment
        self.cumulative_dist = []
        cumulative = 0.0
        for percentage in self.percentages:
            cumulative += percentage
            self.cumulative_dist.append(cumulative)
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initialized traffic splitter with split: {traffic_split}")
    
    def assign_variant(self, user_id: str) -> str:
        """
        Assign a variant to a user based on consistent hashing.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Assigned variant name
        """
        # Create hash of user ID for consistent assignment
        hash_value = hashlib.md5(user_id.encode()).hexdigest()
        hash_int = int(hash_value, 16)
        
        # Normalize to [0, 1) range
        normalized_value = (hash_int % 10000) / 10000.0
        
        # Find which variant this value falls into
        for i, cumulative in enumerate(self.cumulative_dist):
            if normalized_value <= cumulative:
                return self.variants[i]
        
        # Fallback to last variant (shouldn't happen with proper cumulative dist)
        return self.variants[-1]
    
    def get_assignment_probability(self, user_id: str, variant: str) -> float:
        """
        Get the probability that a user would be assigned to a specific variant.
        
        Args:
            user_id: User identifier
            variant: Variant name
            
        Returns:
            Probability (0.0 to 1.0)
        """
        if variant not in self.traffic_split:
            return 0.0
        
        return self.traffic_split[variant]
    
    def validate_assignment(self, user_id: str, variant: str) -> bool:
        """
        Validate if a user should be assigned to a variant.
        
        Args:
            user_id: User identifier
            variant: Variant name
            
        Returns:
            True if assignment is valid
        """
        assigned_variant = self.assign_variant(user_id)
        return assigned_variant == variant
    
    def get_traffic_distribution(self, num_users: int = 10000) -> Dict[str, int]:
        """
        Simulate traffic distribution for validation.
        
        Args:
            num_users: Number of users to simulate
            
        Returns:
            Dictionary mapping variant names to user counts
        """
        distribution = {variant: 0 for variant in self.variants}
        
        for i in range(num_users):
            user_id = f"user_{i}"
            variant = self.assign_variant(user_id)
            distribution[variant] += 1
        
        return distribution
    
    def update_traffic_split(self, new_traffic_split: Dict[str, float]) -> None:
        """
        Update the traffic split configuration.
        
        Args:
            new_traffic_split: New traffic split configuration
        """
        # Validate new split
        total_percentage = sum(new_traffic_split.values())
        if abs(total_percentage - 1.0) > 0.001:
            raise ValueError(f"Traffic split percentages must sum to 1.0, got {total_percentage}")
        
        self.traffic_split = new_traffic_split
        self.variants = list(new_traffic_split.keys())
        self.percentages = list(new_traffic_split.values())
        
        # Recalculate cumulative distribution
        self.cumulative_dist = []
        cumulative = 0.0
        for percentage in self.percentages:
            cumulative += percentage
            self.cumulative_dist.append(cumulative)
        
        self.logger.info(f"Updated traffic split to: {new_traffic_split}")
    
    def get_variant_info(self) -> Dict[str, Dict[str, float]]:
        """
        Get information about all variants and their traffic allocations.
        
        Returns:
            Dictionary with variant information
        """
        info = {}
        cumulative = 0.0
        
        for i, variant in enumerate(self.variants):
            percentage = self.percentages[i]
            info[variant] = {
                "percentage": percentage,
                "cumulative_percentage": cumulative + percentage,
                "range_start": cumulative,
                "range_end": cumulative + percentage
            }
            cumulative += percentage
        
        return info 