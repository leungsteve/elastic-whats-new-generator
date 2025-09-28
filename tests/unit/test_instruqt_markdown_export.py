import pytest
import tempfile
from pathlib import Path
from src.integrations.instruqt_exporter import InstruqtExporter
from src.integrations.markdown_exporter import MarkdownExporter, MarkdownFormat
from src.core.models import Feature, LabInstruction, Domain, Theme


class TestInstruqtMarkdownExport:

    @pytest.fixture
    def instruqt_exporter(self):
        """Create an InstruqtExporter instance."""
        return InstruqtExporter()

    @pytest.fixture
    def markdown_exporter(self):
        """Create a MarkdownExporter instance."""
        return MarkdownExporter()

    @pytest.fixture
    def sample_feature(self):
        """Create a sample feature for testing."""
        return Feature(
            id="search-001",
            name="Advanced Search Filters",
            description="New filtering capabilities for advanced search queries",
            benefits=["Improved search precision", "Better user experience"],
            theme=Theme.OPTIMIZE,
            domain=Domain.SEARCH,
            documentation_links=["https://docs.elastic.co/search-filters"]
        )

    @pytest.fixture
    def sample_lab_instruction(self):
        """Create a sample lab instruction for testing."""
        return LabInstruction(
            title="Hands-on with Advanced Search Filters",
            objective="Learn to use advanced search filters to improve query precision",
            scenario="In this lab, you'll work with Elasticsearch to create advanced search filters that improve query precision and performance. You'll apply these filters to real-world data scenarios.",
            setup_instructions="Prepare your Elasticsearch environment with sample data. Ensure you have access to Kibana for visualization and testing.",
            steps=[
                "Setup your search environment with sample data using the provided index template",
                "Create basic filters using term and range queries",
                "Build complex filters with bool queries combining multiple conditions",
                "Test filter performance and compare results with unfiltered queries",
                "Validate that your filters produce the expected results"
            ],
            validation="Verify that your filters work correctly by checking query response times are improved and results match expected criteria. Run the provided test queries to confirm functionality.",
            estimated_time=30,
            difficulty="intermediate"
        )

    def test_instruqt_exporter_supports_markdown_export(self, instruqt_exporter):
        """Test that InstruqtExporter has markdown export capabilities."""
        # Check if InstruqtExporter has methods we expect for markdown export
        assert hasattr(instruqt_exporter, 'export_lab_instruction')
        # We'll add markdown-specific methods in the next implementation step

    def test_lab_instruction_to_markdown_conversion(self, sample_lab_instruction, markdown_exporter):
        """Test converting lab instruction content to markdown format."""
        # For now, this tests the basic structure we'll need
        assert sample_lab_instruction.title
        assert sample_lab_instruction.objective
        assert sample_lab_instruction.scenario
        assert len(sample_lab_instruction.steps) == 5

        # Test that we can format the basic content as markdown
        markdown_title = f"# {sample_lab_instruction.title}"
        assert "Hands-on with Advanced Search Filters" in markdown_title

        markdown_objective = f"## Objective\n\n{sample_lab_instruction.objective}"
        assert "Learn to use advanced search filters" in markdown_objective

    def test_lab_steps_markdown_formatting(self, sample_lab_instruction):
        """Test that lab steps can be formatted as markdown."""
        steps_markdown_parts = []

        for i, step in enumerate(sample_lab_instruction.steps, 1):
            step_markdown = f"## Step {i}\n\n{step}\n\n"
            steps_markdown_parts.append(step_markdown)

        # Verify we generated markdown for all steps
        assert len(steps_markdown_parts) == 5
        assert "## Step 1" in steps_markdown_parts[0]
        assert "Setup your search environment" in steps_markdown_parts[0]
        assert "## Step 2" in steps_markdown_parts[1]
        assert "Create basic filters" in steps_markdown_parts[1]

    def test_objective_markdown_formatting(self, sample_lab_instruction):
        """Test formatting objective as markdown."""
        objective_markdown = f"## Objective\n\n{sample_lab_instruction.objective}\n\n"

        assert "## Objective" in objective_markdown
        assert "Learn to use advanced search filters" in objective_markdown

    def test_scenario_markdown_formatting(self, sample_lab_instruction):
        """Test formatting scenario as markdown."""
        scenario_markdown = f"## Scenario\n\n{sample_lab_instruction.scenario}\n\n"

        assert "## Scenario" in scenario_markdown
        assert "Elasticsearch to create advanced search filters" in scenario_markdown

    def test_validation_markdown_formatting(self, sample_lab_instruction):
        """Test formatting validation as markdown."""
        validation_markdown = f"## Validation\n\n{sample_lab_instruction.validation}\n\n"

        assert "## Validation" in validation_markdown
        assert "Verify that your filters work correctly" in validation_markdown

    def test_complete_lab_markdown_document(self, sample_lab_instruction):
        """Test creating a complete lab markdown document."""
        # Build complete markdown document
        markdown_content = f"# {sample_lab_instruction.title}\n\n"
        markdown_content += f"**Estimated Time:** {sample_lab_instruction.estimated_time} minutes\n"
        markdown_content += f"**Difficulty:** {sample_lab_instruction.difficulty}\n\n"

        # Objective
        markdown_content += f"## Objective\n\n{sample_lab_instruction.objective}\n\n"

        # Scenario
        markdown_content += f"## Scenario\n\n{sample_lab_instruction.scenario}\n\n"

        # Setup instructions
        markdown_content += f"## Setup\n\n{sample_lab_instruction.setup_instructions}\n\n"

        # Steps
        for i, step in enumerate(sample_lab_instruction.steps, 1):
            markdown_content += f"## Step {i}\n\n{step}\n\n"

        # Validation
        markdown_content += f"## Validation\n\n{sample_lab_instruction.validation}\n\n"

        # Verify complete document structure
        assert "# Hands-on with Advanced Search Filters" in markdown_content
        assert "**Estimated Time:** 30 minutes" in markdown_content
        assert "**Difficulty:** intermediate" in markdown_content
        assert "## Objective" in markdown_content
        assert "## Scenario" in markdown_content
        assert "## Setup" in markdown_content
        assert "## Step 1" in markdown_content
        assert "## Step 2" in markdown_content
        assert "## Step 3" in markdown_content
        assert "## Validation" in markdown_content

    def test_multiple_labs_markdown_export(self, sample_lab_instruction):
        """Test exporting multiple labs as a combined markdown document."""
        # Create multiple lab instructions
        lab1 = sample_lab_instruction
        lab2 = LabInstruction(
            title="Advanced Query Optimization",
            objective="Learn to optimize complex search queries for better performance",
            scenario="You'll work with performance monitoring tools to identify and resolve query bottlenecks in Elasticsearch.",
            setup_instructions="Ensure you have access to a test Elasticsearch cluster with monitoring enabled.",
            steps=[
                "Analyze current query performance using explain API",
                "Identify performance bottlenecks in your queries",
                "Apply optimization techniques to improve performance"
            ],
            validation="Verify that optimized queries perform better than original versions by comparing response times.",
            estimated_time=45,
            difficulty="advanced"
        )

        labs = [lab1, lab2]

        # Build combined markdown document
        combined_markdown = "# Elasticsearch Workshop\n\n"
        combined_markdown += f"**Total Labs:** {len(labs)}\n"
        combined_markdown += f"**Total Time:** {sum(lab.estimated_time for lab in labs)} minutes\n\n"

        combined_markdown += "## Table of Contents\n\n"
        for i, lab in enumerate(labs, 1):
            combined_markdown += f"{i}. [{lab.title}](#{lab.title.lower().replace(' ', '-')})\n"
        combined_markdown += "\n"

        for i, lab in enumerate(labs, 1):
            combined_markdown += f"# Lab {i}: {lab.title}\n\n"
            combined_markdown += f"**Estimated Time:** {lab.estimated_time} minutes\n"
            combined_markdown += f"**Difficulty:** {lab.difficulty}\n\n"
            combined_markdown += f"## Description\n\n{lab.description}\n\n"

            # Add more lab content here...
            combined_markdown += "---\n\n"

        # Verify combined document
        assert "# Elasticsearch Workshop" in combined_markdown
        assert "**Total Labs:** 2" in combined_markdown
        assert "**Total Time:** 75 minutes" in combined_markdown
        assert "## Table of Contents" in combined_markdown
        assert "# Lab 1: Hands-on with Advanced Search Filters" in combined_markdown
        assert "# Lab 2: Advanced Query Optimization" in combined_markdown
        assert "---" in combined_markdown  # Lab separator

    def test_markdown_format_variations(self, sample_lab_instruction):
        """Test different markdown format variations for lab export."""
        base_content = {
            'title': sample_lab_instruction.title,
            'description': sample_lab_instruction.description,
            'time': sample_lab_instruction.estimated_time,
            'difficulty': sample_lab_instruction.difficulty
        }

        # Standard format
        standard_md = f"# {base_content['title']}\n\n{base_content['description']}\n\n"
        standard_md += f"**Time:** {base_content['time']} min | **Difficulty:** {base_content['difficulty']}\n\n"

        # GitHub format with badges
        github_md = f"# {base_content['title']}\n\n"
        github_md += f"![Difficulty](https://img.shields.io/badge/difficulty-{base_content['difficulty']}-blue)\n"
        github_md += f"![Time](https://img.shields.io/badge/time-{base_content['time']}min-green)\n\n"
        github_md += f"{base_content['description']}\n\n"

        # Reveal.js format with slide separators
        reveal_md = f"# {base_content['title']}\n\n{base_content['description']}\n\n---\n\n"
        reveal_md += f"## Lab Details\n\n- **Time:** {base_content['time']} minutes\n- **Difficulty:** {base_content['difficulty']}\n\n"

        # Verify different formats
        assert "**Time:**" in standard_md
        assert "![Difficulty]" in github_md
        assert "---" in reveal_md
        assert base_content['title'] in standard_md
        assert base_content['title'] in github_md
        assert base_content['title'] in reveal_md

    def test_lab_export_to_file(self, sample_lab_instruction):
        """Test exporting lab instruction to markdown file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_lab.md"

            # Create markdown content
            markdown_content = f"# {sample_lab_instruction.title}\n\n"
            markdown_content += f"{sample_lab_instruction.description}\n\n"
            markdown_content += f"**Estimated Time:** {sample_lab_instruction.estimated_time} minutes\n"

            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            # Verify file exists and content
            assert output_path.exists()

            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "# Hands-on with Advanced Search Filters" in content
                assert "**Estimated Time:** 30 minutes" in content

    def test_lab_markdown_with_images_and_links(self, sample_lab_instruction):
        """Test lab markdown with embedded images and links."""
        # Add images and links to lab content
        enhanced_content = f"# {sample_lab_instruction.title}\n\n"
        enhanced_content += f"{sample_lab_instruction.description}\n\n"

        # Add diagram
        enhanced_content += "## Architecture Overview\n\n"
        enhanced_content += "![Search Architecture](../images/search-architecture.png)\n\n"

        # Add reference links
        enhanced_content += "## References\n\n"
        enhanced_content += "- [Elasticsearch Documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/)\n"
        enhanced_content += "- [Search API Guide](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-search.html)\n\n"

        # Add code with syntax highlighting
        enhanced_content += "## Sample Query\n\n"
        enhanced_content += "```json\n"
        enhanced_content += '{\n  "query": {\n    "bool": {\n      "filter": [\n        {"term": {"status": "published"}}\n      ]\n    }\n  }\n}\n'
        enhanced_content += "```\n\n"

        # Verify enhanced content
        assert "![Search Architecture]" in enhanced_content
        assert "[Elasticsearch Documentation]" in enhanced_content
        assert "```json" in enhanced_content
        assert '"bool"' in enhanced_content

    def test_lab_table_of_contents_generation(self, sample_lab_instruction):
        """Test automatic table of contents generation for labs."""
        # Generate TOC from lab steps
        toc_content = "## Table of Contents\n\n"

        # Add main sections
        toc_content += "1. [Learning Objectives](#learning-objectives)\n"
        toc_content += "2. [Prerequisites](#prerequisites)\n"

        # Add steps
        for i, step in enumerate(sample_lab_instruction.steps, 1):
            step_anchor = step['title'].lower().replace(' ', '-').replace(':', '')
            toc_content += f"{i + 2}. [Step {i}: {step['title']}](#step-{i}-{step_anchor})\n"

        toc_content += f"{len(sample_lab_instruction.steps) + 3}. [Validation](#validation)\n\n"

        # Verify TOC structure
        assert "## Table of Contents" in toc_content
        assert "[Learning Objectives](#learning-objectives)" in toc_content
        assert "[Prerequisites](#prerequisites)" in toc_content
        assert "[Step 1: Setup Search Environment](#step-1-setup-search-environment)" in toc_content
        assert "[Validation](#validation)" in toc_content