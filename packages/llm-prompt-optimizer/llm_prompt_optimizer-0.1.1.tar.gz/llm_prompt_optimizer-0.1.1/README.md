# llm-prompt-optimizer

A comprehensive framework for systematic A/B testing, optimization, and performance analytics of LLM prompts across multiple providers (OpenAI, Anthropic, Google, HuggingFace, local models).

## Author

**Sherin Joseph Roy**
- Email: sherin.joseph2217@gmail.com
- GitHub: [@Sherin-SEF-AI](https://github.com/Sherin-SEF-AI/prompt-optimizer.git)
- LinkedIn: [@sherin-roy-deepmost](https://www.linkedin.com/in/sherin-roy-deepmost/)

## Features

- **Multi-Variant A/B Testing**: Statistical rigor with early stopping and significance testing
- **Prompt Version Control**: Git-like branching and merging for prompt management
- **Performance Analytics**: Quality scoring, cost tracking, and comprehensive reporting
- **Automated Optimization**: Genetic algorithms and RLHF for prompt improvement
- **Multi-Provider Support**: OpenAI, Anthropic, Google, HuggingFace, local models
- **Data Management**: SQLAlchemy ORM, Redis caching, and efficient storage
- **Visualization Dashboards**: Interactive charts and real-time monitoring
- **RESTful API**: FastAPI-based server with comprehensive endpoints
- **CLI Tools**: Command-line interface for experiment management
- **Framework Integrations**: Easy integration with popular ML frameworks

## Installation

```bash
pip install llm-prompt-optimizer
```

Or install from source:

```bash
git clone https://github.com/Sherin-SEF-AI/prompt-optimizer.git
cd prompt-optimizer
pip install -e .
```

## Quick Start

### Basic Usage

```python
from prompt_optimizer import PromptOptimizer
from prompt_optimizer.types import OptimizerConfig, ExperimentConfig, ProviderType

# Initialize the optimizer
config = OptimizerConfig(
    database_url="sqlite:///prompt_optimizer.db",
    default_provider=ProviderType.OPENAI,
    api_keys={"openai": "your-api-key"}
)
optimizer = PromptOptimizer(config)

# Create an A/B test experiment
experiment_config = ExperimentConfig(
    name="email_subject_test",
    traffic_split={"control": 0.5, "variant": 0.5},
    provider=ProviderType.OPENAI,
    model="gpt-3.5-turbo"
)

experiment = optimizer.create_experiment(
    name="Email Subject Line Test",
    description="Testing different email subject line prompts",
    variants=[
        "Write an engaging subject line for: {topic}",
        "Create a compelling email subject about: {topic}"
    ],
    config=experiment_config
)

# Test prompts
result = await optimizer.test_prompt(
    experiment_id=experiment.id,
    user_id="user123",
    input_data={"topic": "AI in healthcare"}
)

# Analyze results
analysis = optimizer.analyze_experiment(experiment.id)
print(f"Best variant: {analysis.best_variant}")
print(f"Confidence: {analysis.confidence_level:.2%}")
```

### CLI Usage

```bash
# List experiments
prompt-optimizer list-experiments

# Create experiment
prompt-optimizer create-experiment --name "Test" --variants "prompt1" "prompt2"

# Run analysis
prompt-optimizer analyze --experiment-id exp_123

# Optimize prompt
prompt-optimizer optimize --prompt "Your prompt here"
```

### API Usage

Start the server:

```bash
uvicorn prompt_optimizer.api.server:app --reload
```

Access the API at http://localhost:8000 and interactive docs at http://localhost:8000/docs.

## Architecture

```
prompt-optimizer/
├── core/                 # Core optimization engine
├── testing/             # A/B testing framework
├── providers/           # LLM provider integrations
├── analytics/           # Performance analytics
├── optimization/        # Genetic algorithms, RLHF
├── storage/             # Database and caching
├── api/                 # FastAPI server
├── cli/                 # Command-line interface
├── visualization/       # Dashboards and charts
└── types.py            # Type definitions
```

## Configuration

### Environment Variables

```bash
export PROMPT_OPTIMIZER_DATABASE_URL="postgresql://user:pass@localhost/prompt_opt"
export PROMPT_OPTIMIZER_REDIS_URL="redis://localhost:6379"
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export GOOGLE_API_KEY="your-google-key"
```

### Configuration File

Create `config.yaml`:

```yaml
database:
  url: "sqlite:///prompt_optimizer.db"
  pool_size: 10
  max_overflow: 20

redis:
  url: "redis://localhost:6379"
  ttl: 3600

providers:
  openai:
    api_key: "${OPENAI_API_KEY}"
    default_model: "gpt-3.5-turbo"
  anthropic:
    api_key: "${ANTHROPIC_API_KEY}"
    default_model: "claude-3-sonnet-20240229"

optimization:
  max_iterations: 50
  population_size: 20
  mutation_rate: 0.1
  crossover_rate: 0.8

testing:
  default_significance_level: 0.05
  min_sample_size: 100
  max_duration_days: 14
```

## Examples

### A/B Testing Email Prompts

```python
# Create experiment for email subject lines
experiment = optimizer.create_experiment(
    name="Email Subject Optimization",
    description="Testing different email subject line prompts",
    variants=[
        "Subject: {topic} - You won't believe what we found!",
        "Subject: Discover the latest in {topic}",
        "Subject: {topic} insights that will change everything"
    ],
    config=ExperimentConfig(
        traffic_split={"v1": 0.33, "v2": 0.33, "v3": 0.34},
        min_sample_size=50,
        significance_level=0.05
    )
)

# Run tests
for i in range(100):
    result = await optimizer.test_prompt(
        experiment_id=experiment.id,
        user_id=f"user_{i}",
        input_data={"topic": "artificial intelligence"}
    )

# Analyze results
analysis = optimizer.analyze_experiment(experiment.id)
print(f"Best performing variant: {analysis.best_variant}")
```

### Prompt Optimization

```python
# Optimize a customer service prompt
optimized = await optimizer.optimize_prompt(
    base_prompt="Help the customer with their issue",
    optimization_config=OptimizationConfig(
        max_iterations=30,
        target_metrics=[MetricType.QUALITY, MetricType.COST],
        constraints={"max_tokens": 100}
    )
)

print(f"Original: {optimized.original_prompt}")
print(f"Optimized: {optimized.optimized_prompt}")
print(f"Improvement: {optimized.improvement_score:.2%}")
```

### Quality Scoring

```python
from prompt_optimizer.analytics import QualityScorer

scorer = QualityScorer()
score = await scorer.score_response(
    prompt="Explain machine learning",
    response="Machine learning is a subset of AI that enables computers to learn from data."
)

print(f"Overall Score: {score.overall_score:.3f}")
print(f"Relevance: {score.relevance:.3f}")
print(f"Coherence: {score.coherence:.3f}")
print(f"Accuracy: {score.accuracy:.3f}")
```

## Testing

Run the test suite:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run with coverage
pytest --cov=prompt_optimizer tests/

# Run specific test
pytest tests/test_ab_testing.py::test_experiment_creation
```

## Documentation

- [API Reference](https://github.com/Sherin-SEF-AI/prompt-optimizer#readme)
- [Examples](https://github.com/Sherin-SEF-AI/prompt-optimizer#examples)
- [Configuration Guide](https://github.com/Sherin-SEF-AI/prompt-optimizer#configuration)

## Contributing

1. Fork the repository: https://github.com/Sherin-SEF-AI/prompt-optimizer.git
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Roadmap

- [ ] Advanced prompt templates and variables
- [ ] Multi-modal prompt optimization
- [ ] Real-time streaming analytics
- [ ] Enterprise SSO integration
- [ ] Advanced cost optimization algorithms
- [ ] Prompt security and safety checks
- [ ] Integration with popular ML platforms
- [ ] Mobile app for experiment monitoring

## Support

- **Issues**: [GitHub Issues](https://github.com/Sherin-SEF-AI/prompt-optimizer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Sherin-SEF-AI/prompt-optimizer/discussions)
- **Email**: sherin.joseph2217@gmail.com
- **LinkedIn**: [Sherin Joseph Roy](https://www.linkedin.com/in/sherin-roy-deepmost/)

## Acknowledgments

- OpenAI, Anthropic, Google, and HuggingFace for their LLM APIs
- The open-source community for the excellent libraries used in this project
- All contributors and users of this framework

---

**Made with ❤️ by Sherin Joseph Roy** 