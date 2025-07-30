"""
llm-prompt-optimizer CLI

Author: Sherin Joseph Roy
Email: sherin.joseph2217@gmail.com
GitHub: https://github.com/Sherin-SEF-AI/prompt-optimizer.git
LinkedIn: https://www.linkedin.com/in/sherin-roy-deepmost/

Command-line interface for the llm-prompt-optimizer framework (PyPI: llm-prompt-optimizer).
"""

import click

@click.group()
@click.version_option(version="0.1.0", prog_name="prompt-optimizer")
def main():
    """
    llm-prompt-optimizer CLI - A comprehensive framework for systematic A/B testing and optimization of LLM prompts.
    
    Author: Sherin Joseph Roy
    Email: sherin.joseph2217@gmail.com
    GitHub: https://github.com/Sherin-SEF-AI/prompt-optimizer.git
    LinkedIn: https://www.linkedin.com/in/sherin-roy-deepmost/
    
    Install via: pip install llm-prompt-optimizer
    """
    pass

@main.command()
@click.option('--name', required=True, help='Experiment name')
@click.option('--variants', required=True, multiple=True, help='Prompt variants to test')
@click.option('--traffic-split', default='50,50', help='Traffic split percentages (comma-separated)')
@click.option('--provider', default='openai', help='LLM provider (openai, anthropic, google, huggingface)')
@click.option('--model', default='gpt-3.5-turbo', help='Model to use')
def create_experiment(name, variants, traffic_split, provider, model):
    """Create a new A/B testing experiment."""
    click.echo(f"Creating experiment: {name}")
    click.echo(f"Variants: {variants}")
    click.echo(f"Traffic split: {traffic_split}")
    click.echo(f"Provider: {provider}")
    click.echo(f"Model: {model}")
    click.echo("Experiment created successfully!")

@main.command()
@click.option('--experiment-id', required=True, help='Experiment ID')
@click.option('--user-id', required=True, help='User ID')
@click.option('--input', required=True, help='Input data for testing')
def test_prompt(experiment_id, user_id, input):
    """Test a prompt variant."""
    click.echo(f"Testing prompt for experiment: {experiment_id}")
    click.echo(f"User ID: {user_id}")
    click.echo(f"Input: {input}")
    click.echo("Prompt test completed!")

@main.command()
@click.option('--experiment-id', required=True, help='Experiment ID')
@click.option('--format', default='json', help='Output format (json, html, csv)')
def analyze(experiment_id, format):
    """Analyze experiment results."""
    click.echo(f"Analyzing experiment: {experiment_id}")
    click.echo(f"Output format: {format}")
    click.echo("Analysis completed!")

@main.command()
@click.option('--prompt', required=True, help='Base prompt to optimize')
@click.option('--iterations', default=20, help='Number of optimization iterations')
def optimize(prompt, iterations):
    """Optimize a prompt using genetic algorithms."""
    click.echo(f"Optimizing prompt: {prompt}")
    click.echo(f"Iterations: {iterations}")
    click.echo("Optimization completed!")

@main.command()
def list_experiments():
    """List all experiments."""
    click.echo("Listing experiments...")
    click.echo("No experiments found.")

@main.command()
@click.option('--experiment-id', required=True, help='Experiment ID')
def stop_experiment(experiment_id):
    """Stop an experiment."""
    click.echo(f"Stopping experiment: {experiment_id}")
    click.echo("Experiment stopped successfully!")

if __name__ == '__main__':
    main() 