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
            // Use the actual quality analysis endpoint
            const qualityData = await this.api.analyzeQuality(repoPath);
            console.log('Quality analysis data:', qualityData);

            this.displayQualityAnalysis(qualityData.quality_metrics);
        } catch (error) {
            console.error('Quality analysis error:', error);
            resultsDiv.innerHTML = `<div class="error">Quality analysis failed: ${error.message}</div>`;
        }
    }

    // Quality analysis methods removed - using backend quality analysis instead

    displayQualityAnalysis(qualityMetrics) {
        const resultsDiv = document.getElementById('quality-results');
        
        const overallScore = Math.round(qualityMetrics.quality_score * 100);
        
        resultsDiv.innerHTML = `
            <div class="quality-analysis-dashboard">
                <h3>Code Quality Analysis</h3>
                
                ${this.renderOverallScore(overallScore)}
                ${this.renderQualityMetrics(qualityMetrics)}
                ${this.renderQualityInsights(qualityMetrics)}
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

    renderQualityMetrics(metrics) {
        return `
            <div class="quality-metrics-section">
                <h4>Quality Metrics</h4>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-number">${metrics.total_events}</div>
                        <div class="metric-label">Total Events</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-number">${metrics.performance_events}</div>
                        <div class="metric-label">Performance Events</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-number">${metrics.refactoring_events}</div>
                        <div class="metric-label">Refactoring Events</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-number">${metrics.error_handling_events}</div>
                        <div class="metric-label">Error Handling</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-number">${metrics.complexity_events}</div>
                        <div class="metric-label">Complexity Events</div>
                    </div>
                </div>
            </div>
        `;
    }

    renderQualityInsights(metrics) {
        const insights = [];
        
        if (metrics.performance_events > 0) {
            insights.push(`✅ Found ${metrics.performance_events} performance-related improvements`);
        }
        
        if (metrics.refactoring_events > 0) {
            insights.push(`🔄 Detected ${metrics.refactoring_events} refactoring activities`);
        }
        
        if (metrics.error_handling_events > 0) {
            insights.push(`🛡️ Found ${metrics.error_handling_events} error handling improvements`);
        }
        
        if (metrics.complexity_events > 0) {
            insights.push(`⚠️ Identified ${metrics.complexity_events} complexity-related events`);
        }
        
        if (metrics.total_events === 0) {
            insights.push(`ℹ️ No semantic events found - consider analyzing more code activity`);
        }
        
        const insightsHtml = insights.map(insight => 
            `<div class="quality-insight">${insight}</div>`
        ).join('');
        
        const recommendations = this.generateRecommendations(metrics);
        
        return `
            <div class="quality-insights-section">
                <h4>Quality Insights</h4>
                <div class="insights-list">
                    ${insightsHtml}
                </div>
                
                <h4>Recommendations</h4>
                <div class="recommendations-list">
                    ${recommendations}
                </div>
            </div>
        `;
    }

    generateRecommendations(metrics) {
        const recommendations = [];
        
        if (metrics.performance_events === 0) {
            recommendations.push(`🚀 Consider adding performance monitoring and optimization`);
        }
        
        if (metrics.error_handling_events === 0) {
            recommendations.push(`🛡️ Improve error handling and exception management`);
        }
        
        if (metrics.refactoring_events === 0) {
            recommendations.push(`🔄 Regular refactoring can improve code maintainability`);
        }
        
        if (metrics.quality_score < 0.5) {
            recommendations.push(`📈 Focus on code quality improvements and best practices`);
        }
        
        if (recommendations.length === 0) {
            recommendations.push(`✨ Code quality looks good! Keep up the excellent work.`);
        }
        
        return recommendations.map(rec => 
            `<div class="quality-recommendation">${rec}</div>`
        ).join('');
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

    async updateRepositorySelect(repositories) {
        const select = document.getElementById('quality-repo');
        if (!select) return;
        
        // Clear existing options except the first placeholder
        select.innerHTML = '<option value="">Select a repository...</option>';
        
        // Add repository options with current branch info
        for (const repo of repositories) {
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
            select.appendChild(option);
        }
    }
}

// Export to global scope
window.QualityAnalysis = QualityAnalysis;
