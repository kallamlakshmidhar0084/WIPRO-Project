from dataclasses import dataclass
from threading import Lock
from uuid import uuid4


@dataclass(frozen=True)
class StoredSnippet:
    snippet_id: str
    code: str
    query: str | None = None


class SnippetStore:
    def __init__(self) -> None:
        self._snippets: dict[str, StoredSnippet] = {}
        self._lock = Lock()

    def create(self, code: str, query: str | None = None) -> StoredSnippet:
        snippet = StoredSnippet(snippet_id=str(uuid4()), code=code, query=query)
        with self._lock:
            self._snippets[snippet.snippet_id] = snippet
        return snippet

    def get(self, snippet_id: str) -> StoredSnippet | None:
        with self._lock:
            return self._snippets.get(snippet_id)


snippet_store = SnippetStore()
