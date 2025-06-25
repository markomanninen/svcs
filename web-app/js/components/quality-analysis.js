// Quality Analysis Component
class QualityAnalysis {
    constructor(apiClient, utils) {
        this.api = apiClient;
        this.utils = utils;
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        const analyzeBtn = document.getElementById('analyze-quality');
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => this.analyzeQuality());
        }
    }

    async analyzeQuality() {
        const repoPath = document.getElementById('quality-repo').value;
        
        if (!repoPath) {
            alert('Please select a repository for quality analysis');
            return;
        }

        const resultsDiv = document.getElementById('quality-results');
        resultsDiv.style.display = 'block';
        resultsDiv.innerHTML = '<div class="loading">Analyzing code quality...</div>';

        try {
            // Search for quality-related semantic patterns
            const patterns = await Promise.all([
                this.searchPattern(repoPath, 'performance'),
                this.searchPattern(repoPath, 'architecture'),
                this.searchPattern(repoPath, 'error_handling'),
                this.searchPattern(repoPath, 'testing'),
                this.searchPattern(repoPath, 'documentation'),
                this.searchPattern(repoPath, 'security')
            ]);

            const [performance, architecture, errorHandling, testing, documentation, security] = patterns;

            this.displayQualityAnalysis({
                performance,
                architecture,
                errorHandling,
                testing,
                documentation,
                security
            });
        } catch (error) {
            resultsDiv.innerHTML = `<div class="error">Quality analysis failed: ${error.message}</div>`;
        }
    }

    async searchPattern(repoPath, patternType) {
        try {
            return await this.api.searchSemanticPatterns({
                repository_path: repoPath,
                pattern_type: patternType,
                min_confidence: 0.6,
                limit: 20,
                since_date: '30 days ago'
            });
        } catch (error) {
            console.warn(`Failed to search ${patternType} patterns:`, error);
            return { events: [] };
        }
    }

    displayQualityAnalysis(patterns) {
        const resultsDiv = document.getElementById('quality-results');
        
        const overallScore = this.calculateOverallQualityScore(patterns);
        
        resultsDiv.innerHTML = `
            <div class="quality-analysis-dashboard">
                <h3>Code Quality Analysis</h3>
                
                ${this.renderOverallScore(overallScore)}
                ${this.renderPatternAnalysis('Performance', patterns.performance, 'performance')}
                ${this.renderPatternAnalysis('Architecture', patterns.architecture, 'architecture')}
                ${this.renderPatternAnalysis('Error Handling', patterns.errorHandling, 'error-handling')}
                ${this.renderPatternAnalysis('Testing', patterns.testing, 'testing')}
                ${this.renderPatternAnalysis('Documentation', patterns.documentation, 'documentation')}
                ${this.renderPatternAnalysis('Security', patterns.security, 'security')}
                ${this.renderRecommendations(patterns)}
            </div>
        `;
    }

    renderOverallScore(score) {
        const scoreClass = score >= 80 ? 'excellent' : score >= 60 ? 'good' : score >= 40 ? 'fair' : 'poor';
        
        return `
            <div class="overall-score-section">
                <div class="score-display ${scoreClass}">
                    <div class="score-circle">
                        <span class="score-number">${score}</span>
                        <span class="score-max">/100</span>
                    </div>
                    <div class="score-label">Overall Quality Score</div>
                </div>
                <div class="score-description">
                    ${this.getScoreDescription(score)}
                </div>
            </div>
        `;
    }

    renderPatternAnalysis(title, patternData, cssClass) {
        const events = patternData.events || [];
        const score = this.calculatePatternScore(events);
        const scoreClass = score >= 80 ? 'excellent' : score >= 60 ? 'good' : score >= 40 ? 'fair' : 'poor';

        const recentEvents = events
            .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
            .slice(0, 5);

        const eventsHtml = recentEvents.map(event => `
            <div class="quality-event">
                <div class="event-info">
                    <span class="event-type">${event.event_type}</span>
                    <span class="event-confidence">${(event.confidence * 100).toFixed(1)}%</span>
                </div>
                <div class="event-description">${event.description || 'No description'}</div>
                <div class="event-location">${event.location || 'N/A'}</div>
            </div>
        `).join('');

        return `
            <div class="quality-pattern-section ${cssClass}">
                <div class="pattern-header">
                    <h4>${title}</h4>
                    <div class="pattern-score ${scoreClass}">${score}/100</div>
                </div>
                <div class="pattern-summary">
                    <div class="pattern-stats">
                        <span class="stat">📊 ${events.length} events found</span>
                        <span class="stat">⭐ Avg confidence: ${this.calculateAvgConfidence(events)}%</span>
                    </div>
                </div>
                ${events.length > 0 ? `
                    <div class="pattern-events">
                        <h5>Recent Events</h5>
                        ${eventsHtml}
                    </div>
                ` : '<div class="no-events">No recent events found</div>'}
            </div>
        `;
    }

    renderRecommendations(patterns) {
        const recommendations = this.generateRecommendations(patterns);
        
        const recommendationsHtml = recommendations.map(rec => `
            <div class="recommendation ${rec.priority}">
                <div class="rec-header">
                    <span class="rec-icon">${rec.icon}</span>
                    <span class="rec-title">${rec.title}</span>
                    <span class="rec-priority">${rec.priority}</span>
                </div>
                <div class="rec-description">${rec.description}</div>
            </div>
        `).join('');

        return `
            <div class="recommendations-section">
                <h4>Recommendations</h4>
                <div class="recommendations-list">
                    ${recommendationsHtml}
                </div>
            </div>
        `;
    }

    calculateOverallQualityScore(patterns) {
        const scores = [
            this.calculatePatternScore(patterns.performance.events || []),
            this.calculatePatternScore(patterns.architecture.events || []),
            this.calculatePatternScore(patterns.errorHandling.events || []),
            this.calculatePatternScore(patterns.testing.events || []),
            this.calculatePatternScore(patterns.documentation.events || []),
            this.calculatePatternScore(patterns.security.events || [])
        ];

        return Math.round(scores.reduce((sum, score) => sum + score, 0) / scores.length);
    }

    calculatePatternScore(events) {
        if (events.length === 0) return 30; // Base score for no data
        
        const avgConfidence = events.reduce((sum, event) => sum + (event.confidence || 0), 0) / events.length;
        const eventDensity = Math.min(events.length / 10, 1); // Normalize to max 10 events
        
        return Math.round(30 + (avgConfidence * 40) + (eventDensity * 30));
    }

    calculateAvgConfidence(events) {
        if (events.length === 0) return 0;
        const avg = events.reduce((sum, event) => sum + (event.confidence || 0), 0) / events.length;
        return (avg * 100).toFixed(1);
    }

    getScoreDescription(score) {
        if (score >= 80) return "Excellent code quality with strong patterns across all areas.";
        if (score >= 60) return "Good code quality with room for improvement in some areas.";
        if (score >= 40) return "Fair code quality. Several areas need attention.";
        return "Poor code quality. Significant improvements needed across multiple areas.";
    }

    generateRecommendations(patterns) {
        const recommendations = [];
        
        // Performance recommendations
        const perfEvents = patterns.performance.events || [];
        if (perfEvents.length < 3) {
            recommendations.push({
                icon: '⚡',
                title: 'Improve Performance Monitoring',
                priority: 'medium',
                description: 'Add more performance optimizations and monitoring to identify bottlenecks.'
            });
        }

        // Testing recommendations
        const testEvents = patterns.testing.events || [];
        if (testEvents.length < 5) {
            recommendations.push({
                icon: '🧪',
                title: 'Increase Test Coverage',
                priority: 'high',
                description: 'Add more comprehensive tests to improve code reliability and maintainability.'
            });
        }

        // Documentation recommendations
        const docEvents = patterns.documentation.events || [];
        if (docEvents.length < 3) {
            recommendations.push({
                icon: '📚',
                title: 'Enhance Documentation',
                priority: 'medium',
                description: 'Add more inline documentation and code comments for better maintainability.'
            });
        }

        // Security recommendations
        const secEvents = patterns.security.events || [];
        if (secEvents.length < 2) {
            recommendations.push({
                icon: '🔒',
                title: 'Security Review Needed',
                priority: 'high',
                description: 'Conduct security analysis and implement security best practices.'
            });
        }

        // Error handling recommendations
        const errorEvents = patterns.errorHandling.events || [];
        if (errorEvents.length < 3) {
            recommendations.push({
                icon: '⚠️',
                title: 'Improve Error Handling',
                priority: 'medium',
                description: 'Add more robust error handling and validation throughout the codebase.'
            });
        }

        // If no specific recommendations, add general ones
        if (recommendations.length === 0) {
            recommendations.push({
                icon: '✅',
                title: 'Maintain Current Quality',
                priority: 'low',
                description: 'Continue following current development practices and monitor for regressions.'
            });
        }

        return recommendations.slice(0, 5); // Limit to top 5 recommendations
    }

    updateRepositorySelect(repositories) {
        const select = document.getElementById('quality-repo');
        if (!select) return;
        
        // Clear existing options except the first placeholder
        select.innerHTML = '<option value="">Select a repository...</option>';
        
        // Add repository options
        repositories.forEach(repo => {
            const option = document.createElement('option');
            option.value = repo.path;
            option.textContent = repo.name || repo.path;
            select.appendChild(option);
        });
    }
}

// Export to global scope
window.QualityAnalysis = QualityAnalysis;
