import zstandard
import numpy as np
import os
import json
from stereo_map_tools._C_stereo_map_tools import StatefulVisualSamplingRunner, Status, VisualSamplingRunnerImplKind, is_hdf5_threadsafe
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Dict, Callable, Tuple, List
import sys
import logging
from threading import Lock

HDF5_WINDOWS_ENCODING = "utf-8"


def filename_encode(filename):
    """
    Encode filename for use in the HDF5 library.

    Due to how HDF5 handles filenames on different systems, this should be
    called on any filenames passed to the HDF5 library. See the documentation on
    filenames in h5py for more information.
    """
    filename = os.fspath(filename)
    if sys.platform == "win32":
        if isinstance(filename, str):
            return filename.encode(HDF5_WINDOWS_ENCODING, "strict")
        return filename
    return os.fsencode(filename)


def filename_decode(filename):
    """
    Decode filename used by HDF5 library.

    Due to how HDF5 handles filenames on different systems, this should be
    called on any filenames passed from the HDF5 library. See the documentation
    on filenames in h5py for more information.
    """
    if sys.platform == "win32":
        if isinstance(filename, bytes):
            return filename.decode(HDF5_WINDOWS_ENCODING, "strict")
        elif isinstance(filename, str):
            return filename
        else:
            raise TypeError("expect bytes or str, not %s" % type(filename).__name__)
    return os.fsdecode(filename)


def get_logger(name: str = "lazydog") -> logging.Logger:
    # 创建logger对象
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()

    # file_handler = logging.FileHandler('app.log')
    # file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    # file_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    # logger.addHandler(file_handler)
    return logger


def check_int(v) -> bool:
    if not isinstance(v, int) or v <= 0:
        return False
    return True


# the default name
class SamplingFileNames:
    info_file_name = "info.json"
    data_file_fmt = "{}.data"
    data_storage_file_name = "reader_map.json"


sampling_element_dtype = np.dtype([("x", "f4"), ("y", "f4"), ("gene_count", "i4"), ("mid_count", "i4")])
sampling_element_dtype_size = sampling_element_dtype.itemsize
sampling_index_dtype = np.dtype("u8")
sampling_index_size = sampling_index_dtype.itemsize
# uint64
sampling_count_size = 8

__sampling_read_cache_dict__ = {}


def read_sampling_chunk_data(result_dir: str, level_str: str, chunk_str: str) -> bytes:
    """
    Args:
        result_dir:str,the dir of sampling result
        level_str:a str will used as the prefix of file,key of map!
        chunk_str:xi_yi like
    """
    reader_map_file = os.path.join(result_dir, SamplingFileNames.data_storage_file_name)
    if reader_map_file not in __sampling_read_cache_dict__:
        with open(reader_map_file, "r") as f:
            reader_map = json.load(f)
            __sampling_read_cache_dict__[reader_map_file] = reader_map
    else:
        reader_map = __sampling_read_cache_dict__[reader_map_file]
    storage_info = reader_map[str(level_str)][chunk_str]
    data_file = os.path.join(result_dir, SamplingFileNames.data_file_fmt.format(level_str))
    with open(data_file, "rb") as f:
        storage_start = storage_info["start"]
        storage_size = storage_info["size"]
        f.seek(storage_start)
        data = bytearray(zstandard.decompress(f.read(storage_size)))
    data_view = memoryview(data)
    element_size = (len(data) - sampling_count_size) // (sampling_element_dtype_size + sampling_index_size)
    left = sampling_count_size
    right = sampling_count_size + sampling_element_dtype_size * element_size
    sampling_element_view = data_view[left:right]
    # shuffle it,and will change the ptr! not any copy!
    sampling_array = np.frombuffer(sampling_element_view, dtype=sampling_element_dtype)
    np.random.shuffle(sampling_array)
    return data


def clear_cache_dict(file_path: str) -> None:
    if file_path in __sampling_read_cache_dict__:
        __sampling_read_cache_dict__.pop(file_path)


class VisualSamplingParams:

    def __init__(
        self,
        data_file: str,
        result_dir: str,
        bin_size: int,
        max_block_size: int,
        min_block_size: int,
        prefetch_queue_size: int = 3,
        n_parse_workers: int = 2,
        n_compress_workers: int = 8,
        callback: Callable = None
    ) -> None:
        self.data_file = data_file
        self.result_dir = result_dir
        self.bin_size = bin_size
        self.max_block_size = max_block_size
        self.min_block_size = min_block_size
        self.prefetch_queue_size = prefetch_queue_size
        self.n_parse_workers = n_parse_workers
        self.n_compress_workers = n_compress_workers
        self.callback = callback


class VisualSamplingScheduler(object):

    def __init__(self, pool_size: int = 4, logger: logging.Logger = None):
        n = os.cpu_count()
        if pool_size <= 0 or pool_size > n:
            pool_size = n
        if logger is None:
            self.logger = get_logger()
            self.logger.info("using the default logger")
        else:
            self.logger = logger
        self.logger.info("initialize the pool with size {}".format(pool_size))
        self.parallel_pool = ThreadPoolExecutor(pool_size, "visual sampling")
        self.sequence_pool = ThreadPoolExecutor(1, "single visual sampling")
        # the running tasks
        self.running_tasks: Dict[str, Tuple[StatefulVisualSamplingRunner, Future]] = {}
        # the ready tasks!
        self.ready_tasks: List[Tuple[str, StatefulVisualSamplingRunner, Callable]] = []
        # protect the task queue!
        self.cache_lock = Lock()

    @staticmethod
    def key(file_path: str, bin_size: int) -> str:
        return "{}_{}".format(file_path, bin_size)

    def generate_callback(self, cache_key: str = None, other_callback: Callable = None) -> None:
        """
        generate a callback for the running task,invoke the w
        """

        def callback(f: Future) -> None:
            if other_callback is not None:
                other_callback()
            self.remove_task(cache_key=cache_key)

        return callback

    def remove_task(self, cache_key: str = None) -> None:
        """
        this is thread safe!
        to avoid that,while we remove a cache item from cache,but we call the
        cancel task,and got the remove the future,and it will be deconstruct!
        """
        with self.cache_lock:
            if cache_key in self.running_tasks:
                self.logger.info("remove key -> '{}' in cache!".format(cache_key))
                self.running_tasks.pop(cache_key)
            else:
                self.logger.info("cache key -> {} is already removed,maybe it is finished?".format(cache_key))

    def add_task_to_pool(self, runner: StatefulVisualSamplingRunner = None):
        pool: ThreadPoolExecutor = None
        f: Future = None
        if is_hdf5_threadsafe():
            pool = self.parallel_pool
        else:
            impl_kind = runner.get_impl_kind()
            if impl_kind == VisualSamplingRunnerImplKind.lock_free:
                pool = self.parallel_pool
            elif impl_kind == VisualSamplingRunnerImplKind.lock_sync:
                pool = self.sequence_pool
        if pool is not None:
            f = pool.submit(runner.run)
            if pool == self.parallel_pool:
                self.logger.info("submit to the parallel pool...")
            else:
                self.logger.info("submit to the sequence pool...")
        else:
            self.logger.info("the runner is invalid,so we will not start any task for it1")
        return f

    def deprecated_submit(
        self,
        data_file: str,
        result_dir: str,
        bin_size: int,
        max_block_size: int,
        min_block_size: int,
        prefetch_queue_size: int = 3,
        n_parse_workers: int = 2,
        n_compress_workers: int = 8,
        callback: Callable = None
    ) -> Future:
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
            callback:the callback you want to invoke!
        Returns:
            if success,return a asspcoated future of task,else return None
        """
        self.logger.warning(
            "{} is deprecated,use {} instead!".format(self.deprecated_submit.__name__, self.submit_batch.__name__)
        )
        cache_key = self.key(file_path=data_file, bin_size=bin_size)
        if cache_key in self.running_tasks:
            # raise RuntimeError("the running task is already in ready queue...")
            self.logger.info("the cache key -> {} is already in running queue!".format(cache_key))
            return None

        check_int_values = [
            bin_size, max_block_size, min_block_size, prefetch_queue_size, n_parse_workers, n_compress_workers
        ]

        for v in check_int_values:
            if not check_int(v):
                self.logger.info("fail to check the size...")
                return None

        runner = StatefulVisualSamplingRunner(
            data_file=filename_encode(data_file),
            result_dir=filename_encode(result_dir),
            bin_size=bin_size,
            max_block_size=max_block_size,
            min_block_size=min_block_size,
            prefetch_queue_size=prefetch_queue_size,
            n_parse_workers=n_parse_workers,
            n_compress_workers=n_compress_workers
        )
        if runner.init() != Status.kSuccess:
            self.logger.info("fail to init runner with cache key -> {}".format(cache_key))
            return None
        f = self.add_task_to_pool(runner=runner)
        if f is not None:
            f.add_done_callback(self.generate_callback(cache_key=cache_key, other_callback=callback))
            self.logger.info("add task with key -> {}".format(cache_key))
            # save the running pair!
            with self.cache_lock:
                self.running_tasks[cache_key] = [runner, f]
        return f

    def submit_batch(self, sampling_param_list: List[VisualSamplingParams] = None, start_run: bool = False) -> None:
        """
        Args:
            start_run:if True,we will start the running func immediately,else,just init,do not run it!on windows,this maybe block!
        """
        if start_run:
            self.logger.info(
                "we will start the sampling after initialize,if you submit several tasks,\
                    maybe block by the CALL_GUARD of hdf5,recommend set it False,\
                        and invoke start_ready_task func after submit!"
            )
        with self.cache_lock:
            for sampling_param in sampling_param_list:
                check_int_values = [
                    sampling_param.bin_size, sampling_param.max_block_size, sampling_param.min_block_size,
                    sampling_param.prefetch_queue_size, sampling_param.n_parse_workers,
                    sampling_param.n_compress_workers
                ]
                for v in check_int_values:
                    if not check_int(v):
                        self.logger.info(
                            "got bad int values -> {},just ignore file -> {}".format(v, sampling_param.data_file)
                        )
                        continue
                cache_key = self.key(file_path=sampling_param.data_file, bin_size=sampling_param.bin_size)
                if cache_key in self.running_tasks:
                    self.logger.info(
                        "the cache key -> {} is already in running queue!we never append it again!".format(cache_key)
                    )
                    continue
                runner = StatefulVisualSamplingRunner(
                    data_file=filename_encode(sampling_param.data_file),
                    result_dir=filename_encode(sampling_param.result_dir),
                    bin_size=sampling_param.bin_size,
                    max_block_size=sampling_param.max_block_size,
                    min_block_size=sampling_param.min_block_size,
                    prefetch_queue_size=sampling_param.prefetch_queue_size,
                    n_parse_workers=sampling_param.n_parse_workers,
                    n_compress_workers=sampling_param.n_compress_workers
                )
                if runner.init() != Status.kSuccess:
                    self.logger.info(
                        "fail to init runner for cache key -> {},so we will never put it to any queue!".
                        format(cache_key)
                    )
                    continue
                impl_kind: VisualSamplingRunnerImplKind = runner.get_impl_kind()
                if impl_kind != VisualSamplingRunnerImplKind.lock_free and impl_kind != VisualSamplingRunnerImplKind.lock_sync:
                    self.logger.info("the impl kind -> {} is unexpected!".format(impl_kind))
                if start_run:
                    f = self.add_task_to_pool(runner=runner)
                    if f is not None:
                        f.add_done_callback(
                            self.generate_callback(cache_key=cache_key, other_callback=sampling_param.callback)
                        )
                        self.running_tasks[cache_key] = (runner, f)
                        self.logger.info("add {} to running list!".format(cache_key))
                else:
                    self.ready_tasks.append((cache_key, runner, sampling_param.callback))
                    self.logger.info("add {} to ready list!".format(cache_key))

    def start_ready_tasks(self) -> None:
        """
        start the ready tasks,and then clear the running queue!
        """
        with self.cache_lock:
            for (cache_key, runner, callback) in self.ready_tasks:
                f = self.add_task_to_pool(runner=runner)
                if f is not None:
                    f.add_done_callback(self.generate_callback(cache_key=cache_key, other_callback=callback))
                    self.running_tasks[cache_key] = (runner, f)
                    self.logger.info('add {} to running list!'.format(cache_key))
            self.logger.info("now we will clear the ready queue!")
            self.ready_tasks.clear()

    def cancel_task(self, data_file: str) -> int:
        """
        data_file:the file you want to remove!
        """
        self.logger.info("we will remove all the task from data file -> {}".format(data_file))
        """
        the lock is very important,to make sure that while we invoke the stop running task
        the impl ptr is only nullptr or valid
        if not use lock,threadA invoke the stop_running_task,but the threadB delete the impl ptr
        then we invoke a func with null pointer,will got error!

        only two thread will access the impl ptr,one is the sampling func
        another is the cancel task,so we must make sure that thread safe of the two thread!
        """
        task_futures: List[Future] = []
        # get the lock,only keep the future obj,and invoke f.result() after release the lock!
        with self.cache_lock:
            self.logger.info(self.running_tasks)
            cache_items = list(self.running_tasks.items())
            for cache_key, (runner, f) in cache_items:
                if cache_key.startswith(data_file):
                    if runner.stop_running_task():
                        self.logger.info("successfully cancel the running task of -> {}".format(cache_key))
                        self.logger.info("waiting the runner clear the resource")
                        task_futures.append(f)
        if (len(task_futures) > 0):
            for task_future in task_futures:
                task_future.result()
        else:
            self.logger.info("can not find the cache key -> {},maybe it is already finished?".format(data_file))
        return len(task_futures)

    def cancel_task_2(self, data_file: str, bin_size: int) -> bool:
        cache_key = self.key(data_file, bin_size)
        task_future: Future = None
        with self.cache_lock:
            if cache_key in self.running_tasks:
                runner, f = self.running_tasks[cache_key]
                if runner.stop_running_task():
                    self.logger.info("successfully cancel the running task of -> {}".format(cache_key))
                    self.logger.info("waiting the runner clear the resource")
                    # the python future can use for multi time...
                    task_future = f
        if task_future is not None:
            # because f.result() maybe require got the lock!
            task_future.result()
        return (task_future is not None)

    def cancel_all_task(self) -> int:
        self.wait_unfinished_tasks(False)

    def wait_unfinished_tasks(self, wait: bool = False) -> None:
        task_futures = []
        with self.cache_lock:
            for cache_key in self.running_tasks:
                runner, f = self.running_tasks[cache_key]
                if not wait:
                    runner.stop_running_task()
                    self.logger.info("stop the running task -> {}".format(cache_key))
                task_futures.append(f)
        self.logger.info("waiting all the tasks...")
        # wait all the result!
        self.logger.info("wait ")
        for task_future in task_futures:
            task_future.result()

    def get_running_task_num(self) -> int:
        with self.cache_lock:
            return len(self.running_tasks)

    def get_ready_task_num(self) -> int:
        with self.cache_lock:
            return len(self.ready_tasks)

    def has_running_task(self) -> bool:
        with self.cache_lock:
            return len(self.running_tasks) > 0

    def has_ready_task(self) -> bool:
        with self.cache_lock:
            return len(self.ready_tasks) > 0
