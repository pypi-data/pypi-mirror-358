# weaver/cli.py

import sys
import click
from weaver.project import Project
from weaver.exceptions import WeaverError
from weaver.config import get_openai_api_key

@click.group()
@click.option(
    "--api-key", "-k",
    help="Your OpenAI API key (overrides env or config file).",
)
@click.pass_context
def cli(ctx, api_key):
    """
    python-weaver CLI.
    """
    # Resolve and stash the key in context
    ctx.ensure_object(dict)
    ctx.obj["OPENAI_API_KEY"] = get_openai_api_key(api_key)

# Then in commands where you call litellm or any SDK, inject ctx.obj["OPENAI_API_KEY"]
# For example:
@cli.command()
@click.argument("project_name")
@click.argument("project_goal")
@click.pass_context

def cli():
    """python-weaver CLI: orchestrate long-duration LLM workflows."""
    pass

@cli.command()
@click.argument("project_name")
@click.argument("project_goal")
def init(project_name: str, project_goal: str):
    """
    Initialize a new weaver project.

    PROJECT_NAME  Name of the project directory to create.
    PROJECT_GOAL  A concise description of the overall project goal.
    """
    try:
        project = Project(project_name, project_goal)
        click.echo(f"[weaver] Initialized project '{project_name}'.")
    except WeaverError as e:
        click.echo(f"[weaver][error] {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument("project_name")
@click.argument("sources", nargs=-1, type=click.Path(exists=True))
def ingest(project_name: str, sources):
    """
    Ingest content into an existing project.

    PROJECT_NAME  Name of the existing project.
    SOURCES       One or more file paths or URLs to ingest.
    """
    try:
        project = Project(project_name)  # loads existing project
        project.ingest(list(sources))
        click.echo(f"[weaver] Ingested {len(sources)} source(s) into '{project_name}'.")
    except WeaverError as e:
        click.echo(f"[weaver][error] {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument("project_name")
def plan(project_name: str):
    """
    Generate a step-by-step plan for an existing project.

    PROJECT_NAME  Name of the existing project.
    """
    try:
        project = Project(project_name)  # loads existing project
        project.plan()
        click.echo(f"[weaver] Plan generated. Review and edit '{project_name}/blueprint.csv' as needed.")
    except WeaverError as e:
        click.echo(f"[weaver][error] {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument("project_name")
@click.option(
    "--no-human-feedback", is_flag=True,
    help="Run without pausing for CSV edits between tasks."
)
@click.option(
    "--steps", default=0, show_default=True,
    help="Number of tasks to run (0 = all pending tasks)."
)
def run(project_name: str, no_human_feedback: bool, steps: int):
    """
    Execute the tasks in the project.

    PROJECT_NAME      Name of the existing project.
    --no-human-feedback  Do not pause for human edits after each task.
    --steps N         Only run N tasks (0 means run all).
    """
    try:
        project = Project(project_name)  # loads existing project
        project.run(
            human_feedback=not no_human_feedback,
            steps=steps
        )
        click.echo(f"[weaver] Execution complete for project '{project_name}'.")
    except WeaverError as e:
        click.echo(f"[weaver][error] {e}", err=True)
        sys.exit(1)

def main():
    cli()

if __name__ == "__main__":
    main()
