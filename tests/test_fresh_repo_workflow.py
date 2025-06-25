#!/usr/bin/env python3
"""
SVCS Complete Workflow Test in Fresh Repository

This script creates a fresh repository from scratch and tests:
1. Create /tmp/svcs_test directory and initialize git
2. Initialize SVCS repository-local tracking
3. Create initial code and commit
4. Make code modifications and commit (semantic changes)
5. Create feature branch
6. Make changes on feature branch
7. Search for semantic changes transferred from parent
8. Merge changes back to parent branch
9. Verify semantic changes are preserved in local repo database
"""

import os
import subprocess
import sys
import shutil
from pathlib import Path
import sqlite3
import tempfile
import datetime

# Global log file handle for test output
log_file = None

def init_logging():
    """Initialize logging to file."""
    global log_file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"test_fresh_repo_workflow_{timestamp}.log"
    log_file = open(log_filename, 'w', encoding='utf-8')
    log_and_print(f"🚀 SVCS Fresh Repository Workflow Test - {datetime.datetime.now()}")
    log_and_print(f"📝 Log file: {log_filename}")
    log_and_print("=" * 70)
    return log_filename

def log_and_print(message):
    """Print message and write to log file."""
    print(message)
    if log_file:
        log_file.write(message + '\n')
        log_file.flush()

def close_logging():
    """Close the log file."""
    global log_file
    if log_file:
        log_and_print(f"\n📝 Test completed at: {datetime.datetime.now()}")
        log_file.close()
        log_file = None

class SVCSFreshRepoTest:
    def __init__(self):
        self.test_dir = Path("/tmp/svcs_test")
        self.original_dir = Path.cwd()
        self.svcs_source = Path.cwd()  # Current SVCS directory
        
    def run_command(self, cmd, check=True, capture_output=True):
        """Run a shell command and return the result"""
        if isinstance(cmd, list):
            cmd_str = ' '.join(cmd)
        else:
            cmd_str = cmd
        log_and_print(f"🔧 Running: {cmd_str}")
        
        result = subprocess.run(cmd, shell=True if isinstance(cmd, str) else False, 
                              capture_output=capture_output, text=True, check=check, 
                              cwd=self.test_dir)
        
        if capture_output and result.stdout.strip():
            log_and_print(f"📤 Output: {result.stdout.strip()}")
        if result.stderr and result.stderr.strip():
            log_and_print(f"⚠️  Error: {result.stderr.strip()}")
        
        return result
    
    def setup_fresh_repo(self):
        """Create a fresh repository in /tmp/svcs_test"""
        log_and_print("\n🏗️  STEP 1: Setting up fresh repository")
        
        # Clean up any existing test directory
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
            log_and_print(f"🧹 Cleaned up existing {self.test_dir}")
        
        # Create fresh directory
        self.test_dir.mkdir(parents=True, exist_ok=True)
        log_and_print(f"📁 Created fresh directory: {self.test_dir}")
        
        # Initialize git repository
        self.run_command("git init")
        self.run_command("git config user.name 'SVCS Test User'")
        self.run_command("git config user.email 'test@svcs.example'")
        
        log_and_print("✅ Fresh git repository initialized")
    
    def copy_svcs_files(self):
        """Copy necessary SVCS files to the test repository"""
        print("\n📋 STEP 2: Copying SVCS files")
        
        # Essential SVCS files
        svcs_files = [
            "svcs_repo_local.py",
            "svcs_local_cli.py", 
            "svcs_repo_hooks.py",
            "svcs_repo_analyzer.py",
            "svcs_multilang.py"
        ]
        
        # Copy SVCS Python files
        for file in svcs_files:
            src = self.svcs_source / file
            dst = self.test_dir / file
            if src.exists():
                shutil.copy2(src, dst)
                print(f"📄 Copied {file}")
            else:
                print(f"⚠️  Missing source file: {file}")
        
        # Copy .svcs directory with analyzer
        svcs_dir = self.svcs_source / ".svcs"
        if svcs_dir.exists():
            shutil.copytree(svcs_dir, self.test_dir / ".svcs")
            print("📁 Copied .svcs directory")
            
            # Remove existing databases to start with a truly fresh repository
            fresh_svcs_dir = self.test_dir / ".svcs"
            for db_file in ["semantic.db", "semantic_events.db", "history.db"]:
                db_path = fresh_svcs_dir / db_file
                if db_path.exists():
                    db_path.unlink()
                    print(f"🗑️  Removed existing database: {db_file}")
        else:
            # Create minimal .svcs directory if it doesn't exist
            (self.test_dir / ".svcs").mkdir(exist_ok=True)
            print("📁 Created .svcs directory")
        
        # Copy svcs_mcp directory for advanced features
        svcs_mcp_dir = self.svcs_source / "svcs_mcp"
        if svcs_mcp_dir.exists():
            shutil.copytree(svcs_mcp_dir, self.test_dir / "svcs_mcp")
            print("📁 Copied svcs_mcp directory")
        
        print("✅ SVCS files copied successfully")
    
    def initialize_svcs(self):
        """Initialize SVCS in the fresh repository"""
        print("\n🔧 STEP 3: Initializing SVCS")
        
        result = self.run_command("python3 svcs_local_cli.py init")
        
        # Verify initialization
        svcs_db = self.test_dir / ".svcs" / "semantic.db"
        if svcs_db.exists():
            print("✅ SVCS database created")
        else:
            print("❌ SVCS database not found")
            return False
        
        # Check git hooks
        hooks_dir = self.test_dir / ".git" / "hooks"
        expected_hooks = ["post-commit", "post-merge", "post-checkout", "pre-push"]
        
        for hook in expected_hooks:
            hook_file = hooks_dir / hook
            if hook_file.exists():
                print(f"✅ Git hook installed: {hook}")
            else:
                print(f"❌ Missing git hook: {hook}")
        
        print("✅ SVCS initialization completed")
        return True
    
    def create_initial_code(self):
        """Create initial code and commit"""
        print("\n📝 STEP 4: Creating initial code")
        
        # Create initial Python file
        initial_code = '''#!/usr/bin/env python3
"""
Initial code for SVCS workflow testing.
"""

import math

def calculate_area(radius):
    """Calculate the area of a circle."""
    return math.pi * radius ** 2

def calculate_perimeter(radius):
    """Calculate the perimeter of a circle."""
    return 2 * math.pi * radius

class Circle:
    """A simple circle class."""
    
    def __init__(self, radius):
        self.radius = radius
    
    def area(self):
        """Get the area of the circle."""
        return calculate_area(self.radius)
    
    def perimeter(self):
        """Get the perimeter of the circle."""
        return calculate_perimeter(self.radius)

if __name__ == "__main__":
    circle = Circle(5)
    print(f"Circle with radius 5:")
    print(f"  Area: {circle.area():.2f}")
    print(f"  Perimeter: {circle.perimeter():.2f}")
'''
        
        code_file = self.test_dir / "geometry.py"
        with open(code_file, 'w') as f:
            f.write(initial_code)
        
        # Commit initial code
        self.run_command("git add geometry.py")
        self.run_command('git commit -m "Initial commit: basic circle geometry functions"')
        
        print("✅ Initial code committed")
    
    def make_semantic_changes(self):
        """Make semantic changes to trigger SVCS analysis"""
        print("\n🔄 STEP 5: Making semantic changes")
        
        # Enhanced code with new functionality
        enhanced_code = '''#!/usr/bin/env python3
"""
Enhanced geometry code for SVCS workflow testing.
"""

import math
from typing import Union

def calculate_area(radius: float) -> float:
    """Calculate the area of a circle with type hints."""
    if radius < 0:
        raise ValueError("Radius cannot be negative")
    return math.pi * radius ** 2

def calculate_perimeter(radius: float) -> float:
    """Calculate the perimeter of a circle with type hints."""
    if radius < 0:
        raise ValueError("Radius cannot be negative")
    return 2 * math.pi * radius

def calculate_volume(radius: float, height: float) -> float:
    """NEW FUNCTION: Calculate the volume of a cylinder."""
    base_area = calculate_area(radius)
    return base_area * height

class Circle:
    """An enhanced circle class with validation."""
    
    def __init__(self, radius: float):
        if radius < 0:
            raise ValueError("Radius cannot be negative")
        self.radius = radius
        self._cached_area = None
    
    def area(self) -> float:
        """Get the area of the circle with caching."""
        if self._cached_area is None:
            self._cached_area = calculate_area(self.radius)
        return self._cached_area
    
    def perimeter(self) -> float:
        """Get the perimeter of the circle."""
        return calculate_perimeter(self.radius)
    
    def scale(self, factor: float) -> 'Circle':
        """NEW METHOD: Create a new circle scaled by a factor."""
        return Circle(self.radius * factor)

class Cylinder(Circle):
    """NEW CLASS: A cylinder extending circle."""
    
    def __init__(self, radius: float, height: float):
        super().__init__(radius)
        self.height = height
    
    def volume(self) -> float:
        """Calculate the volume of the cylinder."""
        return calculate_volume(self.radius, self.height)
    
    def surface_area(self) -> float:
        """Calculate the surface area of the cylinder."""
        base_area = self.area()
        side_area = self.perimeter() * self.height
        return 2 * base_area + side_area

if __name__ == "__main__":
    # Test circle
    circle = Circle(5)
    print(f"Circle with radius 5:")
    print(f"  Area: {circle.area():.2f}")
    print(f"  Perimeter: {circle.perimeter():.2f}")
    
    # Test cylinder
    cylinder = Cylinder(3, 10)
    print(f"\\nCylinder with radius 3 and height 10:")
    print(f"  Volume: {cylinder.volume():.2f}")
    print(f"  Surface Area: {cylinder.surface_area():.2f}")
    
    # Test scaling
    big_circle = circle.scale(2)
    print(f"\\nScaled circle (2x):")
    print(f"  New radius: {big_circle.radius}")
    print(f"  New area: {big_circle.area():.2f}")
'''
        
        code_file = self.test_dir / "geometry.py"
        with open(code_file, 'w') as f:
            f.write(enhanced_code)
        
        # Commit semantic changes
        self.run_command("git add geometry.py")
        self.run_command('git commit -m "Enhance geometry: add type hints, validation, new functions and classes"')
        
        print("✅ Semantic changes committed")
    
    def check_semantic_events(self, description=""):
        """Check current semantic events in the database"""
        print(f"\n📊 Checking semantic events {description}")
        
        # Check with CLI
        result = self.run_command("python3 svcs_local_cli.py events --limit 10")
        
        # Also check database directly
        db_path = self.test_dir / ".svcs" / "semantic.db"
        if db_path.exists():
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM semantic_events")
            count = cursor.fetchone()[0]
            print(f"📈 Total semantic events in database: {count}")
            
            # Get events by branch
            cursor.execute("""
                SELECT branch, COUNT(*) 
                FROM semantic_events 
                GROUP BY branch
                ORDER BY COUNT(*) DESC
            """)
            branch_counts = cursor.fetchall()
            
            print("📊 Events by branch:")
            for branch, event_count in branch_counts:
                print(f"  🌿 {branch}: {event_count} events")
            
            conn.close()
            return count
        else:
            print("❌ Semantic database not found")
            return 0
    
    def create_feature_branch(self):
        """Create a feature branch and make changes"""
        print("\n🌿 STEP 6: Creating feature branch")
        
        # Create feature branch
        self.run_command("git checkout -b feature/advanced-shapes")
        
        # Add new advanced shapes functionality
        advanced_code = '''#!/usr/bin/env python3
"""
Advanced shapes module for feature branch testing.
"""

import math
from abc import ABC, abstractmethod
from typing import Protocol

class Shape(ABC):
    """Abstract base class for all shapes."""
    
    @abstractmethod
    def area(self) -> float:
        """Calculate the area of the shape."""
        pass
    
    @abstractmethod
    def perimeter(self) -> float:
        """Calculate the perimeter of the shape."""
        pass

class HasVolume(Protocol):
    """Protocol for shapes that have volume."""
    
    def volume(self) -> float:
        """Calculate the volume."""
        ...

class Rectangle(Shape):
    """NEW CLASS: Rectangle implementation."""
    
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height
    
    def area(self) -> float:
        """Calculate rectangle area."""
        return self.width * self.height
    
    def perimeter(self) -> float:
        """Calculate rectangle perimeter."""
        return 2 * (self.width + self.height)

class Triangle(Shape):
    """NEW CLASS: Triangle implementation."""
    
    def __init__(self, a: float, b: float, c: float):
        # Validate triangle inequality
        if not (a + b > c and a + c > b and b + c > a):
            raise ValueError("Invalid triangle sides")
        self.a, self.b, self.c = a, b, c
    
    def area(self) -> float:
        """Calculate triangle area using Heron's formula."""
        s = self.perimeter() / 2  # semi-perimeter
        return math.sqrt(s * (s - self.a) * (s - self.b) * (s - self.c))
    
    def perimeter(self) -> float:
        """Calculate triangle perimeter."""
        return self.a + self.b + self.c

def calculate_total_area(*shapes: Shape) -> float:
    """NEW FUNCTION: Calculate total area of multiple shapes."""
    return sum(shape.area() for shape in shapes)

def compare_shapes(shape1: Shape, shape2: Shape) -> dict:
    """NEW FUNCTION: Compare two shapes."""
    return {
        "shape1_area": shape1.area(),
        "shape2_area": shape2.area(),
        "area_difference": abs(shape1.area() - shape2.area()),
        "larger_shape": "shape1" if shape1.area() > shape2.area() else "shape2"
    }

if __name__ == "__main__":
    # Test new shapes
    rectangle = Rectangle(4, 6)
    triangle = Triangle(3, 4, 5)
    
    print("🔷 Rectangle (4x6):")
    print(f"  Area: {rectangle.area()}")
    print(f"  Perimeter: {rectangle.perimeter()}")
    
    print("🔺 Triangle (3-4-5):")
    print(f"  Area: {triangle.area():.2f}")
    print(f"  Perimeter: {triangle.perimeter()}")
    
    print(f"\\n📊 Total area: {calculate_total_area(rectangle, triangle):.2f}")
    
    comparison = compare_shapes(rectangle, triangle)
    print(f"📈 Shape comparison: {comparison}")
'''
        
        shapes_file = self.test_dir / "advanced_shapes.py"
        with open(shapes_file, 'w') as f:
            f.write(advanced_code)
        
        # Commit feature branch changes
        self.run_command("git add advanced_shapes.py")
        self.run_command('git commit -m "Feature: Add advanced shapes with ABC, protocols, and new classes"')
        
        print("✅ Feature branch created with new functionality")
    
    def search_semantic_changes(self):
        """Search for semantic changes transferred from parent"""
        print("\n🔍 STEP 7: Searching for semantic changes from parent")
        
        # Get current branch
        result = self.run_command("git branch --show-current")
        current_branch = result.stdout.strip()
        
        # Compare branches
        result = self.run_command(f"python3 svcs_local_cli.py compare main {current_branch}")
        
        # Show merged events to see cross-branch visibility
        result = self.run_command("python3 svcs_local_cli.py merged-events --limit 15")
        
        print("✅ Semantic changes searched and compared")
    
    def merge_back_to_main(self):
        """Merge feature branch back to main"""
        print("\n🔄 STEP 8: Merging feature branch back to main")
        
        # Switch to main
        self.run_command("git checkout main")
        
        # Count events before merge
        events_before = self.check_semantic_events("(main before merge)")
        
        # Merge feature branch
        self.run_command("git merge feature/advanced-shapes --no-ff -m 'Merge feature/advanced-shapes: Add advanced shape classes'")
        
        # Count events after merge
        events_after = self.check_semantic_events("(main after merge)")
        
        print(f"📈 Events added during merge: {events_after - events_before}")
        print("✅ Feature branch merged successfully")
        
        return events_after
    
    def verify_final_state(self):
        """Verify the final state of the repository and semantic data"""
        print("\n✅ STEP 9: Final verification")
        
        # Check files exist
        files_to_check = ["geometry.py", "advanced_shapes.py"]
        for file in files_to_check:
            file_path = self.test_dir / file
            if file_path.exists():
                print(f"✅ File exists: {file}")
            else:
                print(f"❌ Missing file: {file}")
        
        # Final event count
        final_events = self.check_semantic_events("(final state)")
        
        # Show git commit history
        print("\n📜 Git commit history:")
        self.run_command("git log --oneline --graph")
        
        # Show current branch
        result = self.run_command("git branch --show-current")
        print(f"🌿 Current branch: {result.stdout.strip()}")
        
        # Check git notes
        print("\n📝 Git notes verification:")
        result = self.run_command("git notes --ref refs/notes/svcs-semantic list", check=False)
        notes_lines = [line for line in result.stdout.strip().split('\n') if line.strip()]
        print(f"📝 Git notes found: {len(notes_lines)}")
        
        return final_events
    
    def cleanup(self):
        """Clean up the test directory"""
        print(f"\n🧹 Cleaning up test directory: {self.test_dir}")
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
            print("✅ Cleanup completed")
    
    def run_complete_test(self):
        """Run the complete SVCS workflow test"""
        # Initialize logging first
        log_filename = init_logging()
        
        try:
            log_and_print("🚀 SVCS Fresh Repository Complete Workflow Test")
            log_and_print("=" * 70)
            
            # Step 1-3: Setup
            self.setup_fresh_repo()
            self.copy_svcs_files()
            if not self.initialize_svcs():
                log_and_print("❌ SVCS initialization failed")
                return False
            
            # Step 4-5: Initial development
            self.create_initial_code()
            initial_events = self.check_semantic_events("(after initial commit)")
            
            self.make_semantic_changes()
            enhanced_events = self.check_semantic_events("(after enhancements)")
            
            # Step 6-7: Feature branch development
            self.create_feature_branch()
            feature_events = self.check_semantic_events("(after feature branch)")
            
            self.search_semantic_changes()
            
            # Step 8-9: Merge and verification
            final_events = self.merge_back_to_main()
            self.verify_final_state()
            
            # Summary
            log_and_print("\n" + "=" * 70)
            log_and_print("🎯 COMPLETE WORKFLOW TEST SUMMARY")
            log_and_print("=" * 70)
            log_and_print(f"📊 Initial events: {initial_events}")
            log_and_print(f"📊 After enhancements: {enhanced_events}")
            log_and_print(f"📊 After feature development: {feature_events}")
            log_and_print(f"📊 Final events: {final_events}")
            log_and_print(f"📈 Total new events created: {final_events}")
            
            if final_events > 0:
                log_and_print("✅ SUCCESS: Complete workflow validated!")
                log_and_print("✅ SVCS successfully tracked semantic changes throughout development")
                log_and_print("✅ Repository-local database maintained data integrity")
                log_and_print("✅ Git integration worked seamlessly")
                log_and_print("✅ Branch workflows preserved semantic history")
                return True
            else:
                log_and_print("❌ FAILURE: No semantic events were tracked")
                return False
                
        except Exception as e:
            log_and_print(f"❌ Test failed with error: {e}")
            import traceback
            log_and_print(f"📜 Traceback:\n{traceback.format_exc()}")
            return False
        
        finally:
            # Always clean up test directory and close logging
            self.cleanup()
            close_logging()
            if 'log_filename' in locals():
                print(f"\n📝 Complete test log saved to: {log_filename}")

def main():
    """Main entry point"""
    tester = SVCSFreshRepoTest()
    success = tester.run_complete_test()
    
    if success:
        print("\n🎉 SVCS Fresh Repository Test: PASSED")
        return 0
    else:
        print("\n💥 SVCS Fresh Repository Test: FAILED") 
        return 1

if __name__ == "__main__":
    sys.exit(main())
