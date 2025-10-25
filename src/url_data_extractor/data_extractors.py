from url_data_extractor.exceptions import (
    DataElementNotFoundException,
    InvalidBuilderStateException,
    NonMatchingURLException,
)
from url_data_extractor.matchers import URLMatcher
from url_data_extractor._url_utils import url_path_parts

from dataclasses import dataclass, field
from typing import Optional, Protocol, Self
from urllib.parse import ParseResult


class URLDataElementExtractor(Protocol):
    def extract_data_element(self, parsed_url: ParseResult) -> str: ...


@dataclass
class URLDataExtractor:
    url_matcher: URLMatcher
    element_extractors: dict[str, URLDataElementExtractor]

    def extract_url_data(self, parsed_url: ParseResult) -> Optional[dict[str, str]]:
        if not self.url_matcher.match_url(parsed_url):
            raise NonMatchingURLException(f"'{parsed_url.geturl()}' is not a matching URL.")

        return {
            element_name: element_extractor.extract_data_element(parsed_url)
            for (element_name, element_extractor) in self.element_extractors.items()
        }

    @dataclass
    class Builder:
        url_matcher: Optional[URLMatcher] = None
        element_extractors: dict[str, URLDataElementExtractor] = field(default_factory=dict)

        def with_url_matcher(self, url_matcher: URLMatcher) -> Self:
            self.url_matcher = url_matcher
            return self

        def with_data_element_extractor(
            self, element_name: str, element_extractor: URLDataElementExtractor
        ) -> Self:
            self.element_extractors[element_name] = element_extractor
            return self

        def build(self) -> URLDataExtractor:
            if self.url_matcher is None:
                raise InvalidBuilderStateException(
                    "Cannot build a URLDataExtractor instance, no URL matcher set."
                )

            if not self.element_extractors:
                raise InvalidBuilderStateException(
                    "Cannot build a URLDataExtractor instance, no URLDataElementExtractors set."
                )

            return URLDataExtractor(self.url_matcher, self.element_extractors)


@dataclass
class PathPartDataExtractor(URLDataElementExtractor):
    path_index: int

    def extract_data_element(self, parsed_url: ParseResult) -> str:
        parts = url_path_parts(parsed_url)
        parts_count = len(parts)

        index = self.path_index
        if index < 0:
            index = parts_count + index

        if index >= parts_count:
            raise DataElementNotFoundException("Attempting to retrieve path part out of bounds.")

        return parts[index]
