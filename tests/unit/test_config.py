import pytest
from pathlib import Path
from src.core.config import ConfigLoader, DomainConfig, PersonaConfig
from src.core.models import Domain


class TestConfigLoader:

    def test_load_config_file(self):
        """Test loading the domains.yaml configuration file."""
        config_loader = ConfigLoader()
        config_data = config_loader.load_config()

        assert 'domains' in config_data
        assert 'presentation_templates' in config_data
        assert 'lab_templates' in config_data
        assert 'content_settings' in config_data

    def test_get_domain_config(self):
        """Test getting domain-specific configuration."""
        config_loader = ConfigLoader()

        # Test search domain
        search_config = config_loader.get_domain_config(Domain.SEARCH)
        assert isinstance(search_config, DomainConfig)
        assert search_config.display_name == "Search"
        assert search_config.description
        assert len(search_config.personas) > 0
        assert len(search_config.competitive_advantages) > 0

        # Test observability domain
        obs_config = config_loader.get_domain_config(Domain.OBSERVABILITY)
        assert obs_config.display_name == "Observability"
        assert len(obs_config.personas) > 0

    def test_get_all_domain_configs(self):
        """Test getting all domain configurations."""
        config_loader = ConfigLoader()
        all_configs = config_loader.get_all_domain_configs()

        assert len(all_configs) == 4  # search, observability, security, all_domains
        assert Domain.SEARCH in all_configs
        assert Domain.OBSERVABILITY in all_configs
        assert Domain.SECURITY in all_configs
        assert Domain.ALL_DOMAINS in all_configs

    def test_personas_are_loaded(self):
        """Test that personas are properly loaded."""
        config_loader = ConfigLoader()
        search_config = config_loader.get_domain_config(Domain.SEARCH)

        assert len(search_config.personas) >= 3  # developer, architect, product_manager

        # Check persona structure
        first_persona = search_config.personas[0]
        assert isinstance(first_persona, PersonaConfig)
        assert first_persona.name
        assert first_persona.title
        assert len(first_persona.pain_points) > 0
        assert len(first_persona.goals) > 0

    def test_get_domain_hooks(self):
        """Test getting domain-specific hooks."""
        config_loader = ConfigLoader()

        for domain in [Domain.SEARCH, Domain.OBSERVABILITY, Domain.SECURITY]:
            hooks = config_loader.get_domain_hooks(domain)

            assert 'challenge' in hooks
            assert 'pain_points' in hooks
            assert 'hook' in hooks
            assert len(hooks['pain_points']) <= 3  # Top 3 pain points

    def test_get_presentation_template(self):
        """Test getting presentation templates."""
        config_loader = ConfigLoader()

        opening_hook = config_loader.get_presentation_template('opening_hook')
        assert opening_hook.structure
        assert 'challenge_statement' in opening_hook.structure

    def test_get_lab_template(self):
        """Test getting lab templates."""
        config_loader = ConfigLoader()

        beginner_template = config_loader.get_lab_template('beginner')
        assert beginner_template.estimated_time == 15
        assert len(beginner_template.prerequisites) > 0
        assert beginner_template.complexity

        intermediate_template = config_loader.get_lab_template('intermediate')
        assert intermediate_template.estimated_time == 30

    def test_get_content_settings(self):
        """Test getting content generation settings."""
        config_loader = ConfigLoader()
        settings = config_loader.get_content_settings()

        assert 'short' in settings.slide_length
        assert 'medium' in settings.slide_length
        assert 'long' in settings.slide_length
        assert settings.slide_length['short'] == 50

        assert 'business' in settings.audience_styles
        assert 'technical' in settings.audience_styles

    def test_get_competitive_advantages(self):
        """Test getting competitive advantages."""
        config_loader = ConfigLoader()

        for domain in [Domain.SEARCH, Domain.OBSERVABILITY, Domain.SECURITY]:
            advantages = config_loader.get_competitive_advantages(domain)
            assert isinstance(advantages, list)
            assert len(advantages) > 0

    def test_get_cross_domain_scenarios(self):
        """Test getting cross-domain scenarios."""
        config_loader = ConfigLoader()
        scenarios = config_loader.get_cross_domain_scenarios()

        assert isinstance(scenarios, list)
        assert len(scenarios) > 0

        # Check scenario structure
        for scenario in scenarios:
            assert 'name' in scenario
            assert 'description' in scenario
            assert 'domains' in scenario
            assert 'value_prop' in scenario

    def test_invalid_domain_raises_error(self):
        """Test that invalid domain raises appropriate error."""
        config_loader = ConfigLoader()

        # This should raise an error for unknown domain
        with pytest.raises(ValueError, match="No configuration found for domain"):
            # Create a fake domain enum value (this would fail in real usage)
            from enum import Enum
            class FakeDomain(Enum):
                FAKE = "fake"

            # Mock the domain to test error handling
            config_loader._domains = {}  # Clear loaded domains
            config_loader.get_domain_config(FakeDomain.FAKE)

    def test_invalid_template_raises_error(self):
        """Test that invalid template name raises appropriate error."""
        config_loader = ConfigLoader()

        with pytest.raises(ValueError, match="Presentation template not found"):
            config_loader.get_presentation_template('nonexistent_template')

        with pytest.raises(ValueError, match="Lab difficulty template not found"):
            config_loader.get_lab_template('nonexistent_difficulty')

    def test_config_file_not_found_raises_error(self):
        """Test that missing config file raises appropriate error."""
        config_loader = ConfigLoader(Path('/nonexistent/path/config.yaml'))

        with pytest.raises(FileNotFoundError, match="Configuration file not found"):
            config_loader.load_config()