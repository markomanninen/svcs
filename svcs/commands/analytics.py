#!/usr/bin/env python3
"""
SVCS Analytics and Quality Commands

Commands for generating analytics reports and quality analysis.
"""

import json
import os
import sys
from pathlib import Path
from .base import ensure_svcs_initialized, print_svcs_error


def cmd_analytics(args):
    """Generate analytics reports."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if not ensure_svcs_initialized(repo_path):
        print_svcs_error("SVCS not initialized. Run 'svcs init' first.")
        return
    
    print(f"📊 Generating analytics for repository: {repo_path.name}")
    
    try:
        # Try to use repository-local analytics if available
        try:
            from svcs_repo_analytics import generate_repository_analytics_report
            report = generate_repository_analytics_report(str(repo_path))
        except ImportError:
            # Fallback to adapted legacy analytics
            original_dir = os.getcwd()
            os.chdir(repo_path)
            
            # Import and adapt legacy analytics
            sys.path.insert(0, str(repo_path.parent))
            import svcs_analytics
            
            # Create a mock global context for legacy module
            class MockGlobalContext:
                def __init__(self, repo_path):
                    self.repo_path = repo_path
                    
                def get_projects(self):
                    return [{'path': str(repo_path), 'name': repo_path.name}]
                    
                def get_database_path(self, project_path):
                    return str(repo_path / '.svcs' / 'semantic.db')
            
            # Monkey patch for repository-local operation
            svcs_analytics.global_context = MockGlobalContext(repo_path)
            report = svcs_analytics.generate_analytics_report()
            os.chdir(original_dir)
        
        if args.output:
            output_path = Path(args.output)
            if args.format == 'json':
                with open(output_path, 'w') as f:
                    json.dump(report, f, indent=2)
                print(f"✅ Analytics report exported to: {output_path}")
            else:
                print_svcs_error("Only JSON export is currently supported")
        else:
            # Display summary
            print("✅ Analytics Report Generated")
            if isinstance(report, dict):
                print(f"📈 Total events: {report.get('total_events', 'N/A')}")
                print(f"👥 Authors: {report.get('author_count', 'N/A')}")
                print(f"📅 Date range: {report.get('date_range', 'N/A')}")
                print(f"🏆 Top event type: {report.get('top_event_type', 'N/A')}")
            
    except Exception as e:
        print_svcs_error(f"Error: {e}")


def cmd_quality(args):
    """Quality analysis."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if not ensure_svcs_initialized(repo_path):
        print_svcs_error("SVCS not initialized. Run 'svcs init' first.")
        return
    
    print(f"🎯 Running quality analysis for repository: {repo_path.name}")
    
    try:
        # Try repository-local quality analysis if available
        try:
            from svcs_repo_quality import RepositoryQualityAnalyzer
            analyzer = RepositoryQualityAnalyzer(str(repo_path))
            report = analyzer.generate_quality_report()
        except ImportError:
            # Fallback to adapted legacy quality analysis
            original_dir = os.getcwd()
            os.chdir(repo_path)
            
            sys.path.insert(0, str(repo_path.parent))
            import svcs_quality
            
            # Adapt for repository-local operation
            report = svcs_quality.analyze_repository_quality(str(repo_path))
            os.chdir(original_dir)
        
        print("✅ Quality Analysis Complete")
        
        if isinstance(report, dict):
            print(f"📊 Quality Score: {report.get('quality_score', 'N/A')}")
            print(f"🔧 Improvement Areas: {len(report.get('improvement_areas', []))}")
            print(f"✨ Positive Trends: {len(report.get('positive_trends', []))}")
            print(f"⚠️ Quality Issues: {len(report.get('quality_issues', []))}")
            
            if args.verbose and 'improvement_areas' in report:
                print("\n🔧 Top Improvement Areas:")
                for area in report['improvement_areas'][:3]:
                    print(f"   • {area}")
                    
        if args.output:
            output_path = Path(args.output)
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"💾 Quality report exported to: {output_path}")
            
    except Exception as e:
        print_svcs_error(f"Error: {e}")
