import base64
import textwrap
from typing import Annotated

import fastmcp
import git
import pydantic

from bir_mcp.config import get_config
from bir_mcp.utils import filter_dict_by_keys, json_dumps_for_ai

mcp = fastmcp.FastMCP(
    name="Bir MCP server",
    instructions=textwrap.dedent("""
    """),
)


@mcp.tool
def get_git_repository_metadata(
    repositoty_path: Annotated[
        str, pydantic.Field(description="The filesystem path to the repository.")
    ],
) -> str:
    """Retrieves metadata about the Git repository, such as branch names and remote urls."""
    repo = git.Repo(repositoty_path, search_parent_directories=True)
    branch_names = [b.name for b in repo.branches]
    remotes = [{"name": r.name, "urls": list(r.urls)} for r in repo.remotes]
    metadata = {
        "remotes": remotes,
        "branch_names": branch_names,
        "active_branch_name": repo.active_branch.name,
    }
    metadata = json_dumps_for_ai(metadata)
    return metadata


@mcp.tool
def list_all_gitlab_repository_branch_files(
    remote_url: Annotated[
        str,
        pydantic.Field(
            description=textwrap.dedent(f"""
                The remote url of a GitLab repository in the following format:
                "{get_config().gitlab_url}/{{project_path}}/.git"
        """)
        ),
    ],
    branch: Annotated[
        str,
        pydantic.Field(description="The branch to fetch files from."),
    ],
) -> str:
    """Recursively lists all files and directories in the repository."""
    config = get_config()
    project = config.get_gitlab_project_from_url(remote_url)
    tree = project.repository_tree(ref=branch, get_all=True, recursive=True)
    tree = {"files": [{"path": item["path"], "type": item["type"]} for item in tree]}
    tree = json_dumps_for_ai(tree)
    return tree


@mcp.tool
def get_file_content(
    remote_url: Annotated[
        str,
        pydantic.Field(
            description=textwrap.dedent(f"""
                The remote url of a GitLab repository in the following format:
                "{get_config().gitlab_url}/{{project_path}}/.git"
        """)
        ),
    ],
    branch: Annotated[
        str,
        pydantic.Field(description="The branch to fetch files from."),
    ],
    file_path: Annotated[
        str,
        pydantic.Field(description="The path to the file relative to the root of the repository."),
    ],
) -> str:
    """Retrieves the text content of a specific file."""
    config = get_config()
    project = config.get_gitlab_project_from_url(remote_url)
    file = project.files.get(file_path=file_path, ref=branch)
    content = base64.b64decode(file.content).decode()
    return content


@mcp.tool
def search_in_repository(
    remote_url: Annotated[
        str,
        pydantic.Field(
            description=textwrap.dedent(f"""
                The remote url of a GitLab repository in the following format:
                "{get_config().gitlab_url}/{{project_path}}/.git"
        """)
        ),
    ],
    branch: Annotated[
        str,
        pydantic.Field(description="The branch to fetch files from."),
    ],
    query: Annotated[
        str,
        pydantic.Field(description="The text query to search for."),
    ],
) -> str:
    """
    Performs a basic search for a text query within the project's files.
    Doesn't support regex, but is case-insensitive.
    Returns a list of occurences within files, with file path, starting line in the file
    and a snippet of the contextual window in which the query was found.
    For details see the [API docs](https://docs.gitlab.com/api/search/#project-search-api).
    """
    config = get_config()
    project = config.get_gitlab_project_from_url(remote_url)
    results = project.search(
        scope="blobs",
        search=query,
        ref=branch,
    )
    results = [
        {
            "file_path": result["path"],
            "starting_line_in_file": result["startline"],
            "snippet": result["data"],
        }
        for result in results
    ]
    results = json_dumps_for_ai(results)
    return results


@mcp.tool
def get_latest_pipeline_info(
    remote_url: Annotated[
        str,
        pydantic.Field(
            description=textwrap.dedent(f"""
                The remote url of a GitLab repository in the following format:
                "{get_config().gitlab_url}/{{project_path}}/.git"
        """)
        ),
    ],
) -> str:
    """Retrieves the latest pipeline info, such as url, status, duration, commit, jobs, etc."""
    config = get_config()
    project = config.get_gitlab_project_from_url(remote_url)
    pipeline = project.pipelines.latest()

    commit = project.commits.get(pipeline.sha)
    commit = filter_dict_by_keys(
        commit.attributes,
        ["title", "author_name", "web_url"],
    )

    jobs = pipeline.jobs.list(all=True)
    jobs = [
        filter_dict_by_keys(
            job.attributes,
            ["name", "status", "stage", "allow_failure", "web_url"],
        )
        for job in jobs
    ]

    info = {
        "web_url": pipeline.web_url,
        "created_at": config.format_datetime(pipeline.created_at),
        "status": pipeline.status,
        "source": pipeline.source,
        "duration_seconds": pipeline.duration,
        "queued_duration_seconds": pipeline.queued_duration,
        "commit_sha": pipeline.sha,
        "commit": commit,
        "jobs": jobs,
    }
    info = json_dumps_for_ai(info)
    return info


def main():
    mcp.run()


if __name__ == "__main__":
    main()
