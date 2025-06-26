#!/usr/bin/env python3
"""
SVCS Repository Quality Insights - Git-integrated code quality evolution analysis

This is the repository-local version of svcs_quality.py, designed to work with
the new .svcs/semantic.db architecture while providing enhanced git integration.

Key Changes from Legacy Version:
- Reads from local .svcs/semantic.db instead of global database
- Enhanced with git blame integration for author-quality correlation
- Added branch-aware quality analysis
- Git history quality trend tracking
- Preserved all existing quality analysis logic

Usage:
    python3 svcs_repo_quality.py
    python3 svcs_repo_quality.py --branch main
    python3 svcs_repo_quality.py --author "John Doe"
    python3 svcs_repo_quality.py --since "2024-01-01"
"""

import sys
import os
import subprocess
import argparse
from collections import defaultdict, Counter
from datetime import datetime, timedelta

# Import from centralized API
sys.path.insert(0, '.')
try:
    from svcs.api import get_full_log, get_node_evolution
except ImportError:
    print("❌ Error: Could not import from svcs.api")
    print("   Make sure you're running this from a repository with SVCS initialized")
    print("   Run 'svcs init' first if this is a new repository")
    sys.exit(1)

class RepositoryQualityAnalyzer:
    """Analyzes code quality trends from semantic events with git integration."""
    
    def __init__(self, branch=None, author=None, since=None):
        self.branch = branch
        self.author = author
        self.since = since
        self.events = self._get_filtered_events()
        
        # Enhanced quality indicators with git context
        self.quality_indicators = {
            'positive': [
                'error_handling_introduced',
                'error_handling_pattern_improved',
                'type_annotations_introduced', 
                'functional_programming_adopted',
                'default_parameters_added',
                'decorator_added',
                'assertion_usage_changed',
                'abstract_maintainability_improvement',
                'abstract_readability_improvement',
                'design_pattern_applied',
                'algorithm_optimized'
            ],
            'negative': [
                'error_handling_removed',
                'function_complexity_changed',  # when complexity increases
                'functional_programming_removed',
                'abstract_code_complexity_increase'
            ],
            'refactoring': [
                'node_signature_changed',
                'comprehension_usage_changed',
                'lambda_usage_changed',
                'loop_converted_to_comprehension',
                'abstract_code_simplification'
            ],
            'architectural': [
                'abstract_architecture_change',
                'abstract_design_pattern',
                'abstract_abstraction_improvement'
            ]
        }
    
    def _get_filtered_events(self):
        """Get events filtered by branch, author, and date."""
        events = get_full_log()
        
        # Filter by branch if specified
        if self.branch:
            events = self._filter_by_branch(events, self.branch)
        
        # Filter by author if specified
        if self.author:
            events = [e for e in events if e.get('author', '') == self.author]
        
        # Filter by date if specified
        if self.since:
            try:
                since_date = datetime.fromisoformat(self.since.replace('T', ' '))
                since_timestamp = since_date.timestamp()
                events = [e for e in events if e.get('timestamp', 0) >= since_timestamp]
            except ValueError:
                print(f"⚠️  Warning: Invalid date format '{self.since}', ignoring filter")
        
        return events
    
    def _filter_by_branch(self, events, branch):
        """Filter events by git branch."""
        try:
            # Get commits on the specified branch
            branch_commits = subprocess.run(
                ['git', 'rev-list', branch],
                capture_output=True, text=True, check=True
            ).stdout.strip().split('\n')
            branch_commits = set(commit for commit in branch_commits if commit)
            
            # Filter events to only those on this branch
            filtered_events = []
            for event in events:
                commit_hash = event.get('commit_hash', '')
                if commit_hash and any(commit_hash.startswith(bc) for bc in branch_commits):
                    filtered_events.append(event)
            
            return filtered_events
            
        except subprocess.CalledProcessError:
            print(f"⚠️  Warning: Could not get commits for branch '{branch}', showing all events")
            return events
    
    def get_git_info(self):
        """Get git repository information."""
        try:
            current_branch = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                capture_output=True, text=True, check=True
            ).stdout.strip()
            
            repo_name = subprocess.run(
                ['git', 'rev-parse', '--show-toplevel'],
                capture_output=True, text=True, check=True
            ).stdout.strip().split('/')[-1]
            
            return {'current_branch': current_branch, 'repo_name': repo_name}
        except subprocess.CalledProcessError:
            return {'current_branch': 'unknown', 'repo_name': 'unknown'}
    
    def analyze_quality_trends(self):
        """Analyze overall code quality trends with git integration."""
        
        git_info = self.get_git_info()
        
        print("🏆 REPOSITORY CODE QUALITY EVOLUTION ANALYSIS")
        print("=" * 60)
        print(f"📁 Repository: {git_info['repo_name']}")
        print(f"🌿 Current Branch: {git_info['current_branch']}")
        
        if self.branch:
            print(f"🎯 Analyzing Branch: {self.branch}")
        if self.author:
            print(f"👤 Analyzing Author: {self.author}")
        if self.since:
            print(f"📅 Since: {self.since}")
        
        if not self.events:
            print("\n❌ No semantic events found with current filters.")
            return
        
        # Calculate quality scores
        positive_events = [e for e in self.events if e['event_type'] in self.quality_indicators['positive']]
        negative_events = [e for e in self.events if e['event_type'] in self.quality_indicators['negative']]
        refactoring_events = [e for e in self.events if e['event_type'] in self.quality_indicators['refactoring']]
        architectural_events = [e for e in self.events if e['event_type'] in self.quality_indicators['architectural']]
        
        total_quality_events = len(positive_events) + len(negative_events) + len(refactoring_events)
        
        print(f"\n📊 QUALITY METRICS SUMMARY")
        print(f"   Total Events Analyzed: {len(self.events)}")
        print(f"   Quality-Related Events: {total_quality_events}")
        
        if total_quality_events > 0:
            quality_score = (len(positive_events) + len(refactoring_events) - len(negative_events)) / total_quality_events * 100
            print(f"   Overall Quality Score: {quality_score:.1f}%")
        
        print(f"\n🎯 QUALITY EVENT BREAKDOWN")
        print(f"   ✅ Positive Improvements: {len(positive_events)}")
        print(f"   ⚠️  Potential Regressions: {len(negative_events)}")
        print(f"   🔄 Refactoring Activities: {len(refactoring_events)}")
        print(f"   🏗️  Architectural Changes: {len(architectural_events)}")
        
        # Quality trends over time
        self.analyze_quality_trends_over_time()
        
        # Author quality contributions (git integration)
        self.analyze_author_quality_contributions()
        
        # File-level quality analysis
        self.analyze_file_quality_patterns()
        
        # Git-enhanced quality insights
        self.analyze_git_quality_correlation()
    
    def analyze_quality_trends_over_time(self):
        """Analyze how quality has evolved over time."""
        print(f"\n📈 QUALITY EVOLUTION OVER TIME")
        
        # Group events by month
        monthly_quality = defaultdict(lambda: {'positive': 0, 'negative': 0, 'refactoring': 0})
        
        for event in self.events:
            timestamp = event.get('timestamp', 0)
            if timestamp:
                month = datetime.fromtimestamp(timestamp).strftime('%Y-%m')
                event_type = event['event_type']
                
                if event_type in self.quality_indicators['positive']:
                    monthly_quality[month]['positive'] += 1
                elif event_type in self.quality_indicators['negative']:
                    monthly_quality[month]['negative'] += 1
                elif event_type in self.quality_indicators['refactoring']:
                    monthly_quality[month]['refactoring'] += 1
        
        if not monthly_quality:
            print("   No temporal data available")
            return
        
        # Show recent months
        sorted_months = sorted(monthly_quality.keys())[-6:]  # Last 6 months
        
        for month in sorted_months:
            data = monthly_quality[month]
            total = data['positive'] + data['negative'] + data['refactoring']
            if total > 0:
                score = (data['positive'] + data['refactoring'] - data['negative']) / total * 100
                print(f"   {month}: {score:>5.1f}% quality score ({total} events)")
    
    def analyze_author_quality_contributions(self):
        """Analyze quality contributions by author using git integration."""
        print(f"\n👥 AUTHOR QUALITY CONTRIBUTIONS")
        
        author_quality = defaultdict(lambda: {'positive': 0, 'negative': 0, 'refactoring': 0})
        
        for event in self.events:
            author = event.get('author', 'Unknown')
            event_type = event['event_type']
            
            if event_type in self.quality_indicators['positive']:
                author_quality[author]['positive'] += 1
            elif event_type in self.quality_indicators['negative']:
                author_quality[author]['negative'] += 1
            elif event_type in self.quality_indicators['refactoring']:
                author_quality[author]['refactoring'] += 1
        
        # Calculate quality scores for each author
        for author, data in author_quality.items():
            total = data['positive'] + data['negative'] + data['refactoring']
            if total > 0:
                score = (data['positive'] + data['refactoring'] - data['negative']) / total * 100
                print(f"   {author:<20} {score:>5.1f}% quality score ({total} events)")
    
    def analyze_file_quality_patterns(self):
        """Analyze quality patterns by file."""
        print(f"\n📁 FILE QUALITY ANALYSIS")
        
        file_quality = defaultdict(lambda: {'positive': 0, 'negative': 0, 'refactoring': 0})
        
        for event in self.events:
            file_path = event.get('location', 'Unknown')
            event_type = event['event_type']
            
            if event_type in self.quality_indicators['positive']:
                file_quality[file_path]['positive'] += 1
            elif event_type in self.quality_indicators['negative']:
                file_quality[file_path]['negative'] += 1
            elif event_type in self.quality_indicators['refactoring']:
                file_quality[file_path]['refactoring'] += 1
        
        # Show files with most quality activity
        file_scores = []
        for file_path, data in file_quality.items():
            total = data['positive'] + data['negative'] + data['refactoring']
            if total > 0:
                score = (data['positive'] + data['refactoring'] - data['negative']) / total * 100
                file_scores.append((score, total, file_path))
        
        file_scores.sort(key=lambda x: x[1], reverse=True)  # Sort by total activity
        
        for score, total, file_path in file_scores[:8]:  # Top 8 files
            file_name = file_path.split('/')[-1]
            print(f"   {file_name:<25} {score:>5.1f}% quality score ({total} events)")
    
    def analyze_git_quality_correlation(self):
        """Analyze correlation between git activities and quality changes."""
        print(f"\n🔗 GIT-QUALITY CORRELATION ANALYSIS")
        
        # Group events by commit
        commit_quality = defaultdict(lambda: {'positive': 0, 'negative': 0, 'refactoring': 0})
        
        for event in self.events:
            commit_hash = event.get('commit_hash', 'unknown')
            event_type = event['event_type']
            
            if event_type in self.quality_indicators['positive']:
                commit_quality[commit_hash]['positive'] += 1
            elif event_type in self.quality_indicators['negative']:
                commit_quality[commit_hash]['negative'] += 1
            elif event_type in self.quality_indicators['refactoring']:
                commit_quality[commit_hash]['refactoring'] += 1
        
        # Find commits with significant quality impact
        significant_commits = []
        for commit_hash, data in commit_quality.items():
            total = data['positive'] + data['negative'] + data['refactoring']
            if total >= 3:  # Minimum 3 quality events
                score = (data['positive'] + data['refactoring'] - data['negative'])
                significant_commits.append((score, total, commit_hash))
        
        significant_commits.sort(reverse=True)  # Best quality impact first
        
        print(f"   Commits with Significant Quality Impact:")
        for score, total, commit_hash in significant_commits[:5]:
            try:
                # Get commit message
                commit_msg = subprocess.run(
                    ['git', 'show', '--format=%s', '--no-patch', commit_hash],
                    capture_output=True, text=True, check=True
                ).stdout.strip()
                
                direction = "📈" if score > 0 else "📉" if score < 0 else "➡️"
                print(f"   {direction} {commit_hash[:8]}: {commit_msg[:50]}...")
                print(f"      Quality Impact: {score:+} ({total} events)")
                
            except subprocess.CalledProcessError:
                print(f"   {commit_hash[:8]}: Quality Impact {score:+} ({total} events)")
    
    def generate_quality_report(self):
        """Generate a comprehensive quality report."""
        self.analyze_quality_trends()
        
        # Additional quality insights
        self.analyze_error_handling_patterns()
        self.analyze_modern_practices_adoption()
        self.provide_quality_recommendations()
    
    def analyze_error_handling_patterns(self):
        """Analyze error handling improvement patterns."""
        print(f"\n🛡️  ERROR HANDLING ANALYSIS")
        
        error_events = [
            e for e in self.events 
            if 'error' in e['event_type'].lower() or 'exception' in e['event_type'].lower()
        ]
        
        if not error_events:
            print("   No error handling events found")
            return
        
        error_types = Counter(e['event_type'] for e in error_events)
        print(f"   Total Error Handling Events: {len(error_events)}")
        
        for event_type, count in error_types.most_common():
            print(f"   {event_type}: {count} events")
    
    def analyze_modern_practices_adoption(self):
        """Analyze adoption of modern coding practices."""
        print(f"\n🚀 MODERN PRACTICES ADOPTION")
        
        modern_practices = {
            'Type Annotations': ['type_annotations_introduced'],
            'Functional Programming': ['functional_programming_adopted'],
            'Decorators': ['decorator_added'],
            'Comprehensions': ['comprehension_usage_changed', 'loop_converted_to_comprehension'],
            'Design Patterns': ['design_pattern_applied', 'abstract_design_pattern']
        }
        
        for practice, event_types in modern_practices.items():
            count = sum(1 for event in self.events if event['event_type'] in event_types)
            if count > 0:
                print(f"   {practice}: {count} adoptions")
    
    def provide_quality_recommendations(self):
        """Provide quality improvement recommendations based on analysis."""
        print(f"\n💡 QUALITY IMPROVEMENT RECOMMENDATIONS")
        
        positive_events = [e for e in self.events if e['event_type'] in self.quality_indicators['positive']]
        negative_events = [e for e in self.events if e['event_type'] in self.quality_indicators['negative']]
        
        # Calculate ratios for recommendations
        error_handling_events = sum(1 for e in self.events if 'error' in e['event_type'].lower())
        type_annotation_events = sum(1 for e in self.events if 'type_annotations' in e['event_type'])
        
        recommendations = []
        
        if len(negative_events) > len(positive_events):
            recommendations.append("🔍 Focus on code quality: More regressions than improvements detected")
        
        if error_handling_events < len(self.events) * 0.1:
            recommendations.append("🛡️  Consider improving error handling coverage")
        
        if type_annotation_events < len(self.events) * 0.05:
            recommendations.append("📝 Consider adding more type annotations for better code clarity")
        
        if not recommendations:
            recommendations.append("✅ Code quality trends look positive!")
        
        for rec in recommendations:
            print(f"   {rec}")

def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(description='SVCS Repository Quality Analysis')
    parser.add_argument('--branch', help='Analyze specific git branch')
    parser.add_argument('--author', help='Analyze specific author')
    parser.add_argument('--since', help='Analyze events since date (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    try:
        analyzer = RepositoryQualityAnalyzer(
            branch=args.branch,
            author=args.author,
            since=args.since
        )
        analyzer.generate_quality_report()
        
    except Exception as e:
        print(f"❌ Error generating quality analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
