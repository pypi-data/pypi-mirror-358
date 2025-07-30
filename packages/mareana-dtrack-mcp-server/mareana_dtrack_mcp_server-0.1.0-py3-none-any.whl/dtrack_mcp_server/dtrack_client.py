"""
DependencyTrack MCP Server
Provides AI assistants with vulnerability assessment capabilities for CI/CD pipelines
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional, Sequence
from urllib.parse import urlparse

import requests
from mcp.server import Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
from pydantic import BaseModel, Field


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DependencyTrackClient:
    """
    DependencyTrack API client focused on vulnerability assessment for CI/CD pipelines.
    Only handles Critical & High severity vulnerabilities.
    """
    
    def __init__(self, base_url: str, username: str, password: str):
        """Initialize DependencyTrack client."""
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api/v1"
        
        # Initialize session
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        
        # Login and get Bearer token
        token = self._login(username, password)
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        logger.info("Successfully connected to DependencyTrack server")
    
    def _login(self, username: str, password: str) -> str:
        """Login to DependencyTrack and get Bearer token."""
        try:
            response = self.session.post(
                f"{self.api_url}/user/login",
                data={"username": username, "password": password},
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "*/*"
                },
                timeout=10
            )
            response.raise_for_status()
            return response.text.strip()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to login to DependencyTrack server: {e}")
            raise ConnectionError(f"Failed to login to DependencyTrack server: {e}")
    
    def _get(self, endpoint: str, params: Dict[str, Any] = None) -> Any:
        """Make GET request to DependencyTrack API."""
        url = f"{self.api_url}{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise Exception(f"API request failed: {e}")
    
    def search_projects(self, query: str) -> List[Dict[str, Any]]:
        """Universal project search with automatic pattern detection."""
        # Auto-detect if wildcards are used
        if '%' in query:
            # Use SQL LIKE pattern search
            all_projects = self.list_projects(fetch_all=True)
            
            # Convert SQL LIKE pattern to Python regex-like matching
            if query.startswith('%') and query.endswith('%'):
                # %pattern% - contains
                search_term = query[1:-1].lower()
                return [p for p in all_projects if search_term in p.get('name', '').lower()]
            elif query.startswith('%'):
                # %pattern - ends with
                search_term = query[1:].lower()
                return [p for p in all_projects if p.get('name', '').lower().endswith(search_term)]
            elif query.endswith('%'):
                # pattern% - starts with
                search_term = query[:-1].lower()
                return [p for p in all_projects if p.get('name', '').lower().startswith(search_term)]
        
        # Simple contains search (no wildcards)
        all_projects = self.list_projects(fetch_all=True)
        query_lower = query.lower()
        return [p for p in all_projects if query_lower in p.get('name', '').lower()]
    
    def list_projects(self, fetch_all: bool = False, page_size: int = 100) -> List[Dict[str, Any]]:
        """List all projects with pagination support."""
        if not fetch_all:
            return self._get("/project", params={"limit": page_size})
        
        # Fetch all projects with pagination
        all_projects = []
        offset = 0
        
        while True:
            params = {"limit": page_size, "offset": offset}
            projects = self._get("/project", params=params)
            
            if not projects:
                break
                
            all_projects.extend(projects)
            
            # If we got fewer projects than the page size, we've reached the end
            if len(projects) < page_size:
                break
                
            offset += page_size
        
        return all_projects
    
    def get_project_vulnerabilities(self, project_uuid: str, critical_high_only: bool = True, suppress_inactive: bool = True) -> List[Dict[str, Any]]:
        """Get vulnerabilities for a specific project."""
        params = {}
        if suppress_inactive:
            params['suppressed'] = 'false'
        
        vulnerabilities = self._get(f"/vulnerability/project/{project_uuid}", params=params)
        
        if critical_high_only:
            # Filter to only Critical and High severity
            filtered_vulns = []
            for vuln in vulnerabilities:
                severity = vuln.get('severity', '').upper()
                if severity in ['CRITICAL', 'HIGH']:
                    filtered_vulns.append(vuln)
            return filtered_vulns
        
        return vulnerabilities
    
    def get_vulnerability_details(self, vulnerability_uuid: str) -> Dict[str, Any]:
        """Get detailed information about a specific vulnerability."""
        return self._get(f"/vulnerability/{vulnerability_uuid}")
    
    def get_critical_high_vulnerabilities_with_fixes(self, project_uuid: str) -> Dict[str, Any]:
        """Get Critical & High vulnerabilities for Jenkins pipeline assessment."""
        # Get only Critical & High vulnerabilities
        vulnerabilities = self.get_project_vulnerabilities(project_uuid, critical_high_only=True)
        
        result = {
            'project_uuid': project_uuid,
            'has_critical_high_vulns': len(vulnerabilities) > 0,
            'total_critical_high': len(vulnerabilities),
            'critical_count': 0,
            'high_count': 0,
            'vulnerabilities': []
        }
        
        for vuln in vulnerabilities:
            severity = vuln.get('severity', '').upper()
            if severity == 'CRITICAL':
                result['critical_count'] += 1
            elif severity == 'HIGH':
                result['high_count'] += 1
            
            # Get components affected
            components = vuln.get('components', [])
            component_info = []
            for comp in components:
                component_info.append({
                    'name': comp.get('name', 'Unknown'),
                    'version': comp.get('version', 'Unknown'),
                    'purl': comp.get('purl', '')
                })
            
            # Try to get fix information
            fix_available = False
            fix_info = "No fix information available"
            
            vuln_uuid = vuln.get('uuid')
            if vuln_uuid:
                try:
                    vuln_details = self.get_vulnerability_details(vuln_uuid)
                    
                    # Check for fix information
                    if vuln_details.get('patchedVersions'):
                        fix_available = True
                        fix_info = f"Patched versions: {vuln_details.get('patchedVersions')}"
                    elif vuln_details.get('recommendation'):
                        fix_available = True
                        fix_info = vuln_details.get('recommendation')
                    else:
                        # Check references for fix hints
                        references = vuln_details.get('references', '')
                        if 'patch' in references.lower() or 'fix' in references.lower():
                            fix_available = True
                            fix_info = "Check references for fix information"
                            
                except Exception as e:
                    # Ignore detailed vulnerability fetch errors for MCP
                    logger.warning(f"Failed to get detailed vulnerability info: {e}")
            
            vuln_summary = {
                'vuln_id': vuln.get('vulnId', 'Unknown'),
                'severity': severity,
                'cvss_score': vuln.get('cvssV3BaseScore') or vuln.get('cvssV2BaseScore', 'N/A'),
                'description': vuln.get('description', '')[:200] + '...' if len(vuln.get('description', '')) > 200 else vuln.get('description', ''),
                'components': component_info,
                'fix_available': fix_available,
                'fix_info': fix_info,
                'published': vuln.get('published', ''),
                'cwe': vuln.get('cwe', {}).get('name', '') if vuln.get('cwe') else ''
            }
            
            result['vulnerabilities'].append(vuln_summary)
        
        return result


# Global DependencyTrack client instance
dt_client: Optional[DependencyTrackClient] = None


async def initialize_client():
    """Initialize the DependencyTrack client from environment variables."""
    global dt_client
    
    base_url = os.getenv('DTRACK_BASE_URL')
    username = os.getenv('DTRACK_USERNAME')
    password = os.getenv('DTRACK_PASSWORD')
    
    if not all([base_url, username, password]):
        raise ValueError(
            "Missing required environment variables: DTRACK_BASE_URL, DTRACK_USERNAME, DTRACK_PASSWORD"
        )
    
    try:
        dt_client = DependencyTrackClient(base_url, username, password)
        logger.info("DependencyTrack client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize DependencyTrack client: {e}")
        raise


# Initialize MCP Server
server = Server("dtrack-mcp-server")


@server.list_resources()
async def list_resources() -> list[Resource]:
    """List available resources."""
    return [
        Resource(
            uri="dtrack://projects",
            name="DependencyTrack Projects",
            description="List of all projects in DependencyTrack",
            mimeType="application/json"
        ),
        Resource(
            uri="dtrack://vulnerabilities",
            name="Critical & High Vulnerabilities",
            description="All critical and high severity vulnerabilities across projects",
            mimeType="application/json"
        )
    ]


@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read a specific resource."""
    if dt_client is None:
        await initialize_client()
    
    if uri == "dtrack://projects":
        projects = dt_client.list_projects(fetch_all=True)
        return json.dumps({
            "projects": projects,
            "total_count": len(projects)
        }, indent=2)
    
    elif uri == "dtrack://vulnerabilities":
        # Get all projects and their critical/high vulnerabilities
        projects = dt_client.list_projects(fetch_all=True)
        all_vulnerabilities = []
        
        for project in projects[:10]:  # Limit to first 10 projects to avoid timeout
            try:
                project_vulns = dt_client.get_critical_high_vulnerabilities_with_fixes(project['uuid'])
                if project_vulns['has_critical_high_vulns']:
                    project_vulns['project_name'] = project['name']
                    all_vulnerabilities.append(project_vulns)
            except Exception as e:
                logger.warning(f"Failed to get vulnerabilities for project {project['name']}: {e}")
        
        return json.dumps({
            "vulnerable_projects": all_vulnerabilities,
            "total_vulnerable_projects": len(all_vulnerabilities)
        }, indent=2)
    
    raise ValueError(f"Unknown resource: {uri}")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="search_projects",
            description="Search for projects in DependencyTrack by name. Supports wildcards (% for SQL LIKE patterns). Examples: 'admin%' (starts with), '%service' (ends with), 'admin' (contains)",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query - supports wildcards (% for SQL LIKE patterns)"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="list_projects",
            description="List all projects in DependencyTrack with optional pagination",
            inputSchema={
                "type": "object",
                "properties": {
                    "fetch_all": {
                        "type": "boolean",
                        "description": "If true, fetches all projects across all pages",
                        "default": False
                    },
                    "page_size": {
                        "type": "integer",
                        "description": "Number of projects per page",
                        "default": 100
                    }
                }
            }
        ),
        Tool(
            name="get_project_vulnerabilities",
            description="Get vulnerabilities for a specific project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_uuid": {
                        "type": "string",
                        "description": "UUID of the project"
                    },
                    "critical_high_only": {
                        "type": "boolean",
                        "description": "If true, returns only CRITICAL and HIGH severity vulnerabilities",
                        "default": True
                    },
                    "suppress_inactive": {
                        "type": "boolean",
                        "description": "If true, only returns active vulnerabilities",
                        "default": True
                    }
                },
                "required": ["project_uuid"]
            }
        ),
        Tool(
            name="get_vulnerability_assessment",
            description="Get Critical & High vulnerabilities for a project with fix information - ideal for CI/CD pipeline assessment",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_uuid": {
                        "type": "string",
                        "description": "UUID of the project"
                    }
                },
                "required": ["project_uuid"]
            }
        ),
        Tool(
            name="get_vulnerability_details",
            description="Get detailed information about a specific vulnerability",
            inputSchema={
                "type": "object",
                "properties": {
                    "vulnerability_uuid": {
                        "type": "string",
                        "description": "UUID of the vulnerability"
                    }
                },
                "required": ["vulnerability_uuid"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute a tool call."""
    if dt_client is None:
        await initialize_client()
    
    try:
        if name == "search_projects":
            query = arguments.get("query", "")
            if not query:
                return [TextContent(type="text", text="Error: Query parameter is required")]
            
            projects = dt_client.search_projects(query)
            result = {
                "query": query,
                "projects": projects,
                "total_found": len(projects)
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "list_projects":
            fetch_all = arguments.get("fetch_all", False)
            page_size = arguments.get("page_size", 100)
            
            projects = dt_client.list_projects(fetch_all=fetch_all, page_size=page_size)
            result = {
                "projects": projects,
                "total_count": len(projects),
                "fetch_all": fetch_all,
                "page_size": page_size
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_project_vulnerabilities":
            project_uuid = arguments.get("project_uuid")
            if not project_uuid:
                return [TextContent(type="text", text="Error: project_uuid parameter is required")]
            
            critical_high_only = arguments.get("critical_high_only", True)
            suppress_inactive = arguments.get("suppress_inactive", True)
            
            vulnerabilities = dt_client.get_project_vulnerabilities(
                project_uuid, critical_high_only, suppress_inactive
            )
            
            result = {
                "project_uuid": project_uuid,
                "vulnerabilities": vulnerabilities,
                "total_count": len(vulnerabilities),
                "critical_high_only": critical_high_only,
                "suppress_inactive": suppress_inactive
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_vulnerability_assessment":
            project_uuid = arguments.get("project_uuid")
            if not project_uuid:
                return [TextContent(type="text", text="Error: project_uuid parameter is required")]
            
            assessment = dt_client.get_critical_high_vulnerabilities_with_fixes(project_uuid)
            return [TextContent(type="text", text=json.dumps(assessment, indent=2))]
        
        elif name == "get_vulnerability_details":
            vulnerability_uuid = arguments.get("vulnerability_uuid")
            if not vulnerability_uuid:
                return [TextContent(type="text", text="Error: vulnerability_uuid parameter is required")]
            
            details = dt_client.get_vulnerability_details(vulnerability_uuid)
            return [TextContent(type="text", text=json.dumps(details, indent=2))]
        
        else:
            return [TextContent(type="text", text=f"Error: Unknown tool '{name}'")]
    
    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Run the MCP server."""
    # Don't initialize client on startup - do it lazily when needed
    logger.info("Starting DependencyTrack MCP server (lazy initialization)")
    
    # Import here to avoid issues with uvloop on some systems
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())