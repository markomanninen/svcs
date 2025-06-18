#!/usr/bin/env python3
"""
SVCS Quality Insights - AI-powered code quality evolution analysis
"""

import sys
import os
from collections import defaultdict, Counter
from datetime import datetime, timedelta

sys.path.insert(0, '.svcs')
from api import get_full_log, get_node_evolution

class CodeQualityAnalyzer:
    """Analyzes code quality trends from semantic events."""
    
    def __init__(self):
        self.events = get_full_log()
        self.quality_indicators = {
            'positive': [
                'error_handling_introduced',
                'type_annotations_introduced', 
                'functional_programming_adopted',
                'default_parameters_added',
                'decorator_added',
                'assertion_usage_changed'  # when assertions increase
            ],
            'negative': [
                'error_handling_removed',
                'function_complexity_changed',  # when complexity increases
                'functional_programming_removed'
            ],
            'refactoring': [
                'node_signature_changed',
                'comprehension_usage_changed',
                'lambda_usage_changed'
            ]
        }
    
    def analyze_quality_trends(self):
        """Analyze overall code quality trends."""
        
        print("🏆 CODE QUALITY EVOLUTION ANALYSIS")
        print("=" * 50)
        
        # Calculate quality scores
        positive_events = [e for e in self.events if e['event_type'] in self.quality_indicators['positive']]
        negative_events = [e for e in self.events if e['event_type'] in self.quality_indicators['negative']]
        refactoring_events = [e for e in self.events if e['event_type'] in self.quality_indicators['refactoring']]
        
        # Complexity analysis
        complexity_events = [e for e in self.events if 'complexity' in e['event_type']]
        complexity_increases = [e for e in complexity_events if 'increased' in e.get('details', '')]
        complexity_decreases = [e for e in complexity_events if 'decreased' in e.get('details', '')]
        
        print(f"\n📈 QUALITY METRICS")
        print(f"   Positive Changes: {len(positive_events)} events")
        print(f"   Negative Changes: {len(negative_events)} events")
        print(f"   Refactoring Events: {len(refactoring_events)} events")
        print(f"   Complexity Increases: {len(complexity_increases)} events")
        print(f"   Complexity Decreases: {len(complexity_decreases)} events")
        
        # Quality score calculation
        quality_score = len(positive_events) - len(negative_events) - len(complexity_increases)
        
        print(f"\n🎯 OVERALL QUALITY SCORE: {quality_score}")
        if quality_score > 0:
            print("   📈 Code quality is improving!")
        elif quality_score < 0:
            print("   📉 Code quality may need attention")
        else:
            print("   ➡️  Code quality is stable")
        
        self.analyze_error_handling_evolution()
        self.analyze_modernization_trends()
        self.identify_quality_hotspots()
        self.provide_quality_recommendations()
    
    def analyze_error_handling_evolution(self):
        """Analyze how error handling has evolved."""
        
        print(f"\n🛡️  ERROR HANDLING EVOLUTION")
        
        error_events = [e for e in self.events if 'error' in e['event_type'] or 'exception' in e['event_type']]
        
        introduced = [e for e in error_events if 'introduced' in e['event_type'] or 'added' in e['event_type']]
        removed = [e for e in error_events if 'removed' in e['event_type']]
        
        print(f"   Error Handling Added: {len(introduced)} events")
        print(f"   Error Handling Removed: {len(removed)} events")
        
        if introduced:
            print("   Recent Error Handling Improvements:")
            for event in introduced[-3:]:  # Show last 3
                print(f"     • {event['node_id']} in {event['location']}")
    
    def analyze_modernization_trends(self):
        """Analyze adoption of modern Python features."""
        
        print(f"\n🚀 MODERNIZATION TRENDS")
        
        modern_features = {
            'Type Annotations': ['type_annotations'],
            'Async Programming': ['async', 'await'],
            'Functional Programming': ['functional_programming', 'lambda', 'comprehension'],
            'Decorators': ['decorator'],
            'Advanced Patterns': ['starred_expression', 'slice_usage']
        }
        
        for feature, keywords in modern_features.items():
            count = sum(1 for e in self.events if any(kw in e['event_type'] for kw in keywords))
            if count > 0:
                trend = "🔥" if count >= 3 else "📈" if count >= 1 else "➡️"
                print(f"   {trend} {feature}: {count} adoption events")
    
    def identify_quality_hotspots(self):
        """Identify files with quality concerns."""
        
        print(f"\n🔥 QUALITY HOTSPOTS")
        
        # Files with high complexity increases
        complexity_by_file = defaultdict(int)
        for event in self.events:
            if 'complexity' in event['event_type'] and 'increased' in event.get('details', ''):
                complexity_by_file[event['location']] += 1
        
        if complexity_by_file:
            print("   Files with Complexity Increases:")
            for filepath, count in sorted(complexity_by_file.items(), key=lambda x: x[1], reverse=True):
                print(f"     • {filepath}: {count} increases")
        
        # Files with most changes (potential refactoring candidates)
        file_activity = Counter(e['location'] for e in self.events)
        high_activity_files = [(f, c) for f, c in file_activity.most_common(3) if c > 10]
        
        if high_activity_files:
            print("   High Activity Files (may need refactoring):")
            for filepath, count in high_activity_files:
                print(f"     • {filepath}: {count} changes")
    
    def provide_quality_recommendations(self):
        """Provide actionable quality improvement recommendations."""
        
        print(f"\n💡 QUALITY RECOMMENDATIONS")
        
        recommendations = []
        
        # Check for missing error handling
        functions_without_error_handling = set()
        for event in self.events:
            if event['event_type'] == 'node_added' and 'func:' in event['node_id']:
                # Check if this function has error handling events
                func_error_events = [e for e in self.events 
                                   if e['node_id'] == event['node_id'] 
                                   and ('error' in e['event_type'] or 'exception' in e['event_type'])]
                if not func_error_events:
                    functions_without_error_handling.add(event['node_id'])
        
        if functions_without_error_handling:
            recommendations.append(f"Consider adding error handling to {len(functions_without_error_handling)} functions")
        
        # Check for complexity increases without refactoring
        high_complexity_functions = set()
        for event in self.events:
            if 'complexity' in event['event_type'] and 'increased' in event.get('details', ''):
                high_complexity_functions.add(event['node_id'])
        
        if high_complexity_functions:
            recommendations.append(f"Consider refactoring {len(high_complexity_functions)} functions with complexity increases")
        
        # Check for modernization opportunities
        old_patterns = [e for e in self.events if e['event_type'] in ['node_added', 'node_signature_changed']]
        modern_patterns = [e for e in self.events if 'type_annotations' in e['event_type'] or 'functional_programming' in e['event_type']]
        
        if len(old_patterns) > len(modern_patterns) * 3:
            recommendations.append("Consider adopting more modern Python patterns (type hints, functional programming)")
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        else:
            print("   ✅ No immediate quality concerns detected!")

def generate_quality_report():
    """Generate a comprehensive quality report."""
    
    analyzer = CodeQualityAnalyzer()
    analyzer.analyze_quality_trends()
    
    # Save quality report
    with open('svcs_quality_report.txt', 'w') as f:
        f.write(f"SVCS Quality Report - Generated: {datetime.now().isoformat()}\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Total Events Analyzed: {len(analyzer.events)}\n")
        f.write(f"Quality Indicators Tracked: {len(analyzer.quality_indicators)}\n")
        # Add more detailed analysis to file
    
    print(f"\n💾 Quality report saved to: svcs_quality_report.txt")

if __name__ == "__main__":
    try:
        generate_quality_report()
    except Exception as e:
        print(f"Error generating quality analysis: {e}")
        import traceback
        traceback.print_exc()
