/**
 * Cleanup Manager Component
 * Handles repository cleanup operations and database maintenance
 */
class CleanupManager {
    constructor(apiClient, utils) {
        this.api = apiClient;
        this.utils = utils;
        this.initializeElements();
        this.attachEventListeners();
    }

    initializeElements() {
        this.repoSelect = document.getElementById('cleanup-repo');
        this.cleanOrphanedButton = document.querySelector('button[onclick="cleanupOrphanedData()"]');
        this.cleanUnreachableButton = document.querySelector('button[onclick="cleanupUnreachableCommits()"]');
        this.showStatsButton = document.querySelector('button[onclick="getDatabaseStats()"]');
        this.resultsContainer = document.getElementById('cleanup-results');
        this.resultsContent = document.getElementById('cleanup-results-content');
    }

    attachEventListeners() {
        if (this.cleanOrphanedButton) {
            this.cleanOrphanedButton.onclick = () => this.cleanupOrphanedData();
        }

        if (this.cleanUnreachableButton) {
            this.cleanUnreachableButton.onclick = () => this.cleanupUnreachableCommits();
        }

        if (this.showStatsButton) {
            this.showStatsButton.onclick = () => this.getDatabaseStats();
        }
    }

    async cleanupOrphanedData() {
        const repoPath = this.repoSelect.value;
        
        if (!repoPath) {
            this.utils.showError('Please select a repository');
            return;
        }

        if (!confirm('Are you sure you want to clean orphaned data? This action cannot be undone.')) {
            return;
        }

        try {
            this.utils.showLoading(this.resultsContent, 'Cleaning orphaned data...');
            this.resultsContainer.style.display = 'block';

            const result = await this.api.cleanupOrphanedData({
                repository_path: repoPath
            });

            this.displayCleanupResults(result, 'Orphaned Data Cleanup');

        } catch (error) {
            this.utils.showError(`Failed to cleanup orphaned data: ${error.message}`);
            this.resultsContainer.style.display = 'none';
        }
    }

    async cleanupUnreachableCommits() {
        const repoPath = this.repoSelect.value;
        
        if (!repoPath) {
            this.utils.showError('Please select a repository');
            return;
        }

        if (!confirm('Are you sure you want to clean unreachable commits? This action cannot be undone.')) {
            return;
        }

        try {
            this.utils.showLoading(this.resultsContent, 'Cleaning unreachable commits...');
            this.resultsContainer.style.display = 'block';

            const result = await this.api.cleanupUnreachableCommits({
                repository_path: repoPath
            });

            this.displayCleanupResults(result, 'Unreachable Commits Cleanup');

        } catch (error) {
            this.utils.showError(`Failed to cleanup unreachable commits: ${error.message}`);
            this.resultsContainer.style.display = 'none';
        }
    }

    async getDatabaseStats() {
        const repoPath = this.repoSelect.value;
        
        if (!repoPath) {
            this.utils.showError('Please select a repository');
            return;
        }

        try {
            this.utils.showLoading(this.resultsContent, 'Getting database statistics...');
            this.resultsContainer.style.display = 'block';

            const result = await this.api.getDatabaseStats({
                repository_path: repoPath
            });

            this.displayDatabaseStats(result);

        } catch (error) {
            this.utils.showError(`Failed to get database stats: ${error.message}`);
            this.resultsContainer.style.display = 'none';
        }
    }

    displayCleanupResults(result, operationType) {
        let html = `
            <div class="cleanup-results-summary">
                <h4>🧹 ${operationType} Results</h4>
                <div class="cleanup-status ${result.success ? 'success' : 'error'}">
                    Status: ${result.success ? '✅ Cleanup Successful' : '❌ Cleanup Failed'}
                </div>
            </div>
        `;

        if (result.summary) {
            const summary = result.summary;
            html += `
                <div class="cleanup-summary">
                    <h5>Cleanup Summary</h5>
                    <div class="summary-grid">
                        <div class="summary-item">
                            <span class="summary-label">Items Removed:</span>
                            <span class="summary-value">${summary.items_removed || 0}</span>
                        </div>
                        <div class="summary-item">
                            <span class="summary-label">Space Freed:</span>
                            <span class="summary-value">${summary.space_freed || 'Unknown'}</span>
                        </div>
                        <div class="summary-item">
                            <span class="summary-label">Processing Time:</span>
                            <span class="summary-value">${summary.processing_time || 'Unknown'}</span>
                        </div>
                    </div>
                </div>
            `;
        }

        if (result.details && result.details.length > 0) {
            html += `
                <div class="cleanup-details">
                    <h5>Cleanup Details</h5>
                    ${result.details.map(detail => `
                        <div class="detail-item">
                            <div class="detail-type">${detail.type || 'Unknown'}</div>
                            <div class="detail-description">${detail.description || 'No description'}</div>
                            <div class="detail-count">Count: ${detail.count || 0}</div>
                        </div>
                    `).join('')}
                </div>
            `;
        }

        if (result.warnings && result.warnings.length > 0) {
            html += `
                <div class="cleanup-warnings">
                    <h5>⚠️ Warnings</h5>
                    <ul>
                        ${result.warnings.map(warning => `<li>${warning}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        if (result.errors && result.errors.length > 0) {
            html += `
                <div class="cleanup-errors">
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
                <summary style="cursor: pointer; color: #4CAF50;">View Raw Cleanup Data</summary>
                <pre style="background: #f8f9fa; padding: 15px; border-radius: 4px; margin-top: 10px; font-size: 0.9em; overflow-x: auto;">${JSON.stringify(result, null, 2)}</pre>
            </details>
        `;

        this.resultsContent.innerHTML = html;
    }

    displayDatabaseStats(result) {
        let html = `
            <div class="stats-summary">
                <h4>📊 Database Statistics</h4>
                <div class="stats-status ${result.success ? 'success' : 'error'}">
                    Status: ${result.success ? '✅ Stats Retrieved' : '❌ Failed to Get Stats'}
                </div>
            </div>
        `;

        if (result.stats) {
            const stats = result.stats;
            
            // Overall statistics
            html += `
                <div class="database-overview">
                    <h5>Database Overview</h5>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <span class="stat-label">Database Size:</span>
                            <span class="stat-value">${stats.database_size || 'Unknown'}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Total Records:</span>
                            <span class="stat-value">${stats.total_records || 0}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Last Updated:</span>
                            <span class="stat-value">${stats.last_updated || 'Unknown'}</span>
                        </div>
                    </div>
                </div>
            `;

            // Table statistics
            if (stats.tables) {
                html += `
                    <div class="table-stats">
                        <h5>Table Statistics</h5>
                        <div class="tables-list">
                            ${Object.entries(stats.tables).map(([tableName, tableStats]) => `
                                <div class="table-item">
                                    <div class="table-name">${tableName}</div>
                                    <div class="table-details">
                                        Records: ${tableStats.count || 0} | 
                                        Size: ${tableStats.size || 'Unknown'} |
                                        Last Modified: ${tableStats.last_modified || 'Unknown'}
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
            }

            // Performance metrics
            if (stats.performance) {
                html += `
                    <div class="performance-stats">
                        <h5>Performance Metrics</h5>
                        <div class="performance-grid">
                            <div class="perf-item">
                                <span class="perf-label">Query Time:</span>
                                <span class="perf-value">${stats.performance.avg_query_time || 'Unknown'}</span>
                            </div>
                            <div class="perf-item">
                                <span class="perf-label">Index Usage:</span>
                                <span class="perf-value">${stats.performance.index_usage || 'Unknown'}</span>
                            </div>
                            <div class="perf-item">
                                <span class="perf-label">Cache Hit Ratio:</span>
                                <span class="perf-value">${stats.performance.cache_hit_ratio || 'Unknown'}</span>
                            </div>
                        </div>
                    </div>
                `;
            }

            // Repository-specific stats
            if (stats.repository) {
                html += `
                    <div class="repo-stats">
                        <h5>Repository Statistics</h5>
                        <div class="repo-details">
                            <div class="repo-stat">
                                <span class="repo-label">Semantic Events:</span>
                                <span class="repo-value">${stats.repository.semantic_events || 0}</span>
                            </div>
                            <div class="repo-stat">
                                <span class="repo-label">Commits Analyzed:</span>
                                <span class="repo-value">${stats.repository.commits_analyzed || 0}</span>
                            </div>
                            <div class="repo-stat">
                                <span class="repo-label">Files Tracked:</span>
                                <span class="repo-value">${stats.repository.files_tracked || 0}</span>
                            </div>
                            <div class="repo-stat">
                                <span class="repo-label">Active Branches:</span>
                                <span class="repo-value">${stats.repository.active_branches || 0}</span>
                            </div>
                        </div>
                    </div>
                `;
            }
        }

        // Recommendations
        if (result.recommendations && result.recommendations.length > 0) {
            html += `
                <div class="stats-recommendations">
                    <h5>💡 Recommendations</h5>
                    <ul>
                        ${result.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        // Add raw data
        html += `
            <details class="raw-data" style="margin-top: 20px;">
                <summary style="cursor: pointer; color: #4CAF50;">View Raw Statistics Data</summary>
                <pre style="background: #f8f9fa; padding: 15px; border-radius: 4px; margin-top: 10px; font-size: 0.9em; overflow-x: auto;">${JSON.stringify(result, null, 2)}</pre>
            </details>
        `;

        this.resultsContent.innerHTML = html;
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
window.CleanupManager = CleanupManager;
