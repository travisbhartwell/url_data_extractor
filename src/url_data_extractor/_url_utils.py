from urllib.parse import ParseResult


def url_path_parts(parsed_url: ParseResult) -> list[str]:
    return [part for part in parsed_url.path.split("/") if part != ""]
