from url_data_extractor.matchers import CompoundMatcher, HostMatcher, PathPartsMatcher
from url_data_extractor.data_extractors import URLDataExtractor, PathPartDataExtractor

from pprint import pprint
from urllib.parse import urlparse

gitHubIssueURLDataExtractor = (
    URLDataExtractor.Builder()
    .with_url_matcher(
        CompoundMatcher.Builder()
        .with_matcher(HostMatcher("github.com"))
        .with_matcher(PathPartsMatcher.Builder().with_value_at_index(-2, "issues").build())
        .build()
    )
    .with_data_element_extractor("org", PathPartDataExtractor(0))
    .with_data_element_extractor("repo", PathPartDataExtractor(1))
    .with_data_element_extractor("issue", PathPartDataExtractor(-1))
    .build()
)

urls = [
    "https://github.com/PluMGMK/vbesvga.drv/issues/113",
    "https://github.com/hynek/hello-svc-part-2/blob/main/pyproject.toml",
    "https://youtube.com",
]

for url in urls:
    print(f"Attempting to extract data from '{url}'")

    try:
        data = gitHubIssueURLDataExtractor.extract_url_data(urlparse(url))
        pprint(data)
    except Exception as e:
        print(e)
