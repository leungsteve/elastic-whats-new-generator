"""
Complete presentation generation system for Elastic What's New Generator.

This module generates full presentations following the 7-slide framework
with opening hooks, theme deep dives, cross-platform benefits, and calls to action.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict

from src.core.models import Feature, Theme, Domain, Presentation, SlideContent
from src.core.generators.content_generator import ContentGenerator
from src.core.config import config_loader


class PresentationGenerator:
    """Generates complete presentations following the Elastic framework."""

    def __init__(self, content_generator: Optional[ContentGenerator] = None):
        """Initialize with content generator."""
        self.content_generator = content_generator or ContentGenerator()

        # Load configuration
        self.config_loader = config_loader

        # Competitive differentiation points
        self.competitive_advantages = {
            "platform_vs_point": [
                "Single platform vs. 5+ point solutions",
                "Unified data model eliminates silos",
                "Cross-domain correlations impossible with separate tools"
            ],
            "performance": [
                "10x faster queries with advanced optimization",
                "Real-time analytics at petabyte scale",
                "Sub-second search across billions of documents"
            ],
            "ai_native": [
                "Built-in machine learning, not bolted on",
                "AI-powered insights out of the box",
                "Natural language interfaces for everyone"
            ]
        }

    def generate_complete_presentation(
        self,
        features: List[Feature],
        domain: Domain,
        quarter: str,
        audience: str = "mixed"
    ) -> Presentation:
        """
        Generate a complete presentation following the 7-slide framework.

        Args:
            features: List of features to include
            domain: Target domain
            quarter: Quarter identifier (e.g., "Q1-2024")
            audience: Target audience type

        Returns:
            Complete presentation with all slides
        """
        # Group features by theme
        features_by_theme = self._group_features_by_theme(features)

        # Generate all slides
        slides = []

        # 1. Opening Hook
        slides.append(self._generate_opening_hook_slide(domain, audience))

        # 2. Innovation Overview
        slides.append(self._generate_innovation_overview_slide(features_by_theme, domain))

        # 3-5. Theme Deep Dives (3 slides)
        for theme in [Theme.SIMPLIFY, Theme.OPTIMIZE, Theme.AI_INNOVATION]:
            theme_features = features_by_theme.get(theme, [])
            slides.append(self._generate_theme_deep_dive_slide(theme, theme_features, domain))

        # 6. Cross-Platform Benefits
        slides.append(self._generate_cross_platform_benefits_slide(features, domain))

        # 7. Competitive Differentiation
        slides.append(self._generate_competitive_differentiation_slide(domain))

        # 8. Business Case/ROI
        slides.append(self._generate_business_case_slide(features, domain))

        # 9. Call to Action
        slides.append(self._generate_call_to_action_slide(domain, quarter))

        # Create presentation
        presentation_id = f"pres-{domain.value}-{quarter.lower()}"
        title = self._generate_presentation_title(domain, quarter)

        return Presentation(
            id=presentation_id,
            domain=domain,
            quarter=quarter,
            title=title,
            slides=slides,
            featured_themes=list(features_by_theme.keys()),
            feature_ids=[f.id for f in features]
        )

    def _group_features_by_theme(self, features: List[Feature]) -> Dict[Theme, List[Feature]]:
        """Group features by their themes."""
        grouped = defaultdict(list)
        for feature in features:
            if feature.theme:
                grouped[feature.theme].append(feature)
            else:
                # Default to SIMPLIFY if no theme
                grouped[Theme.SIMPLIFY].append(feature)
        return dict(grouped)

    def _generate_opening_hook_slide(self, domain: Domain, audience: str) -> SlideContent:
        """Generate opening hook slide with domain-specific challenge."""
        try:
            # Get domain configuration
            domain_config = self.config_loader.get_domain_config(domain)
            hook_data = self.config_loader.get_domain_hooks(domain)

            content = f"""
## The Challenge

{hook_data['challenge']}

### Impact on Your Organization
{chr(10).join(f"• {pain}" for pain in hook_data['pain_points'])}

### The Opportunity
{hook_data['hook']}
            """.strip()

            return SlideContent(
                title="The Infrastructure Challenge",
                content=content,
                business_value="Organizations waste 40% of their infrastructure budget on inefficient solutions",
                theme=Theme.SIMPLIFY  # Opening is about simplifying the problem
            )
        except Exception as e:
            # Fallback to basic content if config fails
            content = f"""
## The Infrastructure Challenge

Modern {domain.display_name.lower()} operations face increasing complexity and cost pressures.

### Common Challenges
• Rising operational costs and complexity
• Fragmented tools and data silos
• Difficulty scaling with business growth

### The Opportunity
What if you could simplify operations while delivering better outcomes?
            """.strip()

            return SlideContent(
                title="The Infrastructure Challenge",
                content=content,
                business_value="Organizations waste 40% of their infrastructure budget on inefficient solutions",
                theme=Theme.SIMPLIFY
            )

    def _generate_innovation_overview_slide(self, features_by_theme: Dict[Theme, List[Feature]], domain: Domain) -> SlideContent:
        """Generate innovation overview slide."""
        content_parts = ["## Three Game-Changing Innovations", ""]

        for theme in [Theme.SIMPLIFY, Theme.OPTIMIZE, Theme.AI_INNOVATION]:
            feature_count = len(features_by_theme.get(theme, []))
            theme_features = features_by_theme.get(theme, [])

            content_parts.append(f"### {theme.title} - {theme.tagline}")
            if theme_features:
                # Show key feature names
                key_features = [f.name for f in theme_features[:2]]  # Top 2 features
                content_parts.append(f"*Featuring: {', '.join(key_features)}*")
            content_parts.append("")

        content_parts.extend([
            "### The Platform Advantage",
            "• **Unified Experience**: One platform, three domains, infinite possibilities",
            "• **Cross-Domain Intelligence**: Insights impossible with point solutions",
            "• **Accelerated Innovation**: Ship faster with integrated AI and automation"
        ])

        return SlideContent(
            title="Three Game-Changing Innovations",
            subtitle=f"Transforming {domain.display_name} at Scale",
            content="\n".join(content_parts),
            business_value="Platform approach delivers 3x ROI compared to point solutions",
            theme=Theme.AI_INNOVATION  # Innovation overview
        )

    def _generate_theme_deep_dive_slide(self, theme: Theme, features: List[Feature], domain: Domain) -> SlideContent:
        """Generate deep dive slide for a specific theme."""
        if not features:
            # Generate placeholder content if no features for this theme
            content = f"""
## {theme.title} - {theme.tagline}

### Coming Soon
Exciting {theme.title.lower()} innovations are being developed for {domain.display_name}.

### The Vision
• Reduce complexity and operational overhead
• Accelerate time to value
• Enable focus on business outcomes vs. infrastructure management
            """.strip()

            return SlideContent(
                title=f"{theme.title}: {theme.tagline}",
                content=content,
                business_value=f"{theme.title} innovations reduce operational costs by 30%",
                theme=theme
            )

        # Generate content for actual features
        content_parts = [f"## {theme.title} - {theme.tagline}", ""]

        for feature in features[:3]:  # Limit to top 3 features per slide
            content_parts.extend([
                f"### {feature.name}",
                f"{feature.description}",
                ""
            ])

            if feature.benefits:
                content_parts.append("**Key Benefits:**")
                content_parts.extend(f"• {benefit}" for benefit in feature.benefits[:3])
                content_parts.append("")

        # Add theme-specific business value
        theme_business_values = {
            Theme.SIMPLIFY: "Reduce operational complexity by 50% and time-to-value by 70%",
            Theme.OPTIMIZE: "Improve performance by 10x while reducing infrastructure costs by 40%",
            Theme.AI_INNOVATION: "Accelerate insights delivery by 5x with AI-powered automation"
        }

        return SlideContent(
            title=f"{theme.title}: {theme.tagline}",
            content="\n".join(content_parts),
            business_value=theme_business_values[theme],
            theme=theme
        )

    def _generate_cross_platform_benefits_slide(self, features: List[Feature], domain: Domain) -> SlideContent:
        """Generate cross-platform benefits slide."""
        if domain == Domain.ALL_DOMAINS:
            # For unified presentations, show how domains work together
            content = """
## Platform Synergies in Action

### Search + Observability
• **Performance Insights**: Search metrics feed observability dashboards
• **Smart Alerting**: Search-powered anomaly detection in monitoring data
• **Unified Dashboards**: Single pane of glass for application and search health

### Search + Security
• **Threat Intelligence**: Search across security events and threat data
• **Incident Response**: Fast search and correlation during security incidents
• **Compliance Reporting**: Automated search-based compliance documentation

### Observability + Security
• **Security Monitoring**: Observability data enriches security context
• **Threat Detection**: Performance anomalies indicate potential attacks
• **Forensic Analysis**: Combined logs provide complete incident timeline

### The Platform Effect
**1 + 1 + 1 = 10x Value**
            """.strip()
        else:
            # For domain-specific presentations, show how this domain enhances others
            domain_synergies = {
                Domain.SEARCH: """
## How Search Enhances Your Platform

### Observability Enhancement
• **Log Analysis**: Fast search across massive log volumes
• **Metric Correlation**: Search-powered investigation of performance issues
• **Dashboard Insights**: Search-based drill-downs in monitoring data

### Security Enhancement
• **Threat Hunting**: Rapid search across security events and threat intelligence
• **Incident Investigation**: Fast correlation of security events and indicators
• **Compliance Search**: Instant access to audit trails and compliance data

### Business Impact
Search capabilities amplify the value of every other platform component
                """.strip(),

                Domain.OBSERVABILITY: """
## How Observability Enhances Your Platform

### Search Enhancement
• **Performance Monitoring**: Real-time visibility into search application health
• **Capacity Planning**: Predictive insights for search infrastructure scaling
• **User Experience**: Monitor search relevance and user satisfaction metrics

### Security Enhancement
• **Security Monitoring**: Detect anomalous patterns in security data
• **Threat Response**: Monitor security tool performance and effectiveness
• **Compliance Tracking**: Continuous monitoring of security policy adherence

### Business Impact
Observability provides the intelligence layer for autonomous platform operations
                """.strip(),

                Domain.SECURITY: """
## How Security Enhances Your Platform

### Search Enhancement
• **Data Protection**: Secure search over sensitive data with field-level security
• **Access Control**: Role-based search permissions and audit trails
• **Threat Prevention**: Protect search infrastructure from security threats

### Observability Enhancement
• **Security Monitoring**: Monitor for threats in observability data
• **Compliance Tracking**: Ensure monitoring practices meet security requirements
• **Incident Response**: Security-aware observability during incidents

### Business Impact
Security provides the trust foundation for platform adoption at scale
                """.strip()
            }
            content = domain_synergies[domain]

        return SlideContent(
            title="Cross-Platform Benefits",
            subtitle="The Power of Platform Thinking",
            content=content,
            business_value="Platform approach delivers 3x better outcomes than point solutions",
            theme=Theme.OPTIMIZE  # Cross-platform is about optimization
        )

    def _generate_competitive_differentiation_slide(self, domain: Domain) -> SlideContent:
        """Generate competitive differentiation slide."""
        content = """
## Why Elastic Wins

### Platform vs. Point Solutions
• **Single Platform**: Replace 5+ vendors with one unified solution
• **Unified Data Model**: No more data silos or integration complexity
• **Cross-Domain Intelligence**: Insights impossible with separate tools

### Performance Leadership
• **10x Faster**: Advanced optimization techniques and algorithms
• **Infinite Scale**: From gigabytes to petabytes without compromise
• **Real-Time**: Sub-second response times at any scale

### AI-Native Architecture
• **Built-In ML**: Machine learning core to the platform, not bolt-on
• **Natural Language**: Ask questions in plain English, get instant answers
• **Autonomous Operations**: Self-healing, self-optimizing platform

### The Elastic Advantage
**Open Source Heritage + Enterprise Scale + Cloud Innovation**
        """.strip()

        return SlideContent(
            title="Competitive Differentiation",
            subtitle="Why Elastic Wins",
            content=content,
            business_value="Elastic customers report 5x better ROI vs. competitive solutions",
            theme=Theme.AI_INNOVATION  # Differentiation is about innovation
        )

    def _generate_business_case_slide(self, features: List[Feature], domain: Domain) -> SlideContent:
        """Generate business case and ROI slide."""
        # Calculate potential savings based on features
        all_benefits = []
        for feature in features:
            all_benefits.extend(feature.benefits)

        # Extract quantitative benefits
        cost_savings = [b for b in all_benefits if any(keyword in b.lower() for keyword in ['reduce', 'save', 'cost', '%', 'faster', 'efficiency'])]

        content = f"""
## Business Case & ROI

### Quantified Benefits
{chr(10).join(f"• {benefit}" for benefit in cost_savings[:5])}

### Financial Impact (12-Month Projection)
• **Infrastructure Costs**: 40-60% reduction through optimization
• **Operational Efficiency**: 50% reduction in time spent on maintenance
• **Developer Productivity**: 3x faster feature delivery
• **Risk Reduction**: 75% faster incident resolution

### Total Economic Impact
• **ROI**: 300-500% in first year
• **Payback Period**: 3-6 months
• **Net Present Value**: $2.5M+ for mid-size organizations

### Implementation Timeline
• **Phase 1**: Core deployment (30 days)
• **Phase 2**: Advanced features (60 days)
• **Phase 3**: Full optimization (90 days)
        """.strip()

        return SlideContent(
            title="Business Case & ROI",
            subtitle="Quantified Value Delivery",
            content=content,
            business_value="Average customer achieves 400% ROI within 12 months",
            theme=Theme.OPTIMIZE  # ROI is about optimization
        )

    def _generate_call_to_action_slide(self, domain: Domain, quarter: str) -> SlideContent:
        """Generate call to action slide."""
        content = f"""
## Next Steps

### Immediate Actions
• **Free Trial**: Start exploring these innovations today
• **Proof of Concept**: 30-day guided implementation with our experts
• **Architecture Review**: Assess your current {domain.display_name.lower()} infrastructure

### Implementation Path
• **Week 1-2**: Environment setup and data ingestion
• **Week 3-4**: Feature configuration and testing
• **Month 2**: Production deployment and optimization
• **Month 3**: Advanced features and cross-domain integration

### Support & Resources
• **Documentation**: Comprehensive guides and tutorials
• **Community**: Join 100,000+ Elastic community members
• **Professional Services**: Expert implementation and optimization support

### Ready to Transform Your {domain.display_name}?
**Contact your Elastic representative or visit elastic.co/trial**
        """.strip()

        return SlideContent(
            title="Ready to Get Started?",
            subtitle="Your Path to Success",
            content=content,
            business_value="Customers who start with a POC achieve 95% success rate in production",
            theme=Theme.SIMPLIFY  # CTA is about simplifying the next step
        )

    def _generate_presentation_title(self, domain: Domain, quarter: str) -> str:
        """Generate presentation title."""
        if domain == Domain.ALL_DOMAINS:
            return f"Elastic Platform Innovations - {quarter}"
        else:
            return f"{domain.display_name} Innovations - {quarter}"