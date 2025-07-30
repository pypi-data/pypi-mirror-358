# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: A =CS-Lib= for Managing MARMEE AAS (Abstracted Accessible Service) Control File Parameters
#+end_org """

####+BEGIN: b:py3:cs:file/dblockControls :classification "cs-u"
""" #+begin_org
* [[elisp:(org-cycle)][| /Control Parameters Of This File/ |]] :: dblk ctrls classifications=cs-u
#+BEGIN_SRC emacs-lisp
(setq-local b:dblockControls t) ; (setq-local b:dblockControls nil)
(put 'b:dblockControls 'py3:cs:Classification "cs-u") ; one of cs-mu, cs-u, cs-lib, b-lib, pyLibPure
#+END_SRC
#+RESULTS:
: cs-mu
#+end_org """
####+END:

####+BEGIN: b:prog:file/proclamations :outLevel 1
""" #+begin_org
* *[[elisp:(org-cycle)][| Proclamations |]]* :: Libre-Halaal Software --- Part Of Blee ---  Poly-COMEEGA Format.
** This is Libre-Halaal Software. © Libre-Halaal Foundation. Subject to AGPL.
** It is not part of Emacs. It is part of Blee.
** Best read and edited  with Poly-COMEEGA (Polymode Colaborative Org-Mode Enhance Emacs Generalized Authorship)
#+end_org """
####+END:

####+BEGIN: b:prog:file/particulars :authors ("./inserts/authors-mb.org")
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars |]]* :: Authors, version
** This File: NOTYET
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:python:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['ro'], }
csInfo['version'] = '202209130210'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'ro-Panel.org'
csInfo['groupingType'] = 'IcmGroupingType-pkged'
csInfo['cmndParts'] = 'IcmCmndParts[common] IcmCmndParts[param]'
####+END:

""" #+begin_org
* [[elisp:(org-cycle)][| ~Description~ |]] :: [[file:/bisos/git/auth/bxRepos/blee-binders/bisos-core/PyFwrk/bisos-pip/bisos.cs/_nodeBase_/fullUsagePanel-en.org][PyFwrk bisos.b.cs Panel For RO]] ||
Module description comes here.
** Relevant Panels:
** Status: In use with BISOS
** /[[elisp:(org-cycle)][| Planned Improvements |]]/ :
*** TODO complete fileName in particulars.
#+end_org """

####+BEGIN: b:prog:file/orgTopControls :outLevel 1
""" #+begin_org
* [[elisp:(org-cycle)][| Controls |]] :: [[elisp:(delete-other-windows)][(1)]] | [[elisp:(show-all)][Show-All]]  [[elisp:(org-shifttab)][Overview]]  [[elisp:(progn (org-shifttab) (org-content))][Content]] | [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] | [[elisp:(bx:org:run-me)][Run]] | [[elisp:(bx:org:run-me-eml)][RunEml]] | [[elisp:(progn (save-buffer) (kill-buffer))][S&Q]]  [[elisp:(save-buffer)][Save]]  [[elisp:(kill-buffer)][Quit]] [[elisp:(org-cycle)][| ]]
** /Version Control/ ::  [[elisp:(call-interactively (quote cvs-update))][cvs-update]]  [[elisp:(vc-update)][vc-update]] | [[elisp:(bx:org:agenda:this-file-otherWin)][Agenda-List]]  [[elisp:(bx:org:todo:this-file-otherWin)][ToDo-List]]
#+end_org """
####+END:

####+BEGIN: b:python:file/workbench :outLevel 1
""" #+begin_org
* [[elisp:(org-cycle)][| Workbench |]] :: [[elisp:(python-check (format "/bisos/venv/py3/bisos3/bin/python -m pyclbr %s" (bx:buf-fname))))][pyclbr]] || [[elisp:(python-check (format "/bisos/venv/py3/bisos3/bin/python -m pydoc ./%s" (bx:buf-fname))))][pydoc]] || [[elisp:(python-check (format "/bisos/pipx/bin/pyflakes %s" (bx:buf-fname)))][pyflakes]] | [[elisp:(python-check (format "/bisos/pipx/bin/pychecker %s" (bx:buf-fname))))][pychecker (executes)]] | [[elisp:(python-check (format "/bisos/pipx/bin/pycodestyle %s" (bx:buf-fname))))][pycodestyle]] | [[elisp:(python-check (format "/bisos/pipx/bin/flake8 %s" (bx:buf-fname))))][flake8]] | [[elisp:(python-check (format "/bisos/pipx/bin/pylint %s" (bx:buf-fname))))][pylint]]  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:orgItem/basic :type "=PyImports= " :title "*Py Library IMPORTS*" :comment "-- with classification based framework/imports"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  =PyImports=  [[elisp:(outline-show-subtree+toggle)][||]] *Py Library IMPORTS* -- with classification based framework/imports  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:framework/imports :basedOn "classification"
""" #+begin_org
** Imports Based On Classification=cs-u
#+end_org """
from bisos import b
from bisos.b import cs
from bisos.b import b_io

import collections
####+END:

from bisos.bpo import bpo
from bisos.bpo import bpoFpsCls

import pathlib
import os
import abc

####+BEGIN: bx:cs:py3:section :title "Service Specification"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Service Specification*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "CSU" :anchor ""  :extraInfo "Command Services Section"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _CSU_: |]]  Command Services Section  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: b:py3:cs:func/typing :funcName "examples_csu" :funcType "eType" :retType "" :deco "default" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-eType  [[elisp:(outline-show-subtree+toggle)][||]] /examples_csu/ deco=default  deco=default   [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def examples_csu(
####+END:
        bpoId: str,
        envRelPath: str,
        sectionTitle: typing.AnyStr = '',
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Examples of Service Access Instance Commands.
    #+end_org """

    def cpsInit(): return collections.OrderedDict()
    def menuItem(verbosity): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity=verbosity) # 'little' or 'none'

    cs.examples.menuChapter('Mail FileParams Access And Management --- Applicable To InMail and OutMail*')

    icmWrapper = ""
    cmndName = "marmeeAasMail_fps"
    cps = cpsInit() ; cps['bpoId'] = bpoId ; cps['envRelPath'] = envRelPath
    cmndArgs = "list" ;
    cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='none', icmWrapper=icmWrapper)

    icmWrapper = ""
    cmndName = "marmeeAasMail_fps"
    cps = cpsInit() ; cps['bpoId'] = bpoId ; cps['envRelPath'] = envRelPath
    cmndArgs = "menu" ;
    cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='none', icmWrapper=icmWrapper)

####+BEGIN: b:py3:cs:func/args :funcName "commonParamsSpecify" :comment "" :funcType "FmWrk" :retType "Void" :deco "" :argsList "csParams"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-A-FmWrk  [[elisp:(outline-show-subtree+toggle)][||]] /commonParamsSpecify/ deco=  [[elisp:(org-cycle)][| ]]  [[elisp:(org-cycle)][| ]]
#+end_org """
def commonParamsSpecify(
    csParams,
):
####+END:
    """
** Invoked class's static method.
    """

    csParams.parDictAdd(
        parName='aasMarmeeBase',
        parDescription="AAS Marmee Base",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        # parScope=icm.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--aasMarmeeBase',
    )

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "marmeeAasMail_fps" :comment "" :extent "verify" :parsMand "bpoId envRelPath" :argsMin 1 :argsMax 9999 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<marmeeAasMail_fps>>  =verify= parsMand=bpoId envRelPath argsMin=1 argsMax=9999 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class marmeeAasMail_fps(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'envRelPath', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 9999,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Mandatory Param
             envRelPath: typing.Optional[str]=None,  # Cs Mandatory Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        callParamsDict = {'bpoId': bpoId, 'envRelPath': envRelPath, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  A starting point command.
        #+end_org """)

        cmndArgsSpecDict = self.cmndArgsSpec()

        action = self.cmndArgsGet("0", cmndArgsSpecDict, argsList)
        actionArgs = self.cmndArgsGet("1&9999", cmndArgsSpecDict, argsList)

        #fpsBase = os.path.join(bpo.bpoBaseDir_obtain(bpoId), envRelPath)

        basedFps = b.pattern.sameInstance(AasMail_FPs, bpoId, envRelPath)

        fpsBase = basedFps.basePath_obtain()

        if action == "list":
            print(f"With fpBase={fpsBase} and cls={AasMail_FPs} name={basedFps.__class__.__name__}.")
            if b.fpCls.fpParamsReveal(cmndOutcome=cmndOutcome).cmnd(
                    rtInv=rtInv,
                    cmndOutcome=cmndOutcome,
                    fpBase=fpsBase,
                    cls=basedFps.__class__.__name__,
                    argsList=['getExamples'],
            ).isProblematic(): return(b_io.eh.badOutcome(cmndOutcome))

        elif action == "menu":
            print(f"With fpBase={fpsBase} and cls={AasMail_FPs} NOTYET.")
        else:
            print(f"bad input {action}")

        return(cmndOutcome)

####+BEGIN: b:py3:cs:method/args :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/ deco=default  deco=default   [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self, ):
####+END:
        """  #+begin_org
** [[elisp:(org-cycle)][| *cmndArgsSpec:* | ]]
        #+end_org """

        cmndArgsSpecDict = cs.arg.CmndArgsSpecDict()
        cmndArgsSpecDict.argsDictAdd(
            argPosition="0",
            argName="action",
            argChoices=['list', 'menu',],
            argDescription="Action to be specified by rest"
        )
        cmndArgsSpecDict.argsDictAdd(
            argPosition="1&9999",
            argName="actionArgs",
            argChoices=[],
            argDescription="Rest of args for use by action"
        )

        return cmndArgsSpecDict


####+BEGIN: b:py3:cs:cmnd/classHead :modPrefix "new" :cmndName "binsPreps" :comment "" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<binsPreps>>  =verify= ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class binsPreps(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
    ) -> b.op.Outcome:

        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
####+END:
        pkgsList = canon_pythonPkgsSpec()
        for pkgName in pkgsList:
            pkgVersion = pkgsList[pkgName]
            canon_pythonPkgInstall(pkgName, pkgVersion)

        pkgsList = canon_linuxPkgsSpec()
        for pkgName in pkgsList:
            pkgVersion = pkgsList[pkgName]
            canon_linuxPkgInstall(pkgName, pkgVersion)


        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=None,
        )

####+BEGIN: b:py3:cs:cmnd/classHead :modPrefix "new" :cmndName "binsPrepsCurInfo" :comment "" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<binsPrepsCurInfo>>  =verify= ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class binsPrepsCurInfo(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
    ) -> b.op.Outcome:

        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
####+END:
        #G = cs.globalContext.get()
        #g_runArgs = G.icmRunArgsGet()

        #
        # Python Packages
        #
        pkgsList = canon_pythonPkgsSpec()
        for pkgName in pkgsList:
            # Not all packages ahve __version__ so this is not reliable
            #exec("import {pyModule}".format(pyModule=each))
            #exec("print {pyModule}.__version__".format(pyModule=each))

            installedVer = pythonPkg_versionGet(pkgName)

            installedLoc = pythonPkg_locationGet(pkgName)

            b_io.ann.write(
                "Python:: pkgName={pkgName} -- expectedVer={expectedVer} -- installedVer={installedVer} -- installedLoc={installedLoc}"
                .format(pkgName=pkgName,
                        expectedVer=pkgsList[pkgName],
                        installedVer=installedVer,
                        installedLoc=installedLoc,
                ))

        #
        # Linux Packages
        #
        pkgsList = canon_linuxPkgsSpec()
        for pkgName in pkgsList:

            installedVer = linuxPkg_versionGet(pkgName)

            b_io.ann.write(
                "Linux::  pkgName={pkgName} -- expectedVer={expectedVer} -- installedVer={installedVer}"
                .format(pkgName=pkgName,
                        expectedVer=pkgsList[pkgName],
                        installedVer=installedVer,
                ))

        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=None,
        )


####+BEGIN: bx:cs:python:section :title "Supporting Classes And Functions"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Supporting Classes And Functions*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:
"""
*       /Empty/  [[elisp:(org-cycle)][| ]]
"""


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || IIF       ::  canon_linuxPkgInstall    [[elisp:(org-cycle)][| ]]
"""
def canon_linuxPkgInstall(
        pkgName,
        pkgVersion,
):
    """
** Install a given Linux pkg based on its canonical name and version.
"""
    distroName = platform.linux_distribution()[0]

    if  distroName == "Ubuntu":
        return linuxPkgInstall_aptGet(pkgName, pkgVersion)
    elif distroName == "Redhat":
        return linuxPkgInstall_yum(pkgName, pkgVersion)
    elif distroName == "CentOS Linux":
        return linuxPkgInstall_yum(pkgName, pkgVersion)
    else:
        b_io.eh.problem_info("Unsupported Distribution == {}".format(distroName))
        return

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || IIF       ::  linuxPkgInstall_ubuntu    [[elisp:(org-cycle)][| ]]
"""
def linuxPkgInstall_aptGet(
        pkgName,
        pkgVersion,
):
    """
** Install a given linux pkg with apt-get based on its canonical name and version.
"""
    installedVersion = linuxPkg_versionGet(pkgName)
    if pkgVersion:
        if installedVersion == pkgVersion:
            b_io.ann.write("Linux::  {pkgName} ver={ver} (as expected) is already installed -- skipped".format(
                pkgName=pkgName, ver=installedVersion))
            return
        else:
            outcome = icm.subProc_bash(
                """echo NOTYET pip install {pkgName}=={pkgVersion}"""
                .format(pkgName=pkgName, pkgVersion=pkgVersion)
            ).log()
            if outcome.isProblematic(): return b_io.eh.badOutcome(outcome)
            resultStr = outcome.stdout.strip()
            b_io.ann.write(resultStr)
            return

    installedVersion = linuxPkg_versionGet(pkgName)
    if installedVersion:
        b_io.ann.write("Linux::  {pkgName} ver={ver} (as any) is already installed -- skipped".format(
            pkgName=pkgName, ver=installedVersion))
        return
    else:
        outcome = icm.subProc_bash(
            """sudo apt-get install {pkgName}"""
            .format(pkgName=pkgName)
        ).log()
        if outcome.isProblematic(): return b_io.eh.badOutcome(outcome)
        resultStr = outcome.stdout.strip()
        b_io.ann.write(resultStr)
        return


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || IIF       ::  linuxPkgInstall_redhat    [[elisp:(org-cycle)][| ]]
"""
def linuxPkgInstall_yum(
        pkgName,
        pkgVersion,
):
    """
** Install a given linux pkg with yum based on its canonical name and version.
"""

    outcome = icm.subProc_bash(
        """sudo yum install {pkgName}"""
        .format(pkgName=pkgName)
    ).log()
    if outcome.isProblematic(): return b_io.eh.badOutcome(outcome)
    resultStr = outcome.stdout.strip()
    b_io.ann.write(resultStr)
    return


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || IIF       ::  linuxPkg_versionGet    [[elisp:(org-cycle)][| ]]
"""
def linuxPkg_versionGet(
        pkgName,
):
    """
** Return version as string if Python pkgName is installed
** Return None if Python pkgName is not installed
"""
    dpkgQueryOpts = """dpkg-query --show --showformat='${db:Status-Status}\n'"""
    outcome = icm.subProc_bash(
        """{dpkgQueryOpts} {pkgName}"""
        .format(dpkgQueryOpts=dpkgQueryOpts, pkgName=pkgName)
    ).log()
    if outcome.isProblematic():
        b_io.eh.badOutcome(outcome)
        return None

    resultStr = outcome.stdout.strip()
    if resultStr == "":
        return None

    dpkgQueryOpts = """dpkg-query --show --showformat='${Version}\n'"""
    outcome = icm.subProc_bash(
        """{dpkgQueryOpts} {pkgName}"""
        .format(dpkgQueryOpts=dpkgQueryOpts, pkgName=pkgName)
    ).log()
    if outcome.isProblematic():
        b_io.eh.badOutcome(outcome)
        return None

    resultStr = outcome.stdout.strip()
    if resultStr == "":
        return None
    else:
        return resultStr



"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || IIF       ::  canon_pythonPkgInstall    [[elisp:(org-cycle)][| ]]
"""
def canon_pythonPkgInstall(
        pkgName,
        pkgVersion,
):
    """
** Install a given Python pkg based on its canonical name and version.
"""
    return pythonPkg_install_pip(pkgName, pkgVersion)

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || IIF       ::  pythonPkg_install_ubuntu    [[elisp:(org-cycle)][| ]]
"""
def pythonPkg_install_pip(
        pkgName,
        pkgVersion,
):
    """
** Install a given Python pkg based on its canonical name and version.
If version is specified,  the package is installed or updated to that version.
If version is None,
    if package is already installed no action is taken
    if package is not installed, the latest is installed
"""
    installedVersion = pythonPkg_versionGet(pkgName)
    if pkgVersion:
        if installedVersion == pkgVersion:
            b_io.ann.write("Python:: {pkgName} ver={ver} (as expected) is already installed -- skipped".format(
                pkgName=pkgName, ver=installedVersion))
            return
        else:
            outcome = icm.subProc_bash(
                """echo pip install {pkgName}=={pkgVersion}"""
                .format(pkgName=pkgName, pkgVersion=pkgVersion)
            ).log()
            if outcome.isProblematic(): return b_io.eh.badOutcome(outcome)
            resultStr = outcome.stdout.strip()
            b_io.ann.write(resultStr)
            return

    installedVersion = pythonPkg_versionGet(pkgName)
    if installedVersion:
        b_io.ann.write("Python:: {pkgName} ver={ver} (as any) is already installed -- skipped".format(
            pkgName=pkgName, ver=installedVersion))
        return
    else:
        outcome = icm.subProc_bash(
            """echo pip install {pkgName}"""
            .format(pkgName=pkgName)
        ).log()
        if outcome.isProblematic(): return b_io.eh.badOutcome(outcome)
        resultStr = outcome.stdout.strip()
        b_io.ann.write(resultStr)
        return


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || IIF       ::  pythonPkg_versionGet    [[elisp:(org-cycle)][| ]]
"""
def pythonPkg_versionGet(
        pkgName,
):
    """
** Return version as string if Python pkgName is installed
** Return None if Python pkgName is not installed
"""
    outcome = icm.subProc_bash(
        """pip show {pkg} | egrep '^Version' | cut -d ':' -f 2"""
        .format(pkg=pkgName)
    ).log()
    if outcome.isProblematic():
        b_io.eh.badOutcome(outcome)
        return None

    resultStr = outcome.stdout.strip()
    if resultStr == "":
        return None
    else:
        return resultStr

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || IIF       ::  pythonPkg_locationGet    [[elisp:(org-cycle)][| ]]
"""
def pythonPkg_locationGet(
        pkgName,
):
    """
** Return location as string if Python pkgName is installed
** Return None if Python pkgName is not installed
"""
    outcome = icm.subProc_bash(
        """pip show {pkg} | egrep '^Location' | cut -d ':' -f 2"""
        .format(pkg=pkgName)
    ).log()
    if outcome.isProblematic():
        b_io.eh.badOutcome(outcome)
        return None

    resultStr = outcome.stdout.strip()
    if resultStr == "":
        return None
    else:
        return resultStr






####+BEGIN: b:py3:cs:framework/endOfFile :basedOn "classification"
""" #+begin_org
* *[[elisp:(org-cycle)][| ~End-Of-Editable-Text~ |]]* :: emacs and org variables and control parameters
#+end_org """

#+STARTUP: showall

### local variables:
### no-byte-compile: t
### end:
####+END:
