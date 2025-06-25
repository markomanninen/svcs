/**
 * Branch Comparison Component
 * Handles comparing semantic changes between two git branches
 */
class BranchComparison {
    constructor(apiClient, utils) {
        this.api = apiClient;
        this.utils = utils;
        this.initializeElements();
        this.attachEventListeners();
    }

    initializeElements() {
        this.repoSelect = document.getElementById('compare-repo');
        this.branch1Select = document.getElementById('branch1');
        this.branch2Select = document.getElementById('branch2');
        this.limitInput = document.getElementById('compare-limit');
        this.compareButton = document.querySelector('button[onclick="compareBranches()"]');
        this.resultsContainer = document.getElementById('compare-results');
        this.resultsContent = document.getElementById('compare-results-content');
    }

    attachEventListeners() {
        if (this.repoSelect) {
            this.repoSelect.addEventListener('change', () => {
                this.loadBranches();
            });
        }

        if (this.compareButton) {
            this.compareButton.onclick = () => this.compareBranches();
        }
    }

    // Add toggle functionality for branch input mode
    toggleBranchInputMode() {
        const branch1 = document.getElementById('branch1');
        const branch2 = document.getElementById('branch2');
        const toggleButton = document.querySelector('button[onclick="toggleBranchInputMode()"]');
        
        if (branch1.tagName === 'SELECT') {
            // Switch to text inputs
            const currentValue1 = branch1.value;
            const currentValue2 = branch2.value;
            
            branch1.outerHTML = `<input type="text" id="branch1" class="form-control" placeholder="main" value="${currentValue1}">`;
            branch2.outerHTML = `<input type="text" id="branch2" class="form-control" placeholder="develop" value="${currentValue2}">`;
            
            toggleButton.innerHTML = 'Switch to Dropdown Mode';
        } else {
            // Switch to select dropdowns
            const currentValue1 = branch1.value;
            const currentValue2 = branch2.value;
            
            branch1.outerHTML = `<select id="branch1" class="form-control"><option value="">Select branch...</option></select>`;
            branch2.outerHTML = `<select id="branch2" class="form-control"><option value="">Select branch...</option></select>`;
            
            // Restore values if they were text
            if (currentValue1) {
                document.getElementById('branch1').innerHTML += `<option value="${currentValue1}" selected>${currentValue1}</option>`;
            }
            if (currentValue2) {
                document.getElementById('branch2').innerHTML += `<option value="${currentValue2}" selected>${currentValue2}</option>`;
            }
            
            toggleButton.innerHTML = 'Switch to Text Input Mode';
            
            // Try to load branches
            this.loadBranches();
        }
    }

    async loadBranches() {
        const repoPath = this.repoSelect.value;
        if (!repoPath) {
            this.clearBranchSelects();
            return;
        }

        try {
            // Use repository status to get current branch info
            const result = await this.api.getRepositoryStatus(repoPath);
            if (result && result.current_branch) {
                this.populateBranchSelectsFromStatus(result);
            } else {
                console.log('No branch information available from repository status');
            }
        } catch (error) {
            console.error('Error loading branches:', error);
            // Don't show error for missing branch info, it's optional
        }
    }

    clearBranchSelects() {
        const selects = [this.branch1Select, this.branch2Select];
        selects.forEach(select => {
            if (select) {
                select.innerHTML = '<option value="">Select branch...</option>';
            }
        });
    }

    populateBranchSelects(branches, currentBranch) {
        const selects = [this.branch1Select, this.branch2Select];
        selects.forEach(select => {
            if (select) {
                select.innerHTML = '<option value="">Select branch...</option>' +
                    branches.map(branch => {
                        const label = branch === currentBranch ? `${branch} (current)` : branch;
                        return `<option value="${branch}">${label}</option>`;
                    }).join('');
            }
        });
    }

    showBranchLoadError() {
        const selects = [this.branch1Select, this.branch2Select];
        selects.forEach(select => {
            if (select) {
                select.innerHTML = '<option value="">Failed to load branches</option>';
            }
        });
    }

    async compareBranches() {
        const repoPath = this.repoSelect.value;
        const branch1 = this.branch1Select.value;
        const branch2 = this.branch2Select.value;
        const limit = parseInt(this.limitInput.value) || 10;

        if (!repoPath || !branch1 || !branch2) {
            this.utils.showError('Please select a repository and both branches');
            return;
        }

        if (branch1 === branch2) {
            this.utils.showError('Please select two different branches to compare');
            return;
        }

        try {
            this.utils.showLoading(this.resultsContent, 'Comparing branches...');
            this.resultsContainer.style.display = 'block';

            const result = await this.api.compareBranches({
                repository_path: repoPath,
                branch1: branch1,
                branch2: branch2,
                limit: limit
            });

            this.displayComparisonResults(result);

        } catch (error) {
            this.utils.showError(`Branch comparison failed: ${error.message}`);
            this.resultsContainer.style.display = 'none';
        }
    }

    displayComparisonResults(result) {
        if (!result.comparison) {
            this.resultsContent.innerHTML = '<div class="no-repositories">No comparison data available</div>';
            return;
        }

        const comparison = result.comparison;
        let html = `
            <div class="comparison-summary">
                <h4>Branch Comparison Summary</h4>
                <div class="comparison-meta">
                    <strong>Branch 1:</strong> ${comparison.branch1 || 'Unknown'}<br>
                    <strong>Branch 2:</strong> ${comparison.branch2 || 'Unknown'}<br>
                    <strong>Total Changes:</strong> ${comparison.total_changes || 0}
                </div>
            </div>
        `;

        if (comparison.changes && comparison.changes.length > 0) {
            html += `
                <div class="changes-list">
                    <h4>Semantic Changes</h4>
                    ${comparison.changes.map(change => `
                        <div class="change-item">
                            <div class="change-type">${change.change_type || 'Unknown'}</div>
                            <div class="change-details">${change.details || 'No details available'}</div>
                            <div class="change-meta">
                                Location: ${change.location || 'Unknown'} |
                                Branch: ${change.branch || 'Unknown'} |
                                Impact: ${change.impact || 'Unknown'}
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        } else {
            html += '<div class="no-repositories">No semantic changes detected between branches</div>';
        }

        // Add raw data in expandable section
        html += `
            <details class="raw-data" style="margin-top: 20px;">
                <summary style="cursor: pointer; color: #4CAF50;">View Raw Comparison Data</summary>
                <pre style="background: #f8f9fa; padding: 15px; border-radius: 4px; margin-top: 10px; font-size: 0.9em; overflow-x: auto;">${JSON.stringify(result, null, 2)}</pre>
            </details>
        `;

        this.resultsContent.innerHTML = html;
    }

    populateBranchSelectsFromStatus(statusResult) {
        const selects = [this.branch1Select, this.branch2Select];
        const currentBranch = statusResult.current_branch;
        
        // Add common branches and current branch
        const commonBranches = ['main', 'master', 'develop', 'staging'];
        const branches = [...new Set([currentBranch, ...commonBranches])].filter(Boolean);
        
        selects.forEach(select => {
            if (select && select.tagName === 'SELECT') {
                select.innerHTML = '<option value="">Select branch...</option>' +
                    branches.map(branch => {
                        const label = branch === currentBranch ? `${branch} (current)` : branch;
                        return `<option value="${branch}">${label}</option>`;
                    }).join('');
            }
        });
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
window.BranchComparison = BranchComparison;
