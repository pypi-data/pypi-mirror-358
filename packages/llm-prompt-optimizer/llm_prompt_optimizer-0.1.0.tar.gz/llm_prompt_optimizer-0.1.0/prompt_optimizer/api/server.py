"""
FastAPI server for prompt optimization API.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn

from ..core.optimizer import PromptOptimizer
from ..types import ProviderType, ExperimentConfig, OptimizationConfig
from prompt_optimizer import PromptOptimizer
from prompt_optimizer.types import OptimizerConfig


# Factory to create the FastAPI app with a config
def create_app(config: Optional[OptimizerConfig] = None):
    if config is None:
        config = OptimizerConfig()
    optimizer = PromptOptimizer(config)
    app = FastAPI(
        title="Prompt Optimizer API",
        description="A comprehensive framework for systematic A/B testing and optimization of LLM prompts by Sherin Joseph Roy",
        version="0.1.0",
        contact={
            "name": "Sherin Joseph Roy",
            "email": "sherin.joseph2217@gmail.com",
            "url": "https://github.com/Sherin-SEF-AI/prompt-optimizer.git",
        },
        license_info={
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
        },
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def root():
        return {
            "message": "Prompt Optimizer API",
            "version": "0.1.0",
            "author": "Sherin Joseph Roy",
            "email": "sherin.joseph2217@gmail.com",
            "github": "https://github.com/Sherin-SEF-AI/prompt-optimizer.git",
            "linkedin": "https://www.linkedin.com/in/sherin-roy-deepmost/",
            "docs": "/docs"
        }

    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "prompt-optimizer"}

    # Additional endpoints can be added here as you implement them in PromptOptimizer

    return app

app = create_app()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 