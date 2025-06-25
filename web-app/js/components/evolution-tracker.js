// Evolution Tracker Component
class EvolutionTracker {
    constructor(apiClient, utils) {
        this.api = apiClient;
        this.utils = utils;
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        const trackBtn = document.getElementById('track-evolution');
        if (trackBtn) {
            trackBtn.addEventListener('click', () => this.trackEvolution());
        }
    }

    async trackEvolution() {
        const repoPath = document.getElementById('evolution-repo').value;
        const nodeId = document.getElementById('node-id').value;
        
        console.log('Track evolution called with:', { repoPath, nodeId });
        
        if (!repoPath || !nodeId) {
            alert('Please select a repository and enter a node ID');
            return;
        }

        const resultsDiv = document.getElementById('evolution-results');
        resultsDiv.style.display = 'block';
        resultsDiv.innerHTML = '<div class="loading">Tracking evolution...</div>';

        try {
            const params = {
                repository_path: repoPath,
                node_id: nodeId
            };

            // Add optional filters
            const eventTypesEl = document.getElementById('evolution-event-types');
            if (eventTypesEl && eventTypesEl.value) {
                params.event_types = eventTypesEl.value.split(',').map(t => t.trim());
            }

            const sinceDateEl = document.getElementById('evolution-since');
            if (sinceDateEl && sinceDateEl.value) {
                params.since_date = sinceDateEl.value;
            }

            const minConfidenceEl = document.getElementById('evolution-confidence');
            if (minConfidenceEl && minConfidenceEl.value) {
                params.min_confidence = parseFloat(minConfidenceEl.value);
            }

            const result = await this.api.getFilteredEvolution(params);
            console.log('Raw API result for evolution:', result);
            this.displayEvolutionResults(result);
        } catch (error) {
            resultsDiv.innerHTML = `<div class="error">Evolution tracking failed: ${error.message}</div>`;
        }
    }

    displayEvolutionResults(result) {
        const resultsDiv = document.getElementById('evolution-results');
        
        // Debug logging - examine the full response structure
        console.log('Full Evolution API result:', JSON.stringify(result, null, 2));
        
        // The API client's callAPI method returns result.data, so our evolution data is at result.evolution
        let events = result.evolution || [];
        
        console.log('Extracted events:', events);
        console.log('Events array type:', Array.isArray(events));
        console.log('Events length:', events ? events.length : 'undefined');
        
        if (!events || !Array.isArray(events) || events.length === 0) {
            resultsDiv.innerHTML = '<div class="info">No evolution events found for this node</div>';
            return;
        }

        // Sort events by timestamp (created_at from server)
        const sortedEvents = events.sort((a, b) => a.created_at - b.created_at);

        const timelineHtml = sortedEvents.map((event, index) => `
            <div class="evolution-event" data-index="${index}">
                <div class="evolution-timeline-marker"></div>
                <div class="evolution-event-content">
                    <div class="evolution-event-header">
                        <span class="evolution-event-type">${event.event_type}</span>
                        <span class="evolution-event-timestamp">${new Date(event.created_at * 1000).toLocaleString()}</span>
                        ${event.confidence ? `<span class="evolution-event-confidence">${(event.confidence * 100).toFixed(1)}%</span>` : ''}
                    </div>
                    <div class="evolution-event-details">
                        <div class="evolution-location"><strong>Location:</strong> ${event.location || 'N/A'}</div>
                        <div class="evolution-description">${event.details || 'No description'}</div>
                        ${event.author ? `<div class="evolution-author"><strong>Author:</strong> ${event.author}</div>` : ''}
                        ${event.commit_hash ? `<div class="evolution-commit"><strong>Commit:</strong> <code>${event.commit_hash.substring(0, 8)}</code></div>` : ''}
                        ${event.layer ? `<div class="evolution-layer"><strong>Layer:</strong> ${event.layer}</div>` : ''}
                    </div>
                </div>
            </div>
        `).join('');

        const statsHtml = this.generateEvolutionStats(events, result);

        resultsDiv.innerHTML = `
            <div class="evolution-summary">
                <h3>Evolution Timeline for ${result.node_id || 'Node'}</h3>
                ${statsHtml}
            </div>
            <div class="evolution-timeline">
                ${timelineHtml}
            </div>
        `;
    }

    generateEvolutionStats(events, data) {
        const eventTypes = {};
        const authors = {};
        let totalConfidence = 0;
        let confidenceCount = 0;

        events.forEach(event => {
            // Count event types
            eventTypes[event.event_type] = (eventTypes[event.event_type] || 0) + 1;
            
            // Count authors
            if (event.author) {
                authors[event.author] = (authors[event.author] || 0) + 1;
            }
            
            // Calculate average confidence
            if (event.confidence) {
                totalConfidence += event.confidence;
                confidenceCount++;
            }
        });

        const avgConfidence = confidenceCount > 0 ? (totalConfidence / confidenceCount * 100).toFixed(1) : 'N/A';
        const timeSpan = events.length > 1 ? 
            `${new Date(events[0].created_at * 1000).toLocaleDateString()} - ${new Date(events[events.length - 1].created_at * 1000).toLocaleDateString()}` : 
            events.length > 0 ? new Date(events[0].created_at * 1000).toLocaleDateString() : 'N/A';

        return `
            <div class="evolution-stats">
                <div class="stat-item">
                    <span class="stat-label">Total Events:</span>
                    <span class="stat-value">${events.length}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Time Span:</span>
                    <span class="stat-value">${timeSpan}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Avg Confidence:</span>
                    <span class="stat-value">${avgConfidence}${avgConfidence !== 'N/A' ? '%' : ''}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Event Types:</span>
                    <span class="stat-value">${Object.keys(eventTypes).join(', ')}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Contributors:</span>
                    <span class="stat-value">${Object.keys(authors).length}</span>
                </div>
            </div>
        `;
    }

    async updateRepositorySelect(repositories) {
        const select = document.getElementById('evolution-repo');
        if (!select) return;
        
        // Clear existing options except the first placeholder
        select.innerHTML = '<option value="">Select a repository...</option>';
        
        // Add repository options with current branch info
        for (const repo of repositories) {
            const option = document.createElement('option');
            option.value = repo.path;
            
            // Try to get current branch info
            let label = repo.name || repo.path;
            try {
                const branchInfo = await this.api.getRepositoryBranches(repo.path);
                if (branchInfo && branchInfo.current_branch) {
                    label = `${label}:(${branchInfo.current_branch})`;
                }
            } catch (error) {
                // If branch info fails, just use the basic label
                console.warn(`Failed to get branch info for ${repo.path}:`, error);
            }
            
            option.textContent = label;
            select.appendChild(option);
        }
        
        // Add event listener for repository selection changes
        select.removeEventListener('change', this.handleRepositoryChange.bind(this));
        select.addEventListener('change', this.handleRepositoryChange.bind(this));
    }

    async handleRepositoryChange(event) {
        const selectedRepo = event.target.value;
        await this.populateEventTypesFromMetadata(selectedRepo);
    }

    async populateEventTypesFromMetadata(repositoryPath) {
        const eventTypesInput = document.getElementById('evolution-event-types');
        if (!eventTypesInput) return;

        if (!repositoryPath) {
            // Clear placeholder when no repository selected
            eventTypesInput.placeholder = "signature_changed,function_made_async";
            return;
        }

        try {
            const metadata = await this.api.getRepositoryMetadata(repositoryPath);
            
            if (metadata.event_types && metadata.event_types.length > 0) {
                // Update placeholder with actual available event types
                const sampleEventTypes = metadata.event_types.slice(0, 3).join(',');
                eventTypesInput.placeholder = `e.g., ${sampleEventTypes}`;
                eventTypesInput.title = `Available event types: ${metadata.event_types.join(', ')}`;
            }
        } catch (error) {
            console.error('Failed to load repository metadata for evolution:', error);
            // Keep default placeholder on error
            eventTypesInput.placeholder = "signature_changed,function_made_async";
        }
    }
}

// Export to global scope
window.EvolutionTracker = EvolutionTracker;
