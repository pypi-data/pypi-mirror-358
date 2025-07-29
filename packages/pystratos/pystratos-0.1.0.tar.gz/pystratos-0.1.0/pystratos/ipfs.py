import io
import uuid
from types import TracebackType
from typing import IO, Union, overload

import httpx

__ALL__ = ["AsyncIpfsClient"]


class AsyncIpfsClient:
    """AsyncIpfsClient is an asynchronous client for interacting with IPFS (InterPlanetary File System)."""

    def __init__(
        self, base_url: str = "http://127.0.0.1:5001/api/v0", timeout: int | None = None
    ):
        """
        Initializes the AsyncIpfsClient with the specified base URL and timeout.

        :param base_url: The base URL for the IPFS API.
        :param timeout: Optional timeout for HTTP requests."""
        self.base_url = base_url
        self._async_client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
        )

    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        await self.close()

    async def close(self):
        await self._async_client.aclose()

    @overload
    async def add(
        self, file: bytes, *, filename: str | None = None
    ) -> dict: ...  # pragma: no cover

    @overload
    async def add(
        self, file: IO[bytes], *, filename: str | None = None
    ) -> dict: ...  # pragma: no cover

    async def add(
        self, file: Union[bytes, IO[bytes]], *, filename: str | None = None
    ) -> dict:
        """
        Adds a file to IPFS.
        :param file: The file to add, either as bytes or a file-like object.
        :param filename: Optional name for the file in IPFS. If not provided, a random UUID will be used as the filename.
        :return: A dictionary containing the response from the IPFS API, typically including the CID (Content Identifier) of the added file.
        """
        if isinstance(file, bytes):
            file = io.BytesIO(file)
        if filename is None:
            filename = uuid.uuid4().hex
        files = {"file": (filename, file, "application/octet-stream")}
        response = await self._async_client.post(f"{self.base_url}/add", files=files)
        response.raise_for_status()
        return response.json()

    async def cat(self, cid):
        """Retrieves a file from IPFS by its CID.
        :param cid: The Content Identifier (CID) of the file to retrieve.
        """
        params = {"arg": cid}
        response = await self._async_client.post(f"{self.base_url}/cat", params=params)
        response.raise_for_status()
        return response.content
