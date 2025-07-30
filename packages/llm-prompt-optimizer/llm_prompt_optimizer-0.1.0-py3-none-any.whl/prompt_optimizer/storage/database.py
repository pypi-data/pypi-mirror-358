"""
Database management for prompt optimization.
"""

import logging
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from uuid import uuid4
from datetime import datetime

from .models import Base, Experiment, Variant, TestResult, OptimizationRun, CostEntry
from ..types import Experiment as ExperimentType, TestResult as TestResultType


logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages database operations for prompt optimization.
    
    Features:
    - SQLAlchemy ORM integration
    - Connection pooling
    - Transaction management
    - Data validation
    - Migration support
    """
    
    def __init__(self, database_url: str):
        """
        Initialize database manager.
        
        Args:
            database_url: Database connection URL
        """
        self.database_url = database_url
        self.engine = create_engine(database_url, pool_pre_ping=True)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.logger = logging.getLogger(__name__)
        
        # Create tables
        Base.metadata.create_all(bind=self.engine)
        self.logger.info("Database initialized")
    
    def get_session(self) -> Session:
        """Get a database session."""
        return self.SessionLocal()
    
    def save_experiment(self, experiment: ExperimentType) -> str:
        """
        Save an experiment to the database.
        
        Args:
            experiment: Experiment object
            
        Returns:
            Experiment ID
        """
        with self.get_session() as session:
            try:
                db_experiment = Experiment(
                    id=experiment.id,
                    name=experiment.name,
                    description=experiment.description,
                    status=experiment.status.value if hasattr(experiment.status, 'value') else experiment.status,
                    created_at=experiment.created_at,
                    started_at=experiment.started_at,
                    completed_at=experiment.completed_at,
                    config={
                        "traffic_split": experiment.config.traffic_split,
                        "min_sample_size": experiment.config.min_sample_size,
                        "significance_level": experiment.config.significance_level,
                        "max_duration_days": experiment.config.max_duration_days,
                        "provider": experiment.config.provider.value if hasattr(experiment.config.provider, 'value') else experiment.config.provider,
                        "model": experiment.config.model
                    }
                )
                
                session.add(db_experiment)
                
                # Create variant records
                for variant in experiment.variants:
                    db_variant = Variant(
                        id=str(uuid4()),
                        experiment_id=experiment.id,
                        name=variant.name,
                        template=variant.template,
                        version=variant.version,
                        parameters=variant.parameters,
                        meta=variant.metadata
                    )
                    session.add(db_variant)
                
                session.commit()
                self.logger.info(f"Saved experiment: {experiment.id}")
                return experiment.id
                
            except SQLAlchemyError as e:
                session.rollback()
                self.logger.error(f"Error saving experiment: {e}")
                raise
    
    def save_test_result(self, result: TestResultType) -> str:
        """
        Save a test result to the database.
        
        Args:
            result: Test result object
            
        Returns:
            Result ID
        """
        with self.get_session() as session:
            try:
                # Look up the DB variant id using experiment_id and variant_name
                db_variant = session.query(Variant).filter(
                    Variant.experiment_id == result.experiment_id,
                    Variant.name == result.variant_name
                ).first()
                if not db_variant:
                    raise ValueError(f"Variant '{result.variant_name}' not found for experiment '{result.experiment_id}'")
                db_result = TestResult(
                    id=str(uuid4()),
                    experiment_id=result.experiment_id,
                    variant_id=db_variant.id,
                    user_id=result.user_id,
                    timestamp=result.timestamp,
                    quality_score=result.quality_score,
                    latency_ms=result.latency_ms,
                    cost_usd=result.cost_usd,
                    tokens_used=result.tokens_used,
                    response_text=result.response,
                    meta=result.metadata
                )
                
                session.add(db_result)
                session.commit()
                
                self.logger.debug(f"Saved test result for experiment {result.experiment_id}, variant {result.variant_name}")
                return db_result.id
                
            except SQLAlchemyError as e:
                session.rollback()
                self.logger.error(f"Error saving test result: {e}")
                raise
    
    def get_experiment(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an experiment by ID.
        
        Args:
            experiment_id: Experiment ID
            
        Returns:
            Experiment data or None
        """
        with self.get_session() as session:
            try:
                db_experiment = session.query(Experiment).filter(
                    Experiment.id == experiment_id
                ).first()
                if not db_experiment:
                    return None
                # Get variants
                variants = session.query(Variant).filter(
                    Variant.experiment_id == experiment_id
                ).all()
                return {
                    "id": db_experiment.id,
                    "name": db_experiment.name,
                    "description": db_experiment.description,
                    "status": db_experiment.status,
                    "created_at": db_experiment.created_at,
                    "started_at": db_experiment.started_at,
                    "completed_at": db_experiment.completed_at,
                    "config": db_experiment.config,
                    "variants": [
                        {
                            "name": v.name,
                            "template": v.template,
                            "parameters": v.parameters,
                            "version": v.version,
                            "metadata": v.meta
                        }
                        for v in variants
                    ]
                }
            except SQLAlchemyError as e:
                self.logger.error(f"Error getting experiment: {e}")
                return None
    
    def get_test_results(
        self, 
        experiment_id: str, 
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get test results for an experiment.
        
        Args:
            experiment_id: Experiment ID
            limit: Maximum number of results to return
            
        Returns:
            List of test results
        """
        with self.get_session() as session:
            try:
                query = session.query(TestResult).filter(
                    TestResult.experiment_id == experiment_id
                ).order_by(TestResult.timestamp.desc())
                
                if limit:
                    query = query.limit(limit)
                
                results = query.all()
                
                # Map variant_id to variant_name
                variant_id_to_name = {v.id: v.name for v in session.query(Variant).filter(Variant.experiment_id == experiment_id).all()}
                return [
                    {
                        "experiment_id": r.experiment_id,
                        "variant_name": variant_id_to_name.get(r.variant_id, r.variant_id),
                        "user_id": r.user_id,
                        "timestamp": r.timestamp,
                        "quality_score": r.quality_score,
                        "latency_ms": r.latency_ms,
                        "cost_usd": r.cost_usd,
                        "tokens_used": r.tokens_used,
                        "response": r.response_text,
                        "metadata": r.meta
                    }
                    for r in results
                ]
                
            except SQLAlchemyError as e:
                self.logger.error(f"Error getting test results: {e}")
                return []
    
    def update_experiment_status(
        self, 
        experiment_id: str, 
        status: str,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None
    ) -> bool:
        """
        Update experiment status.
        
        Args:
            experiment_id: Experiment ID
            status: New status
            started_at: Start timestamp
            completed_at: Completion timestamp
            
        Returns:
            Success status
        """
        with self.get_session() as session:
            try:
                experiment = session.query(Experiment).filter(
                    Experiment.id == experiment_id
                ).first()
                
                if not experiment:
                    return False
                
                experiment.status = status
                if started_at:
                    experiment.started_at = started_at
                if completed_at:
                    experiment.completed_at = completed_at
                
                session.commit()
                self.logger.info(f"Updated experiment {experiment_id} status to {status}")
                return True
                
            except SQLAlchemyError as e:
                session.rollback()
                self.logger.error(f"Error updating experiment status: {e}")
                return False
    
    def get_experiment_summary(self, experiment_id: str) -> Dict[str, Any]:
        """
        Get experiment summary statistics.
        
        Args:
            experiment_id: Experiment ID
            
        Returns:
            Summary statistics
        """
        with self.get_session() as session:
            try:
                experiment = session.query(Experiment).filter(
                    Experiment.id == experiment_id
                ).first()
                if not experiment:
                    return {}
                # Return summary using instance attributes
                return {
                    "id": experiment.id,
                    "name": experiment.name,
                    "status": experiment.status,
                    "created_at": experiment.created_at,
                    "started_at": experiment.started_at,
                    "completed_at": experiment.completed_at,
                }
            except SQLAlchemyError as e:
                self.logger.error(f"Error getting experiment summary: {e}")
                return {}
    
    def save_optimization_run(
        self,
        experiment_id: str,
        original_prompt: str,
        optimized_prompt: str,
        improvement_score: float,
        metrics_improvement: Dict[str, Any],
        optimization_history: List[Dict[str, Any]]
    ) -> str:
        """
        Save an optimization run.
        
        Args:
            experiment_id: Experiment ID
            original_prompt: Original prompt
            optimized_prompt: Optimized prompt
            improvement_score: Improvement score
            metrics_improvement: Improvement metrics
            optimization_history: Optimization history
            
        Returns:
            Optimization run ID
        """
        with self.get_session() as session:
            try:
                optimization_run = OptimizationRun(
                    id=str(uuid4()),
                    experiment_id=experiment_id,
                    original_prompt=original_prompt,
                    optimized_prompt=optimized_prompt,
                    improvement_score=improvement_score,
                    metrics_improvement=metrics_improvement,
                    optimization_history=optimization_history
                )
                
                session.add(optimization_run)
                session.commit()
                
                self.logger.info(f"Saved optimization run: {optimization_run.id}")
                return optimization_run.id
                
            except SQLAlchemyError as e:
                session.rollback()
                self.logger.error(f"Error saving optimization run: {e}")
                raise
    
    def save_cost_entry(
        self,
        experiment_id: str,
        provider: str,
        model: str,
        tokens_used: int,
        cost_usd: float,
        meta: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Save a cost entry.
        
        Args:
            experiment_id: Experiment ID
            provider: Provider name
            model: Model name
            tokens_used: Number of tokens used
            cost_usd: Cost in USD
            meta: Additional metadata
            
        Returns:
            Cost entry ID
        """
        with self.get_session() as session:
            try:
                cost_entry = CostEntry(
                    id=str(uuid4()),
                    experiment_id=experiment_id,
                    provider=provider,
                    model=model,
                    tokens_used=tokens_used,
                    cost_usd=cost_usd,
                    meta=meta or {}
                )
                
                session.add(cost_entry)
                session.commit()
                
                self.logger.debug(f"Saved cost entry: {cost_entry.id}")
                return cost_entry.id
                
            except SQLAlchemyError as e:
                session.rollback()
                self.logger.error(f"Error saving cost entry: {e}")
                raise
    
    def health_check(self) -> bool:
        """
        Perform database health check.
        
        Returns:
            True if database is healthy
        """
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
                return True
        except Exception as e:
            self.logger.error(f"Database health check failed: {e}")
            return False
    
    def update_experiment(self, experiment: ExperimentType) -> bool:
        """
        Update an experiment in the database.
        Args:
            experiment: Updated experiment object
        Returns:
            Success status
        """
        with self.get_session() as session:
            try:
                db_experiment = session.query(Experiment).filter(
                    Experiment.id == experiment.id
                ).first()
                if not db_experiment:
                    return False
                
                db_experiment.name = experiment.name
                db_experiment.description = experiment.description
                db_experiment.status = experiment.status.value if hasattr(experiment.status, 'value') else experiment.status
                db_experiment.started_at = experiment.started_at
                db_experiment.completed_at = experiment.completed_at
                
                session.commit()
                return True
            except SQLAlchemyError as e:
                session.rollback()
                self.logger.error(f"Error updating experiment: {e}")
                return False
    
    def save_analysis_report(self, analysis: Dict[str, Any]) -> str:
        """
        Save an analysis report to the database.
        Args:
            analysis: Analysis report data
        Returns:
            Report ID
        """
        with self.get_session() as session:
            try:
                report_id = str(uuid4())
                # Store analysis as JSON in a simple table or use existing structure
                # For now, we'll store it in the experiment config
                experiment_id = analysis.get("experiment_id")
                if experiment_id:
                    db_experiment = session.query(Experiment).filter(
                        Experiment.id == experiment_id
                    ).first()
                    if db_experiment:
                        config = db_experiment.config or {}
                        config["analysis_report"] = analysis
                        db_experiment.config = config
                        session.commit()
                
                return report_id
            except SQLAlchemyError as e:
                session.rollback()
                self.logger.error(f"Error saving analysis report: {e}")
                raise
    
    def save_optimized_prompt(self, optimized_prompt: Dict[str, Any]) -> str:
        """
        Save an optimized prompt to the database.
        Args:
            optimized_prompt: Optimized prompt data
        Returns:
            Optimization ID
        """
        with self.get_session() as session:
            try:
                optimization_id = str(uuid4())
                # Store optimization run
                optimization_run = OptimizationRun(
                    id=optimization_id,
                    experiment_id=optimized_prompt.get("experiment_id", ""),
                    original_prompt=optimized_prompt.get("original_prompt", ""),
                    optimized_prompt=optimized_prompt.get("optimized_prompt", ""),
                    improvement_score=optimized_prompt.get("improvement_score", 0.0),
                    metrics_improvement=optimized_prompt.get("metrics_improvement", {}),
                    optimization_history=optimized_prompt.get("optimization_history", [])
                )
                session.add(optimization_run)
                session.commit()
                return optimization_id
            except SQLAlchemyError as e:
                session.rollback()
                self.logger.error(f"Error saving optimized prompt: {e}")
                raise 