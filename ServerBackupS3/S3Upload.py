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
from ServerBackupS3.defaults import MAX_S3_OBJECT_SIZE
from ServerBackupS3.defaults import CHUNK_SIZE
from ServerBackupS3.defaults import DEFAULT_S3_RETRY_TIMEOUT
from ServerBackupS3.defaults import DEFAULT_S3_FAILURE_TIMEOUT


class S3UploadError(Exception):
    pass


class S3Upload(object):

    def __connect_to_bucket(self):

        from boto.s3.connection import S3Connection
        from boto.s3.connection import OrdinaryCallingFormat

        if self.verbose:
            print "DEBUG: Setting up S3Connection to", \
                self.host+":"+self.bucket_name

        self.conn = S3Connection(
            host=self.host,
            calling_format=OrdinaryCallingFormat()
            )
        self.bucket = self.conn.get_bucket(self.bucket_name, validate=False)

    def __init__(self, bucket_name, region, verbose=False):

        self.verbose = verbose
        self.host = "s3-"+region+".amazonaws.com"
        self.bucket_name = bucket_name
        self.conn = None
        self.bucket = None
        self.__connect_to_bucket()

    def multipart_from_process(self, backup_name, process,
                               verbose=False):
        import socket
        import time
        import cStringIO
        import sys
        import traceback

        if self.verbose:
            print "DEBUG: Multipart Upload of", backup_name

        multipart_upload = self.bucket.initiate_multipart_upload(backup_name)
        part_num = 0
        object_num = 0
        bytes_uploaded = 0

        while True:
            # READ INPUT DATA FROM PIPE
            output = process.stdout.read(CHUNK_SIZE)

            if output == '' and process.poll() is not None:
                break

            if output:
                bytes_read = len(output)
                # Handle backups larger than MAX_S3_OBJECT_SIZE
                if bytes_uploaded + bytes_read > MAX_S3_OBJECT_SIZE:
                    if self.verbose:
                        print "DEBUG: OVERFLOWING MAX_S3_OBJECT_SIZE."
                    # finish multipart upload
                    multipart_upload.complete_upload()

                    # reset counters
                    part_num = 0
                    object_num += 1
                    bytes_uploaded = 0

                    # setup next upload object
                    multipart_upload = self.bucket.initiate_multipart_upload(
                        "%s.%02d"%(backup_name, object_num)
                        )

                    if self.verbose:
                        print "DEBUG: setup next upload object:", \
                            "%s.%02d"%(backup_name, object_num)

                part_num += 1

                while True:
                    if self.verbose:
                        print "DEBUG: TRYING UPLOAD CHUNK:", \
                            part_num, " len:", len(output)
                    try:
                        upload_fp = cStringIO.StringIO(output)
                        multipart_upload.upload_part_from_file(
                            upload_fp, part_num)
                        bytes_uploaded += bytes_read
                        break

                    except socket.error:
                        print "Warning: socket error in part upload:"
                        traceback.print_exc(file=sys.stdout)
                        multipart_upload = None # abandon current mpu object
                        first_fail_time = time.time()

                        while True:
                            # TRY TO RECONNECT TO S3
                            try:
                                print "  Trying to reconnect to S3"
                                self.__connect_to_bucket() # reconnect to bucket

                                # find the mpu
                                for upload in \
                                    self.bucket.get_all_multipart_uploads():

                                    print "  Check multi-part upload: %s"%(
                                        upload.key_name)

                                    if (
                                            object_num == 0 and
                                            upload.key_name == backup_name
                                        ) or (
                                            object_num > 0 and
                                            upload.key_name == "%s.%02d"%(
                                                backup_name, object_num)
                                        ):
                                        print " that's it..."
                                        multipart_upload = upload
                                break # from out of while True..

                            except socket.error:

                                if (time.time() > (first_fail_time +
                                                   DEFAULT_S3_FAILURE_TIMEOUT)):

                                    raise S3UploadError(
                                        "Error: reached hard fail timeout"
                                        )

                                print "Warning: socket error while "+ \
                                    "reconnecting:"
                                traceback.print_exc(file=sys.stdout)
                                print "will retry in"+ \
                                    str(DEFAULT_S3_RETRY_TIMEOUT)+"s"

                                time.sleep(DEFAULT_S3_RETRY_TIMEOUT)

        if self.verbose:
            print "DEBUG: done with upload of", backup_name, \
                "in", object_num+1, "objects"

        return_code = process.poll()

        if verbose:
            print "DEBUG: process exited with code:", return_code
        multipart_upload.complete_upload()

        return True
