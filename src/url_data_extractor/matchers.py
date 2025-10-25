from dataclasses import dataclass, field
from typing import Protocol, Self
from urllib.parse import ParseResult

from url_data_extractor.exceptions import InvalidBuilderStateException
from url_data_extractor._url_utils import url_path_parts

class URLMatcher(Protocol):
    def match_url(self, parsed_url: ParseResult) -> bool: ...


@dataclass(frozen=True)
class CompoundMatcher(URLMatcher):
    matchers: list[URLMatcher]

    def match_url(self, parsed_url: URLMatcher) -> bool:
        if not self.matchers:
            return False

        return all([matcher.match_url(parsed_url) for matcher in self.matchers])

    @dataclass
    class Builder:
        matchers: list[URLMatcher] = field(default_factory=list)

        def with_matcher(self, matcher: URLMatcher) -> Self:
            self.matchers.append(matcher)
            return self

        def build(self) -> CompoundMatcher:
            if not self.matchers:
                raise InvalidBuilderStateException(
                    "Cannot build a CompoundMatcher instance, no matchers set."
                )

            return CompoundMatcher(self.matchers)


@dataclass
class HostMatcher(URLMatcher):
    host: str

    def match_url(self, parsed_url: ParseResult) -> bool:
        return parsed_url.hostname == self.host


@dataclass(frozen=True)
class PathPartsMatcher(URLMatcher):
    values_by_index: dict[int, str]

    def match_url(self, parsed_url: ParseResult) -> bool:
        parts = url_path_parts(parsed_url) 
        parts_count = len(parts)

        if not parts_count:
            return False

        values_to_match_dict = self.get_values_to_match_dict(parts_count)

        for index, value in values_to_match_dict.items():
            if index >= parts_count:
                return False

            if parts[index] != value:
                return False

        return True

    def get_values_to_match_dict(self, parts_count: int) -> dict[int, str]:
        values_to_match_dict = {}

        for index, value in self.values_by_index.items():
            if index < 0:
                index = parts_count + index
            values_to_match_dict[index] = value

        return values_to_match_dict

    @dataclass
    class Builder:
        values_by_index: dict[int, str] = field(default_factory=dict)

        def with_value_at_index(self, index: int, value: str) -> Self:
            self.values_by_index[index] = value
            return self

        def build(self) -> PathPartsMatcher:
            if not self.values_by_index:
                raise InvalidBuilderStateException(
                    "Cannot build a PathPartsMatcher instnace, no values at index matchers defined."
                )

            return PathPartsMatcher(self.values_by_index)
