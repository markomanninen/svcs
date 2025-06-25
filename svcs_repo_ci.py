#!/usr/bin/env python3
"""
SVCS Repository-Local CI/CD Integration

CI/CD integration that works with the new repository-local architecture:
- Uses repository-local databases (.svcs/semantic.db)
- Integrates with git notes for team collaboration
- Branch-aware semantic analysis
- Repository-specific CI/CD operations
"""

import json
import os
import subprocess
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Import repository-local modules
from svcs_repo_local import RepositoryLocalSVCS


class RepositoryLocalCIIntegration:
    """Repository-local CI/CD integration for SVCS semantic analysis."""
    
    def __init__(self, repo_path: str = None):
        """Initialize with repository path (defaults to current directory)."""
        self.repo_path = Path(repo_path or Path.cwd()).resolve()
        self.svcs = RepositoryLocalSVCS(self.repo_path)
        
        # Quality thresholds for CI/CD gates
        self.quality_thresholds = {
            'max_complexity_increases': 3,
            'min_error_handling_ratio': 0.7,
            'max_function_count_without_tests': 5,
            'max_files_without_documentation': 2
        }
    
    def is_initialized(self) -> bool:
        """Check if SVCS is initialized for this repository."""
        status = self.svcs.get_repository_status()
        return status.get('initialized', False)
    
    def run_pr_analysis(self, target_branch: str = "main") -> Dict[str, Any]:
        """Run semantic analysis for a pull request (repository-local)."""
        
        print("🔍 SVCS Repository-Local PR Analysis")
        print("=" * 40)
        
        if not self.is_initialized():
            return {
                "status": "error",
                "message": "SVCS not initialized in repository. Run 'svcs init' first."
            }
        
        # Check if target branch exists
        try:
            subprocess.run(["git", "rev-parse", "--verify", target_branch], 
                         cwd=self.repo_path, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError:
            # Branch doesn't exist, check available branches
            try:
                result = subprocess.run(["git", "branch", "-a"], 
                                      cwd=self.repo_path, capture_output=True, text=True, check=True)
                available_branches = [b.strip().replace('* ', '').replace('origin/', '') 
                                    for b in result.stdout.split('\n') if b.strip()]
                available_branches = list(set([b for b in available_branches if not b.startswith('remotes/')]))
                
                return {
                    "status": "error", 
                    "message": f"Target branch '{target_branch}' not found. Available branches: {', '.join(available_branches)}"
                }
            except subprocess.CalledProcessError:
                return {"status": "error", "message": f"Could not find target branch '{target_branch}'"}
        
        # Get commits in the PR
        try:
            # Get commits between target branch and current HEAD
            cmd = ["git", "rev-list", f"{target_branch}..HEAD", "--reverse"]
            result = subprocess.run(cmd, cwd=self.repo_path, capture_output=True, text=True, check=True)
            pr_commits = result.stdout.strip().split('\n') if result.stdout.strip() else []
        except subprocess.CalledProcessError:
            print("❌ Could not get PR commits")
            return {"status": "error", "message": "Could not analyze PR commits"}
        
        if not pr_commits:
            print("ℹ️  No new commits found")
            return {"status": "success", "message": "No changes to analyze"}
        
        print(f"📊 Analyzing {len(pr_commits)} commits...")
        
        # Analyze each commit using repository-local data
        pr_analysis = {
            "status": "success",
            "commits_analyzed": len(pr_commits),
            "total_events": 0,
            "quality_score": 0,
            "concerns": [],
            "improvements": [],
            "recommendations": [],
            "event_summary": {},
            "files_changed": set(),
            "branch_name": self.svcs.get_current_branch(),
            "target_branch": target_branch
        }
        
        # Get semantic events for the PR commits
        for commit_hash in pr_commits:
            # Get events for this specific commit from repository-local database
            commit_events = self._get_commit_events(commit_hash)
            pr_analysis["total_events"] += len(commit_events)
            
            for event in commit_events:
                pr_analysis["files_changed"].add(event.get("location", "unknown"))
                event_type = event.get("event_type", "unknown")
                pr_analysis["event_summary"][event_type] = pr_analysis["event_summary"].get(event_type, 0) + 1
        
        pr_analysis["files_changed"] = list(pr_analysis["files_changed"])
        
        # Quality assessment
        self._assess_pr_quality(pr_analysis)
        
        # Generate report
        self._generate_pr_report(pr_analysis)
        
        return pr_analysis
    
    def _get_commit_events(self, commit_hash: str) -> List[Dict[str, Any]]:
        """Get semantic events for a specific commit from repository-local database."""
        try:
            with self.svcs.db.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT event_type, node_id, location, details, layer, 
                           layer_description, confidence, reasoning, impact, created_at
                    FROM semantic_events 
                    WHERE commit_hash = ?
                    ORDER BY created_at
                """, (commit_hash,))
                
                events = []
                for row in cursor.fetchall():
                    events.append({
                        "event_type": row[0],
                        "node_id": row[1],
                        "location": row[2],
                        "details": row[3],
                        "layer": row[4],
                        "layer_description": row[5],
                        "confidence": row[6],
                        "reasoning": row[7],
                        "impact": row[8],
                        "created_at": row[9],
                        "commit_hash": commit_hash
                    })
                
                return events
        except Exception as e:
            print(f"Warning: Could not get events for commit {commit_hash}: {e}")
            return []
    
    def _assess_pr_quality(self, analysis: Dict[str, Any]) -> None:
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
    
    def _generate_pr_report(self, analysis: Dict[str, Any]) -> None:
        """Generate a formatted PR report."""
        
        report = f"""
# 🔍 SVCS Repository-Local Semantic Analysis Report

## 📊 Summary
- **Repository**: {self.repo_path.name}
- **Branch**: {analysis['branch_name']} → {analysis['target_branch']}
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
        
        report += f"\n---\n*Generated by SVCS Repository-Local CI at {datetime.now().isoformat()}*\n"
        
        # Save report
        report_path = self.repo_path / 'svcs_pr_report.md'
        with open(report_path, 'w') as f:
            f.write(report)
        
        print(f"📄 PR report saved to: {report_path}")
        print(report)
    
    def run_quality_gate(self, strict: bool = False, target_branch: str = "main") -> Dict[str, Any]:
        """Run quality gate checks for CI/CD pipeline (repository-local)."""
        
        print("🚪 SVCS Repository-Local Quality Gate Check")
        print(f"   Mode: {'STRICT' if strict else 'NORMAL'}")
        print(f"   Target Branch: {target_branch}")
        print("=" * 40)
        
        if not self.is_initialized():
            return {
                "status": "error",
                "passed": False,
                "message": "SVCS not initialized in repository. Run 'svcs init' first."
            }
        
        # Get current branch
        current_branch = self.svcs.get_current_branch()
        
        # Handle same branch scenario
        if current_branch == target_branch:
            print(f"ℹ️  Current branch ({current_branch}) is same as target branch ({target_branch})")
            print("📊 Analyzing recent commits for quality assessment")
            
            # For same-branch scenario, analyze recent commits (last 10 or last 24 hours)
            try:
                # Get recent commits (last 10 commits)
                cmd = ["git", "log", "--oneline", "-10", "--pretty=format:%H"]
                result = subprocess.run(cmd, cwd=self.repo_path, capture_output=True, text=True, check=True)
                recent_commit_hashes = result.stdout.strip().split('\n') if result.stdout.strip() else []
                
                # Get events from these recent commits
                all_events = self.svcs.get_branch_events(current_branch, limit=1000)
                recent_events = [e for e in all_events if e.get('commit_hash') in recent_commit_hashes]
                
                print(f"🔍 Analyzing last {len(recent_commit_hashes)} commits on {current_branch}")
                print(f"📊 Found {len(recent_events)} semantic events in recent commits")
                
            except subprocess.CalledProcessError:
                # Fallback to time-based recent events
                recent_events = self.svcs.get_branch_events(current_branch, limit=50)
                print(f"⚠️  Using fallback: analyzing {len(recent_events)} recent events")
        
        else:
            # Different branches - get commits since diverging from target branch (like PR analysis)
            try:
                # Check if target branch exists
                subprocess.run(["git", "rev-parse", "--verify", target_branch], 
                             cwd=self.repo_path, capture_output=True, text=True, check=True)
                
                # Get commits between target branch and current HEAD
                cmd = ["git", "rev-list", f"{target_branch}..HEAD", "--reverse"]
                result = subprocess.run(cmd, cwd=self.repo_path, capture_output=True, text=True, check=True)
                commits_since_target = result.stdout.strip().split('\n') if result.stdout.strip() else []
                
                if commits_since_target:
                    # Focus on events from commits since target branch
                    all_events = self.svcs.get_branch_events(current_branch, limit=1000)
                    recent_events = [e for e in all_events if e.get('commit_hash') in commits_since_target]
                    print(f"📊 Analyzing {len(commits_since_target)} commits since {target_branch}")
                    print(f"🔍 Found {len(recent_events)} semantic events in these commits")
                else:
                    # No commits since target branch - analyze recent events
                    recent_events = self.svcs.get_branch_events(current_branch, limit=50)
                    print(f"ℹ️  No commits since {target_branch}, analyzing recent events on {current_branch}")
                    
            except subprocess.CalledProcessError:
                # Target branch doesn't exist, fall back to recent events
                recent_events = self.svcs.get_branch_events(current_branch, limit=50)
                print(f"⚠️  Target branch '{target_branch}' not found, analyzing recent events on {current_branch}")
        
        # Quality checks (strict mode affects thresholds)
        checks = {
            "complexity_increases": self._check_complexity_increases(recent_events, strict),
            "error_handling_coverage": self._check_error_handling_coverage(recent_events, strict),
            "modernization_progress": self._check_modernization_progress(recent_events, strict)
        }
        
        # In strict mode, ALL checks must pass. In normal mode, we're more lenient
        if strict:
            all_passed = all(checks.values())
        else:
            # In normal mode, allow one failing check if at least 2 pass
            passed_count = sum(checks.values())
            all_passed = passed_count >= 2
        
        print(f"🔍 Complexity Control: {'✅' if checks['complexity_increases'] else '❌'}")
        print(f"🛡️  Error Handling: {'✅' if checks['error_handling_coverage'] else '❌'}")
        print(f"🚀 Modernization: {'✅' if checks['modernization_progress'] else '❌'}")
        
        print(f"\n🏁 Quality Gate: {'✅ PASSED' if all_passed else '❌ FAILED'}")
        
        # Calculate commits analyzed based on analysis mode
        if current_branch == target_branch:
            # Same branch mode - get unique commit hashes from events analyzed
            commits_analyzed = len(set(e.get('commit_hash') for e in recent_events if e.get('commit_hash')))
            analysis_mode = "recent_commits"
        else:
            # Different branch mode - count commits since target
            try:
                cmd = ["git", "rev-list", f"{target_branch}..HEAD"]
                result = subprocess.run(cmd, cwd=self.repo_path, capture_output=True, text=True, check=True)
                commits_since_target = result.stdout.strip().split('\n') if result.stdout.strip() else []
                commits_analyzed = len(commits_since_target)
                analysis_mode = "since_target_branch"
            except subprocess.CalledProcessError:
                commits_analyzed = len(set(e.get('commit_hash') for e in recent_events if e.get('commit_hash')))
                analysis_mode = "fallback_recent"
        
        return {
            "status": "success",
            "passed": all_passed,
            "strict_mode": strict,
            "target_branch": target_branch,
            "branch": current_branch,
            "repository": str(self.repo_path),
            "analysis_mode": analysis_mode,
            "checks": checks,
            "events_analyzed": len(recent_events),
            "commits_analyzed": commits_analyzed
        }
    
    def _check_complexity_increases(self, events: List[Dict[str, Any]], strict: bool = False) -> bool:
        """Check if complexity increases are within acceptable limits."""
        complexity_increases = len([e for e in events 
                                   if 'complexity' in e.get('event_type', '') 
                                   and 'increased' in e.get('details', '')])
        # In strict mode, allow fewer complexity increases
        threshold = 1 if strict else self.quality_thresholds['max_complexity_increases']
        return complexity_increases <= threshold
    
    def _check_error_handling_coverage(self, events: List[Dict[str, Any]], strict: bool = False) -> bool:
        """Check error handling coverage."""
        new_functions = len([e for e in events 
                           if e.get('event_type') == 'node_added' 
                           and 'func:' in e.get('node_id', '')])
        error_handling_events = len([e for e in events 
                                   if 'error_handling' in e.get('event_type', '') or
                                      'try' in e.get('details', '').lower() or
                                      'except' in e.get('details', '').lower()])
        
        if new_functions == 0:
            return True
        
        # In strict mode, require higher error handling coverage
        min_ratio = 0.9 if strict else self.quality_thresholds['min_error_handling_ratio']
        ratio = error_handling_events / new_functions
        return ratio >= min_ratio
    
    def _check_modernization_progress(self, events: List[Dict[str, Any]], strict: bool = False) -> bool:
        """Check if codebase is adopting modern patterns."""
        modern_events = len([e for e in events 
                           if any(pattern in e.get('event_type', '') 
                                 for pattern in ['type_annotations', 'functional_programming', 'decorator']) or
                              any(pattern in e.get('details', '').lower()
                                 for pattern in ['async', 'await', 'type hint', 'dataclass'])])
        total_events = len(events)
        
        if total_events == 0:
            return True
        
        # In strict mode, require higher modernization ratio
        min_ratio = 0.2 if strict else 0.1
        return (modern_events / total_events) >= min_ratio
    
    def generate_ci_report(self, format_type: str = "text") -> str:
        """Generate CI report in specified format (repository-local)."""
        
        if not self.is_initialized():
            return "❌ SVCS not initialized in repository. Run 'svcs init' first."
        
        current_branch = self.svcs.get_current_branch()
        events = self.svcs.get_branch_events(current_branch, limit=200)
        
        if format_type.lower() == "json":
            return self._generate_json_report(events)
        elif format_type.lower() == "junit":
            return self._generate_junit_xml(events)
        else:
            return self._generate_text_report(events)
    
    def _generate_text_report(self, events: List[Dict[str, Any]]) -> str:
        """Generate text format CI report."""
        current_branch = self.svcs.get_current_branch()
        
        report_lines = [
            "🔍 SVCS Repository-Local CI Report",
            "=" * 40,
            f"Repository: {self.repo_path.name}",
            f"Branch: {current_branch}",
            f"Total Events: {len(events)}",
            f"Generated: {datetime.now().isoformat()}",
            ""
        ]
        
        # Event summary
        event_summary = {}
        for event in events:
            event_type = event.get('event_type', 'unknown')
            event_summary[event_type] = event_summary.get(event_type, 0) + 1
        
        if event_summary:
            report_lines.append("📊 Event Summary:")
            for event_type, count in sorted(event_summary.items()):
                report_lines.append(f"  • {event_type}: {count}")
            report_lines.append("")
        
        # Quality metrics
        quality_result = self.run_quality_gate()
        report_lines.append("🎯 Quality Metrics:")
        if quality_result.get('checks'):
            for check_name, passed in quality_result['checks'].items():
                status = "✅ PASS" if passed else "❌ FAIL"
                report_lines.append(f"  • {check_name}: {status}")
        
        return "\n".join(report_lines)
    
    def _generate_json_report(self, events: List[Dict[str, Any]]) -> str:
        """Generate JSON format CI report."""
        current_branch = self.svcs.get_current_branch()
        status = self.svcs.get_repository_status()
        quality_result = self.run_quality_gate()
        
        report_data = {
            "repository": {
                "path": str(self.repo_path),
                "name": self.repo_path.name,
                "branch": current_branch,
                "initialized": status.get('initialized', False)
            },
            "analysis": {
                "total_events": len(events),
                "events_by_type": {},
                "quality_gate": quality_result,
                "generated_at": datetime.now().isoformat()
            }
        }
        
        # Event summary
        for event in events:
            event_type = event.get('event_type', 'unknown')
            report_data["analysis"]["events_by_type"][event_type] = \
                report_data["analysis"]["events_by_type"].get(event_type, 0) + 1
        
        return json.dumps(report_data, indent=2)
    
    def _generate_junit_xml(self, events: List[Dict[str, Any]]) -> str:
        """Generate JUnit-style XML for CI systems."""
        
        quality_result = self.run_quality_gate()
        quality_passed = quality_result.get('passed', False)
        
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="SVCS Repository-Local Quality Checks" tests="1" failures="{0 if quality_passed else 1}" time="1.0">
    <testcase name="Quality Gate" classname="SVCSRepositoryLocal">
        {"" if quality_passed else '<failure message="Quality gate failed">Quality thresholds not met</failure>'}
    </testcase>
</testsuite>'''
    
    def generate_ci_artifacts(self) -> Dict[str, str]:
        """Generate artifacts for CI/CD systems."""
        
        if not self.is_initialized():
            return {"error": "SVCS not initialized in repository"}
        
        current_branch = self.svcs.get_current_branch()
        events = self.svcs.get_branch_events(current_branch, limit=200)
        artifacts = {}
        
        # Generate JUnit-style XML for test reporting
        junit_xml = self._generate_junit_xml(events)
        junit_path = self.repo_path / 'svcs-quality-report.xml'
        with open(junit_path, 'w') as f:
            f.write(junit_xml)
        artifacts['junit_xml'] = str(junit_path)
        
        # Generate JSON summary for badges/metrics
        json_report = self._generate_json_report(events)
        summary_path = self.repo_path / 'svcs-summary.json'
        with open(summary_path, 'w') as f:
            f.write(json_report)
        artifacts['json_summary'] = str(summary_path)
        
        print("📊 Repository-Local CI artifacts generated:")
        print(f"  - {junit_path}")
        print(f"  - {summary_path}")
        
        return artifacts


# Wrapper functions for CLI and Web API compatibility
def analyze_pr_semantic_impact(target_branch: str = "main", repo_path: str = None) -> Dict[str, Any]:
    """Analyze semantic impact of PR changes (CLI/API wrapper)."""
    ci = RepositoryLocalCIIntegration(repo_path)
    return ci.run_pr_analysis(target_branch)


def run_quality_gate(strict: bool = False, repo_path: str = None) -> Dict[str, Any]:
    """Run quality gate check (CLI/API wrapper)."""
    ci = RepositoryLocalCIIntegration(repo_path)
    return ci.run_quality_gate(strict)


def generate_ci_report(format_type: str = "text", repo_path: str = None) -> str:
    """Generate CI report in specified format (CLI/API wrapper)."""
    ci = RepositoryLocalCIIntegration(repo_path)
    return ci.generate_ci_report(format_type)


def generate_ci_artifacts(repo_path: str = None) -> Dict[str, str]:
    """Generate CI artifacts (CLI/API wrapper)."""
    ci = RepositoryLocalCIIntegration(repo_path)
    return ci.generate_ci_artifacts()


def _calculate_risk_level(analysis: Dict[str, Any]) -> str:
    """Calculate risk level based on analysis results."""
    total_events = analysis.get('total_events', 0)
    concerns = len(analysis.get('concerns', []))
    quality_score = analysis.get('quality_score', 0)
    
    if concerns > 2 or quality_score < -3:
        return 'high'
    elif concerns > 0 or total_events > 15 or quality_score < 0:
        return 'medium'
    else:
        return 'low'


def main():
    """Main CLI for repository-local CI/CD integration."""
    
    if len(sys.argv) < 2:
        print("Usage: python svcs_repo_ci.py [pr-analysis|quality-gate|artifacts|report] [options]")
        print("Repository-local CI/CD integration for SVCS")
        print("\nCommands:")
        print("  pr-analysis [target-branch]  - Analyze PR semantic impact (default: main)")
        print("  quality-gate [--strict]      - Run quality gate checks")
        print("  artifacts                    - Generate CI artifacts")
        print("  report [format]              - Generate CI report (text|json|junit)")
        sys.exit(1)
    
    command = sys.argv[1]
    
    # Initialize CI with current directory
    ci = RepositoryLocalCIIntegration()
    
    if command == "pr-analysis":
        target_branch = sys.argv[2] if len(sys.argv) > 2 else "main"
        result = ci.run_pr_analysis(target_branch)
        sys.exit(0 if result.get("status") == "success" else 1)
    
    elif command == "quality-gate":
        strict = "--strict" in sys.argv
        result = ci.run_quality_gate(strict=strict)
        passed = result.get('passed', False)
        sys.exit(0 if passed else 1)
    
    elif command == "artifacts":
        result = ci.generate_ci_artifacts()
        if "error" in result:
            print(f"❌ {result['error']}")
            sys.exit(1)
        sys.exit(0)
    
    elif command == "report":
        format_type = sys.argv[2] if len(sys.argv) > 2 else "text"
        result = ci.generate_ci_report(format_type)
        print(result)
        sys.exit(0)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
