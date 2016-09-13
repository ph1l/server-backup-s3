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

## Crontab Example

This is an example setup of a server backup of all mounted filesystems monthly.

* Create a file to store backup credentials:

    sudo touch /etc/server-backup-s3.source
    sudo chmod 600 /etc/server-backup-s3.source
    sudo ${EDITOR} /etc/server-backup-s3.source

Use the following contents (with your valid backup creds:)

    export AWS_ACCESS_KEY_ID=AAAAAAA
    export AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxx

* Download public key for backup encryption

    sudo gpg --recv-keys CE4A0BF21E1C237DD8C400FAA39487B22697143F

* Here's an example crontab for root (`sudo crontab -e`)

    MAILTO=admin@example.com
    PATH=/usr/bin:/bin:/usr/sbin:/sbin
    # m h  dom mon dow   command
    1 0 1 * * . /etc/server-backup-s3.source && /usr/local/sbin/server-backup-s3 --encrypt --recipient CE4A0BF21E1C237DD8C400FAA39487B22697143F --bucket backups.example.com --region us-west-1
