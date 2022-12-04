# haimtran 03 OCT 2022
# test multipart upload using
# high level sdk
# show multi-thread handling the upload
# ref: https://aws.amazon.com/premiumsupport/knowledge-center/s3-multipart-upload-cli/

import sys
import threading
import boto3
from boto3.s3.transfer import TransferConfig


s3 = boto3.resource("s3")


class TransferCallBack:
    """
    the s3 transfer manager periodically calls the __call__ method
    throughout the upload and download process so that it can take action,
    such as displaying the progress to the user
    """

    def __init__(self, target_size) -> None:
        """ """
        self._target_size = target_size
        self._total_transferred = 0
        self._lock = threading.Lock()
        self.thread_infor = {}

    def __call__(self, bytes_transferred):
        """
        this is periodically called by the s3 transfer manager
        """
        thread = threading.current_thread()
        with self._lock:
            self._total_transferred += bytes_transferred
            if thread.ident not in self.thread_infor.keys():
                self.thread_infor[thread.ident] = bytes_transferred
            else:
                self.thread_infor[thread.ident] += bytes_transferred
            target = self._target_size
            sys.stdout.write(
                f"\r{self._total_transferred} of {target} transferred"
                f"({(self._total_transferred / target) * 100:.2f}%)."
            )
            sys.stdout.flush()
            print(f"{self._total_transferred} of {target} thread {thread.ident}")


def upload_with_default_configuration(
    local_file_path, bucket_name, object_key, file_size_mb
):
    """
    configuration
    """
    transfer_callback = TransferCallBack(file_size_mb)
    s3.Bucket(bucket_name).upload_file(
        local_file_path, object_key, Callback=transfer_callback
    )
    return transfer_callback.thread_infor


def upload_with_chunksize_and_meta(
    local_file_path, bucket_name, object_key, file_size_mb, metadata=None
):
    """
    control the chunk size
    """
    transfer_callback = TransferCallBack(file_size_mb)
    config = TransferConfig(multipart_chunksize=1024 * 1024, max_concurrency=20)
    # extra_args = {"Metadata": metadata} if metadata else None
    s3.Bucket(bucket_name).upload_file(
        local_file_path,
        object_key,
        Config=config,
        # ExtraArgs=extra_args,
        Callback=transfer_callback,
    )
    return transfer_callback.thread_infor


def upload_with_high_threshold(local_file_path, bucket_name, object_key, file_size_mb):
    """
    setting a multipath threshold larger than the size of the file
    results in the trasfer manager sending the file as a standard upload
    instead of a multipart upload
    """
    transfer_callback = TransferCallBack(file_size_mb)
    config = TransferConfig(multipart_threshold=file_size_mb * 2)
    s3.Bucket(bucket_name).upload_file(
        local_file_path, object_key, Config=config, Callback=transfer_callback
    )
    return transfer_callback.thread_infor


if __name__ == "__main__":
    thread_infor = upload_with_chunksize_and_meta(
        "./setup.mov", "haimtran-workspace", "multipart-upload/setup.mov", 1434217919
    )
    print(thread_infor)
