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

# Path Defaults
###############
#

# DEFAULT_CACHE_DIR
#   defines where we cache local info about tar's listed-incremental archives

DEFAULT_CACHE_DIR = "/var/cache/backup"

# DEFAULT_TEMP_DIR
#   defines where we mount lvm snapshots for backups

DEFAULT_TEMP_DIR = "/tmp/backup"
