# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: A =CmndSvc= for
#+end_org """

####+BEGIN: b:py3:cs:file/dblockControls :classification "cs-u"
""" #+begin_org
* [[elisp:(org-cycle)][| /Control Parameters Of This File/ |]] :: dblk ctrls classifications=cs-u
#+BEGIN_SRC emacs-lisp
(setq-local b:dblockControls t) ; (setq-local b:dblockControls nil)
(put 'b:dblockControls 'py3:cs:Classification "cs-u") ; one of cs-mu, cs-u, cs-lib, bpf-lib, pyLibPure
#+END_SRC
#+RESULTS:
: cs-u
#+end_org """
####+END:

####+BEGIN: b:prog:file/proclamations :outLevel 1
""" #+begin_org
* *[[elisp:(org-cycle)][| Proclamations |]]* :: Libre-Halaal Software --- Part Of BISOS ---  Poly-COMEEGA Format.
** This is Libre-Halaal Software. © Neda Communications, Inc. Subject to AGPL.
** It is part of BISOS (ByStar Internet Services OS)
** Best read and edited  with Blee in Poly-COMEEGA (Polymode Colaborative Org-Mode Enhance Emacs Generalized Authorship)
#+end_org """
####+END:

####+BEGIN: b:prog:file/particulars :authors ("./inserts/authors-mb.org")
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars |]]* :: Authors, version
** This File: /l/pip/sbom/py3/bisos/sbom/sbomSeed.py
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:py3:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['sbomSeed'], }
csInfo['version'] = '202502212104'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'sbomSeed-Panel.org'
csInfo['groupingType'] = 'IcmGroupingType-pkged'
csInfo['cmndParts'] = 'IcmCmndParts[common] IcmCmndParts[param]'
####+END:

""" #+begin_org
* [[elisp:(org-cycle)][| ~Description~ |]] :: [[file:/bisos/git/auth/bxRepos/blee-binders/bisos-core/COMEEGA/_nodeBase_/fullUsagePanel-en.org][BISOS COMEEGA Panel]]
Module description comes here.
** Relevant Panels:
** Status: In use with BISOS
** /[[elisp:(org-cycle)][| Planned Improvements |]]/ :
*** TODO complete fileName in particulars.
#+end_org """

####+BEGIN: b:prog:file/orgTopControls :outLevel 1
""" #+begin_org
* [[elisp:(org-cycle)][| Controls |]] :: [[elisp:(delete-other-windows)][(1)]] | [[elisp:(show-all)][Show-All]]  [[elisp:(org-shifttab)][Overview]]  [[elisp:(progn (org-shifttab) (org-content))][Content]] | [[file:Panel.org][Panel]] | [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] | [[elisp:(bx:org:run-me)][Run]] | [[elisp:(bx:org:run-me-eml)][RunEml]] | [[elisp:(progn (save-buffer) (kill-buffer))][S&Q]]  [[elisp:(save-buffer)][Save]]  [[elisp:(kill-buffer)][Quit]] [[elisp:(org-cycle)][| ]]
** /Version Control/ ::  [[elisp:(call-interactively (quote cvs-update))][cvs-update]]  [[elisp:(vc-update)][vc-update]] | [[elisp:(bx:org:agenda:this-file-otherWin)][Agenda-List]]  [[elisp:(bx:org:todo:this-file-otherWin)][ToDo-List]]

#+end_org """
####+END:

####+BEGIN: b:py3:file/workbench :outLevel 1
""" #+begin_org
* [[elisp:(org-cycle)][| Workbench |]] :: [[elisp:(python-check (format "/bisos/venv/py3/bisos3/bin/python -m pyclbr %s" (bx:buf-fname))))][pyclbr]] || [[elisp:(python-check (format "/bisos/venv/py3/bisos3/bin/python -m pydoc ./%s" (bx:buf-fname))))][pydoc]] || [[elisp:(python-check (format "/bisos/pipx/bin/pyflakes %s" (bx:buf-fname)))][pyflakes]] | [[elisp:(python-check (format "/bisos/pipx/bin/pychecker %s" (bx:buf-fname))))][pychecker (executes)]] | [[elisp:(python-check (format "/bisos/pipx/bin/pycodestyle %s" (bx:buf-fname))))][pycodestyle]] | [[elisp:(python-check (format "/bisos/pipx/bin/flake8 %s" (bx:buf-fname))))][flake8]] | [[elisp:(python-check (format "/bisos/pipx/bin/pylint %s" (bx:buf-fname))))][pylint]]  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

# ####+BEGIN: b:py3:cs:framework/imports :basedOn "classification"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] *Imports* =Based on Classification=cs-u=
#+end_org """
from bisos import b
from bisos.b import cs
from bisos.b import b_io
from bisos.common import csParam

import collections
# ####+END:

####+BEGIN: bx:cs:py3:section :title "Public Classes"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Public Classes*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:class/decl :className "AptPkg" :superClass "object" :comment "Abstraction of an Apt Package" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /AptPkg/  superClass=object =Abstraction of an Apt Package=  [[elisp:(org-cycle)][| ]]
#+end_org """
class AptPkg(object):
####+END:
    """
** Abstraction of
"""
    def __init__(
            self,
            name: str | None =None,
            func: typing.Callable | None =None,
            osVers: list[str] | None =None,
    ):
        self._aptPkgName = name
        self._aptPkgFunc = func
        self._osVers = osVers

    @property
    def name(self) -> str | None:
        return self._aptPkgName

    @name.setter
    def name(self, value: str | None,):
        self._aptPkgName = value

    @property
    def func(self) -> typing.Callable | None:
        return self._aptPkgFunc

    @func.setter
    def func(self, value: typing.Callable | None,):
        self._aptPkgFunc = value

    @property
    def osVers(self) -> list[str] | None:
        return self._osVers

    @osVers.setter
    def osVers(self, value: list[str] | None,):
        self._osVers = value

####+BEGIN: b:py3:class/decl :className "PipPkg" :superClass "object" :comment "Abstraction of a Pip Package" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /PipPkg/  superClass=object =Abstraction of a Pip Package=  [[elisp:(org-cycle)][| ]]
#+end_org """
class PipPkg(object):
####+END:
    """
** Abstraction of
"""
    def __init__(
            self,
            name: str | None =None,
            ver: str | None =None,
    ):
        self._pipPkgName = name
        self._ver = ver

    @property
    def name(self) -> str | None:
        return self._pipPkgName

    @name.setter
    def name(self, value: str | None,):
        self._pipPkgName = value

    @property
    def ver(self) -> str | None:
        return self._ver

    @ver.setter
    def ver(self, value: str | None,):
        self._ver = value


####+BEGIN: b:py3:class/decl :className "SbomSeedInfo" :superClass "object" :comment "Abstraction of a  Interface" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /SbomSeedInfo/  superClass=object =Abstraction of a  Interface=  [[elisp:(org-cycle)][| ]]
#+end_org """
class SbomSeedInfo(object):
####+END:
    """
** Abstraction of
"""
    _instance = None

    # Singleton using New
    def __new__(cls):
        if cls._instance is None:
            # print('Creating the object')
            cls._instance = super(SbomSeedInfo, cls).__new__(cls)
            # Put any initialization here.
        return cls._instance

    def __init__(
            self,
            aptPkgsList: list[AptPkg] | None =None,
            pipPkgsList: list[PipPkg] | None =None,
            pipxPkgsList: list[PipPkg] | None =None,
            examplesHook: typing.Callable | None =None,
    ):
        self._aptPkgsList = aptPkgsList
        self._pipPkgsList = pipPkgsList
        self._pipxPkgsList = pipPkgsList
        self._examplesHook = examplesHook

    @property
    def seedType(self) -> str | None:
        return self._seedType

    @seedType.setter
    def seedType(self, value: str | None,):
        self._seedType = value

    @property
    def aptPkgsList(self) -> list[AptPkg] | None:
        return self._aptPkgsList

    @aptPkgsList.setter
    def aptPkgsList(self, value: list[AptPkg] | None,):
        self._aptPkgsList = value

    @property
    def pipPkgsList(self) -> list[PipPkg] | None:
        return self._pipPkgsList

    @pipPkgsList.setter
    def pipPkgsList(self, value: list[PipPkg] | None,):
        self._pipPkgsList = value

    @property
    def pipxPkgsList(self) -> list[PipPkg] | None:
        return self._pipxPkgsList

    @pipxPkgsList.setter
    def pipxPkgsList(self, value: list[PipPkg] | None,):
        self._pipxPkgsList = value


    @property
    def examplesHook(self) -> typing.Callable | None:
        return self._examplesHook

    @examplesHook.setter
    def examplesHook(self, value: typing.Callable | None,):
        self._examplesHook = value

    def aptPkgsNames(self,) -> list[str]:
        result: list[str] = []
        if self.aptPkgsList is None:
            return result
        for eachPkg in self.aptPkgsList:
            if eachPkg.name is None:
                continue
            result.append(eachPkg.name)
        return result

    def namedAptPkg(self, name: str) -> AptPkg | None:
        result: AptPkg | None = None
        if self.aptPkgsList is None:
            print(f"EH_problem NOTYET -- self.aptPkgsList is None")
            return result
        for eachPkg in self.aptPkgsList:
            if eachPkg.name is None:
                continue
            elif eachPkg.name == name:
                result = eachPkg
            else:
                continue
        return result

    def pipPkgsNames(self,) -> list[str]:
        result: list[str] = []
        if self.pipPkgsList is None:
            return result
        for eachPkg in self.pipPkgsList:
            if eachPkg.name is None:
                continue
            result.append(eachPkg.name)
        return result

    def namedPipPkg(self, name: str) -> PipPkg | None:
        result: PipPkg | None = None
        if self.pipPkgsList is None:
            return result
        for eachPkg in self.pipPkgsList:
            if eachPkg.name is None:
                continue
            elif eachPkg.name == name:
                result = eachPkg
            else:
                continue
        return result

    def pipxPkgsNames(self,) -> list[str]:
        result: list[str] = []
        if self.pipxPkgsList is None:
            return result
        for eachPkg in self.pipxPkgsList:
            if eachPkg.name is None:
                continue
            result.append(eachPkg.name)
        return result

    def namedPipxPkg(self, name: str) -> PipPkg | None:
        result: PipPkg | None = None
        if self.pipxPkgsList is None:
            return result
        for eachPkg in self.pipxPkgsList:
            if eachPkg.name is None:
                continue
            elif eachPkg.name == name:
                result = eachPkg
            else:
                continue

        return result


sbomSeedInfo = SbomSeedInfo()

####+BEGIN: bx:cs:py3:section :title "Public Functions"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Public Functions*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:func/typing :funcName "aptPkg" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /aptPkg/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def aptPkg(
####+END:
        pkgName: str,
        func: typing.Callable | None = None,
        osVers: list[str] | None = None,
) -> AptPkg:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    pkg = AptPkg(name=pkgName, func=func, osVers=osVers)
    return pkg

####+BEGIN: b:py3:cs:func/typing :funcName "pipPkg" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /pipPkg/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def pipPkg(
####+END:
        pkgName: str,
        ver: str | None = None,
) -> PipPkg:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    pkg = PipPkg(name=pkgName, ver=ver)
    return pkg

####+BEGIN: b:py3:cs:func/typing :funcName "setup" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /setup/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def setup(
####+END:
        aptPkgsList: list[AptPkg] | None = None,
        pipPkgsList: list[PipPkg] | None = None,
        pipxPkgsList: list[PipPkg] | None = None,
        examplesHook: typing.Callable | None = None,
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """
    sbomSeedInfo.aptPkgsList  = aptPkgsList
    sbomSeedInfo.pipPkgsList  = pipPkgsList
    sbomSeedInfo.pipxPkgsList  = pipxPkgsList
    sbomSeedInfo.examplesHook  = examplesHook

    plant()


####+BEGIN: b:py3:cs:func/typing :funcName "plant" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /plant/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def plant(
####+END:
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

####+BEGINNOT: b:py3:cs:seed/withWhich :seedName "seedSbom.cs"
    """ #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  seed       [[elisp:(outline-show-subtree+toggle)][||]] <<seedSbom.cs>>   [[elisp:(org-cycle)][| ]]
#+end_org """
    # import __main__
    import shutil
    import os
    import sys

    seedName = 'seedSbom.cs'
    seedPath = shutil.which(seedName)
    if seedPath is None:
        print(f'sys.exit() --- which found nothing for {seedName} --- Aborting')
        sys.exit()

    __file__ = os.path.abspath(seedPath)
    # __name__ = '__main__'
    with open(__file__) as f:
        code = compile(f.read(), __file__, 'exec')
        exec(code, globals())

####+END:


####+BEGIN: b:py3:cs:func/typing :funcName "plantFile" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /plantFile/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def plantFile(
####+END:
) -> str:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

####+BEGIN: b:py3:cs:seed/withWhich :seedName "seedSbom.cs"
    """ #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  seed       [[elisp:(outline-show-subtree+toggle)][||]] <<seedSbom.cs>>   [[elisp:(org-cycle)][| ]]
#+end_org """
    import shutil
    import os
    import sys

    seedName = 'seedSbom.cs'
    seedPath = shutil.which(seedName)
    if seedPath is None:
        print(f'sys.exit() --- which found nothing for {seedName} --- Aborting')
        sys.exit()

    __file__ = os.path.abspath(seedPath)

    return __file__

####+END:


####+BEGIN: b:py3:cs:framework/endOfFile :basedOn "classification"
""" #+begin_org
* [[elisp:(org-cycle)][| *End-Of-Editable-Text* |]] :: emacs and org variables and control parameters
#+end_org """

#+STARTUP: showall

### local variables:
### no-byte-compile: t
### end:
####+END:
