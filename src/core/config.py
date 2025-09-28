"""
Configuration loader for domain-specific content generation.

This module loads and parses YAML configuration files containing
domain personas, challenges, templates, and content settings.
"""

import yaml
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass

from src.core.models import Domain, Theme


@dataclass
class PersonaConfig:
    """Configuration for a domain persona."""
    name: str
    title: str
    pain_points: List[str]
    goals: List[str]


@dataclass
class DomainConfig:
    """Configuration for a specific domain."""
    display_name: str
    description: str
    personas: List[PersonaConfig]
    common_challenges: List[str]
    sample_data_types: List[Dict[str, Any]]
    competitive_advantages: List[str]


@dataclass
class PresentationTemplate:
    """Configuration for presentation templates."""
    structure: List[str]


@dataclass
class LabTemplate:
    """Configuration for lab templates."""
    estimated_time: int
    prerequisites: List[str]
    complexity: str


@dataclass
class ContentSettings:
    """Configuration for content generation settings."""
    slide_length: Dict[str, int]
    audience_styles: Dict[str, Dict[str, str]]


class ConfigLoader:
    """Loads and manages domain configuration from YAML files."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize with optional config path."""
        if config_path is None:
            # Default to config/domains.yaml in project root
            self.config_path = Path(__file__).parent.parent.parent / "config" / "domains.yaml"
        else:
            self.config_path = config_path

        self._config_data: Optional[Dict[str, Any]] = None
        self._domains: Optional[Dict[Domain, DomainConfig]] = None

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if self._config_data is None:
            try:
                with open(self.config_path, 'r', encoding='utf-8') as file:
                    self._config_data = yaml.safe_load(file)
            except FileNotFoundError:
                raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML in configuration file: {e}")

        return self._config_data

    def get_domain_config(self, domain: Domain) -> DomainConfig:
        """Get configuration for a specific domain."""
        if self._domains is None:
            self._load_domains()

        if domain not in self._domains:
            raise ValueError(f"No configuration found for domain: {domain}")

        return self._domains[domain]

    def get_all_domain_configs(self) -> Dict[Domain, DomainConfig]:
        """Get configurations for all domains."""
        if self._domains is None:
            self._load_domains()

        return self._domains.copy()

    def get_presentation_template(self, template_name: str) -> PresentationTemplate:
        """Get presentation template configuration."""
        config = self.load_config()
        templates = config.get('presentation_templates', {})

        if template_name not in templates:
            raise ValueError(f"Presentation template not found: {template_name}")

        template_data = templates[template_name]
        return PresentationTemplate(
            structure=template_data.get('structure', [])
        )

    def get_lab_template(self, difficulty: str) -> LabTemplate:
        """Get lab template for specific difficulty level."""
        config = self.load_config()
        lab_templates = config.get('lab_templates', {})
        difficulty_levels = lab_templates.get('difficulty_levels', {})

        if difficulty not in difficulty_levels:
            raise ValueError(f"Lab difficulty template not found: {difficulty}")

        template_data = difficulty_levels[difficulty]
        return LabTemplate(
            estimated_time=template_data.get('estimated_time', 30),
            prerequisites=template_data.get('prerequisites', []),
            complexity=template_data.get('complexity', 'Unknown')
        )

    def get_content_settings(self) -> ContentSettings:
        """Get content generation settings."""
        config = self.load_config()
        settings_data = config.get('content_settings', {})

        return ContentSettings(
            slide_length=settings_data.get('slide_length', {'short': 50, 'medium': 100, 'long': 200}),
            audience_styles=settings_data.get('audience_styles', {})
        )

    def get_domain_hooks(self, domain: Domain) -> Dict[str, Any]:
        """Get domain-specific opening hooks and challenges."""
        domain_config = self.get_domain_config(domain)

        # Extract pain points from personas for hooks
        all_pain_points = []
        for persona in domain_config.personas:
            all_pain_points.extend(persona.pain_points)

        # Create hook based on domain description and challenges
        challenge = f"{domain_config.description} faces critical operational challenges"
        hook = f"What if you could transform {domain_config.display_name.lower()} operations and deliver breakthrough results?"

        return {
            "challenge": challenge,
            "pain_points": all_pain_points[:3],  # Top 3 pain points
            "hook": hook
        }

    def get_cross_domain_scenarios(self) -> List[Dict[str, Any]]:
        """Get cross-domain integration scenarios."""
        config = self.load_config()
        all_domains_config = config.get('domains', {}).get('all_domains', {})

        return all_domains_config.get('cross_domain_scenarios', [])

    def get_competitive_advantages(self, domain: Domain) -> List[str]:
        """Get competitive advantages for a specific domain."""
        domain_config = self.get_domain_config(domain)
        return domain_config.competitive_advantages

    def _load_domains(self):
        """Load domain configurations from YAML."""
        config = self.load_config()
        domains_data = config.get('domains', {})

        self._domains = {}

        # Map YAML domain keys to Domain enum values
        domain_mapping = {
            'search': Domain.SEARCH,
            'observability': Domain.OBSERVABILITY,
            'security': Domain.SECURITY,
            'all_domains': Domain.ALL_DOMAINS
        }

        for domain_key, domain_enum in domain_mapping.items():
            if domain_key in domains_data:
                domain_data = domains_data[domain_key]

                # Parse personas
                personas = []
                for persona_data in domain_data.get('personas', []):
                    persona = PersonaConfig(
                        name=persona_data.get('name', ''),
                        title=persona_data.get('title', ''),
                        pain_points=persona_data.get('pain_points', []),
                        goals=persona_data.get('goals', [])
                    )
                    personas.append(persona)

                # Create domain config
                domain_config = DomainConfig(
                    display_name=domain_data.get('display_name', domain_key.title()),
                    description=domain_data.get('description', ''),
                    personas=personas,
                    common_challenges=domain_data.get('common_challenges', []),
                    sample_data_types=domain_data.get('sample_data_types', []),
                    competitive_advantages=domain_data.get('competitive_advantages', [])
                )

                self._domains[domain_enum] = domain_config


# Global configuration loader instance
config_loader = ConfigLoader()