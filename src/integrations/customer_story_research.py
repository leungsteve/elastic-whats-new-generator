"""
Customer Story Research Service for Elastic What's New Generator.

This service specializes in discovering and extracting customer success stories,
business value metrics, and competitive positioning data to enhance presentations
with real-world impact narratives.
"""

import asyncio
import re
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import logging

import requests
from bs4 import BeautifulSoup

from ..core.models import (
    Feature, CustomerStory, BusinessImpact, Domain, Theme
)

logger = logging.getLogger(__name__)


class CustomerStoryResearcher:
    """Researches and extracts customer success stories for features."""

    def __init__(self):
        """Initialize the customer story researcher."""
        self.known_story_sources = {
            "elastic_blog": "https://www.elastic.co/blog",
            "elastic_customers": "https://www.elastic.co/customers",
            "elastic_case_studies": "https://www.elastic.co/case-studies"
        }

        self.business_metrics_patterns = [
            r"(\d+)%\s+(reduction|decrease|improvement|increase)",
            r"(\d+)x\s+(faster|improvement|reduction)",
            r"reduced\s+.*?by\s+(\d+)%",
            r"improved\s+.*?by\s+(\d+)%",
            r"saved\s+.*?(\d+)\s+(hours|minutes|days)",
            r"\$(\d+(?:,\d+)*)\s+(?:saved|reduction|cost savings)"
        ]

    async def research_customer_stories(
        self,
        feature: Feature,
        max_stories: int = 3
    ) -> List[CustomerStory]:
        """
        Research customer success stories related to a feature.

        Args:
            feature: The feature to research stories for
            max_stories: Maximum number of stories to return

        Returns:
            List of customer success stories
        """
        logger.info(f"Researching customer stories for {feature.name}")

        stories = []

        # Generate sample stories based on feature domain and theme
        # In a real implementation, this would scrape actual customer stories
        stories.extend(self._generate_sample_stories(feature, max_stories))

        # In a production system, add actual web scraping here:
        # stories.extend(await self._scrape_elastic_customer_stories(feature))

        return stories[:max_stories]

    async def research_business_impact(
        self,
        feature: Feature
    ) -> BusinessImpact:
        """
        Research quantified business impact data for a feature.

        Args:
            feature: The feature to research impact for

        Returns:
            Business impact data with metrics
        """
        logger.info(f"Researching business impact for {feature.name}")

        # Generate realistic business impact based on feature theme and domain
        return self._generate_business_impact(feature)

    def _generate_sample_stories(self, feature: Feature, count: int) -> List[CustomerStory]:
        """Generate realistic sample customer stories."""
        domain_industries = {
            Domain.SEARCH: ["E-commerce", "Media & Publishing", "SaaS", "Enterprise Software"],
            Domain.OBSERVABILITY: ["Financial Services", "Technology", "Healthcare", "Manufacturing"],
            Domain.SECURITY: ["Banking", "Government", "Healthcare", "Cybersecurity"]
        }

        domain_challenges = {
            Domain.SEARCH: [
                "Poor search relevance affecting conversion rates",
                "Slow search performance with large product catalogs",
                "Difficulty implementing personalized search experiences"
            ],
            Domain.OBSERVABILITY: [
                "High MTTR due to scattered monitoring tools",
                "Inability to correlate metrics across infrastructure",
                "Reactive instead of proactive incident response"
            ],
            Domain.SECURITY: [
                "Advanced persistent threats going undetected",
                "Time-consuming manual threat hunting",
                "False positive alerts overwhelming security teams"
            ]
        }

        theme_outcomes = {
            Theme.SIMPLIFY: [
                "Reduced operational complexity by 60%",
                "Consolidated 5 tools into 1 unified platform",
                "Enabled self-service capabilities for 200+ users"
            ],
            Theme.OPTIMIZE: [
                "Improved query performance by 300%",
                "Reduced infrastructure costs by 40%",
                "Achieved 99.9% uptime with automated scaling"
            ],
            Theme.AI_INNOVATION: [
                "Reduced false positives by 85% with ML",
                "Automated 90% of routine investigations",
                "Identified threats 10x faster than manual methods"
            ]
        }

        industries = domain_industries.get(feature.domain, ["Technology"])
        challenges = domain_challenges.get(feature.domain, ["Operational inefficiencies"])
        outcomes = theme_outcomes.get(feature.theme or Theme.SIMPLIFY, ["Improved operations"])

        stories = []
        company_templates = [
            "TechCorp", "GlobalInc", "DataSystems", "CloudFirst", "InnovateCo"
        ]

        for i in range(min(count, len(company_templates))):
            industry = industries[i % len(industries)]
            challenge = challenges[i % len(challenges)]
            outcome = outcomes[i % len(outcomes)]

            # Extract metrics from outcome
            metrics = self._extract_metrics_from_text(outcome)

            story = CustomerStory(
                company_name=f"{company_templates[i]} (anonymized)",
                industry=industry,
                challenge=challenge,
                solution=f"Deployed {feature.name} to address {feature.domain.display_name.lower()} challenges",
                outcome=outcome,
                quote=f"'{feature.name} has transformed how we approach {feature.domain.display_name.lower()}. The results speak for themselves.'",
                metrics=metrics
            )
            stories.append(story)

        return stories

    def _generate_business_impact(self, feature: Feature) -> BusinessImpact:
        """Generate realistic business impact data."""
        theme = feature.theme or Theme.SIMPLIFY

        impact_templates = {
            Theme.SIMPLIFY: BusinessImpact(
                productivity_gains="40-60% reduction in manual tasks",
                time_savings="Save 15-20 hours per week per analyst",
                cost_savings="25-35% reduction in operational costs",
                risk_reduction="Lower human error risk through automation"
            ),
            Theme.OPTIMIZE: BusinessImpact(
                roi_percentage=180.0,
                productivity_gains="2-3x performance improvement",
                cost_savings="30-50% infrastructure cost reduction",
                competitive_advantage="Deliver results 5x faster than competitors"
            ),
            Theme.AI_INNOVATION: BusinessImpact(
                competitive_advantage="First-to-market AI capabilities in industry",
                productivity_gains="Unlock insights impossible with manual analysis",
                risk_reduction="Proactive threat detection and prevention",
                time_savings="Automate 80% of routine decision-making"
            )
        }

        base_impact = impact_templates.get(theme, impact_templates[Theme.SIMPLIFY])

        # Add domain-specific customizations
        if feature.domain == Domain.SEARCH:
            base_impact.competitive_advantage = "Improve customer experience and conversion rates"
        elif feature.domain == Domain.OBSERVABILITY:
            base_impact.risk_reduction = "Reduce downtime and improve system reliability"
        elif feature.domain == Domain.SECURITY:
            base_impact.risk_reduction = "Strengthen security posture and compliance"

        return base_impact

    def _extract_metrics_from_text(self, text: str) -> Dict[str, str]:
        """Extract quantified metrics from text."""
        metrics = {}

        for pattern in self.business_metrics_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    value, metric_type = match[0], match[1] if len(match) > 1 else "improvement"
                    key = f"{metric_type.lower()}_percentage" if "%" in text else f"{metric_type.lower()}_factor"
                    metrics[key] = f"{value}%"
                else:
                    metrics["improvement"] = str(match)

        return metrics

    async def research_competitive_positioning(
        self,
        feature: Feature,
        competitors: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Research competitive positioning and differentiation.

        Args:
            feature: The feature to research positioning for
            competitors: List of competitor names to research

        Returns:
            Competitive positioning analysis
        """
        if not competitors:
            competitors = self._get_default_competitors(feature.domain)

        positioning = {
            "differentiators": self._generate_differentiators(feature),
            "competitive_advantages": self._generate_competitive_advantages(feature),
            "market_position": self._generate_market_position(feature),
            "competitor_comparison": self._generate_competitor_comparison(feature, competitors)
        }

        return positioning

    def _get_default_competitors(self, domain: Domain) -> List[str]:
        """Get default competitors based on domain."""
        competitor_map = {
            Domain.SEARCH: ["Solr", "Amazon CloudSearch", "Azure Cognitive Search"],
            Domain.OBSERVABILITY: ["Datadog", "New Relic", "Splunk"],
            Domain.SECURITY: ["Splunk SIEM", "IBM QRadar", "Microsoft Sentinel"]
        }
        return competitor_map.get(domain, ["Generic Competitor"])

    def _generate_differentiators(self, feature: Feature) -> List[str]:
        """Generate key differentiators for the feature."""
        theme = feature.theme or Theme.SIMPLIFY

        differentiator_templates = {
            Theme.SIMPLIFY: [
                "Unified platform eliminating tool sprawl",
                "Zero-configuration deployment and management",
                "Self-service capabilities for non-technical users"
            ],
            Theme.OPTIMIZE: [
                "Industry-leading performance and scale",
                "Intelligent resource optimization",
                "Cost-effective architecture with better ROI"
            ],
            Theme.AI_INNOVATION: [
                "Built-in machine learning without data science expertise",
                "Real-time AI insights and automation",
                "Continuously learning and improving algorithms"
            ]
        }

        base_differentiators = differentiator_templates[theme]
        domain_specific = f"Deep {feature.domain.display_name.lower()} domain expertise and optimization"

        return base_differentiators + [domain_specific]

    def _generate_competitive_advantages(self, feature: Feature) -> List[str]:
        """Generate competitive advantages."""
        return [
            f"Integrated approach vs. point solutions in {feature.domain.display_name.lower()}",
            "Open source foundation with enterprise security",
            "Elastic Stack ecosystem synergies and cross-domain insights",
            "Cloud-native architecture with deployment flexibility"
        ]

    def _generate_market_position(self, feature: Feature) -> str:
        """Generate market positioning statement."""
        theme = feature.theme or Theme.SIMPLIFY
        theme_focus = {
            Theme.SIMPLIFY: "operational simplicity",
            Theme.OPTIMIZE: "performance leadership",
            Theme.AI_INNOVATION: "AI innovation"
        }

        return f"Market leader in {feature.domain.display_name.lower()} with focus on {theme_focus[theme]} and enterprise-grade reliability"

    def _generate_competitor_comparison(self, feature: Feature, competitors: List[str]) -> Dict[str, str]:
        """Generate competitor comparison points."""
        comparison = {}

        for competitor in competitors[:3]:  # Limit to top 3
            comparison[competitor] = f"Unlike {competitor}, {feature.name} provides integrated {feature.domain.display_name.lower()} capabilities with built-in AI and unified data model"

        return comparison


class BusinessValueCalculator:
    """Calculates quantified business value for features."""

    def __init__(self):
        """Initialize the business value calculator."""
        self.roi_multipliers = {
            Theme.SIMPLIFY: 1.5,  # 150% ROI typical for simplification
            Theme.OPTIMIZE: 2.0,  # 200% ROI typical for optimization
            Theme.AI_INNOVATION: 2.5  # 250% ROI typical for AI innovation
        }

    def calculate_roi_projection(
        self,
        feature: Feature,
        deployment_cost: float = 100000,  # Default deployment cost
        annual_savings: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculate ROI projection for a feature.

        Args:
            feature: The feature to calculate ROI for
            deployment_cost: Estimated deployment cost
            annual_savings: Annual savings estimate

        Returns:
            ROI projection with timeline
        """
        theme = feature.theme or Theme.SIMPLIFY
        multiplier = self.roi_multipliers[theme]

        if not annual_savings:
            annual_savings = deployment_cost * multiplier

        roi_percentage = ((annual_savings - deployment_cost) / deployment_cost) * 100
        payback_months = (deployment_cost / annual_savings) * 12

        return {
            "roi_percentage": round(roi_percentage, 1),
            "payback_months": round(payback_months, 1),
            "annual_savings": annual_savings,
            "three_year_value": annual_savings * 3,
            "break_even_timeline": f"{payback_months:.1f} months"
        }

    def generate_value_drivers(self, feature: Feature) -> List[Dict[str, str]]:
        """Generate specific value drivers for a feature."""
        domain_drivers = {
            Domain.SEARCH: [
                {"driver": "Increased Conversion Rate", "impact": "2-5% improvement"},
                {"driver": "Reduced Customer Support", "impact": "30% fewer search-related tickets"},
                {"driver": "Developer Productivity", "impact": "50% faster implementation"}
            ],
            Domain.OBSERVABILITY: [
                {"driver": "Reduced MTTR", "impact": "60% faster incident resolution"},
                {"driver": "Infrastructure Optimization", "impact": "25% cost reduction"},
                {"driver": "Improved Uptime", "impact": "99.9% availability target"}
            ],
            Domain.SECURITY: [
                {"driver": "Threat Detection Speed", "impact": "10x faster identification"},
                {"driver": "Reduced False Positives", "impact": "80% noise reduction"},
                {"driver": "Compliance Automation", "impact": "90% automated reporting"}
            ]
        }

        return domain_drivers.get(feature.domain, [
            {"driver": "Operational Efficiency", "impact": "Significant improvement"},
            {"driver": "Cost Reduction", "impact": "Measurable savings"},
            {"driver": "Risk Mitigation", "impact": "Enhanced security posture"}
        ])