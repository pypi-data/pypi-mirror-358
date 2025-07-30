import datetime
import functools
import os
import zoneinfo

import gitlab
import pydantic


class Config(pydantic.BaseModel, frozen=True):
    gitlab_url: str = "https://gitlab.kapitalbank.az"
    gitlab_private_token: str | None = None
    jira_api_key: str | None = None
    timezone_name: str = "Asia/Baku"

    @property
    def timezone(self) -> zoneinfo.ZoneInfo:
        return zoneinfo.ZoneInfo(self.timezone_name)

    @functools.cache
    def get_gitlab_client(self) -> gitlab.Gitlab:
        if not self.gitlab_private_token:
            raise ValueError("Gitlab private token is not set, cannot connect to Gitlab.")

        client = gitlab.Gitlab(
            url=self.gitlab_url,
            private_token=self.gitlab_private_token,
        )
        client.auth()
        return client

    def extract_gitlab_project_path_from_remote_url(self, url: str) -> str:
        url = url.removeprefix(self.gitlab_url)
        url = url.removesuffix(".git")
        url = url.strip("/")
        return url

    def get_gitlab_project_from_url(self, remote_url: str):
        project_path = self.extract_gitlab_project_path_from_remote_url(remote_url)
        client = self.get_gitlab_client()
        project = client.projects.get(project_path)
        return project

    def format_datetime(self, date: datetime.datetime | str, timespec: str = "seconds") -> str:
        date = datetime.datetime.fromisoformat(date) if isinstance(date, str) else date
        date = date.astimezone(self.timezone)
        date = date.isoformat(timespec=timespec, sep=" ")
        return date


@functools.cache
def get_config():
    config = Config(
        gitlab_private_token=os.getenv("GITLAB_PRIVATE_TOKEN"),
        jira_api_key=os.getenv("JIRA_API_KEY"),
    )
    return config
