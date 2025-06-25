// Natural Language Query Component
class NaturalLanguageQuery {
    constructor(apiClient, utils) {
        this.api = apiClient;
        this.utils = utils;
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // The onclick handler in HTML will call the global function
        // Make sure the global function is available
        window.executeNaturalQuery = () => this.executeNaturalQuery();
    }

    async executeNaturalQuery() {
        const repoPath = document.getElementById('nlq-repo').value;
        const queryText = document.getElementById('natural-query-input').value.trim();
        
        if (!repoPath) {
            alert('Please select a repository');
            return;
        }
        
        if (!queryText) {
            alert('Please enter a query');
            return;
        }

        const resultsDiv = document.getElementById('nlq-results');
        resultsDiv.style.display = 'block';
        resultsDiv.innerHTML = '<div class="loading">Processing your query...</div>';

        try {
            const result = await this.api.executeNaturalQuery(repoPath, queryText);
            
            this.displayNLQResults(result);
        } catch (error) {
            console.error('Natural language query failed:', error);
            resultsDiv.innerHTML = `<div class="error">Query failed: ${error.message}</div>`;
        }
    }

    displayNLQResults(result) {
        const resultsDiv = document.getElementById('nlq-results-content');
        
        let html = '<div class="nlq-response">';
        
        if (result.response) {
            html += `
                <div class="ai-response">
                    <h4>🤖 AI Response</h4>
                    <div class="response-text">${this.utils.escapeHtml(result.response)}</div>
                </div>
            `;
        }
        
        if (result.events && result.events.length > 0) {
            html += `
                <div class="supporting-events">
                    <h4>📊 Supporting Data (${result.events.length} events)</h4>
                    <div class="events-grid">
            `;
            
            result.events.slice(0, 10).forEach(event => {
                html += `
                    <div class="event-card">
                        <div class="event-header">
                            <span class="event-type">${event.event_type}</span>
                            <span class="event-confidence">Confidence: ${(event.confidence * 100).toFixed(0)}%</span>
                        </div>
                        <div class="event-location">${event.location || 'N/A'}</div>
                        <div class="event-description">${this.utils.escapeHtml(event.description || '')}</div>
                        <div class="event-meta">
                            <small>
                                ${event.author} • ${this.utils.formatDate(event.timestamp)}
                            </small>
                        </div>
                    </div>
                `;
            });
            
            html += '</div></div>';
        }
        
        html += '</div>';
        
        resultsDiv.innerHTML = html;
    }

    async updateRepositorySelect(repositories) {
        const select = document.getElementById('nlq-repo');
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
                console.warn(`Failed to get branch info for ${repo.path}:`, error);
            }
            
            option.textContent = label;
            select.appendChild(option);
        }
    }
}

// Export to global scope
window.NaturalLanguageQuery = NaturalLanguageQuery;
