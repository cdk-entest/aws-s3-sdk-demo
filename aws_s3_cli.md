---
title: basic s3 cli
author: haimtran
---

## host a static web using s3

- using cli, create a bucket
- setup for hosting a static web
- update policy for public web
- empty bucket
- remove bucket

## create a bucket

export BUCKET=$mc-bucket-demo-110889

simple way

```bash
aws s3api create-bucket \
  --bucket $BUCKET \
  --region ap-southeast-1 \
  --create-bucket-configuration LocationConstraint=ap-southeast-1
```

more configuration via json

```bash
aws s3api create-bucket \
      --generate-cli-skeleton \
      > bucket.json
```

then configure the bucket.json

```bash
aws s3api create-bucket \
      --cli-input-json \
      file://bucket.json
```

## delete a bucket

empty a bucket first

```bash
aws s3 rm s3://$BUCKET/ --recursive
```

then delete the bucket

```bash
aws s3api delete-bucket
  --bucket $BUCKET \
  --region ap-southeast-1
```

or very simple

```bash
aws s3 rm s3://$BUCKET
```

## s3 static hosting

```bash
aws s3 website s3://$BUCKET/ \
  --index-document index.html \
  --error-document error.html
```

put bucket policy

```bash
aws s3api put-bucket-policy \
  --bucket $BUCKET \
  --policy file://policy.json
```

bucket policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": ["s3:GetObject"],
      "Resource": ["arn:aws:s3:::$BUCKET/*"]
    }
  ]
}
```
