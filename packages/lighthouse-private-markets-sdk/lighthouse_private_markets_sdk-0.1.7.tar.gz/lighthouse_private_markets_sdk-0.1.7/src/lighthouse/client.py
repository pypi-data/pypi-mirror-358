from json import JSONDecodeError
from typing import Any, Dict, Iterable, Literal, Optional, Tuple, TypeVar, Union

import requests
from httpx import Client as HttpClient
from postgrest import APIError, APIResponse, SyncPostgrestClient
from postgrest.exceptions import APIError, generate_default_error_message
from pydantic import ValidationError

_ReturnT = TypeVar("_ReturnT")


class LighthouseFilterQuery:
    """Query builder after select() has been called."""

    def __init__(self, query_builder, lighthouse):
        self._query = query_builder
        self._lighthouse = lighthouse  # Store reference to parent

    def single(self):
        """Request a single record."""
        result = self._query.single()
        return LighthouseFilterQuery(result, self._lighthouse)

    def eq(self, column: str, value: Any):
        """Equal to filter."""
        result = self._query.eq(column, value)
        return LighthouseFilterQuery(result, self._lighthouse)

    def neq(self, column: str, value: Any):
        """Not equal to filter."""
        result = self._query.neq(column, value)
        return LighthouseFilterQuery(result, self._lighthouse)

    def gt(self, column: str, value: Any):
        """Greater than filter."""
        result = self._query.gt(column, value)
        return LighthouseFilterQuery(result, self._lighthouse)

    def lt(self, column: str, value: Any):
        """Less than filter."""
        result = self._query.lt(column, value)
        return LighthouseFilterQuery(result, self._lighthouse)

    def gte(self, column: str, value: Any):
        """Greater than or equal to filter."""
        result = self._query.gte(column, value)
        return LighthouseFilterQuery(result, self._lighthouse)

    def lte(self, column: str, value: Any):
        """Less than or equal to filter."""
        result = self._query.lte(column, value)
        return LighthouseFilterQuery(result, self._lighthouse)

    def order(
        self,
        column: str,
        *,
        desc: bool = False,
        nullsfirst: bool = False,
        foreign_table: Optional[str] = None,
    ):
        """Sort the returned rows in some specific order."""
        result = self._query.order(
            column, desc=desc, nullsfirst=nullsfirst, foreign_table=foreign_table
        )
        return LighthouseFilterQuery(result, self._lighthouse)

    def limit(self, size: int, *, foreign_table: Optional[str] = None):
        """Limit the number of rows returned."""
        result = self._query.limit(size, foreign_table=foreign_table)
        return LighthouseFilterQuery(result, self._lighthouse)

    def range(self, start: int, end: int, foreign_table: Optional[str] = None):
        """Get a range of rows."""
        result = self._query.range(start, end, foreign_table=foreign_table)
        return LighthouseFilterQuery(result, self._lighthouse)

    def offset(self, size: int):
        """Set the starting row index."""
        result = self._query.offset(size)
        return LighthouseFilterQuery(result, self._lighthouse)

    def is_(self, column: str, value: Any):
        """An 'is' filter."""
        result = self._query.is_(column, value)
        return LighthouseFilterQuery(result, self._lighthouse)

    def in_(self, column: str, values: Iterable[Any]):
        """An 'in' filter."""
        result = self._query.in_(column, values)
        return LighthouseFilterQuery(result, self._lighthouse)

    def contains(self, column: str, value: Union[Iterable[Any], str, Dict[Any, Any]]):
        """A 'contains' filter."""
        result = self._query.contains(column, value)
        return LighthouseFilterQuery(result, self._lighthouse)

    def contained_by(
        self, column: str, value: Union[Iterable[Any], str, Dict[Any, Any]]
    ):
        """A 'contained by' filter."""
        result = self._query.contained_by(column, value)
        return LighthouseFilterQuery(result, self._lighthouse)

    def like(self, column: str, pattern: str):
        """A 'LIKE' filter."""
        result = self._query.like(column, pattern)
        return LighthouseFilterQuery(result, self._lighthouse)

    def ilike(self, column: str, pattern: str):
        """An 'ILIKE' filter (case insensitive)."""
        result = self._query.ilike(column, pattern)
        return LighthouseFilterQuery(result, self._lighthouse)

    def match(self, query: Dict[str, Any]):
        """Match multiple columns."""
        result = self._query.match(query)
        return LighthouseFilterQuery(result, self._lighthouse)

    def not_(self):
        """Negate the next filter."""
        result = self._query.not_
        return LighthouseFilterQuery(result, self._lighthouse)

    def or_(self, filters: str, reference_table: Union[str, None] = None):
        """An 'or' filter."""
        result = self._query.or_(filters, reference_table)
        return LighthouseFilterQuery(result, self._lighthouse)

    def filter(self, column: str, operator: str, criteria: str):
        """Apply a custom filter."""
        result = self._query.filter(column, operator, criteria)
        return LighthouseFilterQuery(result, self._lighthouse)

    def csv(self):
        """Return results as CSV."""
        result = self._query.csv()
        return LighthouseFilterQuery(result, self._lighthouse)

    def explain(
        self,
        analyze: bool = False,
        verbose: bool = False,
        settings: bool = False,
        buffers: bool = False,
        wal: bool = False,
        format: Literal["text", "json"] = "text",
    ):
        """Get query explanation."""
        result = self._query.explain(analyze, verbose, settings, buffers, wal, format)
        return LighthouseFilterQuery(result, self._lighthouse)

    def execute(self) -> APIResponse[_ReturnT]:
        """Execute with custom handling."""
        # Build the URL from the query
        url = f"{self._lighthouse.DEFAULT_URL}/rest/v1{self._query.path}?{self._query.params}"

        # Make request to the custom API endpoint using the main session
        r = self._lighthouse.session.post(  # Use the parent's session
            f"{self._lighthouse.DEFAULT_URL}/functions/v1/custom_api_request",
            json={"url": url, "method": "GET"},
        )

        response_data = r.json()

        try:
            if r.status_code == 200:
                if isinstance(response_data, dict) and "data" in response_data:
                    return APIResponse[_ReturnT](data=response_data["data"])
                else:
                    return APIResponse[_ReturnT](data=response_data)
            else:
                raise APIError({"message": r.text})
        except ValidationError as e:
            raise APIError({"message": str(e)})
        except JSONDecodeError as e:
            raise APIError({"message": f"Failed to parse response: {r.text}"})

    def like_all_of(self, column: str, pattern: str):
        """A 'LIKE' filter for pattern matching."""
        result = self._query.like_all_of(column, pattern)
        return LighthouseFilterQuery(result, self._lighthouse)

    def like_any_of(self, column: str, pattern: str):
        """A 'LIKE' filter for pattern matching."""
        result = self._query.like_any_of(column, pattern)
        return LighthouseFilterQuery(result, self._lighthouse)

    def ilike_all_of(self, column: str, pattern: str):
        """An 'ILIKE' filter for pattern matching (case insensitive)."""
        result = self._query.ilike_all_of(column, pattern)
        return LighthouseFilterQuery(result, self._lighthouse)

    def ilike_any_of(self, column: str, pattern: str):
        """An 'ILIKE' filter for pattern matching (case insensitive)."""
        result = self._query.ilike_any_of(column, pattern)
        return LighthouseFilterQuery(result, self._lighthouse)

    def fts(self, column: str, query: Any):
        """Full text search filter."""
        result = self._query.fts(column, query)
        return LighthouseFilterQuery(result, self._lighthouse)

    def plfts(self, column: str, query: Any):
        """Plain full text search filter."""
        result = self._query.plfts(column, query)
        return LighthouseFilterQuery(result, self._lighthouse)

    def phfts(self, column: str, query: Any):
        """Phrase full text search filter."""
        result = self._query.phfts(column, query)
        return LighthouseFilterQuery(result, self._lighthouse)

    def wfts(self, column: str, query: Any):
        """Websearch full text search filter."""
        result = self._query.wfts(column, query)
        return LighthouseFilterQuery(result, self._lighthouse)

    def cs(self, column: str, values: Iterable[Any]):
        """Contains filter."""
        result = self._query.cs(column, values)
        return LighthouseFilterQuery(result, self._lighthouse)

    def cd(self, column: str, values: Iterable[Any]):
        """Contained by filter."""
        result = self._query.cd(column, values)
        return LighthouseFilterQuery(result, self._lighthouse)

    def ov(self, column: str, value: Iterable[Any]):
        """Overlaps filter."""
        result = self._query.ov(column, value)
        return LighthouseFilterQuery(result, self._lighthouse)

    def sl(self, column: str, range: Tuple[int, int]):
        """Strictly left of range."""
        result = self._query.sl(column, range)
        return LighthouseFilterQuery(result, self._lighthouse)

    def sr(self, column: str, range: Tuple[int, int]):
        """Strictly right of range."""
        result = self._query.sr(column, range)
        return LighthouseFilterQuery(result, self._lighthouse)

    def nxl(self, column: str, range: Tuple[int, int]):
        """Not extending left of range."""
        result = self._query.nxl(column, range)
        return LighthouseFilterQuery(result, self._lighthouse)

    def nxr(self, column: str, range: Tuple[int, int]):
        """Not extending right of range."""
        result = self._query.nxr(column, range)
        return LighthouseFilterQuery(result, self._lighthouse)

    def adj(self, column: str, range: Tuple[int, int]):
        """Adjacent to range."""
        result = self._query.adj(column, range)
        return LighthouseFilterQuery(result, self._lighthouse)

    def overlaps(self, column: str, values: Iterable[Any]):
        """Overlaps with values."""
        result = self._query.overlaps(column, values)
        return LighthouseFilterQuery(result, self._lighthouse)

    def maybe_single(self):
        """Retrieves at most one row from the result."""
        result = self._query.maybe_single()
        return LighthouseFilterQuery(result, self._lighthouse)

    def range_gt(self, column: str, range: Tuple[int, int]):
        """Greater than range filter."""
        result = self._query.range_gt(column, range)
        return LighthouseFilterQuery(result, self._lighthouse)

    def range_gte(self, column: str, range: Tuple[int, int]):
        """Greater than or equal to range filter."""
        result = self._query.range_gte(column, range)
        return LighthouseFilterQuery(result, self._lighthouse)

    def range_lt(self, column: str, range: Tuple[int, int]):
        """Less than range filter."""
        result = self._query.range_lt(column, range)
        return LighthouseFilterQuery(result, self._lighthouse)

    def range_lte(self, column: str, range: Tuple[int, int]):
        """Less than or equal to range filter."""
        result = self._query.range_lte(column, range)
        return LighthouseFilterQuery(result, self._lighthouse)

    def range_adjacent(self, column: str, range: Tuple[int, int]):
        """Adjacent to range filter."""
        result = self._query.range_adjacent(column, range)
        return LighthouseFilterQuery(result, self._lighthouse)


class LighthouseSelectQuery:
    """Query builder after from_() but before select()."""

    def __init__(self, query_builder, lighthouse):
        self._query = query_builder
        self._lighthouse = lighthouse

    def select(self, *columns: str):
        """Select specific columns to return."""
        result = self._query.select(*columns)
        return LighthouseFilterQuery(result, self._lighthouse)


class Lighthouse:
    DEFAULT_URL = "https://api.trylighthouse.vc"

    def __init__(self, api_key: str):
        """Initialize the Lighthouse client."""
        self.api_key = api_key

        # Common headers for all requests
        self.headers = {
            "x-lighthouse-app-id": api_key,
            "apiKey": "sb_publishable_LuLdStPgW5jyNfVSv_oIFA__86JWQSR",
            "Content-Type": "application/json",
        }

        # Create a single session for all requests
        self.session = requests.Session()
        self.session.headers.update(self.headers)

        # PostgREST client for query building
        self.postgrest = SyncPostgrestClient(
            f"{self.DEFAULT_URL}/rest/v1", headers=self.headers
        )

    def from_(self, table: str):
        """Get query builder with custom execute."""
        return LighthouseSelectQuery(self.postgrest.from_(table), self)
