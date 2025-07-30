"""
Experiment management for A/B testing.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from ..types import (
    Experiment,
    ExperimentConfig,
    TestStatus,
    TestResult,
    AnalysisReport,
)


logger = logging.getLogger(__name__)


class ExperimentManager:
    """
    Manages A/B test experiments and their lifecycle.
    """
    
    def __init__(self):
        """Initialize the experiment manager."""
        self.experiments: Dict[str, Experiment] = {}
        self.logger = logging.getLogger(__name__)
    
    def create_experiment(
        self,
        name: str,
        description: Optional[str],
        variants: List,
        config: ExperimentConfig
    ) -> Experiment:
        """Create a new experiment."""
        experiment = Experiment(
            name=name,
            description=description,
            variants=variants,
            config=config,
            status=TestStatus.DRAFT
        )
        
        self.experiments[experiment.id] = experiment
        self.logger.info(f"Created experiment: {experiment.id}")
        
        return experiment
    
    def get_experiment(self, experiment_id: str) -> Optional[Experiment]:
        """Get an experiment by ID."""
        return self.experiments.get(experiment_id)
    
    def list_experiments(self, status: Optional[TestStatus] = None) -> List[Experiment]:
        """List experiments, optionally filtered by status."""
        experiments = list(self.experiments.values())
        
        if status:
            experiments = [exp for exp in experiments if exp.status == status]
        
        return experiments
    
    def update_experiment_status(self, experiment_id: str, status: TestStatus) -> None:
        """Update the status of an experiment."""
        if experiment_id in self.experiments:
            self.experiments[experiment_id].status = status
            self.logger.info(f"Updated experiment {experiment_id} status to {status}")
    
    def add_test_result(self, experiment_id: str, result: TestResult) -> None:
        """Add a test result to an experiment."""
        if experiment_id in self.experiments:
            self.experiments[experiment_id].results.append(result)
    
    def get_experiment_results(self, experiment_id: str) -> List[TestResult]:
        """Get all test results for an experiment."""
        if experiment_id in self.experiments:
            return self.experiments[experiment_id].results
        return []
    
    def check_experiment_completion(self, experiment_id: str) -> bool:
        """Check if an experiment should be completed based on criteria."""
        experiment = self.get_experiment(experiment_id)
        if not experiment:
            return False
        
        config = experiment.config
        results = experiment.results
        
        # Check minimum sample size
        variant_counts = {}
        for result in results:
            variant_counts[result.variant_name] = variant_counts.get(result.variant_name, 0) + 1
        
        min_samples_met = all(
            count >= config.min_sample_size 
            for count in variant_counts.values()
        )
        
        # Check maximum duration
        if experiment.started_at:
            duration = datetime.utcnow() - experiment.started_at
            max_duration_met = duration.days >= config.max_duration_days
        else:
            max_duration_met = False
        
        return min_samples_met or max_duration_met
    
    def cleanup_completed_experiments(self) -> List[str]:
        """Clean up completed experiments and return their IDs."""
        completed_ids = []
        
        for experiment_id, experiment in self.experiments.items():
            if experiment.status == TestStatus.COMPLETED:
                completed_ids.append(experiment_id)
        
        for experiment_id in completed_ids:
            del self.experiments[experiment_id]
        
        if completed_ids:
            self.logger.info(f"Cleaned up {len(completed_ids)} completed experiments")
        
        return completed_ids 