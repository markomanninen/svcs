#!/usr/bin/env python3
"""
SVCS CI/CD Integration Commands

Commands for continuous integration and deployment support.
"""

import os
import sys
from pathlib import Path
from .base import ensure_svcs_initialized, print_svcs_error


def cmd_ci(args):
    """CI/CD integration."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if not ensure_svcs_initialized(repo_path):
        print_svcs_error("SVCS not initialized. Run 'svcs init' first.")
        return
    
    print(f"🔄 Running CI command: {args.ci_command}")
    
    try:
        original_dir = os.getcwd()
        os.chdir(repo_path)
        
        # Try to use new repository-local CI integration first
        try:
            sys.path.insert(0, str(repo_path.parent))
            import svcs_repo_ci as svcs_ci
        except ImportError:
            # Fallback to legacy CI integration
            sys.path.insert(0, str(repo_path.parent))
            import svcs_ci
        
        if args.ci_command == 'pr-analysis':
            target_branch = args.target or 'main'
            result = svcs_ci.analyze_pr_semantic_impact(target_branch)
            print("✅ PR Analysis Complete")
            if isinstance(result, dict):
                print(f"📊 Semantic changes: {result.get('change_count', 'N/A')}")
                print(f"🎯 Risk level: {result.get('risk_level', 'N/A')}")
                
        elif args.ci_command == 'quality-gate':
            result = svcs_ci.run_quality_gate(strict=args.strict)
            print("✅ Quality Gate Complete")
            if isinstance(result, dict):
                passed = result.get('passed', False)
                print(f"{'✅' if passed else '❌'} Status: {'PASSED' if passed else 'FAILED'}")
                
        elif args.ci_command == 'report':
            format_type = args.format or 'text'
            result = svcs_ci.generate_ci_report(format_type)
            print(f"✅ CI Report generated in {format_type} format")
            
        os.chdir(original_dir)
        
    except Exception as e:
        print_svcs_error(f"Error: {e}")
        os.chdir(original_dir)
