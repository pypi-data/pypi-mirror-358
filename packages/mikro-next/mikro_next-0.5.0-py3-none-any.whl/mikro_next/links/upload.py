import asyncio


from mikro_next.scalars import ArrayLike, ImageFileLike, MeshLike, ParquetLike, FileLike
from rath.links.parsing import ParsingLink
from rath.operation import Operation, opify
from typing import Any, Tuple, Type, Union
from mikro_next.io.upload import (
    aupload_bigfile,
    aupload_xarray,
    aupload_parquet,
    astore_media_file,
    astore_mesh_file,
)
from pydantic import Field
from concurrent.futures import ThreadPoolExecutor
import uuid
from functools import partial
from mikro_next.datalayer import DataLayer


async def apply_recursive(
    func, obj, typeguard: Union[Type[Any], Tuple[Type[Any], ...]]
) -> Any:
    """
    Recursively applies an asynchronous function to elements in a nested structure.

    Args:
        func (callable): The asynchronous function to apply.
        obj (any): The nested structure (dict, list, tuple, etc.) to process.
        typeguard (type): The type of elements to apply the function to.

    Returns:
        any: The nested structure with the function applied to elements of the specified type.
    """
    if isinstance(
        obj, dict
    ):  # If obj is a dictionary, recursively apply to each key-value pair
        return {k: await apply_recursive(func, v, typeguard) for k, v in obj.items()}
    elif isinstance(obj, list):  # If obj is a list, recursively apply to each element
        return await asyncio.gather(
            *[apply_recursive(func, elem, typeguard) for elem in obj]
        )
    elif isinstance(
        obj, tuple
    ):  # If obj is a tuple, recursively apply to each element and convert back to tuple
        return tuple(
            await asyncio.gather(
                *[apply_recursive(func, elem, typeguard) for elem in obj]
            )
        )
    elif isinstance(obj, typeguard):
        return await func(obj)
    else:  # If obj is not a dict, list, tuple, or matching the typeguard, return it as is
        return obj


async def afake_upload(xarray: ArrayLike, *args, **kwargs) -> str:
    return str(uuid.uuid4())


class UploadLink(ParsingLink):
    """Data Layer Upload Link

    This link is used to upload  supported types to a DataLayer.
    It parses queries, mutatoin and subscription arguments and
    uploads the items to the DataLayer, and substitures the
    DataFrame with the S3 path.

    Args:
        ParsingLink (_type_): _description_


    """

    datalayer: DataLayer

    executor: ThreadPoolExecutor = Field(
        default_factory=lambda: ThreadPoolExecutor(max_workers=4), exclude=True
    )
    _executor_session: Any = None

    async def __aenter__(self):
        self._executor_session = self.executor.__enter__()
        return self

    async def aget_image_credentials(self, key, datalayer) -> Any:
        from mikro_next.api.schema import RequestUploadMutation, RequestUploadInput

        operation = opify(
            RequestUploadMutation.Meta.document,
            variables={
                "input": RequestUploadInput(key=key, datalayer=datalayer).model_dump()
            },
        )

        if not self.next:
            raise ValueError("No next link found. Please set the next link.")

        async for result in self.next.aexecute(operation):
            return RequestUploadMutation(**result.data).request_upload

    async def aget_table_credentials(self, key, datalayer) -> Any:
        from mikro_next.api.schema import (
            RequestTableUploadMutation,
            RequestTableUploadInput,
        )

        if not self.next:
            raise ValueError("No next link found. Please set the next link.")

        operation = opify(
            RequestTableUploadMutation.Meta.document,
            variables={
                "input": RequestTableUploadInput(
                    key=key, datalayer=datalayer
                ).model_dump(by_alias=True, exclude_unset=True)
            },
        )

        async for result in self.next.aexecute(operation):
            return RequestTableUploadMutation(**result.data).request_table_upload

    async def aget_bigfile_credentials(self, file: FileLike, datalayer) -> Any:
        from mikro_next.api.schema import (
            RequestFileUploadMutation,
            RequestFileUploadInput,
        )

        if not self.next:
            raise ValueError("No next link found. Please set the next link.")

        operation = opify(
            RequestFileUploadMutation.Meta.document,
            variables={
                "input": RequestFileUploadInput(
                    fileName=file.file_name, datalayer=datalayer
                ).model_dump(by_alias=True, exclude_unset=True)
            },
        )

        async for result in self.next.aexecute(operation):
            return RequestFileUploadMutation(**result.data).request_file_upload

    async def aget_mesh_credentials(self, key, datalayer) -> Any:
        from mikro_next.api.schema import (
            RequestMeshUploadMutation,
            RequestMeshUploadInput,
        )

        if not self.next:
            raise ValueError("No next link found. Please set the next link.")

        operation = opify(
            RequestMeshUploadMutation.Meta.document,
            variables={
                "input": RequestMeshUploadInput(
                    key=key, datalayer=datalayer
                ).model_dump(by_alias=True, exclude_unset=True)
            },
        )

        async for result in self.next.aexecute(operation):
            return RequestMeshUploadMutation(**result.data).request_mesh_upload

    async def arequest_media_credentials(self, file_name: str, datalayer: str) -> Any:
        from mikro_next.api.schema import (
            RequestMediaUploadMutation,
            RequestMediaUploadInput,
        )

        if not self.next:
            raise ValueError("No next link found. Please set the next link.")

        operation = opify(
            RequestMediaUploadMutation.Meta.document,
            variables={
                "input": RequestMediaUploadInput(
                    fileName=file_name, datalayer=datalayer
                ).model_dump(by_alias=True, exclude_unset=True)
            },
        )

        async for result in self.next.aexecute(operation):
            return RequestMediaUploadMutation(**result.data).request_media_upload

    async def aupload_parquet(
        self, datalayer: "DataLayer", parquet_input: ParquetLike
    ) -> str:
        assert datalayer is not None, "Datalayer must be set"
        endpoint_url = await datalayer.get_endpoint_url()

        credentials = await self.aget_table_credentials(parquet_input.key, endpoint_url)
        return await aupload_parquet(
            parquet_input,
            credentials,
            datalayer,
            self._executor_session,
        )

    async def aupload_xarray(self, datalayer: "DataLayer", xarray: ArrayLike) -> str:
        assert datalayer is not None, "Datalayer must be set"
        endpoint_url = await datalayer.get_endpoint_url()

        credentials = await self.aget_image_credentials(xarray.key, endpoint_url)
        return await aupload_xarray(
            xarray,
            credentials,
            datalayer,
        )

    async def aupload_bigfile(self, datalayer: "DataLayer", file: FileLike) -> str:
        assert datalayer is not None, "Datalayer must be set"
        endpoint_url = await datalayer.get_endpoint_url()

        credentials = await self.aget_bigfile_credentials(file, endpoint_url)
        return await aupload_bigfile(
            file,
            credentials,
            datalayer,
        )

    async def aupload_mediafile(
        self, datalayer: "DataLayer", file: ImageFileLike
    ) -> str:
        assert datalayer is not None, "Datalayer must be set"
        endpoint_url = await datalayer.get_endpoint_url()

        credentials = await self.arequest_media_credentials(
            file.file_name, endpoint_url
        )
        return await astore_media_file(
            file,
            credentials,
            datalayer,
        )

    async def astore_mesh_file(self, datalayer: "DataLayer", mesh: MeshLike) -> str:
        assert datalayer is not None, "Datalayer must be set"
        endpoint_url = await datalayer.get_endpoint_url()

        credentials = await self.aget_mesh_credentials(mesh.key, endpoint_url)
        return await astore_mesh_file(
            mesh,
            credentials,
            datalayer,
        )

    async def aparse(self, operation: Operation) -> Operation:
        """Parse the operation (Async)

        Extracts the DataFrame from the operation and uploads it to the DataLayer.

        Args:
            operation (Operation): The operation to parse

        Returns:
            Operation: _description_
        """

        datalayer = operation.context.kwargs.get("datalayer", self.datalayer)

        operation.variables = await apply_recursive(
            partial(self.aupload_xarray, datalayer),
            operation.variables,
            ArrayLike,
        )
        operation.variables = await apply_recursive(
            partial(self.aupload_parquet, datalayer), operation.variables, ParquetLike
        )
        operation.variables = await apply_recursive(
            partial(self.aupload_bigfile, datalayer),
            operation.variables,
            (FileLike),
        )
        operation.variables = await apply_recursive(
            partial(self.aupload_mediafile, datalayer),
            operation.variables,
            (ImageFileLike),
        )
        operation.variables = await apply_recursive(
            partial(self.astore_mesh_file, datalayer), operation.variables, MeshLike
        )

        return operation

    async def adisconnect(self):
        self.executor.__exit__(None, None, None)
