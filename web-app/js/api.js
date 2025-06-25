// API Communication Module
class APIClient {
    constructor(baseURL = Config.API_BASE_URL) {
        this.baseURL = baseURL;
    }

    async callAPI(endpoint, data = null, options = {}) {
        console.log(`Calling API: ${endpoint}`, data);
        
        try {
            const requestOptions = {
                method: data ? 'POST' : 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            };
            
            if (data) {
                requestOptions.body = JSON.stringify(data);
            }
            
            const response = await fetch(this.baseURL + endpoint, requestOptions);
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error || `HTTP ${response.status}: ${response.statusText}`);
            }
            
            if (!result.success) {
                throw new Error(result.error || 'API call failed');
            }
            
            return result.data || result;
        } catch (error) {
            console.error(`API call failed:`, error);
            throw error;
        }
    }

    // System endpoints
    async getSystemStatus() {
        return this.callAPI('/api/system/status');
    }

    // Repository endpoints
    async discoverRepositories() {
        return this.callAPI('/api/repositories/discover');
    }

    async getRepositoryStatus(repositoryPath) {
        return this.callAPI('/api/repositories/status', {
            repository_path: repositoryPath
        });
    }

    async getRepositoryMetadata(repositoryPath) {
        return this.callAPI('/api/repository/metadata', {
            repository_path: repositoryPath
        });
    }

    async registerRepository(params) {
        return this.callAPI('/api/repositories/register', params);
    }

    async unregisterRepository(params) {
        return this.callAPI('/api/repositories/unregister', params);
    }

    async initializeRepository(params) {
        return this.callAPI('/api/repositories/initialize', params);
    }

    // Semantic search endpoints
    async searchEvents(params) {
        return this.callAPI('/api/semantic/search_events', params);
    }

    async searchEventsAdvanced(params) {
        return this.callAPI('/api/semantic/search_advanced', params);
    }

    async getRecentActivity(repositoryPath, days = 7, limit = 20) {
        return this.callAPI('/api/semantic/recent_activity', {
            repository_path: repositoryPath,
            days,
            limit
        });
    }

    async searchSemanticPatterns(params) {
        return this.callAPI('/api/semantic/pattern_search', params);
    }

    // Evolution tracking
    async trackEvolution(repositoryPath, nodeId, filters = {}) {
        return this.callAPI('/api/semantic/evolution', {
            repository_path: repositoryPath,
            node_id: nodeId,
            ...filters
        });
    }

    async getFilteredEvolution(params) {
        return this.callAPI('/api/semantic/filtered_evolution', params);
    }

    // Analytics endpoints
    async generateAnalytics(repositoryPath) {
        return this.callAPI('/api/analytics/generate', { repository_path: repositoryPath });
    }

    async getProjectStatistics(params) {
        return this.callAPI('/api/analytics/project_statistics', params);
    }

    // Quality analysis
    async analyzeQuality(repositoryPath) {
        return this.callAPI('/api/quality/analyze', { repository_path: repositoryPath });
    }

    // Branch comparison endpoints
    async compareBranches(params) {
        return this.callAPI('/api/compare/branches', params);
    }

    async getRepositoryBranches(repositoryPath) {
        return this.callAPI('/api/repository/branches', {
            repository_path: repositoryPath
        });
    }

    // CI/CD Integration endpoints
    async analyzePRImpact(params) {
        return this.callAPI('/api/ci/pr_analysis', params);
    }

    async runQualityGate(params) {
        return this.callAPI('/api/ci/quality_gate', params);
    }

    // Git Notes endpoints
    async syncGitNotes(params) {
        return this.callAPI('/api/notes/sync', params);
    }

    async fetchGitNotes(params) {
        return this.callAPI('/api/notes/fetch', params);
    }

    async getGitNote(params) {
        return this.callAPI('/api/notes/show', params);
    }

    // Cleanup endpoints
    async cleanupOrphanedData(params) {
        return this.callAPI('/api/cleanup/orphaned_data', params);
    }

    async cleanupUnreachableCommits(params) {
        return this.callAPI('/api/cleanup/unreachable_commits', params);
    }

    async getDatabaseStats(params) {
        return this.callAPI('/api/cleanup/database_stats', params);
    }

    // Natural language query
    async executeNaturalQuery(repositoryPath, query) {
        return this.callAPI('/api/query/natural_language', {
            repository_path: repositoryPath,
            query
        });
    }
}

// Export APIClient class
window.APIClient = APIClient;

// Create global API client instance
const API = new APIClient();
