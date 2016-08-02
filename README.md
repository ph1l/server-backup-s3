# server-backup-s3

Author: `"Philip Freeman" <elektron@halo.nu>`

This is a python backup script to do encrypted incremental tar backups to s3

## Dependencies

* tar
* gnupg
* python
* python boto

This utility is tested on Debian Wheeezy, Jessie, and Stretch with the default
`python-boto` package.

## Usage

    # export AWS_ACCESS_KEY_ID=AAAAAAA
    # export AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxx
    # server-backup-s3 -e -r KEY_ID -B S3_BUCKET -R AWS_REGION

See the --help for more info

## s3 Permissions

The AWS user that performs the backup uploads only needs access to
s3:PutObject in the backup bucket. Example IAM user inline policy:

    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "1",
                "Effect": "Allow",
                "Action": [
                    "s3:PutObject",
                    "s3:AbortMultipartUpload"
                ],
                "Resource": [
                    "arn:aws:s3:::server-backup.example.com/*"
                ]
            },
            {
                "Sid": "2",
                "Effect": "Allow",
                "Action": [
                    "s3:ListBucketMultipartUploads"
                ],
                "Resource": [
                    "arn:aws:s3:::server-backup.example.com"
                ]
            }
        ]
    }
