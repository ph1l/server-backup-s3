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

class BackupFilesystem(object):

    def __get_cur_level(self):

        import sys
        import traceback

        try:
            with open(self.curlevel_filename) as level_file:
                self.curlevel = int(level_file.readline())
        except:
            self.curlevel = 0
            if self.verbose:
                print "DEBUG: Exception getting current level:"
                traceback.print_exc(file=sys.stdout)
                print "DEBUG: Setting current level to 0"

    def __gunzip_incremental_data(self):

        import gzip
        import os
        import shutil

        if self.curlevel == 0:
            # First Full Backup
            # cleanup previous incremental data
            if os.path.exists(self.incremental_filename):
                os.remove(self.incremental_filename)
            if os.path.exists(self.incremental_filename+".gz"):
                os.remove(self.incremental_filename+".gz")
        else:
            # Subsequent Incrementals
            # decompress incremental data from previous backup
            with gzip.open(self.incremental_filename+".gz", 'rb') as f_in, \
                    open(self.incremental_filename, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

    def __check_gpg_encryption(self, key_id, verbose=False):
        """
            test that we can encrypt to recipient
        """
        import subprocess

        gpg_check_command = [
            "gpg", "--quiet", "--trust-model", "always",
            "--encrypt", "--recipient", key_id
            ]

        gpg_process = subprocess.Popen(
            gpg_check_command,
            stdin=open("/dev/null"),
            stdout=open("/dev/null", 'w'),
            stderr=open("/dev/null", 'w')
            )
        return_code = gpg_process.wait()
        if return_code == 0:
            if verbose:
                print "DEBUG: encryption to", key_id, "succeeded"
            return True
        else:
            if verbose:
                print "DEBUG: encryption to", key_id, "failed"
            return False

    def __init__(self, source_filesystem, force_full=False, max_level=3,
                 encrypt=False, recipients=None, cache_dir=DEFAULT_CACHE_DIR,
                 verbose=False):

        import os

        if verbose:
            print "DEBUG: Backup filesystem:", source_filesystem

        self.verbose = verbose
        self.max_level = max_level
        self.clean_filesystem = source_filesystem.replace("/", "_")

        backup_cache_dir = cache_dir + "/" + self.clean_filesystem
        if not os.path.exists(backup_cache_dir):
            os.makedirs(backup_cache_dir)

        self.curlevel_filename = backup_cache_dir+"/curlevel"
        if force_full:
            self.curlevel = 0
        else:
            self.__get_cur_level()

        self.incremental_filename = backup_cache_dir+"/incr"
        self.__gunzip_incremental_data()

        self.tar_command = [
            "tar", "-C", source_filesystem, "--exclude-caches-under",
            "--listed-incremental="+self.incremental_filename,
            "--one-file-system", "-clpf", "-", "."
            ]

        self.encrypt = encrypt

        if encrypt:
            if verbose:
                print "DEBUG: encrypt to:", ", ".join(recipients)

            self.gpg_command = [
                "gpg", "--quiet", "--trust-model", "always", "--encrypt"
                ]

            num_recipients = 0
            for recipient in recipients:
                if self.__check_gpg_encryption(recipient):
                    self.gpg_command.extend(("--recipient", recipient))
                    num_recipients += 1
                else:
                    print "WARNING: Skipping encryption recipient:", \
                        recipient, "(encryption test failed)"
            if num_recipients < 1:
                raise Exception(
                    "Encryption requested, but no valid recipients found")

    def get_name(self):

        import datetime

        if self.encrypt:
            ext = ".tar.gpg"
        else:
            ext = ".tar.gz"

        return self.clean_filesystem + "-" + \
            datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "." + \
            str(self.curlevel) + ext

    def get_pipe(self):

        import subprocess

        self.tar_process = subprocess.Popen(
            self.tar_command,
            stdout=subprocess.PIPE)

        if self.encrypt:
            pipe_process = subprocess.Popen(
                self.gpg_command,
                stdin=self.tar_process.stdout,
                stdout=subprocess.PIPE)

        else:
            self.pipe_process = subprocess.Popen(
                ["gzip", "-c"],
                stdin=self.tar_process.stdout,
                stdout=subprocess.PIPE)

        self.tar_process.stdout.close()  # Allow tar_process to receive a
                                         # SIGPIPE if gpg_process exits.
        return pipe_process

    def __gzip_incremental_data(self):
        import gzip
        import os
        import shutil
        with open(self.incremental_filename, 'rb') as f_in, \
                gzip.open(self.incremental_filename+".gz", 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
        os.remove(self.incremental_filename)

    def __increment_level(self):
        with open(self.curlevel_filename, 'w') as level_file:
            if self.curlevel < self.max_level:
                level_file.write(str(self.curlevel+1)+"\n")
            else:
                level_file.write("0\n")

    def success(self):
        if self.verbose:
            print "DEBUG: backup completed successfully..."
        self.__gzip_incremental_data()
        self.__increment_level()

    def failure(self):

        import os

        print "Error: backup failed..."
        # Terminate tar process
        self.tar_process.terminate()
        # wait for process to stop
        self.tar_process.communicate()
        # remove new incremental data
        if os.path.exists(self.incremental_filename):
            os.remove(self.incremental_filename)
