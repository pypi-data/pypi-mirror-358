"""
Genetic algorithm for prompt optimization.
"""

import logging
import random
from typing import List, Dict, Any, Optional, Tuple
import re

from ..types import OptimizationConfig, OptimizedPrompt, ProviderType
from ..analytics.quality_scorer import QualityScorer
from ..providers.base import BaseProvider


logger = logging.getLogger(__name__)


class GeneticOptimizer:
    """
    Genetic algorithm-based prompt optimizer.
    
    Features:
    - Population-based evolution
    - Crossover and mutation operations
    - Fitness-based selection
    - Multi-objective optimization
    - Constraint handling
    """
    
    def __init__(self):
        """Initialize the genetic optimizer."""
        self.logger = logging.getLogger(__name__)
        
        # Genetic algorithm parameters
        self.population_size = 20
        self.mutation_rate = 0.1
        self.crossover_rate = 0.8
        self.elite_size = 2
        
        # Prompt templates for mutation
        self.prompt_templates = [
            "You are a helpful assistant. {task}",
            "Please help me with the following: {task}",
            "I need assistance with: {task}",
            "Can you help me with this: {task}",
            "Task: {task}. Please provide a detailed response.",
            "I'm looking for help with: {task}",
            "Please analyze and respond to: {task}",
            "Help me understand: {task}",
        ]
        
        # Quality modifiers
        self.quality_modifiers = [
            "be concise",
            "be detailed",
            "be professional",
            "be friendly",
            "be technical",
            "be creative",
            "be analytical",
            "be helpful",
            "be accurate",
            "be thorough"
        ]
    
    async def optimize(
        self,
        base_prompt: str,
        config: OptimizationConfig,
        providers: Dict[ProviderType, BaseProvider],
        quality_scorer: QualityScorer
    ) -> OptimizedPrompt:
        """
        Optimize a prompt using genetic algorithms.
        
        Args:
            base_prompt: Original prompt to optimize
            config: Optimization configuration
            providers: Available LLM providers
            quality_scorer: Quality scoring function
            
        Returns:
            Optimized prompt with metrics
        """
        self.logger.info(f"Starting genetic optimization for prompt: {base_prompt[:50]}...")
        
        # Initialize population
        population = self._initialize_population(base_prompt, config.population_size)
        
        # Evolution history
        evolution_history = []
        best_fitness = 0.0
        best_prompt = base_prompt
        
        # Main evolution loop
        for generation in range(config.max_iterations):
            # Evaluate fitness for all individuals
            fitness_scores = await self._evaluate_population(
                population, config, providers, quality_scorer
            )
            
            # Find best individual
            best_idx = max(range(len(fitness_scores)), key=lambda i: fitness_scores[i])
            current_best_fitness = fitness_scores[best_idx]
            current_best_prompt = population[best_idx]
            
            # Update best if improved
            if current_best_fitness > best_fitness:
                best_fitness = current_best_fitness
                best_prompt = current_best_prompt
            
            # Record evolution
            evolution_history.append({
                "generation": generation,
                "best_fitness": current_best_fitness,
                "avg_fitness": sum(fitness_scores) / len(fitness_scores),
                "best_prompt": current_best_prompt
            })
            
            self.logger.info(f"Generation {generation}: Best fitness = {current_best_fitness:.3f}")
            
            # Check convergence
            if current_best_fitness >= config.fitness_threshold:
                self.logger.info(f"Converged at generation {generation}")
                break
            
            # Create next generation
            population = self._evolve_population(population, fitness_scores, config)
        
        # Calculate final metrics
        final_metrics = await self._calculate_improvement_metrics(
            base_prompt, best_prompt, config, providers, quality_scorer
        )
        
        return OptimizedPrompt(
            original_prompt=base_prompt,
            optimized_prompt=best_prompt,
            improvement_score=best_fitness,
            metrics_improvement=final_metrics,
            optimization_history=evolution_history
        )
    
    def _initialize_population(self, base_prompt: str, population_size: int) -> List[str]:
        """Initialize the population with variations of the base prompt."""
        population = [base_prompt]  # Keep original
        
        for _ in range(population_size - 1):
            variant = self._create_variant(base_prompt)
            population.append(variant)
        
        return population
    
    def _create_variant(self, prompt: str) -> str:
        """Create a variant of the prompt using mutation operations."""
        variant = prompt
        
        # Apply random mutations
        if random.random() < 0.3:
            variant = self._mutate_template(variant)
        
        if random.random() < 0.3:
            variant = self._mutate_style(variant)
        
        if random.random() < 0.2:
            variant = self._mutate_length(variant)
        
        if random.random() < 0.2:
            variant = self._mutate_structure(variant)
        
        return variant
    
    def _mutate_template(self, prompt: str) -> str:
        """Mutate the prompt template."""
        # Extract task from current prompt
        task_match = re.search(r'\{task\}', prompt)
        if task_match:
            # Replace with random template
            template = random.choice(self.prompt_templates)
            return template
        else:
            # Add template structure
            template = random.choice(self.prompt_templates)
            return template.replace("{task}", prompt)
    
    def _mutate_style(self, prompt: str) -> str:
        """Mutate the style of the prompt."""
        modifier = random.choice(self.quality_modifiers)
        
        if "please" in prompt.lower():
            # Add style modifier
            return prompt.replace("please", f"please {modifier}")
        else:
            # Add style instruction
            return f"{prompt} (Please {modifier})"
    
    def _mutate_length(self, prompt: str) -> str:
        """Mutate the length of the prompt."""
        words = prompt.split()
        
        if len(words) > 20 and random.random() < 0.5:
            # Make shorter
            return " ".join(words[:len(words)//2])
        else:
            # Make longer
            additional = random.choice([
                "Please provide a comprehensive response.",
                "I would appreciate detailed information.",
                "Please be thorough in your explanation."
            ])
            return f"{prompt} {additional}"
    
    def _mutate_structure(self, prompt: str) -> str:
        """Mutate the structure of the prompt."""
        # Add context or constraints
        structures = [
            f"Context: You are an expert in this field. {prompt}",
            f"Constraints: Please be accurate and helpful. {prompt}",
            f"Background: This is important for my work. {prompt}",
            f"Requirements: I need this information quickly. {prompt}"
        ]
        
        return random.choice(structures)
    
    async def _evaluate_population(
        self,
        population: List[str],
        config: OptimizationConfig,
        providers: Dict[ProviderType, BaseProvider],
        quality_scorer: QualityScorer
    ) -> List[float]:
        """Evaluate fitness for all individuals in the population."""
        fitness_scores = []
        
        for prompt in population:
            fitness = await self._evaluate_fitness(
                prompt, config, providers, quality_scorer
            )
            fitness_scores.append(fitness)
        
        return fitness_scores
    
    async def _evaluate_fitness(
        self,
        prompt: str,
        config: OptimizationConfig,
        providers: Dict[ProviderType, BaseProvider],
        quality_scorer: QualityScorer
    ) -> float:
        """Evaluate fitness of a single prompt."""
        try:
            # Test prompt with a sample input
            test_input = {"task": "Explain machine learning in simple terms"}
            formatted_prompt = prompt.format(**test_input)
            
            # Get provider
            provider = list(providers.values())[0]  # Use first available provider
            
            # Generate response
            response = await provider.generate(
                prompt=formatted_prompt,
                model="gpt-3.5-turbo",
                max_tokens=100
            )
            
            # Score quality
            quality_score = await quality_scorer.score_response(
                prompt=formatted_prompt,
                response=response.get("text", ""),
                expected_output="A clear explanation of machine learning"
            )
            
            # Calculate fitness based on target metrics
            fitness = 0.0
            for metric in config.target_metrics:
                if metric.value == "quality":
                    fitness += quality_score.overall_score * 0.6
                elif metric.value == "cost":
                    # Prefer shorter prompts (lower cost)
                    cost_factor = max(0, 1 - len(prompt.split()) / 100)
                    fitness += cost_factor * 0.2
                elif metric.value == "latency":
                    # Prefer simpler prompts (lower latency)
                    latency_factor = max(0, 1 - len(prompt) / 500)
                    fitness += latency_factor * 0.2
            
            return fitness
            
        except Exception as e:
            self.logger.warning(f"Error evaluating fitness: {e}")
            return 0.0
    
    def _evolve_population(
        self,
        population: List[str],
        fitness_scores: List[float],
        config: OptimizationConfig
    ) -> List[str]:
        """Evolve the population using selection, crossover, and mutation."""
        new_population = []
        
        # Elitism: keep best individuals
        elite_indices = sorted(
            range(len(fitness_scores)), 
            key=lambda i: fitness_scores[i], 
            reverse=True
        )[:self.elite_size]
        
        for idx in elite_indices:
            new_population.append(population[idx])
        
        # Generate rest of population
        while len(new_population) < len(population):
            # Selection
            parent1 = self._select_parent(population, fitness_scores)
            parent2 = self._select_parent(population, fitness_scores)
            
            # Crossover
            if random.random() < self.crossover_rate:
                child = self._crossover(parent1, parent2)
            else:
                child = parent1
            
            # Mutation
            if random.random() < self.mutation_rate:
                child = self._create_variant(child)
            
            new_population.append(child)
        
        return new_population
    
    def _select_parent(self, population: List[str], fitness_scores: List[float]) -> str:
        """Select a parent using tournament selection."""
        tournament_size = 3
        tournament_indices = random.sample(range(len(population)), tournament_size)
        
        best_idx = max(tournament_indices, key=lambda i: fitness_scores[i])
        return population[best_idx]
    
    def _crossover(self, parent1: str, parent2: str) -> str:
        """Perform crossover between two parents."""
        words1 = parent1.split()
        words2 = parent2.split()
        
        if len(words1) < 2 or len(words2) < 2:
            return parent1
        
        # Single-point crossover
        crossover_point1 = random.randint(1, len(words1) - 1)
        crossover_point2 = random.randint(1, len(words2) - 1)
        
        child_words = words1[:crossover_point1] + words2[crossover_point2:]
        return " ".join(child_words)
    
    async def _calculate_improvement_metrics(
        self,
        original_prompt: str,
        optimized_prompt: str,
        config: OptimizationConfig,
        providers: Dict[ProviderType, BaseProvider],
        quality_scorer: QualityScorer
    ) -> Dict[str, float]:
        """Calculate improvement metrics."""
        metrics = {}
        
        # Test both prompts
        test_input = {"task": "Explain machine learning in simple terms"}
        
        try:
            # Test original prompt
            original_formatted = original_prompt.format(**test_input)
            original_response = await list(providers.values())[0].generate(
                prompt=original_formatted,
                model="gpt-3.5-turbo",
                max_tokens=100
            )
            original_quality = await quality_scorer.score_response(
                prompt=original_formatted,
                response=original_response.get("text", "")
            )
            
            # Test optimized prompt
            optimized_formatted = optimized_prompt.format(**test_input)
            optimized_response = await list(providers.values())[0].generate(
                prompt=optimized_formatted,
                model="gpt-3.5-turbo",
                max_tokens=100
            )
            optimized_quality = await quality_scorer.score_response(
                prompt=optimized_formatted,
                response=optimized_response.get("text", "")
            )
            
            # Calculate improvements
            if original_quality.overall_score > 0:
                metrics["quality_improvement"] = (
                    optimized_quality.overall_score - original_quality.overall_score
                ) / original_quality.overall_score
            
            metrics["length_change"] = (
                len(optimized_prompt.split()) - len(original_prompt.split())
            ) / len(original_prompt.split())
            
            metrics["token_efficiency"] = len(optimized_prompt) / len(original_prompt)
            
        except Exception as e:
            self.logger.warning(f"Error calculating improvement metrics: {e}")
            metrics = {"error": 1.0}
        
        return metrics 