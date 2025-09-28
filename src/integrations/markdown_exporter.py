"""
Markdown export functionality for presentations and content.

This module provides markdown export capabilities for presentations,
supporting multiple markdown formats and customizable output options.
"""

from enum import Enum
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime
import re

from src.core.models import Presentation, SlideContent


class MarkdownFormat(Enum):
    """Supported markdown output formats."""
    STANDARD = "standard"
    GITHUB = "github"
    REVEAL_JS = "reveal_js"


class MarkdownExporter:
    """Exports presentations and content to markdown format."""

    def __init__(self):
        """Initialize the markdown exporter."""
        self.templates = {
            MarkdownFormat.STANDARD: self._get_standard_template(),
            MarkdownFormat.GITHUB: self._get_github_template(),
            MarkdownFormat.REVEAL_JS: self._get_reveal_template()
        }

    def export_presentation(
        self,
        presentation: Presentation,
        format_type: MarkdownFormat = MarkdownFormat.STANDARD,
        include_speaker_notes: bool = True,
        include_metadata: bool = True,
        include_business_value: bool = True,
        template: Optional[str] = None
    ) -> str:
        """
        Export a presentation to markdown format.

        Args:
            presentation: The presentation to export
            format_type: The markdown format to use
            include_speaker_notes: Whether to include speaker notes
            include_metadata: Whether to include presentation metadata
            include_business_value: Whether to include business value statements
            template: Custom template string (overrides format_type)

        Returns:
            Markdown content as string

        Raises:
            ValueError: If format_type is not supported
        """
        if isinstance(format_type, str):
            # Handle string format types
            try:
                format_type = MarkdownFormat(format_type)
            except ValueError:
                raise ValueError(f"Unsupported markdown format: {format_type}")

        # Use custom template or format-specific template
        if template:
            markdown_template = template
        else:
            markdown_template = self.templates[format_type]

        # Generate markdown content
        return self._render_presentation(
            presentation,
            markdown_template,
            format_type,
            include_speaker_notes,
            include_metadata,
            include_business_value
        )

    def export_to_file(
        self,
        presentation: Presentation,
        output_path: Path,
        format_type: MarkdownFormat = MarkdownFormat.STANDARD,
        **kwargs
    ) -> Path:
        """
        Export presentation to a markdown file.

        Args:
            presentation: The presentation to export
            output_path: Path where the markdown file should be saved
            format_type: The markdown format to use
            **kwargs: Additional arguments passed to export_presentation

        Returns:
            Path to the created file
        """
        markdown_content = self.export_presentation(
            presentation,
            format_type=format_type,
            **kwargs
        )

        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        return output_path

    def _render_presentation(
        self,
        presentation: Presentation,
        template: str,
        format_type: MarkdownFormat,
        include_speaker_notes: bool,
        include_metadata: bool,
        include_business_value: bool
    ) -> str:
        """Render the presentation using the specified template."""
        # Prepare template variables
        variables = {
            'title': presentation.title,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'domain': presentation.domain.display_name,
            'quarter': presentation.quarter,
            'slides': []
        }

        # Process slides
        for slide in presentation.slides:
            slide_data = {
                'title': slide.title,
                'subtitle': slide.subtitle or '',
                'content': slide.content,
                'theme': slide.theme.value,
                'business_value': slide.business_value if include_business_value else '',
                'speaker_notes': slide.speaker_notes if include_speaker_notes else ''
            }
            variables['slides'].append(slide_data)

        # Add metadata if requested
        if include_metadata:
            variables['metadata'] = {
                'id': presentation.id,
                'featured_themes': [theme.value for theme in presentation.featured_themes],
                'feature_ids': presentation.feature_ids,
                'generated_at': presentation.generated_at.isoformat() if presentation.generated_at else datetime.now().isoformat()
            }

        # Handle empty presentation
        if not presentation.slides:
            variables['empty_message'] = "No slides available"

        # Render based on format
        return self._render_template(template, variables, format_type)

    def _render_template(self, template: str, variables: Dict[str, Any], format_type: MarkdownFormat) -> str:
        """Render the template with variables."""
        # Simple template rendering (could be enhanced with Jinja2 in the future)
        content = template

        # Replace basic variables
        content = content.replace('{{title}}', variables['title'])
        content = content.replace('{{date}}', variables['date'])
        content = content.replace('{{domain}}', variables['domain'])
        content = content.replace('{{quarter}}', variables['quarter'])

        # Handle empty presentation
        if not variables['slides']:
            content = content.replace('{{slides_content}}', variables.get('empty_message', 'No slides available'))
            return content

        # Render slides
        slides_content = []
        for slide in variables['slides']:
            slide_md = self._render_slide(slide, format_type)
            slides_content.append(slide_md)

        content = content.replace('{{slides_content}}', '\n\n'.join(slides_content))

        # Add metadata if present
        if 'metadata' in variables:
            metadata_md = self._render_metadata(variables['metadata'])
            content = content.replace('{{metadata}}', metadata_md)
        else:
            content = content.replace('{{metadata}}', '')

        return content.strip()

    def _render_slide(self, slide: Dict[str, Any], format_type: MarkdownFormat) -> str:
        """Render a single slide to markdown."""
        parts = []

        # Slide title
        if format_type == MarkdownFormat.REVEAL_JS:
            parts.append(f"<!-- .slide: data-theme=\"{slide['theme']}\" -->")

        # Title with appropriate heading level
        if slide['subtitle']:
            parts.append(f"## {slide['title']}")
            parts.append(f"### {slide['subtitle']}")
        else:
            parts.append(f"## {slide['title']}")

        # Content
        if slide['content']:
            parts.append(slide['content'])

        # Business value (format-specific styling)
        if slide['business_value']:
            if format_type == MarkdownFormat.GITHUB:
                parts.append(f"> **Business Value:** {slide['business_value']}")
            else:
                parts.append(f"**Business Value:** {slide['business_value']}")

        # Speaker notes
        if slide['speaker_notes']:
            if format_type == MarkdownFormat.REVEAL_JS:
                parts.append(f"<!-- Note: {slide['speaker_notes']} -->")
            else:
                parts.append(f"*Speaker Notes: {slide['speaker_notes']}*")

        # Slide separator for reveal.js
        if format_type == MarkdownFormat.REVEAL_JS:
            parts.append("---")

        return '\n\n'.join(parts)

    def _render_metadata(self, metadata: Dict[str, Any]) -> str:
        """Render presentation metadata."""
        parts = [
            "## Presentation Metadata",
            f"**Presentation ID:** {metadata['id']}",
            f"**Featured Themes:** {', '.join(metadata['featured_themes'])}",
            f"**Feature IDs:** {', '.join(metadata['feature_ids'])}",
            f"**Generated At:** {metadata['generated_at']}"
        ]
        return '\n'.join(parts)

    def _get_standard_template(self) -> str:
        """Get the standard markdown template."""
        return """# {{title}}

**Domain:** {{domain}}
**Quarter:** {{quarter}}
**Generated:** {{date}}

{{slides_content}}

{{metadata}}
""".strip()

    def _get_github_template(self) -> str:
        """Get the GitHub flavored markdown template."""
        return """# {{title}}

| | |
|---|---|
| **Domain** | {{domain}} |
| **Quarter** | {{quarter}} |
| **Generated** | {{date}} |

---

{{slides_content}}

---

{{metadata}}
""".strip()

    def _get_reveal_template(self) -> str:
        """Get the reveal.js compatible markdown template."""
        return """# {{title}}

*{{domain}} - {{quarter}}*

---

{{slides_content}}

---

{{metadata}}
""".strip()

    def _escape_markdown(self, text: str) -> str:
        """Escape special markdown characters if needed."""
        # Basic escaping - could be enhanced based on needs
        # For now, we preserve markdown formatting in content
        return text

    def _clean_content(self, content: str) -> str:
        """Clean and normalize content for markdown output."""
        if not content:
            return ""

        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        content = content.strip()

        return content