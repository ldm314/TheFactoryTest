"""ETag / If-Match concurrency grounding (factory Pattern)."""


def etag_for(version: int | str) -> str:
    return 'W/"v%s"' % (version,)


def if_match_ok(if_match: str | None, etag: str) -> bool:
    if not if_match or if_match.strip() == "*":
        return True
    return etag in {part.strip() for part in if_match.split(",")}
