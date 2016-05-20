#!/bin/bash

#    Copyright 2016 Philip J Freeman <elektron@halo.nu>

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

set -euo pipefail
IFS=$'\n\t'

function lv_size()
{
    local vg_name=${1}
    local lv_name=${2}
    local size=$(
            lvs --noheadings --units B ${vg_name}/${lv_name} -o lv_size \
                | egrep -o '[0-9]+'
        )
    log 2 "got size ${size}B for ${vg_name}/${lv_name}"
    echo ${size}
}

function lv_make_snap()
{
    local vg_name=${1}
    local lv_name=${2}
    local alloc_percent=100
    local lv_size=$(lv_size ${vg_name} ${lv_name})
    local snap_alloc=$((
            ((((${lv_size} * ${alloc_percent}) / 100) /512) *512)
            + (1024*1024*128)
        ))
    log 2 "${alloc_percent}% of ${lv_size}B = ${snap_alloc}B"
    local snap_lv_name="${lv_name}.snapshot.$(timestamp)"
    log 1 "generating snapshot ${snap_lv_name} in ${vg_name}"

    lvcreate -L${snap_alloc}B -s -n ${snap_lv_name} ${vg_name}/${lv_name} > /dev/null
    echo ${snap_lv_name}
}

function lv_remove()
{
    local vg_name=${1}
    local lv_name=${2}

    if ! echo "${lv_name}" | grep '\.snapshot\.' > /dev/null; then
        log 0 "ERROR: refusing to remove non-snapshot lv ${vg_name}/${lv_name}"
	exit 1
    fi
    log 1 "force removing snapshot: ${vg_name}/${lv_name}"
    lvremove -f ${vg_name}/${lv_name} > /dev/null
}
