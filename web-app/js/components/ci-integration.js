/**
 * CI/CD Integration Component
 * Handles pull request analysis and quality gate checks
 */
class CIIntegration {
    constructor(apiClient, utils) {
        this.api = apiClient;
        this.utils = utils;
        this.initializeElements();
        this.attachEventListeners();
    }

    initializeElements() {
        this.repoSelect = document.getElementById('ci-repo');
        this.targetBranchSelect = document.getElementById('target-branch');
        this.strictModeCheckbox = document.getElementById('strict-mode');
        this.prAnalysisButton = document.querySelector('button[onclick="runPRAnalysis()"]');
        this.qualityGateButton = document.querySelector('button[onclick="runQualityGate()"]');
        this.refreshBranchButton = document.querySelector('button[onclick="refreshBranchInfo()"]');
        this.showBranchesButton = document.querySelector('button[onclick="showAvailableBranches()"]');
        this.showCurrentBranchButton = document.querySelector('button[onclick="showCurrentBranch()"]');
        this.resultsContainer = document.getElementById('ci-results');
        this.resultsContent = document.getElementById('ci-results-content');
        this.branchInfoContainer = document.getElementById('branch-info');
        this.branchInfoContent = document.getElementById('branch-info-content');
    }

    attachEventListeners() {
        if (this.repoSelect) {
            this.repoSelect.addEventListener('change', () => {
                this.loadBranches();
            });
        }

        if (this.prAnalysisButton) {
            this.prAnalysisButton.onclick = () => this.runPRAnalysis();
        }

        if (this.qualityGateButton) {
            this.qualityGateButton.onclick = () => this.runQualityGate();
        }

        if (this.refreshBranchButton) {
            this.refreshBranchButton.onclick = () => this.refreshBranchInfo();
        }

        if (this.showBranchesButton) {
            this.showBranchesButton.onclick = () => this.showAvailableBranches();
        }

        if (this.showCurrentBranchButton) {
            this.showCurrentBranchButton.onclick = () => this.showCurrentBranch();
        }
    }

    async loadBranches() {
        const repoPath = this.repoSelect.value;
        if (!repoPath) {
            this.clearTargetBranchSelect();
            return;
        }

        try {
            console.log('CI Integration: Loading branches for repo:', repoPath);
            const result = await this.api.getRepositoryBranches(repoPath);
            console.log('CI Integration: API result:', result);
            
            // The API client returns result.data directly, so we get the unwrapped data
            if (result && result.branches) {
                console.log('CI Integration: Found branches:', result.branches);
                this.populateTargetBranchSelect(result.branches, result.current_branch);
            } else {
                console.error('CI Integration: Invalid result structure:', result);
                throw new Error('Failed to load branches - invalid response structure');
            }
        } catch (error) {
            console.error('Error loading branches:', error);
            this.showBranchLoadError();
        }
    }

    clearTargetBranchSelect() {
        if (this.targetBranchSelect) {
            this.targetBranchSelect.innerHTML = '<option value="">Select branch...</option>';
        }
    }

    populateTargetBranchSelect(branches, currentBranch) {
        if (this.targetBranchSelect) {
            // Filter out current branch since comparing current to current doesn't make sense
            const targetBranches = branches.filter(branch => branch !== currentBranch);
            
            this.targetBranchSelect.innerHTML = '<option value="">Select target branch...</option>' +
                targetBranches.map(branch => {
                    return `<option value="${branch}">${branch}</option>`;
                }).join('');
        }
    }

    showBranchLoadError() {
        if (this.targetBranchSelect) {
            this.targetBranchSelect.innerHTML = '<option value="">Failed to load branches</option>';
        }
    }

    async runPRAnalysis() {
        const repoPath = this.repoSelect.value;
        const targetBranch = this.targetBranchSelect.value;

        if (!repoPath) {
            this.utils.showError('Please select a repository');
            return;
        }

        if (!targetBranch) {
            this.utils.showError('Please select a target branch');
            return;
        }

        try {
            this.utils.showLoading(this.resultsContent, 'Analyzing PR impact...');
            this.resultsContainer.style.display = 'block';

            const result = await this.api.analyzePRImpact({
                repository_path: repoPath,
                target_branch: targetBranch
            });

            this.displayPRAnalysisResults(result);

        } catch (error) {
            this.utils.showError(`PR analysis failed: ${error.message}`);
            this.resultsContainer.style.display = 'none';
        }
    }

    async runQualityGate() {
        const repoPath = this.repoSelect.value;
        const targetBranch = this.targetBranchSelect.value;
        const strictMode = this.strictModeCheckbox ? this.strictModeCheckbox.checked : false;

        if (!repoPath) {
            this.utils.showError('Please select a repository');
            return;
        }

        if (!targetBranch) {
            this.utils.showError('Please select a target branch');
            return;
        }

        try {
            this.utils.showLoading(this.resultsContent, 'Running quality gate checks...');
            this.resultsContainer.style.display = 'block';

            const result = await this.api.runQualityGate({
                repository_path: repoPath,
                target_branch: targetBranch,
                strict_mode: strictMode
            });

            this.displayQualityGateResults(result);

        } catch (error) {
            this.utils.showError(`Quality gate failed: ${error.message}`);
            this.resultsContainer.style.display = 'none';
        }
    }

    async refreshBranchInfo() {
        const repoPath = this.repoSelect.value;
        if (!repoPath) {
            this.utils.showError('Please select a repository');
            return;
        }

        try {
            this.utils.showLoading(this.branchInfoContent, 'Refreshing branch information...');
            this.branchInfoContainer.style.display = 'block';

            const result = await this.api.getRepositoryBranches(repoPath);
            this.displayBranchInfo(result);

        } catch (error) {
            this.utils.showError(`Failed to refresh branch info: ${error.message}`);
            this.branchInfoContainer.style.display = 'none';
        }
    }

    async showAvailableBranches() {
        const repoPath = this.repoSelect.value;
        if (!repoPath) {
            this.utils.showError('Please select a repository');
            return;
        }

        try {
            this.utils.showLoading(this.branchInfoContent, 'Loading available branches...');
            this.branchInfoContainer.style.display = 'block';

            const result = await this.api.getRepositoryBranches(repoPath);
            this.displayAvailableBranches(result);

        } catch (error) {
            this.utils.showError(`Failed to load branches: ${error.message}`);
            this.branchInfoContainer.style.display = 'none';
        }
    }

    async showCurrentBranch() {
        const repoPath = this.repoSelect.value;
        if (!repoPath) {
            this.utils.showError('Please select a repository');
            return;
        }

        try {
            this.utils.showLoading(this.branchInfoContent, 'Getting current branch...');
            this.branchInfoContainer.style.display = 'block';

            const result = await this.api.getRepositoryBranches(repoPath);
            this.displayCurrentBranch(result);

        } catch (error) {
            this.utils.showError(`Failed to get current branch: ${error.message}`);
            this.branchInfoContainer.style.display = 'none';
        }
    }

    displayPRAnalysisResults(result) {
        let html = `
            <div class="pr-analysis-summary">
                <h4>🔍 PR Analysis Results</h4>
                <div class="analysis-status ${result.success ? 'success' : 'error'}">
                    Status: ${result.success ? '✅ Analysis Complete' : '❌ Analysis Failed'}
                </div>
            </div>
        `;

        if (result.analysis) {
            const analysis = result.analysis;
            
            html += `
                <div class="pr-metrics">
                    <h5>Impact Metrics</h5>
                    <div class="metrics-grid">
                        <div class="metric-item">
                            <span class="metric-label">Files Changed:</span>
                            <span class="metric-value">${analysis.files_changed || 0}</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">Semantic Events:</span>
                            <span class="metric-value">${analysis.semantic_events || 0}</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">Risk Level:</span>
                            <span class="metric-value risk-${(analysis.risk_level || 'unknown').toLowerCase()}">${analysis.risk_level || 'Unknown'}</span>
                        </div>
                    </div>
                </div>
            `;

            if (analysis.changes && analysis.changes.length > 0) {
                html += `
                    <div class="pr-changes">
                        <h5>Detected Changes</h5>
                        ${analysis.changes.map(change => `
                            <div class="change-item">
                                <div class="change-type">${change.type || 'Unknown Change'}</div>
                                <div class="change-description">${change.description || 'No description available'}</div>
                                <div class="change-impact">Impact: ${change.impact || 'Unknown'}</div>
                            </div>
                        `).join('')}
                    </div>
                `;
            }
        }

        // Add raw data
        html += `
            <details class="raw-data" style="margin-top: 20px;">
                <summary style="cursor: pointer; color: #4CAF50;">View Raw Analysis Data</summary>
                <pre style="background: #f8f9fa; padding: 15px; border-radius: 4px; margin-top: 10px; font-size: 0.9em; overflow-x: auto;">${JSON.stringify(result, null, 2)}</pre>
            </details>
        `;

        this.resultsContent.innerHTML = html;
    }

    displayQualityGateResults(result) {
        let html = `
            <div class="quality-gate-summary">
                <h4>✅ Quality Gate Results</h4>
                <div class="gate-status ${result.passed ? 'success' : 'error'}">
                    Overall Status: ${result.passed ? '✅ PASSED' : '❌ FAILED'}
                </div>
            </div>
        `;

        if (result.checks) {
            html += `
                <div class="quality-checks">
                    <h5>Quality Checks</h5>
                    ${result.checks.map(check => `
                        <div class="check-item ${check.passed ? 'passed' : 'failed'}">
                            <div class="check-name">
                                ${check.passed ? '✅' : '❌'} ${check.name || 'Unknown Check'}
                            </div>
                            <div class="check-description">${check.description || 'No description available'}</div>
                            ${check.details ? `<div class="check-details">${check.details}</div>` : ''}
                        </div>
                    `).join('')}
                </div>
            `;
        }

        if (result.recommendations && result.recommendations.length > 0) {
            html += `
                <div class="quality-recommendations">
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
                <summary style="cursor: pointer; color: #4CAF50;">View Raw Quality Data</summary>
                <pre style="background: #f8f9fa; padding: 15px; border-radius: 4px; margin-top: 10px; font-size: 0.9em; overflow-x: auto;">${JSON.stringify(result, null, 2)}</pre>
            </details>
        `;

        this.resultsContent.innerHTML = html;
    }

    displayBranchInfo(result) {
        // The API client returns unwrapped data directly
        if (!result || !result.branches) {
            this.branchInfoContent.innerHTML = '<div class="error">Failed to load branch information</div>';
            return;
        }

        const data = result;
        let html = `
            <div class="branch-info-summary">
                <h5>🌿 Repository Branch Information</h5>
                <div class="branch-details">
                    <div><strong>Current Branch:</strong> ${data.current_branch || 'Unknown'}</div>
                    <div><strong>Total Branches:</strong> ${data.branches ? data.branches.length : 0}</div>
                </div>
            </div>
        `;

        if (data.branches && data.branches.length > 0) {
            html += `
                <div class="branches-list">
                    <h6>Available Branches:</h6>
                    <ul>
                        ${data.branches.map(branch => `
                            <li ${branch === data.current_branch ? 'style="font-weight: bold; color: #007bff;"' : ''}>
                                ${branch} ${branch === data.current_branch ? '(current)' : ''}
                            </li>
                        `).join('')}
                    </ul>
                </div>
            `;
        }

        this.branchInfoContent.innerHTML = html;
    }

    displayAvailableBranches(result) {
        this.displayBranchInfo(result);
    }

    displayCurrentBranch(result) {
        // The API client returns unwrapped data directly
        if (!result || !result.current_branch) {
            this.branchInfoContent.innerHTML = '<div class="error">Failed to get current branch</div>';
            return;
        }

        this.branchInfoContent.innerHTML = `
            <div class="current-branch-info">
                <h5>📍 Current Branch</h5>
                <div class="current-branch-name">${result.current_branch || 'Unknown'}</div>
                <div class="branch-tip">💡 This is the currently active branch in your repository</div>
            </div>
        `;
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
                let label = `${repo.name}:(loading...)`;
                try {
                    const branchInfo = await this.api.getRepositoryBranches(repo.path);
                    if (branchInfo && branchInfo.current_branch) {
                        label = `${repo.name}:(${branchInfo.current_branch})`;
                    } else {
                        label = `${repo.name}:(unknown)`;
                    }
                } catch (error) {
                    console.warn(`Failed to get branch info for ${repo.path}:`, error);
                    label = `${repo.name}:(error)`;
                }
                
                option.textContent = label;
                this.repoSelect.appendChild(option);
            }
        }
    }
}

// Export for use in main app
window.CIIntegration = CIIntegration;
