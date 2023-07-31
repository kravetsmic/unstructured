import contextlib
import json
import os
import pathlib

import pytest
import requests

from unstructured.documents.elements import NarrativeText
from unstructured.partition.api import partition_multiple_via_api, partition_via_api

DIRECTORY = pathlib.Path(__file__).parent.resolve()

EML_TEST_FILE = "eml/fake-email.eml"

skip_outside_ci = os.getenv("CI", "").lower() in {"", "false", "f", "0"}
skip_not_on_main = os.getenv("GITHUB_REF_NAME", "").lower() != "main"


class MockResponse:
    def __init__(self, status_code):
        self.status_code = status_code

    @property
    def text(self):
        return """[
    {
        "element_id": "f49fbd614ddf5b72e06f59e554e6ae2b",
        "text": "This is a test email to use for unit tests.",
        "type": "NarrativeText",
        "metadata": {
            "date": "2022-12-16T17:04:16-05:00",
            "sent_from": [
                "Matthew Robinson <mrobinson@unstructured.io>"
            ],
            "sent_to": [
                "Matthew Robinson <mrobinson@unstructured.io>"
            ],
            "subject": "Test Email",
            "filename": "fake-email.eml",
            "filetype": "message/rfc822"
        }
    }
]"""

    def json(self):
        return json.loads(self.text)


class MockMultipleResponse:
    def __init__(self, status_code):
        self.status_code = status_code

    def json(self):
        return json.loads(self.text)

    @property
    def text(self):
        return """[
    [
        {
            "element_id": "f49fbd614ddf5b72e06f59e554e6ae2b",
            "text": "This is a test email to use for unit tests.",
            "type": "NarrativeText",
            "metadata": {
                "date": "2022-12-16T17:04:16-05:00",
                "sent_from": [
                    "Matthew Robinson <mrobinson@unstructured.io>"
                ],
                "sent_to": [
                    "Matthew Robinson <mrobinson@unstructured.io>"
                ],
                "subject": "Test Email",
                "filename": "fake-email.eml",
                "filetype": "message/rfc822"
            }
        }
    ],
    [
        {
            "element_id": "f49fbd614ddf5b72e06f59e554e6ae2b",
            "text": "This is a test email to use for unit tests.",
            "type": "NarrativeText",
            "metadata": {
                "date": "2022-12-16T17:04:16-05:00",
                "sent_from": [
                    "Matthew Robinson <mrobinson@unstructured.io>"
                ],
                "sent_to": [
                    "Matthew Robinson <mrobinson@unstructured.io>"
                ],
                "subject": "Test Email",
                "filename": "fake-email.eml",
                "filetype": "message/rfc822"
            }
        }
    ]
]"""


def test_partition_multiple_via_api_with_single_filename(monkeypatch):
    monkeypatch.setattr(
        requests,
        "post",
        lambda *args, **kwargs: MockResponse(status_code=200),
    )
    filename = os.path.join(DIRECTORY, "..", "..", "example-docs", EML_TEST_FILE)

    elements = partition_multiple_via_api(filenames=[filename])
    assert elements[0][0] == NarrativeText(
        "This is a test email to use for unit tests.",
    )
    assert elements[0][0].metadata.filetype == "message/rfc822"


def test_partition_multiple_via_api_from_filenames(monkeypatch):
    monkeypatch.setattr(
        requests,
        "post",
        lambda *args, **kwargs: MockMultipleResponse(status_code=200),
    )

    filenames = [
        os.path.join(DIRECTORY, "..", "..", "example-docs", "eml/fake-email.eml"),
        os.path.join(DIRECTORY, "..", "..", "example-docs", "fake.docx"),
    ]

    elements = partition_multiple_via_api(filenames=filenames)
    assert len(elements) == 2
    assert elements[0][0] == NarrativeText(
        "This is a test email to use for unit tests.",
    )
    assert elements[0][0].metadata.filetype == "message/rfc822"


def test_partition_multiple_via_api_from_files(monkeypatch):
    monkeypatch.setattr(
        requests,
        "post",
        lambda *args, **kwargs: MockMultipleResponse(status_code=200),
    )

    filenames = [
        os.path.join(DIRECTORY, "..", "..", "example-docs", EML_TEST_FILE),
        os.path.join(DIRECTORY, "..", "..", "example-docs", "fake.docx"),
    ]

    with contextlib.ExitStack() as stack:
        files = [stack.enter_context(open(filename, "rb")) for filename in filenames]
        elements = partition_multiple_via_api(
            files=files,
            file_filenames=filenames,
        )
    assert len(elements) == 2
    assert elements[0][0] == NarrativeText(
        "This is a test email to use for unit tests.",
    )
    assert elements[0][0].metadata.filetype == "message/rfc822"


def test_partition_multiple_via_api_raises_with_bad_response(monkeypatch):
    monkeypatch.setattr(
        requests,
        "post",
        lambda *args, **kwargs: MockMultipleResponse(status_code=500),
    )

    filenames = [
        os.path.join(DIRECTORY, "..", "..", "example-docs", EML_TEST_FILE),
        os.path.join(DIRECTORY, "..", "..", "example-docs", "fake.docx"),
    ]

    with pytest.raises(ValueError):
        partition_multiple_via_api(filenames=filenames)


def test_partition_multiple_via_api_raises_with_content_types_size_mismatch(
    monkeypatch,
):
    monkeypatch.setattr(
        requests,
        "post",
        lambda *args, **kwargs: MockMultipleResponse(status_code=500),
    )

    filenames = [
        os.path.join(DIRECTORY, "..", "..", "example-docs", "fake-email.eml"),
        os.path.join(DIRECTORY, "..", "..", "example-docs", "fake.docx"),
    ]

    with pytest.raises(ValueError):
        partition_multiple_via_api(
            filenames=filenames,
            content_types=["text/plain"],
        )


def test_partition_multiple_via_api_from_files_raises_with_size_mismatch(monkeypatch):
    monkeypatch.setattr(
        requests,
        "post",
        lambda *args, **kwargs: MockMultipleResponse(status_code=200),
    )

    filenames = [
        os.path.join(DIRECTORY, "..", "..", "example-docs", EML_TEST_FILE),
        os.path.join(DIRECTORY, "..", "..", "example-docs", "fake.docx"),
    ]

    with contextlib.ExitStack() as stack:
        files = [stack.enter_context(open(filename, "rb")) for filename in filenames]
        with pytest.raises(ValueError):
            partition_multiple_via_api(
                files=files,
                file_filenames=filenames,
                content_types=["text/plain"],
            )


def test_partition_multiple_via_api_from_files_raises_without_filenames(monkeypatch):
    monkeypatch.setattr(
        requests,
        "post",
        lambda *args, **kwargs: MockMultipleResponse(status_code=200),
    )

    filenames = [
        os.path.join(DIRECTORY, "..", "..", "example-docs", EML_TEST_FILE),
        os.path.join(DIRECTORY, "..", "..", "example-docs", "fake.docx"),
    ]

    with contextlib.ExitStack() as stack:
        files = [stack.enter_context(open(filename, "rb")) for filename in filenames]
        with pytest.raises(ValueError):
            partition_multiple_via_api(
                files=files,
            )


def get_api_key():
    api_key = os.getenv("UNS_API_KEY")
    if api_key is None:
        raise ValueError("UNS_API_KEY environment variable not set")
    return api_key


@pytest.mark.skipif(skip_outside_ci, reason="Skipping test run outside of CI")
@pytest.mark.skipif(skip_not_on_main, reason="Skipping test run outside of main branch")
def test_partition_multiple_via_api_valid_request_data_kwargs():
    filenames = [
        os.path.join(
            DIRECTORY,
            "..",
            "..",
            "example-docs",
            "layout-parser-paper-fast.pdf",
        ),
        os.path.join(
            DIRECTORY,
            "..",
            "..",
            "example-docs",
            "layout-parser-paper-fast.jpg",
        ),
    ]

    elements = partition_multiple_via_api(
        filenames=filenames,
        strategy="fast",
        api_key=get_api_key(),
    )
    assert isinstance(elements, list)


@pytest.mark.skipif(skip_outside_ci, reason="Skipping test run outside of CI")
def test_partition_multiple_via_api_invalid_request_data_kwargs():
    filenames = [
        os.path.join(
            DIRECTORY,
            "..",
            "..",
            "example-docs",
            "layout-parser-paper-fast.pdf",
        ),
        os.path.join(
            DIRECTORY,
            "..",
            "..",
            "example-docs",
            "layout-parser-paper-fast.jpg",
        ),
    ]
    with pytest.raises(ValueError):
        partition_multiple_via_api(
            filenames=filenames,
            strategy="not_a_strategy",
            api_key=get_api_key(),
        )
