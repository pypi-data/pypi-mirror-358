import argparse
from gitlab.exceptions import GitlabGetError
from gitlab.v4.objects.pipelines import ProjectPipeline, ProjectPipelineJob
from rich.live import Live
from rich.table import Table
from rich.console import Console, Group
from rich.spinner import Spinner
from rich.panel import Panel
import sys

from monitor_gitlab_jobs import (
    get_project,
    get_jobs_until_finished,
    is_success,
    wait_for_pipeline,
)


console = Console()


def format_status(status: str) -> str:
    status_map = {
        "success": ("[green]✅ success[/]"),
        "failed": ("[red]❌ failed[/]"),
        "canceled": ("[yellow]🚫 canceled[/]"),
        "skipped": ("[blue]⏭️ skipped[/]"),
        "manual": ("[magenta]✋ manual[/]"),
        "pending": ("[cyan]🕓 pending[/]"),
        "running": ("[cyan]🏃 running[/]"),
        "created": ("[grey]🛠️ created[/]"),
    }
    return status_map.get(status, f"[white]❔ {status}[/]")


def render_job_status(jobs: list[ProjectPipelineJob]) -> Table:
    table = Table()
    table.add_column("Job", no_wrap=True)
    table.add_column("Status")

    for job in jobs:
        table.add_row(job.name, format_status(job.status))

    return table


def render_jobs_until_finished(live: Live, pipeline: ProjectPipeline, interval=2) -> list[ProjectPipelineJob]:
    for jobs in get_jobs_until_finished(pipeline, interval=interval):
        live.update(
            Group(
                render_job_status(jobs),
                _spinner("waiting for jobs to finish...")
            )
        )
    # print final jobs without spinner
    live.update(render_job_status(jobs))
    return jobs


def _spinner(text: str) -> Spinner:
    return Spinner("dots", text=text, style="status.spinner")


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="monitor Gitlab job statuses on the CLI")
    parser.add_argument("project_id", type=int)
    parser.add_argument("--token")
    parser.add_argument("--ref")
    parser.add_argument("--gitlab_url", default="https://gitlab.com")
    return parser.parse_args()


def main() -> None:
    args = get_args()
    with console.status("fetching project...") as status:
        try:
            project = get_project(
                project_id=args.project_id,
                gitlab_url=args.gitlab_url,
                token=args.token,
            )
        except GitlabGetError as e:
            console.print(f"failed to get gitlab project ({e.error_message})")
            sys.exit(1)

        status.update("waiting for pipeline to be created...")
        pipeline = wait_for_pipeline(project, ref=args.ref)
        if not pipeline:
            console.print(f"[red]Error:[/] no pipeline found for project {args.project_id} @ {args.ref}")
            sys.exit(1)

    with Live(refresh_per_second=12.5) as live:
        final_jobs = render_jobs_until_finished(live, pipeline)

    if all(is_success(job.status) for job in final_jobs):
        console.print("[green]No jobs failed[/]")
        sys.exit()
    else:
        console.print("[red]Error:[/] some jobs failed")
        sys.exit(1)
