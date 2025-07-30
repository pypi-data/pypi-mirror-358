#!/usr/bin/env python3
"""
Example script to test the DependencyTrack MCP Server locally
"""

import os
import asyncio
from dtrack_mcp_server.dtrack_client import initialize_client, dt_client



async def test_mcp_server():
    """Test the MCP server functionality."""
    print("Testing DependencyTrack MCP Server...")
    
    # Check if environment variables are set
    required_vars = ['DTRACK_BASE_URL', 'DTRACK_USERNAME', 'DTRACK_PASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Missing environment variables: {', '.join(missing_vars)}")
        print("\nPlease set the following environment variables:")
        print("export DTRACK_BASE_URL='https://your-dtrack-server.com'")
        print("export DTRACK_USERNAME='your-username'")
        print("export DTRACK_PASSWORD='your-password'")
        return
    
    try:
        # Initialize the client
        await initialize_client()
        print("✓ Successfully connected to DependencyTrack server")
        
        # Test listing projects
        print("\nTesting project listing...")
        projects = dt_client.list_projects(page_size=5)
        print(f"✓ Found {len(projects)} projects (showing first 5)")
        
        for project in projects:
            name = project.get('name', 'Unknown')
            uuid = project.get('uuid', 'Unknown')
            print(f"  - {name} ({uuid})")
        
        # Test search functionality
        if projects:
            print("\nTesting project search...")
            first_project_name = projects[0].get('name', '')
            if first_project_name:
                # Search for projects containing part of the first project's name
                search_term = first_project_name[:5] if len(first_project_name) > 5 else first_project_name
                search_results = dt_client.search_projects(search_term)
                print(f"✓ Search for '{search_term}' found {len(search_results)} projects")
        
        # Test vulnerability assessment
        if projects:
            print("\nTesting vulnerability assessment...")
            test_project = projects[0]
            project_uuid = test_project.get('uuid')
            project_name = test_project.get('name', 'Unknown')
            
            if project_uuid:
                print(f"Getting vulnerabilities for project: {project_name}")
                assessment = dt_client.get_critical_high_vulnerabilities_with_fixes(project_uuid)
                
                print(f"✓ Vulnerability assessment completed:")
                print(f"  - Has Critical/High vulnerabilities: {assessment['has_critical_high_vulns']}")
                print(f"  - Total Critical/High: {assessment['total_critical_high']}")
                print(f"  - Critical: {assessment['critical_count']}")
                print(f"  - High: {assessment['high_count']}")
                
                if assessment['vulnerabilities']:
                    print(f"  - First vulnerability: {assessment['vulnerabilities'][0]['vuln_id']}")
        
        print("\n✓ All tests completed successfully!")
        print("\nYour DependencyTrack MCP Server is ready to use!")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print("\nPlease check:")
        print("1. DependencyTrack server is accessible")
        print("2. Username and password are correct")
        print("3. User has necessary permissions")


if __name__ == "__main__":
    asyncio.run(test_mcp_server()) 