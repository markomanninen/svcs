// API Communication Module
class APIClient {
    constructor(baseURL = Config.API_BASE_URL) {
        this.baseURL = baseURL;
        // Cache for storing API responses temporarily
        this.cache = new Map();
        this.cacheTimeout = 30000; // 30 seconds
        this.pendingRequests = new Map(); // To prevent duplicate concurrent requests
    }

    // Cache management methods
    getCacheKey(endpoint, data) {
        return `${endpoint}:${JSON.stringify(data || {})}`;
    }

    isValidCacheEntry(entry) {
        return entry && (Date.now() - entry.timestamp) < this.cacheTimeout;
    }

    getCachedResponse(cacheKey) {
        const entry = this.cache.get(cacheKey);
        if (this.isValidCacheEntry(entry)) {
            console.log(`Cache hit for: ${cacheKey}`);
            return entry.data;
        }
        return null;
    }

    setCachedResponse(cacheKey, data) {
        this.cache.set(cacheKey, {
            data: data,
            timestamp: Date.now()
        });
    }

    clearCache() {
        this.cache.clear();
        this.pendingRequests.clear();
    }

    // Clear cache for specific repository
    clearRepositoryCache(repositoryPath) {
        const keysToDelete = [];
        for (const [key, value] of this.cache.entries()) {
            if (key.includes(repositoryPath)) {
                keysToDelete.push(key);
            }
        }
        keysToDelete.forEach(key => this.cache.delete(key));
    }

    async callAPI(endpoint, data = null, options = {}) {
        // Check if caching should be enabled for this endpoint
        const enableCache = options.cache !== false && this.shouldCache(endpoint);
        const cacheKey = enableCache ? this.getCacheKey(endpoint, data) : null;
        
        // Check cache first
        if (enableCache) {
            const cached = this.getCachedResponse(cacheKey);
            if (cached) {
                return cached;
            }

            // Check if there's already a pending request for the same data
            if (this.pendingRequests.has(cacheKey)) {
                console.log(`Waiting for pending request: ${cacheKey}`);
                return await this.pendingRequests.get(cacheKey);
            }
        }

        console.log(`Calling API: ${endpoint}`, data);
        
        const requestPromise = this.makeRequest(endpoint, data, options);
        
        // Store the pending request to prevent duplicates
        if (enableCache) {
            this.pendingRequests.set(cacheKey, requestPromise);
        }

        try {
            const result = await requestPromise;
            
            // Cache the successful result
            if (enableCache) {
                this.setCachedResponse(cacheKey, result);
            }
            
            return result;
        } catch (error) {
            throw error;
        } finally {
            // Clean up pending request
            if (enableCache) {
                this.pendingRequests.delete(cacheKey);
            }
        }
    }

    // Determine if an endpoint should be cached
    shouldCache(endpoint) {
        const cacheableEndpoints = [
            '/api/repository/branches',
            '/api/repositories/discover',
            '/api/repository/metadata'
        ];
        return cacheableEndpoints.includes(endpoint);
    }

    async makeRequest(endpoint, data, options) {
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
            
            // For git notes operations, allow success:false to be handled by the UI
            // rather than throwing an error
            if (!result.success && !endpoint.includes('/api/notes/')) {
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
        const result = await this.callAPI('/api/repositories/register', params);
        // Clear discovery cache since repositories have changed
        this.clearCache();
        return result;
    }

    async unregisterRepository(params) {
        const result = await this.callAPI('/api/repositories/unregister', params);
        // Clear discovery cache since repositories have changed
        this.clearCache();
        return result;
    }

    async initializeRepository(params) {
        const result = await this.callAPI('/api/repositories/initialize', params);
        // Clear cache for this repository
        if (params.repository_path) {
            this.clearRepositoryCache(params.repository_path);
        }
        return result;
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

    // Evolution tracking
    async trackEvolution(repositoryPath, nodeId, filters = {}) {
        return this.callAPI('/api/semantic/evolution', {
            repository_path: repositoryPath,
            node_id: nodeId,
            ...filters
        });
    }

    async getFilteredEvolution(params) {
        return this.callAPI('/api/semantic/evolution', params);
    }

    // Analytics endpoints
    async generateAnalytics(repositoryPath) {
        return this.callAPI('/api/analytics/generate', { repository_path: repositoryPath });
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

    // Force refresh of repository branches (clears cache first)
    async refreshRepositoryBranches(repositoryPath) {
        this.clearRepositoryCache(repositoryPath);
        return this.getRepositoryBranches(repositoryPath);
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
