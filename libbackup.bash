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
IFS=$'\t\n'

BACKUP_CACHE_DIR=/var/cache/libbashbackup

VERBOSE=0

function timestamp()
{
    date +"%Y%m%d-%H%M%S.%Z"
}

function log()
{
    local level="${1}"
    local message="${2}"
    if [ ${level} -le ${VERBOSE} ]; then
        echo "$(timestamp) ${message}" 1>&2
    fi
}

function get_backup_description()
# ARGS: SOURCE_DIR
{
    local source_dir=${1}
    local description="$(hostname -f)-${source_dir//\//_}"

    log 5 "got description \"${description}\" from source_dir \"${source_dir}\""
    echo "${description}"
}

function get_curlevel()
# ARGS: SOURCE_DIR
{
    local source_dir=${1}
    local description=$( get_backup_description "${source_dir}")
    local incremental_data_dir=${BACKUP_CACHE_DIR}/incremental_data
    local curlevel_file=${incremental_data_dir}/${description}.curlevel

    if [ ! -d "${incremental_data_dir}" ]; then
        mkdir -p "${incremental_data_dir}"
    fi

    if [ ! -f "${curlevel_file}" ]; then
        echo 0 >"${curlevel_file}"
    fi

    local curlevel=$(cat "${curlevel_file}")
    #TODO: Check that level is numeric, set to 0 if not.

    log 5 "got curlevel \"${curlevel}\" from source_dir \"${source_dir}\""
    echo ${curlevel}
}

function do_incremental_backup()
# ARGS: SOURCE_DIR LEVEL_LIMIT
{

    local source_dir=${1}
    local level_limit=${2}

    local general_tar_opts=$'--warning=no-file-ignore\t--exclude-caches-under\t--one-file-system\t-clp'

    local description=$( get_backup_description "${source_dir}" )

    local incremental_data_dir=${BACKUP_CACHE_DIR}/incremental_data
    local curlevel_file=${incremental_data_dir}/${description}.curlevel
    local incremental_file=${incremental_data_dir}/${description}.g
    local success_file=${incremental_data_dir}/${description}.success

    local curlevel=$( get_curlevel "${source_dir}" )

    if [ ${curlevel} -eq 0 ]; then
        for file in "${incremental_file}\t${incremental_file}.gz"; do
            if [ -e "${file}" ]; then
                rm ${file}
            fi
        done
    elif [ ${curlevel} -gt 0 ]; then
        gunzip -c ${incremental_file}.gz > ${incremental_file}
    else
        echo "ERROR: curlevel (${curlevel}) doesn't make sense" 1>&2
	exit 1
    fi

    log 3 "backing up \"${source_dir}\" with incremental_file \"${incremental_file}\""
    tar -C "${source_dir}" ${general_tar_opts} --listed-incremental="${incremental_file}" -f - .

    log 3 "compressing incremental_file \"${incremental_file}\""
    gzip -c ${incremental_file} > ${incremental_file}.gz
    rm ${incremental_file}

    if [ ${curlevel} -ge ${level_limit} ]; then
        echo 0 > ${curlevel_file}
    else
        echo $(( ${curlevel} + 1 )) > ${curlevel_file}
    fi

    touch ${success_file}
    log 2 "success backing up \"${source_dir}\""
}

function encrypt_stream()
# ARGS: RECIPIENTS
{
    local recipients="${1}"
    local gpg_recipient_opts=""
    for recipient in ${recipients}; do
        if ! gpg --list-keys ${recipient} > /dev/null 2>&1; then
            echo "Attempting to download GPG Key: ${recipient}" 1>&2
            gpg --recv-key ${recipient}
        fi
        gpg_recipient_opts="${gpg_recipient_opts}-r ${recipient} "
    done
    gpg --quiet --trust-model always -e "${gpg_recipient_opts}"
}

function upload_stream_to_s3()
# ARGS: BACKUP_URL
{
    local backup_url=${1}

    # TODO: check s3cmd version supports stdin

    s3cmd --quiet put - ${backup_url}
}

# Example Usage:
#
#BACKUP_FROM="/tmp"
#LEVEL_LIMIT=3
#ENCRYPT_TO=$'CE4A0BF21E1C237DD8C400FAA39487B22697143F\t0B0A72DD7A25C9D61DFD20DF115D31AF95C7423D'
#DESCRIPTION=$(get_backup_description "${BACKUP_FROM}")
#LEVEL=$(get_curlevel "${BACKUP_FROM}")
#DATE=$(date +%Y%m%d-%H%M%S)
#S3_BUCKET="backups.example.com"
#S3_URL="s3://${S3_BUCKET}/${DESCRIPTION}/${DATE}.${LEVEL}.tar.gpg"
#
#do_incremental_backup "${BACKUP_FROM}" "${LEVEL_LIMIT}" | \
#    encrypt_stream "${ENCRYPT_TO}" | \
#    upload_stream_to_s3 "${S3_URL}"
