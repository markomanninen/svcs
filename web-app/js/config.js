// SVCS Dashboard Configuration
const Config = {
    // API Base URL - adjust this if your backend runs on a different port
    API_BASE_URL: '',
    
    // Default values
    DEFAULTS: {
        SEARCH_LIMIT: 20,
        COMPARE_LIMIT: 10,
        RECENT_ACTIVITY_DAYS: 7
    },
    
    // UI Configuration
    UI: {
        DEBOUNCE_DELAY: 300,
        AUTO_REFRESH_INTERVAL: 30000, // 30 seconds
        MAX_RESULTS_PER_PAGE: 100
    },
    
    // Event types for filtering
    EVENT_TYPES: [
        'function_added',
        'function_modified',
        'function_removed',
        'class_added',
        'class_modified',
        'class_removed',
        'variable_added',
        'variable_modified',
        'variable_removed',
        'import_added',
        'import_removed',
        'complexity_increased',
        'complexity_decreased',
        'error_handling_added',
        'error_handling_improved',
        'performance_optimization',
        'code_style_improved',
        'refactoring_applied'
    ],
    
    // Quality gate checks
    QUALITY_CHECKS: {
        complexity_increases: 'Complexity Control',
        error_handling_coverage: 'Error Handling Coverage',
        modernization_progress: 'Modernization Progress'
    },
    
    // Common branch names for auto-selection
    COMMON_BRANCHES: ['main', 'master', 'develop', 'development', 'staging'],
    
    // Messages
    MESSAGES: {
        NO_REPO_SELECTED: 'Please select a repository first',
        LOADING_REPOSITORIES: 'Loading repositories...',
        NO_REPOSITORIES_FOUND: 'No repositories found',
        SEARCH_FAILED: 'Search failed',
        ANALYSIS_FAILED: 'Analysis failed',
        OPERATION_SUCCESSFUL: 'Operation completed successfully',
        UNEXPECTED_ERROR: 'An unexpected error occurred'
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Config;
}

// Export to global scope for browser usage
window.Config = Config;
