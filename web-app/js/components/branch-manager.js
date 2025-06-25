// Branch Manager Component
class BranchManager {
    constructor(apiClient, utils) {
        this.api = apiClient;
        this.utils = utils;
        this.branches = {};
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Set up repository selection change handlers
        this.setupRepositoryListeners();
    }

    setupRepositoryListeners() {
        // Branch comparison - both branch dropdowns
        const compareRepoSelect = this.utils.$('compare-repo');
        if (compareRepoSelect) {
            compareRepoSelect.addEventListener('change', () => {
                this.loadBranches(compareRepoSelect.value, ['branch1', 'branch2']);
            });
        }

        // Note: CI repo select is handled by CIIntegration component
        // to avoid duplicate event listeners
    }

    async loadBranches(repoPath, targetSelectIds = []) {
        if (!repoPath) {
            // Clear branch dropdowns if no repo selected
            targetSelectIds.forEach(selectId => {
                this.utils.setSelectOptions(selectId, []);
            });
            return;
        }

        try {
            const result = await this.api.getRepositoryBranches(repoPath);
            
            // The API client returns unwrapped data directly
            if (result && result.branches) {
                const branches = result.branches;
                const currentBranch = result.current_branch;
                
                // Cache branches for this repository
                this.branches[repoPath] = {
                    branches,
                    currentBranch
                };

                // Populate target branch dropdowns
                const branchOptions = branches.map(branch => ({
                    value: branch,
                    label: branch === currentBranch ? `${branch} (current)` : branch
                }));

                targetSelectIds.forEach(selectId => {
                    this.utils.setSelectOptions(selectId, branchOptions, currentBranch);
                });
                
                console.log(`Loaded ${branches.length} branches for ${repoPath}`, branches);
            } else {
                throw new Error('Failed to load branches - invalid response structure');
            }
        } catch (error) {
            console.error('Error loading branches:', error);
            // Show placeholder in dropdowns with error indication
            targetSelectIds.forEach(selectId => {
                const select = this.utils.$(selectId);
                if (select) {
                    select.innerHTML = '<option value="">Failed to load branches</option>';
                }
            });
            this.utils.showError(`Failed to load branches: ${error.message}`);
        }
    }

    async refreshBranchInfo(repoPath) {
        if (!repoPath) {
            this.utils.showError('Please select a repository first');
            return;
        }

        try {
            const result = await this.api.getRepositoryBranches(repoPath);
            
            // The API client returns unwrapped data directly
            if (result && result.branches) {
                const branchInfoHtml = `
                    <div class="branch-info">
                        <h4>Branch Information</h4>
                        <p><strong>Current Branch:</strong> <code>${result.current_branch}</code></p>
                        <p><strong>Total Branches:</strong> ${result.branches.length}</p>
                        <h5>Available Branches:</h5>
                        <ul>
                            ${result.branches.map(branch => 
                                `<li>${branch === result.current_branch ? 
                                    `<strong>${branch} (current)</strong>` : 
                                    branch
                                }</li>`
                            ).join('')}
                        </ul>
                    </div>
                `;

                // Show in branch info panel
                const branchInfoPanel = this.utils.$('branch-info');
                if (branchInfoPanel) {
                    this.utils.show(branchInfoPanel);
                    const content = branchInfoPanel.querySelector('.result-content') || 
                        branchInfoPanel.querySelector('#branch-info-content');
                    if (content) {
                        content.innerHTML = branchInfoHtml;
                    }
                }

                this.utils.showSuccess('Branch information refreshed successfully');
            } else {
                throw new Error(result.error || 'Failed to get branch information');
            }
        } catch (error) {
            this.utils.showError(`Failed to refresh branch info: ${error.message}`);
        }
    }

    getBranches(repoPath) {
        return this.branches[repoPath] || null;
    }

    getCurrentBranch(repoPath) {
        const branchData = this.branches[repoPath];
        return branchData ? branchData.currentBranch : null;
    }

    getAllBranches(repoPath) {
        const branchData = this.branches[repoPath];
        return branchData ? branchData.branches : [];
    }

    validateBranch(repoPath, branchName) {
        const branches = this.getAllBranches(repoPath);
        return branches.includes(branchName);
    }

    // Handle section switching to refresh branch data if needed
    onSectionChange(sectionId) {
        if (sectionId === 'ci-integration') {
            const ciRepo = this.utils.$('ci-repo').value;
            if (ciRepo) {
                this.loadBranches(ciRepo, ['target-branch']);
            }
        } else if (sectionId === 'compare') {
            const compareRepo = this.utils.$('compare-repo').value;
            if (compareRepo) {
                this.loadBranches(compareRepo, ['branch1', 'branch2']);
            }
        }
    }
}

// Global functions for HTML onclick handlers
function refreshBranchInfo() {
    const repoPath = this.utils.$('ci-repo').value;
    if (branchManager) {
        branchManager.refreshBranchInfo(repoPath);
    }
}

function showAvailableBranches() {
    const repoPath = this.utils.$('ci-repo').value;
    if (!repoPath) {
        this.utils.showError('Please select a repository first');
        return;
    }

    if (branchManager) {
        branchManager.refreshBranchInfo(repoPath);
    }
}

function showCurrentBranch() {
    const repoPath = this.utils.$('ci-repo').value;
    if (!repoPath) {
        this.utils.showError('Please select a repository first');
        return;
    }

    const branchData = branchManager ? branchManager.getBranches(repoPath) : null;
    if (branchData) {
        const message = `Current branch: ${branchData.currentBranch}`;
        this.utils.showSuccess(message);
    } else {
        this.utils.showError('Branch information not available. Please refresh.');
    }
}

// Export to global scope
window.BranchManager = BranchManager;
