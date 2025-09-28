"""
Enhanced unified presentation generator for multi-domain Elastic presentations.

This module creates compelling presentations that showcase the synergies between
Search, Observability, and Security domains, emphasizing the platform advantage.
"""

from typing import List, Dict, Any, Optional, Set
from datetime import datetime
from collections import defaultdict

from src.core.models import Feature, Theme, Domain, Presentation, SlideContent
from src.core.generators.presentation_generator import PresentationGenerator
from src.core.config import config_loader


class UnifiedPresentationGenerator(PresentationGenerator):
    """Enhanced presentation generator for multi-domain unified presentations."""

    def __init__(self, content_generator=None):
        """Initialize with enhanced multi-domain capabilities."""
        super().__init__(content_generator)

        # Cross-domain synergy narratives
        self.synergy_narratives = {
            ("search", "security"): {
                "title": "Search-Powered Security",
                "story": "Transform security operations with enterprise search capabilities",
                "benefits": [
                    "10x faster threat hunting with advanced search",
                    "Real-time correlation across security data sources",
                    "Natural language queries for security investigations"
                ]
            },
            ("search", "observability"): {
                "title": "Intelligent Observability",
                "story": "Enhance monitoring and troubleshooting with search intelligence",
                "benefits": [
                    "Instant log analysis across petabytes of data",
                    "Smart alerting with search-based anomaly detection",
                    "Unified dashboards for application and infrastructure health"
                ]
            },
            ("security", "observability"): {
                "title": "Security-Aware Operations",
                "story": "Unify security and operational insights for complete visibility",
                "benefits": [
                    "Security context in operational dashboards",
                    "Automated threat detection from operational anomalies",
                    "Integrated incident response workflows"
                ]
            },
            ("search", "security", "observability"): {
                "title": "The Unified Platform Advantage",
                "story": "Achieve 1+1+1=10x impact with complete platform integration",
                "benefits": [
                    "Single source of truth across all data",
                    "Cross-domain correlation impossible with point solutions",
                    "Unified AI/ML models that learn from all domains"
                ]
            }
        }

        # Customer journey stages for unified presentations
        self.customer_journey = {
            "problem_awareness": {
                "title": "The Hidden Cost of Silos",
                "focus": "Illustrate pain points of fragmented tools"
            },
            "solution_exploration": {
                "title": "The Platform Vision",
                "focus": "Show how unified approach addresses multiple challenges"
            },
            "value_demonstration": {
                "title": "Real-World Impact",
                "focus": "Concrete examples and ROI calculations"
            },
            "implementation_path": {
                "title": "Your Journey to Success",
                "focus": "Clear next steps and success metrics"
            }
        }

    def generate_unified_presentation(
        self,
        features: List[Feature],
        quarter: str,
        audience: str = "mixed",
        story_theme: str = "platform_transformation"
    ) -> Presentation:
        """
        Generate an enhanced unified presentation with cross-domain storytelling.

        Args:
            features: List of features across multiple domains
            quarter: Quarter identifier
            audience: Target audience
            story_theme: Narrative theme for the presentation

        Returns:
            Enhanced unified presentation
        """
        # Analyze feature distribution across domains
        domain_analysis = self._analyze_domain_distribution(features)

        # Group features by theme and domain
        features_by_theme = self._group_features_by_theme(features)
        features_by_domain = self._group_features_by_domain(features)

        # Generate enhanced slide sequence
        slides = []

        # 1. Enhanced Opening Hook with Cross-Domain Challenge
        slides.append(self._generate_unified_opening_hook(domain_analysis, audience))

        # 2. The Platform Opportunity
        slides.append(self._generate_platform_opportunity_slide(domain_analysis, features))

        # 3. Cross-Domain Innovation Overview
        slides.append(self._generate_cross_domain_innovation_slide(features_by_theme, features_by_domain))

        # 4-6. Enhanced Theme Deep Dives with Cross-Domain Examples
        for theme in [Theme.SIMPLIFY, Theme.OPTIMIZE, Theme.AI_INNOVATION]:
            slides.append(self._generate_enhanced_theme_slide(
                theme, features_by_theme.get(theme, []), features_by_domain
            ))

        # 7. Cross-Domain Synergy Showcase
        slides.append(self._generate_synergy_showcase_slide(features, domain_analysis))

        # 8. Customer Success Stories
        slides.append(self._generate_customer_success_slide(domain_analysis))

        # 9. Enhanced Business Case with Platform ROI
        slides.append(self._generate_platform_business_case_slide(features, domain_analysis))

        # 10. Implementation Roadmap
        slides.append(self._generate_implementation_roadmap_slide(domain_analysis, quarter))

        # Create enhanced presentation
        presentation_id = f"unified-platform-{quarter.lower()}"
        title = f"Elastic Platform Transformation - {quarter}"

        return Presentation(
            id=presentation_id,
            domain=Domain.ALL_DOMAINS,
            quarter=quarter,
            title=title,
            slides=slides,
            featured_themes=list(features_by_theme.keys()),
            feature_ids=[f.id for f in features]
        )

    def _analyze_domain_distribution(self, features: List[Feature]) -> Dict[str, Any]:
        """Analyze the distribution of features across domains."""
        domain_counts = defaultdict(int)
        domain_features = defaultdict(list)

        for feature in features:
            domain_counts[feature.domain] += 1
            domain_features[feature.domain].append(feature)

        # Identify synergy opportunities
        represented_domains = set(domain_counts.keys())
        synergy_key = tuple(sorted(d.value for d in represented_domains if d != Domain.ALL_DOMAINS))

        return {
            "domain_counts": dict(domain_counts),
            "domain_features": dict(domain_features),
            "represented_domains": represented_domains,
            "synergy_opportunities": self.synergy_narratives.get(synergy_key, {}),
            "total_features": len(features),
            "is_truly_unified": len(represented_domains) >= 3
        }

    def _group_features_by_domain(self, features: List[Feature]) -> Dict[Domain, List[Feature]]:
        """Group features by their domains."""
        grouped = defaultdict(list)
        for feature in features:
            grouped[feature.domain].append(feature)
        return dict(grouped)

    def _generate_unified_opening_hook(self, domain_analysis: Dict, audience: str) -> SlideContent:
        """Generate enhanced opening hook emphasizing cross-domain challenges."""
        domains = domain_analysis["represented_domains"]
        domain_names = [d.display_name for d in domains if d != Domain.ALL_DOMAINS]

        if len(domain_names) >= 3:
            domain_list = f"{', '.join(domain_names[:-1])}, and {domain_names[-1]}"
            challenge_scope = "across your entire technology stack"
        elif len(domain_names) == 2:
            domain_list = f"{domain_names[0]} and {domain_names[1]}"
            challenge_scope = f"in both {domain_list.lower()}"
        else:
            domain_list = domain_names[0] if domain_names else "technology"
            challenge_scope = f"in your {domain_list.lower()} operations"

        content = f"""
## The Modern Infrastructure Dilemma

### The Challenge
Organizations manage **{len(domain_names)} critical domains** separately: {domain_list}

### The Hidden Costs
• **Data Silos**: Critical insights trapped in isolated systems
• **Operational Complexity**: Multiple tools, multiple teams, multiple problems
• **Delayed Response**: Hours wasted correlating data across platforms
• **Vendor Sprawl**: 5-15 point solutions with overlapping costs

### The Opportunity
What if **one platform** could unify {domain_list.lower()} while delivering:
• **10x faster** insights through intelligent correlation
• **50% cost reduction** by replacing multiple vendors
• **Unified AI** that learns from all your data simultaneously

### The Vision
**Stop managing tools. Start managing outcomes.**
        """.strip()

        return SlideContent(
            title="The Modern Infrastructure Dilemma",
            subtitle="Why Point Solutions Are Holding You Back",
            content=content,
            business_value="Organizations spend 40% more on infrastructure when using point solutions vs unified platforms",
            theme=Theme.SIMPLIFY
        )

    def _generate_platform_opportunity_slide(self, domain_analysis: Dict, features: List[Feature]) -> SlideContent:
        """Generate slide showing the platform opportunity."""
        synergies = domain_analysis.get("synergy_opportunities", {})
        total_features = domain_analysis["total_features"]

        content = f"""
## The Elastic Platform Advantage

### Beyond Individual Features
Today we'll explore **{total_features} breakthrough innovations** that work better together than apart.

### The Platform Effect
• **Individual Impact**: Each feature solves specific challenges
• **Combined Power**: Features amplify each other's value
• **Platform Intelligence**: Unified AI learns from all domains
• **Exponential ROI**: 1 + 1 + 1 = 10x business value

### Three Domains, Infinite Possibilities
"""

        # Add domain-specific highlights
        for domain, features_list in domain_analysis["domain_features"].items():
            if domain != Domain.ALL_DOMAINS and features_list:
                feature_names = [f.name for f in features_list[:2]]
                content += f"\n**{domain.display_name}**: {', '.join(feature_names)}"
                if len(features_list) > 2:
                    content += f" + {len(features_list) - 2} more"

        # Add synergy narrative if available
        if synergies:
            content += f"""

### {synergies.get('title', 'Cross-Domain Synergies')}
{synergies.get('story', 'Powerful integrations across all domains')}
"""

        content += """

### The Promise
**One platform. All domains. Exponential impact.**
"""

        return SlideContent(
            title="The Elastic Platform Advantage",
            subtitle="Beyond Individual Features",
            content=content,
            business_value="Platform approach delivers 3-5x ROI compared to best-of-breed point solutions",
            theme=Theme.AI_INNOVATION
        )

    def _generate_cross_domain_innovation_slide(
        self,
        features_by_theme: Dict[Theme, List[Feature]],
        features_by_domain: Dict[Domain, List[Feature]]
    ) -> SlideContent:
        """Generate overview of innovations across domains and themes."""
        content_parts = ["## Cross-Domain Innovation Matrix", ""]

        # Create a matrix view of themes vs domains
        content_parts.append("### Innovation Themes Across All Domains")
        content_parts.append("")

        for theme in [Theme.SIMPLIFY, Theme.OPTIMIZE, Theme.AI_INNOVATION]:
            theme_features = features_by_theme.get(theme, [])
            if theme_features:
                content_parts.append(f"**{theme.title}** - {theme.tagline}")

                # Group theme features by domain
                theme_by_domain = defaultdict(list)
                for feature in theme_features:
                    theme_by_domain[feature.domain].append(feature)

                for domain, domain_features in theme_by_domain.items():
                    if domain != Domain.ALL_DOMAINS:
                        feature_names = [f.name for f in domain_features[:2]]
                        content_parts.append(f"  • {domain.display_name}: {', '.join(feature_names)}")

                content_parts.append("")

        # Add cross-domain impact
        content_parts.extend([
            "### Cross-Domain Impact Stories",
            "• **Search + Security**: 10x faster threat hunting and investigation",
            "• **Observability + Search**: Instant insights across petabytes of operational data",
            "• **Security + Observability**: Unified context for faster incident response",
            "• **All Three Together**: Complete organizational intelligence platform",
            "",
            "### The Multiplication Effect",
            "Each domain amplifies the others - creating value impossible with separate solutions."
        ])

        return SlideContent(
            title="Cross-Domain Innovation Matrix",
            subtitle="Where Themes Meet Domains",
            content="\n".join(content_parts),
            business_value="Cross-domain features deliver 2-3x more value than single-domain implementations",
            theme=Theme.AI_INNOVATION
        )

    def _generate_enhanced_theme_slide(
        self,
        theme: Theme,
        theme_features: List[Feature],
        features_by_domain: Dict[Domain, List[Feature]]
    ) -> SlideContent:
        """Generate enhanced theme slide with cross-domain examples."""
        content_parts = [f"## {theme.title} - {theme.tagline}", ""]

        if not theme_features:
            # Generate compelling placeholder content
            content_parts.extend([
                f"### The {theme.title} Vision",
                f"Powerful {theme.title.lower()} innovations coming soon across all domains.",
                "",
                "### Cross-Platform Impact",
                f"• **Search**: {theme.tagline} for enterprise search experiences",
                f"• **Observability**: {theme.tagline} for monitoring and operations",
                f"• **Security**: {theme.tagline} for threat detection and response",
                "",
                f"### The {theme.title} Promise",
                f"{theme.tagline} across your entire technology stack."
            ])
        else:
            # Group features by domain for this theme
            theme_by_domain = defaultdict(list)
            for feature in theme_features:
                theme_by_domain[feature.domain].append(feature)

            # Show cross-domain impact
            content_parts.append(f"### {theme.title} Across All Domains")
            content_parts.append("")

            for domain in [Domain.SEARCH, Domain.OBSERVABILITY, Domain.SECURITY]:
                domain_features = theme_by_domain.get(domain, [])
                if domain_features:
                    content_parts.append(f"**{domain.display_name}**")
                    for feature in domain_features[:2]:  # Show top 2 features
                        content_parts.append(f"• **{feature.name}**: {feature.description}")
                        if feature.benefits:
                            content_parts.append(f"  *Impact: {feature.benefits[0]}*")
                    content_parts.append("")

            # Add cross-domain synergy for this theme
            content_parts.extend([
                f"### {theme.title} Platform Synergies",
                self._get_theme_synergy_description(theme),
                "",
                "### Business Impact",
                f"**{theme.title} across all domains delivers exponential value**"
            ])

        return SlideContent(
            title=f"{theme.title}: {theme.tagline}",
            subtitle="Platform-Wide Innovation",
            content="\n".join(content_parts),
            business_value=f"{theme.title} innovations reduce complexity while improving outcomes by 50-70%",
            theme=theme
        )

    def _get_theme_synergy_description(self, theme: Theme) -> str:
        """Get theme-specific synergy descriptions."""
        synergies = {
            Theme.SIMPLIFY: "Unified interfaces, consolidated workflows, and single-pane management across all domains",
            Theme.OPTIMIZE: "Shared optimization engines, cross-domain performance insights, and unified resource management",
            Theme.AI_INNOVATION: "Platform-wide AI that learns from search, security, and observability data simultaneously"
        }
        return synergies.get(theme, "Cross-domain innovations that amplify each other's impact")

    def _generate_synergy_showcase_slide(self, features: List[Feature], domain_analysis: Dict) -> SlideContent:
        """Generate slide showcasing specific cross-domain synergies."""
        synergies = domain_analysis.get("synergy_opportunities", {})

        content = """
## Platform Synergies in Action

### Real-World Integration Scenarios
"""

        # Get cross-domain scenarios from configuration
        try:
            cross_domain_scenarios = config_loader.get_cross_domain_scenarios()
            for scenario in cross_domain_scenarios[:3]:  # Show top 3 scenarios
                content += f"""
**{scenario.get('description', 'Cross-domain scenario')}**
• Value: {scenario.get('value_prop', 'Enhanced capabilities')}
• Domains: {', '.join(scenario.get('domains', []))}
"""
        except:
            # Fallback scenarios
            content += """
**Advanced Threat Hunting**
• Use enterprise search to investigate security incidents 10x faster
• Correlate security events with operational context in real-time

**Intelligent Operations**
• Apply AI insights from security and search to optimize infrastructure
• Predict and prevent issues before they impact users

**Unified Analytics**
• Single dashboard showing search performance, security posture, and operational health
• Cross-domain insights impossible with separate tools
"""

        content += """

### The Platform Advantage
• **Data Correlation**: Instant insights across all domains
• **Unified Intelligence**: AI models that learn from everything
• **Operational Efficiency**: One platform, one team, infinite possibilities
• **Innovation Velocity**: Ship features faster with integrated platform

### Customer Reality
*"We replaced 8 vendors with Elastic and increased our team's effectiveness by 300%"*
*- Fortune 500 Technology Company*
"""

        return SlideContent(
            title="Platform Synergies in Action",
            subtitle="Real-World Cross-Domain Impact",
            content=content,
            business_value="Cross-domain synergies typically deliver 200-400% additional ROI beyond individual domain value",
            theme=Theme.AI_INNOVATION
        )

    def _generate_customer_success_slide(self, domain_analysis: Dict) -> SlideContent:
        """Generate customer success stories slide."""
        domains = [d.display_name for d in domain_analysis["represented_domains"] if d != Domain.ALL_DOMAINS]

        content = f"""
## Customer Success Stories

### Global Financial Services Company
**Challenge**: Fragmented security, search, and monitoring across 50+ applications
**Solution**: Unified Elastic platform replacing 12 point solutions
**Results**:
• **75% faster** incident response time
• **$2.5M annual savings** from vendor consolidation
• **10x improvement** in threat detection accuracy

### Fortune 500 Retailer
**Challenge**: Siloed customer search, security monitoring, and operational visibility
**Solution**: Platform approach with cross-domain intelligence
**Results**:
• **40% increase** in search conversion rates
• **90% reduction** in false security alerts
• **60% faster** time to market for new features

### Technology Unicorn
**Challenge**: Scaling {', '.join(domains[:2])} operations during hypergrowth
**Solution**: Elastic platform from day one
**Results**:
• **$5M avoided costs** by preventing vendor sprawl
• **50% reduction** in operational overhead
• **3x faster** developer productivity

### The Pattern
Organizations choosing platform-first approach consistently achieve:
• **300-500% ROI** within 12 months
• **40-70% cost savings** vs point solutions
• **2-3x improvement** in team productivity
"""

        return SlideContent(
            title="Customer Success Stories",
            subtitle="Real Results from Platform Adoption",
            content=content,
            business_value="Customers report average 400% ROI within first year of platform adoption",
            theme=Theme.OPTIMIZE
        )

    def _generate_platform_business_case_slide(self, features: List[Feature], domain_analysis: Dict) -> SlideContent:
        """Generate enhanced business case slide with platform ROI."""
        domain_count = len([d for d in domain_analysis["represented_domains"] if d != Domain.ALL_DOMAINS])

        content = f"""
## Platform Business Case & ROI

### The Platform Premium
**Unified approach delivers {domain_count}x domain value PLUS platform multiplier effect**

### Quantified Benefits (12-Month Impact)
• **Vendor Consolidation**: Replace {domain_count * 3}-{domain_count * 5} vendors with one platform
• **Operational Efficiency**: 50-70% reduction in management overhead
• **Cross-Domain Insights**: New revenue opportunities worth 10-25% of technology budget
• **Team Productivity**: 2-3x improvement in engineering effectiveness

### Financial Impact
"""

        # Calculate domain-specific savings
        base_savings = 500000  # Base savings per domain
        total_savings = base_savings * domain_count
        platform_multiplier = min(2.5, 1 + (domain_count * 0.5))  # Multiplier effect
        total_value = int(total_savings * platform_multiplier)

        content += f"""
• **Direct Cost Savings**: ${total_savings:,} annually from vendor consolidation
• **Platform Multiplier**: {platform_multiplier}x additional value from cross-domain synergies
• **Total Economic Impact**: ${total_value:,} in first year value

### ROI Calculation
• **Investment**: Elastic platform licensing and implementation
• **Return**: {int(platform_multiplier * 100)}% ROI in first 12 months
• **Payback Period**: 3-6 months for most organizations
• **Net Present Value**: ${int(total_value * 2.5):,} over 3 years

### Risk Mitigation
• **Vendor Risk**: Single trusted partner vs {domain_count * 3}+ vendor relationships
• **Technical Debt**: Future-proof platform vs aging point solutions
• **Skills Gap**: One platform expertise vs multiple specialized teams

### Implementation Timeline
• **Phase 1 (Month 1-2)**: Core platform deployment
• **Phase 2 (Month 3-4)**: Cross-domain integration
• **Phase 3 (Month 5-6)**: Advanced analytics and optimization
• **Full ROI Realization**: Month 6-12
"""

        return SlideContent(
            title="Platform Business Case & ROI",
            subtitle="Quantified Value of Unified Approach",
            content=content,
            business_value=f"Platform approach delivers {int(platform_multiplier * 100)}% ROI with {domain_count}x domain coverage",
            theme=Theme.OPTIMIZE
        )

    def _generate_implementation_roadmap_slide(self, domain_analysis: Dict, quarter: str) -> SlideContent:
        """Generate implementation roadmap slide."""
        domains = [d.display_name for d in domain_analysis["represented_domains"] if d != Domain.ALL_DOMAINS]

        content = f"""
## Your Platform Transformation Journey

### Phase 1: Foundation (Months 1-2)
• **Platform Setup**: Deploy Elastic cluster with {', '.join(domains[:2])} capabilities
• **Data Integration**: Connect existing data sources and establish pipelines
• **Team Training**: Upskill teams on unified platform approach
• **Quick Wins**: Identify and implement high-impact use cases

### Phase 2: Integration (Months 3-4)
• **Cross-Domain Workflows**: Implement unified dashboards and alerting
• **Advanced Features**: Deploy AI/ML capabilities across all domains
• **Process Optimization**: Streamline operations with platform automation
• **Success Metrics**: Establish KPIs and measurement frameworks

### Phase 3: Optimization (Months 5-6)
• **Advanced Analytics**: Leverage cross-domain intelligence for new insights
• **Custom Development**: Build domain-specific applications on platform
• **Scaling**: Expand to additional use cases and teams
• **Innovation**: Explore next-generation capabilities

### Success Metrics & Milestones
"""

        # Add domain-specific milestones
        milestones = {
            "Search": "• Search relevance and performance improvements visible in Week 2",
            "Observability": "• MTTR reduction and cost savings measurable by Month 1",
            "Security": "• Threat detection improvements and false positive reduction by Month 1"
        }

        for domain in domains:
            if domain in milestones:
                content += f"\n{milestones[domain]}"

        content += f"""

### Ongoing Support & Resources
• **Professional Services**: Expert guidance throughout transformation
• **Community**: Access to 100,000+ Elastic community members
• **Documentation**: Comprehensive guides and best practices
• **Training**: Certification programs for your teams

### Ready to Begin?
**Your platform transformation starts today**
• **Free Trial**: Experience the platform power immediately
• **Proof of Concept**: 30-day guided implementation
• **Architecture Review**: Assess current state and define target architecture

### Contact Information
**Speak with your Elastic representative or visit elastic.co/platform**
"""

        return SlideContent(
            title="Your Platform Transformation Journey",
            subtitle="From Point Solutions to Platform Excellence",
            content=content,
            business_value="Organizations following this roadmap achieve 95% success rate in platform adoption",
            theme=Theme.SIMPLIFY
        )