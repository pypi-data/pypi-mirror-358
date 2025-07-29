import gzip
import logging
from hashlib import md5
from pathlib import Path

import requests
from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class GenomeSummaryDownloader:
    def __init__(self, db: str, outdir: str = None):
        """
        Initialize the downloader with the database type and data directory.

        :param db: Database type, either 'genbank' or 'refseq'.
        :param data_dir: Directory to save the downloaded files.
        """
        self.base_url = "https://ftp.ncbi.nlm.nih.gov/genomes/ASSEMBLY_REPORTS/"
        match db:
            case "genbank":
                self.file = "assembly_summary_genbank.txt"
            case "refseq":
                self.file = "assembly_summary_refseq.txt"
            case _:
                raise ValueError("Database must be either 'genbank' or 'refseq'.")
        self.url = f"{self.base_url}{self.file}"
        self.outdir = outdir

    def compute_local_md5(self, file_path: Path) -> str:
        hash_md5 = md5()
        with file_path.open("rb") as f:
            for chunk in iter(lambda: f.read(self.chunk_size), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _full_download(
        self, url: str, dest: Path, timeout: int = 10, chunk_size: int = 8192
    ) -> None:
        """
        Download a file from the given URL to the specified destination with progress bar.

        :param url: URL of the file to download.
        :param dest: Destination path to save the downloaded file.
        :param timeout: Timeout for the request in seconds.
        :param chunk_size: Size of each chunk to read from the response.
        """
        print(f"Downloading {url} to {dest}")
        response = requests.get(url, stream=True, timeout=timeout)
        response.raise_for_status()
        total = int(response.headers.get("content-length", 0))
        # Create a buffer to read and decode gzip content on the fly
        decompressor = gzip.GzipFile(fileobj=response.raw)
        # Output gzip file
        with (
            gzip.open(dest, "wb") as out_f,
            tqdm(total=total, unit="B", unit_scale=True, desc=dest.name) as pbar,
        ):
            modified = 0
            # Read lines from the decompressed stream
            for line in decompressor:
                pbar.update(len(line))
                # Modify the first 5 lines if necessary
                if modified < 5:
                    decoded = line.decode("utf-8")
                    if decoded.startswith("#assembly_accession\t"):
                        decoded = decoded.lstrip("#")
                    line = decoded.encode("utf-8")
                    modified += 1
                out_f.write(line)

    def streaming_output(self, timeout: int = 10, chunk_size: int = 8192):
        """
        Stream download a file from the given URL and yield one decoded line at a time.

        :param url: URL of the file to download.
        :param timeout: Timeout for the request in seconds.
        :param chunk_size: Size of chunks to read from the response.
        :yields: One decoded line (str) at a time.
        """
        logging.info(f"Streaming download from {self.url}")
        with requests.get(self.url, stream=True, timeout=timeout) as response:
            response.raise_for_status()
            # Use an iterator over the response content
            # We will buffer bytes until we get a newline, then yield lines
            buffer = b""
            for chunk in response.iter_content(chunk_size=chunk_size):
                if not chunk:
                    continue
                buffer += chunk
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    yield line.decode("utf-8")
            # Yield the last line if it doesn't end with newline
            if buffer:
                yield buffer.decode("utf-8")
