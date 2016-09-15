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

from ServerBackupS3.defaults import DEFAULT_CACHE_DIR
from ServerBackupS3.defaults import DEFAULT_TEMP_DIR
from ServerBackupS3.utils import ensure_cachedir_tag
from ServerBackupS3.utils import get_system_hostname
from ServerBackupS3.utils import discover_filesystems
from ServerBackupS3.S3Upload import S3Upload
from ServerBackupS3.S3Upload import S3UploadError
from ServerBackupS3.LVM import VolumeGroup
from ServerBackupS3.BackupFilesystem import BackupFilesystem

def main():
    """
        parse arguments and kickoff backups
    """
    import argparse
    import os
    import sys
    import traceback

    # Argument Parser
    argparser = argparse.ArgumentParser(
        description="backup a filesystem to s3"
        )

    argparser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='print a bunch of debugging and status info',
        )

    argparser.add_argument(
        '-f', '--filesystem',
        action='append',
        help='filesystem path to backup',
        )
    argparser.add_argument(
        '-l', '--logical-volume',
        action='append',
        help='logical volume to backup',
        )

    argparser.add_argument(
        '-m', '--max-level',
        default=3,
        help='maximum incremental level',
        )
    argparser.add_argument(
        '-F', '--force-full',
        action='store_true',
        help='ignore current level and force full backup',
        )

    argparser.add_argument(
        '-e', '--encrypt',
        action='store_true',
        help='encrypt the backup with gpg',
        )
    argparser.add_argument(
        '-r', '--recipient',
        action='append',
        help='gpg recipient',
        )

    argparser.add_argument(
        '-B', '--bucket',
        help='s3 destination bucket',
        )
    argparser.add_argument(
        '-R', '--region',
        help='s3 destination region',
        )
    argparser.add_argument(
        '-s', '--subdir',
        default=get_system_hostname(),
        help='s3 destination bucket subdirectory',
        )

    argparser.add_argument(
        '-C', '--cache-dir',
        default=DEFAULT_CACHE_DIR,
        help='s3 destination region',
        )
    argparser.add_argument(
        '-T', '--temp-dir',
        default=DEFAULT_TEMP_DIR,
        help='temporary directory for mounting lvm snapshots',
        )

    argparser.add_argument(
        '-P', '--snapshot-percentage',
        type=int,
        default=100,
        help='percentage of source volume size to allocate for snapshot',
        )

    args = argparser.parse_args()

    # Check arguments
    if args.bucket == None:
        print "Error: No destination bucket specified."
        sys.exit(2)

    if args.region == None:
        print "Error: No destination regionspecified."
        sys.exit(2)

    if args.encrypt:
        if args.recipient == None:
            print "Error: requested encryption without any recipients."
            sys.exit(2)

    # Setup Cache Directory
    if not os.path.exists(args.cache_dir):
        os.makedirs(args.cache_dir)

    ensure_cachedir_tag(args.cache_dir, verbose=args.verbose)

    # Setup Temporary Directory
    if not os.path.exists(args.temp_dir):
        os.makedirs(args.temp_dir)

    ensure_cachedir_tag(args.temp_dir, verbose=args.verbose)

    backup_list = []
    # If no filesystems or logical volumes specified,
    if args.filesystem == None and args.logical_volume == None:
        # then get a list of local filesystems
        filesystems = discover_filesystems()
        if args.verbose:
            print "DEBUG: discovered filesystems:", ", ".join(filesystems)
        for filesystem in filesystems:
            backup_list.append(("FILESYSTEM", filesystem))
    else:
        # else, build list from args
        if args.filesystem != None:
            for filesystem in args.filesystem:
                backup_list.append(("FILESYSTEM", filesystem))
        if args.logical_volume != None:
            for volume in args.logical_volume:
                backup_list.append(("VOLUME", volume))

    upload = S3Upload(args.bucket, args.region, verbose=args.verbose)

    for (backup_type, backup_source) in backup_list:

        if backup_type == "VOLUME":

            (volume_group_name, logical_volume_name) = \
                backup_source.split("/")

            group = VolumeGroup(volume_group_name, verbose=args.verbose)
            volume = group.get_volume(logical_volume_name)

            # Make a snapshot
            snapshot = volume.make_snapshot(
                allocation_pct=args.snapshot_percentage)

            # Setup Mountpoint
            mountpoint = args.temp_dir + "/" + volume_group_name + \
                "/" + logical_volume_name

            if not os.path.exists(mountpoint):
                os.makedirs(mountpoint)

            # Mount it
            snapshot.ro_mount(mountpoint)

        elif backup_type == "FILESYSTEM":

            mountpoint = backup_source

        else:

            raise Exception("Internal Error")

        # Do the backup
        try:
            backup = BackupFilesystem(
                mountpoint,
                force_full=args.force_full,
                max_level=args.max_level,
                encrypt=args.encrypt,
                recipients=args.recipient,
                cache_dir=args.cache_dir,
                verbose=args.verbose
                )
        except:
            print "Error: Unexpected exception setting up backup:"
            traceback.print_exc(file=sys.stdout)

        else:

            try:
                upload.multipart_from_process(
                    args.subdir+"/"+backup.get_name(),
                    backup.get_pipe()
                    )

            except S3UploadError:
                print "Error: S3UploadError, failing backup"
                backup.failure()

            except:
                print "Error: Unexpected exception in upload:"
                traceback.print_exc(file=sys.stdout)
                print "failing backup..."
                backup.failure()

            else:
                backup.success()


        if backup_type == "VOLUME":

            ## Unmount the snapshot
            snapshot.umount()

            # Remove the snapshot
            snapshot.remove()


if __name__ == "__main__":
    main()
