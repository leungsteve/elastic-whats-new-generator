import pytest
import tempfile
from pathlib import Path
from src.integrations.markdown_exporter import MarkdownExporter, MarkdownFormat
from src.core.models import Presentation, SlideContent, Theme, Domain


class TestMarkdownExporter:

    @pytest.fixture
    def sample_presentation(self):
        """Create a sample presentation for testing."""
        slides = [
            SlideContent(
                title="Introduction",
                subtitle="Getting Started",
                content="## Welcome\n\nThis is the introduction slide.\n\n• Point 1\n• Point 2",
                business_value="Sets clear expectations",
                theme=Theme.SIMPLIFY,
                speaker_notes="Remember to speak slowly"
            ),
            SlideContent(
                title="Technical Deep Dive",
                content="### Advanced Features\n\n```python\nprint('Hello World')\n```\n\n**Key Benefits:**\n- Performance improvement\n- Better user experience",
                business_value="Drives technical adoption",
                theme=Theme.OPTIMIZE
            ),
            SlideContent(
                title="Call to Action",
                content="## Next Steps\n\n1. Try the demo\n2. Schedule a meeting\n3. Start your trial",
                business_value="Converts prospects to customers",
                theme=Theme.AI_INNOVATION
            )
        ]

        return Presentation(
            id="test-presentation",
            domain=Domain.SEARCH,
            quarter="Q1-2024",
            title="Test Presentation - Q1 2024",
            slides=slides,
            featured_themes=[Theme.SIMPLIFY, Theme.OPTIMIZE, Theme.AI_INNOVATION],
            feature_ids=["feature-1", "feature-2"]
        )

    @pytest.fixture
    def markdown_exporter(self):
        """Create a markdown exporter instance."""
        return MarkdownExporter()

    def test_markdown_exporter_initialization(self, markdown_exporter):
        """Test that MarkdownExporter initializes correctly."""
        assert markdown_exporter is not None
        assert hasattr(markdown_exporter, 'export_presentation')
        assert hasattr(markdown_exporter, 'export_to_file')

    def test_export_presentation_standard_format(self, markdown_exporter, sample_presentation):
        """Test exporting presentation to standard markdown format."""
        markdown_content = markdown_exporter.export_presentation(
            sample_presentation,
            format_type=MarkdownFormat.STANDARD
        )

        # Check basic structure
        assert "# Test Presentation - Q1 2024" in markdown_content
        assert "## Introduction" in markdown_content
        assert "## Technical Deep Dive" in markdown_content
        assert "## Call to Action" in markdown_content

        # Check content preservation
        assert "This is the introduction slide" in markdown_content
        assert "```python" in markdown_content
        assert "print('Hello World')" in markdown_content
        assert "• Point 1" in markdown_content
        assert "• Point 2" in markdown_content

        # Check metadata inclusion
        assert "**Domain:** Search" in markdown_content
        assert "**Quarter:** Q1-2024" in markdown_content

    def test_export_presentation_github_format(self, markdown_exporter, sample_presentation):
        """Test exporting presentation to GitHub flavored markdown."""
        markdown_content = markdown_exporter.export_presentation(
            sample_presentation,
            format_type=MarkdownFormat.GITHUB
        )

        # GitHub-specific formatting
        assert "# Test Presentation - Q1 2024" in markdown_content
        assert "---" in markdown_content  # Section dividers
        assert "> **Business Value:**" in markdown_content  # Blockquotes for business value

        # Check GitHub-style task lists if any
        assert "- [ ]" in markdown_content or "1." in markdown_content

    def test_export_presentation_reveal_js_format(self, markdown_exporter, sample_presentation):
        """Test exporting presentation to reveal.js compatible markdown."""
        markdown_content = markdown_exporter.export_presentation(
            sample_presentation,
            format_type=MarkdownFormat.REVEAL_JS
        )

        # Reveal.js-specific slide separators
        assert "---" in markdown_content or "<!-- .slide:" in markdown_content

        # Should include speaker notes
        assert "Note:" in markdown_content or "<!-- Note:" in markdown_content

    def test_export_with_speaker_notes(self, markdown_exporter, sample_presentation):
        """Test that speaker notes are included when requested."""
        markdown_content = markdown_exporter.export_presentation(
            sample_presentation,
            include_speaker_notes=True
        )

        assert "Remember to speak slowly" in markdown_content

    def test_export_without_speaker_notes(self, markdown_exporter, sample_presentation):
        """Test that speaker notes are excluded when not requested."""
        markdown_content = markdown_exporter.export_presentation(
            sample_presentation,
            include_speaker_notes=False
        )

        assert "Remember to speak slowly" not in markdown_content

    def test_export_with_metadata(self, markdown_exporter, sample_presentation):
        """Test that presentation metadata is included."""
        markdown_content = markdown_exporter.export_presentation(
            sample_presentation,
            include_metadata=True
        )

        assert "Presentation ID:" in markdown_content
        assert "test-presentation" in markdown_content
        assert "Featured Themes:" in markdown_content
        assert "Feature IDs:" in markdown_content

    def test_export_without_metadata(self, markdown_exporter, sample_presentation):
        """Test that metadata can be excluded."""
        markdown_content = markdown_exporter.export_presentation(
            sample_presentation,
            include_metadata=False
        )

        assert "Presentation ID:" not in markdown_content
        assert "Featured Themes:" not in markdown_content

    def test_export_to_file(self, markdown_exporter, sample_presentation):
        """Test exporting presentation to a file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_presentation.md"

            result_path = markdown_exporter.export_to_file(
                sample_presentation,
                output_path,
                format_type=MarkdownFormat.STANDARD
            )

            assert result_path.exists()
            assert result_path == output_path

            # Verify file content
            with open(result_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "# Test Presentation - Q1 2024" in content
                assert "## Introduction" in content

    def test_export_minimal_presentation(self, markdown_exporter):
        """Test exporting a presentation with minimal content."""
        minimal_slide = SlideContent(
            title="Minimal Slide",
            content="Minimal content",
            business_value="Basic value",
            theme=Theme.SIMPLIFY
        )

        minimal_presentation = Presentation(
            id="minimal-test",
            domain=Domain.SEARCH,
            quarter="Q1-2024",
            title="Minimal Presentation",
            slides=[minimal_slide],
            featured_themes=[],
            feature_ids=[]
        )

        markdown_content = markdown_exporter.export_presentation(minimal_presentation)

        assert "# Minimal Presentation" in markdown_content
        assert "## Minimal Slide" in markdown_content

    def test_export_with_special_characters(self, markdown_exporter):
        """Test handling of special characters in content."""
        special_slide = SlideContent(
            title="Special Characters & Symbols",
            content="# Heading with # hash\n\n* List with * asterisk\n\n[Link](http://example.com)\n\n`code with backticks`",
            business_value="Tests markdown escaping",
            theme=Theme.SIMPLIFY
        )

        presentation = Presentation(
            id="special-test",
            domain=Domain.SEARCH,
            quarter="Q1-2024",
            title="Special Test",
            slides=[special_slide],
            featured_themes=[Theme.SIMPLIFY],
            feature_ids=[]
        )

        markdown_content = markdown_exporter.export_presentation(presentation)

        # Content should be preserved correctly
        assert "Special Characters & Symbols" in markdown_content
        assert "`code with backticks`" in markdown_content
        assert "[Link](http://example.com)" in markdown_content

    def test_export_with_business_values(self, markdown_exporter, sample_presentation):
        """Test that business values are properly formatted."""
        markdown_content = markdown_exporter.export_presentation(
            sample_presentation,
            include_business_value=True
        )

        assert "Sets clear expectations" in markdown_content
        assert "Drives technical adoption" in markdown_content
        assert "Converts prospects to customers" in markdown_content

    def test_export_different_themes(self, markdown_exporter):
        """Test that different themes are handled correctly."""
        slides = [
            SlideContent(title="Simplify", content="Simplify content", business_value="Simplifies processes", theme=Theme.SIMPLIFY),
            SlideContent(title="Optimize", content="Optimize content", business_value="Optimizes performance", theme=Theme.OPTIMIZE),
            SlideContent(title="AI Innovation", content="AI content", business_value="Innovates with AI", theme=Theme.AI_INNOVATION)
        ]

        presentation = Presentation(
            id="theme-test",
            domain=Domain.SEARCH,
            quarter="Q1-2024",
            title="Theme Test",
            slides=slides,
            featured_themes=[Theme.SIMPLIFY, Theme.OPTIMIZE, Theme.AI_INNOVATION],
            feature_ids=[]
        )

        markdown_content = markdown_exporter.export_presentation(presentation)

        assert "Simplify content" in markdown_content
        assert "Optimize content" in markdown_content
        assert "AI content" in markdown_content

    def test_markdown_format_enum(self):
        """Test that MarkdownFormat enum has expected values."""
        assert MarkdownFormat.STANDARD
        assert MarkdownFormat.GITHUB
        assert MarkdownFormat.REVEAL_JS

        # Test string values
        assert MarkdownFormat.STANDARD.value == "standard"
        assert MarkdownFormat.GITHUB.value == "github"
        assert MarkdownFormat.REVEAL_JS.value == "reveal_js"

    def test_export_large_presentation(self, markdown_exporter):
        """Test exporting a presentation with many slides."""
        slides = []
        for i in range(20):
            slides.append(SlideContent(
                title=f"Slide {i+1}",
                content=f"Content for slide {i+1}\n\n• Point A\n• Point B",
                business_value=f"Value for slide {i+1}",
                theme=Theme.SIMPLIFY
            ))

        large_presentation = Presentation(
            id="large-test",
            domain=Domain.SEARCH,
            quarter="Q1-2024",
            title="Large Presentation",
            slides=slides,
            featured_themes=[Theme.SIMPLIFY],
            feature_ids=[]
        )

        markdown_content = markdown_exporter.export_presentation(large_presentation)

        # Should handle all slides
        assert "## Slide 1" in markdown_content
        assert "## Slide 20" in markdown_content
        assert "Content for slide 10" in markdown_content

    def test_invalid_format_handling(self, markdown_exporter, sample_presentation):
        """Test handling of invalid format types."""
        with pytest.raises(ValueError, match="Unsupported markdown format"):
            markdown_exporter.export_presentation(
                sample_presentation,
                format_type="invalid_format"
            )

    def test_export_with_custom_template(self, markdown_exporter, sample_presentation):
        """Test exporting with custom markdown template."""
        custom_template = """
# {{title}}

Generated on: {{date}}

{{#slides}}
## {{title}}
{{content}}

---

{{/slides}}
        """.strip()

        markdown_content = markdown_exporter.export_presentation(
            sample_presentation,
            template=custom_template
        )

        assert "Generated on:" in markdown_content
        assert "# Test Presentation - Q1 2024" in markdown_content