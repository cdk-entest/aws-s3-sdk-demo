---
author: haimtran
title: basic boto3 sdk and cli
publishedDate: 03/DEC/2022
---

## Basic S3API

check versioning status using genearte-cli-skeleton option

```bash
aws s3api get-bucket-versioning --generate-cli-skeleton >> template.json
```

and

```bash
aws s3api get-bucket-versioning \
  -cli-input-json \
  file://template.json
```

## Head API

check a bucket name existing or not

```py
def verify_bucket_name(bucket_name: str):
    """
    verify existing of a bucket
    """
    # s3 client
    s3 = boto3.client('s3')
    #
    try:
        response = s3.head_bucket(Bucket=bucket_name)
        print(response)
        raise SystemExit("this bucket has already been created")
    except ClientError as error:
        error_code = int(error.response["Error"]["Code"])
        if error_code == 404:
            # 404 means the bucket does not exist
            print("the bucket not found, please proceed")
        if error_code == 403:
            # 403 means the bucket exist in another AWS account
            raise SystemExit("this bucket already owned by another AWS account")

def test_verify_bucket_name(bucket_name: str):
    """
    test raise
    """
    try:
        verify_bucket_name(bucket_name=bucket_name)
    except SystemExit as error:
        print(error)
```

## Upload Multipart Boto3 SDK

using a callback to monitor progress and threads

```py
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
```

test upload multi-part

```py
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
```

## Generate Pre-signed URL

generate pre-signed url

```py
def test_generate_signed_url(bucket_name: str, key: str):
    """
    generate signed url to view an image
    """
    # create s3 client
    s3 = boto3.client("s3")
    # generate pre_signed_url
    pre_signed_url = s3.generate_presigned_url(
        #
        ClientMethod='get_object',
        # bucket information
        Params={
            "Bucket": bucket_name,
            "Key": key
        },
        # in seconds the link expired
        ExpiresIn=3600,
        HttpMethod="GET"
    )
    #
    print(pre_signed_url)
    # download the object given the pre_signed_url
    try:
        response = requests.get(pre_signed_url)
        print(response)
        with open("image.png", "wb") as file:
            file.write(response.content)
    except ClientError as error:
        print(error)
```

## Access Point Policy

grant access to an IAM user named test. Please note that this policy allow

- access all object in the access point
- list objects in the access point

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Statement2",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::ACCOUNT_ID:user/test"
      },
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:ap-southeast-1:ACCOUNT_ID:accesspoint/test/object/*",
        "arn:aws:s3:ap-southeast-1:ACCOUNT_ID:accesspoint/test"
      ]
    }
  ]
}
```

similar for an IAM role assumed by EC2

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Statement2",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::ACCOUNT_ID:role/RoleForEc2ToAccessS3accessPoint"
      },
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:ap-southeast-1:ACCOUNT_ID:accesspoint/test/object/*",
        "arn:aws:s3:ap-southeast-1:ACCOUNT_ID:accesspoint/test"
      ]
    }
  ]
}
```

test list objects

```bash
aws s3api list-objects  --bucket arn:aws:s3:ap-southeast-1:392194582387:accesspoint/test
```

test get-object

```bash
aws s3api get-object --key test/image_1.png --bucket arn:aws:s3:ap-southeast-1:392194582387:accesspoint/test
```
