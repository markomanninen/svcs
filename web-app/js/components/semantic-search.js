// Semantic Search Component
class SemanticSearch {
    constructor(apiClient, utils) {
        this.api = apiClient;
        this.utils = utils;
    }

    toggleAdvancedFilters() {
        const advanced = document.getElementById('advanced-filters');
        const toggleButtons = document.querySelectorAll('button[onclick*="toggleAdvancedFilters"]');
        
        if (advanced.style.display === 'none' || !advanced.style.display) {
            advanced.style.display = 'block';
            toggleButtons.forEach(btn => btn.textContent = btn.textContent.replace('More Filters', 'Hide Filters'));
        } else {
            advanced.style.display = 'none';
            toggleButtons.forEach(btn => btn.textContent = btn.textContent.replace('Hide Filters', 'More Filters'));
        }
    }

    clearSearchFilters() {
        // Clear repository selection
        const repo = document.getElementById('search-repo');
        if (repo) repo.value = '';

        // Clear main search controls
        const mainFields = [
            'search-event-type', 'search-layer', 'search-author', 
            'search-since-days', 'search-limit', 'search-order-by', 'search-order-desc'
        ];
        
        mainFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                if (fieldId === 'search-limit') {
                    field.value = '20';
                } else if (fieldId === 'search-order-by') {
                    field.value = 'timestamp';
                } else if (fieldId === 'search-order-desc') {
                    field.value = 'true';
                } else {
                    field.value = '';
                }
            }
        });

        // Clear advanced filters
        const advancedFields = [
            'adv-confidence', 'adv-since-date', 'adv-location', 'adv-max-confidence'
        ];
        
        advancedFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) field.value = '';
        });

        // Clear results
        const resultsDiv = document.getElementById('search-results');
        if (resultsDiv) {
            resultsDiv.innerHTML = '';
            resultsDiv.style.display = 'none';
        }
    }

    async performUnifiedSearch() {
        const repoPath = document.getElementById('search-repo').value;
        
        if (!repoPath) {
            alert('Please select a repository to search');
            return;
        }

        const resultsDiv = document.getElementById('search-results');
        resultsDiv.style.display = 'block';
        resultsDiv.innerHTML = '<div class="loading">Searching...</div>';

        try {
            // Gather all search parameters
            const params = this.gatherSearchParameters(repoPath);
            
            // Decide which API to use based on filled advanced filters
            const useAdvancedAPI = this.shouldUseAdvancedAPI(params);
            
            let result;
            if (useAdvancedAPI) {
                result = await this.api.searchEventsAdvanced(params);
                this.displayAdvancedSearchResults(result);
            } else {
                result = await this.api.searchEvents(params);
                this.displaySearchResults(result);
            }

        } catch (error) {
            resultsDiv.innerHTML = `<div class="error">Search failed: ${error.message}</div>`;
        }
    }

    gatherSearchParameters(repoPath) {
        const params = {
            repository_path: repoPath
        };

        // Main search controls (always available)
        const eventType = document.getElementById('search-event-type')?.value;
        if (eventType) params.event_type = eventType;

        const layer = document.getElementById('search-layer')?.value;
        if (layer) params.layers = [layer];

        const author = document.getElementById('search-author')?.value;
        if (author) params.author = author;

        const sinceDays = document.getElementById('search-since-days')?.value;
        if (sinceDays) params.since_days = parseInt(sinceDays);

        const limit = document.getElementById('search-limit')?.value || 20;
        params.limit = parseInt(limit);

        const orderBy = document.getElementById('search-order-by')?.value || 'timestamp';
        params.order_by = orderBy;

        const orderDesc = document.getElementById('search-order-desc')?.value === 'true';
        params.order_desc = orderDesc;

        // Advanced filters (only if filled)
        const confidence = document.getElementById('adv-confidence')?.value;
        if (confidence) params.min_confidence = parseFloat(confidence);

        const maxConfidence = document.getElementById('adv-max-confidence')?.value;
        if (maxConfidence) params.max_confidence = parseFloat(maxConfidence);

        const sinceDate = document.getElementById('adv-since-date')?.value;
        if (sinceDate) params.since_date = sinceDate;

        const location = document.getElementById('adv-location')?.value;
        if (location) params.location_pattern = location;

        return params;
    }

    shouldUseAdvancedAPI(params) {
        // Use advanced API if any advanced-only filters are set
        const advancedOnlyParams = [
            'min_confidence', 'max_confidence', 'since_date', 'location_pattern'
        ];
        
        return advancedOnlyParams.some(param => params.hasOwnProperty(param));
    }

    async getRecentActivity() {
        const repoPath = document.getElementById('search-repo').value;
        
        if (!repoPath) {
            alert('Please select a repository to get activity');
            return;
        }

        const resultsDiv = document.getElementById('search-results');
        resultsDiv.style.display = 'block';
        resultsDiv.innerHTML = '<div class="loading">Loading recent activity...</div>';

        try {
            const result = await this.api.getRecentActivity(repoPath, 7, 15);
            this.displaySearchResults(result);
        } catch (error) {
            resultsDiv.innerHTML = `<div class="error">Failed to load recent activity: ${error.message}</div>`;
        }
    }

    displaySearchResults(result) {
        const resultsDiv = document.getElementById('search-results');
        
        // Use the exact API response structure - no guessing
        const events = result.events || [];
        
        if (!events || events.length === 0) {
            resultsDiv.innerHTML = '<div class="info">No events found</div>';
            return;
        }

        const eventsHtml = events.map(event => {
            // Basic search uses 'created_at', advanced search uses 'timestamp'
            const timestamp = event.created_at || event.timestamp;
            
            return `
            <div class="event-card">
                <div class="event-header">
                    <span class="event-type">${event.event_type}</span>
                    <span class="event-layer">${event.layer}</span>
                    <span class="event-timestamp">${this.utils.formatDate(timestamp)}</span>
                </div>
                <div class="event-content">
                    <div class="event-location"><strong>Location:</strong> ${event.location || 'N/A'}</div>
                    <div class="event-description"><strong>Description:</strong> ${event.details || 'N/A'}</div>
                    ${event.confidence ? `<div class="event-confidence"><strong>Confidence:</strong> ${(event.confidence * 100).toFixed(1)}%</div>` : ''}
                    ${event.author ? `<div class="event-author"><strong>Author:</strong> ${event.author}</div>` : ''}
                </div>
            </div>
        `}).join('');

        resultsDiv.innerHTML = `
            <div class="search-summary">
                Found ${events.length} events
                ${result.total ? ` (showing ${events.length} of ${result.total})` : ''}
            </div>
            <div class="events-list">
                ${eventsHtml}
            </div>
        `;
    }

    displayAdvancedSearchResults(result) {
        const resultsDiv = document.getElementById('search-results');
        
        // Use the exact API response structure - no guessing
        const events = result.results || [];
        
        if (!events || events.length === 0) {
            resultsDiv.innerHTML = '<div class="info">No events found matching your criteria</div>';
            return;
        }

        // Group events by type for better visualization
        const eventsByType = {};
        events.forEach(event => {
            if (!eventsByType[event.event_type]) {
                eventsByType[event.event_type] = [];
            }
            eventsByType[event.event_type].push(event);
        });

        let html = `
            <div class="search-summary">
                Found ${events.length} events across ${Object.keys(eventsByType).length} types
            </div>
        `;

        Object.entries(eventsByType).forEach(([type, typeEvents]) => {
            html += `
                <div class="event-type-group">
                    <h4 class="event-type-header">${type} (${typeEvents.length})</h4>
                    <div class="events-list">
                        ${typeEvents.map(event => `
                            <div class="event-card">
                                <div class="event-header">
                                    <span class="event-layer">${event.layer}</span>
                                    <span class="event-timestamp">${this.utils.formatDate(event.timestamp)}</span>
                                </div>
                                <div class="event-content">
                                    <div class="event-location"><strong>Location:</strong> ${event.location || 'N/A'}</div>
                                    <div class="event-description"><strong>Description:</strong> ${event.details || 'N/A'}</div>
                                    ${event.confidence ? `<div class="event-confidence"><strong>Confidence:</strong> ${(event.confidence * 100).toFixed(1)}%</div>` : ''}
                                    ${event.author ? `<div class="event-author"><strong>Author:</strong> ${event.author}</div>` : ''}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        });

        resultsDiv.innerHTML = html;
    }

    async updateRepositorySelect(repositories) {
        // Update the repository dropdown with the latest repositories
        const select = this.utils.$('search-repo');
        if (select) {
            // Clear existing options except the default
            select.innerHTML = '<option value="">Select a repository...</option>';
            
            // Add registered repositories with current branch info
            const registeredRepos = repositories.filter(repo => repo.registered);
            for (const repo of registeredRepos) {
                const option = document.createElement('option');
                option.value = repo.path;
                
                // Try to get current branch info
                let label = repo.name || repo.path.split('/').pop();
                try {
                    const branchInfo = await this.api.getRepositoryBranches(repo.path);
                    if (branchInfo && branchInfo.current_branch) {
                        label = `${label}:(${branchInfo.current_branch})`;
                    }
                } catch (error) {
                    console.warn(`Failed to get branch info for ${repo.path}:`, error);
                }
                
                option.textContent = label;
                select.appendChild(option);
            }

            // Add event listener for repository selection changes
            select.removeEventListener('change', this.handleRepositoryChange.bind(this)); // Remove any existing listener
            select.addEventListener('change', this.handleRepositoryChange.bind(this));
        }
    }

    async handleRepositoryChange(event) {
        const selectedRepo = event.target.value;
        await this.populateRepositoryDropdowns(selectedRepo);
        
        // Also clear previous search results when repository changes
        const resultsDiv = document.getElementById('search-results');
        if (resultsDiv) {
            resultsDiv.innerHTML = '';
            resultsDiv.style.display = 'none';
        }
    }

    async populateRepositoryDropdowns(repositoryPath) {
        if (!repositoryPath) {
            // Clear dropdowns if no repository selected
            this.clearRepositoryDropdowns();
            return;
        }

        try {
            const metadata = await this.api.getRepositoryMetadata(repositoryPath);
            
            // Populate event types dropdown
            const eventTypeSelect = document.getElementById('search-event-type');
            if (eventTypeSelect && metadata.event_types) {
                eventTypeSelect.innerHTML = '<option value="">All Event Types</option>';
                metadata.event_types.forEach(eventType => {
                    const option = document.createElement('option');
                    option.value = eventType;
                    option.textContent = eventType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                    eventTypeSelect.appendChild(option);
                });
            }

            // Populate layers dropdown
            const layerSelect = document.getElementById('search-layer');
            if (layerSelect && metadata.layers) {
                layerSelect.innerHTML = '<option value="">All Layers</option>';
                metadata.layers.forEach(layer => {
                    const option = document.createElement('option');
                    option.value = layer;
                    option.textContent = layer.charAt(0).toUpperCase() + layer.slice(1);
                    layerSelect.appendChild(option);
                });
            }

            // For authors, we'll populate as datalist suggestions for the text input
            const authorInput = document.getElementById('search-author');
            if (authorInput && metadata.authors) {
                // Remove existing datalist if any
                const existingDatalist = document.getElementById('authors-datalist');
                if (existingDatalist) {
                    existingDatalist.remove();
                }

                // Create new datalist
                const datalist = document.createElement('datalist');
                datalist.id = 'authors-datalist';
                metadata.authors.forEach(author => {
                    const option = document.createElement('option');
                    option.value = author;
                    datalist.appendChild(option);
                });
                
                // Add datalist to DOM and link to input
                document.body.appendChild(datalist);
                authorInput.setAttribute('list', 'authors-datalist');
            }

        } catch (error) {
            console.error('Failed to load repository metadata:', error);
            // Fallback to empty dropdowns on error
            this.clearRepositoryDropdowns();
        }
    }

    clearRepositoryDropdowns() {
        // Clear event types dropdown
        const eventTypeSelect = document.getElementById('search-event-type');
        if (eventTypeSelect) {
            eventTypeSelect.innerHTML = '<option value="">All Event Types</option>';
        }

        // Clear layers dropdown
        const layerSelect = document.getElementById('search-layer');
        if (layerSelect) {
            layerSelect.innerHTML = '<option value="">All Layers</option>';
        }

        // Clear authors datalist
        const existingDatalist = document.getElementById('authors-datalist');
        if (existingDatalist) {
            existingDatalist.remove();
        }
        
        const authorInput = document.getElementById('search-author');
        if (authorInput) {
            authorInput.removeAttribute('list');
        }
    }
}

// Export to global scope
window.SemanticSearch = SemanticSearch;
