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

class LogicalVolumeSnapshot(object):

    def __init__(self, volume, name, size, verbose=False):
        import subprocess

        self.volume = volume
        self.name = name
        self.mounted = False
        self.verbose = verbose

        lvcreate_cmd = ["lvcreate", "-L"+str(size)+"B", "-s", "-n",
                        self.name, self.volume.group.name + "/"
                        + self.volume.name]

        lvcreate_process = subprocess.Popen(lvcreate_cmd)
        return_code = lvcreate_process.wait()
        if return_code != 0:
            raise Exception("Error: command failed")

        self.device = "/dev/"+self.volume.group.name+"/"+self.name

    def is_mounted(self):
        return self.mounted

    def ro_mount(self, mountpoint):
        import subprocess

        if self.is_mounted():
            raise Exception("Snapshot already mounted.")
        mount_cmd = ["mount", "-o", "ro", self.device, mountpoint]
        mount_process = subprocess.Popen(mount_cmd)
        return_code = mount_process.wait()
        if return_code != 0:
            raise Exception("Error: command failed")
        elif self.verbose:
            print "DEBUG: Successfully mounted", self.device, "on", \
                mountpoint

        self.mounted = True

    def umount(self):
        import subprocess
        import time

        #Avoid race conditions:
        time.sleep(2)
        if not self.is_mounted():
            raise Exception("Snapshot not mounted.")
        umount_cmd = ["umount", self.device]
        umount_process = subprocess.Popen(umount_cmd)
        return_code = umount_process.wait()
        if return_code != 0:
            raise Exception("Error: command failed")
        elif self.verbose:
            print "DEBUG: Successfully umounted", self.device

        self.mounted = False

    def remove(self):
        import subprocess

        if self.is_mounted():
            raise Exception("Snapshot mounted.")
        lvremove_cmd = ["lvremove", "-f", self.volume.group.name + "/" + \
            self.name]

        lvremove_process = subprocess.Popen(lvremove_cmd)
        return_code = lvremove_process.wait()
        if return_code != 0:
            raise Exception("Error: command failed")
        elif self.verbose:
            print "DEBUG: Successfully removed", self.name


class LogicalVolume(object):
    def __init__(self, group, volume_name, verbose=False):
        import re

        self.re_number = re.compile(r'^\s*(\d+)')
        self.group = group
        self.name = volume_name
        self.verbose = verbose

    def get_size(self):
        import subprocess

        size_cmd = ["lvs", "--noheadings", "--units", "B",
                    self.group.name + "/" + self.name, "-o", "lv_size"]

        size_process = subprocess.Popen(size_cmd, stdout=subprocess.PIPE)
        return_code = size_process.wait()
        if return_code != 0:
            raise Exception("Error: command failed")
        output = size_process.stdout.read()
        m_number = self.re_number.match(output)
        if m_number == None:
            raise Exception("Error: parsing command output: "+output)
        size = int(m_number.group(1))
        if self.verbose:
            print "DEBUG: got LogicalVolume size:", size
        return size

    def make_snapshot(self, allocation_pct=100):
        import datetime

        lv_size = self.get_size()
        snap_allocation = (
            (int(
                lv_size * float(allocation_pct/100.0)   # Calculate percentage
            ) / 512) * 512                              # Use a 512B boundry
            + (1024*1024*128)                           # add 128MB for overhead
            )
        if self.verbose:
            print "DEBUG: "+str(allocation_pct)+"% of "+str(lv_size)+ \
                "B = "+str(snap_allocation)+"B"
        snap_name = self.name+".snapshot." + \
            datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        if self.verbose:
            print "DEBUG: generating snapshot", snap_name, "in", self.group.name
        return LogicalVolumeSnapshot(self, snap_name, snap_allocation,
                                     verbose=self.verbose)


class VolumeGroup(object):
    def __init__(self, group_name, verbose=False):
        self.name = group_name
        self.verbose = verbose

        # TODO: Validation

    def get_volume(self, volume_name):
        return LogicalVolume(self, volume_name, verbose=self.verbose)
