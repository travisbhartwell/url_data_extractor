from dataclasses import dataclass, field
from typing import Protocol, Self
from urllib.parse import parse_qs, ParseResult

from url_data_extractor.exceptions import InvalidBuilderStateException
from url_data_extractor._url_utils import url_path_parts


class URLMatcher(Protocol):
    def match_url(self, parsed_url: ParseResult) -> bool: ...


class StringMatcherCallable(Protocol):
    def __call__(self, value: str) -> bool: ...


@dataclass(frozen=True)
class CompoundMatcher(URLMatcher):
    matchers: list[URLMatcher]

    def match_url(self, parsed_url: ParseResult) -> bool:
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
    string_matcher: StringMatcherCallable

    def match_url(self, parsed_url: ParseResult) -> bool:
        hostname = parsed_url.hostname
        if hostname is None:
            return False

        return self.string_matcher(hostname)

    @classmethod
    def hostname_equals_matcher(cls, hostname: str) -> HostMatcher:
        return HostMatcher(lambda url_hostname: hostname == url_hostname)


@dataclass(frozen=True)
class PathPartsMatcher(URLMatcher):
    matchers_by_index: dict[int, StringMatcherCallable]

    def match_url(self, parsed_url: ParseResult) -> bool:
        parts = url_path_parts(parsed_url)
        parts_count = len(parts)

        if not parts_count:
            return False

        index_matchers = self._get_index_matchers_dict(parts_count)

        for index, matcher in index_matchers.items():
            if index >= parts_count:
                return False

            if not matcher(parts[index]):
                return False

        return True

    def _get_index_matchers_dict(self, parts_count: int) -> dict[int, StringMatcherCallable]:
        index_matchers = {}

        for index, matcher in self.matchers_by_index.items():
            if index < 0:
                index = parts_count + index
            index_matchers[index] = matcher

        return index_matchers

    @dataclass
    class Builder:
        matchers_by_index: dict[int, StringMatcherCallable] = field(default_factory=dict)

        def with_matcher_at_index(self, index: int, matcher: StringMatcherCallable) -> Self:
            self.matchers_by_index[index] = matcher
            return self

        def with_value_at_index(self, index: int, value: str) -> Self:
            return self.with_matcher_at_index(index, lambda x: x == value)

        def build(self) -> PathPartsMatcher:
            if not self.matchers_by_index:
                raise InvalidBuilderStateException(
                    "Cannot build a PathPartsMatcher instnace, no values at index matchers defined."
                )

            return PathPartsMatcher(self.matchers_by_index)


@dataclass
class URLFragmentStringMatcher(URLMatcher):
    string_matcher: StringMatcherCallable

    def match_url(self, parsed_url: ParseResult) -> bool:
        return self.string_matcher(parsed_url.fragment)


