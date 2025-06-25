#!/usr/bin/env python3
"""
SVCS Web Interface - Visual exploration of semantic code evolution
"""

import sys
import os
import json
from datetime import datetime
from collections import defaultdict, Counter

sys.path.insert(0, '.svcs')
from api import get_full_log, get_node_evolution

def generate_web_interface():
    """Generate a static HTML interface for exploring SVCS data."""
    
    print("🌐 Generating SVCS Web Interface...")
    
    events = get_full_log()
    
    # Prepare data for visualization
    timeline_data = prepare_timeline_data(events)
    network_data = prepare_network_data(events)
    stats_data = prepare_statistics_data(events)
    
    html_content = create_html_interface(timeline_data, network_data, stats_data)
    
    # Write HTML file
    with open('svcs_dashboard.html', 'w') as f:
        f.write(html_content)
    
    print("✅ Web interface generated: svcs_dashboard.html")
    print("🚀 Open in browser to explore your code evolution!")

def prepare_timeline_data(events):
    """Prepare timeline data for visualization."""
    
    timeline = []
    daily_events = defaultdict(list)
    
    for event in events:
        date = datetime.fromtimestamp(event['timestamp']).strftime('%Y-%m-%d')
        daily_events[date].append(event)
    
    for date, day_events in sorted(daily_events.items()):
        event_types = Counter(e['event_type'] for e in day_events)
        timeline.append({
            'date': date,
            'total_events': len(day_events),
            'event_types': dict(event_types),
            'details': day_events[:10]  # Top 10 events for details
        })
    
    return timeline

def prepare_network_data(events):
    """Prepare network data showing relationships between files and functions."""
    
    nodes = []
    links = []
    
    # File nodes
    files = set(e['location'] for e in events)
    for filepath in files:
        file_events = [e for e in events if e['location'] == filepath]
        nodes.append({
            'id': filepath,
            'type': 'file',
            'size': len(file_events),
            'color': '#2E8B57'
        })
    
    # Function/class nodes
    functions = set(e['node_id'] for e in events if e['node_id'].startswith(('func:', 'class:')))
    for func_id in functions:
        func_events = [e for e in events if e['node_id'] == func_id]
        nodes.append({
            'id': func_id,
            'type': 'function',
            'size': min(len(func_events) * 3, 50),
            'color': '#FF6347' if func_id.startswith('func:') else '#4169E1'
        })
        
        # Link functions to their files
        for event in func_events:
            links.append({
                'source': func_id,
                'target': event['location'],
                'strength': 1
            })
    
    return {'nodes': nodes, 'links': links}

def prepare_statistics_data(events):
    """Prepare statistical data for charts."""
    
    return {
        'event_type_distribution': dict(Counter(e['event_type'] for e in events)),
        'file_activity': dict(Counter(e['location'] for e in events)),
        'temporal_activity': prepare_temporal_stats(events),
        'complexity_evolution': prepare_complexity_stats(events)
    }

def prepare_temporal_stats(events):
    """Prepare temporal statistics."""
    
    hourly_activity = defaultdict(int)
    for event in events:
        hour = datetime.fromtimestamp(event['timestamp']).hour
        hourly_activity[hour] += 1
    
    return {
        'hourly': dict(hourly_activity),
        'total_events': len(events),
        'date_range': {
            'start': min(e['timestamp'] for e in events) if events else 0,
            'end': max(e['timestamp'] for e in events) if events else 0
        }
    }

def prepare_complexity_stats(events):
    """Prepare complexity evolution statistics."""
    
    complexity_events = [e for e in events if 'complexity' in e['event_type']]
    error_events = [e for e in events if 'error' in e['event_type'] or 'exception' in e['event_type']]
    modern_events = [e for e in events if any(pattern in e['event_type'] 
                    for pattern in ['functional_programming', 'type_annotations', 'decorator'])]
    
    return {
        'complexity_changes': len(complexity_events),
        'error_handling_evolution': len(error_events),
        'modernization_events': len(modern_events)
    }

def create_html_interface(timeline_data, network_data, stats_data):
    """Create the HTML interface with embedded JavaScript visualizations."""
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SVCS - Semantic Code Evolution Dashboard</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2C3E50 0%, #3498DB 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }}
        
        .dashboard {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            padding: 30px;
        }}
        
        .panel {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .panel h3 {{
            margin: 0 0 20px 0;
            color: #2C3E50;
            font-size: 1.4em;
            border-bottom: 2px solid #3498DB;
            padding-bottom: 10px;
        }}
        
        .full-width {{
            grid-column: 1 / -1;
        }}
        
        .metric {{
            display: inline-block;
            margin: 10px 15px;
            text-align: center;
        }}
        
        .metric-value {{
            display: block;
            font-size: 2em;
            font-weight: bold;
            color: #3498DB;
        }}
        
        .metric-label {{
            display: block;
            font-size: 0.9em;
            color: #7F8C8D;
            margin-top: 5px;
        }}
        
        #timeline {{
            height: 300px;
        }}
        
        #network {{
            height: 400px;
        }}
        
        .chart-container {{
            position: relative;
            height: 300px;
        }}
        
        .event-list {{
            max-height: 300px;
            overflow-y: auto;
            background: white;
            border-radius: 5px;
            padding: 15px;
        }}
        
        .event-item {{
            padding: 8px;
            margin: 5px 0;
            background: #ECF0F1;
            border-radius: 5px;
            border-left: 4px solid #3498DB;
        }}
        
        .event-type {{
            font-weight: bold;
            color: #2C3E50;
        }}
        
        .event-details {{
            font-size: 0.9em;
            color: #7F8C8D;
            margin-top: 3px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 SVCS Dashboard</h1>
            <p>Semantic Code Evolution Analysis</p>
        </div>
        
        <div class="dashboard">
            <!-- Key Metrics -->
            <div class="panel full-width">
                <h3>📊 Key Metrics</h3>
                <div class="metric">
                    <span class="metric-value">{len(timeline_data)}</span>
                    <span class="metric-label">Active Days</span>
                </div>
                <div class="metric">
                    <span class="metric-value">{stats_data['temporal_activity']['total_events']}</span>
                    <span class="metric-label">Total Events</span>
                </div>
                <div class="metric">
                    <span class="metric-value">{len(stats_data['event_type_distribution'])}</span>
                    <span class="metric-label">Event Types</span>
                </div>
                <div class="metric">
                    <span class="metric-value">{len(stats_data['file_activity'])}</span>
                    <span class="metric-label">Files Tracked</span>
                </div>
                <div class="metric">
                    <span class="metric-value">{stats_data['complexity_evolution']['modernization_events']}</span>
                    <span class="metric-label">Modernization Events</span>
                </div>
            </div>
            
            <!-- Timeline -->
            <div class="panel full-width">
                <h3>📈 Evolution Timeline</h3>
                <div id="timeline"></div>
            </div>
            
            <!-- Event Distribution -->
            <div class="panel">
                <h3>🎯 Event Type Distribution</h3>
                <div class="chart-container">
                    <canvas id="eventChart"></canvas>
                </div>
            </div>
            
            <!-- File Activity -->
            <div class="panel">
                <h3>🔥 File Activity</h3>
                <div class="chart-container">
                    <canvas id="fileChart"></canvas>
                </div>
            </div>
            
            <!-- Network Visualization -->
            <div class="panel full-width">
                <h3>🌐 Code Structure Network</h3>
                <div id="network"></div>
            </div>
            
            <!-- Recent Events -->
            <div class="panel full-width">
                <h3>⚡ Recent Events</h3>
                <div class="event-list" id="recentEvents"></div>
            </div>
        </div>
    </div>

    <script>
        // Data from Python
        const timelineData = {json.dumps(timeline_data)};
        const networkData = {json.dumps(network_data)};
        const statsData = {json.dumps(stats_data)};
        
        // Event Type Distribution Chart
        const eventCtx = document.getElementById('eventChart').getContext('2d');
        new Chart(eventCtx, {{
            type: 'doughnut',
            data: {{
                labels: Object.keys(statsData.event_type_distribution).slice(0, 8),
                datasets: [{{
                    data: Object.values(statsData.event_type_distribution).slice(0, 8),
                    backgroundColor: [
                        '#3498DB', '#E74C3C', '#2ECC71', '#F39C12',
                        '#9B59B6', '#1ABC9C', '#34495E', '#E67E22'
                    ]
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }}
                }}
            }}
        }});
        
        // File Activity Chart
        const fileCtx = document.getElementById('fileChart').getContext('2d');
        const topFiles = Object.entries(statsData.file_activity)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 6);
            
        new Chart(fileCtx, {{
            type: 'bar',
            data: {{
                labels: topFiles.map(f => f[0].split('/').pop()),
                datasets: [{{
                    label: 'Changes',
                    data: topFiles.map(f => f[1]),
                    backgroundColor: '#3498DB'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
        
        // Timeline Visualization
        const timelineDiv = d3.select('#timeline');
        const timelineWidth = timelineDiv.node().getBoundingClientRect().width;
        const timelineHeight = 250;
        
        const timelineSvg = timelineDiv
            .append('svg')
            .attr('width', timelineWidth)
            .attr('height', timelineHeight);
            
        const xScale = d3.scaleTime()
            .domain(d3.extent(timelineData, d => new Date(d.date)))
            .range([50, timelineWidth - 50]);
            
        const yScale = d3.scaleLinear()
            .domain([0, d3.max(timelineData, d => d.total_events)])
            .range([timelineHeight - 50, 50]);
        
        const line = d3.line()
            .x(d => xScale(new Date(d.date)))
            .y(d => yScale(d.total_events))
            .curve(d3.curveMonotoneX);
        
        timelineSvg.append('path')
            .datum(timelineData)
            .attr('fill', 'none')
            .attr('stroke', '#3498DB')
            .attr('stroke-width', 3)
            .attr('d', line);
        
        timelineSvg.selectAll('.dot')
            .data(timelineData)
            .enter().append('circle')
            .attr('class', 'dot')
            .attr('cx', d => xScale(new Date(d.date)))
            .attr('cy', d => yScale(d.total_events))
            .attr('r', 5)
            .attr('fill', '#E74C3C');
        
        // Network Visualization
        const networkDiv = d3.select('#network');
        const networkWidth = networkDiv.node().getBoundingClientRect().width;
        const networkHeight = 350;
        
        const networkSvg = networkDiv
            .append('svg')
            .attr('width', networkWidth)
            .attr('height', networkHeight);
        
        const simulation = d3.forceSimulation(networkData.nodes)
            .force('link', d3.forceLink(networkData.links).id(d => d.id))
            .force('charge', d3.forceManyBody().strength(-100))
            .force('center', d3.forceCenter(networkWidth / 2, networkHeight / 2));
        
        const link = networkSvg.append('g')
            .selectAll('line')
            .data(networkData.links)
            .enter().append('line')
            .attr('stroke', '#BDC3C7')
            .attr('stroke-width', 1);
        
        const node = networkSvg.append('g')
            .selectAll('circle')
            .data(networkData.nodes)
            .enter().append('circle')
            .attr('r', d => Math.max(5, d.size / 5))
            .attr('fill', d => d.color)
            .call(d3.drag()
                .on('start', dragstarted)
                .on('drag', dragged)
                .on('end', dragended));
        
        node.append('title')
            .text(d => d.id);
        
        simulation.on('tick', () => {{
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);
            
            node
                .attr('cx', d => d.x)
                .attr('cy', d => d.y);
        }});
        
        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}
        
        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}
        
        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}
        
        // Recent Events List
        const recentEventsDiv = document.getElementById('recentEvents');
        const allEvents = timelineData.flatMap(d => d.details);
        
        allEvents.slice(0, 20).forEach(event => {{
            const eventDiv = document.createElement('div');
            eventDiv.className = 'event-item';
            eventDiv.innerHTML = `
                <div class="event-type">${{event.event_type}}</div>
                <div class="event-details">${{event.node_id}} in ${{event.location}}</div>
                <div class="event-details">${{event.details || ''}}</div>
            `;
            recentEventsDiv.appendChild(eventDiv);
        }});
    </script>
</body>
</html>'''

if __name__ == "__main__":
    generate_web_interface()
