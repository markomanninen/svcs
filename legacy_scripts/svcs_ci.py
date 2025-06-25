#!/usr/bin/env python3
"""
SVCS CI/CD Integration - Continuous semantic analysis for development workflows
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from typing import Dict, List, Any

sys.path.insert(0, '.svcs')
from api import get_full_log, get_commit_details

class SVCSCIIntegration:
    """CI/CD integration for SVCS semantic analysis."""
    
    def __init__(self):
        self.quality_thresholds = {
            'max_complexity_increases': 3,
            'min_error_handling_ratio': 0.7,
            'max_function_count_without_tests': 5,
            'max_files_without_documentation': 2
        }
        
    def run_pr_analysis(self, target_branch: str = "main") -> Dict[str, Any]:
        """Run semantic analysis for a pull request."""
        
        print("🔍 SVCS Pull Request Analysis")
        print("=" * 40)
        
        # Get commits in the PR
        try:
            # Get commits between target branch and current HEAD
            cmd = ["git", "rev-list", f"{target_branch}..HEAD", "--reverse"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            pr_commits = result.stdout.strip().split('\n') if result.stdout.strip() else []
        except subprocess.CalledProcessError:
            print("❌ Could not get PR commits")
            return {"status": "error", "message": "Could not analyze PR commits"}
        
        if not pr_commits:
            print("ℹ️  No new commits found")
            return {"status": "success", "message": "No changes to analyze"}
        
        print(f"📊 Analyzing {len(pr_commits)} commits...")
        
        # Analyze each commit
        pr_analysis = {
            "commits_analyzed": len(pr_commits),
            "total_events": 0,
            "quality_score": 0,
            "concerns": [],
            "improvements": [],
            "recommendations": [],
            "event_summary": {},
            "files_changed": set()
        }
        
        for commit_hash in pr_commits:
            events = get_commit_details(commit_hash)
            pr_analysis["total_events"] += len(events)
            
            for event in events:
                pr_analysis["files_changed"].add(event["location"])
                event_type = event["event_type"]
                pr_analysis["event_summary"][event_type] = pr_analysis["event_summary"].get(event_type, 0) + 1
        
        pr_analysis["files_changed"] = list(pr_analysis["files_changed"])
        
        # Quality assessment
        self.assess_pr_quality(pr_analysis)
        
        # Generate report
        self.generate_pr_report(pr_analysis)
        
        return pr_analysis
    
    def assess_pr_quality(self, analysis: Dict[str, Any]):
        """Assess the quality impact of the PR."""
        
        event_summary = analysis["event_summary"]
        
        # Positive indicators
        positive_events = [
            'error_handling_introduced',
            'type_annotations_introduced',
            'functional_programming_adopted',
            'default_parameters_added',
            'assertion_usage_changed'
        ]
        
        # Negative indicators
        negative_events = [
            'error_handling_removed',
            'function_complexity_changed'  # if complexity increased
        ]
        
        positive_score = sum(event_summary.get(event, 0) for event in positive_events)
        negative_score = sum(event_summary.get(event, 0) for event in negative_events)
        
        analysis["quality_score"] = positive_score - negative_score
        
        # Specific concerns
        if event_summary.get('function_complexity_changed', 0) > self.quality_thresholds['max_complexity_increases']:
            analysis["concerns"].append(f"High number of complexity increases: {event_summary.get('function_complexity_changed')}")
        
        if event_summary.get('error_handling_removed', 0) > 0:
            analysis["concerns"].append(f"Error handling removed in {event_summary.get('error_handling_removed')} places")
        
        # Improvements
        if event_summary.get('error_handling_introduced', 0) > 0:
            analysis["improvements"].append(f"Error handling added to {event_summary.get('error_handling_introduced')} functions")
        
        if event_summary.get('type_annotations_introduced', 0) > 0:
            analysis["improvements"].append("Type annotations introduced")
        
        if event_summary.get('functional_programming_adopted', 0) > 0:
            analysis["improvements"].append("Functional programming patterns adopted")
        
        # Recommendations
        new_functions = event_summary.get('node_added', 0)
        error_handling_events = event_summary.get('error_handling_introduced', 0)
        
        if new_functions > 0 and error_handling_events == 0:
            analysis["recommendations"].append("Consider adding error handling to new functions")
        
        if event_summary.get('node_signature_changed', 0) > 0:
            analysis["recommendations"].append("Verify that signature changes maintain backward compatibility")
    
    def generate_pr_report(self, analysis: Dict[str, Any]):
        """Generate a formatted PR report."""
        
        report = f"""
# 🔍 SVCS Semantic Analysis Report

## 📊 Summary
- **Commits Analyzed**: {analysis['commits_analyzed']}
- **Total Semantic Events**: {analysis['total_events']}
- **Files Modified**: {len(analysis['files_changed'])}
- **Quality Score**: {analysis['quality_score']} 

## 🎯 Event Breakdown
"""
        
        for event_type, count in sorted(analysis["event_summary"].items()):
            report += f"- **{event_type}**: {count}\n"
        
        if analysis["improvements"]:
            report += "\n## ✅ Improvements\n"
            for improvement in analysis["improvements"]:
                report += f"- {improvement}\n"
        
        if analysis["concerns"]:
            report += "\n## ⚠️ Concerns\n"
            for concern in analysis["concerns"]:
                report += f"- {concern}\n"
        
        if analysis["recommendations"]:
            report += "\n## 💡 Recommendations\n"
            for rec in analysis["recommendations"]:
                report += f"- {rec}\n"
        
        report += f"\n## 📁 Files Modified\n"
        for filepath in analysis["files_changed"]:
            report += f"- `{filepath}`\n"
        
        report += f"\n---\n*Generated by SVCS at {datetime.now().isoformat()}*\n"
        
        # Save report
        with open('svcs_pr_report.md', 'w') as f:
            f.write(report)
        
        print("📄 PR report saved to: svcs_pr_report.md")
        print(report)
    
    def run_quality_gate(self) -> bool:
        """Run quality gate checks for CI/CD pipeline."""
        
        print("🚪 SVCS Quality Gate Check")
        print("=" * 30)
        
        events = get_full_log()
        
        # Get recent events (last 10 commits)
        recent_commits = set()
        for event in sorted(events, key=lambda x: x['timestamp'], reverse=True):
            recent_commits.add(event['commit_hash'])
            if len(recent_commits) >= 10:
                break
        
        recent_events = [e for e in events if e['commit_hash'] in recent_commits]
        
        # Quality checks
        checks = {
            "complexity_increases": self.check_complexity_increases(recent_events),
            "error_handling_coverage": self.check_error_handling_coverage(recent_events),
            "modernization_progress": self.check_modernization_progress(recent_events)
        }
        
        all_passed = all(checks.values())
        
        print(f"🔍 Complexity Control: {'✅' if checks['complexity_increases'] else '❌'}")
        print(f"🛡️  Error Handling: {'✅' if checks['error_handling_coverage'] else '❌'}")
        print(f"🚀 Modernization: {'✅' if checks['modernization_progress'] else '❌'}")
        
        print(f"\n🏁 Quality Gate: {'✅ PASSED' if all_passed else '❌ FAILED'}")
        
        return all_passed
    
    def check_complexity_increases(self, events: List[Dict[str, Any]]) -> bool:
        """Check if complexity increases are within acceptable limits."""
        complexity_increases = len([e for e in events if 'complexity' in e['event_type'] and 'increased' in e.get('details', '')])
        return complexity_increases <= self.quality_thresholds['max_complexity_increases']
    
    def check_error_handling_coverage(self, events: List[Dict[str, Any]]) -> bool:
        """Check error handling coverage."""
        new_functions = len([e for e in events if e['event_type'] == 'node_added' and 'func:' in e['node_id']])
        error_handling_events = len([e for e in events if 'error_handling' in e['event_type']])
        
        if new_functions == 0:
            return True
        
        ratio = error_handling_events / new_functions
        return ratio >= self.quality_thresholds['min_error_handling_ratio']
    
    def check_modernization_progress(self, events: List[Dict[str, Any]]) -> bool:
        """Check if codebase is adopting modern patterns."""
        modern_events = len([e for e in events if any(pattern in e['event_type'] 
                           for pattern in ['type_annotations', 'functional_programming', 'decorator'])])
        total_events = len(events)
        
        if total_events == 0:
            return True
        
        # At least 10% of events should be modernization-related
        return (modern_events / total_events) >= 0.1
    
    def generate_ci_artifacts(self):
        """Generate artifacts for CI/CD systems."""
        
        events = get_full_log()
        
        # Generate JUnit-style XML for test reporting
        junit_xml = self.generate_junit_xml(events)
        with open('svcs-quality-report.xml', 'w') as f:
            f.write(junit_xml)
        
        # Generate JSON summary for badges/metrics
        summary = {
            "total_events": len(events),
            "quality_score": self.calculate_overall_quality_score(events),
            "last_updated": datetime.now().isoformat(),
            "modernization_percentage": self.calculate_modernization_percentage(events)
        }
        
        with open('svcs-summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print("📊 CI artifacts generated:")
        print("  - svcs-quality-report.xml")
        print("  - svcs-summary.json")
    
    def generate_junit_xml(self, events: List[Dict[str, Any]]) -> str:
        """Generate JUnit-style XML for CI systems."""
        
        quality_passed = self.run_quality_gate()
        
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="SVCS Quality Checks" tests="1" failures="{0 if quality_passed else 1}" time="1.0">
    <testcase name="Quality Gate" classname="SVCS">
        {"" if quality_passed else '<failure message="Quality gate failed">Quality thresholds not met</failure>'}
    </testcase>
</testsuite>'''
    
    def calculate_overall_quality_score(self, events: List[Dict[str, Any]]) -> float:
        """Calculate overall quality score (0-100)."""
        if not events:
            return 100.0
        
        positive_events = len([e for e in events if any(pattern in e['event_type'] 
                             for pattern in ['error_handling_introduced', 'type_annotations', 'functional_programming_adopted'])])
        negative_events = len([e for e in events if any(pattern in e['event_type']
                             for pattern in ['error_handling_removed', 'complexity.*increased'])])
        
        score = 50 + (positive_events - negative_events) * 5
        return max(0, min(100, score))
    
    def calculate_modernization_percentage(self, events: List[Dict[str, Any]]) -> float:
        """Calculate percentage of modern patterns adopted."""
        if not events:
            return 0.0
        
        modern_events = len([e for e in events if any(pattern in e['event_type']
                           for pattern in ['type_annotations', 'functional_programming', 'decorator', 'comprehension'])])
        
        return (modern_events / len(events)) * 100

def main():
    """Main CLI for CI/CD integration."""
    
    if len(sys.argv) < 2:
        print("Usage: python svcs_ci.py [pr-analysis|quality-gate|artifacts]")
        sys.exit(1)
    
    command = sys.argv[1]
    ci = SVCSCIIntegration()
    
    if command == "pr-analysis":
        target_branch = sys.argv[2] if len(sys.argv) > 2 else "main"
        result = ci.run_pr_analysis(target_branch)
        sys.exit(0 if result["status"] == "success" else 1)
    
    elif command == "quality-gate":
        passed = ci.run_quality_gate()
        sys.exit(0 if passed else 1)
    
    elif command == "artifacts":
        ci.generate_ci_artifacts()
        sys.exit(0)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
