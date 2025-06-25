/**
 * Main Application Entry Point
 * Initializes all dashboard components and handles navigation
 */
class SVCSDashboard {
    constructor() {
        this.api = new APIClient();
        this.utils = new UtilsWrapper();
        this.components = {};
        this.repositories = [];
        this.selectedRepository = null;
        
        this.initializeComponents();
        this.attachNavigationListeners();
        this.loadInitialData();
    }

    initializeComponents() {
        // Initialize all dashboard components
        this.components.systemStatus = new SystemStatus(this.api, this.utils);
        this.components.repositoryManager = new RepositoryManager(this.api, this.utils);
        this.components.branchManager = new BranchManager(this.api, this.utils);
        this.components.semanticSearch = new SemanticSearch(this.api, this.utils);
        this.components.naturalLanguageQuery = new NaturalLanguageQuery(this.api, this.utils);
        this.components.evolutionTracker = new EvolutionTracker(this.api, this.utils);
        this.components.analytics = new Analytics(this.api, this.utils);
        this.components.qualityAnalysis = new QualityAnalysis(this.api, this.utils);
        this.components.branchComparison = new BranchComparison(this.api, this.utils);
        this.components.ciIntegration = new CIIntegration(this.api, this.utils);
        this.components.gitNotesManager = new GitNotesManager(this.api, this.utils);
        this.components.cleanupManager = new CleanupManager(this.api, this.utils);

        console.log('All dashboard components initialized');
    }

    attachNavigationListeners() {
        // Get all navigation buttons
        const navButtons = document.querySelectorAll('.nav-item');
        
        navButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const sectionId = this.extractSectionId(button);
                if (sectionId) {
                    this.showSection(sectionId);
                }
            });
        });

        // Handle direct section navigation from onclick attributes
        this.setupGlobalNavigationFunctions();
    }

    extractSectionId(button) {
        // Extract section ID from button's onclick attribute or data attribute
        const onclickAttr = button.getAttribute('onclick');
        if (onclickAttr) {
            const match = onclickAttr.match(/showSection\\('([^']+)'\\)/);
            if (match) {
                return match[1];
            }
        }
        return button.dataset.section;
    }

    setupGlobalNavigationFunctions() {
        // Make showSection globally available for onclick handlers
        window.showSection = (sectionId) => this.showSection(sectionId);
        
        // Repository Manager functions
        window.showAddRepositoryForm = () => this.components.repositoryManager?.showAddRepositoryForm();
        window.hideAddRepositoryForm = () => this.components.repositoryManager?.hideAddRepositoryForm();
        window.registerRepository = () => this.components.repositoryManager?.registerRepository();
        window.initializeRepository = () => this.components.repositoryManager?.initializeRepository();
        
        // Semantic Search functions
        window.searchEventsBasic = () => this.components.semanticSearch?.performUnifiedSearch();
        window.searchEventsAdvanced = () => this.components.semanticSearch?.performUnifiedSearch();
        window.performSearch = () => this.components.semanticSearch?.performUnifiedSearch();
        window.toggleAdvancedFilters = () => this.components.semanticSearch?.toggleAdvancedFilters();
        window.getRecentActivity = () => this.components.semanticSearch?.getRecentActivity();
        window.clearSearchFilters = () => this.components.semanticSearch?.clearSearchFilters();
        
        // Natural Language Query functions
        window.executeNaturalQuery = () => this.components.naturalLanguageQuery?.executeNaturalQuery();
        
        // Evolution Tracker functions
        window.trackEvolution = () => this.components.evolutionTracker?.trackEvolution();
        
        // Analytics functions
        window.generateAnalytics = () => this.components.analytics?.generateAnalytics();
        
        // Quality Analysis functions
        window.analyzeQuality = () => this.components.qualityAnalysis?.analyzeQuality();
        
        // Branch Comparison functions
        window.compareBranches = () => this.components.branchComparison?.compareBranches();
        window.toggleBranchInputMode = () => this.components.branchComparison?.toggleBranchInputMode();
        
        // CI Integration functions
        window.runPRAnalysis = () => this.components.ciIntegration?.runPRAnalysis();
        window.runQualityGate = () => this.components.ciIntegration?.runQualityGate();
        window.refreshBranchInfo = () => this.components.ciIntegration?.refreshBranchInfo();
        window.showAvailableBranches = () => this.components.ciIntegration?.showAvailableBranches();
        window.showCurrentBranch = () => this.components.ciIntegration?.showCurrentBranch();
        
        // Git Notes Manager functions
        window.syncNotes = () => this.components.gitNotesManager?.syncNotes();
        window.fetchNotes = () => this.components.gitNotesManager?.fetchNotes();
        window.showNote = () => this.components.gitNotesManager?.showNote();
        
        // Cleanup Manager functions
        window.cleanupOrphanedData = () => this.components.cleanupManager?.cleanupOrphanedData();
        window.cleanupUnreachableCommits = () => this.components.cleanupManager?.cleanupUnreachableCommits();
        window.getDatabaseStats = () => this.components.cleanupManager?.getDatabaseStats();
    }

    showSection(sectionId) {
        console.log(`Navigating to section: ${sectionId}`);
        
        // Hide all sections
        const allSections = document.querySelectorAll('.tool-section');
        allSections.forEach(section => {
            section.style.display = 'none';
        });

        // Update navigation active state
        const allNavItems = document.querySelectorAll('.nav-item');
        allNavItems.forEach(item => {
            item.classList.remove('active');
        });

        // Show selected section
        const targetSection = document.getElementById(sectionId);
        if (targetSection) {
            targetSection.style.display = 'block';
            
            // Update active nav item
            const activeNavItem = document.querySelector(`[onclick*="${sectionId}"], [data-section="${sectionId}"]`);
            if (activeNavItem) {
                activeNavItem.classList.add('active');
            }
            
            // Trigger section-specific initialization if needed
            this.onSectionShow(sectionId);
        } else {
            console.warn(`Section not found: ${sectionId}`);
        }
    }

    onSectionShow(sectionId) {
        // Perform section-specific setup when a section is shown
        switch (sectionId) {
            case 'repositories':
                // Refresh repository list when repositories section is shown
                this.components.repositoryManager?.discoverRepositories();
                break;
            case 'search':
                // Update repository selects for search
                this.updateAllRepositorySelects();
                break;
            case 'compare':
                // Ensure branch dropdowns are populated for comparison
                this.updateAllRepositorySelects();
                break;
            case 'ci-integration':
                // Update repository select for CI/CD
                this.updateAllRepositorySelects();
                break;
            default:
                // For other sections, just update repository selects
                this.updateAllRepositorySelects();
                break;
        }
    }

    async loadInitialData() {
        try {
            // Load system status
            await this.components.systemStatus.load();
            
            // Discover repositories
            await this.components.repositoryManager.discoverRepositories();
            
            // Show repositories section by default
            this.showSection('repositories');
            
            console.log('Initial data loaded successfully');
        } catch (error) {
            console.error('Failed to load initial data:', error);
            this.utils.showError('Failed to load initial dashboard data');
        }
    }

    updateAllRepositorySelects() {
        // Update all repository select dropdowns across components
        const repositories = this.components.repositoryManager?.repositories || [];
        
        Object.values(this.components).forEach(component => {
            if (typeof component.updateRepositorySelect === 'function') {
                component.updateRepositorySelect(repositories);
            }
        });
    }

    onRepositoriesUpdated(repositories) {
        // Called when repositories are discovered or updated
        this.repositories = repositories;
        this.updateAllRepositorySelects();
    }

    selectRepository(path) {
        // Handle repository selection
        this.selectedRepository = this.repositories.find(repo => repo.path === path);
        console.log('Selected repository:', this.selectedRepository);
        
        // Notify components of repository selection if needed
        Object.values(this.components).forEach(component => {
            if (typeof component.onRepositorySelected === 'function') {
                component.onRepositorySelected(this.selectedRepository);
            }
        });
    }

    // Utility methods for global access
    showSuccess(message) {
        this.utils.showSuccess(message);
    }

    showError(message) {
        this.utils.showError(message);
    }

    showResult(title, content, containerId) {
        this.utils.showResult(title, content, containerId);
    }
}

// Make global navigation function available immediately
window.showSection = function(sectionId) {
    if (window.dashboard && window.dashboard.showSection) {
        window.dashboard.showSection(sectionId);
    } else {
        console.warn('Dashboard not yet initialized, queuing section:', sectionId);
        // Queue the section to show after initialization
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(() => {
                if (window.dashboard && window.dashboard.showSection) {
                    window.dashboard.showSection(sectionId);
                }
            }, 100);
        });
    }
};

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing SVCS Dashboard...');
    
    // Create global dashboard instance
    window.dashboard = new SVCSDashboard();
    
    // Make utility functions globally available for legacy compatibility
    window.showSuccess = (message) => window.dashboard.showSuccess(message);
    window.showError = (message) => window.dashboard.showError(message);
    window.showResult = (title, content, containerId) => window.dashboard.showResult(title, content, containerId);
    
    console.log('SVCS Dashboard initialized successfully');
});
