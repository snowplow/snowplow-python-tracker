#!/bin/bash
set -e

project_path="/vagrant"
python_bin="~/snowplow-python-2.7-tracker-environment/bin/python2.7"

# Similar to Perl die
function die() {
	echo "$@" 1>&2 ; exit 1;
}

# Check if our Vagrant box is running. Expects `vagrant status` to look like:
#
# > Current machine states:
# >
# > default                   poweroff (virtualbox)
# >
# > The VM is powered off. To restart the VM, simply run `vagrant up`
#
# Parameters:
# 1. out_running (out parameter)
function is_running {
	[ "$#" -eq 1 ] || die "1 argument required, $# provided"
	local __out_running=$1

	set +e
	vagrant status | sed -n 3p | grep -q "^default\s*running (virtualbox)$"
	local retval=${?}
	set -e
	if [ ${retval} -eq "0" ] ; then
		eval ${__out_running}=1
	else
		eval ${__out_running}=0
	fi
}

# Get version, checking we are on the latest
#
# Parameters:
# 1. out_version (out parameter)
# 2. out_error (out parameter)
function get_version {
	[ "$#" -eq 2 ] || die "2 arguments required, $# provided"
	local __out_version=$1
	local __out_error=$2

	# Extract the version from package.json using Node and save it in a file named "VERSION"
	vagrant ssh -c "cd ${project_path} && ${python_bin} -c \"v={}; execfile('snowplow_tracker/_version.py', v); print v['__version__']\" > VERSION"
	file_version=`cat VERSION`
	tag_version=`git describe --abbrev=0 --tags`
	if [ ${file_version} != ${tag_version} ] ; then
		eval ${__out_error}="'File version ${file_version} != tag version ${tag_version}'"
	else
		eval ${__out_version}=${file_version}
	fi
}

# Go to parent-parent dir of this script
function cd_root() {
	source="${BASH_SOURCE[0]}"
	while [ -h "${source}" ] ; do source="$(readlink "${source}")"; done
	dir="$( cd -P "$( dirname "${source}" )/.." && pwd )"
	cd ${dir}
}

function upload_to_pypi() {

	# Register the new release with PyPI
	echo "Registering the release with PyPI. Choose option 1..."
	vagrant ssh -c "cd ${project_path} && ${python_bin} setup.py register"

	# Upload the new release to PyPI
	echo "Uploading the file to PyPI. IMPORTANT: PyPI does not allow a file to be re-uploaded."
	read -p "Do you want to upload the file to PyPI? [Y/N]" -n 1 -r
	if [[ $REPLY =~ ^[Yy]$ ]]
	then
		# We have to upload from a folder which supports hard-linking (which guest folders shared with host don't)
		vagrant ssh -c "cd \$(mktemp -d) && cp -r ${project_path}/* . && ${python_bin} setup.py sdist upload"
	fi
}

cd_root

# Precondition for running
running=0 && is_running "running"
[ ${running} -eq 1 ] || die "Vagrant guest must be running to push"

# Git tag must match version in snowplow_tracker/_version.py
version="" && error="" && get_version "version" "error"
[ "${error}" ] && die "Versions don't match: ${error}. Are you trying to publish an old version, or maybe on the wrong branch?"

upload_to_pypi
