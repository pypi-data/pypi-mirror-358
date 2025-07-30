"""MCP server implementation for Hex API."""

import json
import os
from typing import Any

from fastmcp import FastMCP
from pydantic import BaseModel, Field

from hex_toolkit import HexClient
from hex_toolkit.exceptions import HexAPIError
from hex_toolkit.models.runs import RunStatus


# Pydantic models for tool parameters
class ListProjectsParams(BaseModel):
    """Parameters for listing projects."""

    limit: int = Field(default=25, description="Number of results per page (1-100)")
    include_archived: bool = Field(
        default=False, description="Include archived projects"
    )
    include_trashed: bool = Field(default=False, description="Include trashed projects")
    creator_email: str | None = Field(
        default=None, description="Filter by creator email"
    )
    owner_email: str | None = Field(default=None, description="Filter by owner email")
    search: str | None = Field(
        default=None, description="Search for projects by name or description"
    )


class GetProjectParams(BaseModel):
    """Parameters for getting a project."""

    project_id: str = Field(description="Unique ID for the project")
    include_sharing: bool = Field(
        default=False, description="Include sharing information"
    )


class RunProjectParams(BaseModel):
    """Parameters for running a project."""

    project_id: str = Field(description="Unique ID for the project")
    dry_run: bool = Field(default=False, description="Perform a dry run")
    update_cache: bool = Field(
        default=False, description="Update cached state of published app"
    )
    no_sql_cache: bool = Field(
        default=False, description="Don't use cached SQL results"
    )
    input_params: dict[str, Any] | None = Field(
        default=None, description="JSON object of input parameters"
    )


class RunStatusParams(BaseModel):
    """Parameters for getting run status."""

    project_id: str = Field(description="Unique ID for the project")
    run_id: str = Field(description="Unique ID for the run")


class CancelRunParams(BaseModel):
    """Parameters for canceling a run."""

    project_id: str = Field(description="Unique ID for the project")
    run_id: str = Field(description="Unique ID for the run")


# Initialize FastMCP server
mcp_server = FastMCP("hex-toolkit")


def get_hex_client() -> HexClient:
    """Get an authenticated Hex client instance.

    Returns:
        HexClient: An authenticated client instance.

    Raises:
        ValueError: If HEX_API_KEY environment variable is not set.

    """
    api_key = os.getenv("HEX_API_KEY")
    if not api_key:
        raise ValueError("HEX_API_KEY environment variable not set")

    base_url = os.getenv("HEX_API_BASE_URL")
    return HexClient(api_key=api_key, base_url=base_url)


@mcp_server.tool()
async def hex_list_projects(params: ListProjectsParams) -> dict[str, Any]:
    """List Hex projects with optional filtering and search.

    Returns a list of projects with their metadata including ID, name, status, owner, and timestamps.

    Returns:
        dict[str, Any]: Dictionary containing success status and project list or error message.

    """
    try:
        client = get_hex_client()

        # If searching, we need to fetch all projects and filter
        if params.search:
            all_projects = []
            after_cursor = None
            search_lower = params.search.lower().strip()

            while True:
                response = client.projects.list(
                    limit=100,  # Max for faster fetching
                    include_archived=params.include_archived,
                    include_trashed=params.include_trashed,
                    creator_email=params.creator_email,
                    owner_email=params.owner_email,
                    after=after_cursor,
                )

                page_projects = response.values

                # Filter projects matching search
                for project in page_projects:
                    name = project.title
                    if name:
                        name = name.strip()

                    description = project.description or ""

                    if (search_lower in name.lower()) or (
                        search_lower in description.lower()
                    ):
                        all_projects.append(
                            project.model_dump(exclude_none=True, by_alias=True)
                        )

                # Check for more pages
                pagination = response.pagination
                after_cursor = pagination.after

                if not after_cursor or not page_projects:
                    break

            return {
                "success": True,
                "projects": all_projects,
                "count": len(all_projects),
                "search_query": params.search,
            }
        else:
            # Normal listing without search
            response = client.projects.list(
                limit=params.limit,
                include_archived=params.include_archived,
                include_trashed=params.include_trashed,
                creator_email=params.creator_email,
                owner_email=params.owner_email,
            )

            projects = response.values
            pagination = response.pagination

            return {
                "success": True,
                "projects": [
                    p.model_dump(exclude_none=True, by_alias=True) for p in projects
                ],
                "count": len(projects),
                "has_more": bool(pagination.after),
                "pagination": pagination.model_dump(exclude_none=True, by_alias=True),
            }

    except HexAPIError as e:
        return {"success": False, "error": str(e), "error_type": e.__class__.__name__}
    except Exception as e:
        return {"success": False, "error": str(e), "error_type": "UnexpectedError"}


@mcp_server.tool()
async def hex_get_project(params: GetProjectParams) -> dict[str, Any]:
    """Get detailed metadata about a specific Hex project.

    Returns comprehensive project information including status, timestamps, analytics,
    schedules, and optionally sharing permissions.

    Returns:
        dict[str, Any]: Dictionary containing success status and project data or error message.

    """
    try:
        client = get_hex_client()
        project = client.projects.get(
            params.project_id, include_sharing=params.include_sharing
        )

        return {
            "success": True,
            "project": project.model_dump(exclude_none=True, by_alias=True),
        }

    except HexAPIError as e:
        return {"success": False, "error": str(e), "error_type": e.__class__.__name__}
    except Exception as e:
        return {"success": False, "error": str(e), "error_type": "UnexpectedError"}


@mcp_server.tool()
async def hex_run_project(params: RunProjectParams) -> dict[str, Any]:
    """Trigger a run of the latest published version of a Hex project.

    Returns run information including run ID and URLs to monitor the execution.

    Returns:
        dict[str, Any]: Dictionary containing success status and run information or error message.

    """
    try:
        client = get_hex_client()

        run_info = client.projects.run(
            params.project_id,
            input_params=params.input_params,
            dry_run=params.dry_run,
            update_published_results=params.update_cache,
            use_cached_sql_results=not params.no_sql_cache,
        )

        run_id = run_info.run_id
        run_url = run_info.run_url
        status_url = run_info.run_status_url

        return {
            "success": True,
            "run_id": run_id,
            "run_url": run_url,
            "status_url": status_url,
            "run_info": run_info.model_dump(exclude_none=True, by_alias=True),
        }

    except HexAPIError as e:
        return {"success": False, "error": str(e), "error_type": e.__class__.__name__}
    except Exception as e:
        return {"success": False, "error": str(e), "error_type": "UnexpectedError"}


@mcp_server.tool()
async def hex_get_run_status(params: RunStatusParams) -> dict[str, Any]:
    """Get the current status of a Hex project run.

    Returns status information including state (PENDING, RUNNING, COMPLETED, FAILED, etc.),
    timestamps, and any error messages.

    Returns:
        dict[str, Any]: Dictionary containing success status and run status or error message.

    """
    try:
        client = get_hex_client()
        status = client.runs.get_status(params.project_id, params.run_id)

        return {
            "success": True,
            "status": status.status.value,
            "run_id": status.run_id,
            "project_id": status.project_id,
            "started_at": status.start_time,
            "ended_at": status.end_time,
            "full_status": status.model_dump(exclude_none=True, by_alias=True),
        }

    except HexAPIError as e:
        return {"success": False, "error": str(e), "error_type": e.__class__.__name__}
    except Exception as e:
        return {"success": False, "error": str(e), "error_type": "UnexpectedError"}


@mcp_server.tool()
async def hex_cancel_run(params: CancelRunParams) -> dict[str, Any]:
    """Cancel a running Hex project execution.

    Returns confirmation of the cancellation request.

    Returns:
        dict[str, Any]: Dictionary containing success status and cancellation confirmation or error message.

    """
    try:
        client = get_hex_client()
        client.runs.cancel(params.project_id, params.run_id)

        return {
            "success": True,
            "message": f"Run {params.run_id} cancelled successfully",
            "run_id": params.run_id,
            "project_id": params.project_id,
        }

    except HexAPIError as e:
        return {"success": False, "error": str(e), "error_type": e.__class__.__name__}
    except Exception as e:
        return {"success": False, "error": str(e), "error_type": "UnexpectedError"}


@mcp_server.tool()
async def hex_list_runs(
    project_id: str,
    limit: int = 10,
    offset: int = 0,
    status_filter: str | None = None,
) -> dict[str, Any]:
    """List recent runs for a Hex project.

    Returns a list of runs with their status, timestamps, and duration.

    Returns:
        dict[str, Any]: Dictionary containing success status and runs list or error message.

    """
    try:
        client = get_hex_client()
        response = client.runs.list(
            project_id,
            limit=limit,
            offset=offset,
            status_filter=RunStatus(status_filter) if status_filter else None,
        )

        runs = response.runs
        total_count = len(response.runs)  # ProjectRunsResponse doesn't have totalCount

        return {
            "success": True,
            "runs": [run.model_dump(exclude_none=True, by_alias=True) for run in runs],
            "count": len(runs),
            "total_count": total_count,
            "has_more": total_count > (offset + len(runs)),
        }

    except HexAPIError as e:
        return {"success": False, "error": str(e), "error_type": e.__class__.__name__}
    except Exception as e:
        return {"success": False, "error": str(e), "error_type": "UnexpectedError"}


# Add resources for project information
@mcp_server.resource("projects://list")
async def list_projects_resource() -> str:
    """Get a list of all Hex projects.

    Returns:
        str: Formatted list of projects with their details.

    """
    result = await hex_list_projects(ListProjectsParams())
    if result["success"]:
        projects = result["projects"]
        output = f"Found {len(projects)} projects:\n\n"
        for p in projects:
            name = p.get("title", p.get("name", "Untitled"))
            project_id = p.get("id", p.get("projectId", ""))
            status = p.get("status", {})
            if isinstance(status, dict):
                status = status.get("name", "Unknown")
            output += f"- {name} (ID: {project_id}, Status: {status})\n"
        return output
    else:
        return f"Error: {result['error']}"


@mcp_server.resource("project://{project_id}")
async def get_project_resource(project_id: str) -> str:
    """Get detailed information about a specific project.

    Returns:
        str: Formatted project details including metadata and sharing info.

    """
    result = await hex_get_project(GetProjectParams(project_id=project_id))
    if result["success"]:
        return json.dumps(result["project"], indent=2)
    else:
        return f"Error: {result['error']}"


# Add helpful prompts
@mcp_server.prompt()
async def list_my_projects() -> list[dict[str, str]]:
    """Prompt to list all Hex projects.

    Returns:
        list[dict[str, str]]: List containing the prompt message.

    """
    return [
        {
            "role": "user",
            "content": "List all my Hex projects with their current status",
        }
    ]


@mcp_server.prompt()
async def run_project_prompt() -> list[dict[str, str]]:
    """Prompt to run a Hex project.

    Returns:
        list[dict[str, str]]: List containing the prompt message.

    """
    return [
        {
            "role": "user",
            "content": "I want to run a Hex project. First, list my projects so I can choose which one to run.",
        }
    ]


@mcp_server.prompt()
async def check_running_projects() -> list[dict[str, str]]:
    """Prompt to check on running projects.

    Returns:
        list[dict[str, str]]: List containing the prompt message.

    """
    return [
        {
            "role": "user",
            "content": "Check the status of any currently running Hex projects",
        }
    ]
