# haimtran 04 DEC 2022
# basic s3 sdk
# using json.dumps(response, ident=2, default=str)
import os
import io
from datetime import datetime
import boto3
from boto3.s3.transfer import TransferConfig
import json

# parameter
BUCKET_NAME = ""
PREFIX = "test/"


class UploadCallback:
    """
    upload callback
    """

    def __init__(self, target_size) -> None:
        """
        init with target size or file szie should be uploaded
        """
        self._target_size = target_size
        self._total_uploaded = 0

    def __call__(self, bytes_uploaded) -> None:
        """
        this called periodically by s3 sdk
        """
        self._total_uploaded += bytes_uploaded
        # uploaded in percentage
        uploaded_percent = self._total_uploaded / self._target_size * 100.0
        print(
            f"bytes uloaded {self._total_uploaded} or {uploaded_percent:2.2f}%"
        )


def upload_callback(bytes_uploaded):
    """
    callback periodicallyed called during uploading
    """
    print(bytes_uploaded)


def download_callback(bytes_downloaded):
    """
    call back when downloading file from s3
    """
    print(bytes_downloaded)


# =================================LIST=================================
def test_list_buckets():
    """
    list bucket in an account
    """
    # create low-level client
    s3 = boto3.client("s3")
    # send request to list bucket
    response = s3.list_buckets()
    # parse result
    buckets = response["Buckets"]
    # print each bucket
    for bucket in buckets:
        # print(bucket["Name"])
        print(bucket)


def test_list_object(bucket_name: str, prefix: str):
    """
    list object within a bucket and prefix
    """
    # low level client s3
    s3 = boto3.client("s3")
    # lits object within a object and a prefix
    response = s3.list_objects(Bucket=bucket_name, Prefix=prefix)
    # print response in json format
    print(type(response))
    print(json.dumps(response, indent=2, default=str))


# =================================PUT=================================
def test_put_object(bucket_name: str, key: str):
    """
    upload an object to s3
    """
    # time stamp
    time_stamp = datetime.now().strftime("%m/%d/%Y, %H:%M:%S.%f")
    # low level client s3
    s3 = boto3.client("s3")
    # upload object to s3
    response = s3.put_object(
        Bucket=bucket_name,
        Key=key,
        # bytes or seekable file-like object
        Body=bytes(f"Hello Dev class {time_stamp}", encoding="utf-8"),
    )
    # file
    with open(
        "data.txt",
        "rb",
    ) as file:
        response = s3.put_object(Bucket=bucket_name, Key=key, Body=file)
        print(json.dumps(response, indent=2, default=str))


def test_upload_file(file_name: str, bucket_name: str, key: str):
    """
    download file from s3. check boto.s3.TransferConfig
    """
    # create s3 client
    s3 = boto3.client("s3")
    # upload file
    response = s3.upload_file(Filename=file_name, Bucket=bucket_name, Key=key)
    # upload file object
    with open("data.txt", "rb") as file:
        s3.upload_fileobj(file, Bucket=bucket_name, Key=key)
    print(json.dumps(response, indent=2, default=str))


def test_bucket_upload_file(bucket_name: str, key: str, file_name: str):
    """
    upload file to s3 using high level api
    """
    # high level bucket resource
    bucket = boto3.resource("s3").Bucket(bucket_name)
    # upload file to s3
    response = bucket.upload_file(Filename=file_name, Key=key)
    print(response)


def test_bucket_upload_callback(bucket_name: str, key: str, file_name: str):
    """
    test upload file to s3 with callback
    """
    # get file size in byte
    target_size = os.stat("setup.mov").st_size
    # high level bucket resource
    bucket = boto3.resource("s3").Bucket(bucket_name)
    # upload file to s3
    bucket.upload_file(Filename=file_name, Key=key, Callback=UploadCallback(target_size=target_size))


def test_multipart_upload(bucket_name: str, key: str, file_name: str):
    """
    test upload file to s3 using multipart
    """
    # get file size in byte
    target_size = os.stat("setup.mov").st_size
    # high level bucket resource
    bucket = boto3.resource('s3').Bucket(bucket_name)
    # upload file to s3
    start_time = datetime.now()
    bucket.upload_file(
        Filename=file_name, 
        Key=key,
        Callback=UploadCallback(target_size=target_size),
        Config=TransferConfig(
            # mutiparth_threshold default 8388608 (8MB)
            multipart_threshold=8388608,
            # partition size of each part default 262144 (256KB)
            multipart_chunksize=1024*1024,
            # maximum number of thread default 10
            max_concurrency=100,
            # use thread
            use_threads=True
        )
    )
    # stop time
    stop_time = datetime.now()
    # duration 
    dur = stop_time - start_time
    print(f"start {start_time} stop {stop_time} dur {dur.total_seconds()}sec")


# =================================GET=================================
def test_get_object(bucket_name: str, key: str):
    """
    get object. return a Body stream
    """
    s3 = boto3.client("s3")
    # get object which return binary stream
    response = s3.get_object(Bucket=bucket_name, Key=key)
    print(json.dumps(response, indent=2, default=str))
    # write the return StreamingBody to local file
    # which is iterator and read each byte
    with io.FileIO("download_data.txt", "w") as file:
        for x in response["Body"]:
            file.write(x)


def test_download_file(bucket_name: str, key: str, file_name: str):
    """
    test download file
    """
    # create s3 client
    s3 = boto3.client("s3")
    # download file
    response = s3.download_file(Bucket=bucket_name, Key=key, Filename=file_name)
    print(response)


def test_bucket_download_file(bucket_name: str, key: str, file_name: str):
    """
    high level api to download object
    """
    # high level bucket resource
    bucket = boto3.resource("s3").Bucket(bucket_name)
    # download an object
    response = bucket.download_file(Key=key, Filename=file_name)
    print(response)


def test_bucket_download_callback(bucket_name: str, key: str, file_name: str):
    """
    download file with callback
    """
    # high level s3 resource
    bucket = boto3.resource("s3").Bucket(bucket_name)
    # download a file
    response = bucket.download_file(
        Key=key, Filename=file_name, Callback=download_callback, Config=None
    )
    print(response)


def test_generate_signed_url(bucket_name: str, key: str):
    """
    generate signed url to view an image
    """


if __name__ == "__main__":
    # test_list_buckets()
    # test_list_object(
    #     bucket_name=BUCKET_NAME,
    #     prefix=PREFIX
    # )
    # test_put_object(
    #     bucket_name=BUCKET_NAME,
    #     key="test/{0}.txt".format(str(datetime.now()).replace(' ', '-'))
    # )
    # test_upload_file(
    #     file_name="data.txt",
    #     bucket_name=BUCKET_NAME,
    #     key=f"test/file_upload_{str(datetime.now())}.txt"
    # )
    # test_get_object(
    #     bucket_name=BUCKET_NAME,
    #     key="test/file_upload_2022-12-04 03:38:44.467669.txt"
    # )
    # test_download_file(
    #     bucket_name=BUCKET_NAME,
    #     key="test/file_upload_2022-12-04 03:38:44.467669.txt",
    #     file_name="download_file.txt"
    # )
    # test_bucket_download_file(
    #     bucket_name=BUCKET_NAME,
    #     key="test/file_upload_2022-12-04 03:38:44.467669.txt",
    #     file_name="download_file.txt"
    # )
    # test_bucket_upload_file(
    #     bucket_name=BUCKET_NAME,
    #     key="test/upload_file_{0}".format(str(datetime.now())),
    #     file_name="data.txt",
    # )
    # test_bucket_download_callback(
    #     bucket_name=BUCKET_NAME,
    #     key="test/upload_file_2022-12-04 04:23:54.784127",
    #     file_name="download_file.txt"
    # )
    # test_bucket_upload_callback(
    #     bucket_name=BUCKET_NAME, key="test/upload_video.mov", file_name="setup.mov"
    # )
    test_multipart_upload(
        bucket_name=BUCKET_NAME,
        key="test/multipart_upload.mov",
        file_name="setup.mov"
    )
