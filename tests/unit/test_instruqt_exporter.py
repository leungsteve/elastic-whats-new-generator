import pytest
import tempfile
import yaml
from pathlib import Path
from src.integrations.instruqt_exporter import InstruqtExporter, InstruqtTrack
from src.core.models import LabInstruction, Feature, Domain, Theme


class TestInstruqtTrack:

    def test_track_creation(self):
        """Test basic track creation."""
        track = InstruqtTrack(
            slug="test-track",
            title="Test Track",
            description="A test track",
            tags=["elasticsearch", "test"],
            estimated_time=30,
            challenges=[{"slug": "test-challenge", "title": "Test Challenge"}]
        )

        assert track.slug == "test-track"
        assert track.title == "Test Track"
        assert track.description == "A test track"
        assert track.tags == ["elasticsearch", "test"]
        assert track.estimated_time == 30
        assert len(track.challenges) == 1

    def test_track_to_yaml(self):
        """Test track YAML serialization."""
        track = InstruqtTrack(
            slug="test-track",
            title="Test Track",
            description="A test track",
            tags=["elasticsearch"],
            estimated_time=30,
            challenges=[{"slug": "test", "title": "Test"}]
        )

        yaml_content = track.to_yaml()
        parsed = yaml.safe_load(yaml_content)

        assert parsed["slug"] == "test-track"
        assert parsed["title"] == "Test Track"
        assert parsed["estimated_time"] == 30
        assert "lab_config" in parsed
        assert "version" in parsed["lab_config"]

    def test_default_lab_config(self):
        """Test default lab configuration."""
        track = InstruqtTrack(
            slug="test",
            title="Test",
            description="Test",
            tags=[],
            estimated_time=30,
            challenges=[]
        )

        assert "version" in track.lab_config
        assert "virtualmachines" in track.lab_config
        assert "environment" in track.lab_config

        vm = track.lab_config["virtualmachines"][0]
        assert vm["name"] == "elastic-server"
        assert "elasticsearch" in str(vm["allow_external_ingress"])


class TestInstruqtExporter:

    @pytest.fixture
    def sample_lab_instruction(self):
        """Create a sample lab instruction for testing."""
        return LabInstruction(
            title="Test Elasticsearch Feature",
            objective="Learn how to use the test feature",
            scenario="You are testing a new Elasticsearch feature",
            setup_instructions="1. Start Elasticsearch\n2. Load sample data",
            steps=[
                "**Step 1: Configure** - Set up the feature",
                "**Step 2: Test** - Run some queries",
                "**Step 3: Validate** - Check the results"
            ],
            validation="Verify the feature is working correctly",
            estimated_time=30,
            difficulty="intermediate"
        )

    @pytest.fixture
    def sample_feature(self):
        """Create a sample feature for testing."""
        return Feature(
            id="search-001",
            name="Test Search Feature",
            description="A test search feature for validation",
            domain=Domain.SEARCH,
            theme=Theme.OPTIMIZE,
            benefits=["Faster queries", "Better relevance"]
        )

    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary directory for test outputs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_generate_track_slug(self, sample_feature):
        """Test track slug generation."""
        exporter = InstruqtExporter()
        slug = exporter._generate_track_slug(sample_feature)

        assert slug == "elastic-search-test-search-feature"
        assert slug.islower()
        assert " " not in slug

    def test_generate_challenge_slug(self, sample_feature):
        """Test challenge slug generation."""
        exporter = InstruqtExporter()
        slug = exporter._generate_challenge_slug(sample_feature)

        assert slug == "test-search-feature"
        assert slug.islower()
        assert " " not in slug

    def test_lab_to_challenge_conversion(self, sample_lab_instruction, sample_feature):
        """Test converting lab instruction to Instruqt challenge."""
        exporter = InstruqtExporter()
        challenge = exporter._lab_to_challenge(sample_lab_instruction, sample_feature, "test-challenge")

        assert challenge["slug"] == "test-challenge"
        assert challenge["title"] == sample_lab_instruction.title
        assert challenge["type"] == "challenge"
        assert challenge["teaser"] == sample_lab_instruction.objective
        assert challenge["difficulty"] == sample_lab_instruction.difficulty
        assert challenge["timelimit"] == sample_lab_instruction.estimated_time * 60

        # Check tabs
        assert len(challenge["tabs"]) == 3
        tab_titles = [tab["title"] for tab in challenge["tabs"]]
        assert "Terminal" in tab_titles
        assert "Kibana" in tab_titles
        assert "Elasticsearch" in tab_titles

    def test_format_assignment_markdown(self, sample_lab_instruction):
        """Test assignment markdown formatting."""
        exporter = InstruqtExporter()
        assignment = exporter._format_assignment(sample_lab_instruction)

        assert sample_lab_instruction.title in assignment
        assert sample_lab_instruction.objective in assignment
        assert sample_lab_instruction.scenario in assignment
        assert sample_lab_instruction.validation in assignment

        # Check that steps are formatted correctly
        assert "### Step 1:" in assignment or "### Configure" in assignment
        assert "## Instructions" in assignment
        assert "## Validation" in assignment

    def test_export_single_lab(self, sample_lab_instruction, sample_feature, temp_output_dir):
        """Test exporting a single lab instruction."""
        exporter = InstruqtExporter()
        track_dir = exporter.export_lab_instruction(
            sample_lab_instruction,
            sample_feature,
            temp_output_dir
        )

        # Check track directory was created
        assert track_dir.exists()
        assert track_dir.is_dir()

        # Check track.yml was created
        track_file = track_dir / "track.yml"
        assert track_file.exists()

        # Parse and validate track.yml
        with open(track_file) as f:
            track_data = yaml.safe_load(f)

        assert track_data["title"] == sample_lab_instruction.title
        assert track_data["estimated_time"] == sample_lab_instruction.estimated_time
        assert "elasticsearch" in track_data["tags"]

        # Check challenge directory was created
        challenge_dirs = [d for d in track_dir.iterdir() if d.is_dir() and d.name.startswith("01-")]
        assert len(challenge_dirs) == 1

        challenge_dir = challenge_dirs[0]
        assert (challenge_dir / "assignment.md").exists()
        assert (challenge_dir / "setup-elastic-server").exists()
        assert (challenge_dir / "check-elastic-server").exists()

    def test_export_multiple_labs(self, temp_output_dir):
        """Test exporting multiple lab instructions as combined track."""
        exporter = InstruqtExporter()

        # Create multiple labs and features
        labs = []
        features = []

        for i in range(3):
            lab = LabInstruction(
                title=f"Lab {i+1}",
                objective=f"Objective {i+1}",
                scenario=f"Scenario {i+1}",
                setup_instructions="Setup",
                steps=[f"Step 1 for lab {i+1}"],
                validation="Validate",
                estimated_time=20,
                difficulty="beginner"
            )
            labs.append(lab)

            feature = Feature(
                id=f"feature-{i+1}",
                name=f"Feature {i+1}",
                description=f"Description {i+1}",
                domain=Domain.SEARCH
            )
            features.append(feature)

        track_dir = exporter.export_multiple_labs(
            labs,
            features,
            temp_output_dir,
            "Combined Workshop"
        )

        # Check track was created
        assert track_dir.exists()
        track_file = track_dir / "track.yml"
        assert track_file.exists()

        # Parse track.yml
        with open(track_file) as f:
            track_data = yaml.safe_load(f)

        assert track_data["title"] == "Combined Workshop"
        assert track_data["estimated_time"] == 60  # 3 labs * 20 minutes
        assert len(track_data["challenges"]) == 3

        # Check all challenge directories were created
        challenge_dirs = [d for d in track_dir.iterdir() if d.is_dir() and d.name.startswith("0")]
        assert len(challenge_dirs) == 3

    def test_domain_specific_configuration(self, sample_lab_instruction, temp_output_dir):
        """Test domain-specific track configuration."""
        exporter = InstruqtExporter()

        # Test different domains
        domains = [Domain.SEARCH, Domain.OBSERVABILITY, Domain.SECURITY]

        for domain in domains:
            feature = Feature(
                id=f"test-{domain.value}",
                name=f"Test {domain.display_name} Feature",
                description="Test feature",
                domain=domain
            )

            track_dir = exporter.export_lab_instruction(
                sample_lab_instruction,
                feature,
                temp_output_dir
            )

            # Check track configuration
            track_file = track_dir / "track.yml"
            with open(track_file) as f:
                track_data = yaml.safe_load(f)

            # Domain should be in tags
            assert domain.value in track_data["tags"]

    def test_setup_script_generation(self, sample_feature):
        """Test setup script generation."""
        exporter = InstruqtExporter()
        script = exporter._generate_setup_script(sample_feature)

        assert "#!/bin/bash" in script
        assert "Elasticsearch" in script
        assert "Kibana" in script
        assert "curl" in script

        # Search domain should have ecommerce data
        if sample_feature.domain == Domain.SEARCH:
            assert "ecommerce" in script

    def test_check_script_generation(self, sample_feature):
        """Test validation script generation."""
        exporter = InstruqtExporter()
        script = exporter._generate_check_script(sample_feature)

        assert "#!/bin/bash" in script
        assert sample_feature.name in script
        assert "curl" in script
        assert "_cluster/health" in script

    def test_invalid_input_handling(self, temp_output_dir):
        """Test handling of invalid inputs."""
        exporter = InstruqtExporter()

        # Test mismatched lists
        with pytest.raises(ValueError, match="Number of lab instructions must match"):
            exporter.export_multiple_labs(
                [LabInstruction(title="Test", objective="Test", scenario="Test",
                               setup_instructions="Test", steps=["Test"],
                               validation="Test", estimated_time=30, difficulty="beginner")],
                [],  # Empty features list
                temp_output_dir
            )

    def test_combined_track_slug_generation(self):
        """Test combined track slug generation."""
        exporter = InstruqtExporter()

        # Single domain
        features = [
            Feature(id="1", name="Feature 1", description="Test", domain=Domain.SEARCH),
            Feature(id="2", name="Feature 2", description="Test", domain=Domain.SEARCH)
        ]
        slug = exporter._generate_combined_track_slug(features)
        assert slug == "elastic-search-workshop"

        # Multiple domains
        features = [
            Feature(id="1", name="Feature 1", description="Test", domain=Domain.SEARCH),
            Feature(id="2", name="Feature 2", description="Test", domain=Domain.OBSERVABILITY)
        ]
        slug = exporter._generate_combined_track_slug(features)
        assert slug == "elastic-multi-domain-workshop"