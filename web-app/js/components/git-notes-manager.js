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

            this.displaySyncResults(result);

        } catch (error) {
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
        let html = `
            <div class="sync-results-summary">
                <h4>🔄 Git Notes Sync Results</h4>
                <div class="sync-status ${result.success ? 'success' : 'error'}">
                    Status: ${result.success ? '✅ Sync Successful' : '❌ Sync Failed'}
                </div>
            </div>
        `;

        if (result.details) {
            html += `
                <div class="sync-details">
                    <h5>Sync Details</h5>
                    <div class="details-content">${result.details}</div>
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
                    <h5>❌ Errors</h5>
                    <ul>
                        ${result.errors.map(error => `<li>${error}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        // Add raw data
        html += `
            <details class="raw-data" style="margin-top: 20px;">
                <summary style="cursor: pointer; color: #4CAF50;">View Raw Sync Data</summary>
                <pre style="background: #f8f9fa; padding: 15px; border-radius: 4px; margin-top: 10px; font-size: 0.9em; overflow-x: auto;">${JSON.stringify(result, null, 2)}</pre>
            </details>
        `;

        this.resultsContent.innerHTML = html;
    }

    displayFetchResults(result) {
        let html = `
            <div class="fetch-results-summary">
                <h4>📥 Git Notes Fetch Results</h4>
                <div class="fetch-status ${result.success ? 'success' : 'error'}">
                    Status: ${result.success ? '✅ Fetch Successful' : '❌ Fetch Failed'}
                </div>
            </div>
        `;

        if (result.details) {
            html += `
                <div class="fetch-details">
                    <h5>Fetch Details</h5>
                    <div class="details-content">${result.details}</div>
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

        // Add raw data
        html += `
            <details class="raw-data" style="margin-top: 20px;">
                <summary style="cursor: pointer; color: #4CAF50;">View Raw Fetch Data</summary>
                <pre style="background: #f8f9fa; padding: 15px; border-radius: 4px; margin-top: 10px; font-size: 0.9em; overflow-x: auto;">${JSON.stringify(result, null, 2)}</pre>
            </details>
        `;

        this.resultsContent.innerHTML = html;
    }

    displayNoteContent(result, commitHash) {
        let html = `
            <div class="note-content-header">
                <h4>📝 Git Note for ${commitHash}</h4>
            </div>
        `;

        if (result.success && result.note) {
            const note = result.note;
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
        } else {
            html += `
                <div class="no-note">
                    <div class="no-note-message">
                        ${result.error || 'No note found for this commit'}
                    </div>
                    <div class="no-note-tip">
                        💡 Tip: Git notes may not exist for all commits. Try a different commit hash or create a note first.
                    </div>
                </div>
            `;
        }

        // Add raw data
        html += `
            <details class="raw-data" style="margin-top: 20px;">
                <summary style="cursor: pointer; color: #4CAF50;">View Raw Note Data</summary>
                <pre style="background: #f8f9fa; padding: 15px; border-radius: 4px; margin-top: 10px; font-size: 0.9em; overflow-x: auto;">${JSON.stringify(result, null, 2)}</pre>
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

    updateRepositorySelect(repositories) {
        if (this.repoSelect) {
            const registeredRepos = repositories.filter(repo => repo.registered);
            this.repoSelect.innerHTML = '<option value="">Select a repository...</option>' +
                registeredRepos.map(repo => 
                    `<option value="${repo.path}">${repo.name} (${repo.path})</option>`
                ).join('');
        }
    }
}

// Export for use in main app
window.GitNotesManager = GitNotesManager;
