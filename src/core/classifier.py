"""
Feature classification system for Elastic What's New Generator.

This module provides AI-powered classification of features into the three
universal innovation themes: Simplify, Optimize, and AI Innovation.
"""

import re
from typing import List, Set
from src.core.models import Feature, Theme, ClassificationResult


class FeatureClassifier:
    """Classifies features into innovation themes based on content analysis."""

    def __init__(self):
        """Initialize the classifier with theme-specific keywords."""
        self._optimization_keywords = {
            "performance", "faster", "speed", "memory", "efficient", "optimization",
            "reduce", "compression", "quantization", "cache", "latency", "throughput",
            "cpu", "bandwidth", "storage", "binary", "bbq", "acorn", "pruning"
        }

        self._simplification_keywords = {
            "automated", "automation", "autoops", "simple", "simplified", "reduce complexity",
            "single interface", "unified", "consolidate", "streamline", "centralize",
            "one-click", "self-service", "managed", "auto", "drag-and-drop", "wizard",
            "single pane", "integrated", "coherent"
        }

        self._ai_keywords = {
            "ai", "artificial intelligence", "machine learning", "ml", "llm", "agent",
            "intelligent", "smart", "inference", "model", "neural", "deep learning",
            "assistant", "copilot", "generative", "embedding", "elser", "semantic",
            "vector", "similarity", "recommendation", "prediction", "anomaly detection",
            "natural language", "nlp", "chatbot", "conversational"
        }

    def classify(self, feature: Feature) -> Theme:
        """
        Classify a feature into one of the three innovation themes.

        Args:
            feature: The feature to classify

        Returns:
            The classified theme
        """
        # Combine all feature text for analysis
        # Get content from content research if available
        research_content = ""
        if feature.content_research and feature.content_research.primary_sources:
            research_content = " ".join([
                source.content for source in feature.content_research.primary_sources
                if source.content
            ]).lower()

        text_content = " ".join([
            feature.name.lower(),
            feature.description.lower(),
            " ".join(feature.benefits).lower(),
            research_content
        ])

        # Score each theme based on keyword matches
        ai_score = self._score_theme(text_content, self._ai_keywords)
        simplify_score = self._score_theme(text_content, self._simplification_keywords)
        optimize_score = self._score_theme(text_content, self._optimization_keywords)

        # AI Innovation takes precedence as it's often the most strategic
        if ai_score > 0 and ai_score >= simplify_score and ai_score >= optimize_score:
            return Theme.AI_INNOVATION
        elif optimize_score > simplify_score:
            return Theme.OPTIMIZE
        else:
            return Theme.SIMPLIFY

    def classify_with_confidence(self, feature: Feature, model_used: str = "rule-based") -> ClassificationResult:
        """
        Classify a feature and return detailed results with confidence.

        Args:
            feature: The feature to classify
            model_used: Name of the classification model

        Returns:
            Detailed classification result
        """
        theme = self.classify(feature)

        # Calculate confidence based on keyword match strength
        # Get content from content research if available
        research_content = ""
        if feature.content_research and feature.content_research.primary_sources:
            research_content = " ".join([
                source.content for source in feature.content_research.primary_sources
                if source.content
            ]).lower()

        text_content = " ".join([
            feature.name.lower(),
            feature.description.lower(),
            " ".join(feature.benefits).lower(),
            research_content
        ])

        ai_score = self._score_theme(text_content, self._ai_keywords)
        simplify_score = self._score_theme(text_content, self._simplification_keywords)
        optimize_score = self._score_theme(text_content, self._optimization_keywords)

        total_score = ai_score + simplify_score + optimize_score
        max_score = max(ai_score, simplify_score, optimize_score)

        # Confidence is based on how clearly one theme dominates
        confidence = max_score / max(total_score, 1.0) if total_score > 0 else 0.5
        confidence = min(confidence, 1.0)

        # Generate reasoning
        reasoning = self._generate_reasoning(theme, text_content)

        return ClassificationResult(
            feature_id=feature.id,
            theme=theme,
            confidence=confidence,
            reasoning=reasoning,
            model_used=model_used
        )

    def get_optimization_keywords(self) -> Set[str]:
        """Get the set of optimization keywords."""
        return self._optimization_keywords.copy()

    def get_simplification_keywords(self) -> Set[str]:
        """Get the set of simplification keywords."""
        return self._simplification_keywords.copy()

    def get_ai_keywords(self) -> Set[str]:
        """Get the set of AI innovation keywords."""
        return self._ai_keywords.copy()

    def _score_theme(self, text: str, keywords: Set[str]) -> int:
        """Score how well text matches a theme's keywords."""
        score = 0
        for keyword in keywords:
            if keyword in text:
                score += 1
                # Bonus for exact word boundaries
                if re.search(r'\b' + re.escape(keyword) + r'\b', text):
                    score += 1
        return score

    def _generate_reasoning(self, theme: Theme, text: str) -> str:
        """Generate human-readable reasoning for the classification."""
        if theme == Theme.AI_INNOVATION:
            matched_keywords = [kw for kw in self._ai_keywords if kw in text]
            return f"Classified as AI Innovation due to keywords: {', '.join(matched_keywords[:3])}"
        elif theme == Theme.OPTIMIZE:
            matched_keywords = [kw for kw in self._optimization_keywords if kw in text]
            return f"Classified as Optimize due to keywords: {', '.join(matched_keywords[:3])}"
        else:
            matched_keywords = [kw for kw in self._simplification_keywords if kw in text]
            if matched_keywords:
                return f"Classified as Simplify due to keywords: {', '.join(matched_keywords[:3])}"
            else:
                return "Classified as Simplify (default theme when no strong signals detected)"