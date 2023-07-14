from tempfile import SpooledTemporaryFile
from typing import IO, BinaryIO, List, Optional, Union, cast

import lxml.html
import pandas as pd
from datetime import datetime

from unstructured.documents.elements import (
    Element,
    ElementMetadata,
    Table,
    process_metadata,
)
from unstructured.file_utils.filetype import FileType, add_metadata_with_filetype
from unstructured.partition.common import (
    exactly_one,
    spooled_to_bytes_io_if_needed,
    get_last_modified_date,
    get_last_modified_date_from_file,
)


@process_metadata()
@add_metadata_with_filetype(FileType.CSV)
def partition_csv(
    filename: Optional[str] = None,
    file: Optional[Union[IO[bytes], SpooledTemporaryFile]] = None,
    metadata_filename: Optional[str] = None,
    metadata_date: Optional[datetime] = None,
    include_metadata: bool = True,
    **kwargs,
) -> List[Element]:
    """Partitions Microsoft Excel Documents in .csv format into its document elements.

        Parameters
        ----------
        filename
            A string defining the target filename path.
        file
            A file-like object using "rb" mode --> open(filename, "rb").
    <<<<<<< HEAD
    =======
        metadata_filename
            The filename to use for the metadata.
        metadata_date
            The last modified date for the document.
    >>>>>>> feat: add date field to metadata from csv file
        include_metadata
            Determines whether or not metadata is included in the output.
    """
    exactly_one(filename=filename, file=file)

    if filename:
        table = pd.read_csv(filename)
        last_modification_date = get_last_modified_date(filename)

    else:
        last_modification_date = get_last_modified_date_from_file(file)
        f = spooled_to_bytes_io_if_needed(
            cast(Union[BinaryIO, SpooledTemporaryFile], file)
        )
        table = pd.read_csv(f)

    html_text = table.to_html(index=False, header=False, na_rep="")
    text = lxml.html.document_fromstring(html_text).text_content()

    if include_metadata:
        metadata = ElementMetadata(
            text_as_html=html_text,
            filename=metadata_filename or filename,
            date=metadata_date or last_modification_date,
        )
    else:
        metadata = ElementMetadata()

    return [Table(text=text, metadata=metadata)]
