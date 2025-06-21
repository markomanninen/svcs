#!/usr/bin/env python3
"""
Demo script showing the enhanced SVCS conversational interface capabilities.
This demonstrates how the new API functions enable more meaningful conversations.
"""

import sys
import os
sys.path.append('.svcs')

from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown

try:
    from api import (
        search_events_advanced,
        get_recent_activity, 
        search_semantic_patterns,
        get_project_statistics
    )
except ImportError:
    print("Error: Could not import enhanced API functions")
    sys.exit(1)

console = Console()

def demo_conversational_queries():
    """Demonstrate various conversational query patterns."""
    
    console.print("[bold cyan]🎯 SVCS Enhanced Conversational Interface Demo[/bold cyan]\n")
    
    # Demo 1: Recent Activity
    console.print("[bold yellow]Query: \"What happened in the last 3 days?\"[/bold yellow]")
    recent = get_recent_activity(days=3, limit=10)
    
    if recent:
        table = Table(title="Recent Activity (Last 3 Days)")
        table.add_column("Date", style="cyan")
        table.add_column("Event", style="green") 
        table.add_column("Location", style="blue")
        table.add_column("Author", style="magenta")
        
        for event in recent[:5]:  # Show first 5
            date = event.get('readable_date', 'N/A')[:16]  # YYYY-MM-DD HH:MM
            event_type = event.get('event_type', 'unknown')
            location = event.get('location', 'unknown')
            author = event.get('author', 'unknown')
            table.add_row(date, event_type, location, author)
        
        console.print(table)
        console.print(f"📊 Total: {len(recent)} events. Showing first 5.\n")
    else:
        console.print("No recent activity found.\n")
    
    # Demo 2: Semantic Patterns
    console.print("[bold yellow]Query: \"Show me performance optimizations with high confidence\"[/bold yellow]")
    patterns = search_semantic_patterns(
        pattern_type="performance", 
        min_confidence=0.8,
        limit=5
    )
    
    if patterns:
        console.print("🤖 **AI-Detected Performance Optimizations:**\n")
        for i, event in enumerate(patterns, 1):
            confidence = event.get('confidence', 0)
            details = event.get('details', 'No details')
            location = event.get('location', 'unknown')
            
            console.print(f"{i}. **{location}** (confidence: {confidence:.0%})")
            console.print(f"   {details}\n")
    else:
        console.print("No performance optimizations found.\n")
    
    # Demo 3: Advanced Search
    console.print("[bold yellow]Query: \"Show me recent architecture changes by any author\"[/bold yellow]")
    advanced = search_events_advanced(
        event_types=["abstract_architecture_change", "abstract_abstraction_improvement"],
        layers=["5b"],  # AI layer only
        limit=5,
        order_by="confidence",
        order_desc=True
    )
    
    if advanced:
        console.print("🏗️ **Architecture Changes (AI Analysis):**\n")
        for event in advanced:
            confidence = event.get('confidence', 0)
            reasoning = event.get('reasoning', 'No reasoning provided')
            location = event.get('location', 'unknown')
            
            console.print(f"• **{location}** (confidence: {confidence:.0%})")
            console.print(f"  {reasoning[:100]}{'...' if len(reasoning) > 100 else ''}\n")
    else:
        console.print("No architecture changes found.\n")
    
    # Demo 4: Project Statistics
    console.print("[bold yellow]Query: \"Give me a project overview\"[/bold yellow]")
    stats = get_project_statistics(group_by="layer")
    
    if stats:
        table = Table(title="Project Statistics by Analysis Layer")
        table.add_column("Layer", style="cyan")
        table.add_column("Events", style="green", justify="right")
        table.add_column("Avg Confidence", style="blue", justify="right")
        table.add_column("Latest Activity", style="magenta")
        
        for stat in stats:
            layer = stat.get('category', 'unknown')
            count = stat.get('count', 0)
            confidence = stat.get('avg_confidence', 0)
            latest = stat.get('latest_date', 'N/A')[:16] if stat.get('latest_date') else 'N/A'
            
            conf_str = f"{confidence:.1%}" if confidence > 0 else "N/A"
            table.add_row(layer, str(count), conf_str, latest)
        
        console.print(table)
    else:
        console.print("No statistics available.\n")
    
    # Demo 5: Practical Conversation Examples
    console.print("[bold green]💬 Example Conversational Queries This System Can Handle:[/bold green]\n")
    
    examples = [
        "\"What performance optimizations were made last week?\"",
        "\"Show me all architecture changes by John with high confidence\"", 
        "\"What types of changes happen most frequently in this project?\"",
        "\"Find error handling improvements in the last month\"",
        "\"Show me the evolution of the DataProcessor class since June 1st\"",
        "\"What AI insights were detected with over 90% confidence?\"",
        "\"Recent changes in complex_algorithm.py\"",
        "\"Give me a summary of semantic patterns by layer\""
    ]
    
    for example in examples:
        console.print(f"  • {example}")
    
    console.print(f"\n[bold cyan]🎉 The enhanced API supports rich filtering, pagination, and intelligent result formatting![/bold cyan]")

if __name__ == "__main__":
    demo_conversational_queries()
