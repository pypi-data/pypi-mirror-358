import sys
import click
from weaver.project import Project
from weaver.exceptions import WeaverError
from weaver.config import check_environment, get_missing_credentials

@click.group()
@click.pass_context
def cli(ctx):
    """
    python-weaver CLI: orchestrate long-duration LLM workflows.
    """
    ctx.ensure_object(dict)
    
    # Check environment on startup
    env_error = check_environment()
    if env_error:
        click.echo(f"[weaver][error] {env_error}", err=True)
        click.echo("\nFor setup instructions, see: https://docs.litellm.ai/docs/providers", err=True)
        sys.exit(1)

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

@cli.command()
def check():
    """
    Check credential configuration for all providers.
    """
    missing = get_missing_credentials()
    
    if not missing:
        click.echo("[weaver] ✓ All configured models have valid credentials.")
        return
    
    click.echo("[weaver] Credential status:")
    
    # Show missing credentials
    for provider, creds in missing.items():
        cred_list = " or ".join(creds)
        click.echo(f"  ❌ {provider}: Missing {cred_list}")
    
    # Show available models
    from weaver.config import LLM_CONFIG, validate_model_credentials
    click.echo("\n[weaver] Model availability:")
    
    for model_key in LLM_CONFIG["available_llms"]:
        status = "✓" if validate_model_credentials(model_key) else "❌"
        click.echo(f"  {status} {model_key}")
    
    click.echo("\nFor setup instructions, see: https://docs.litellm.ai/docs/providers")

def main():
    cli()

if __name__ == "__main__":
    main()