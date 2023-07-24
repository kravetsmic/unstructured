from typing import IO, List, Optional

from unstructured.documents.elements import Element, process_metadata
from unstructured.file_utils.filetype import FileType, add_metadata_with_filetype
from unstructured.partition.html import convert_and_partition_html


@process_metadata()
@add_metadata_with_filetype(FileType.RTF)
def partition_rtf(
    filename: Optional[str] = None,
    file: Optional[IO[bytes]] = None,
    include_page_breaks: bool = False,
    include_metadata: bool = True,
    metadata_filename: Optional[str] = None,
    include_path_in_metadata_filename: bool = False,
    **kwargs,
) -> List[Element]:
    """Partitions an RTF document. The document is first converted to HTML and then
    partitioned using partiton_html.

    Parameters
    ----------
    filename
        A string defining the target filename path.
    file
        A file-like object using "rb" mode --> open(filename, "rb").
    include_page_breaks
        If True, the output will include page breaks if the filetype supports it
    include_path_in_metadata_filename
        Determines whether or not metadata filename will contain full path
    """
    return convert_and_partition_html(
        source_format="rtf",
        filename=filename,
        file=file,
        include_page_breaks=include_page_breaks,
        metadata_filename=metadata_filename,
        include_path_in_metadata_filename=include_path_in_metadata_filename,
    )
