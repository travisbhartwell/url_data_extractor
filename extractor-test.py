from url_data_extractor.matchers import CompoundMatcher, HostMatcher, PathPartsMatcher
from url_data_extractor.data_extractors import (
    URLDataExtractor,
    PathPartDataExtractor,
    PathSliceDataExtractor,
)

from pprint import pprint
from urllib.parse import urlparse

issue_data_extractor = (
    URLDataExtractor.Builder()
    .with_url_matcher(
        CompoundMatcher.Builder()
        .with_matcher(HostMatcher.hostname_equals_matcher("github.com"))
        .with_matcher(PathPartsMatcher.Builder().with_value_at_index(-2, "issues").build())
        .build()
    )
    .with_data_element_extractor("org", PathPartDataExtractor(0))
    .with_data_element_extractor("repo", PathPartDataExtractor(1))
    .with_data_element_extractor("issue", PathPartDataExtractor(-1))
    .build()
)

blob_path_data_extractor = (
    URLDataExtractor.Builder()
    .with_url_matcher(
        CompoundMatcher.Builder()
        .with_matcher(HostMatcher.hostname_equals_matcher("github.com"))
        .with_matcher(PathPartsMatcher.Builder().with_value_at_index(2, "blob").build())
        .build()
    )
    .with_data_element_extractor("org", PathPartDataExtractor(0))
    .with_data_element_extractor("repo", PathPartDataExtractor(1))
    .with_data_element_extractor("commit", PathPartDataExtractor(3))
    .with_data_element_extractor("path", PathSliceDataExtractor(4))
    .build()
)

urls = [
    "https://github.com/PluMGMK/vbesvga.drv/issues/113",
    "https://github.com/hynek/hello-svc-part-2/blob/main/pyproject.toml",
    "https://youtube.com",
    "https://github.com/travisbhartwell/mycmd/blob/cc2ec3b0209121806a680f2ad42b7d8ffdb4ebf1/testing/user-base/shell/extended/extended-lib",
]

for url in urls:
    print(f"Attempting to extract data from '{url}'")

    try:
        data = blob_path_data_extractor.extract_url_data(urlparse(url))
        pprint(data)
    except Exception as e:
        print(e)
