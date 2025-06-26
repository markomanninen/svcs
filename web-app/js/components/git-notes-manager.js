/**
 * Git Notes Manager Component
 * Handles git notes synchronization, fetching, and display
 */
class GitNotesManager {
    constructor(apiClient, utils) {
        this.api = apiClient;
        this.utils = utils;
        this.initializeElements();
        this.attachEventListeners();
    }

    initializeElements() {
        this.repoSelect = document.getElementById('notes-repo');
        this.commitHashInput = document.getElementById('commit-hash');
        this.syncButton = document.querySelector('button[onclick="syncNotes()"]');
        this.fetchButton = document.querySelector('button[onclick="fetchNotes()"]');
        this.showNoteButton = document.querySelector('button[onclick="showNote()"]');
        this.resultsContainer = document.getElementById('notes-results');
        this.resultsContent = document.getElementById('notes-results-content');
    }

    attachEventListeners() {
        if (this.syncButton) {
            this.syncButton.onclick = () => this.syncNotes();
        }

        if (this.fetchButton) {
            this.fetchButton.onclick = () => this.fetchNotes();
        }

        if (this.showNoteButton) {
            this.showNoteButton.onclick = () => this.showNote();
        }

        // Allow enter key in commit hash input
        if (this.commitHashInput) {
            this.commitHashInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.showNote();
                }
            });
        }
    }

    async syncNotes() {
        const repoPath = this.repoSelect.value;
        if (!repoPath) {
            this.utils.showError('Please select a repository');
            return;
        }

        try {
            this.utils.showLoading(this.resultsContent, 'Syncing notes to remote...');
            this.resultsContainer.style.display = 'block';

            const result = await this.api.syncGitNotes({
                repository_path: repoPath
            });

            // Always try to display results, even if sync failed
            this.displaySyncResults(result);

        } catch (error) {
            console.error('Sync error:', error);
            this.utils.showError(`Failed to sync notes: ${error.message}`);
            this.resultsContainer.style.display = 'none';
        }
    }

    async fetchNotes() {
        const repoPath = this.repoSelect.value;
        if (!repoPath) {
            this.utils.showError('Please select a repository');
            return;
        }

        try {
            this.utils.showLoading(this.resultsContent, 'Fetching notes from remote...');
            this.resultsContainer.style.display = 'block';

            const result = await this.api.fetchGitNotes({
                repository_path: repoPath
            });

            this.displayFetchResults(result);

        } catch (error) {
            this.utils.showError(`Failed to fetch notes: ${error.message}`);
            this.resultsContainer.style.display = 'none';
        }
    }

    async showNote() {
        const repoPath = this.repoSelect.value;
        const commitHash = this.commitHashInput.value.trim() || 'HEAD';

        if (!repoPath) {
            this.utils.showError('Please select a repository');
            return;
        }

        try {
            this.utils.showLoading(this.resultsContent, `Getting note for ${commitHash}...`);
            this.resultsContainer.style.display = 'block';

            const result = await this.api.getGitNote({
                repository_path: repoPath,
                commit_hash: commitHash
            });

            this.displayNoteContent(result, commitHash);

        } catch (error) {
            this.utils.showError(`Failed to get note: ${error.message}`);
            this.resultsContainer.style.display = 'none';
        }
    }

    displaySyncResults(result) {
        try {
            // Handle case where result might be undefined or malformed
            if (!result) {
                result = { success: false, message: 'No response from server' };
            }

            // Extract the actual sync result from the response structure
            const syncSuccess = result.sync_result === true || result.status === "success" || (result.success && result.sync_result === true);
            const message = result.message || result.data?.message || result.error || 'No details available';
            
            let html = `
                <div class="sync-results-summary">
                    <h4>Git Notes Sync Results</h4>
                    <div class="sync-status ${syncSuccess ? 'success' : 'error'}">
                        Status: ${syncSuccess ? 'Sync Successful' : 'Sync Failed'}
                    </div>
                </div>
            `;

            // Only show details if it's different from the default success message or if there's an error
            if (!syncSuccess || (message && message !== 'Git notes synced successfully to remote')) {
                html += `
                    <div class="sync-details">
                        <h5>Details</h5>
                        <div class="details-content">${message}</div>
                    </div>
                `;
            }

            if (result.synced_notes && result.synced_notes.length > 0) {
                html += `
                    <div class="synced-notes">
                        <h5>Synced Notes (${result.synced_notes.length})</h5>
                        ${result.synced_notes.map(note => `
                            <div class="note-item">
                                <div class="note-commit">${note.commit || 'Unknown commit'}</div>
                                <div class="note-preview">${this.truncateNote(note.content || 'No content')}</div>
                            </div>
                        `).join('')}
                    </div>
                `;
            }

            if (result.errors && result.errors.length > 0) {
                html += `
                    <div class="sync-errors">
                        <h5>Errors</h5>
                        <ul>
                            ${result.errors.map(error => `<li>${error}</li>`).join('')}
                        </ul>
                    </div>
                `;
            }

            // Only show raw data in collapsed state for debugging
            html += `
                <details class="raw-data" style="margin-top: 15px;">
                    <summary style="cursor: pointer; color: #666; font-size: 0.9em;">Debug Data</summary>
                    <pre style="background: #f8f9fa; padding: 10px; border-radius: 4px; margin-top: 8px; font-size: 0.8em; overflow-x: auto; max-height: 200px; overflow-y: auto;">${JSON.stringify(result, null, 2)}</pre>
                </details>
            `;

            this.resultsContent.innerHTML = html;
        } catch (error) {
            console.error('Error displaying sync results:', error);
            this.resultsContent.innerHTML = `
                <div class="sync-results-summary">
                    <h4>Git Notes Sync Results</h4>
                    <div class="sync-status error">
                        Status: Display Error
                    </div>
                    <div class="sync-details">
                        <h5>Details</h5>
                        <div class="details-content">Error displaying results: ${error.message}</div>
                    </div>
                </div>
            `;
        }
    }

    displayFetchResults(result) {
        try {
            // Handle case where result might be undefined or malformed
            if (!result) {
                result = { success: false, message: 'No response from server' };
            }

            // Extract the actual fetch result from the response structure
            const fetchSuccess = result.fetch_result === true || result.status === "success" || (result.success && result.fetch_result === true);
            const message = result.message || result.data?.message || result.error || 'No details available';
            
            let html = `
                <div class="fetch-results-summary">
                    <h4>Git Notes Fetch Results</h4>
                    <div class="fetch-status ${fetchSuccess ? 'success' : 'error'}">
                        Status: ${fetchSuccess ? 'Fetch Successful' : 'Fetch Failed'}
                    </div>
                </div>
            `;

            // Only show details if it's different from the default success message or if there's an error
            if (!fetchSuccess || (message && message !== 'Git notes fetched successfully from remote')) {
                html += `
                    <div class="fetch-details">
                        <h5>Details</h5>
                        <div class="details-content">${message}</div>
                    </div>
                `;
            }

            if (result.fetched_notes && result.fetched_notes.length > 0) {
                html += `
                    <div class="fetched-notes">
                        <h5>Fetched Notes (${result.fetched_notes.length})</h5>
                        ${result.fetched_notes.map(note => `
                            <div class="note-item">
                                <div class="note-commit">${note.commit || 'Unknown commit'}</div>
                                <div class="note-preview">${this.truncateNote(note.content || 'No content')}</div>
                                <div class="note-meta">Size: ${note.size || 'Unknown'} | Modified: ${note.modified || 'Unknown'}</div>
                            </div>
                        `).join('')}
                    </div>
                `;
            }

            if (result.new_notes_count !== undefined) {
                html += `
                    <div class="fetch-summary">
                        <div class="summary-item">
                            <span class="summary-label">New Notes:</span>
                            <span class="summary-value">${result.new_notes_count}</span>
                        </div>
                        <div class="summary-item">
                            <span class="summary-label">Updated Notes:</span>
                            <span class="summary-value">${result.updated_notes_count || 0}</span>
                        </div>
                    </div>
                `;
            }

            // Only show raw data in collapsed state for debugging
            html += `
                <details class="raw-data" style="margin-top: 15px;">
                    <summary style="cursor: pointer; color: #666; font-size: 0.9em;">Debug Data</summary>
                    <pre style="background: #f8f9fa; padding: 10px; border-radius: 4px; margin-top: 8px; font-size: 0.8em; overflow-x: auto; max-height: 200px; overflow-y: auto;">${JSON.stringify(result, null, 2)}</pre>
                </details>
            `;

            this.resultsContent.innerHTML = html;
        } catch (error) {
            console.error('Error displaying fetch results:', error);
            this.resultsContent.innerHTML = `
                <div class="fetch-results-summary">
                    <h4>Git Notes Fetch Results</h4>
                    <div class="fetch-status error">
                        Status: Display Error
                    </div>
                    <div class="fetch-details">
                        <h5>Details</h5>
                        <div class="details-content">Error displaying results: ${error.message}</div>
                    </div>
                </div>
            `;
        }
    }

    displayNoteContent(result, commitHash) {
        let html = `
            <div class="note-content-header">
                <h4>Git Note for ${commitHash}</h4>
            </div>
        `;

        if (result.note && (
            (result.note.semantic_events && Array.isArray(result.note.semantic_events) && result.note.semantic_events.length > 0) ||
            (result.note.content && result.note.content.trim())
        )) {
            const note = result.note;
            
            // If it's a semantic note with events, display them nicely
            if (note.semantic_events && Array.isArray(note.semantic_events)) {
                html += `
                    <div class="note-content">
                        <div class="note-meta-info">
                            <div class="meta-item">
                                <span class="meta-label">Commit:</span>
                                <span class="meta-value">${note.commit_hash || commitHash}</span>
                            </div>
                            <div class="meta-item">
                                <span class="meta-label">Analyzer:</span>
                                <span class="meta-value">${note.analyzer || 'Unknown'}</span>
                            </div>
                            <div class="meta-item">
                                <span class="meta-label">Events:</span>
                                <span class="meta-value">${note.semantic_events.length}</span>
                            </div>
                            <div class="meta-item">
                                <span class="meta-label">Timestamp:</span>
                                <span class="meta-value">${note.timestamp || 'Unknown'}</span>
                            </div>
                        </div>
                        
                        <div class="semantic-events">
                            <h5>Semantic Events (${note.semantic_events.length}):</h5>
                            ${note.semantic_events.map((event, index) => `
                                <div class="event-item" style="border-left: 3px solid #4CAF50; padding-left: 15px; margin-bottom: 15px;">
                                    <div class="event-header">
                                        <strong>${event.event_type}</strong> - ${event.node_id}
                                        <span style="color: #666; font-size: 0.9em;">(${event.location})</span>
                                    </div>
                                    <div class="event-details" style="margin-top: 5px;">
                                        <div><strong>Details:</strong> ${event.details}</div>
                                        <div><strong>Layer:</strong> ${event.layer} - ${event.layer_description}</div>
                                        <div><strong>Confidence:</strong> ${(event.confidence * 100).toFixed(1)}%</div>
                                        <div><strong>Impact:</strong> ${event.impact}</div>
                                        ${event.reasoning ? `<div><strong>Reasoning:</strong> ${event.reasoning}</div>` : ''}
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
            } else {
                // Display as regular note content
                html += `
                    <div class="note-content">
                        <div class="note-meta-info">
                            <div class="meta-item">
                                <span class="meta-label">Commit:</span>
                                <span class="meta-value">${note.commit || commitHash}</span>
                            </div>
                            <div class="meta-item">
                                <span class="meta-label">Size:</span>
                                <span class="meta-value">${note.size || 'Unknown'}</span>
                            </div>
                            <div class="meta-item">
                                <span class="meta-label">Created:</span>
                                <span class="meta-value">${note.created || 'Unknown'}</span>
                            </div>
                        </div>
                        
                        <div class="note-body">
                            <h5>Note Content:</h5>
                            <pre class="note-text">${note.content || 'No content available'}</pre>
                        </div>
                    </div>
                `;
            }
        } else {
            html += `
                <div class="no-note">
                    <div class="no-note-message">
                        ${result.error || 'No note found for this commit'}
                    </div>
                    <div class="no-note-tip">
                        Tip: Git notes may not exist for all commits. Try a different commit hash or create a note first.
                    </div>
                </div>
            `;
        }

        // Add raw data
        html += `
            <details class="raw-data" style="margin-top: 20px;">
                <summary style="cursor: pointer; color: #666; font-size: 0.9em;">Debug Data</summary>
                <pre style="background: #f8f9fa; padding: 10px; border-radius: 4px; margin-top: 8px; font-size: 0.8em; overflow-x: auto; max-height: 200px; overflow-y: auto;">${JSON.stringify(result, null, 2)}</pre>
            </details>
        `;

        this.resultsContent.innerHTML = html;
    }

    truncateNote(content, maxLength = 100) {
        if (!content || content.length <= maxLength) {
            return content;
        }
        return content.substring(0, maxLength) + '...';
    }

    async updateRepositorySelect(repositories) {
        if (this.repoSelect) {
            const registeredRepos = repositories.filter(repo => repo.registered);
            
            // Clear existing options
            this.repoSelect.innerHTML = '<option value="">Select a repository...</option>';
            
            // Add repository options with current branch info
            for (const repo of registeredRepos) {
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
                this.repoSelect.appendChild(option);
            }
        }
    }
}

// Export for use in main app
window.GitNotesManager = GitNotesManager;
