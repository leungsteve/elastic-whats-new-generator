"""
Instruqt track exporter for Elastic What's New Generator.

This module exports generated lab instructions to Instruqt track format,
enabling hands-on training experiences on the Instruqt platform.
"""

import json
import yaml
from typing import List, Dict, Any, Optional
from pathlib import Path
from dataclasses import asdict

from src.core.models import LabInstruction, Feature, Domain


class InstruqtTrack:
    """Represents an Instruqt track configuration."""

    def __init__(
        self,
        slug: str,
        title: str,
        description: str,
        tags: List[str],
        estimated_time: int,
        challenges: List[Dict[str, Any]],
        lab_config: Optional[Dict[str, Any]] = None
    ):
        self.slug = slug
        self.title = title
        self.description = description
        self.tags = tags
        self.estimated_time = estimated_time
        self.challenges = challenges
        self.lab_config = lab_config or self._default_lab_config()

    def _default_lab_config(self) -> Dict[str, Any]:
        """Default Instruqt lab configuration for Elastic."""
        return {
            "version": "0.32",
            "virtualmachines": [
                {
                    "name": "elastic-server",
                    "image": "gcr.io/instruqt/elasticsearch:8.11.0",
                    "machine_type": "n1-standard-2",
                    "allow_external_ingress": [
                        {"name": "elasticsearch", "port": 9200, "protocol": "http"},
                        {"name": "kibana", "port": 5601, "protocol": "http"}
                    ]
                }
            ],
            "environment": {
                "ELASTIC_VERSION": "8.11.0",
                "KIBANA_HOST": "http://elastic-server:5601",
                "ELASTICSEARCH_HOST": "http://elastic-server:9200"
            }
        }

    def to_yaml(self) -> str:
        """Convert track to Instruqt YAML format."""
        track_data = {
            "slug": self.slug,
            "title": self.title,
            "description": self.description,
            "tags": self.tags,
            "estimated_time": self.estimated_time,
            "lab_config": self.lab_config,
            "challenges": self.challenges
        }

        return yaml.dump(track_data, default_flow_style=False, sort_keys=False)


class InstruqtExporter:
    """Exports lab instructions to Instruqt track format."""

    def __init__(self):
        """Initialize the exporter."""
        self.track_templates = {
            "search": {
                "tags": ["elasticsearch", "search", "elastic"],
                "vm_config": {
                    "sample_data": ["ecommerce", "logs", "metrics"],
                    "elasticsearch_config": {
                        "indices.template": "search-optimized"
                    }
                }
            },
            "observability": {
                "tags": ["elasticsearch", "observability", "monitoring", "elastic"],
                "vm_config": {
                    "sample_data": ["metrics", "logs", "apm"],
                    "elasticsearch_config": {
                        "indices.template": "observability-optimized"
                    },
                    "additional_services": ["metricbeat", "filebeat", "apm-server"]
                }
            },
            "security": {
                "tags": ["elasticsearch", "security", "siem", "elastic"],
                "vm_config": {
                    "sample_data": ["security_events", "audit_logs", "threat_intel"],
                    "elasticsearch_config": {
                        "indices.template": "security-optimized",
                        "security.enabled": True
                    },
                    "additional_services": ["winlogbeat", "auditbeat"]
                }
            }
        }

    def export_lab_instruction(
        self,
        lab_instruction: LabInstruction,
        feature: Feature,
        output_dir: Path
    ) -> Path:
        """
        Export a single lab instruction to Instruqt track format.

        Args:
            lab_instruction: The lab instruction to export
            feature: The feature this lab is for
            output_dir: Directory to save the track files

        Returns:
            Path to the generated track directory
        """
        # Generate track slug and metadata
        track_slug = self._generate_track_slug(feature)
        track_dir = output_dir / track_slug
        track_dir.mkdir(parents=True, exist_ok=True)

        # Create track configuration
        track = self._create_track_from_lab(lab_instruction, feature, track_slug)

        # Write track.yml
        track_file = track_dir / "track.yml"
        with open(track_file, 'w', encoding='utf-8') as f:
            f.write(track.to_yaml())

        # Create challenge directories and files
        for i, challenge in enumerate(track.challenges):
            challenge_dir = track_dir / f"0{i+1}-{challenge['slug']}"
            challenge_dir.mkdir(exist_ok=True)

            self._create_challenge_files(challenge, challenge_dir, feature)

        # Create setup scripts
        self._create_setup_scripts(track_dir, feature)

        return track_dir

    def export_multiple_labs(
        self,
        lab_instructions: List[LabInstruction],
        features: List[Feature],
        output_dir: Path,
        track_title: str = "Elastic Features Workshop"
    ) -> Path:
        """
        Export multiple lab instructions as a single multi-challenge track.

        Args:
            lab_instructions: List of lab instructions
            features: Corresponding features for each lab
            output_dir: Directory to save the track files
            track_title: Title for the combined track

        Returns:
            Path to the generated track directory
        """
        if len(lab_instructions) != len(features):
            raise ValueError("Number of lab instructions must match number of features")

        # Generate combined track
        track_slug = self._generate_combined_track_slug(features)
        track_dir = output_dir / track_slug
        track_dir.mkdir(parents=True, exist_ok=True)

        # Create combined track
        track = self._create_combined_track(lab_instructions, features, track_slug, track_title)

        # Write track.yml
        track_file = track_dir / "track.yml"
        with open(track_file, 'w', encoding='utf-8') as f:
            f.write(track.to_yaml())

        # Create challenge directories for each lab
        for i, (lab, feature) in enumerate(zip(lab_instructions, features)):
            challenge_slug = self._generate_challenge_slug(feature)
            challenge_dir = track_dir / f"0{i+1}-{challenge_slug}"
            challenge_dir.mkdir(exist_ok=True)

            # Create challenge from lab instruction
            challenge = self._lab_to_challenge(lab, feature, challenge_slug)
            self._create_challenge_files(challenge, challenge_dir, feature)

        # Create shared setup scripts
        self._create_setup_scripts(track_dir, features[0])  # Use first feature's domain

        return track_dir

    def _generate_track_slug(self, feature: Feature) -> str:
        """Generate a track slug from feature name."""
        slug = feature.name.lower().replace(' ', '-').replace('_', '-')
        slug = ''.join(c for c in slug if c.isalnum() or c == '-')
        return f"elastic-{feature.domain.value}-{slug}"

    def _generate_combined_track_slug(self, features: List[Feature]) -> str:
        """Generate a track slug for combined features."""
        domains = set(f.domain.value for f in features)
        if len(domains) == 1:
            domain_part = list(domains)[0]
        else:
            domain_part = "multi-domain"

        return f"elastic-{domain_part}-workshop"

    def _generate_challenge_slug(self, feature: Feature) -> str:
        """Generate a challenge slug from feature name."""
        slug = feature.name.lower().replace(' ', '-').replace('_', '-')
        return ''.join(c for c in slug if c.isalnum() or c == '-')

    def _create_track_from_lab(
        self,
        lab_instruction: LabInstruction,
        feature: Feature,
        track_slug: str
    ) -> InstruqtTrack:
        """Create an Instruqt track from a lab instruction."""
        # Get domain-specific configuration
        domain_config = self.track_templates.get(feature.domain.value, self.track_templates["search"])

        # Create single challenge from lab
        challenge = self._lab_to_challenge(lab_instruction, feature, "hands-on-lab")

        return InstruqtTrack(
            slug=track_slug,
            title=lab_instruction.title,
            description=lab_instruction.objective,
            tags=domain_config["tags"],
            estimated_time=lab_instruction.estimated_time,
            challenges=[challenge]
        )

    def _create_combined_track(
        self,
        lab_instructions: List[LabInstruction],
        features: List[Feature],
        track_slug: str,
        track_title: str
    ) -> InstruqtTrack:
        """Create a combined track from multiple lab instructions."""
        # Determine tags from all features
        all_tags = set()
        total_time = 0

        for feature in features:
            domain_config = self.track_templates.get(feature.domain.value, self.track_templates["search"])
            all_tags.update(domain_config["tags"])

        for lab in lab_instructions:
            total_time += lab.estimated_time

        # Create challenges
        challenges = []
        for lab, feature in zip(lab_instructions, features):
            challenge_slug = self._generate_challenge_slug(feature)
            challenge = self._lab_to_challenge(lab, feature, challenge_slug)
            challenges.append(challenge)

        # Create description
        feature_names = [f.name for f in features]
        description = f"Hands-on workshop exploring {', '.join(feature_names[:2])}"
        if len(feature_names) > 2:
            description += f" and {len(feature_names) - 2} more Elastic innovations"

        return InstruqtTrack(
            slug=track_slug,
            title=track_title,
            description=description,
            tags=list(all_tags),
            estimated_time=total_time,
            challenges=challenges
        )

    def _lab_to_challenge(
        self,
        lab_instruction: LabInstruction,
        feature: Feature,
        challenge_slug: str
    ) -> Dict[str, Any]:
        """Convert a lab instruction to Instruqt challenge format."""
        return {
            "slug": challenge_slug,
            "title": lab_instruction.title,
            "type": "challenge",
            "teaser": lab_instruction.objective,
            "assignment": self._format_assignment(lab_instruction),
            "tabs": [
                {
                    "title": "Terminal",
                    "type": "terminal",
                    "hostname": "elastic-server"
                },
                {
                    "title": "Kibana",
                    "type": "service",
                    "hostname": "elastic-server",
                    "port": 5601
                },
                {
                    "title": "Elasticsearch",
                    "type": "service",
                    "hostname": "elastic-server",
                    "port": 9200
                }
            ],
            "difficulty": lab_instruction.difficulty,
            "timelimit": lab_instruction.estimated_time * 60  # Convert to seconds
        }

    def _format_assignment(self, lab_instruction: LabInstruction) -> str:
        """Format lab instruction as Instruqt assignment markdown."""
        assignment_parts = [
            f"# {lab_instruction.title}",
            "",
            f"## Objective",
            lab_instruction.objective,
            "",
            f"## Scenario",
            lab_instruction.scenario,
            "",
            f"## Setup",
            lab_instruction.setup_instructions,
            "",
            f"## Instructions"
        ]

        # Add numbered steps
        for i, step in enumerate(lab_instruction.steps, 1):
            assignment_parts.extend([
                f"### {step.split('**')[1].split('**')[0] if '**' in step else f'Step {i}'}",
                step.replace('**Step ', '').replace('**', ''),
                ""
            ])

        # Add validation
        assignment_parts.extend([
            "## Validation",
            lab_instruction.validation,
            "",
            "## Next Steps",
            "Once you've completed this challenge, click **Check** to validate your work and proceed."
        ])

        return "\n".join(assignment_parts)

    def _create_challenge_files(
        self,
        challenge: Dict[str, Any],
        challenge_dir: Path,
        feature: Feature
    ):
        """Create challenge files in the challenge directory."""
        # Create assignment.md
        assignment_file = challenge_dir / "assignment.md"
        with open(assignment_file, 'w', encoding='utf-8') as f:
            f.write(challenge["assignment"])

        # Create setup script
        setup_file = challenge_dir / "setup-elastic-server"
        setup_script = self._generate_setup_script(feature)
        with open(setup_file, 'w', encoding='utf-8') as f:
            f.write(setup_script)
        setup_file.chmod(0o755)  # Make executable

        # Create check script
        check_file = challenge_dir / "check-elastic-server"
        check_script = self._generate_check_script(feature)
        with open(check_file, 'w', encoding='utf-8') as f:
            f.write(check_script)
        check_file.chmod(0o755)  # Make executable

    def _create_setup_scripts(self, track_dir: Path, feature: Feature):
        """Create track-level setup scripts."""
        # Create track setup script
        setup_file = track_dir / "setup-elastic-server"
        setup_script = self._generate_track_setup_script(feature)
        with open(setup_file, 'w', encoding='utf-8') as f:
            f.write(setup_script)
        setup_file.chmod(0o755)

    def _generate_setup_script(self, feature: Feature) -> str:
        """Generate challenge setup script."""
        domain_config = self.track_templates.get(feature.domain.value, self.track_templates["search"])

        script_parts = [
            "#!/bin/bash",
            "# Setup script for " + feature.name,
            "",
            "set -euo pipefail",
            "",
            "# Wait for Elasticsearch to be ready",
            "echo 'Waiting for Elasticsearch...'",
            "until curl -s http://localhost:9200/_cluster/health; do",
            "  sleep 2",
            "done",
            "",
            "# Wait for Kibana to be ready",
            "echo 'Waiting for Kibana...'",
            "until curl -s http://localhost:5601/api/status; do",
            "  sleep 2",
            "done",
            ""
        ]

        # Add domain-specific setup
        if feature.domain.value == "search":
            script_parts.extend([
                "# Load sample ecommerce data",
                "curl -X POST 'localhost:9200/_bulk' -H 'Content-Type: application/json' --data-binary @/opt/sample-data/ecommerce.json",
                ""
            ])
        elif feature.domain.value == "observability":
            script_parts.extend([
                "# Load sample metrics and logs",
                "curl -X POST 'localhost:9200/_bulk' -H 'Content-Type: application/json' --data-binary @/opt/sample-data/metrics.json",
                "curl -X POST 'localhost:9200/_bulk' -H 'Content-Type: application/json' --data-binary @/opt/sample-data/logs.json",
                ""
            ])
        elif feature.domain.value == "security":
            script_parts.extend([
                "# Load sample security events",
                "curl -X POST 'localhost:9200/_bulk' -H 'Content-Type: application/json' --data-binary @/opt/sample-data/security-events.json",
                ""
            ])

        script_parts.extend([
            "echo 'Setup complete!'",
            "exit 0"
        ])

        return "\n".join(script_parts)

    def _generate_check_script(self, feature: Feature) -> str:
        """Generate challenge validation script."""
        return f"""#!/bin/bash
# Validation script for {feature.name}

set -euo pipefail

# Basic checks that Elasticsearch and Kibana are running
if ! curl -s http://localhost:9200/_cluster/health | grep -q '"status":"green"\\|"status":"yellow"'; then
    echo "❌ Elasticsearch cluster is not healthy"
    exit 1
fi

if ! curl -s http://localhost:5601/api/status | grep -q '"overall":{{.*"level":"available"'; then
    echo "❌ Kibana is not available"
    exit 1
fi

# Feature-specific validation would go here
# This is a basic template - actual validation should be customized per feature

echo "✅ Basic validation passed!"
echo "✅ {feature.name} lab completed successfully!"
exit 0
"""

    def _generate_track_setup_script(self, feature: Feature) -> str:
        """Generate track-level setup script."""
        return f"""#!/bin/bash
# Track setup script for {feature.domain.display_name} domain

set -euo pipefail

# Install and configure Elasticsearch
echo "Setting up Elasticsearch cluster..."

# Basic Elasticsearch configuration
cat > /etc/elasticsearch/elasticsearch.yml << EOF
cluster.name: instruqt-cluster
node.name: elastic-server
path.data: /var/lib/elasticsearch
path.logs: /var/log/elasticsearch
network.host: 0.0.0.0
http.port: 9200
discovery.type: single-node
xpack.security.enabled: false
EOF

# Start services
systemctl start elasticsearch
systemctl enable elasticsearch

# Start Kibana
systemctl start kibana
systemctl enable kibana

echo "Track setup complete!"
exit 0
"""