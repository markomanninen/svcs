#!/usr/bin/env python3
"""
Repository-Local Adapters for Legacy SVCS Modules

This module provides adapter functions to make legacy SVCS modules work
in repository-local mode, adapting their global database operations
to work with local .svcs/semantic.db files.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional


class RepositoryLocalAdapter:
    """Base adapter for converting legacy modules to repository-local operation."""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        self.svcs_dir = self.repo_path / '.svcs'
        self.db_path = self.svcs_dir / 'semantic.db'
        
    def ensure_svcs_initialized(self):
        """Ensure SVCS is initialized for this repository."""
        if not self.db_path.exists():
            raise FileNotFoundError(f"SVCS not initialized for {self.repo_path}. Run 'svcs init' first.")
    
    def setup_legacy_module_context(self, module_name: str):
        """Set up the execution context for a legacy module."""
        # Change to repository directory
        original_dir = os.getcwd()
        os.chdir(self.repo_path)
        
        # Add parent directory to path to find legacy modules
        parent_dir = self.repo_path.parent
        if str(parent_dir) not in sys.path:
            sys.path.insert(0, str(parent_dir))
            
        return original_dir
    
    def cleanup_context(self, original_dir: str):
        """Clean up the execution context."""
        os.chdir(original_dir)


class AnalyticsAdapter(RepositoryLocalAdapter):
    """Adapter for svcs_analytics.py module."""
    
    def generate_repository_analytics(self) -> Dict[str, Any]:
        """Generate analytics for the current repository."""
        self.ensure_svcs_initialized()
        original_dir = self.setup_legacy_module_context('svcs_analytics')
        
        try:
            import svcs_analytics
            
            # Mock the global project context to work with single repository
            class MockProjectContext:
                def __init__(self, repo_path: Path):
                    self.repo_path = repo_path
                    
                def get_all_projects(self):
                    return [{'path': str(self.repo_path), 'name': self.repo_path.name}]
                    
                def get_database_path(self, project_path: str = None):
                    return str(self.repo_path / '.svcs' / 'semantic.db')
            
            # Monkey patch for repository-local operation
            original_context = getattr(svcs_analytics, 'project_context', None)
            svcs_analytics.project_context = MockProjectContext(self.repo_path)
            
            # Generate analytics
            if hasattr(svcs_analytics, 'generate_repository_analytics'):
                result = svcs_analytics.generate_repository_analytics()
            elif hasattr(svcs_analytics, 'generate_analytics_report'):
                result = svcs_analytics.generate_analytics_report()
            else:
                # Fallback: call main analytics function
                result = svcs_analytics.main()
                
            # Restore original context
            if original_context:
                svcs_analytics.project_context = original_context
                
            return result
            
        finally:
            self.cleanup_context(original_dir)


class QualityAdapter(RepositoryLocalAdapter):
    """Adapter for svcs_quality.py module."""
    
    def analyze_repository_quality(self) -> Dict[str, Any]:
        """Analyze quality for the current repository."""
        self.ensure_svcs_initialized()
        original_dir = self.setup_legacy_module_context('svcs_quality')
        
        try:
            import svcs_quality
            
            # Adapt quality analysis for repository-local operation
            if hasattr(svcs_quality, 'analyze_repository'):
                result = svcs_quality.analyze_repository(str(self.repo_path))
            elif hasattr(svcs_quality, 'generate_quality_report'):
                result = svcs_quality.generate_quality_report(str(self.repo_path))
            else:
                # Fallback: call main quality function
                result = svcs_quality.main()
                
            return result
            
        finally:
            self.cleanup_context(original_dir)


class WebAdapter(RepositoryLocalAdapter):
    """Adapter for svcs_web.py module."""
    
    def generate_static_dashboard(self, output_path: Optional[str] = None) -> str:
        """Generate static dashboard for the current repository."""
        self.ensure_svcs_initialized()
        original_dir = self.setup_legacy_module_context('svcs_web')
        
        try:
            import svcs_web
            
            # Set output path
            if not output_path:
                output_path = f"{self.repo_path.name}_dashboard.html"
                
            # Mock project context for single repository
            class MockWebContext:
                def __init__(self, repo_path: Path):
                    self.repo_path = repo_path
                    
                def get_project_data(self):
                    return {
                        'name': self.repo_path.name,
                        'path': str(self.repo_path),
                        'database': str(self.repo_path / '.svcs' / 'semantic.db')
                    }
            
            # Adapt web generation
            original_context = getattr(svcs_web, 'web_context', None)
            svcs_web.web_context = MockWebContext(self.repo_path)
            
            if hasattr(svcs_web, 'generate_dashboard'):
                svcs_web.generate_dashboard(output_path)
            elif hasattr(svcs_web, 'create_dashboard'):
                svcs_web.create_dashboard(output_path)
            else:
                # Fallback: call main function
                svcs_web.main()
                
            # Restore context
            if original_context:
                svcs_web.web_context = original_context
                
            return output_path
            
        finally:
            self.cleanup_context(original_dir)


class WebServerAdapter(RepositoryLocalAdapter):
    """Adapter for svcs_web_server.py module."""
    
    def start_web_server(self, host: str = '127.0.0.1', port: int = 8080, debug: bool = False):
        """Start web server for the current repository."""
        self.ensure_svcs_initialized()
        original_dir = self.setup_legacy_module_context('svcs_web_server')
        
        try:
            import svcs_web_server
            
            # Configure for repository-local operation
            svcs_web_server.REPOSITORY_PATH = str(self.repo_path)
            svcs_web_server.DATABASE_PATH = str(self.db_path)
            
            # Start server
            if hasattr(svcs_web_server, 'create_app'):
                app = svcs_web_server.create_app()
                app.run(host=host, port=port, debug=debug)
            elif hasattr(svcs_web_server, 'run_server'):
                svcs_web_server.run_server(host=host, port=port, debug=debug)
            else:
                # Fallback: call main function
                svcs_web_server.main()
                
        finally:
            self.cleanup_context(original_dir)


class CIAdapter(RepositoryLocalAdapter):
    """Adapter for svcs_ci.py module."""
    
    def run_ci_command(self, command: str, **kwargs) -> Dict[str, Any]:
        """Run CI command for the current repository."""
        self.ensure_svcs_initialized()
        original_dir = self.setup_legacy_module_context('svcs_repo_ci')
        
        try:
            # Try to use new repository-local CI integration first
            try:
                import svcs_repo_ci as svcs_ci
            except ImportError:
                # Fallback to legacy CI integration
                import svcs_ci
            
            # Set repository context
            if hasattr(svcs_ci, 'CURRENT_REPOSITORY'):
                svcs_ci.CURRENT_REPOSITORY = str(self.repo_path)
            
            if command == 'pr-analysis':
                target_branch = kwargs.get('target', 'main')
                if hasattr(svcs_ci, 'analyze_pr_semantic_impact'):
                    result = svcs_ci.analyze_pr_semantic_impact(target_branch)
                else:
                    result = {'status': 'not_implemented'}
                    
            elif command == 'quality-gate':
                strict = kwargs.get('strict', False)
                if hasattr(svcs_ci, 'run_quality_gate'):
                    result = svcs_ci.run_quality_gate(strict=strict)
                else:
                    result = {'status': 'not_implemented'}
                    
            elif command == 'report':
                format_type = kwargs.get('format', 'text')
                if hasattr(svcs_ci, 'generate_ci_report'):
                    result = svcs_ci.generate_ci_report(format_type)
                else:
                    result = {'status': 'not_implemented'}
                    
            else:
                result = {'error': f'Unknown CI command: {command}'}
                
            return result
            
        finally:
            self.cleanup_context(original_dir)


class DiscussAdapter(RepositoryLocalAdapter):
    """Adapter for svcs_discuss.py module."""
    
    def start_interactive_session(self):
        """Start conversational interface for the current repository."""
        self.ensure_svcs_initialized()
        original_dir = self.setup_legacy_module_context('svcs_discuss')
        
        try:
            import legacy_scripts.svcs_discuss as svcs_discuss
            
            # Set repository context
            svcs_discuss.REPOSITORY_PATH = str(self.repo_path)
            svcs_discuss.DATABASE_PATH = str(self.db_path)
            
            # Start interactive session
            if hasattr(svcs_discuss, 'start_interactive_session'):
                svcs_discuss.start_interactive_session()
            elif hasattr(svcs_discuss, 'main'):
                svcs_discuss.main()
            else:
                print("❌ Interactive session not available")
                
        finally:
            self.cleanup_context(original_dir)
    
    def process_query(self, query: str) -> str:
        """Process a single natural language query."""
        self.ensure_svcs_initialized()
        original_dir = self.setup_legacy_module_context('svcs_discuss')
        
        try:
            import legacy_scripts.svcs_discuss as svcs_discuss
            
            # Set repository context
            svcs_discuss.REPOSITORY_PATH = str(self.repo_path)
            svcs_discuss.DATABASE_PATH = str(self.db_path)
            
            # Process query
            if hasattr(svcs_discuss, 'process_query'):
                result = svcs_discuss.process_query(query)
            elif hasattr(svcs_discuss, 'handle_query'):
                result = svcs_discuss.handle_query(query)
            else:
                result = f"Query processed: {query}"
                
            return result
            
        finally:
            self.cleanup_context(original_dir)


# Convenience functions for CLI usage
def get_analytics_adapter(repo_path: str) -> AnalyticsAdapter:
    """Get analytics adapter for repository."""
    return AnalyticsAdapter(repo_path)


def get_quality_adapter(repo_path: str) -> QualityAdapter:
    """Get quality adapter for repository."""
    return QualityAdapter(repo_path)


def get_web_adapter(repo_path: str) -> WebAdapter:
    """Get web adapter for repository."""
    return WebAdapter(repo_path)


def get_web_server_adapter(repo_path: str) -> WebServerAdapter:
    """Get web server adapter for repository."""
    return WebServerAdapter(repo_path)


def get_ci_adapter(repo_path: str) -> CIAdapter:
    """Get CI adapter for repository."""
    return CIAdapter(repo_path)


def get_discuss_adapter(repo_path: str) -> DiscussAdapter:
    """Get discussion adapter for repository."""
    return DiscussAdapter(repo_path)
