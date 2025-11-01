from urllib.parse import parse_qsl, ParseResult


def url_path_parts(parsed_url: ParseResult) -> list[str]:
    return [part for part in parsed_url.path.split("/") if part != ""]


def url_query_dict(parsed_url: ParseResult) -> dict[str, str]:
    return dict(parse_qsl(parsed_url.query))
