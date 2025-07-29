# monitor-gitlab-jobs
Script to observe the status of all jobs in your latest Gitlab pipeline

## Installation
```bash
pip install monitor-gitlab-jobs
```

## Usage

```bash
usage: monitor-gitlab-jobs [-h] [--token TOKEN] [--ref REF] [--gitlab_url GITLAB_URL] project_id

monitor Gitlab job statuses on the CLI

positional arguments:
  project_id

options:
  -h, --help            show this help message and exit
  --token TOKEN
  --ref REF
  --gitlab_url GITLAB_URL
```

## Features
- print a pretty table of all jobs of the latest pipeline (optionally given a ref) and their statuses
- update the table until all jobs are finished
- returns 0 if all jobs are either successful or skipped, 1 otherwise

## Example outputs
```bash
$ monitor-gitlab-jobs 1234 --token $GITLAB_ACCESS_TOKEN --gitlab_url $GITLAB_URL --ref 0.6.4
┏━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Job                      ┃ Status     ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ run_tests                │ ✅ success │
│ build_docker             │ ✅ success │
└──────────────────────────┴────────────┘
No jobs failed
```

```bash
$ monitor-gitlab-jobs 5678 --token $GITLAB_ACCESS_TOKEN --gitlab_url $GITLAB_URL
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Job                       ┃ Status     ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ unit_test                 │ 🏃 running │
│ integration_test          │ 🕓 pending │
│ lint                      │ ✅ success │
│ build                     │ ✅ success │
└───────────────────────────┴────────────┘
⠹ waiting for jobs to finish...
```