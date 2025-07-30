#! /bin/bash

function echoErr { echo "E: $@" 1>&2; }
function echoAnn { echo "A: $@" 1>&2; }
function echoOut { echo "$@"; }

fbxoBase="${HOME}/foreignBxo"
bisosVenvName="py2-bisos-3"


function usage {
    echoOut "$0                    # fbxoBase=${HOME}/foreignBxo  -- bisosVenvName=py2-bisos-3"
    echoOut "$0 foreignBxoBaseDir  # bisosVenvName=py2-bisos-3"
    echoOut "$0 foreignBxoBaseDir  bisosVenvName"
}

function fbxoBaseSetup {
    #
    # Assumptions:
    #   1) initial bx-platformInfoManage.py base parameters has already been setup
    #   2) bx-bases has already been setup
    #   3) This script is being run by  --bisosUserName of bx-platformInfoManage.py
    #   4) uni sos.marme has already been installed in py2-bisos-3 and/or perhaps other venv
    #
    # Actions Taken:
    #   A) Above assumptions are verified
    #   B) ForeignBxo base is created based on $1
    #   C) If $2 is specified, that virtenv is used. Otherwise py2-bisos-3 is activated.
    #   D) System's bx-platformInfoManage.py are copied into the active virtenv
    #
    #

    if [ $# -gt 2 ] ; then
	echoErr "Usage: Bad Nu Of Args -- Expected less than 3 -- Got $#"
	usage
	exit 1
    fi


    if [ ! -z "$1" ] ; then
	fbxoBase="$1"
    fi

    if [ ! -z "$2" ] ; then
	bisosVenvName="$2"
    fi
    
    echoAnn  "Using fbxoBase=${fbxoBase} and  bisosVenvName=${bisosVenvName}"

    if [ ! -d "${fbxoBase}" ] ; then
	mkdir -p ${fbxoBase}
    fi

    if [ ! -d "${fbxoBase}" ] ; then    
	echoErr "Missing ${fbxoBase}"
	return 1
    fi
    
    local currentUser=$(id -un)
    local currentUserGroup=$(id -g -n ${currentUser})

    # in case functions are inherited -- as they are not, this is harmless
    if [ "$( type -t deactivate )" == "function" ] ; then
	deactivate
    fi

    #
    # System-wide bx-platformInfoManage.py is assumed to have been installed
    #
    #if ! which bx-platformInfoManage.py > /dev/null ; then

    local bx_platformInfoManage=$( which -a bx-platformInfoManage.py | grep -v venv | head -1 )

    if [ ! -f "${bx_platformInfoManage}" ] ; then 
	echoErr "Missing ${bx_platformInfoManage}"
	return 1
    fi
    
    local bisosUserName=$( ${bx_platformInfoManage} -i pkgInfoParsGet | grep bisosUserName | cut -d '=' -f 2 )
    local bisosGroupName=$( ${bx_platformInfoManage}  -i pkgInfoParsGet | grep bisosGroupName | cut -d '=' -f 2 )
    
    local rootDir_bisos=$( ${bx_platformInfoManage}  -i pkgInfoParsGet | grep rootDir_bisos | cut -d '=' -f 2 )
    local rootDir_bxo=$( ${bx_platformInfoManage}  -i pkgInfoParsGet | grep rootDir_bxo | cut -d '=' -f 2 )
    local rootDir_deRun=$( ${bx_platformInfoManage} -i pkgInfoParsGet | grep rootDir_deRun | cut -d '=' -f 2 )        

    if [ "${currentUser}" != "${bisosUserName}" ] ; then
	echoErr "currentUser=${currentUser} is not same as bisosUserName=${bisosUserName}"
	return 1
    fi

    local bisosVirtEnvBase="${rootDir_bisos}/venv/${bisosVenvName}"


    source ${bisosVirtEnvBase}/bin/activate

    pip -V

    #
    # We set the virtenv's params to be same as system's
    #
 
    sudo bx-platformInfoManage.py --bisosUserName="${bisosUserName}"  -i pkgInfoParsSet
    sudo bx-platformInfoManage.py --bisosGroupName="${bisosGroupName}"  -i pkgInfoParsSet     

    sudo bx-platformInfoManage.py --rootDir_bisos="${rootDir_bisos}"  -i pkgInfoParsSet
    sudo bx-platformInfoManage.py --rootDir_bxo="${rootDir_bxo}"  -i pkgInfoParsSet
    sudo bx-platformInfoManage.py --rootDir_deRun="${rootDir_deRun}"  -i pkgInfoParsSet    

    sudo bx-platformInfoManage.py --rootDir_foreignBxo="${fbxoBase}"  -i pkgInfoParsSet

    echo "========= bx-platformInfoManage.py -i pkgInfoParsGet ========="
    bx-platformInfoManage.py -i pkgInfoParsGet
}


fbxoBaseSetup $@

