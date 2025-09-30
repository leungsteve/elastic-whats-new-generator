// Elastic What's New Generator - Frontend Application
class ElasticGenerator {
    constructor() {
        this.apiBase = 'http://localhost:8000';
        this.features = [];
        this.currentPresentation = null;
        this.currentLabs = null;
        this.isGenerating = false;

        // View mode for presentation and labs
        this.presentationViewMode = 'rendered';
        this.labViewMode = 'rendered';
        this.presentationMarkdown = '';
        this.labMarkdown = '';

        // Configure marked.js for syntax highlighting
        if (typeof marked !== 'undefined' && typeof hljs !== 'undefined') {
            marked.setOptions({
                breaks: true,
                gfm: true,
                headerIds: true,
                mangle: false,
                sanitize: false,
                highlight: function(code, lang) {
                    if (lang && hljs.getLanguage(lang)) {
                        try {
                            return hljs.highlight(code, { language: lang }).value;
                        } catch (err) {
                            console.error('Highlight error:', err);
                        }
                    }
                    return hljs.highlightAuto(code).value;
                }
            });
        }

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
            this.filterFeatures();
        });

        // Domain filtering
        document.querySelectorAll('input[name="domain"]').forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.renderFeatures();
            });
        });

        // Test features filtering
        const testFeatureToggle = document.getElementById('show-test-features');
        if (testFeatureToggle) {
            testFeatureToggle.addEventListener('change', () => {
                this.renderFeatures();
                // Also update presentation and lab feature selectors
                const presentationContainer = document.getElementById('presentation-features');
                const labContainer = document.getElementById('lab-features');
                if (presentationContainer) {
                    this.populateFeatureSelector('presentation-features');
                }
                if (labContainer) {
                    this.populateFeatureSelector('lab-features');
                }
            });
        }

        // Modal close on outside click
        document.getElementById('add-feature-modal').addEventListener('click', (e) => {
            if (e.target.id === 'add-feature-modal') {
                this.closeAddFeatureModal();
            }
        });

        // Content preview modal close on outside click
        document.getElementById('content-preview-modal').addEventListener('click', (e) => {
            if (e.target.id === 'content-preview-modal') {
                this.closeContentPreview();
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
            case 'analytics':
                this.loadAnalytics();
                break;
        }
    }

    // Feature Management
    async loadFeatures() {
        try {
            this.showLoading('features-table-body');

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
        const tbody = document.getElementById('features-table-body');

        if (this.features.length === 0) {
            tbody.innerHTML = '<tr><td colspan="9" style="text-align: center; padding: 40px; color: #718096;"><i class="fas fa-box-open"></i><br>No features found. Add some features to get started!</td></tr>';
            return;
        }

        // Filter features to show
        const testToggle = document.getElementById('show-test-features');
        const showTestFeatures = testToggle ? testToggle.checked : false;

        let featuresToRender = this.features.filter(feature => {
            const isTest = this.isTestFeature(feature);
            return !isTest || showTestFeatures;
        });

        // Apply additional filters
        featuresToRender = this.applyFeatureFilters(featuresToRender);

        let html = '';
        for (const feature of featuresToRender) {
            const created = new Date(feature.created_at).toLocaleString('en-US', {
                month: 'short', day: 'numeric', year: 'numeric'
            });

            // Research status
            const research = feature.content_research || {};
            const status = research.status || 'pending';
            const hasLlmExtracted = research.llm_extracted && research.llm_extracted.summary;

            let statusBadge = '';
            switch(status) {
                case 'completed':
                    statusBadge = hasLlmExtracted
                        ? '<span class="status-badge status-completed"><i class="fas fa-check-circle"></i> Complete</span>'
                        : '<span class="status-badge status-pending"><i class="fas fa-clock"></i> Empty</span>';
                    break;
                case 'in_progress':
                    statusBadge = '<span class="status-badge status-progress"><i class="fas fa-spinner fa-pulse"></i> In Progress</span>';
                    break;
                case 'failed':
                    statusBadge = '<span class="status-badge status-failed"><i class="fas fa-exclamation-circle"></i> Failed</span>';
                    break;
                default:
                    statusBadge = '<span class="status-badge status-pending"><i class="fas fa-minus-circle"></i> Pending</span>';
            }

            // Docs indicator
            const docsCount = feature.documentation_links?.length || 0;
            const docsInfo = docsCount > 0
                ? `<span class="docs-badge"><i class="fas fa-link"></i> ${docsCount}</span>`
                : '<span style="color: #cbd5e0;">-</span>';

            // Benefits count
            const benefitsCount = feature.benefits?.length || 0;

            // Research timestamp
            let researchedTime = '-';
            if (research.last_updated && (status === 'completed' || status === 'failed')) {
                researchedTime = new Date(research.last_updated).toLocaleString('en-US', {
                    month: 'short', day: 'numeric', year: 'numeric',
                    hour: 'numeric', minute: '2-digit'
                });
            }

            html += `
                <tr>
                    <td><input type="checkbox" class="feature-checkbox" value="${feature.id}" onchange="window.app.updateBulkButtons()"></td>
                    <td class="title-cell">
                        <div class="feature-name-cell">
                            <strong>${feature.name}</strong>
                            <button class="btn-expand" onclick="window.app.toggleFeatureDetails('${feature.id}')" title="Show details">
                                <i class="fas fa-chevron-down" id="icon-${feature.id}"></i>
                            </button>
                        </div>
                    </td>
                    <td><span class="domain-badge domain-${feature.domain}">${feature.domain}</span></td>
                    <td class="number-cell">${benefitsCount}</td>
                    <td>${statusBadge}</td>
                    <td class="timestamp-cell">${researchedTime}</td>
                    <td>${docsInfo}</td>
                    <td class="timestamp-cell">${created}</td>
                    <td class="actions-cell">
                        ${status === 'pending' || status === 'failed' ? `
                            <button class="btn-icon" onclick="window.app.triggerResearch('${feature.id}')" title="Start Research">
                                <i class="fas fa-search"></i>
                            </button>
                        ` : status === 'completed' ? `
                            <button class="btn-icon" onclick="window.app.viewResearch('${feature.id}')" title="View Research">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="btn-icon" onclick="window.app.triggerResearch('${feature.id}')" title="Re-run Research">
                                <i class="fas fa-sync-alt"></i>
                            </button>
                        ` : `
                            <button class="btn-icon" title="Research In Progress" disabled>
                                <i class="fas fa-spinner fa-pulse"></i>
                            </button>
                        `}
                        <button class="btn-icon" onclick="app.editFeature('${feature.id}')" title="Edit">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn-icon" onclick="app.deleteFeature('${feature.id}')" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
                <tr id="details-row-${feature.id}" class="details-row" style="display: none;">
                    <td colspan="9" class="details-cell">
                        <div class="feature-details-expanded">
                            <div class="details-section">
                                <strong>Description:</strong>
                                <p>${feature.description}</p>
                            </div>

                            ${feature.benefits && feature.benefits.length > 0 ? `
                                <div class="details-section">
                                    <strong>Benefits:</strong>
                                    <ul>
                                        ${feature.benefits.map(b => `<li>${b}</li>`).join('')}
                                    </ul>
                                </div>
                            ` : ''}

                            ${feature.documentation_links && feature.documentation_links.length > 0 ? `
                                <div class="details-section">
                                    <strong>Documentation Links:</strong>
                                    <ul>
                                        ${feature.documentation_links.map(link => `<li><a href="${link}" target="_blank">${link}</a></li>`).join('')}
                                    </ul>
                                </div>
                            ` : ''}

                            ${hasLlmExtracted ? `
                                <div class="details-section ai-section">
                                    <h4>AI-Extracted Content</h4>

                                    ${research.llm_extracted.version_info ? `
                                        <div class="ai-version-badge">${research.llm_extracted.version_info}</div>
                                    ` : ''}

                                    <div class="ai-subsection">
                                        <strong>Summary:</strong>
                                        <p>${research.llm_extracted.summary || 'No summary available'}</p>
                                    </div>

                                    ${research.llm_extracted.key_capabilities && research.llm_extracted.key_capabilities.length > 0 ? `
                                        <div class="ai-subsection">
                                            <strong>Key Capabilities:</strong>
                                            <ul>
                                                ${research.llm_extracted.key_capabilities.map(cap => `<li>${cap}</li>`).join('')}
                                            </ul>
                                        </div>
                                    ` : ''}

                                    ${research.llm_extracted.use_cases && research.llm_extracted.use_cases.length > 0 ? `
                                        <div class="ai-subsection">
                                            <strong>Use Cases:</strong>
                                            <ul>
                                                ${research.llm_extracted.use_cases.map(uc => `<li>${uc}</li>`).join('')}
                                            </ul>
                                        </div>
                                    ` : ''}

                                    ${research.llm_extracted.prerequisites && research.llm_extracted.prerequisites.length > 0 ? `
                                        <div class="ai-subsection">
                                            <strong>Prerequisites:</strong>
                                            <ul>
                                                ${research.llm_extracted.prerequisites.map(pre => `<li>${pre}</li>`).join('')}
                                            </ul>
                                        </div>
                                    ` : ''}

                                    ${research.llm_extracted.implementation_steps && research.llm_extracted.implementation_steps.length > 0 ? `
                                        <div class="ai-subsection">
                                            <strong>Implementation Steps:</strong>
                                            <ol class="steps-list">
                                                ${research.llm_extracted.implementation_steps.map(step => `<li>${step}</li>`).join('')}
                                            </ol>
                                        </div>
                                    ` : ''}

                                    ${research.llm_extracted.configuration_examples && research.llm_extracted.configuration_examples.length > 0 ? `
                                        <div class="ai-subsection">
                                            <strong>Configuration Examples:</strong>
                                            <ul class="code-list">
                                                ${research.llm_extracted.configuration_examples.map(conf => `<li><pre><code>${conf.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</code></pre></li>`).join('')}
                                            </ul>
                                        </div>
                                    ` : ''}

                                    ${research.llm_extracted.api_commands && research.llm_extracted.api_commands.length > 0 ? `
                                        <div class="ai-subsection">
                                            <strong>API Commands:</strong>
                                            <ul class="code-list">
                                                ${research.llm_extracted.api_commands.map(cmd => `<li><pre><code>${cmd.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</code></pre></li>`).join('')}
                                            </ul>
                                        </div>
                                    ` : ''}

                                    ${research.llm_extracted.metrics_examples && research.llm_extracted.metrics_examples.length > 0 ? `
                                        <div class="ai-subsection">
                                            <strong>Performance Metrics:</strong>
                                            <ul>
                                                ${research.llm_extracted.metrics_examples.map(metric => `<li>${metric}</li>`).join('')}
                                            </ul>
                                        </div>
                                    ` : ''}

                                    ${research.llm_extracted.comparisons && research.llm_extracted.comparisons.length > 0 ? `
                                        <div class="ai-subsection">
                                            <strong>Comparisons:</strong>
                                            <ul>
                                                ${research.llm_extracted.comparisons.map(comp => `<li>${comp}</li>`).join('')}
                                            </ul>
                                        </div>
                                    ` : ''}

                                    ${research.llm_extracted.limitations && research.llm_extracted.limitations.length > 0 ? `
                                        <div class="ai-subsection ai-limitations">
                                            <strong>Limitations & Caveats:</strong>
                                            <ul>
                                                ${research.llm_extracted.limitations.map(lim => `<li>${lim}</li>`).join('')}
                                            </ul>
                                        </div>
                                    ` : ''}

                                    ${(research.llm_extracted.hands_on_exercise_ideas?.length > 0 ||
                                       research.llm_extracted.sample_data_suggestions?.length > 0 ||
                                       research.llm_extracted.validation_checkpoints?.length > 0 ||
                                       research.llm_extracted.common_pitfalls?.length > 0) ? `
                                        <div class="ai-section-divider">
                                            <h5><i class="fas fa-flask"></i> Lab Generation Hints</h5>
                                        </div>

                                        ${research.llm_extracted.hands_on_exercise_ideas?.length > 0 ? `
                                            <div class="ai-subsection ai-lab-hint">
                                                <strong>Hands-On Exercise Ideas:</strong>
                                                <ul>
                                                    ${research.llm_extracted.hands_on_exercise_ideas.map(ex => `<li>${ex}</li>`).join('')}
                                                </ul>
                                            </div>
                                        ` : ''}

                                        ${research.llm_extracted.sample_data_suggestions?.length > 0 ? `
                                            <div class="ai-subsection ai-lab-hint">
                                                <strong>Sample Data Suggestions:</strong>
                                                <ul>
                                                    ${research.llm_extracted.sample_data_suggestions.map(data => `<li>${data}</li>`).join('')}
                                                </ul>
                                            </div>
                                        ` : ''}

                                        ${research.llm_extracted.validation_checkpoints?.length > 0 ? `
                                            <div class="ai-subsection ai-lab-hint">
                                                <strong>Validation Checkpoints:</strong>
                                                <ul>
                                                    ${research.llm_extracted.validation_checkpoints.map(check => `<li>${check}</li>`).join('')}
                                                </ul>
                                            </div>
                                        ` : ''}

                                        ${research.llm_extracted.common_pitfalls?.length > 0 ? `
                                            <div class="ai-subsection ai-lab-hint">
                                                <strong>Common Pitfalls:</strong>
                                                <ul>
                                                    ${research.llm_extracted.common_pitfalls.map(pit => `<li>${pit}</li>`).join('')}
                                                </ul>
                                            </div>
                                        ` : ''}
                                    ` : ''}

                                    ${(research.llm_extracted.demo_scenario ||
                                       research.llm_extracted.business_impact_metrics?.length > 0 ||
                                       research.llm_extracted.competitive_advantages?.length > 0 ||
                                       research.llm_extracted.visual_aids_suggestions?.length > 0) ? `
                                        <div class="ai-section-divider">
                                            <h5><i class="fas fa-presentation"></i> Presentation Generation Hints</h5>
                                        </div>

                                        ${research.llm_extracted.demo_scenario ? `
                                            <div class="ai-subsection ai-presentation-hint">
                                                <strong>Demo Scenario:</strong>
                                                <p>${research.llm_extracted.demo_scenario}</p>
                                            </div>
                                        ` : ''}

                                        ${research.llm_extracted.business_impact_metrics?.length > 0 ? `
                                            <div class="ai-subsection ai-presentation-hint">
                                                <strong>Business Impact Metrics:</strong>
                                                <ul>
                                                    ${research.llm_extracted.business_impact_metrics.map(metric => `<li>${metric}</li>`).join('')}
                                                </ul>
                                            </div>
                                        ` : ''}

                                        ${research.llm_extracted.competitive_advantages?.length > 0 ? `
                                            <div class="ai-subsection ai-presentation-hint">
                                                <strong>Competitive Advantages:</strong>
                                                <ul>
                                                    ${research.llm_extracted.competitive_advantages.map(adv => `<li>${adv}</li>`).join('')}
                                                </ul>
                                            </div>
                                        ` : ''}

                                        ${research.llm_extracted.visual_aids_suggestions?.length > 0 ? `
                                            <div class="ai-subsection ai-presentation-hint">
                                                <strong>Visual Aids Suggestions:</strong>
                                                <ul>
                                                    ${research.llm_extracted.visual_aids_suggestions.map(vis => `<li>${vis}</li>`).join('')}
                                                </ul>
                                            </div>
                                        ` : ''}
                                    ` : ''}
                                </div>
                            ` : ''}
                        </div>
                    </td>
                </tr>
            `;
        }

        tbody.innerHTML = html;
    }

    applyFeatureFilters(features) {
        const searchTerm = document.getElementById('feature-search')?.value.toLowerCase() || '';
        const researchFilter = document.getElementById('research-status-filter')?.value || '';

        return features.filter(feature => {
            // Search filter
            if (searchTerm) {
                const searchable = [
                    feature.name,
                    feature.description,
                    ...(feature.benefits || [])
                ].join(' ').toLowerCase();
                if (!searchable.includes(searchTerm)) {
                    return false;
                }
            }

            // Research status filter
            if (researchFilter) {
                const status = feature.content_research?.status || 'pending';
                if (status !== researchFilter) {
                    return false;
                }
            }

            return true;
        });
    }

    filterFeatures() {
        this.renderFeatures();
    }

    sortFeatures(column) {
        if (!this.featureSortColumn || this.featureSortColumn !== column) {
            this.featureSortColumn = column;
            this.featureSortDirection = 'asc';
        } else {
            this.featureSortDirection = this.featureSortDirection === 'asc' ? 'desc' : 'asc';
        }

        this.features.sort((a, b) => {
            let aVal, bVal;
            switch(column) {
                case 'name': aVal = a.name; bVal = b.name; break;
                case 'domain': aVal = a.domain; bVal = b.domain; break;
                case 'benefits': aVal = a.benefits?.length || 0; bVal = b.benefits?.length || 0; break;
                case 'research':
                    aVal = a.content_research?.status || 'pending';
                    bVal = b.content_research?.status || 'pending';
                    break;
                case 'researched':
                    aVal = a.content_research?.last_updated ? new Date(a.content_research.last_updated) : new Date(0);
                    bVal = b.content_research?.last_updated ? new Date(b.content_research.last_updated) : new Date(0);
                    break;
                case 'docs':
                    aVal = a.documentation_links?.length || 0;
                    bVal = b.documentation_links?.length || 0;
                    break;
                case 'created': aVal = new Date(a.created_at); bVal = new Date(b.created_at); break;
                default: return 0;
            }

            if (aVal < bVal) return this.featureSortDirection === 'asc' ? -1 : 1;
            if (aVal > bVal) return this.featureSortDirection === 'asc' ? 1 : -1;
            return 0;
        });

        this.renderFeatures();
    }

    toggleFeatureDetails(featureId) {
        const detailsRow = document.getElementById(`details-row-${featureId}`);
        const icon = document.getElementById(`icon-${featureId}`);

        if (detailsRow.style.display === 'none') {
            detailsRow.style.display = 'table-row';
            icon.className = 'fas fa-chevron-up';
        } else {
            detailsRow.style.display = 'none';
            icon.className = 'fas fa-chevron-down';
        }
    }

    toggleAllFeatures() {
        const selectAll = document.getElementById('select-all-features');
        const checkboxes = document.querySelectorAll('.feature-checkbox');
        checkboxes.forEach(cb => cb.checked = selectAll.checked);
        this.updateBulkButtons();
    }

    updateBulkButtons() {
        const checked = document.querySelectorAll('.feature-checkbox:checked').length;
        document.getElementById('bulk-delete-btn').style.display = checked > 0 ? 'inline-block' : 'none';
        document.getElementById('bulk-research-btn').style.display = checked > 0 ? 'inline-block' : 'none';
    }

    async deleteSelectedFeatures() {
        const selected = Array.from(document.querySelectorAll('.feature-checkbox:checked')).map(cb => cb.value);
        if (selected.length === 0) return;

        if (!confirm(`Delete ${selected.length} feature(s)?`)) return;

        for (const id of selected) {
            await this.deleteFeature(id, false);
        }
        await this.loadFeatures();
        this.showToast(`Deleted ${selected.length} feature(s)`, 'success');
    }

    async researchSelectedFeatures() {
        const selected = Array.from(document.querySelectorAll('.feature-checkbox:checked')).map(cb => cb.value);
        if (selected.length === 0) return;

        this.showToast(`Starting research for ${selected.length} feature(s)...`, 'info');

        for (const id of selected) {
            await this.triggerResearch(id, false);
        }
        await this.loadFeatures();
        this.showToast(`Research completed for ${selected.length} feature(s)`, 'success');
    }

    async triggerResearch(featureId, showToast = true) {
        // Get feature name for confirmation dialog
        const feature = this.features.find(f => f.id === featureId);
        const featureName = feature ? feature.name : 'this feature';
        const isRerun = feature?.content_research?.status === 'completed';

        // Show confirmation dialog
        const confirmMessage = isRerun
            ? `Re-run research for "${featureName}"?\n\n` +
              `This will:\n` +
              `• Scrape documentation URLs again\n` +
              `• Use LLM to extract structured content (incurs API costs)\n` +
              `• Overwrite existing research data\n\n` +
              `Continue?`
            : `Start research for "${featureName}"?\n\n` +
              `This will:\n` +
              `• Scrape documentation URLs\n` +
              `• Use LLM to extract structured content (incurs API costs)\n` +
              `• Enable enhanced presentation and lab generation\n\n` +
              `Continue?`;

        if (!confirm(confirmMessage)) {
            return;
        }

        try {
            const response = await fetch(`${this.apiBase}/features/${featureId}/research`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    feature_id: featureId,
                    force_refresh: isRerun
                })
            });

            if (response.ok) {
                if (showToast) {
                    this.showToast(isRerun ? 'Research re-started successfully' : 'Research started successfully', 'success');
                }
                await this.loadFeatures();
            } else {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Research request failed');
            }
        } catch (error) {
            console.error('Research failed:', error);
            if (showToast) {
                this.showToast(`Research failed: ${error.message}`, 'error');
            }
        }
    }

    async viewResearch(featureId) {
        window.open(`/features/${featureId}/research/detailed`, '_blank');
    }

    renderContentResearchSection(feature) {
        const research = feature.content_research;
        if (!research) {
            return `
                <div class="content-research">
                    <button class="btn btn-primary btn-small" onclick="app.triggerContentResearch('${feature.id}')">
                        <i class="fas fa-search"></i> Research Content
                    </button>
                </div>
            `;
        }

        const statusIcon = {
            pending: 'fas fa-clock',
            in_progress: 'fas fa-spinner fa-spin',
            completed: 'fas fa-check-circle',
            failed: 'fas fa-exclamation-triangle'
        }[research.status] || 'fas fa-question-circle';

        const statusColor = {
            pending: 'warning',
            in_progress: 'info',
            completed: 'success',
            failed: 'danger'
        }[research.status] || 'secondary';

        return `
            <div class="content-research">
                <div class="research-status ${statusColor}">
                    <i class="${statusIcon}"></i>
                    <span>Research: ${research.status}</span>
                </div>

                ${research.status === 'completed' ? `
                    <div class="research-summary">
                        <small>
                            ${research.primary_sources ? research.primary_sources.length : 0} sources analyzed
                            ${research.extracted_content?.key_concepts ? `• ${research.extracted_content.key_concepts.length} key concepts` : ''}
                            ${research.embeddings?.feature_summary ? '• AI embeddings generated' : ''}
                        </small>
                    </div>
                    <div class="research-actions">
                        <button class="btn btn-secondary btn-small" onclick="window.app.viewContentResearch('${feature.id}')">
                            <i class="fas fa-eye"></i> View Research
                        </button>
                        <button class="btn btn-secondary btn-small" onclick="app.triggerContentResearch('${feature.id}', true)">
                            <i class="fas fa-refresh"></i> Refresh
                        </button>
                    </div>
                ` : research.status === 'failed' ? `
                    <div class="research-actions">
                        <button class="btn btn-primary btn-small" onclick="app.triggerContentResearch('${feature.id}', true)">
                            <i class="fas fa-redo"></i> Retry Research
                        </button>
                    </div>
                ` : research.status === 'pending' ? `
                    <div class="research-actions">
                        <button class="btn btn-primary btn-small" onclick="app.triggerContentResearch('${feature.id}', true)">
                            <i class="fas fa-play"></i> Start Research
                        </button>
                    </div>
                ` : ''}
            </div>
        `;
    }

    async triggerContentResearch(featureId, forceRefresh = false) {
        try {
            const response = await fetch(`${this.apiBase}/features/${featureId}/research`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    feature_id: featureId,
                    force_refresh: forceRefresh
                })
            });

            if (!response.ok) {
                throw new Error(`Research failed: ${response.statusText}`);
            }

            const result = await response.json();
            this.showToast(`Content research ${result.research_status} for feature`, 'success');

            // Refresh the feature data to show updated research status
            setTimeout(() => this.loadFeatures(), 1000);

            // If modal is currently open for this feature, refresh it
            const modal = document.getElementById('content-research-modal');
            if (modal && modal.dataset.featureId === featureId) {
                setTimeout(() => this.viewContentResearch(featureId), 1500);
            }

        } catch (error) {
            console.error('Content research failed:', error);
            this.showToast(`Content research failed: ${error.message}`, 'error');
        }
    }

    async viewContentResearch(featureId) {
        try {
            const response = await fetch(`${this.apiBase}/features/${featureId}/research/detailed`);
            if (!response.ok) {
                throw new Error(`Failed to load research data: ${response.statusText}`);
            }

            const feature = await response.json();
            this.showContentResearchModal(feature);

        } catch (error) {
            console.error('Failed to load content research:', error);
            this.showToast(`Failed to load research data: ${error.message}`, 'error');
        }
    }

    showContentResearchModal(feature) {
        const research = feature.content_research;

        const modalHtml = `
            <div class="modal" id="content-research-modal" data-feature-id="${feature.feature_id}">
                <div class="modal-content large">
                    <div class="modal-header">
                        <h3>Content Research: ${feature.feature_name}</h3>
                        <div class="modal-header-actions">
                            <button class="btn btn-secondary btn-small" onclick="app.triggerContentResearch('${feature.feature_id}', true)" title="Refresh research data">
                                <i class="fas fa-refresh"></i> Refresh
                            </button>
                            <button class="close-btn" onclick="app.closeContentResearchModal()">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    </div>
                    <div class="modal-body">
                        <div class="research-tabs">
                            <div class="tab-nav">
                                <button class="tab-btn active" data-tab="summary">Summary</button>
                                <button class="tab-btn" data-tab="sources">Sources</button>
                                <button class="tab-btn" data-tab="insights">AI Insights</button>
                                <button class="tab-btn" data-tab="concepts">Key Concepts</button>
                            </div>

                            <div class="tab-panel active" id="summary-panel">
                                <h4>Research Summary</h4>
                                <div class="summary-stats">
                                    <div class="stat">
                                        <span class="label">Status:</span>
                                        <span class="value">${research.status}</span>
                                    </div>
                                    <div class="stat">
                                        <span class="label">Last Updated:</span>
                                        <span class="value">${new Date(research.last_updated).toLocaleString()}</span>
                                    </div>
                                    <div class="stat">
                                        <span class="label">Primary Sources:</span>
                                        <span class="value">${research.primary_sources?.length || 0}</span>
                                    </div>
                                    <div class="stat">
                                        <span class="label">Related Sources:</span>
                                        <span class="value">${research.related_sources?.length || 0}</span>
                                    </div>
                                </div>

                                ${research.llm_extracted ? `
                                    <div class="llm-extracted-content">
                                        <h5>🤖 AI-Generated Summary</h5>
                                        <div class="llm-summary">
                                            <p>${research.llm_extracted.summary}</p>
                                        </div>

                                        ${research.llm_extracted.use_cases?.length ? `
                                            <div class="llm-section">
                                                <h6>Use Cases</h6>
                                                <ul>
                                                    ${research.llm_extracted.use_cases.map(useCase => `<li>${useCase}</li>`).join('')}
                                                </ul>
                                            </div>
                                        ` : ''}

                                        ${research.llm_extracted.key_capabilities?.length ? `
                                            <div class="llm-section">
                                                <h6>Key Capabilities</h6>
                                                <ul>
                                                    ${research.llm_extracted.key_capabilities.map(capability => `<li>${capability}</li>`).join('')}
                                                </ul>
                                            </div>
                                        ` : ''}

                                        ${research.llm_extracted.benefits?.length ? `
                                            <div class="llm-section">
                                                <h6>Benefits</h6>
                                                <ul>
                                                    ${research.llm_extracted.benefits.map(benefit => `<li>${benefit}</li>`).join('')}
                                                </ul>
                                            </div>
                                        ` : ''}

                                        ${research.llm_extracted.technical_requirements?.length ? `
                                            <div class="llm-section">
                                                <h6>Technical Requirements</h6>
                                                <ul>
                                                    ${research.llm_extracted.technical_requirements.map(req => `<li>${req}</li>`).join('')}
                                                </ul>
                                            </div>
                                        ` : ''}

                                        <div class="llm-metadata">
                                            <small>
                                                <strong>Target Audience:</strong> ${research.llm_extracted.target_audience || 'developers'} •
                                                <strong>Complexity:</strong> ${research.llm_extracted.complexity_level || 'intermediate'} •
                                                <strong>Model:</strong> ${research.llm_extracted.model_used || 'N/A'}
                                            </small>
                                        </div>
                                    </div>
                                ` : ''}

                                ${research.ai_insights?.technical_summary ? `
                                    <div class="technical-summary">
                                        <h5>Technical Summary</h5>
                                        <p>${research.ai_insights.technical_summary}</p>
                                    </div>
                                ` : ''}

                                ${research.ai_insights?.business_value ? `
                                    <div class="business-value">
                                        <h5>Business Value</h5>
                                        <p>${research.ai_insights.business_value}</p>
                                    </div>
                                ` : ''}
                            </div>

                            <div class="tab-panel" id="sources-panel">
                                <h4>Documentation Sources</h4>
                                ${this.renderSourcesList(research.primary_sources, 'Primary')}
                                ${research.related_sources?.length ? this.renderSourcesList(research.related_sources, 'Related') : ''}
                            </div>

                            <div class="tab-panel" id="insights-panel">
                                <h4>AI-Generated Insights</h4>
                                ${this.renderAIInsights(research.ai_insights)}
                            </div>

                            <div class="tab-panel" id="concepts-panel">
                                <h4>Key Concepts & Examples</h4>
                                ${this.renderExtractedContent(research.extracted_content)}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);

        // Show the modal
        const modal = document.getElementById('content-research-modal');
        if (modal) {
            modal.style.display = 'block';

            // Close modal when clicking outside
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeContentResearchModal();
                }
            });
        }

        // Setup tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tabName = e.target.dataset.tab;
                this.switchResearchTab(tabName);
            });
        });
    }

    renderSourcesList(sources, type) {
        if (!sources || sources.length === 0) return '';

        return `
            <div class="sources-section">
                <h5>${type} Sources (${sources.length})</h5>
                <div class="sources-list">
                    ${sources.map(source => `
                        <div class="source-item">
                            <div class="source-header">
                                <h6>${source.title}</h6>
                                <span class="source-type">${source.content_type}</span>
                            </div>
                            <div class="source-meta">
                                <a href="${source.url}" target="_blank" class="source-url">
                                    <i class="fas fa-external-link-alt"></i> ${source.url}
                                </a>
                                <span class="word-count">${source.word_count} words</span>
                            </div>
                            ${source.content ? `
                                <div class="source-preview">
                                    ${source.content.substring(0, 200)}...
                                </div>
                            ` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    renderAIInsights(insights) {
        if (!insights) return '<p>No AI insights available.</p>';

        return `
            <div class="insights-grid">
                ${insights.implementation_complexity ? `
                    <div class="insight-item">
                        <h5>Implementation Complexity</h5>
                        <p>${insights.implementation_complexity}</p>
                    </div>
                ` : ''}

                ${insights.learning_curve ? `
                    <div class="insight-item">
                        <h5>Learning Curve</h5>
                        <p>${insights.learning_curve}</p>
                    </div>
                ` : ''}

                ${insights.recommended_audience?.length ? `
                    <div class="insight-item">
                        <h5>Recommended Audience</h5>
                        <ul>
                            ${insights.recommended_audience.map(audience => `<li>${audience}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}

                ${insights.content_themes?.length ? `
                    <div class="insight-item">
                        <h5>Content Themes</h5>
                        <div class="theme-tags">
                            ${insights.content_themes.map(theme => `<span class="theme-tag">${theme}</span>`).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderExtractedContent(content) {
        if (!content) return '<p>No extracted content available.</p>';

        return `
            ${content.key_concepts?.length ? `
                <div class="content-section">
                    <h5>Key Concepts (${content.key_concepts.length})</h5>
                    <div class="concept-tags">
                        ${content.key_concepts.map(concept => `<span class="concept-tag">${concept}</span>`).join('')}
                    </div>
                </div>
            ` : ''}

            ${content.use_cases?.length ? `
                <div class="content-section">
                    <h5>Use Cases</h5>
                    <div class="use-cases">
                        ${content.use_cases.map(useCase => `
                            <div class="use-case">
                                <h6>${useCase.title}</h6>
                                <p>${useCase.description}</p>
                                <div class="use-case-meta">
                                    <span class="complexity">${useCase.complexity}</span>
                                    <span class="time">${useCase.estimated_time}</span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            ` : ''}

            ${content.configuration_examples?.length ? `
                <div class="content-section">
                    <h5>Configuration Examples</h5>
                    <div class="code-examples">
                        ${content.configuration_examples.map(example => `
                            <div class="code-example">
                                <h6>${example.title}</h6>
                                <p>${example.description}</p>
                                <pre><code class="language-${example.language}">${example.code}</code></pre>
                            </div>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
        `;
    }

    switchResearchTab(tabName) {
        // Remove active classes
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.remove('active'));

        // Add active classes
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        document.getElementById(`${tabName}-panel`).classList.add('active');
    }

    closeContentResearchModal() {
        const modal = document.getElementById('content-research-modal');
        if (modal) {
            modal.remove();
        }
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

    isTestFeature(feature) {
        // Check if feature is a test feature based on name and description
        // Only flag as test if contains specific test-related patterns
        const nameText = feature.name.toLowerCase();
        const descText = feature.description.toLowerCase();

        // More specific patterns to avoid false positives
        const testPatterns = [
            /\btest\b/,                    // "test" as a whole word
            /\btesting\b/,                  // "testing" as a whole word
            /test feature/,                 // "test feature" phrase
            /validation test/,              // "validation test" phrase
            /serverless persistence/        // specific test feature name
        ];

        const isTest = testPatterns.some(pattern =>
            pattern.test(nameText) || pattern.test(descText)
        );

        console.log(`Feature "${feature.name}" - Test: ${isTest}`);
        return isTest;
    }

    filterFeaturesByTestStatus() {
        console.log('Test feature toggle clicked!');
        // Re-render features with current test filter setting
        this.renderFeatures();

        // Also update presentation and lab feature selectors
        const presentationContainer = document.getElementById('presentation-features');
        const labContainer = document.getElementById('lab-features');

        if (presentationContainer) {
            this.populateFeatureSelector('presentation-features');
        }

        if (labContainer) {
            this.populateFeatureSelector('lab-features');
        }
    }

    populateFeatureSelector(containerId, filterDomain = null) {
        const container = document.getElementById(containerId);
        let features = [...this.features];

        // Preserve currently checked features before re-rendering
        const checkedFeatures = new Set(
            Array.from(container.querySelectorAll('input[type="checkbox"]:checked'))
                .map(cb => cb.value)
        );

        // Apply test feature filtering - hide test features by default
        const testToggle = document.getElementById('show-test-features');
        const showTestFeatures = testToggle ? testToggle.checked : false;

        features = features.filter(feature => {
            const isTest = this.isTestFeature(feature);
            return !isTest || showTestFeatures;
        });

        // Filter by domain if specified
        if (filterDomain && filterDomain !== 'all_domains') {
            features = features.filter(f => f.domain === filterDomain);
        }

        // Sort by name by default
        features.sort((a, b) => a.name.localeCompare(b.name));

        // Store features for search/sort
        container.dataset.allFeatures = JSON.stringify(features);

        // Render as list, preserving checked state
        // For lab features, use radio buttons (single selection only)
        const inputType = containerId === 'lab-features' ? 'radio' : 'checkbox';
        const inputName = containerId === 'lab-features' ? 'selected-lab-feature' : 'selected-features';

        container.innerHTML = features.map(feature => `
            <div class="feature-list-item" data-feature-id="${feature.id}">
                <input type="${inputType}" value="${feature.id}" name="${inputName}" ${checkedFeatures.has(feature.id) ? 'checked' : ''}>
                <div class="feature-list-item-content">
                    <div class="feature-list-item-name">${feature.name}</div>
                    <div class="feature-list-item-meta">
                        <span class="feature-list-item-domain ${feature.domain}">${feature.domain}</span>
                        <span class="feature-list-item-date">${feature.created_at ? new Date(feature.created_at).toLocaleDateString() : ''}</span>
                    </div>
                </div>
            </div>
        `).join('');

        // Setup search and sort handlers if not already done
        this.setupFeatureSelectorHandlers(containerId);
    }

    setupFeatureSelectorHandlers(containerId) {
        const prefix = containerId.replace('-features', '');
        const searchInput = document.getElementById(`${prefix}-feature-search`);
        const sortSelect = document.getElementById(`${prefix}-sort`);

        if (searchInput && !searchInput.dataset.handlerSet) {
            searchInput.dataset.handlerSet = 'true';
            searchInput.addEventListener('input', (e) => {
                this.filterFeatureList(containerId, e.target.value, sortSelect?.value || 'name');
            });
        }

        if (sortSelect && !sortSelect.dataset.handlerSet) {
            sortSelect.dataset.handlerSet = 'true';
            sortSelect.addEventListener('change', (e) => {
                this.filterFeatureList(containerId, searchInput?.value || '', e.target.value);
            });
        }
    }

    filterFeatureList(containerId, searchTerm, sortBy) {
        const container = document.getElementById(containerId);
        const featuresData = container.dataset.allFeatures;

        if (!featuresData) return;

        let features = JSON.parse(featuresData);

        // Filter by search term
        if (searchTerm) {
            const term = searchTerm.toLowerCase();
            features = features.filter(f =>
                f.name.toLowerCase().includes(term) ||
                f.description.toLowerCase().includes(term) ||
                f.domain.toLowerCase().includes(term)
            );
        }

        // Sort features
        features.sort((a, b) => {
            switch(sortBy) {
                case 'domain':
                    return a.domain.localeCompare(b.domain) || a.name.localeCompare(b.name);
                case 'date':
                    return new Date(b.created_at || 0) - new Date(a.created_at || 0);
                case 'name':
                default:
                    return a.name.localeCompare(b.name);
            }
        });

        // Re-render filtered/sorted list
        // For lab features, use radio buttons (single selection only)
        const inputType = containerId === 'lab-features' ? 'radio' : 'checkbox';
        const inputName = containerId === 'lab-features' ? 'selected-lab-feature' : 'selected-features';

        container.innerHTML = features.map(feature => `
            <div class="feature-list-item" data-feature-id="${feature.id}">
                <input type="${inputType}" value="${feature.id}" name="${inputName}">
                <div class="feature-list-item-content">
                    <div class="feature-list-item-name">${feature.name}</div>
                    <div class="feature-list-item-meta">
                        <span class="feature-list-item-domain ${feature.domain}">${feature.domain}</span>
                        <span class="feature-list-item-date">${feature.created_at ? new Date(feature.created_at).toLocaleDateString() : ''}</span>
                    </div>
                </div>
            </div>
        `).join('');
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
            documentation_links: this.parseTextareaLines(document.getElementById('feature-links').value)
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
                this.closeAddFeatureModal();
                this.showToast('Feature added successfully!', 'success');

                // Reload all features from server to get complete data
                await this.loadFeatures();
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
        try {
            // First get the current feature data
            const response = await fetch(`${this.apiBase}/features/${featureId}`);
            if (!response.ok) {
                throw new Error(`Failed to load feature: ${response.statusText}`);
            }

            const feature = await response.json();
            this.showEditFeatureModal(feature);

        } catch (error) {
            console.error('Failed to load feature for editing:', error);
            this.showToast(`Failed to load feature: ${error.message}`, 'error');
        }
    }

    showEditFeatureModal(feature) {
        const modalHtml = `
            <div class="modal" id="edit-feature-modal">
                <div class="modal-content large">
                    <div class="modal-header">
                        <h3>Edit Feature: ${feature.name}</h3>
                        <button class="close-btn" onclick="window.app.closeEditFeatureModal()">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="modal-body">
                        <form id="edit-feature-form">
                            <div class="form-group">
                                <label for="edit-name">Feature Name *</label>
                                <input type="text" id="edit-name" name="name" value="${feature.name}" required>
                            </div>

                            <div class="form-group">
                                <label for="edit-description">Description *</label>
                                <textarea id="edit-description" name="description" rows="4" required>${feature.description}</textarea>
                            </div>

                            <div class="form-group">
                                <label for="edit-domain">Domain *</label>
                                <select id="edit-domain" name="domain" required>
                                    <option value="search" ${feature.domain === 'search' ? 'selected' : ''}>Search</option>
                                    <option value="observability" ${feature.domain === 'observability' ? 'selected' : ''}>Observability</option>
                                    <option value="security" ${feature.domain === 'security' ? 'selected' : ''}>Security</option>
                                </select>
                            </div>

                            <div class="form-group">
                                <label for="edit-benefits">Benefits</label>
                                <textarea id="edit-benefits" name="benefits" rows="3" placeholder="Enter benefits, one per line">${(feature.benefits || []).join('\n')}</textarea>
                            </div>

                            <div class="form-group">
                                <label for="edit-documentation-links">Documentation Links</label>
                                <textarea id="edit-documentation-links" name="documentation_links" rows="3" placeholder="Enter URLs, one per line">${(feature.documentation_links || []).join('\n')}</textarea>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" onclick="window.app.closeEditFeatureModal()">
                            Cancel
                        </button>
                        <button type="button" class="btn btn-primary" onclick="window.app.saveFeatureChanges('${feature.id}')">
                            <i class="fas fa-save"></i> Save Changes
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);

        // Show the modal
        const modal = document.getElementById('edit-feature-modal');
        if (modal) {
            modal.style.display = 'block';

            // Close modal when clicking outside
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeEditFeatureModal();
                }
            });
        }
    }

    async saveFeatureChanges(featureId) {
        try {
            const form = document.getElementById('edit-feature-form');
            const formData = new FormData(form);

            // Parse benefits and documentation links from textarea
            const benefits = formData.get('benefits').split('\n').map(b => b.trim()).filter(b => b.length > 0);
            const documentationLinks = formData.get('documentation_links').split('\n').map(l => l.trim()).filter(l => l.length > 0);

            const updateData = {
                name: formData.get('name'),
                description: formData.get('description'),
                domain: formData.get('domain'),
                benefits: benefits,
                documentation_links: documentationLinks
            };

            const response = await fetch(`${this.apiBase}/features/${featureId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(updateData)
            });

            if (!response.ok) {
                throw new Error(`Failed to update feature: ${response.statusText}`);
            }

            this.closeEditFeatureModal();
            this.showToast('Feature updated successfully!', 'success');

            // Refresh the features list to show updated data
            this.loadFeatures();

        } catch (error) {
            console.error('Failed to update feature:', error);
            this.showToast(`Failed to update feature: ${error.message}`, 'error');
        }
    }

    closeEditFeatureModal() {
        const modal = document.getElementById('edit-feature-modal');
        if (modal) {
            modal.remove();
        }
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
            audience: document.getElementById('presentation-audience').value,
            // Advanced Storytelling Features
            narrative_style: document.getElementById('narrative-style').value,
            talk_track_detail: document.getElementById('talk-track-detail').value,
            technical_depth: document.getElementById('technical-depth').value,
            include_customer_stories: document.getElementById('include-customer-stories').checked,
            competitive_positioning: document.getElementById('competitive-positioning').checked,
            storytelling_enabled: document.getElementById('storytelling-enabled').checked
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
        previewText += `**Slides:** ${slides.length}\n`;

        // Show storytelling information if available
        if (this.currentPresentation.story_arc) {
            const arc = this.currentPresentation.story_arc;
            previewText += `**Narrative Style:** ${arc.narrative_style || 'Standard'}\n`;
            previewText += `**Story Arc:** ${arc.positions ? arc.positions.length + ' story positions' : 'Classic structure'}\n`;
        }

        if (this.currentPresentation.talk_tracks && this.currentPresentation.talk_tracks.length > 0) {
            previewText += `**Talk Tracks:** ${this.currentPresentation.talk_tracks.length} comprehensive tracks included\n`;
        }

        if (this.currentPresentation.customer_stories && this.currentPresentation.customer_stories.length > 0) {
            previewText += `**Customer Stories:** ${this.currentPresentation.customer_stories.length} success stories\n`;
        }

        previewText += '\n' + '='.repeat(80) + '\n\n';

        // Show story arc overview if available
        if (this.currentPresentation.story_arc && this.currentPresentation.story_arc.positions) {
            previewText += `## 🎭 Story Arc Overview\n\n`;
            this.currentPresentation.story_arc.positions.forEach((position, index) => {
                previewText += `**${position.position}:** ${position.summary}\n`;
            });
            previewText += '\n' + '='.repeat(80) + '\n\n';
        }

        // Show slides with full content
        slides.forEach((slide, index) => {
            previewText += `## Slide ${index + 1}: ${slide.title}\n\n`;
            if (slide.subtitle) {
                previewText += `### ${slide.subtitle}\n\n`;
            }

            previewText += `${slide.content}\n\n`;

            if (slide.business_value) {
                previewText += `**Business Value:**\n${slide.business_value}\n\n`;
            }

            // Show speaker notes/talk track (check both locations)
            const speakerNotes = slide.speaker_notes ||
                                this.currentPresentation.talk_tracks?.find(track =>
                                    track.slide_number === index + 1 || track.slide_title === slide.title
                                )?.speaker_notes;

            if (speakerNotes) {
                previewText += `**🎤 Speaker Notes / Talk Track:**\n${speakerNotes}\n\n`;
            }

            previewText += '-'.repeat(80) + '\n\n';
        });

        // Show customer stories summary if available
        if (this.currentPresentation.customer_stories && this.currentPresentation.customer_stories.length > 0) {
            previewText += `## 💼 Customer Success Stories\n\n`;
            this.currentPresentation.customer_stories.forEach((story, index) => {
                previewText += `### ${story.company_name} (${story.industry})\n\n`;
                previewText += `**Challenge:** ${story.challenge}\n\n`;
                previewText += `**Solution:** ${story.solution}\n\n`;
                previewText += `**Outcome:** ${story.outcome}\n\n`;
                if (story.metrics && story.metrics.length > 0) {
                    previewText += `**Metrics:**\n`;
                    story.metrics.forEach(metric => {
                        previewText += `- ${metric}\n`;
                    });
                    previewText += '\n';
                }
                previewText += '-'.repeat(80) + '\n\n';
            });
        }

        // Store markdown for toggling
        this.presentationMarkdown = previewText;

        // Render based on current view mode
        this.renderPresentationView();
    }

    renderPresentationView() {
        const content = document.getElementById('presentation-content');

        if (!this.presentationMarkdown) {
            return;
        }

        if (this.presentationViewMode === 'rendered') {
            // Render as formatted markdown
            if (typeof marked !== 'undefined') {
                content.innerHTML = marked.parse(this.presentationMarkdown);
                content.classList.remove('raw-view');
                content.classList.add('rendered-view');
            } else {
                // Fallback if marked.js not loaded
                content.textContent = this.presentationMarkdown;
            }
        } else {
            // Show raw markdown
            content.textContent = this.presentationMarkdown;
            content.classList.remove('rendered-view');
            content.classList.add('raw-view');
        }
    }

    togglePresentationView(mode) {
        this.presentationViewMode = mode;

        // Update button states
        document.querySelectorAll('#presentation-preview .view-toggle button').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.view === mode);
        });

        this.renderPresentationView();
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
            include_business_value: true,
            // Include storytelling parameters for LLM generation
            narrative_style: document.getElementById('presentation-narrative-style').value || 'problem_solution',
            technical_depth: document.getElementById('presentation-technical-depth').value || 'medium'
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
        // Get selected feature (radio button - single selection only)
        const selectedFeature = document.querySelector('#lab-features input[name="selected-lab-feature"]:checked');

        if (!selectedFeature) {
            this.showToast('Please select a feature for lab generation', 'warning');
            return;
        }

        const featureId = selectedFeature.value;

        const requestData = {
            feature_ids: [featureId],  // Always array with single feature
            track_title: document.getElementById('workshop-title').value,
            format_type: document.getElementById('lab-format').value,
            include_metadata: document.getElementById('include-metadata').checked,
            export_format: 'inline',
            // Enhanced lab generation parameters
            scenario_type: document.getElementById('lab-scenario-type').value,
            data_size: document.getElementById('lab-data-size').value,
            technical_depth: document.getElementById('lab-technical-depth').value,
            // Legacy storytelling parameters (kept for compatibility)
            narrative_style: 'customer_journey',
            include_customer_stories: true,
            storytelling_enabled: true
        };

        try {
            this.showToast('Generating lab...', 'info');

            // Always use single lab endpoint
            const response = await fetch(`${this.apiBase}/labs/markdown/single`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            if (response.ok) {
                this.currentLabs = await response.json();
                this.displayLabPreview();
                this.showToast('Lab generated successfully!', 'success');
            } else {
                const errorText = await response.text();
                console.error(`Lab generation failed:`, {
                    status: response.status,
                    statusText: response.statusText,
                    url: response.url,
                    body: errorText,
                    requestData: requestData
                });
                throw new Error(`Failed to generate lab: ${response.status} ${response.statusText}`);
            }
        } catch (error) {
            console.error('Error generating lab:', error);
            this.showToast(`Error generating lab: ${error.message}`, 'error');
        }
    }

    displayLabPreview() {
        const preview = document.getElementById('lab-preview');
        const content = document.getElementById('lab-content');

        if (!this.currentLabs) {
            return;
        }

        const labContent = this.currentLabs.content || 'No content available';

        // Store markdown for toggling
        this.labMarkdown = labContent;

        // Render based on current view mode
        this.renderLabView();
    }

    renderLabView() {
        const content = document.getElementById('lab-content');

        if (!this.labMarkdown) {
            return;
        }

        if (this.labViewMode === 'rendered') {
            // Render as formatted markdown
            if (typeof marked !== 'undefined') {
                content.innerHTML = marked.parse(this.labMarkdown);
                content.classList.remove('raw-view');
                content.classList.add('rendered-view');
            } else {
                // Fallback if marked.js not loaded
                content.textContent = this.labMarkdown;
            }
        } else {
            // Show raw markdown
            content.textContent = this.labMarkdown;
            content.classList.remove('rendered-view');
            content.classList.add('raw-view');
        }
    }

    toggleLabView(mode) {
        this.labViewMode = mode;

        // Update button states
        document.querySelectorAll('#lab-preview .view-toggle button').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.view === mode);
        });

        this.renderLabView();
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
            const selectedFeature = document.querySelector('#lab-features input[name="selected-lab-feature"]:checked');

            if (!selectedFeature) {
                this.showToast('No feature selected', 'warning');
                return;
            }

            const requestData = {
                feature_ids: [selectedFeature.value],  // Always array with single feature
                track_title: document.getElementById('workshop-title').value,
                format_type: document.getElementById('lab-format').value,
                include_metadata: document.getElementById('include-metadata').checked,
                export_format: 'file',
                scenario_type: document.getElementById('lab-scenario-type').value,
                data_size: document.getElementById('lab-data-size').value,
                technical_depth: document.getElementById('lab-technical-depth').value
            };

            try {
                // Always use single lab endpoint
                const response = await fetch(`${this.apiBase}/labs/markdown/single`, {
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

    // LLM Prompts Viewer
    async openPromptsViewer() {
        const modal = document.getElementById('prompts-viewer-modal');
        modal.style.display = 'flex';

        // Setup tab switching
        const tabs = document.querySelectorAll('.prompt-tab');
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                // Update active tab
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');

                // Update active section
                const sections = document.querySelectorAll('.prompt-section');
                sections.forEach(s => s.classList.remove('active'));
                document.getElementById(`${tab.dataset.tab}-prompt-section`).classList.add('active');
            });
        });

        // Load prompts from server
        try {
            const response = await fetch(`${this.apiBase}/prompts/config`);
            const prompts = await response.json();

            // Populate presentation prompts
            document.getElementById('presentation-system-prompt').textContent =
                prompts.presentation_generator?.system_prompt || 'Using default prompts (config file not found)';
            document.getElementById('presentation-user-prompt').textContent =
                prompts.presentation_generator?.user_prompt || 'Using default prompts (config file not found)';

            // Populate extraction prompts
            document.getElementById('extraction-system-prompt').textContent =
                prompts.content_extractor?.system_prompt || 'Using default prompts (config file not found)';
            document.getElementById('extraction-user-prompt').textContent =
                prompts.content_extractor?.user_prompt || 'Using default prompts (config file not found)';

            // Populate lab prompts
            document.getElementById('lab-system-prompt').textContent =
                prompts.lab_generator?.system_prompt || 'Using default prompts (config file not found)';
            document.getElementById('lab-user-prompt').textContent =
                prompts.lab_generator?.user_prompt || 'Using default prompts (config file not found)';

        } catch (error) {
            console.error('Failed to load prompts:', error);
            this.showToast('Failed to load prompts configuration', 'error');
        }
    }

    closePromptsViewer() {
        document.getElementById('prompts-viewer-modal').style.display = 'none';
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

    // Analytics Functions
    async loadAnalytics() {
        try {
            await Promise.all([
                this.loadAnalyticsSummary(),
                this.loadGeneratedContent(),
                this.loadLLMLogs()
            ]);
        } catch (error) {
            console.error('Failed to load analytics:', error);
        }
    }

    async loadAnalyticsSummary() {
        try {
            const response = await fetch('/api/llm-usage/analytics');
            const data = await response.json();
            const analytics = data.analytics;

            // Update summary cards
            document.getElementById('total-llm-calls').textContent = analytics.total_calls || 0;
            const totalCost = analytics.total_cost_usd || 0;
            document.getElementById('total-cost').textContent = `$${totalCost.toFixed(6)}`;
            const avgTime = analytics.avg_response_time_seconds || 0;
            document.getElementById('avg-response-time').textContent = avgTime > 0 ? `${avgTime.toFixed(2)}s` : '-';
            const successRate = analytics.success_rate || 0;
            document.getElementById('success-rate').textContent = `${(successRate * 100).toFixed(1)}%`;

            // Render provider chart
            this.renderChart('provider-chart', analytics.by_provider);

            // Render operation chart
            this.renderChart('operation-chart', analytics.by_operation);
        } catch (error) {
            console.error('Failed to load analytics summary:', error);
        }
    }

    renderChart(containerId, data) {
        const container = document.getElementById(containerId);
        if (!data || Object.keys(data).length === 0) {
            container.innerHTML = '<p style="color: #718096; text-align: center; padding: 40px;">No data available</p>';
            return;
        }

        // Find max value for scaling
        const maxValue = Math.max(...Object.values(data));

        // Create bar chart
        let html = '';
        for (const [key, value] of Object.entries(data)) {
            const percentage = (value / maxValue) * 100;
            html += `<div class="chart-bar"><div class="chart-label">${key}</div><div class="chart-bar-visual" style="width: ${percentage}%"></div><div class="chart-value">${value}</div></div>`;
        }
        container.innerHTML = html;
    }

    async loadGeneratedContent() {
        try {
            const response = await fetch('/api/generated-content?size=50');
            const data = await response.json();

            this.allGeneratedContent = data.contents;
            this.renderGeneratedContent(data.contents);
        } catch (error) {
            console.error('Failed to load generated content:', error);
        }
    }

    renderGeneratedContent(contents) {
        const tbody = document.getElementById('generated-content-body');

        if (!contents || contents.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 40px; color: #718096;">No generated content yet</td></tr>';
            return;
        }

        let html = '';
        for (const content of contents) {
            const timestamp = new Date(content.timestamp).toLocaleString('en-US', {
                month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
            });
            const icon = content.content_type === 'presentation' ? 'fa-file-powerpoint' : 'fa-flask';
            const typeClass = content.content_type === 'presentation' ? 'type-presentation' : 'type-lab';

            // Get feature names (first 2)
            const featureNames = content.feature_names.slice(0, 2).join(', ');
            const moreFeatures = content.feature_names.length > 2 ? ` +${content.feature_names.length - 2}` : '';

            html += `
                <tr>
                    <td><span class="type-badge ${typeClass}"><i class="fas ${icon}"></i> ${content.content_type}</span></td>
                    <td class="title-cell">${content.title}</td>
                    <td><span class="domain-badge domain-${content.domain}">${content.domain}</span></td>
                    <td><span class="feature-count">${featureNames}${moreFeatures}</span></td>
                    <td class="timestamp-cell">${timestamp}</td>
                    <td class="actions-cell">
                        <button class="btn-icon" onclick="window.app.viewContent('${content.id}')" title="View">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn-icon" onclick="window.app.downloadContent('${content.id}')" title="Download">
                            <i class="fas fa-download"></i>
                        </button>
                    </td>
                </tr>
            `;
        }

        tbody.innerHTML = html;
    }

    filterGeneratedContent() {
        const typeFilter = document.getElementById('content-type-filter').value;
        const domainFilter = document.getElementById('content-domain-filter').value;

        let filtered = this.allGeneratedContent || [];

        if (typeFilter) {
            filtered = filtered.filter(c => c.content_type === typeFilter);
        }

        if (domainFilter) {
            filtered = filtered.filter(c => c.domain === domainFilter);
        }

        this.renderGeneratedContent(filtered);
    }

    sortContent(column) {
        if (!this.contentSortColumn || this.contentSortColumn !== column) {
            this.contentSortColumn = column;
            this.contentSortDirection = 'asc';
        } else {
            this.contentSortDirection = this.contentSortDirection === 'asc' ? 'desc' : 'asc';
        }

        const sorted = [...(this.allGeneratedContent || [])].sort((a, b) => {
            let aVal, bVal;
            switch(column) {
                case 'type': aVal = a.content_type; bVal = b.content_type; break;
                case 'title': aVal = a.title; bVal = b.title; break;
                case 'domain': aVal = a.domain; bVal = b.domain; break;
                case 'features': aVal = a.feature_ids?.length || 0; bVal = b.feature_ids?.length || 0; break;
                case 'timestamp': aVal = new Date(a.timestamp); bVal = new Date(b.timestamp); break;
                default: return 0;
            }

            if (aVal < bVal) return this.contentSortDirection === 'asc' ? -1 : 1;
            if (aVal > bVal) return this.contentSortDirection === 'asc' ? 1 : -1;
            return 0;
        });

        this.renderGeneratedContent(sorted);
    }

    sortActivity(column) {
        if (!this.activitySortColumn || this.activitySortColumn !== column) {
            this.activitySortColumn = column;
            this.activitySortDirection = 'asc';
        } else {
            this.activitySortDirection = this.activitySortDirection === 'asc' ? 'desc' : 'asc';
        }

        const sorted = [...(this.allLLMLogs || [])].sort((a, b) => {
            let aVal, bVal;
            switch(column) {
                case 'operation': aVal = a.operation_type; bVal = b.operation_type; break;
                case 'features': aVal = a.feature_ids?.length || 0; bVal = b.feature_ids?.length || 0; break;
                case 'domain': aVal = a.domain || ''; bVal = b.domain || ''; break;
                case 'provider': aVal = a.provider; bVal = b.provider; break;
                case 'tokens': aVal = a.token_usage?.total_tokens || 0; bVal = b.token_usage?.total_tokens || 0; break;
                case 'cost': aVal = a.estimated_cost_usd || 0; bVal = b.estimated_cost_usd || 0; break;
                case 'duration': aVal = a.response_time_seconds; bVal = b.response_time_seconds; break;
                case 'timestamp': aVal = new Date(a.timestamp); bVal = new Date(b.timestamp); break;
                default: return 0;
            }

            if (aVal < bVal) return this.activitySortDirection === 'asc' ? -1 : 1;
            if (aVal > bVal) return this.activitySortDirection === 'asc' ? 1 : -1;
            return 0;
        });

        this.renderLLMLogs(sorted);
    }

    async viewContentDetails(contentId) {
        try {
            const response = await fetch(`/api/generated-content/${contentId}`);
            const content = await response.json();

            const features = content.feature_names.join(', ');
            alert(`Content: ${content.title}\nType: ${content.content_type}\nDomain: ${content.domain}\nFeatures: ${features}`);
        } catch (error) {
            console.error('Failed to load content details:', error);
        }
    }

    async downloadContent(contentId) {
        try {
            const response = await fetch(`/api/generated-content/${contentId}/markdown`);
            const data = await response.json();

            // Create download link
            const blob = new Blob([data.markdown], { type: 'text/markdown' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            const filename = data.title.toLowerCase().replace(/\s+/g, '-');
            a.download = `${filename}.md`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Failed to download content:', error);
        }
    }

    async viewContent(contentId) {
        try {
            this.showToast('Loading content...', 'info');

            // Fetch markdown content
            const response = await fetch(`/api/generated-content/${contentId}/markdown`);
            if (!response.ok) {
                throw new Error('Failed to fetch content');
            }
            const data = await response.json();

            // Store for toggling
            this.previewMarkdown = data.markdown;
            this.previewViewMode = 'rendered';

            // Update title
            document.getElementById('preview-modal-title').textContent = data.title;

            // Render content
            this.renderPreviewView();

            // Show modal
            document.getElementById('content-preview-modal').style.display = 'flex';

            this.showToast('Content loaded', 'success');
        } catch (error) {
            console.error('Failed to load content:', error);
            this.showToast('Failed to load content', 'error');
        }
    }

    renderPreviewView() {
        const content = document.getElementById('preview-modal-content');

        if (!this.previewMarkdown) {
            content.innerHTML = '<div class="empty-state"><p>No content available</p></div>';
            return;
        }

        if (this.previewViewMode === 'rendered') {
            // Render as formatted markdown
            if (typeof marked !== 'undefined') {
                content.innerHTML = marked.parse(this.previewMarkdown);
                content.classList.add('rendered-view');
                content.classList.remove('raw-view');
            } else {
                // Fallback if marked.js not loaded
                content.textContent = this.previewMarkdown;
            }
        } else {
            // Show raw markdown
            content.textContent = this.previewMarkdown;
            content.classList.add('raw-view');
            content.classList.remove('rendered-view');
        }
    }

    togglePreviewView(mode) {
        this.previewViewMode = mode;

        // Update button states
        document.querySelectorAll('#content-preview-modal .view-toggle button').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.view === mode);
        });

        this.renderPreviewView();
    }

    closeContentPreview() {
        document.getElementById('content-preview-modal').style.display = 'none';
        this.previewMarkdown = '';
        this.previewViewMode = 'rendered';
    }

    async loadLLMLogs() {
        try {
            const response = await fetch('/api/llm-usage/logs?size=50');
            const data = await response.json();

            this.allLLMLogs = data.logs || [];
            this.renderLLMLogs(this.allLLMLogs);
        } catch (error) {
            console.error('Failed to load LLM logs:', error);
        }
    }

    showAnalyticsTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.analytics-tabs .tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        event.target.closest('.tab-btn').classList.add('active');

        // Update tab panels
        document.querySelectorAll('.analytics-tab-panel').forEach(panel => {
            panel.classList.remove('active');
        });
        document.getElementById(`analytics-${tabName}-tab`).classList.add('active');
    }

    filterLLMActivity() {
        const operationFilter = document.getElementById('activity-operation-filter').value;
        const domainFilter = document.getElementById('activity-domain-filter').value;
        const providerFilter = document.getElementById('activity-provider-filter').value;

        let filtered = this.allLLMLogs;

        if (operationFilter) {
            filtered = filtered.filter(log => log.operation_type === operationFilter);
        }
        if (domainFilter) {
            filtered = filtered.filter(log => log.domain === domainFilter);
        }
        if (providerFilter) {
            filtered = filtered.filter(log => log.provider === providerFilter);
        }

        this.renderLLMLogs(filtered);
    }

    renderLLMLogs(logs) {
        const tbody = document.getElementById('llm-activity-body');

        if (!logs || logs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 40px; color: #718096;">No LLM activity yet</td></tr>';
            return;
        }

        let html = '';
        for (const log of logs) {
            const timestamp = new Date(log.timestamp).toLocaleString('en-US', {
                month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
            });
            const statusIcon = log.success ? '<i class="fas fa-check-circle" style="color: #48bb78;"></i>' : '<i class="fas fa-exclamation-circle" style="color: #f56565;"></i>';

            // Build feature context string with names
            let featureContext = '-';
            if (log.feature_ids && log.feature_ids.length > 0) {
                const displayFeatures = log.feature_ids.slice(0, 1).map(id => {
                    const feature = this.features.find(f => f.id === id);
                    return feature ? feature.name : id;
                });
                const moreCount = log.feature_ids.length - displayFeatures.length;
                featureContext = displayFeatures[0];
                if (moreCount > 0) {
                    featureContext += ` <span style="color: #a0aec0;">+${moreCount}</span>`;
                }
            }

            const domainBadge = log.domain ? `<span class="domain-badge domain-${log.domain}">${log.domain}</span>` : '-';
            const tokens = log.token_usage ? log.token_usage.total_tokens.toLocaleString() : '-';
            const cost = log.estimated_cost_usd ? `$${log.estimated_cost_usd.toFixed(4)}` : '-';
            const duration = `${log.response_time_seconds.toFixed(2)}s`;

            html += `
                <tr>
                    <td>${statusIcon} ${log.operation_type}</td>
                    <td class="features-cell">${featureContext}</td>
                    <td>${domainBadge}</td>
                    <td><span class="provider-badge">${log.provider}</span></td>
                    <td class="number-cell">${tokens}</td>
                    <td class="number-cell">${cost}</td>
                    <td class="number-cell">${duration}</td>
                    <td class="timestamp-cell">${timestamp}</td>
                </tr>
            `;
        }

        tbody.innerHTML = html;
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
    // Make app globally accessible for onclick handlers
    window.app = app;
});
