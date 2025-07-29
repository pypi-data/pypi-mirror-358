"""
some faster implemention for stereo map,include data sampling...
"""
from __future__ import annotations
import typing
from typing import List
import numpy as np
import numpy.typing as npt
from typing import overload

__all__ = [
    "generate_bin1_visual_sampling_data", "Status", "get_status_string", "filter_data_with_coordinates_i32",
    "filter_data_with_coordinates_u32", "filter_data_with_coordinates_i64", "filter_data_with_coordinates_u64",
    "filter_data_with_coordinates_f32", "filter_data_with_coordinates_f64", "filter_data_with_polygons",
    "PyStatefulMask"
]


class DatasetCompressKind:
    __members__: typing.ClassVar[dict[str, DatasetCompressKind]]
    gzip: typing.ClassVar[DatasetCompressKind]
    zstd: typing.ClassVar[DatasetCompressKind]
    bz2: typing.ClassVar[DatasetCompressKind]
    lz4: typing.ClassVar[DatasetCompressKind]
    lfs: typing.ClassVar[DatasetCompressKind]


class GeneCachePolicy:
    __members__: typing.ClassVar[dict[str, GeneCachePolicy]]
    always_cache_in_file: typing.ClassVar[GeneCachePolicy]
    never_cache_in_file: typing.ClassVar[GeneCachePolicy]
    auto_cache_in_file: typing.ClassVar[GeneCachePolicy]
    unknown_policy: typing.ClassVar[GeneCachePolicy]


class MaskUpdateKind:
    __members__: typing.ClassVar[dict[str, MaskUpdateKind]]
    AND: typing.ClassVar[MaskUpdateKind]
    OR: typing.ClassVar[MaskUpdateKind]
    XOR: typing.ClassVar[MaskUpdateKind]
    XNOR: typing.ClassVar


class VisualSamplingRunnerImplKind:
    __members__: typing.ClassVar[dict[str, VisualSamplingRunnerImplKind]]
    lock_sync: typing.ClassVar[VisualSamplingRunnerImplKind]
    lock_free: typing.ClassVar[VisualSamplingRunnerImplKind]
    other: typing.ClassVar[VisualSamplingRunnerImplKind]


class BlockFilterMode:
    __members__: typing.ClassVar[dict[str, MaskUpdateKind]]
    Strict: typing.ClassVar[BlockFilterMode]
    Fuzzy: typing.ClassVar[BlockFilterMode]
    Precise: typing.ClassVar[BlockFilterMode]


class MaskOverflowPartProcessKind:
    __members__: typing.ClassVar[dict[str, MaskOverflowPartProcessKind]]
    TraitAsBackground: typing.ClassVar[MaskOverflowPartProcessKind]
    TraitAsFrontGround: typing.ClassVar[MaskOverflowPartProcessKind]
    TraitAsNone: typing.ClassVar[MaskOverflowPartProcessKind]


class Status:
    """
    Members:
        kSuccess
        kFileNotFoundError
        kInvalidBlockSize
        kFailCreateDir
        kNotSupportedFile
        kFailOpenFile
        kInvalidShape
        kInvaidSourceID
        kFailCreateFile
        kRunWithAsync
        kNotSupportedType
        kFailSelectBlockRange
        kFailReadBlockData
        kEarlyStopping
        kNotChunkAndCompressed
        kSizeMismatch
        kDecompressedError
        kNotSupportDtype
        kUnknown
        kFailGetStorageinfo
        kZstdCreateCtxError
        kZstdSetParameterError
        kZstdCompressError
        kInvalidBinsize
        kInvalidPrefetchQueueSize
        kIsNotAsyncTask
        kSamplingImplNotInit
    """
    __members__: typing.ClassVar[
        dict[str, Status]
    ]                                           # value = {"kSuccess": <Status.kSuccess: 0>,"kFileNotFoundError": <Status.kFileNotFoundError: 1>,"kInvalidBlockSize": <Status.kInvalidBlockSize: 3>,"kFailCreateDir": <Status.kFailCreateDir: 4>,"kNotSupportedFile": <Status.kNotSupportedFile: 5>,"kFailOpenFile": <Status.kFailOpenFile: 6>,"kInvalidShape": <Status.kInvalidShape: 7>,"kInvaidSourceID": <Status.kInvaidSourceID: 8>,"kFailCreateFile": <Status.kFailCreateFile: 9>}
    kFailCreateDir: typing.ClassVar[Status]     # value = <Status.kFailCreateDir: 4>
    kFailCreateFile: typing.ClassVar[Status]    # value = <Status.kFailCreateFile: 9>
    kFailOpenFile: typing.ClassVar[Status]      # value = <Status.kFailOpenFile: 6>
    kFileNotFoundError: typing.ClassVar[Status] # value = <Status.kFileNotFoundError: 1>
    kInvaidSourceID: typing.ClassVar[Status]    # value = <Status.kInvaidSourceID: 8>
    kInvalidBlockSize: typing.ClassVar[Status]  # value = <Status.kInvalidBlockSize: 3>
    kInvalidShape: typing.ClassVar[Status]      # value = <Status.kInvalidShape: 7>
    kNotSupportedFile: typing.ClassVar[Status]  # value = <Status.kNotSupportedFile: 5>
    kSuccess: typing.ClassVar[Status]           # value = <Status.kSuccess: 0>
    kRunWithAsync: typing.ClassVar[Status]
    kNotSupportedType: typing.ClassVar[Status]
    kFailSelectBlockRange: typing.ClassVar[Status]
    kFailReadBlockData: typing.ClassVar[Status]
    kEarlyStopping: typing.ClassVar[Status]
    kNotChunkAndCompressed: typing.ClassVar[Status]
    kSizeMismatch: typing.ClassVar[Status]
    kDecompressedError: typing.ClassVar[Status]
    kNotSupportDtype: typing.ClassVar[Status]
    kUnknown: typing.ClassVar[Status]
    kFailGetStorageinfo: typing.ClassVar[Status]
    kZstdCreateCtxError: typing.ClassVar[Status]
    kZstdSetParameterError: typing.ClassVar[Status]
    kZstdCompressError: typing.ClassVar[Status]
    kInvalidBinsize: typing.ClassVar[Status]
    kInvalidPrefetchQueueSize: typing.ClassVar[Status]
    kIsNotAsyncTask: typing.ClassVar[Status]
    kSamplingImplNotInit: typing.ClassVar[Status]

    def __eq__(self, other: typing.Any) -> bool:
        ...

    def __getstate__(self) -> int:
        ...

    def __hash__(self) -> int:
        ...

    def __index__(self) -> int:
        ...

    def __init__(self, value: int) -> None:
        ...

    def __int__(self) -> int:
        ...

    def __ne__(self, other: typing.Any) -> bool:
        ...

    def __repr__(self) -> str:
        ...

    def __setstate__(self, state: int) -> None:
        ...

    def __str__(self) -> str:
        ...

    @property
    def name(self) -> str:
        ...

    @property
    def value(self) -> int:
        ...


def get_status_string(status: Status) -> str:
    ...


kFailCreateDir: Status     # value = <Status.kFailCreateDir: 4>
kFailCreateFile: Status    # value = <Status.kFailCreateFile: 9>
kFailOpenFile: Status      # value = <Status.kFailOpenFile: 6>
kFileNotFoundError: Status # value = <Status.kFileNotFoundError: 1>
kInvaidSourceID: Status    # value = <Status.kInvaidSourceID: 8>
kInvalidBlockSize: Status  # value = <Status.kInvalidBlockSize: 3>
kInvalidShape: Status      # value = <Status.kInvalidShape: 7>
kNotSupportedFile: Status  # value = <Status.kNotSupportedFile: 5>
kSuccess: Status           # value = <Status.kSuccess: 0>


def generate_bin1_visual_sampling_data(
    gene_file: str,
    result_dir: str,
    max_block_size: int,
    min_block_size: int,
    prefetch_queue_size: int = 3,
    n_parse_workers: int = 2,
    n_compress_workers: int = 8,
    quick_sampling: bool = True
) -> Status:
    """
    generate the visual sampling data of bin1 for stereomap!
    Args:
        gene_file:str,the file of of gene
        result_dir:str,the directory to save the bin sampling...
        max_block_size:int,the max block size of sampling,must be power of 2!
            if the max block size == chunk_size of gene file,will using fast function!
        min_block_size:int,the min block size of sampling,also the power of 2
        prefetch_queue_size:int,the cache queue size,default value is 3
        n_parse_workers:the n workers use to parse the data,if not use hdf5,we will parse it self!!! default 3
        n_compress_workers:the n workers use to compress with zstd default is 8
        quick_sampling:bool,if true,we will try to use the fastest function! default is true
    """
    ...


def generate_any_visual_sampling_data(
    gene_file: str,
    result_dir: str,
    max_block_size: int,
    min_block_size: int,
    bin_size: int = 1,
    prefetch_queue_size: int = 3,
    n_parse_workers: int = 2,
    n_compress_workers: int = 8,
    quick_sampling: bool = True
) -> Status:
    """
    generate the visual sampling data of any bin size for stereomap!
    Args:
        gene_file:str,the file of of gene
        result_dir:str,the directory to save the bin sampling...
        max_block_size:int,the max block size of sampling,must be power of 2!
            if the max block size == chunk_size of gene file,will using fast function!
        min_block_size:int,the min block size of sampling,also the power of 2
        bin_size:int,default is 1,if <=0,will get error!
        prefetch_queue_size:int,the cache queue size,default value is 3
        n_parse_workers:the n workers use to parse the data,if not use hdf5,we will parse it self!!! default 3
        n_compress_workers:the n workers use to compress with zstd default is 8
        quick_sampling:bool,if true,we will try to use the fastest function! default is true
    """
    ...


def filter_data_with_coordinates_i32(
    coordinates: npt.NDArray[np.int32], filter_coordinates: npt.NDArray[np.int32], parallel: int
) -> npt.NDArray[np.uint64]:
    """
    Args:
        coordinates:nxm shape, m >=2
        filter_coordinates:same as coordiantes
        parallel:int
        x_col:int,default = 0
        y_col:int,default = 1
    Returns:
        results:1d array,uint64 type,return the index if the value of coordinates in filter coordinates
    """
    ...


def filter_data_with_coordinates_u32(
    coordinates: npt.NDArray[np.uint32], filter_coordinates: npt.NDArray[np.uint32], parallel: int
) -> npt.NDArray[np.uint64]:
    """
     Args:
        coordinates:nxm shape, m >=2
        filter_coordinates:same as coordiantes
        parallel:int
        x_col:int,default = 0
        y_col:int,default = 1
    Returns:
        results:1d array,uint64 type,return the index if the value of coordinates in filter coordinates
    """
    ...


def filter_data_with_coordinates_i64(
    coordinates: npt.NDArray[np.int64], filter_coordinates: npt.NDArray[np.int64], parallel: int
) -> npt.NDArray[np.uint64]:
    """
    Args:
        coordinates:nxm shape, m >=2
        filter_coordinates:same as coordiantes
        parallel:int
        x_col:int,default = 0
        y_col:int,default = 1
    Returns:
        results:1d array,uint64 type,return the index if the value of coordinates in filter coordinates
    """
    ...


def filter_data_with_coordinates_u64(
    coordinates: npt.NDArray[np.uint64], filter_coordinates: npt.NDArray[np.uint64], parallel: int
) -> npt.NDArray[np.uint64]:
    """
    Args:
        coordinates:nxm shape, m >=2
        filter_coordinates:same as coordiantes
        parallel:int
        x_col:int,default = 0
        y_col:int,default = 1
    Returns:
        results:1d array,uint64 type,return the index if the value of coordinates in filter coordinates
    """
    ...


def filter_data_with_coordinates_f32(
    coordinates: npt.NDArray[np.float32], filter_coordinates: npt.NDArray[np.float32], parallel: int
) -> npt.NDArray[np.uint64]:
    """
    Args:
        coordinates:nxm shape, m >=2
        filter_coordinates:same as coordiantes
        parallel:int
        x_col:int,default = 0
        y_col:int,default = 1
    Returns:
        results:1d array,uint64 type,return the index if the value of coordinates in filter coordinates
    """
    ...


def filter_data_with_coordinates_f64(
    coordinates: npt.NDArray[np.double], filter_coordinates: npt.NDArray[np.double], parallel: int
) -> npt.NDArray[np.uint64]:
    """
    Args:
        coordinates:nxm shape, m >=2
        filter_coordinates:same as coordiantes
        parallel:int
        x_col:int,default = 0
        y_col:int,default = 1
    Returns:
        results:1d array,uint64 type,return the index if the value of coordinates in filter coordinates
    """
    ...


@overload
def filter_data_with_coordinates(
    coordinates: npt.NDArray,
    filter_coordinates: npt.NDArray,
    parallel: int,
    x_col: int = 0,
    y_col: int = 1
) -> npt.NDArray[np.uint64 | np.uint32]:
    """
    Args:
        coordinates:nxm shape, m >=2
        filter_coordinates:same as coordiantes
        parallel:int
        x_col:int,default = 0
        y_col:int,default = 1
    Returns:
        results:1d array,uint64 type,return the index if the value of coordinates in filter coordinates
    """
    ...


@overload
def filter_data_with_coordinates(
    coordinates: npt.NDArray,
    filter_coordinates: npt.NDArray,
    parallel: int,
    x_field_name: str = "x",
    y_field_name: str = "y"
) -> npt.NDArray[np.uint64 | np.uint32]:
    """
    Args:
        coordinates:(n,) shape,the field must be a structured dtype!
        filter_coordinates:same as coordiantes
        parallel:int
        x_field_name:int,default = 0
        y_field_name:int,default = 1
    Returns:
        results:1d array,uint64 type,return the index if the value of coordinates in filter coordinates
    """
    ...


@overload
def filter_data_with_polygons(
    coordinates: npt.NDArray[np.int32],
    polygons: List[npt.NDArray[np.int32]],
    parallel: int,
    x_col: int = 0,
    y_col: int = 1
) -> npt.NDArray[np.uint64]:
    """
      Args:
        coordinates:n x m shape,m >=2
        polygons:a list of polygon,the element should be nx2 coors
        parallel:int,
        x_col:default is 0,the index of x
        y_col:default is 1
    Returns:
        results:1d array,uint64 type,return the index if the value of coordinates in filter coordinates
    """
    ...


@overload
def filter_data_with_polygons(
    coordinates: npt.NDArray[np.int32],
    polygons: List[npt.NDArray[np.int32]],
    parallel: int,
    x_field_name: str = "x",
    y_field_name: str = "y"
) -> npt.NDArray[np.uint64]:
    """
      Args:
        coordinates:n x m shape,m >=2
        polygons:a list of polygon,the element should be nx2 coors
        parallel:int,
        x_field_name:the name of x field,default is 'x'
        y_field_name:the name of y field,default is 'y'
    Returns:
        results:1d array,uint64 type,return the index if the value of coordinates in filter coordinates
    """
    ...


@overload
def filter_data_with_polygons(
    coordinates: npt.NDArray[np.int32],
    polygons: List[npt.NDArray[np.int32]],
    parallel: int,
    x_col: int = 0,
    y_col: int = 1
) -> npt.NDArray[np.uint64]:
    """
      Args:
        coordinates:nx2 shape,int32 array
        polygons:a list of polygon,the element should be nx2 coors
    Returns:
        results:1d array,uint64 type,return the index if the value of coordinates in filter coordinates
    """
    ...


class PyStatefulMask():

    @overload
    def __init__(self, w: int, h: int) -> None:
        ...

    @overload
    def __init__(self, w: int, h: int, polygons: List[npt.NDArray], x_col: int = 0, y_col=1) -> None:
        ...

    def update_with_coordinates(
        self, coordinates: npt.NDArray[np.int32], op: MaskUpdateKind, x_col: int = 0, y_col=1
    ) -> None:
        ...

    def update_with_polygons(self, polygons: List[npt.NDArray[np.int32]], op: MaskUpdateKind) -> None:
        ...

    def update_with_mask_and_rect(
        self,
        other_mask: PyStatefulMask,
        x1: int,
        y1: int,
        rw: int,
        rh: int,
        op: MaskUpdateKind,
        overflow_part_op: MaskOverflowPartProcessKind = MaskOverflowPartProcessKind.TraitAsBackground
    ) -> None:
        ...

    def update_with_mask(
        self,
        other_mask: PyStatefulMask,
        op: MaskUpdateKind,
        overflow_part_op: MaskOverflowPartProcessKind = MaskOverflowPartProcessKind.TraitAsBackground
    ) -> None:
        ...

    def get_chunk_mask_with_rect(self, x1: int, y1: int, rw: int, rh: int, color: int) -> npt.NDArray[np.uint8]:
        ...

    def get_chunk_mask(self, color: int) -> npt.NDArray[np.uint8]:
        ...

    def get_chunk_mask_coordinates_with_rect(self, x1: int, y1: int, rw: int, rh: int) -> npt.NDArray[np.int32]:
        ...

    def get_chunk_mask_coordinates(self) -> npt.NDArray[np.int32]:
        ...

    def get_chunk_mask_with_compress(self, stride: int, color: int, on_lt: bool = True) -> npt.NDArray[np.uint8]:
        ...

    def get_chunk_mask_with_compress_and_rect(
        self,
        x1: int,
        y1: int,
        rw: int,
        rh: int,
        stride: int,
        color: int,
        only_lt: bool = True
    ) -> npt.NDArray[np.uint8]:
        ...


@overload
def filter_data_with_mask(
    coordinates: npt.NDArray,
    mask: PyStatefulMask,
    stride: int = 1,
    filter_mode: BlockFilterMode = BlockFilterMode.Strict,
    x_col=0,
    y_col=1
) -> npt.NDArray[np.uint64]:
    ...


@overload
def filter_data_with_mask(
    coordinates: npt.NDArray,
    mask: PyStatefulMask,
    stride: int = 1,
    filter_mode: BlockFilterMode = BlockFilterMode.Strict,
    x_field_name="x",
    y_field_name="y"
) -> npt.NDArray[np.uint64]:
    ...


class StatefulVisualSamplingRunner():

    def __init__(
        self,
        data_file: str,
        result_dir: str,
        bin_size: int,
        max_block_size: int,
        min_block_size: int,
        prefetch_queue_size: int = 3,
        n_parse_workers: int = 2,
        n_compress_workers: int = 8
    ) -> StatefulVisualSamplingRunner:
        """
        Args:
            data_file:str,the file of of gene
            result_dir:str,the directory to save the bin sampling...
            bin_size:int
            max_block_size:int,the max block size of sampling,must be power of 2!
                if the max block size == chunk_size of gene file,will using fast function!
            min_block_size:int,the min block size of sampling,also the power of 2
            prefetch_queue_size:int,the cache queue size,default value is 3
            n_parse_workers:the n workers use to parse the data,if not use hdf5,we will parse it self!!! default 3
            n_compress_workers:the n workers use to compress with zstd default is 8
        """
        ...

    def init(self) -> Status:
        """
        init the impl ptr
        """
        ...

    def run(self) -> Status:
        """
        run the sampling task...
        """
        ...

    def run_with_async() -> None:
        "run with async"
        ...

    def wait_and_get_result() -> Status:
        """
        wait the running task and get the return result!
        """
        ...

    def stop_running_task() -> bool:
        """
        stop the running task,if success return True,else False
        """
        ...

    def is_valid() -> bool:
        """
        return True means current runner is valid with a sampling task
        False means nullptr!
        """
        ...

    def get_impl_kind() -> VisualSamplingRunnerImplKind:
        """
        return the impl kind,contains lock free and lock sync
        you can decide put the running task to different queue!
        """
        ...


def is_hdf5_threadsafe() -> bool:
    """
    return a flag,if True,means current hdf5 is thread safe...
    """
    ...


def filter_gene_file_with_coordinates(
    gene_file: str,
    output_gene_file: str,
    bin_sizes: List[int],
    coordinates: np.ndarray,
    coordinate_bin_size: int,
    allow_share_coordinate_ptr: bool = False,
    x_col: int = 0,
    y_col: int = 1,
    cache_policy: GeneCachePolicy = GeneCachePolicy.auto_cache_in_file,
    compress_kind: DatasetCompressKind = DatasetCompressKind.gzip,
    compress_level: int = 3
):
    """
    suppport parallel in python,just use python's threadpool to execute it!
    this function used for select the gene datas from the given condition(with selected coordinates),and make a new gene file
    Args:
        gene_file:str,a path,in c++,we always using utf8 to decode this,if the path is invalid,return false
        output_gene_file:the output gene file
        bin_sizes:a list of int,tell us which bin sizes you want to export!
        coordinates:numpy.array,shoud be n x m with int32 type(if other type,we try to convert to int32),m >= 2,if m==2,maybe faster(trigger the shared condition)  
        coordinate_bin_size:int,means which bin expression the coordinate from,like bin10,bin20,etc...
        allow_share_coordinate_ptr:bool,if True,we will pass the pointer to c++ directly,this is very useful for the large array!
        cache_policy:default is auto
        compress_kind:the output dataset's compress method,default is gzip
        compress_level:int,default is 3!
    """
    ...
