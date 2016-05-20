# server-backup-s3

Author: `"Philip Freeman" <elektron@halo.nu>`

This is a bash backup script to do encrypted incremental tar backups to s3

## Dependencies

* Linux
* s3cmd (>=1.5.0)

## Usage

    # ./server-backup-s3 <CONFIG_FILE>

See the beginning of server-backup-s3 script for detailed configuration
description.

    # ./lvm-snapshot-backup-s3 <CONFIG_FILE>

See the beginning of lvm-snapshot-backup-s3 script for detailed
configuration description.

## s3 Permissions

The AWS user that performs the backup uploads only needs access to
s3:PutObject in the backup bucket. Example IAM user inline policy:

    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "Stmt1456902749000",
                "Effect": "Allow",
                "Action": [
                    "s3:PutObject"
                ],
                "Resource": [
                    "arn:aws:s3:::backup.example.com/*"
                ]
            }
        ]
    }
