#!/bin/bash
#set -x

StandaloneIimBriefDescription="Qemu-KVM (libvirt -- virsh) ByStar (Bx) Bootstrap. With -i virtBuild a new Bx VM is created using retrived preseed.cfg"

ORIGIN="
* Revision And Libre-Halaal CopyLeft -- Part Of ByStar -- Best Used With Blee
"

####+BEGIN: bx:dblock:bash:top-of-file :vc "cvs" partof: "bystar" :copyleft "halaal+brief"
typeset RcsId="$Id: bxBootstrapGuest.sh,v 1.1 2018-01-09 05:31:54 lsipusr Exp $"
# *CopyLeft*
# Copyright (c) 2011 Neda Communications, Inc. -- http://www.neda.com
# See PLPC-120001 for restrictions.
# This is a Halaal Poly-Existential intended to remain perpetually Halaal.
####+END:

__author__="
* Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
"

_comment_="
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(delete-other-windows)][(1)]]  *Common iimStandaloneLib*
"

####+BEGIN: bx:dblock:global:file-insert :file "/libre/ByStar/InitialTemplates/software/bxDblock/bash/iimStandaloneLib.bash"
#
# /opt/public/osmt/bin/iimStandaloneLib.bash is common code
# which is included in the begining of iimStandalone modules.
# 

if [ -z "${BASH_VERSION}" ] ; then
    echo "UnSupported Bash"
    exit 1
fi

shopt -s expand_aliases
shopt -s extglob
#shopt

alias _CommentBegin_='cat << _CommentEnd_ > /dev/null'


_CommentBegin_
*  [[elisp:(org-cycle)][| ]]  iimLib        :: /[dblock]/ iimStandaloneLib.bash [[elisp:(org-cycle)][| ]]
_CommentEnd_

alias integer='typeset -i'
alias OrderedArray='typeset -a'
alias Array='typeset -a'
alias ListFuncs='typeset -F | sed -e s/"declare -f "//' 
alias TagVar='typeset -t'
alias TagVarList='typeset -t | sed -e s/"declare -t "// | cut -d= -f1'

alias TM_trace='tm_fileName=$FUNCNAME; tm_lineNo=$LINENO; tm_trace'
alias LOG_event='tm_fileName=$FUNCNAME; tm_lineNo=$LINENO; log_event'
alias LOG_message='tm_fileName=$FUNCNAME; tm_lineNo=$LINENO; log_event'
alias EH_oops='printf  >&2 "EH_,$FUNCNAME,$LINENO: OOPS"'
alias EH_problem='tm_fileName=$FUNCNAME; tm_lineNo=$LINENO; eh_problem'
alias EH_problemRet='tm_fileName=$FUNCNAME; tm_lineNo=$LINENO; eh_problem; return'
alias EH_fatal='tm_fileName=$FUNCNAME; tm_lineNo=$LINENO; eh_fatal'
alias EH_exit='tm_fileName=$FUNCNAME; tm_lineNo=$LINENO; eh_fatal'
alias EH_assert='opDoAssert eval '
alias opDoAssert='_opDoAssert "${G_myName}" "$FUNCNAME" $LINENO'
alias lpReturn='lpLastRetFuncIsValid=1; lpLastRetFunc=$FUNCNAME; return'
alias G_funcEntry='G_thisFunc=$FUNCNAME; G_thisFuncArgs=$@'
alias opDo='_opDo "${G_myName}" "$FUNCNAME" $LINENO "JUST_DO"'


function _opDoRunOnly {
  #
  # $1: mode
  # $2: msg
  # $3: failed msg
  # $4-: command

  if [[ "${1}X" == "JUST_DOX" ]] ; then
    shift; shift; shift;
    "$@" || err=$?
    return $err
  else
    typeset err=0
    typeset mode="${1}"
    typeset failedMsg="${3}"
    shift; shift; shift;
    "$@" || err=$?
    if [[ $err -ne 0 ]] ; then
      EH_problem "$failedMsg" "$err"
      if [[ "${mode}X" == "EXITX" ]] ; then
	exit $err
      fi
      return $err
    fi
  fi
}

function _opDoShowOnly {
  #
  # $1: mode
  # $2: msg
  # $3: failed msg
  # $4-: command
    if [[ "${BASH_VERSION}" != "" ]] ; then
	#echo -e ${2} 1>&2
	printf "%b \n" "${2}"
    else
	print -u2 "${2}"
    fi
}


function _opDoShowRun {
  #
  # $1: mode
  # $2: msg
  # $3: failed msg
  # $4-: command
  _opDoShowOnly "$@"
  _opDoRunOnly "$@"
}

function shift4ThenEcho {
    shift || exit
    shift || exit
    shift || exit
    shift || exit
    echo $*
}

function G_funcEntryShow {
    echo "${G_myName}:${G_thisFunc}:" 1>&2
}

function _opDoAfterPause {
    #shift
    #shift
    #shift
    #shift
    shift4ThenEcho "$@"
    _pauseForVerification ; if [[ ${skipIt} == "true" ]] ; then return; fi;
    _opDo "$@"
}

function _opDo {
    err=0
    typeset scriptName="$1"; shift || exit 
    typeset functionName="$1"; shift || exit
    typeset lineNumber="$1"; shift || exit
    typeset mode="$1"; shift || exit

    if [[ -z "${__opDo_prevScriptName}" ]] ; then
	export __opDo_prevScriptName=""
    fi
    if [[ -z "${__opDo_prevFunctionName}" ]] ; then
	export __opDo_prevFunctionName=""
    fi
    if [[ "${__opDo_prevScriptName}X" == "${scriptName}X" ]] ; then
	scriptName=""
    else
	__opDo_prevScriptName="${scriptName}"
	scriptName="${scriptName}::"
    fi
    if [[ "${__opDo_prevFunctionName}" == "${functionName}" ]] ; then
	functionName=""
    else
	__opDo_prevFunctionName="${functionName}"
    fi
    
    if [ -z "${G_recordMode}" ] ; then
	lineNumberTag="** [${lineNumber}]"
    else
	lineNumberTag="** [[file:${G_myFullName}::${lineNumber}][${lineNumber}]]"	
    fi

    if [ -z "${G_recordMode}" ] ; then
	scriptFuncName="* ${scriptName}${functionName}"	
    else
	scriptFuncName="* [[file:${G_myFullName}::function ${functionName}][${scriptName}${functionName}]]"		
    fi

    typeset msg
    typeset failedMsg
    dateTag=$( date +%Y%m%d%H%M%S%N )
    case "${G_verbose}" in
	"verbose")
	    if [ "${scriptName}" == "" ] ; then
		if [ "${functionName}" == "" ] ; then
		   msg="${lineNumberTag}: $@"
		else
		    #msg="* ${scriptName}${functionName} -- ${dateTag}\n${lineNumber}: $@"
		    msg="${scriptFuncName} -- ${dateTag}\n${lineNumberTag}: $@"
		fi 
	    else
		#msg="* ${scriptName}${functionName} -- ${dateTag}\n${lineNumber}: $@"
		msg="${scriptFuncName} -- ${dateTag}\n${lineNumberTag}: $@"		
	    fi
	    failedMsg="FAILED: ${scriptName}${functionName}${lineNumber}: $@ [ErrCode]="
	    ;;
	*)
	    msg="$@"
	    failedMsg="FAILED: $@ [ErrCode]="
	    ;;
    esac
    case "${G_runMode}" in
	"runOnly")
	    _opDoRunOnly "$mode" "$msg" "$failedMsg" "$@" || return $?
	    ;;
	"showOnly")
	    _opDoShowOnly "$mode" "$msg" "$failedMsg" "$@" || return
	    ;;
	"showRun")
	    _opDoShowRun "$mode" "$msg" "$failedMsg" "$@" || return
	    ;;
	"runSafe")
	    #runSafe = unprotected: showRun, protected: show
	    if [[ ${__opDo_withinCritical} -eq 0 ]] ; then
		_opDoShowRun "$mode" "$msg" "$failedMsg" "$@" || return
	    else
		_opDoShowOnly "$mode" "$msg" "$failedMsg" "$@" || return
	    fi
	    ;;
	"showCritical"|"showProtected")
	    #showCritical    = unprotected: run,     protected: show
	    if [[ ${__opDo_withinCritical} -eq 0 ]] ; then
		_opDoRunOnly "$mode" "$msg" "$failedMsg" "$@" || return
	    else
		_opDoShowOnly "$mode" "$msg" "$failedMsg" "$@" || return
	    fi
	    ;;
	"showRunCritical"|"showRunProtected")
	    #showRunCritical = unprotected: run,     protected: showRun 
	    if [[ ${__opDo_withinCritical} -eq 0 ]] ; then
		_opDoRunOnly "$mode" "$msg" "$failedMsg" "$@" || return
	    else
		_opDoShowRun "$mode" "$msg" "$failedMsg" "$@" || return
	    fi
	    ;;
    esac
    return $err
}

function _opDoAssert {
    typeset err=0
    typeset scriptName="$1"; shift || exit 
    typeset functionName="$1"; shift || exit
    typeset lineNumber="$1"; shift || exit
    scriptName="${scriptName}::"
    lineNumber="[${lineNumber}]"
    typeset failedMsg="ASSERTION FAILED: ${scriptName}${functionName}${lineNumber}: $@ [ErrCode]="
    "$@" || err=$?
    if [[ $err -ne 0 ]] ; then
	EH_problem "$failedMsg" "$err"
	exit $err
    fi
}


tm_trace() {
  # $1 = traceNu
  # $2 = traceString

  if [ ${traceLevel} ] ; then
    if test $1 -le ${traceLevel} ; then
      shift
      printf >&2 "TM_,${tm_fileName},${tm_setFile},${tm_lineNo}: $*\n"
    fi
  fi
}

log_event() {
  printf >&2 "LOG_,${tm_fileName},${tm_setFile},${tm_lineNo}: $*\n"
}

eh_problem() {
  printf >&2 "EH_,${G_myName},${tm_fileName},${tm_lineNo}: PROBLEM: $*\n"
}

eh_fatal() {
  printf >&2 "EH_,${tm_fileName},${tm_lineNo}: FATAL $*\n"
  exit 1
}

function vis_runFunc {
  #EH_assert [[ $# -gt 0 ]]
  typeset func=$1
  shift
  ${func} "$@"
}

function vis_reRunAsRoot {
    EH_assert [[ $# -gt 0 ]]

    globalReRunRetVal=0

    runId=$( id -u )
    if [ "${runId}" != "0" ] ; then
	#ANT_raw "Re Invokation as root:"
	#opDo sudo ${opBinBase}/${G_myName} -i runFunc $@
	#export G_runMode="runOnly"
	opDo sudo ${G_myFullName} ${G_commandOptions} -i runFunc $@
	globalReRunRetVal=$?
	#ANT_raw retVal=${globalReRunRetVal}
	lpReturn 0
    else
	lpReturn 127
    fi
}


FN_fileSymlinkUpdate() {
  # $1 is the source/origin  name (should exist)
  # $2 is the target name (gets created)

  if  test $# -ne 2 ; then
    EH_problem "$0 requires two args: Args=$*"
    return 1
  fi

  if test -a $1 ;   then  # Src file exists
    if test  -h $2 ;     then
      printf "$2 already a symlink, removing it\n"
      ls -l $2 1>&2
      /bin/rm $2
      printf "running: ln -s $1 $2 "
      ln -s $1 $2
    elif test -a $2 ; then
      # The target should not have existed before
      printf "$2 exists: skiping $0 of $1\n"
      ls -l $2 1>&2
    else
      ln -s $1 $2
      ls -l $2 1>&2
    fi
  else
    printf "No $1: skiping $0 of $1\n"
  fi
}

#alias continueAfterThis='echo "${G_myName}::$0:$LINENO"; _continueAfterThis; if [[ ${skipIt} == "true" ]] ; then return; fi;'
alias continueAfterThis='_continueAfterThis; if [[ ${skipIt} == "true" ]] ; then return; fi;'

function _continueAfterThis {
    #echo "About to: $*"
    if [ ${G_humanUser} != "TRUE" ] ; then
	return
    fi
    echo -n "Hit enter to continue, \"skip\" to skip or \"EXIT\" to exit: "
    skipIt=false
    while read line ; do
	if [[ "${line}_" == "SKIP_"  || "${line}_" == "skip_" ]] ; then
	echo "Skiped"
	    skipIt=true
	    break
	fi

	if [[ "${line}_" == "EXIT_"  || "${line}_" == "exit_" ]] ; then
	    exit
	fi

	if [[ "${line}_" == "_" ]] ; then
	    #echo "Continuing ...."
	    break
	fi

	echo "HA! ${line} -- Say Again"
	echo -n "Hit enter to continue, \"skip\" to skip or \"EXIT\" to exit: "
    done
}


_CommentBegin_
*  [[elisp:(org-cycle)][| ]]  iimLib        :: /[dblock]-End/ iimStandaloneLib.bash [[elisp:(org-cycle)][| ]]
_CommentEnd_


####+END:


_CommentBegin_
####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/libre/ByStar/InitialTemplates/software/plusOrg/dblock/inserts/topControls.org"
*      ================
*  /Controls/ ::  [[elisp:(org-cycle)][| ]]  [[elisp:(show-all)][Show-All]]  [[elisp:(org-shifttab)][Overview]]  [[elisp:(progn (org-shifttab) (org-content))][Content]] | [[file:Panel.org][Panel]] | [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] | [[elisp:(bx:org:run-me)][Run]] | [[elisp:(bx:org:run-me-eml)][RunEml]] | [[elisp:(delete-other-windows)][(1)]] | [[elisp:(progn (save-buffer) (kill-buffer))][S&Q]]  [[elisp:(save-buffer)][Save]]  [[elisp:(kill-buffer)][Quit]] [[elisp:(org-cycle)][| ]]
** /Version Control/ ::  [[elisp:(call-interactively (quote cvs-update))][cvs-update]]  [[elisp:(vc-update)][vc-update]] | [[elisp:(bx:org:agenda:this-file-otherWin)][Agenda-List]]  [[elisp:(bx:org:todo:this-file-otherWin)][ToDo-List]] 

####+END:
_CommentEnd_

_CommentBegin_
*      ================
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(delete-other-windows)][(1)]] CONTENTS-LIST ################
_CommentEnd_

function vis_moduleDescription {  cat  << _EOF_
*  [[elisp:(org-cycle)][| ]]  *[Description:]*
**  [[elisp:(org-cycle)][| ]]  Xrefs        :: *[Related/Xrefs:]*  <<Xref-Here->>  -- External Documents  [[elisp:(org-cycle)][| ]]
**  [[elisp:(org-cycle)][| ]]  Panel        :: [[file:/libre/ByStar/InitialTemplates/activeDocs/blee/syncUpdate/virBox/fullUsagePanel-en.org::Xref-][Panel Roadmap Documentation]] [[elisp:(org-cycle)][| ]]
_EOF_
}

function vis_moduleUsage {  cat  << _EOF_
*  [[elisp:(org-cycle)][| ]]  *[Usage:]*
   See -i examples for more details.
_EOF_
}

function vis_moduleStatus {  cat  << _EOF_
*  [[elisp:(org-cycle)][| ]]  *[Status:]*
** TODO [#B] [[elisp:(org-cycle)][| ]]  Next Steps    ::  Redirect stderr to be colored  [[elisp:(org-cycle)][| ]]
    http://serverfault.com/questions/59262/bash-print-stderr-in-red-color
   SCHEDULED: <2016-08-02 Tue>
** TODO [#B] [[elisp:(org-cycle)][| ]]  Next Steps    ::  We are ready to add virshInstall to virtBuild   [[elisp:(org-cycle)][| ]]
    SCHEDULED: <2016-07-31 Sun>
_EOF_
}

_CommentBegin_
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(delete-other-windows)][(1)]]  *Examples and IIFs*
_CommentEnd_


_CommentBegin_
*  [[elisp:(org-cycle)][| ]]  IIM Wide      :: G_postParamHook  [[elisp:(org-cycle)][| ]]
_CommentEnd_

function G_postParamHook {
    EH_assert [[ $# -eq 0 ]]
}


_CommentBegin_
*  [[elisp:(org-cycle)][| ]]  Examples      :: Examples  [[elisp:(org-cycle)][| ]]
_CommentEnd_


function vis_examples {
    typeset extraInfo="-h -v -n showRun -r basic"
    #typeset extraInfo=""
    typeset runInfo="-p ri=lsipusr:passive"

    typeset examplesInfo="${extraInfo} ${runInfo}"

    visLibExamplesOutput ${G_myName} 
  cat  << _EOF_
$( examplesSeperatorTopLabel "${G_myName}" )
$( examplesSeperatorChapter "Main IIFs" )
${G_myName} -i installBisos
${G_myName} ${extraInfo} -i installBisos
$( examplesSeperatorChapter "Virt-Install -- Create New VMs From Scratch" )
${G_myName} ${extraInfo} -i virtBuild next distro small ubuntu 1804 bx2
${G_myName} ${extraInfo} -i virtBuild next distro small ubuntu 1604 bx2
${G_myName} ${extraInfo} -i virtBuild next distro small debian 8 bx2
${G_myName} ${extraInfo} -i virtBuild next bxInstaller medium ubuntu 1804 bx2
${G_myName} ${extraInfo} -i virtBuild next bxInstaller medium ubuntu 1604 bx2
${G_myName} ${extraInfo} -i virtBuild next bxContainer medium ubuntu 1604 bx2  # NOTYET
${G_myName} ${extraInfo} -i virtBuild next bxInstaller large ubuntu 1804 bx2
${G_myName} ${extraInfo} -i virtBuild next bxInstaller large ubuntu 1604 bx2
${G_myName} ${extraInfo} -i virtBuild next bxContainer large ubuntu 1604 bx2   # NOTYET
$( examplesSeperatorChapter "Virt-Install -- Create New VMs From Scratch" )
${G_myName} ${extraInfo} -i vmDelete vmName
${G_myName} ${extraInfo} -i vmDelete ub1604preseed4
${G_myName} ${extraInfo} -i getNextNuForVmBuild ub-1604-bx2-distro-
${G_myName} ${extraInfo} -i getNextNuForVmBuild ub-1604-bx2-bxInstaller-
${G_myName} ${extraInfo} -i getCurNuForVmTemplate ub-1604-bx2-distro-
${G_myName} ${extraInfo} -i getCurNuForVmTemplate ub-1604-bx2-bxInstaller-
$( examplesSeperatorChapter "Virt-Install -- Create New VMs From Scratch" )
${G_myName} ${extraInfo} -i virtStartConnect ub-1604-bx2-bxInstaller-13
${G_myName} ${extraInfo} -i wgetPreseedFileWithName ubuntu 1604 preseed-bxInstaller.cfg
${G_myName} ${extraInfo} -i wgetPreseedFileWithName ubuntu 1604 preseed-distro.cfg
$( examplesSeperatorChapter "Virsh -- Installations and Verifications" )
${G_myName} ${extraInfo} -i distroAndOsInfoShow
${G_myName} ${extraInfo} -i virshInstallVerify
_EOF_
}

noArgsHook() {
  vis_examples
}

_CommentBegin_
*  [[elisp:(org-cycle)][| ]]  IIFs          :: installBisos  [[elisp:(org-cycle)][| ]]
_CommentEnd_


function vis_installBisos {
    EH_assert [[ $# -eq 0 ]]
    opDo echo "ZZ"
    opDo date
    opDo eval "echo mmm"
    opDo eval "echo jjj > /dev/null"    
    opDo ${G_myName} -v -n showRun -i wgetPreseedFileWithName 1 2 3
    vis_wgetPreseedFileWithName 5 6 7
    opDo iimBashStart.sh
    opDo bsrApache2Cap.sh -h -v -n showRun -p bystarUid=ea-59043 -p sr=so/sr/apache2/docBySource -i srA2VirDomStdout
    opDo vis_wgetPreseedFileWithName 8 8 8   
    lpReturn
    
    vis_virtBuild next bxInstaller small ubuntu 1604 bx2
}


_CommentBegin_
*  [[elisp:(org-cycle)][| ]]  Code          :: wgetPreseedWithName  [[elisp:(org-cycle)][| ]]
_CommentEnd_


function vis_wgetPreseedFileWithName {
    EH_assert [[ $# -eq 3 ]]
    typeset distroName=$1
    typeset distroGeneration=$2
    typeset preseedName=$3
    
    wget -O /tmp/${preseedName}  http://www.bysource.org/bx/all/${distroName}/${distroGeneration}/${preseedName}

    echo /tmp/${preseedName}
    
    lpReturn
}


_CommentBegin_
*  [[elisp:(org-cycle)][| ]]  Code          :: vmDelete <vmName>  [[elisp:(org-cycle)][| ]]
_CommentEnd_


function vis_vmDelete {
    EH_assert [[ $# -eq 1 ]]

    typeset vmName=$1

    typeset vmDefinedNames=$( virsh --connect qemu:///system list --all --name )

    if LIST_isIn ${vmName} "${vmDefinedNames}" ; then
	opDo virsh destroy ${vmName}
	opDo virsh undefine ${vmName}
    else
	EH_problem "${vmName} is not defined, undefine skipped"
    fi

    typeset vmDisksList=$( sudo ls  /var/lib/libvirt/images )

    if LIST_isIn ${vmName}.qcow2 "${vmDisksList}" ; then
	opDo sudo /bin/rm /var/lib/libvirt/images/${vmName}.qcow2
    else
	EH_problem "${vmName} image does not exist, deletion skipped"
    fi
    
    lpReturn
}


_CommentBegin_
*  [[elisp:(org-cycle)][| ]]  Code          :: getNextNuForVmBuild <vmNameTemplate>   [[elisp:(org-cycle)][| ]]
_CommentEnd_

function vis_getNextNuForVmBuild {
  EH_assert [[ $# -eq 1 ]]
  nameTemplate=${1}

  lastUsedNu=$( vis_getCurNuForVmTemplate ${nameTemplate} )

  if [ ${lastUsedNu} -eq "-1" ] ; then
      echo "0"
  else
      integer nextNu=$( expr ${lastUsedNu} + 1 )
      echo ${nextNu}
  fi
}


_CommentBegin_
*  [[elisp:(org-cycle)][| ]]  Code          :: getCurNuForVmTemplate <vmNameTemplate>   [[elisp:(org-cycle)][| ]]
_CommentEnd_

function vis_getCurNuForVmTemplate {
  EH_assert [[ $# -eq 1 ]]
  nameTemplate=${1}

  typeset vmDefinedNames=$( virsh --connect qemu:///system list --all --name |  grep ${nameTemplate} )  

  if [ -z "${vmDefinedNames}" ] ; then
      printf  "Missing Templates -- Assuming 0\n"  1>&2 
      echo "-1"
      return
  fi

  lastUsedNu=0
  for thisName in ${vmDefinedNames}; do
      thisUsedNu=${thisName#${nameTemplate}}
      if [ ${thisUsedNu} -ge ${lastUsedNu} ] ; then
	  lastUsedNu=${thisUsedNu}
      fi
  done
  echo ${lastUsedNu}
}


_CommentBegin_
*  [[elisp:(org-cycle)][| ]]  Code          :: virtBuild <vmName> <buildState> <vmProfile> <distroName> <distroGen> <bxGeneration>  [[elisp:(org-cycle)][| ]]
_CommentEnd_


function vis_virtBuild {
    #set -x
    G_funcEntry
    function describeF {  G_funcEntryShow; cat  << _EOF_
Add -p location={bx,std} After apt-mirror has been setup
_EOF_
    }
    EH_assert [[ $# -eq 6 ]]

    typeset vmName=$1
    typeset buildState=$2        
    typeset vmProfile=$3
    typeset distroName=$4
    typeset distroGeneration=$5       
    typeset bxGeneration=$6

    typeset nameTemplate="ub-1604-bx1-buildState-0"

    #
    # NOTYET, check for uid=0 -- Say that it should be
    # non-root and then su-ed -- Bacuse of connect to VM Desktop
    #
    if vis_reRunAsRoot ${G_thisFunc} $@ ; then lpReturn ${globalReRunRetVal}; fi;

    vmParamRam=512
    vmParamDisk=5
    vmParamCpus=1    

    function setVmProfileParams {
	EH_assert [[ $# -eq 1 ]]
	typeset vmProfile=$1

	if [ "${vmProfile}" == "minimal" ] ; then
	    vmParamRam=512
	    vmParamDisk=5
	    vmParamCpus=1    
	elif [ "${vmProfile}" == "small" ] ; then
	    vmParamRam=1024
	    vmParamDisk=8
	    vmParamCpus=1    
	elif [ "${vmProfile}" == "medium" ] ; then
	    vmParamRam=2049
	    vmParamDisk=20
	    vmParamCpus=2    
	elif [ "${vmProfile}" == "large" ] ; then
	    vmParamRam=4096
	    vmParamDisk=100
	    vmParamCpus=2    
	else
	    EH_problem "Unknown vmProfile=${vmProfile}"
	    return 101
	fi
    }

    setVmProfileParams ${vmProfile} 

    function getPreseedName {
	EH_assert [[ $# -eq 1 ]]
	typeset buildState=$1

	if [ "${buildState}" == "distro" ] ; then
	    echo "preseed-distro.cfg"
	    return
	elif [ "${buildState}" == "bxInstaller" ] ; then
	    echo "preseed-bxInstaller.cfg"
	    return
	elif [ "${buildState}" == "bxContainer" ] ; then
	    echo "preseed-bxContainer.cfg"
	    return
	else
	    EH_problem "Unknown buildState=${buildState}"
	    return 101
	fi
    }
    
    function prepPreseedCfg {
	EH_assert [[ $# -eq 2 ]]
	typeset preseedCfgInFile=$1
	typeset nextNu=$2	

	typeset preseedCfgOutFile=/tmp/preseed.cfg

	cat   ${preseedCfgInFile} | sed -e "s:unassigned-hostname:${bxGeneration}-${buildState}-${nextNu}:" \
					-e "s:unassigned-domain:${bxGeneration}.intra:" > ${preseedCfgOutFile}
	echo ${preseedCfgOutFile}
    }

    function ubuntuReleaseNumberToName {
	EH_assert [[ $# -eq 1 ]]
	typeset releaseNu=$1

	case "${releaseNu}" in
	    "1804")
		echo "bionic"
		;;
	    "1604")
		echo "xenial"
		;;
	    *)
		echo ""
		;;
	esac
	return
    }
    
    
    if [ "${distroName}" == "ubuntu" ] ; then
	local distroShortName="ub"
	local distroFullName="ubuntu"
	local ubuntuRleaseName=$( ubuntuReleaseNumberToName "${distroGeneration}" )
	if [ -z "${ubuntuRleaseName}" ] ; then
	    EH_problem "Unknown Ubuntu Release Name"
	    return 
	fi
	locationUrl="http://archive.ubuntu.com/ubuntu/dists/${ubuntuRleaseName}/main/installer-amd64"
	
    elif [ "${distroName}" == "debian" ] ; then
	distroShortName="deb"	
	distroFullName="debian"
	
	locationUrl="ftp://ftp.us.debian.org/debian/dists/stable/main/installer-amd64"
	preseedName=$( getPreseedName ${buildState} )
	if [ -z ${preseedName} ] ; then
	    EH_problem ""
	    return 101
	fi
	preseedFile="/opt/public/osmt/distBase/${distroFullName}/${distroGeneration}/debPkgs/${preseedName}"
	if [ ! -f "${preseedFile}" ] ; then
	    EH_problem "Missing ${preseedFile}"
	    return 101
	fi
	preseedCanonicalFile="/opt/public/osmt/distBase/${distroFullName}/${distroGeneration}/debPkgs/preseed.cfg"
	FN_fileSymlinkUpdate ${preseedFile} ${preseedCanonicalFile}
    else
	EH_problem "Unknown distroName=${dustroName}"
	lpReturn
    fi

    if [ "${vmName}" == "next" ] ; then
	nameTemplate="${distroShortName}-${distroGeneration}-${bxGeneration}-${buildState}-"
	nextNu=$( vis_getNextNuForVmBuild ${nameTemplate} )
	vmName=${nameTemplate}${nextNu}
    fi

    preseedName=$( getPreseedName ${buildState} )
    if [ -z ${preseedName} ] ; then
	EH_problem ""
	return 101
    fi
    preseedFile=$( vis_wgetPreseedFileWithName ${distroName} ${distroGeneration} ${preseedName} )
    #preseedFile="/opt/public/osmt/distBase/${distroFullName}/${distroGeneration}/debPkgs/${preseedName}"
    if [ ! -f "${preseedFile}" ] ; then
	EH_problem "Missing ${preseedFile}"
	return 101
    fi
    preseedCanonicalFile=$( prepPreseedCfg ${preseedFile} ${nextNu} )

    #debugOption="--debug "
    debugOption=" "    

    opDo  virt-install --connect=qemu:///system ${debugOption} \
         --location=${locationUrl}\
	 --initrd-inject=${preseedCanonicalFile} \
         --extra-args=\"auto\" \
         --name ${vmName} \
	 --ram=${vmParamRam} \
	 --vcpus=${vmParamCpus} \
         --disk=pool=default,size=${vmParamDisk},format=qcow2,bus=virtio


    # NOTYET: if original X User is root, this will fail
    #
    # Upon Completion, we want to do a full reboot/restart
    opDo vis_virtStartConnect ${vmName}
    
    lpReturn
}


_CommentBegin_
*  [[elisp:(org-cycle)][| ]]  Code          :: virtStartConnect <vmName>  [[elisp:(org-cycle)][| ]]
_CommentEnd_

function vis_virtStartConnect {
    G_funcEntry
    function describeF {  G_funcEntryShow; cat  << _EOF_
Add -p location={bx,std} After apt-mirror has been setup
_EOF_
    }
    EH_assert [[ $# -eq 1 ]]

    typeset vmName=$1

    opDo virsh --connect qemu:///system start ${vmName}
    
    opDo virt-viewer --connect qemu:///system ${vmName} &
    
    lpReturn
}



_CommentBegin_
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(delete-other-windows)][(1)]]  *Virsh Installations and Verifications*
_CommentEnd_


_CommentBegin_
*  [[elisp:(org-cycle)][| ]]  Code          :: vis_distroAndOsInfoShow  [[elisp:(org-cycle)][| ]]
_CommentEnd_

function vis_distroAndOsInfoShow {
    G_funcEntry
    function describeF {  G_funcEntryShow; cat  << _EOF_
_EOF_
    }
    EH_assert [[ $# -eq 0 ]]

    opDo cat /etc/lsb-release
    opDo cat /etc/os-release
    opDo cat /etc/issue
    opDo cat /proc/version

    opDo lsb_release -a
    opDo uname -a
}

_CommentBegin_
*  [[elisp:(org-cycle)][| ]]  Code          :: vis_virshInstallVerify  [[elisp:(org-cycle)][| ]]
_CommentEnd_

function vis_virshInstallVerify {
    G_funcEntry
    function describeF {  G_funcEntryShow; cat  << _EOF_
_EOF_
    }
    EH_assert [[ $# -eq 0 ]]

    typeset exitCode=0

    opDo which virsh virt-viewer jjZZ
    exitCode=$?

    echo "exitCode=${exitCode}"
    
    lpReturn ${exitCode}
}


_CommentBegin_
*  [[elisp:(org-cycle)][| ]]  Code          :: vis_virshInstall  [[elisp:(org-cycle)][| ]]
_CommentEnd_

function vis_virshInstall {
    G_funcEntry
    function describeF {  G_funcEntryShow; cat  << _EOF_
_EOF_
    }
    EH_assert [[ $# -eq 0 ]]
   
    typeset exitCode=0

    vis_virshVerify
    exitCode=$?

    if [[ ${exitCode} == 0 ]] ; then
	printf "Virsh has already been installed\n -- Installation Skipped.\n"
	lpReturn
    fi

    echo "NOTYET Fully Implemented"

    #opDo vis_distroAndOsVarsGet

    #vis_virshInstall_DEFAULT_DEFAULT
}


_CommentBegin_
*  [[elisp:(org-cycle)][| ]]  Code          :: vis_virshInstall_UBUNTU_1604  [[elisp:(org-cycle)][| ]]
_CommentEnd_


function vis_virshInstall_UBUNTU_1604 {
    G_funcEntry
    function describeF {  G_funcEntryShow; cat  << _EOF_
_EOF_
    }
    EH_assert [[ $# -eq 0 ]]
   
    typeset exitCode=0

    vis_virshVerify
    exitCode=$?

    if [[ ${exitCode} == 0 ]] ; then
	printf "Virsh has already been installed\n -- Installation Skipped.\n"
	lpReturn
    fi

    echo "NOTYET Fully Implemented"

    #opDo vis_distroAndOsVarsGet

    #vis_virshInstall_DEFAULT_DEFAULT
}


_CommentBegin_
*  [[elisp:(org-cycle)][| ]]  Code          :: vis_virshInstall_UBUNTU_1804  [[elisp:(org-cycle)][| ]]
_CommentEnd_


function vis_virshInstall_UBUNTU_1804 {
    G_funcEntry
    function describeF {  G_funcEntryShow; cat  << _EOF_
_EOF_
    }
    EH_assert [[ $# -eq 0 ]]
   
    typeset exitCode=0

    vis_virshVerify
    exitCode=$?

    if [[ ${exitCode} == 0 ]] ; then
	printf "Virsh has already been installed\n -- Installation Skipped.\n"
	lpReturn
    fi

    echo "NOTYET Fully Implemented"

    #opDo vis_distroAndOsVarsGet

    #vis_virshInstall_DEFAULT_DEFAULT
}



_CommentBegin_
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(delete-other-windows)][(1)]]  *Common iimStandaloneActions*
_CommentEnd_


####+BEGIN: bx:dblock:global:file-insert :file "/libre/ByStar/InitialTemplates/software/bxDblock/bash/iimStandaloneActions.bash"
#
# /opt/public/osmt/bin/iimStandaloneLib.bash is common code
# which is included at the end of iimStandalone modules.
# 


_CommentBegin_
*  [[elisp:(org-cycle)][| ]]  iimActions    :: /[dblock]/ iimStandaloneActions.bash [[elisp:(org-cycle)][| ]]
_CommentEnd_

function visLibExamplesOutput {
    # $1=callingsName
    cat  << _EOF_
$( examplesSeperatorChapter "COMMON SEEDED EXAMPLES" )
${1} -i examplesCommonSeeded
${1} -i visit
${1} -i describe
${1} -i examples
_EOF_
}

function vis_examplesCommonSeeded {
 cat  << _EOF_
$( examplesSeperatorChapter "COMMON EXAMPLES" )
${G_myName} -i showMe
${G_myName} -i seedHelp
${G_myName} -n showOnly -T 9 -i help
${G_myName} -i runFunc func args
${G_myName} -i visit
_EOF_
}


function examplesSeperatorTopLabel {
 cat  << _EOF_
###############################  $@  #################################
_EOF_
}


function examplesSeperatorChapter {
 cat  << _EOF_
#################  $@  #################
_EOF_
}


function examplesSeperatorSection {
 cat  << _EOF_
=================  $@  =================
_EOF_
}


function examplesSeperatorSubSection {
 cat  << _EOF_
-----------------  $@  -----------------
_EOF_
}

function vis_showMe {
 cat  << _EOF_
--- Program Parameters
RcsId=${RcsId}
G_argsOrig=${G_argsOrig}
G_progName=${G_progName}
G_myName=${G_myName}
G_myInvokedName=${G_myInvokedName}
G_myFullName=${G_myFullName}
G_runMode=${G_runMode}
G_verbose=${G_verbose}
G_checkMode=${G_checkMode}
G_forceMode=${G_forceMode}
--- OSMT Configurable Parameters
opShellVersion=${.sh.version}
opBase=${opBase}
--- User Parameters
opRunAcctName=${opRunAcctName}
_EOF_
# Also Trace Level
# NOTYET, Also show other relevant opBase and config parameters

  printf -- "--- OSMT INFO ---"
  # NOTYET, test that it exists, use the right variable
  cat /etc/osmtInfo
}

function vis_seedHelp {
 cat  << _EOF_

The following features are available to all scripts based on
seedActions.sh and seedSubjectActions.sh

Tracing:     -T <runLevelNumber>  -- Ex: ${G_myName} -T 9
Run Mode:    -n <runMode>         -- Ex: ${G_myName} -n runSafe
Record Mode: -r <recordMode>      -- Ex: ${G_myName} -r basic
Verbose:     -v                   -- Ex: ${G_myName} -v
Elaborate:   -e                   -- Ex: ${G_myName} -e elaborationTextIsIgnored
Force Mode:  -f                   -- Ex: ${G_myName} -f
Check Mode:  -c                   -- Ex: ${G_myName} -c fast

Tracing
=======
            DEFAULT: -T 0

            Trace Number Conventions:

	    0: No Tracing
	    1: Application Basic Info
	    2: Application General Info
	    3: Application Function Entry and Exit
    	    4: Application Debugging
	    5: Wrappers Library
	    6: Seed Script
	    7: Seed Supporting Libraries (eg, doLib.sh)
	    8: ocp_library
	    9: Quick Debug, usually temporary

Run Mode:
=========
           DEFAULT: runOnly

G_runMode=
   showOnly:           at opDo* just show the args always return 0
   runOnly:            at opDo* just execute
   showRun:            at opDo both runOnly and showOnly
   runSafe:            at opDo both show and run, but if protected
                       then just show
   showProtected:      Run everything and don't show except for
                       show only protected
   showRunProtected:   Run everything and don't show except for
                       run and show rotected

runSafe = unprotected: showRun, protected: show
showProtected = unprotected: run, protected: show
showRunProtected = unprotected: run, protected: showRun 

Verbose Mode:
=============

G_verbose=
   verbose        When Set, verbose format (eg, line nu, time tag, ...)
                  of Tracing and RunMode are selected.

Force Mode:
=============

G_forceMode=
   force          When Set, force/overwrite mode of operation
                  is selected.

Check Mode:
===========

G_checkMode={fast,strict,full}
   fast:          1) Skip asserting and consistency checks.
                  2) Do less than default, invoker will 
                     compensate
   strict:        Do asserts and consistency checks.
   full:          1) Do more than default

_EOF_
}




#opBasePathSet

#systemName=`uname -n`
#devlOsType=`uname -s`


###

#PATH=/usr/sbin:/usr/bin:/sbin

# Get options (defaults immediately below):

badUsage=
traceLevel=

Array paramInfo
loadFiles=""

#G_checkMode=""
#G_forceMode=""

G_argsOrig="$@"
#G_progName=`FN_nonDirsPart ${0}`
G_progName=$( basename ${0} )
G_myName=${G_progName}
G_myInvokedName=${0}

G_humanUser=FALSE

#TM_trace 9 ${G_argsOrig}

dotMeParamTmpFile=/tmp/${G_progName}.dotMe.$$

G_runMode="runOnly"
G_runModeCmndOption=" -n runOnly "

G_recordMode=""
G_recordModeCmndOption=""

G_paramCmndOption=""

while getopts e:T:c:i:p:l:u?n:r:vfh c
do
    case $c in
    T)
	case $OPTARG in
	*[!0-9]* )
	    echo "$0: -T requires a numeric option"
 	    badUsage=TRUE
	    ;;
        [0-9]* )
	    traceLevel=$OPTARG
	    ;;
	esac
	;;
    i)
        visibleFunction="${OPTARG}"   # rest of argv is passed to visibleFunction
	;;
    p)
       leftSide=`ATTR_leftSide "${OPTARG}"`
       rightSide=`ATTR_rightSide "${OPTARG}"`
  
       echo "${leftSide}"="${rightSide}" >> ${dotMeParamTmpFile}

       G_paramCmndOption=" -p ${OPTARG} ${G_paramCmndOption}"
       ;;
    l)
	loadFiles="${loadFiles} ${OPTARG}"
	G_myName=`FN_nonDirsPart ${OPTARG}`
        G_myInvokedName=${OPTARG}
	;;

    c)
	G_checkMode="${OPTARG}"
	G_checkCmndOption=" -c "
	;;

    e)
	# Elaboration Text SimplyIgnored
        elaborationTextSimplyIgnored="${OPTARG}"
	;;

    n)
	case ${OPTARG} in 
	    "runOnly")
		G_runMode="runOnly"
   	        G_runModeCmndOption=" -n runOnly "
		;;
	    "showOnly")
		G_runMode="showOnly"
   	        G_runModeCmndOption=" -n showOnly "
		;;
	    "showRun")
		G_runMode="showRun"
   	        G_runModeCmndOption=" -n showRun "
		;;
	    "runSafe")
		G_runMode="runSafe"
   	        G_runModeCmndOption=" -n runSafe "
		;;
	    "showProtected")
		G_runMode="showProtected"
   	        G_runModeCmndOption=" -n showProtected "
		;;
	    "showRunProtected")
		G_runMode="showRunProtected"
   	        G_runModeCmndOption=" -n showRunProtected "
		;;
	    *)
		badUsage=TRUE
		;;
	esac
	;;

    r)
	case ${OPTARG} in 
	    "basic")
		G_recordMode="basic"
   	        G_recordModeCmndOption=" -r basic "
		;;
	    *)
		badUsage=TRUE
		;;
	esac
	;;

    v)
	G_verbose="verbose"
        G_verboseCmndOption=" -v "
	;;

    f)
	G_forceMode="force"
	G_forceModeCmndOption=" -f "
	;;

    h)
	G_humanUser=TRUE
	G_humanCmndOption=" -h "
	;;

    u | \?)
	badUsage=TRUE
	;;
    esac
done

G_commandOptions="${G_checkCmndOption} ${G_runModeCmndOption} ${G_verboseCmndOption} ${G_humanCmndOption} ${G_forceModeCmndOption} ${G_paramCmndOption}"
#echo "G_commandOptions=${G_commandOptions}"

typeset myOptind=$OPTIND


function FN_absolutePathGet {
  # $1 = given file

  if  test  $# -ne 1 ; then
    return 1
  fi

  typeset givenFile=$1

  if [ "${givenFile}" == "" ] ; then
      return 1
  fi

  # Similar to expand-file-name in elisp
  # Convert filename NAME to absolute, and canonicalize it.
  # 

  givenFile=`eval /bin/echo "${givenFile}"`

  typeset absPath=`
  case $givenFile in
    */*) cd ${givenFile%/*} ;;
  esac
  pwd -P
`/${givenFile##*/} 

  echo ${absPath}
}


function opMyFullNameGet {
    #set -x
    typeset firstChar=${G_myInvokedName:0:1}

    if [ "${firstChar}" == "/" ] ; then 
	G_myFullName=${G_myInvokedName}
	G_myFullName=$( FN_absolutePathGet ${G_myFullName} )
	return 
    fi
    
    if [[ -f ${G_myInvokedName} ]] ; then
	G_myFullName=${PWD}/${G_myInvokedName}
    else
	G_myFullName=$( which ${G_myName} )
    fi

    G_myFullName=$( FN_absolutePathGet ${G_myFullName} )

    if [[ ! -f ${G_myFullName} ]] ; then
	echo "${G_myFullName} not found"
	return 1
    fi
}

opMyFullNameGet


if [[ "${G_forceMode}_" != "_" ]] ; then
    export G_forceMode="${G_forceMode}"
fi
if [[ "${G_checkMode}_" != "_" ]] ; then
    export G_checkMode="${G_checkMode}"
    #print -u2 G_checkMode="${G_checkMode}"
fi


G_preParamHookVal=`ListFuncs | egrep '^G_preParamHook$'`
if [ "${G_preParamHookVal}X" != "X" ] ;   then
  G_preParamHook 
fi

#
# EXECUTE PARAMETER ASSIGNMENTS
#


if [[ -f ${dotMeParamTmpFile} ]] ; then
  . ${dotMeParamTmpFile}
  rm ${dotMeParamTmpFile}
fi


G_postParamHookVal=`ListFuncs | egrep '^G_postParamHook$'`
if [ "${G_postParamHookVal}X" != "X" ] ;   then
  G_postParamHook 
fi


_CommentBegin_
**  [[elisp:(org-cycle)][| ]]  IimSeed      :: iimRecordBegin  [[elisp:(org-cycle)][| ]]
_CommentEnd_

function iimRecordBegin {
    typeset dateTag=$( date +%y%m%d%H%M%S%N )
    typeset userIdTag=$( id -u -n )

    typeset recordingBaseDir="/tmp"

    if [[ -d "/var/log/bisos/iim/bash" ]] ; then
	recordingBaseDir="/var/log/bisos/iim/bash"
    fi

    logFile=${recordingBaseDir}/${userIdTag}-${G_myName}-${dateTag}-log.org
    
    exec &> >(tee "${logFile}")
    printf "Started Logging To ${logFile}\n"
    cat  << _EOF_
${G_myName}  ${G_argsOrig} 
at ${G_myFullName} started at 
$( date ) by $( id -u -n) 
*  /Controls/ ::  [[elisp:(org-cycle)][| ]]  [[elisp:(show-all)][Show-All]]  [[elisp:(org-shifttab)][Overview]]  [[elisp:(progn (org-shifttab) (org-content))][Content]] | [[file:Panel.org][Panel]] | [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] | [[elisp:(bx:org:run-me)][Run]] | [[elisp:(bx:org:run-me-eml)][RunEml]] | [[elisp:(delete-other-windows)][(1)]] | [[elisp:(progn (save-buffer) (kill-buffer))][S&Q]]  [[elisp:(save-buffer)][Save]]  [[elisp:(kill-buffer)][Quit]] [[elisp:(org-cycle)][| ]]
** /Version Control/ ::  [[elisp:(call-interactively (quote cvs-update))][cvs-update]]  [[elisp:(vc-update)][vc-update]] | [[elisp:(bx:org:agenda:this-file-otherWin)][Agenda-List]]  [[elisp:(bx:org:todo:this-file-otherWin)][ToDo-List]] 
_EOF_
}


_CommentBegin_
**  [[elisp:(org-cycle)][| ]]  IimSeed      :: iimRecordEnd  [[elisp:(org-cycle)][| ]]
_CommentEnd_

function iimRecordEnd {
    printf "End Logging To ${logFile}\n"
    date
    cat  << _EOF_
* Parameters:
#+STARTUP: content
_EOF_
}



#
# VERIFY COMPLETENESS OF REQUIRED PARAMETERS
#
function opParamMandatoryVerify {

  #if [[ "${BASH_VERSION}_" != "_" ]] ; then
    # Because bash does not implement 
    # typeset -t, this feature is not
    # functional in bash
  #  return 0
  #fi

  typeset retVal=0
  typeset i=""

  paramsList=`TagVarList`
  
  for i in ${paramsList} ; do
    if  [ "${i}X" == "X" ] ; then continue; fi;
      echo "if [ \"\${$i}_\" == \"MANDATORY_\" ] || [ \"\${$i}_\" == \"mandatory_\" ] ; then echo \"$i must be specified\"; badUsage=TRUE; fi;" > ${dotMeParamTmpFile}

      #cat ${dotMeParamTmpFile}
      . ${dotMeParamTmpFile}
  done

  if [[ "${badUsage}" == "TRUE" ]] ; then
    exit 1
  fi

  FN_fileRmIfThere ${dotMeParamTmpFile}

  return ${retVal}
}

function dash_i_set {
    if [ "${dash_i}" = "" ] ; then
	dash_i="-i"
    elif [ "${dash_i}" = "nil" ] ; then
	dash_i=""
    else
	EH_problem "Oops"
	exit 1
    fi
}

function usage {

  # to get subject specific itemCmd_ lines

    printf >&2 "Usage: ${G_myName} [ -T traceLevel ] [ -u ] [ -p parameter=value ] [-i visibleFunction] \n"
    
    visFuncsList=`ListFuncs | egrep '^vis_'`
    printf >&2 "Usage: visibleFunction is one of: "
    for i in ${visFuncsList}
    do
      printf >&2 "${i##vis_} "
    done
    printf >&2 "\n"

}


#########  EXECUTION STARTS HERE ############

#G_validateOption ${action}  "${actionValidList}"

#G_validateRunOS "${runOSValidList}"


#
# REPORT USAGE PROBLEMS
#

if [ ${badUsage} ] ; then
    usage
    exit 1
fi

#shift `expr $OPTIND - 1`
shift `expr $myOptind - 1`

G_argv="$@"

#TM_trace 9 Args="$@"

#
# PERFORM REQUESTED TASKS
#


if [ "${visibleFunction}X" != "X" ]
then
    #echo "running ${visibleFunction}"
    if [ ! -z "${G_recordMode}" ] ; then
	iimRecordBegin
    fi
    
    vis_${visibleFunction} "$@"
    exitCode=$?

    if [ ! -z "${G_recordMode}" ] ; then	
	iimRecordEnd
    fi
    
    exit ${exitCode}
fi

function runNoArgsHook {
  noArgsHookVal=`ListFuncs | egrep '^noArgsHook$'`
  if [ "${noArgsHookVal}X" != "X" ] ;   then
    noArgsHook "$@"
  else
    echo "No action taken. Specify options."
    usage
  fi
  exit
}

if [ ! -z "${G_recordMode}" ] ; then
    iimRecordBegin
fi

runNoArgsHook "$@"
exitCode=$?

if [ ! -z "${G_recordMode}" ] ; then	
    iimRecordEnd
fi

exit ${exitCode}

_CommentBegin_
*  [[elisp:(org-cycle)][| ]]  iimActions    :: /[dblock]-End/ iimStandaloneActions.bash [[elisp:(org-cycle)][| ]]
_CommentEnd_

####+END:



_CommentBegin_
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(delete-other-windows)][(1)]]  *End Of Editable Text*
_CommentEnd_

####+BEGIN: bx:dblock:bash:end-of-file :type "basic"
_CommentBegin_
*  [[elisp:(org-cycle)][| ]]  Common        ::  /[dblock] -- End-Of-File Controls/ [[elisp:(org-cycle)][| ]]
_CommentEnd_
#+STARTUP: showall
#local variables:
#major-mode: sh-mode
#fill-column: 90
# end:
####+END:
