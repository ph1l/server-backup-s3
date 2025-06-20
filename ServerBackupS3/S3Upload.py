# vim:et:ts=4:sts=4:ai
"""
    s3-backup

    Copyright 2016 Philip J Freeman <elektron@halo.nu>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import boto3


class S3UploadError(Exception):
    pass


class S3Upload(object):

    def __init__(self, bucket_name, region, verbose=False):

        self.verbose = verbose
        self.host = "s3-"+region+".amazonaws.com"
        self.bucket_name = bucket_name
        self.conn = None
        self.s3 = boto3.Session().resource("s3")


    def multipart_from_process(self, backup_name, process, verbose=False):

        self.s3.Object(self.bucket_name, backup_name).upload_fileobj(process.stdout)

        if self.verbose:
            print("DEBUG: done with upload of", backup_name)

        return_code = process.poll()

        if verbose:
            print("DEBUG: process exited with code:", return_code)

        return True
