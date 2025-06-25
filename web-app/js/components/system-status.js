// System Status Component
class SystemStatus {
    constructor(apiClient, utils) {
        this.api = apiClient;
        this.utils = utils;
        this.status = {};
        this.refreshInterval = null;
    }

    async load() {
        try {
            // Clear any existing capabilities section
            const existingCapabilities = document.querySelector('.system-info .capabilities-section');
            if (existingCapabilities) {
                existingCapabilities.remove();
            }
            
            this.status = await this.api.getSystemStatus();
            this.display();
        } catch (error) {
            console.error('Failed to load system status:', error);
            const grid = this.utils.$('system-info-grid');
            if (grid) {
                grid.innerHTML = `<div class="error">Failed to load system status: ${error.message}</div>`;
            }
        }
    }

    display() {
        const grid = this.utils.$('system-info-grid');
        if (!grid) return;

        // Format capabilities list for display
        const capabilitiesList = this.status.capabilities?.map(cap => 
            cap.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
        ).join('<br>• ') || '';

        grid.innerHTML = `
            <div class="info-item">
                <div class="value">${this.status.repositories?.registered || 0}</div>
                <div class="label">Registered Repos</div>
            </div>
            <div class="info-item">
                <div class="value">${this.status.repositories?.discovered || 0}</div>
                <div class="label">Discovered Repos</div>
            </div>
            <div class="info-item">
                <div class="value">${this.status.repo_local_available ? '✅' : '❌'}</div>
                <div class="label">Repo Local Available</div>
            </div>
        `;

        // Add capabilities as a separate section below the grid
        if (this.status.capabilities && this.status.capabilities.length > 0) {
            this.addCapabilitiesSection(grid.parentNode);
        }
    }

    addCapabilitiesSection(container) {
        // Remove existing capabilities section
        const existing = container.querySelector('.capabilities-section');
        if (existing) existing.remove();

        const capabilitiesList = this.status.capabilities.map(cap => 
            cap.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
        ).join('<br>• ');

        const capabilitiesSection = this.utils.createElement('div', 'capabilities-section');
        capabilitiesSection.style.cssText = `
            margin-top: 20px;
            background: white;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #dee2e6;
        `;
        capabilitiesSection.innerHTML = `
            <h4 style="color: #2c3e50; margin-bottom: 15px; display: flex; align-items: center;">
                <span style="background: #007bff; color: white; padding: 3px 8px; border-radius: 12px; font-size: 0.8em; margin-right: 10px;">${this.status.capabilities.length}</span>
                System Capabilities
            </h4>
            <div style="
                columns: 2; 
                column-gap: 20px; 
                font-size: 0.9em; 
                line-height: 1.6;
                color: #495057;
            ">
                • ${capabilitiesList}
            </div>
        `;

        container.appendChild(capabilitiesSection);
    }

    startAutoRefresh(interval = Config.UI.AUTO_REFRESH_INTERVAL) {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }

        this.refreshInterval = setInterval(() => {
            this.load();
        }, interval);
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    getStatus() {
        return this.status;
    }

    isRepoLocalAvailable() {
        return this.status.repo_local_available || false;
    }

    getCapabilities() {
        return this.status.capabilities || [];
    }

    getRepositoryCounts() {
        return this.status.repositories || { registered: 0, discovered: 0 };
    }
}

// Export to global scope for initialization
window.SystemStatus = SystemStatus;
