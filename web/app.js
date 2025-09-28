// Elastic What's New Generator - Frontend Application
class ElasticGenerator {
    constructor() {
        this.apiBase = 'http://localhost:8000';
        this.features = [];
        this.currentPresentation = null;
        this.currentLabs = null;
        this.isGenerating = false;

        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadFeatures();
        this.setupTabs();
    }

    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                this.switchTab(e.target.closest('.nav-item').dataset.tab);
            });
        });

        // Search functionality
        document.getElementById('feature-search').addEventListener('input', (e) => {
            this.filterFeatures(e.target.value);
        });

        // Domain filtering
        document.querySelectorAll('input[name="domain"]').forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.filterFeaturesByDomain();
            });
        });

        // Modal close on outside click
        document.getElementById('add-feature-modal').addEventListener('click', (e) => {
            if (e.target.id === 'add-feature-modal') {
                this.closeAddFeatureModal();
            }
        });

        // Presentation domain change
        document.getElementById('presentation-domain').addEventListener('change', (e) => {
            this.updatePresentationFeatureSelector();
        });
    }

    setupTabs() {
        // Show features tab by default
        this.switchTab('features');
    }

    switchTab(tabName) {
        // Update nav items
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');

        // Load tab-specific content
        switch(tabName) {
            case 'presentations':
                this.populateFeatureSelector('presentation-features');
                break;
            case 'labs':
                this.populateFeatureSelector('lab-features');
                break;
            case 'exports':
                this.loadExportHistory();
                break;
        }
    }

    // Feature Management
    async loadFeatures() {
        try {
            this.showLoading('features-grid');

            // Try to load from API, fall back to sample data
            try {
                const response = await fetch(`${this.apiBase}/features`);
                if (response.ok) {
                    this.features = await response.json();
                } else {
                    throw new Error('API not available');
                }
            } catch (error) {
                // Use sample data from the API that generates sample features
                console.log('Using sample data from API');
                this.features = await this.getSampleFeatures();
            }

            this.renderFeatures();
        } catch (error) {
            console.error('Error loading features:', error);
            this.showToast('Error loading features', 'error');
            this.renderFeatures(); // Render empty state
        }
    }

    async getSampleFeatures() {
        try {
            // Get sample data by trying to generate a presentation, which will return sample features
            const response = await fetch(`${this.apiBase}/presentations/unified`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    feature_ids: [],
                    quarter: 'Q1-2024',
                    audience: 'mixed'
                })
            });

            if (response.ok) {
                const data = await response.json();
                // Extract feature info from the metadata
                return this.convertPresentationToFeatures(data);
            } else {
                return this.getHardcodedFeatures();
            }
        } catch (error) {
            console.log('Falling back to hardcoded features');
            return this.getHardcodedFeatures();
        }
    }

    convertPresentationToFeatures(presentationData) {
        // Create mock features based on what we know exists
        return [
            {
                id: 'bbq-001',
                name: 'Better Binary Quantization (BBQ)',
                description: '95% memory reduction with improved ranking quality',
                domain: 'search',
                theme: 'optimize',
                benefits: ['Reduces memory usage by 95%', 'Improves ranking quality', 'Faster query performance'],
                documentation_links: ['https://www.elastic.co/blog/better-binary-quantization'],
                created_at: new Date().toISOString()
            },
            {
                id: 'acorn-001',
                name: 'ACORN Retrieval',
                description: 'Efficient retrieval using automatic clustering',
                domain: 'search',
                theme: 'optimize',
                benefits: ['Improves retrieval efficiency', 'Better clustering', 'Enhanced search performance'],
                documentation_links: ['https://www.elastic.co/guide/acorn'],
                created_at: new Date().toISOString()
            },
            {
                id: 'agent-builder-001',
                name: 'Agent Builder',
                description: 'Framework for building AI agents with Elasticsearch',
                domain: 'search',
                theme: 'ai_innovation',
                benefits: ['Rapid AI agent development', 'Elasticsearch integration', 'Flexible framework'],
                documentation_links: ['https://www.elastic.co/guide/agent-builder'],
                created_at: new Date().toISOString()
            }
        ];
    }

    getHardcodedFeatures() {
        return [
            {
                id: 'bbq-001',
                name: 'Better Binary Quantization (BBQ)',
                description: '95% memory reduction with improved ranking quality',
                domain: 'search',
                theme: 'optimize',
                benefits: ['Reduces memory usage by 95%', 'Improves ranking quality', 'Faster query performance'],
                documentation_links: ['https://www.elastic.co/blog/better-binary-quantization'],
                created_at: new Date().toISOString()
            },
            {
                id: 'acorn-001',
                name: 'ACORN Retrieval',
                description: 'Efficient retrieval using automatic clustering',
                domain: 'search',
                theme: 'optimize',
                benefits: ['Improves retrieval efficiency', 'Better clustering', 'Enhanced search performance'],
                documentation_links: ['https://www.elastic.co/guide/acorn'],
                created_at: new Date().toISOString()
            },
            {
                id: 'agent-builder-001',
                name: 'Agent Builder',
                description: 'Framework for building AI agents with Elasticsearch',
                domain: 'search',
                theme: 'ai_innovation',
                benefits: ['Rapid AI agent development', 'Elasticsearch integration', 'Flexible framework'],
                documentation_links: ['https://www.elastic.co/guide/agent-builder'],
                created_at: new Date().toISOString()
            },
            {
                id: 'autoops-obs-001',
                name: 'AutoOps for Observability',
                description: 'Automated monitoring and alerting for observability data',
                domain: 'observability',
                theme: 'simplify',
                benefits: ['Reduces operational overhead', 'Automated alerting', 'Improved monitoring'],
                documentation_links: ['https://www.elastic.co/observability/autoops'],
                created_at: new Date().toISOString()
            },
            {
                id: 'managed-security-001',
                name: 'Managed Security Rules',
                description: 'Automated security rule management and updates',
                domain: 'security',
                theme: 'simplify',
                benefits: ['Automated rule updates', 'Improved security posture', 'Reduced management overhead'],
                documentation_links: ['https://www.elastic.co/security/rules'],
                created_at: new Date().toISOString()
            }
        ];
    }

    renderFeatures() {
        const grid = document.getElementById('features-grid');

        if (this.features.length === 0) {
            grid.innerHTML = `
                <div class="loading">
                    <i class="fas fa-box-open"></i>
                    No features found. Add some features to get started!
                </div>
            `;
            return;
        }

        grid.innerHTML = this.features.map(feature => `
            <div class="feature-card" data-id="${feature.id}">
                <h3>${feature.name}</h3>
                <div class="domain-badge ${feature.domain}">${feature.domain}</div>
                <p>${feature.description}</p>

                ${feature.benefits && feature.benefits.length > 0 ? `
                <div class="benefits">
                    <h4>Benefits:</h4>
                    <ul>
                        ${feature.benefits.slice(0, 3).map(benefit => `<li>${benefit}</li>`).join('')}
                    </ul>
                </div>
                ` : ''}

                <div class="feature-actions">
                    <button class="btn btn-secondary btn-small" onclick="app.editFeature('${feature.id}')">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                    <button class="btn btn-secondary btn-small" onclick="app.deleteFeature('${feature.id}')">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
        `).join('');
    }

    filterFeatures(searchTerm) {
        const cards = document.querySelectorAll('.feature-card');
        cards.forEach(card => {
            const text = card.textContent.toLowerCase();
            const matches = text.includes(searchTerm.toLowerCase());
            card.style.display = matches ? 'block' : 'none';
        });
    }

    filterFeaturesByDomain() {
        const checkedDomains = Array.from(document.querySelectorAll('input[name="domain"]:checked'))
            .map(cb => cb.value);

        const cards = document.querySelectorAll('.feature-card');
        cards.forEach(card => {
            const domain = card.querySelector('.domain-badge').className.split(' ')[1];
            const shouldShow = checkedDomains.includes('all') || checkedDomains.includes(domain);
            card.style.display = shouldShow ? 'block' : 'none';
        });
    }

    populateFeatureSelector(containerId, filterDomain = null) {
        const container = document.getElementById(containerId);
        let features = this.features;

        // For lab features, prioritize valid sample features but show all
        if (containerId === 'lab-features') {
            const validSampleFeatureIds = [
                'bbq-001', 'acorn-001', 'agent-builder-001', 'cross-cluster-001',
                'autoops-obs-001', 'apm-performance-001', 'ai-assistant-obs-001',
                'siem-efficiency-001', 'managed-security-001', 'ml-security-001'
            ];
            // Sort to show sample features first, then user-created features
            features = this.features.sort((a, b) => {
                const aIsValid = validSampleFeatureIds.includes(a.id);
                const bIsValid = validSampleFeatureIds.includes(b.id);
                if (aIsValid && !bIsValid) return -1;
                if (!aIsValid && bIsValid) return 1;
                return 0;
            });
        }

        // Filter by domain if specified
        if (filterDomain && filterDomain !== 'all_domains') {
            features = features.filter(f => f.domain === filterDomain);
        }

        container.innerHTML = features.map(feature => {
            // For lab features, mark user-created features with a warning
            let label = `${feature.name} (${feature.domain})`;
            let extraClass = '';

            if (containerId === 'lab-features') {
                const validSampleFeatureIds = [
                    'bbq-001', 'acorn-001', 'agent-builder-001', 'cross-cluster-001',
                    'autoops-obs-001', 'apm-performance-001', 'ai-assistant-obs-001',
                    'siem-efficiency-001', 'managed-security-001', 'ml-security-001'
                ];
                if (!validSampleFeatureIds.includes(feature.id)) {
                    label += ' ⚠️ (New feature - lab generation may not work)';
                    extraClass = ' style="color: #856404;"';
                }
            }

            return `
                <label class="feature-checkbox"${extraClass}>
                    <input type="checkbox" value="${feature.id}" name="selected-features">
                    <span>${label}</span>
                </label>
            `;
        }).join('');
    }

    updatePresentationFeatureSelector() {
        const selectedDomain = document.getElementById('presentation-domain').value;
        this.populateFeatureSelector('presentation-features', selectedDomain);
    }

    // Feature CRUD Operations
    showAddFeatureModal() {
        document.getElementById('add-feature-modal').style.display = 'block';
    }

    closeAddFeatureModal() {
        document.getElementById('add-feature-modal').style.display = 'none';
        document.getElementById('add-feature-form').reset();
    }

    async submitFeature() {
        const featureData = {
            name: document.getElementById('feature-name').value,
            description: document.getElementById('feature-description').value,
            domain: document.getElementById('feature-domain').value,
            benefits: this.parseTextareaLines(document.getElementById('feature-benefits').value),
            documentation_links: this.parseTextareaLines(document.getElementById('feature-links').value),
            scrape_docs: document.getElementById('scrape-docs').checked
        };

        if (!featureData.name || !featureData.description || !featureData.domain) {
            this.showToast('Please fill in all required fields', 'error');
            return;
        }

        try {
            const response = await fetch(`${this.apiBase}/features`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(featureData)
            });

            if (response.ok) {
                const newFeature = await response.json();
                this.features.push({
                    id: newFeature.id,
                    name: newFeature.name,
                    description: newFeature.description,
                    domain: newFeature.domain,
                    theme: newFeature.theme,
                    benefits: featureData.benefits,
                    documentation_links: featureData.documentation_links,
                    created_at: newFeature.created_at
                });

                this.renderFeatures();
                this.updatePresentationFeatureSelector();
                this.populateFeatureSelector('lab-features');
                this.closeAddFeatureModal();
                this.showToast('Feature added successfully!', 'success');
            } else {
                throw new Error('Failed to create feature');
            }
        } catch (error) {
            console.error('Error creating feature:', error);
            this.showToast('Error creating feature', 'error');
        }
    }

    parseTextareaLines(text) {
        return text.split('\n').map(line => line.trim()).filter(line => line.length > 0);
    }

    async editFeature(featureId) {
        // For now, just show a simple alert
        this.showToast('Edit feature functionality coming soon!', 'warning');
    }

    async deleteFeature(featureId) {
        if (!confirm('Are you sure you want to delete this feature?')) {
            return;
        }

        try {
            const response = await fetch(`${this.apiBase}/features/${featureId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.features = this.features.filter(f => f.id !== featureId);
                this.renderFeatures();
                this.showToast('Feature deleted successfully!', 'success');
            } else {
                throw new Error('Failed to delete feature');
            }
        } catch (error) {
            console.error('Error deleting feature:', error);
            this.showToast('Error deleting feature', 'error');
        }
    }

    // Presentation Generation
    async generatePresentation() {
        // Prevent concurrent requests
        if (this.isGenerating) {
            return;
        }
        this.isGenerating = true;

        const selectedFeatures = Array.from(document.querySelectorAll('#presentation-features input:checked'))
            .map(cb => cb.value);

        // If no features selected, send empty array to use all features for the domain
        // The API will automatically select all features matching the domain

        const requestData = {
            feature_ids: selectedFeatures,
            domain: document.getElementById('presentation-domain').value,
            quarter: document.getElementById('presentation-quarter').value,
            audience: document.getElementById('presentation-audience').value
        };

        try {
            this.showToast('Generating presentation...', 'info');

            const endpoint = requestData.domain === 'all_domains' ?
                '/presentations/unified' : '/presentations/complete';

            const response = await fetch(`${this.apiBase}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            if (response.ok) {
                this.currentPresentation = await response.json();
                this.displayPresentationPreview();
                this.showToast('Presentation generated successfully!', 'success');
            } else {
                const errorText = await response.text();
                console.error(`Presentation generation failed:`, {
                    status: response.status,
                    statusText: response.statusText,
                    url: response.url,
                    body: errorText,
                    requestData: requestData
                });
                throw new Error(`Failed to generate presentation: ${response.status} ${response.statusText}`);
            }
        } catch (error) {
            console.error('Error generating presentation:', error);
            this.showToast(`Error generating presentation: ${error.message}`, 'error');
        } finally {
            this.isGenerating = false;
        }
    }

    displayPresentationPreview() {
        const preview = document.getElementById('presentation-preview');
        const content = document.getElementById('presentation-content');

        if (!this.currentPresentation) {
            return;
        }

        const presentation = this.currentPresentation.presentation;
        const slides = presentation.slides || [];

        let previewText = `# ${presentation.title}\n\n`;
        previewText += `**Domain:** ${presentation.domain}\n`;
        previewText += `**Quarter:** ${presentation.quarter}\n`;
        previewText += `**Slides:** ${slides.length}\n\n`;

        slides.forEach((slide, index) => {
            previewText += `## Slide ${index + 1}: ${slide.title}\n`;
            if (slide.subtitle) {
                previewText += `### ${slide.subtitle}\n`;
            }
            previewText += `${slide.content.substring(0, 200)}...\n\n`;
        });

        content.textContent = previewText;
        preview.style.display = 'block';
    }

    async exportPresentation(format) {
        if (!this.currentPresentation) {
            this.showToast('No presentation to export', 'warning');
            return;
        }

        const selectedFeatures = Array.from(document.querySelectorAll('#presentation-features input:checked'))
            .map(cb => cb.value);

        const requestData = {
            feature_ids: selectedFeatures,
            domain: document.getElementById('presentation-domain').value,
            quarter: document.getElementById('presentation-quarter').value,
            audience: document.getElementById('presentation-audience').value,
            format_type: format,
            include_speaker_notes: true,
            include_metadata: true,
            include_business_value: true
        };

        try {
            const response = await fetch(`${this.apiBase}/presentations/markdown/export`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            if (response.ok) {
                const result = await response.json();
                if (result.download_url) {
                    // Open download URL
                    window.open(`${this.apiBase}${result.download_url}`, '_blank');
                    this.showToast(`Presentation exported as ${format}!`, 'success');
                }
            } else {
                throw new Error('Failed to export presentation');
            }
        } catch (error) {
            console.error('Error exporting presentation:', error);
            this.showToast('Error exporting presentation', 'error');
        }
    }

    // Lab Generation
    async generateLabs() {
        const selectedFeatures = Array.from(document.querySelectorAll('#lab-features input:checked'))
            .map(cb => cb.value);

        // Handle feature selection for lab generation
        let featureIds = selectedFeatures;
        const validSampleFeatureIds = [
            'bbq-001', 'acorn-001', 'agent-builder-001', 'cross-cluster-001',
            'autoops-obs-001', 'apm-performance-001', 'ai-assistant-obs-001',
            'siem-efficiency-001', 'managed-security-001', 'ml-security-001'
        ];

        if (featureIds.length === 0) {
            // No features selected - use first valid sample feature
            featureIds = [validSampleFeatureIds[0]];
        } else {
            // Check if selected features include invalid ones
            const invalidFeatures = featureIds.filter(id => !validSampleFeatureIds.includes(id));
            if (invalidFeatures.length > 0) {
                this.showToast(`Warning: New features (${invalidFeatures.join(', ')}) may not work for lab generation. Using sample feature instead.`, 'warning');
                // Use first valid feature instead
                featureIds = [validSampleFeatureIds[0]];
            }
        }

        if (featureIds.length === 0) {
            this.showToast('No features available for lab generation', 'warning');
            return;
        }

        const requestData = {
            feature_ids: featureIds,
            track_title: document.getElementById('workshop-title').value,
            format_type: document.getElementById('lab-format').value,
            include_metadata: document.getElementById('include-metadata').checked,
            export_format: 'inline'
        };

        try {
            this.showToast('Generating labs...', 'info');

            const endpoint = featureIds.length === 1 ?
                '/labs/markdown/single' : '/labs/markdown/export';

            const response = await fetch(`${this.apiBase}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            if (response.ok) {
                this.currentLabs = await response.json();
                this.displayLabPreview();
                this.showToast('Labs generated successfully!', 'success');
            } else {
                const errorText = await response.text();
                console.error(`Lab generation failed:`, {
                    status: response.status,
                    statusText: response.statusText,
                    url: response.url,
                    body: errorText,
                    requestData: requestData
                });
                throw new Error(`Failed to generate labs: ${response.status} ${response.statusText}`);
            }
        } catch (error) {
            console.error('Error generating labs:', error);
            this.showToast(`Error generating labs: ${error.message}`, 'error');
        }
    }

    displayLabPreview() {
        const preview = document.getElementById('lab-preview');
        const content = document.getElementById('lab-content');

        if (!this.currentLabs) {
            return;
        }

        const labContent = this.currentLabs.content || 'No content available';
        content.textContent = labContent.substring(0, 2000) + (labContent.length > 2000 ? '...' : '');
        preview.style.display = 'block';
    }

    async exportLabs(exportFormat) {
        if (!this.currentLabs) {
            this.showToast('No labs to export', 'warning');
            return;
        }

        if (exportFormat === 'inline') {
            // Show full content in a new window
            const newWindow = window.open('', '_blank');
            newWindow.document.write(`
                <html>
                    <head>
                        <title>Lab Workshop</title>
                        <style>
                            body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; padding: 2rem; max-width: 800px; margin: 0 auto; }
                            pre { white-space: pre-wrap; }
                        </style>
                    </head>
                    <body>
                        <pre>${this.currentLabs.content}</pre>
                    </body>
                </html>
            `);
        } else {
            // Download as file
            const selectedFeatures = Array.from(document.querySelectorAll('#lab-features input:checked'))
                .map(cb => cb.value);

            const requestData = {
                feature_ids: selectedFeatures,
                track_title: document.getElementById('workshop-title').value,
                format_type: document.getElementById('lab-format').value,
                include_metadata: document.getElementById('include-metadata').checked,
                export_format: 'file'
            };

            try {
                const endpoint = selectedFeatures.length === 1 ?
                    '/labs/markdown/single' : '/labs/markdown/export';

                const response = await fetch(`${this.apiBase}${endpoint}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(requestData)
                });

                if (response.ok) {
                    const result = await response.json();
                    if (result.download_url) {
                        window.open(`${this.apiBase}${result.download_url}`, '_blank');
                        this.showToast('Lab downloaded successfully!', 'success');
                    }
                } else {
                    throw new Error('Failed to export labs');
                }
            } catch (error) {
                console.error('Error exporting labs:', error);
                this.showToast('Error exporting labs', 'error');
            }
        }
    }

    // Export History
    loadExportHistory() {
        const exportList = document.getElementById('export-list');
        // Mock export history for now
        exportList.innerHTML = `
            <div class="export-item">
                <div class="export-info">
                    <h4>Search Features Presentation - GitHub Markdown</h4>
                    <p>Generated on ${new Date().toLocaleDateString()} • 3 features • 6,372 characters</p>
                </div>
                <div class="export-actions">
                    <button class="btn btn-secondary btn-small">
                        <i class="fas fa-download"></i> Download
                    </button>
                </div>
            </div>
            <div class="export-item">
                <div class="export-info">
                    <h4>Advanced Search Workshop - Standard Markdown</h4>
                    <p>Generated on ${new Date().toLocaleDateString()} • 2 labs • 3,027 characters</p>
                </div>
                <div class="export-actions">
                    <button class="btn btn-secondary btn-small">
                        <i class="fas fa-download"></i> Download
                    </button>
                </div>
            </div>
        `;
    }

    // Utility Methods
    showLoading(containerId) {
        document.getElementById(containerId).innerHTML = `
            <div class="loading">
                <i class="fas fa-spinner fa-spin"></i>
                Loading...
            </div>
        `;
    }

    showToast(message, type = 'success') {
        const toast = document.getElementById('status-toast');
        const messageElement = toast.querySelector('.toast-message');
        const iconElement = toast.querySelector('i');

        messageElement.textContent = message;

        // Update icon and class based on type
        toast.className = `toast ${type}`;
        switch(type) {
            case 'success':
                iconElement.className = 'fas fa-check-circle';
                break;
            case 'error':
                iconElement.className = 'fas fa-exclamation-circle';
                break;
            case 'warning':
                iconElement.className = 'fas fa-exclamation-triangle';
                break;
            case 'info':
                iconElement.className = 'fas fa-info-circle';
                break;
        }

        toast.classList.add('show');

        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
}

// Global functions for onclick handlers
function showAddFeatureModal() {
    app.showAddFeatureModal();
}

function closeAddFeatureModal() {
    app.closeAddFeatureModal();
}

function submitFeature() {
    app.submitFeature();
}

function generatePresentation() {
    app.generatePresentation();
}

function exportPresentation(format) {
    app.exportPresentation(format);
}

function generateLabs() {
    app.generateLabs();
}

function exportLabs(exportFormat) {
    app.exportLabs(exportFormat);
}

// Initialize the application
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new ElasticGenerator();
});