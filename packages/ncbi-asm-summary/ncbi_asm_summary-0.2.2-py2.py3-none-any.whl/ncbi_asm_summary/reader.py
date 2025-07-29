import argparse
import gzip

# logging
import logging
from pathlib import Path

from ncbi_asm_summary.downloader import GenomeSummaryDownloader
from ncbi_asm_summary.parser import tableRow

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class AssemblySummaryStream:
    def __init__(self, file_path=None, db=None):
        if file_path is None and db is None:
            raise ValueError("Either file_path or db must be provided.")
        if file_path is not None and db is not None:
            raise ValueError("Only one of file_path or db should be provided.")
        if db not in [None, "genbank", "refseq"]:
            raise ValueError("db must be either 'genbank' or 'refseq'.")
        self.file_path = file_path
        self.db = db

    def _read_line(self, line):
        yield tableRow(*[i.strip() for i in line.split("\t")])

    def _is_gzipped(self):
        try:
            with open(self.file_path, "rb") as f:
                return f.read(2) == b"\x1f\x8b"
        except Exception:
            return False

    def _local_stream(self):
        if self.file_path and not Path(self.file_path).exists():
            raise FileNotFoundError(f"File {self.file_path} does not exist.")
        if self._is_gzipped():
            con = gzip.open(self.file_path, "rt")
        else:
            con = open(self.file_path, "r")
        with con as file_con:
            for line in file_con:
                if line.startswith("GC"):
                    yield from self._read_line(line)

    def _remote_stream(self):
        if self.db is None:
            raise ValueError("db must be provided for remote connection.")
        downloader = GenomeSummaryDownloader(db=self.db)
        for i in downloader.streaming_output():
            if i.startswith("GC"):
                yield from self._read_line(i)

    def stream(self):
        """
        Stream the assembly summary file, either from a local file or a remote source.

        :return: Generator yielding tableRow objects.
        """
        if self.file_path:
            return self._local_stream()
        elif self.db:
            return self._remote_stream()
        else:
            raise ValueError("No valid source provided for streaming.")


def main():
    parser = argparse.ArgumentParser(description="Stream NCBI Assembly Summary file.")
    parser.add_argument(
        "file_path",
        type=str,
        nargs="?",
        default=None,
        help="Path to the assembly summary file.",
    )
    parser.add_argument(
        "-d",
        "--db",
        type=str,
        choices=["genbank", "refseq"],
        default=None,
        help="Database type, either 'genbank' or 'refseq'.",
    )
    parser.add_argument(
        "-n",
        "--nrows",
        type=int,
        default=float("inf"),
        help="Number of rows to display (default: 10)",
    )
    parser.add_argument(
        "-c",
        "--columns",
        type=str,
        nargs="*",
        default=["assembly_accession", "ftp_path"],
        help="Columns to display from the assembly summary file (default: assembly_accession, ftp_path)",
    )
    parser.add_argument("--header", action="store_true", help="Include header in output")
    args = parser.parse_args()
    # column validation
    valid_columns = list(tableRow.__dataclass_fields__.keys())
    input_columns = set(args.columns)
    invalid_columns = set(input_columns) - set(valid_columns)
    if invalid_columns:
        raise ValueError(
            f"Invalid column names: {', '.join(invalid_columns)}. Valid columns are: {', '.join(valid_columns)}"
        )
    stream = AssemblySummaryStream(file_path=args.file_path, db=args.db)
    nrows = args.nrows - 1
    row_count = 0
    logging.info(
        f"First {nrows + 1} rows, from {Path(args.file_path).stem if args.file_path else args.db}..."
    )
    # Header is done this way because  otherwise the log info of 
    # the streaming download will print in between it and the other data
    # only matters when viewing in the terminal, not saving to a file
    have_printed_header = False
    for row in stream.stream():
        if args.header and not have_printed_header:
            header = "\t".join(args.columns)
            print(header)
            have_printed_header = True
        row_data = [getattr(row, col) for col in args.columns]
        print("\t".join(row_data))
        row_count += 1
        if row_count > nrows:
            break


if __name__ == "__main__":
    main()
