from gitlab import Gitlab
from gitlab.exceptions import GitlabHttpError
from gitlab.v4.objects.projects import Project
from gitlab.v4.objects.pipelines import ProjectPipeline, ProjectPipelineJob
from datetime import datetime
import time
from typing import Generator



def is_finished(status: str) -> bool:
    return status in  [
        "success",
        "failed",
        "skipped",
        "manual",
        "canceled",
    ]


def is_success(status: str) -> bool:
    return status in [
        "success",
        "skipped",
    ]


def get_project(project_id: int, gitlab_url: str, token: str=None) -> Project:
    gl = Gitlab(gitlab_url, private_token=token)
    return gl.projects.get(project_id)


def wait_for_pipeline(project: Project, ref: str, timeout: int=30, interval: int=2) -> ProjectPipeline | None:
    """
    get latest pipeline for `project` at `ref`. if no pipeline exists yet, check every `interval` seconds again.
    times out after `timeout` seconds. returns None on timeout.
    """
    _start_time = datetime.now()
    while timeout > (datetime.now() - _start_time).total_seconds():
        try:
            return project.pipelines.latest(ref=ref)
        except GitlabHttpError:
            time.sleep(interval)


def get_jobs_until_finished(pipeline: ProjectPipeline, interval: int=2) -> Generator[list[ProjectPipelineJob], None, None]:
    """
    yields the jobs of `pipeline` every `interval` seconds until all jobs are finished
    """
    while True:
        _start_time = datetime.now()
        jobs = pipeline.jobs.list()
        yield jobs
        statuses = [j.status for j in jobs]
        if all(is_finished(s) for s in statuses):
            break

        _end_time = datetime.now()
        time.sleep(max(0, interval - (_end_time - _start_time).total_seconds()))
