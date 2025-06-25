// Analytics Component
class Analytics {
    constructor(apiClient, utils) {
        this.api = apiClient;
        this.utils = utils;
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        const generateBtn = document.getElementById('generate-analytics');
        if (generateBtn) {
            generateBtn.addEventListener('click', () => this.generateAnalytics());
        }
    }

    async generateAnalytics() {
        const repoPath = document.getElementById('analytics-repo').value;
        
        if (!repoPath) {
            alert('Please select a repository for analytics');
            return;
        }

        const resultsDiv = document.getElementById('analytics-results');
        resultsDiv.style.display = 'block';
        resultsDiv.innerHTML = '<div class="loading">Generating analytics...</div>';

        try {
            // Generate analytics (this includes project statistics)
            console.log('Calling analytics API for:', repoPath);
            const analyticsData = await this.api.generateAnalytics(repoPath);
            console.log('Analytics data received:', analyticsData);

            // Get recent activity for trends
            console.log('Calling recent activity API for:', repoPath);
            const recentActivity = await this.api.getRecentActivity(repoPath, 30, 100);
            console.log('Recent activity received:', recentActivity);

            this.displayAnalytics(analyticsData.analytics, recentActivity);
        } catch (error) {
            console.error('Analytics error:', error);
            resultsDiv.innerHTML = `<div class="error">Analytics generation failed: ${error.message}</div>`;
        }
    }

    displayAnalytics(stats, recentActivity) {
        const resultsDiv = document.getElementById('analytics-results');
        
        // Process recent activity for trends
        const activityTrends = this.processActivityTrends(recentActivity.events || []);
        const authorStats = this.processAuthorStats(recentActivity.events || []);
        
        // Use the event type counts from analytics data directly
        const eventTypeStats = this.processEventTypeStatsFromAnalytics(stats.event_types || {});

        resultsDiv.innerHTML = `
            <div class="analytics-dashboard">
                <h3>Project Analytics</h3>
                
                ${this.renderOverviewStats(stats)}
                ${this.renderActivityTrends(activityTrends)}
                ${this.renderAuthorStats(authorStats)}
                ${this.renderEventTypeDistribution(eventTypeStats)}
                ${this.renderQualityMetrics(stats)}
            </div>
        `;
    }

    renderOverviewStats(stats) {
        // Calculate derived statistics from available data
        const eventTypesCount = stats.event_types ? Object.keys(stats.event_types).length : 0;
        const topFilesCount = stats.top_files ? Object.keys(stats.top_files).length : 0;
        
        return `
            <div class="analytics-section">
                <h4>Overview Statistics</h4>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">${stats.total_events || 0}</div>
                        <div class="stat-label">Total Events</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${eventTypesCount}</div>
                        <div class="stat-label">Event Types</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${topFilesCount}</div>
                        <div class="stat-label">Active Files</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${stats.patterns ? stats.patterns.length : 0}</div>
                        <div class="stat-label">Patterns</div>
                    </div>
                </div>
            </div>
        `;
    }

    renderActivityTrends(trends) {
        const trendHtml = trends.map(trend => `
            <div class="trend-item">
                <span class="trend-date">${trend.date}</span>
                <div class="trend-bar">
                    <div class="trend-fill" style="width: ${trend.percentage}%"></div>
                </div>
                <span class="trend-count">${trend.count}</span>
            </div>
        `).join('');

        return `
            <div class="analytics-section">
                <h4>Activity Trends (Last 30 Days)</h4>
                <div class="trends-chart">
                    ${trendHtml}
                </div>
            </div>
        `;
    }

    renderAuthorStats(authorStats) {
        const sortedAuthors = Object.entries(authorStats)
            .sort(([,a], [,b]) => b.count - a.count)
            .slice(0, 10);

        const authorHtml = sortedAuthors.map(([author, data]) => `
            <div class="author-stat">
                <span class="author-name">${author}</span>
                <div class="author-bar">
                    <div class="author-fill" style="width: ${data.percentage}%"></div>
                </div>
                <span class="author-count">${data.count} events</span>
            </div>
        `).join('');

        return `
            <div class="analytics-section">
                <h4>Top Contributors</h4>
                <div class="authors-chart">
                    ${authorHtml}
                </div>
            </div>
        `;
    }

    renderEventTypeDistribution(eventStats) {
        const sortedEvents = Object.entries(eventStats)
            .sort(([,a], [,b]) => b.count - a.count);

        const eventHtml = sortedEvents.map(([eventType, data]) => `
            <div class="event-stat">
                <span class="event-type">${eventType}</span>
                <div class="event-bar">
                    <div class="event-fill" style="width: ${data.percentage}%"></div>
                </div>
                <span class="event-count">${data.count}</span>
            </div>
        `).join('');

        return `
            <div class="analytics-section">
                <h4>Event Type Distribution</h4>
                <div class="events-chart">
                    ${eventHtml}
                </div>
            </div>
        `;
    }

    renderQualityMetrics(stats) {
        const qualityScore = this.calculateQualityScore(stats);
        
        return `
            <div class="analytics-section">
                <h4>Code Quality Indicators</h4>
                <div class="quality-metrics">
                    <div class="quality-score">
                        <div class="score-circle">
                            <span class="score-number">${qualityScore}</span>
                            <span class="score-label">Quality Score</span>
                        </div>
                    </div>
                    <div class="quality-details">
                        <div class="quality-item">
                            <span class="quality-metric">Test Coverage Events</span>
                            <span class="quality-value">${stats.test_events || 0}</span>
                        </div>
                        <div class="quality-item">
                            <span class="quality-metric">Refactoring Events</span>
                            <span class="quality-value">${stats.refactoring_events || 0}</span>
                        </div>
                        <div class="quality-item">
                            <span class="quality-metric">Bug Fix Events</span>
                            <span class="quality-value">${stats.bug_fix_events || 0}</span>
                        </div>
                        <div class="quality-item">
                            <span class="quality-metric">Documentation Events</span>
                            <span class="quality-value">${stats.documentation_events || 0}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    processActivityTrends(events) {
        const dailyCounts = {};
        const maxCount = 30; // Last 30 days
        
        // Initialize last 30 days
        for (let i = 0; i < maxCount; i++) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            const dateStr = date.toISOString().split('T')[0];
            dailyCounts[dateStr] = 0;
        }

        // Count events by day
        events.forEach(event => {
            // Use created_at (Unix timestamp in seconds) and convert to milliseconds
            const timestamp = event.created_at || event.commit_timestamp;
            if (timestamp) {
                const date = new Date(timestamp * 1000).toISOString().split('T')[0];
                if (dailyCounts.hasOwnProperty(date)) {
                    dailyCounts[date]++;
                }
            }
        });

        const maxEvents = Math.max(...Object.values(dailyCounts), 1);
        
        return Object.entries(dailyCounts)
            .sort(([a], [b]) => new Date(a) - new Date(b))
            .map(([date, count]) => ({
                date: new Date(date).toLocaleDateString(),
                count,
                percentage: (count / maxEvents) * 100
            }));
    }

    processAuthorStats(events) {
        const authorCounts = {};
        
        events.forEach(event => {
            if (event.author) {
                authorCounts[event.author] = (authorCounts[event.author] || 0) + 1;
            }
        });

        const maxCount = Math.max(...Object.values(authorCounts), 1);
        
        Object.keys(authorCounts).forEach(author => {
            authorCounts[author] = {
                count: authorCounts[author],
                percentage: (authorCounts[author] / maxCount) * 100
            };
        });

        return authorCounts;
    }

    processEventTypeStats(events) {
        const eventCounts = {};
        
        events.forEach(event => {
            eventCounts[event.event_type] = (eventCounts[event.event_type] || 0) + 1;
        });

        const maxCount = Math.max(...Object.values(eventCounts), 1);
        
        Object.keys(eventCounts).forEach(eventType => {
            eventCounts[eventType] = {
                count: eventCounts[eventType],
                percentage: (eventCounts[eventType] / maxCount) * 100
            };
        });

        return eventCounts;
    }

    processEventTypeStatsFromAnalytics(eventTypeCounts) {
        const maxCount = Math.max(...Object.values(eventTypeCounts), 1);
        const eventTypeStats = {};
        
        Object.entries(eventTypeCounts).forEach(([eventType, count]) => {
            eventTypeStats[eventType] = {
                count: count,
                percentage: (count / maxCount) * 100
            };
        });

        return eventTypeStats;
    }

    calculateQualityScore(stats) {
        // Simple quality score calculation based on available metrics
        let score = 70; // Base score
        
        if (stats.test_events > 10) score += 10;
        if (stats.refactoring_events > 5) score += 10;
        if (stats.documentation_events > 5) score += 5;
        if (stats.bug_fix_events < stats.total_events * 0.1) score += 5;
        
        return Math.min(score, 100);
    }

    async updateRepositorySelect(repositories) {
        const select = document.getElementById('analytics-repo');
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
window.Analytics = Analytics;
