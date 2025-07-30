"""
Type definitions for the prompt-optimizer package.
"""

from typing import Dict, List, Optional, Any, Union, Literal
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel, Field


class ProviderType(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"
    VLLM = "vllm"


class MetricType(str, Enum):
    """Types of metrics that can be tracked."""
    QUALITY = "quality"
    LATENCY = "latency"
    COST = "cost"
    TOKENS = "tokens"
    USER_SATISFACTION = "user_satisfaction"
    CONVERSION_RATE = "conversion_rate"


class TestStatus(str, Enum):
    """Status of A/B tests."""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    STOPPED = "stopped"


class SignificanceLevel(str, Enum):
    """Statistical significance levels."""
    P01 = "0.01"
    P05 = "0.05"
    P10 = "0.10"


class OptimizerConfig(BaseModel):
    """Configuration for the PromptOptimizer."""
    database_url: str = Field(default="sqlite:///prompt_optimizer.db")
    redis_url: Optional[str] = Field(default=None)
    default_provider: ProviderType = Field(default=ProviderType.OPENAI)
    api_keys: Dict[str, str] = Field(default_factory=dict)
    max_concurrent_tests: int = Field(default=10)
    cache_ttl: int = Field(default=3600)  # seconds
    log_level: str = Field(default="INFO")


class PromptVariant(BaseModel):
    """A prompt variant for A/B testing."""
    name: str
    template: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    version: str = Field(default="1.0.0")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ExperimentConfig(BaseModel):
    """Configuration for an A/B test experiment."""
    name: str
    description: Optional[str] = None
    traffic_split: Dict[str, float] = Field(description="Variant name to traffic percentage")
    min_sample_size: int = Field(default=100, description="Minimum samples per variant")
    significance_level: float = Field(default=0.05, description="Statistical significance level")
    max_duration_days: int = Field(default=14, description="Maximum test duration")
    early_stopping: bool = Field(default=True, description="Enable early stopping")
    metrics: List[MetricType] = Field(default_factory=lambda: [MetricType.QUALITY, MetricType.COST])
    provider: ProviderType = Field(default=ProviderType.OPENAI)
    model: str = Field(default="gpt-3.5-turbo")


class TestResult(BaseModel):
    """Result of a single test run."""
    experiment_id: str
    variant_name: str
    user_id: str
    input_data: Dict[str, Any]
    response: str
    quality_score: Optional[float] = None
    latency_ms: float
    cost_usd: float
    tokens_used: int
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class QualityScore(BaseModel):
    """Quality score for a response."""
    overall_score: float = Field(ge=0.0, le=1.0)
    relevance: float = Field(ge=0.0, le=1.0)
    coherence: float = Field(ge=0.0, le=1.0)
    accuracy: float = Field(ge=0.0, le=1.0)
    safety: float = Field(ge=0.0, le=1.0)
    feedback: Optional[str] = None


class SignificanceResult(BaseModel):
    """Statistical significance test result."""
    is_significant: bool
    p_value: float
    confidence_interval: tuple[float, float]
    effect_size: float
    power: float
    sample_size: int
    variant_a: str
    variant_b: str


class AnalysisReport(BaseModel):
    """Complete analysis report for an experiment."""
    experiment_id: str
    status: TestStatus
    best_variant: Optional[str] = None
    confidence_level: float
    total_samples: int
    duration_days: float
    significance_results: List[SignificanceResult] = Field(default_factory=list)
    metrics_summary: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class OptimizationConfig(BaseModel):
    """Configuration for prompt optimization."""
    target_metrics: List[MetricType] = Field(default_factory=lambda: [MetricType.QUALITY])
    max_iterations: int = Field(default=50)
    population_size: int = Field(default=20)
    mutation_rate: float = Field(default=0.1)
    crossover_rate: float = Field(default=0.8)
    fitness_threshold: float = Field(default=0.95)
    constraints: Dict[str, Any] = Field(default_factory=dict)


class OptimizedPrompt(BaseModel):
    """Result of prompt optimization."""
    original_prompt: str
    optimized_prompt: str
    improvement_score: float
    metrics_improvement: Dict[str, float] = Field(default_factory=dict)
    optimization_history: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PromptVersion(BaseModel):
    """Version control for prompts."""
    id: str
    prompt: str
    version: str
    branch: str = Field(default="main")
    parent_version: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None


class PromptDiff(BaseModel):
    """Difference between two prompt versions."""
    version_a: str
    version_b: str
    additions: List[str] = Field(default_factory=list)
    deletions: List[str] = Field(default_factory=list)
    changes: List[Dict[str, Any]] = Field(default_factory=list)
    similarity_score: float


class Experiment(BaseModel):
    """An A/B test experiment."""
    id: str
    name: str
    description: Optional[str] = None
    variants: List[PromptVariant]
    config: ExperimentConfig
    status: TestStatus = Field(default=TestStatus.DRAFT)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results: List[TestResult] = Field(default_factory=list)


# Additional utility types
JSON = Dict[str, Any]
UserID = str
ExperimentID = str
VariantName = str
PromptTemplate = str 