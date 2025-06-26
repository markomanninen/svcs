/**
 * Repository Manager Component
 * Handles repository discovery, registration, and management
 */
class RepositoryManager {
    constructor(apiClient, utils) {
        this.api = apiClient;
        this.utils = utils;
        this.repositories = [];
        this.selectedRepository = null;
        this.initializeElements();
        this.attachEventListeners();
    }

    initializeElements() {
        this.repositoriesList = document.getElementById('repositories-list');
        this.addRepoForm = document.getElementById('add-repo-form');
        this.repoPathInput = document.getElementById('repo-path');
        this.repoNameInput = document.getElementById('repo-name');
    }

    attachEventListeners() {
        // Attach global functions for onclick handlers
        window.showAddRepositoryForm = () => this.showAddRepositoryForm();
        window.hideAddRepositoryForm = () => this.hideAddRepositoryForm();
        window.registerRepository = () => this.registerRepository();
        window.initializeRepository = () => this.initializeRepository();
        window.selectRepository = (path) => this.selectRepository(path);
        window.registerRepositoryPath = (path) => this.registerRepositoryPath(path);
        window.unregisterRepository = (path) => this.unregisterRepository(path);
        window.getRepositoryStatus = (path) => this.getRepositoryStatus(path);
        window.closeStatusModal = () => this.closeStatusModal();
    }

    async discoverRepositories() {
        try {
            this.utils.showLoading(this.repositoriesList, 'Discovering repositories...');
            
            const result = await this.api.discoverRepositories();
            this.repositories = result.repositories || [];
            this.displayRepositories();
            this.notifyRepositoriesUpdated();
            
            console.log(`Discovered ${this.repositories.length} repositories`);
        } catch (error) {
            console.error('Failed to discover repositories:', error);
            if (this.repositoriesList) {
                this.repositoriesList.innerHTML = 
                    `<div class="error">Failed to discover repositories: ${error.message}</div>`;
            }
        }
    }

    displayRepositories() {
        if (!this.repositoriesList) return;

        if (this.repositories.length === 0) {
            this.repositoriesList.innerHTML = `
                <div class="no-repositories">
                    <h3>No repositories found</h3>
                    <p>Click "Add Repository" to register a new SVCS repository</p>
                </div>
            `;
            return;
        }

        this.repositoriesList.innerHTML = this.repositories.map(repo => this.createRepositoryCard(repo)).join('');
    }

    createRepositoryCard(repo) {
        const statusClass = repo.registered ? 'registered' : 'discovered';
        const statusText = repo.registered ? 'Registered' : 'Discovered';
        
        return `
            <div class="repository-card ${repo.registered ? 'selected' : ''}" onclick="selectRepository('${repo.path}')">
                <div class="repo-header">
                    <div class="repo-name">${repo.name}</div>
                    <div class="repo-status ${statusClass}">
                        ${statusText}
                    </div>
                </div>
                <div class="repo-info">
                    Branch: ${repo.branch || 'unknown'} | 
                    Events: ${repo.event_count || 0} | 
                    Last Activity: ${repo.last_activity || 'unknown'}
                </div>
                <div class="repo-path">${repo.path}</div>
                <div style="margin-top: 15px;">
                    ${!repo.registered ? `<button class="btn btn-success" onclick="event.stopPropagation(); registerRepositoryPath('${repo.path}')">Register</button>` : ''}
                    <button class="btn btn-warning" onclick="event.stopPropagation(); getRepositoryStatus('${repo.path}')">Status</button>
                    ${repo.registered ? `<button class="btn btn-danger" onclick="event.stopPropagation(); unregisterRepository('${repo.path}')">Unregister</button>` : ''}
                </div>
            </div>
        `;
    }

    notifyRepositoriesUpdated() {
        // Notify main dashboard that repositories have been updated
        if (window.dashboard && typeof window.dashboard.onRepositoriesUpdated === 'function') {
            window.dashboard.onRepositoriesUpdated(this.repositories);
        }
    }

    selectRepository(path) {
        this.selectedRepository = this.repositories.find(repo => repo.path === path);
        console.log('Selected repository:', this.selectedRepository);
        
        // Notify main dashboard of selection
        if (window.dashboard && typeof window.dashboard.selectRepository === 'function') {
            window.dashboard.selectRepository(path);
        }
    }

    showAddRepositoryForm() {
        if (this.addRepoForm) {
            this.addRepoForm.style.display = 'block';
        }
    }

    hideAddRepositoryForm() {
        if (this.addRepoForm) {
            this.addRepoForm.style.display = 'none';
        }
        if (this.repoPathInput) {
            this.repoPathInput.value = '';
        }
        if (this.repoNameInput) {
            this.repoNameInput.value = '';
        }
    }

    async addRepository() {
        const path = this.repoPathInput ? this.repoPathInput.value : '';
        const name = this.repoNameInput ? this.repoNameInput.value : '';
        
        if (!path) {
            this.utils.showError('Please enter a repository path');
            return;
        }
        
        try {
            // Try to initialize first (this handles directory creation, git init, and svcs init)
            const initResult = await this.api.initializeRepository({ path: path });
            
            // Then register the repository
            await this.api.registerRepository({
                path: path,
                name: name || undefined
            });
            
            this.utils.showSuccess('Repository added and registered successfully!');
            this.hideAddRepositoryForm();
            this.discoverRepositories();
        } catch (error) {
            this.utils.showError(`Failed to add repository: ${error.message}`);
        }
    }

    async registerRepository() {
        const path = this.repoPathInput ? this.repoPathInput.value : '';
        const name = this.repoNameInput ? this.repoNameInput.value : '';
        
        if (!path) {
            this.utils.showError('Please enter a repository path');
            return;
        }
        
        try {
            await this.api.registerRepository({
                path: path,
                name: name || undefined
            });
            
            this.utils.showSuccess('Repository registered successfully!');
            this.hideAddRepositoryForm();
            this.discoverRepositories();
        } catch (error) {
            this.utils.showError(`Failed to register repository: ${error.message}`);
        }
    }

    async registerRepositoryPath(path) {
        try {
            await this.api.registerRepository({ path: path });
            this.utils.showSuccess('Repository registered successfully!');
            this.discoverRepositories();
        } catch (error) {
            this.utils.showError(`Failed to register repository: ${error.message}`);
        }
    }

    async initializeRepository() {
        const path = this.repoPathInput ? this.repoPathInput.value : '';
        
        if (!path) {
            this.utils.showError('Please enter a repository path');
            return;
        }
        
        try {
            const result = await this.api.initializeRepository({ path: path });
            this.utils.showSuccess('Repository initialized successfully!');
            this.hideAddRepositoryForm();
            this.discoverRepositories();
        } catch (error) {
            this.utils.showError(`Failed to initialize repository: ${error.message}`);
        }
    }

    async unregisterRepository(path) {
        if (!confirm('Are you sure you want to unregister this repository?')) {
            return;
        }
        
        try {
            await this.api.unregisterRepository({ path: path });
            this.utils.showSuccess('Repository unregistered successfully!');
            this.discoverRepositories();
        } catch (error) {
            this.utils.showError(`Failed to unregister repository: ${error.message}`);
        }
    }

    async getRepositoryStatus(path) {
        try {
            const status = await this.api.getRepositoryStatus(path);
            
            if (status) {
                const statusText = `
Repository Status: ${path}

• Repository Name: ${status.repository_name || 'Unknown'}
• Git Initialized: ${status.git_initialized ? '✅ Yes' : '❌ No'}
• SVCS Initialized: ${status.svcs_initialized ? '✅ Yes' : '❌ No'}
• Current Branch: ${status.current_branch || 'Unknown'}
• Database Exists: ${status.database_exists ? '✅ Yes' : '❌ No'}
• Recent Events (7 days): ${status.recent_events_count || 0}
• Registered in Registry: ${status.registered_in_central_registry ? '✅ Yes' : '❌ No'}
                `.trim();
                
                this.showStatusModal('Repository Status', statusText);
            } else {
                this.utils.showError(`Failed to get repository status: No data returned`);
            }
        } catch (error) {
            this.utils.showError(`Failed to get repository status: ${error.message}`);
        }
    }

    showStatusModal(title, content) {
        // Remove any existing status modal
        const existingModal = document.getElementById('status-modal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // Create status modal
        const modal = document.createElement('div');
        modal.id = 'status-modal';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        `;
        
        modal.innerHTML = `
            <div style="
                background: white;
                border-radius: 12px;
                padding: 30px;
                max-width: 600px;
                max-height: 80vh;
                overflow-y: auto;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
            ">
                <div style="
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 20px;
                    border-bottom: 1px solid #e9ecef;
                    padding-bottom: 15px;
                ">
                    <h3 style="margin: 0; color: #2c3e50;">${title}</h3>
                    <button onclick="closeStatusModal()" style="
                        background: #dc3545;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 8px 12px;
                        cursor: pointer;
                        font-size: 14px;
                    ">Close</button>
                </div>
                <pre style="
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    font-family: 'Courier New', monospace;
                    font-size: 14px;
                    line-height: 1.6;
                    margin: 0;
                    white-space: pre-wrap;
                ">${content}</pre>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Close modal when clicking outside
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }

    closeStatusModal() {
        const modal = document.getElementById('status-modal');
        if (modal) {
            modal.remove();
        }
    }

    updateRepositorySelect(repositories) {
        // This method is called by the main dashboard to update repository dropdowns
        // in other components when repositories change
        this.repositories = repositories || this.repositories;
    }
}

// Export for use in main app
window.RepositoryManager = RepositoryManager;
