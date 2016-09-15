# vim:et:ts=4:sts=4:ai
"""
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

# S3 MULTIPART Settings
####################
#
# Limitations:
#  * Multipart uploads can have at most 10000 parts.
#  * Objects can be up to 5TB in total size.
#
# so, MAX_S3_OBJECT_SIZE / MAX_S3_OBJECT_SIZE must be less than 10000.
#
# (https://aws.amazon.com/blogs/aws/amazon-s3-multipart-upload/)
#

# MAX_S3_OBJECT_SIZE
#   defines the maximum object size we upload to s3

MAX_S3_OBJECT_SIZE = 1024*1024*1024*1024 # 1TB

# CHUNK_SIZE
#   defines the size of multi-part "chunks" we upload to s3

CHUNK_SIZE = 1024*1024*128 # 128MiB

# DEFAULT_S3_RETRY_TIMEOUT
#   time to wait, in seconds, before re attempting an S3 connection in failure
#   state.
#

DEFAULT_S3_RETRY_TIMEOUT = 60

# DEFAULT_S3_FAILURE_TIMEOUT
#   after timeout, in seconds, give up and let backup fail
#

DEFAULT_S3_FAILURE_TIMEOUT = 7200


# Path Defaults
###############
#

# DEFAULT_CACHE_DIR
#   defines where we cache local info about tar's listed-incremental archives

DEFAULT_CACHE_DIR = "/var/cache/backup"

# DEFAULT_TEMP_DIR
#   defines where we mount lvm snapshots for backups

DEFAULT_TEMP_DIR = "/tmp/backup"
