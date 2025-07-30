"""
SQLAlchemy models for prompt optimization data.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Experiment(Base):
    """Experiment model."""
    __tablename__ = "experiments"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    config = Column(JSON)
    
    # Relationships
    variants = relationship("Variant", back_populates="experiment")
    results = relationship("TestResult", back_populates="experiment")


class Variant(Base):
    """Prompt variant model."""
    __tablename__ = "variants"
    
    id = Column(String(36), primary_key=True)
    experiment_id = Column(String(36), ForeignKey("experiments.id"))
    name = Column(String(255), nullable=False)
    template = Column(Text, nullable=False)
    version = Column(String(50), nullable=False)
    parameters = Column(JSON)
    meta = Column(JSON)
    
    # Relationships
    experiment = relationship("Experiment", back_populates="variants")
    results = relationship("TestResult", back_populates="variant")


class TestResult(Base):
    """Test result model."""
    __tablename__ = "test_results"
    
    id = Column(String(36), primary_key=True)
    experiment_id = Column(String(36), ForeignKey("experiments.id"))
    variant_id = Column(String(36), ForeignKey("variants.id"))
    user_id = Column(String(255), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    quality_score = Column(Float)
    latency_ms = Column(Float)
    cost_usd = Column(Float)
    tokens_used = Column(Integer)
    response_text = Column(Text)
    meta = Column(JSON)
    
    # Relationships
    experiment = relationship("Experiment", back_populates="results")
    variant = relationship("Variant", back_populates="results")


class OptimizationRun(Base):
    """Optimization run model."""
    __tablename__ = "optimization_runs"
    
    id = Column(String(36), primary_key=True)
    experiment_id = Column(String(36), ForeignKey("experiments.id"))
    original_prompt = Column(Text, nullable=False)
    optimized_prompt = Column(Text, nullable=False)
    improvement_score = Column(Float)
    metrics_improvement = Column(JSON)
    optimization_history = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class CostEntry(Base):
    """Cost tracking model."""
    __tablename__ = "cost_entries"
    
    id = Column(String(36), primary_key=True)
    experiment_id = Column(String(36), ForeignKey("experiments.id"))
    provider = Column(String(50), nullable=False)
    model = Column(String(100), nullable=False)
    tokens_used = Column(Integer, nullable=False)
    cost_usd = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    meta = Column(JSON) 