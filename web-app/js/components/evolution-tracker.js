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
            const eventTypes = document.getElementById('evolution-event-types').value;
            if (eventTypes) {
                params.event_types = eventTypes.split(',').map(t => t.trim());
            }

            const sinceDate = document.getElementById('evolution-since').value;
            if (sinceDate) {
                params.since_date = sinceDate;
            }

            const minConfidence = document.getElementById('evolution-confidence').value;
            if (minConfidence) {
                params.min_confidence = parseFloat(minConfidence);
            }

            const result = await this.api.getFilteredEvolution(params);
            this.displayEvolutionResults(result);
        } catch (error) {
            resultsDiv.innerHTML = `<div class="error">Evolution tracking failed: ${error.message}</div>`;
        }
    }

    displayEvolutionResults(result) {
        const resultsDiv = document.getElementById('evolution-results');
        
        if (!result.events || result.events.length === 0) {
            resultsDiv.innerHTML = '<div class="info">No evolution events found for this node</div>';
            return;
        }

        // Sort events by timestamp
        const sortedEvents = result.events.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

        const timelineHtml = sortedEvents.map((event, index) => `
            <div class="evolution-event" data-index="${index}">
                <div class="evolution-timeline-marker"></div>
                <div class="evolution-event-content">
                    <div class="evolution-event-header">
                        <span class="evolution-event-type">${event.event_type}</span>
                        <span class="evolution-event-timestamp">${new Date(event.timestamp).toLocaleString()}</span>
                        ${event.confidence ? `<span class="evolution-event-confidence">${(event.confidence * 100).toFixed(1)}%</span>` : ''}
                    </div>
                    <div class="evolution-event-details">
                        <div class="evolution-location"><strong>Location:</strong> ${event.location || 'N/A'}</div>
                        <div class="evolution-description">${event.description || 'No description'}</div>
                        ${event.author ? `<div class="evolution-author"><strong>Author:</strong> ${event.author}</div>` : ''}
                        ${event.commit_hash ? `<div class="evolution-commit"><strong>Commit:</strong> <code>${event.commit_hash.substring(0, 8)}</code></div>` : ''}
                        ${event.metadata ? `
                            <details class="evolution-metadata">
                                <summary>Metadata</summary>
                                <pre>${JSON.stringify(event.metadata, null, 2)}</pre>
                            </details>
                        ` : ''}
                    </div>
                </div>
            </div>
        `).join('');

        const statsHtml = this.generateEvolutionStats(result.events);

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

    generateEvolutionStats(events) {
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
            `${new Date(events[0].timestamp).toLocaleDateString()} - ${new Date(events[events.length - 1].timestamp).toLocaleDateString()}` : 
            new Date(events[0].timestamp).toLocaleDateString();

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

    updateRepositorySelect(repositories) {
        const select = document.getElementById('evolution-repo');
        if (!select) return;
        
        // Clear existing options except the first placeholder
        select.innerHTML = '<option value="">Select a repository...</option>';
        
        // Add repository options
        repositories.forEach(repo => {
            const option = document.createElement('option');
            option.value = repo.path;
            option.textContent = repo.name || repo.path;
            select.appendChild(option);
        });
    }
}

// Export to global scope
window.EvolutionTracker = EvolutionTracker;
