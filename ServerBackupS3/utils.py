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

def ensure_cachedir_tag(cache_dir, verbose=False):
    """
        check for, create CACHEDIR.TAG in cache_dir
    """

    import os

    if not os.path.exists(cache_dir + "/CACHEDIR.TAG"):
        if verbose:
            print "DEBUG: creating CACHEDIR.TAG in", cache_dir
        with open(cache_dir + "/CACHEDIR.TAG", "w") as cachedir_tag:
            cachedir_tag.write("Signature: 8a477f597d28d172789f06886806bc55\n")

def get_system_hostname():
    """
        get system hostname
    """
    import socket

    return socket.getfqdn()

def discover_filesystems():
    """
        auto-magically discover filesystems to backup
    """

    import os
    import re

    re_mountpoint = re.compile(r'^[^#]\S*\s+(/\S*)')

    filesystems = []

    with open("/etc/fstab") as fstab:
        for line in fstab.readlines():
            m_mountpoint = re_mountpoint.match(line)
            if m_mountpoint:
                mountpoint = m_mountpoint.group(1)
                if os.path.ismount(mountpoint):
                    filesystems.append(mountpoint)
    return filesystems
