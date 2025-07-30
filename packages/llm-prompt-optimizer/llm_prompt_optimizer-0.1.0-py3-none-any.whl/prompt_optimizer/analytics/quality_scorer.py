"""
Quality scoring for LLM responses.
"""

import logging
from typing import Dict, Any, Optional, List
import re
from difflib import SequenceMatcher

from ..types import QualityScore


logger = logging.getLogger(__name__)


class QualityScorer:
    """
    Evaluates the quality of LLM responses.
    
    Features:
    - Relevance scoring
    - Coherence evaluation
    - Accuracy assessment
    - Safety checking
    - Custom quality metrics
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the quality scorer."""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Quality thresholds
        self.relevance_threshold = self.config.get("relevance_threshold", 0.7)
        self.coherence_threshold = self.config.get("coherence_threshold", 0.6)
        self.accuracy_threshold = self.config.get("accuracy_threshold", 0.8)
        self.safety_threshold = self.config.get("safety_threshold", 0.9)
    
    async def score_response(
        self,
        prompt: str,
        response: str,
        expected_output: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> QualityScore:
        """
        Score the quality of a response.
        
        Args:
            prompt: Input prompt
            response: Generated response
            expected_output: Expected output (if available)
            context: Additional context for scoring
            
        Returns:
            QualityScore object
        """
        # Calculate individual scores
        relevance = self._score_relevance(prompt, response, context)
        coherence = self._score_coherence(response)
        accuracy = self._score_accuracy(response, expected_output)
        safety = self._score_safety(response)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(relevance, coherence, accuracy, safety)
        
        # Generate feedback
        feedback = self._generate_feedback(relevance, coherence, accuracy, safety)
        
        return QualityScore(
            overall_score=overall_score,
            relevance=relevance,
            coherence=coherence,
            accuracy=accuracy,
            safety=safety,
            feedback=feedback
        )
    
    def _score_relevance(
        self, 
        prompt: str, 
        response: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> float:
        """Score how relevant the response is to the prompt."""
        if not response.strip():
            return 0.0
        
        # Extract key terms from prompt
        prompt_terms = self._extract_key_terms(prompt.lower())
        response_terms = self._extract_key_terms(response.lower())
        
        if not prompt_terms:
            return 0.5  # Neutral if no clear terms
        
        # Calculate term overlap
        overlap = len(set(prompt_terms) & set(response_terms))
        total_prompt_terms = len(set(prompt_terms))
        
        if total_prompt_terms == 0:
            return 0.5
        
        relevance = overlap / total_prompt_terms
        
        # Boost score for longer, more detailed responses
        if len(response.split()) > 10:
            relevance = min(relevance * 1.1, 1.0)
        
        return relevance
    
    def _score_coherence(self, response: str) -> float:
        """Score the coherence and readability of the response."""
        if not response.strip():
            return 0.0
        
        sentences = response.split('.')
        if len(sentences) < 2:
            return 0.5  # Single sentence responses
        
        # Check for logical flow
        coherence_score = 0.0
        
        # Length penalty for very short responses
        if len(response.split()) < 5:
            coherence_score -= 0.2
        
        # Grammar and structure checks
        if self._has_good_structure(response):
            coherence_score += 0.3
        
        # Check for repetitive content
        if not self._is_repetitive(response):
            coherence_score += 0.2
        
        # Check for logical connectors
        if self._has_logical_connectors(response):
            coherence_score += 0.3
        
        return max(0.0, min(1.0, coherence_score + 0.4))  # Base score of 0.4
    
    def _score_accuracy(self, response: str, expected_output: Optional[str] = None) -> float:
        """Score the accuracy of the response."""
        if expected_output:
            # Compare with expected output
            similarity = SequenceMatcher(None, response.lower(), expected_output.lower()).ratio()
            return similarity
        else:
            # Heuristic accuracy scoring
            accuracy_score = 0.5  # Base score
            
            # Check for factual indicators
            if self._has_factual_indicators(response):
                accuracy_score += 0.2
            
            # Check for confidence markers
            if self._has_confidence_markers(response):
                accuracy_score += 0.1
            
            # Penalize for uncertainty markers
            if self._has_uncertainty_markers(response):
                accuracy_score -= 0.1
            
            return max(0.0, min(1.0, accuracy_score))
    
    def _score_safety(self, response: str) -> float:
        """Score the safety of the response."""
        safety_score = 1.0
        
        # Check for harmful content
        harmful_patterns = [
            r'\b(harm|hurt|kill|attack|violence)\b',
            r'\b(hate|discriminate|racist|sexist)\b',
            r'\b(illegal|crime|criminal)\b',
        ]
        
        for pattern in harmful_patterns:
            if re.search(pattern, response.lower()):
                safety_score -= 0.3
        
        # Check for personal information
        personal_info_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b\d{4}-\d{4}-\d{4}-\d{4}\b',  # Credit card
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
        ]
        
        for pattern in personal_info_patterns:
            if re.search(pattern, response):
                safety_score -= 0.2
        
        return max(0.0, min(1.0, safety_score))
    
    def _calculate_overall_score(
        self, 
        relevance: float, 
        coherence: float, 
        accuracy: float, 
        safety: float
    ) -> float:
        """Calculate overall quality score."""
        # Weighted average
        weights = {
            'relevance': 0.3,
            'coherence': 0.2,
            'accuracy': 0.3,
            'safety': 0.2
        }
        
        overall = (
            relevance * weights['relevance'] +
            coherence * weights['coherence'] +
            accuracy * weights['accuracy'] +
            safety * weights['safety']
        )
        
        return max(0.0, min(1.0, overall))
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from text."""
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'
        }
        
        # Extract words
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out stop words and short words
        key_terms = [word for word in words if word not in stop_words and len(word) > 2]
        
        return key_terms
    
    def _has_good_structure(self, text: str) -> bool:
        """Check if text has good structure."""
        sentences = text.split('.')
        if len(sentences) < 2:
            return False
        
        # Check for varied sentence lengths
        sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
        if len(sentence_lengths) < 2:
            return False
        
        # Check for reasonable sentence length variation
        avg_length = sum(sentence_lengths) / len(sentence_lengths)
        return 3 <= avg_length <= 25
    
    def _is_repetitive(self, text: str) -> bool:
        """Check if text is repetitive."""
        words = text.lower().split()
        if len(words) < 10:
            return False
        
        # Check for repeated phrases
        word_pairs = [' '.join(words[i:i+2]) for i in range(len(words)-1)]
        unique_pairs = set(word_pairs)
        
        repetition_ratio = len(unique_pairs) / len(word_pairs)
        return repetition_ratio < 0.7
    
    def _has_logical_connectors(self, text: str) -> bool:
        """Check for logical connectors."""
        connectors = [
            'because', 'therefore', 'however', 'although', 'furthermore',
            'moreover', 'in addition', 'consequently', 'thus', 'hence'
        ]
        
        text_lower = text.lower()
        return any(connector in text_lower for connector in connectors)
    
    def _has_factual_indicators(self, text: str) -> bool:
        """Check for factual indicators."""
        indicators = [
            'according to', 'research shows', 'studies indicate',
            'evidence suggests', 'data shows', 'statistics'
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in indicators)
    
    def _has_confidence_markers(self, text: str) -> bool:
        """Check for confidence markers."""
        markers = [
            'definitely', 'certainly', 'clearly', 'obviously',
            'undoubtedly', 'without doubt', 'sure'
        ]
        
        text_lower = text.lower()
        return any(marker in text_lower for marker in markers)
    
    def _has_uncertainty_markers(self, text: str) -> bool:
        """Check for uncertainty markers."""
        markers = [
            'maybe', 'perhaps', 'possibly', 'might', 'could',
            'uncertain', 'unclear', 'not sure', 'don\'t know'
        ]
        
        text_lower = text.lower()
        return any(marker in text_lower for marker in markers)
    
    def _generate_feedback(
        self, 
        relevance: float, 
        coherence: float, 
        accuracy: float, 
        safety: float
    ) -> str:
        """Generate feedback based on scores."""
        feedback_parts = []
        
        if relevance < self.relevance_threshold:
            feedback_parts.append("Response could be more relevant to the prompt")
        
        if coherence < self.coherence_threshold:
            feedback_parts.append("Response could be more coherent and well-structured")
        
        if accuracy < self.accuracy_threshold:
            feedback_parts.append("Response accuracy could be improved")
        
        if safety < self.safety_threshold:
            feedback_parts.append("Response contains potential safety concerns")
        
        if not feedback_parts:
            return "Response meets quality standards"
        
        return "; ".join(feedback_parts) 