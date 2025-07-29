from typing import Protocol

from .types.issues import Issue, IssueAttachment, IssueComment, IssueLink, Worklog


class IssueProtocol(Protocol):
    async def issue_get(self, issue_id: str) -> Issue | None: ...
    async def issue_get_comments(self, issue_id: str) -> list[IssueComment] | None: ...
    async def issues_get_links(self, issue_id: str) -> list[IssueLink] | None: ...
    async def issues_find(
        self,
        query: str,
        *,
        per_page: int = 15,
        page: int = 1,
    ) -> list[Issue]: ...
    async def issue_get_worklogs(self, issue_id: str) -> list[Worklog] | None: ...
    async def issue_get_attachments(
        self, issue_id: str
    ) -> list[IssueAttachment] | None: ...
    async def issues_count(self, query: str) -> int: ...


class IssueProtocolWrap(IssueProtocol):
    def __init__(self, original: IssueProtocol):
        self._original = original
