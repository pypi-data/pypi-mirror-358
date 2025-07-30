#!/usr/bin/env python

""" #+begin_org
* Panel::  [[file:/bisos/panels/bisos-apps/NameOfThePanelComeHere/_nodeBase_/fullUsagePanel-en.org]]
* Overview and Relevant Pointers
#+end_org """

from bisos import b
# from bisos.b import cmndsSeed
from bisos.b import cs
from bisos.b import b_io

# import collections
import typing

from bisos.sbom import pkgsSeed
ap = pkgsSeed.aptPkg
pp = pkgsSeed.pipPkg

aptPkgsList = [
    ap("djbdns"),
    ap("facter"),
]

pipPkgsList = [
    pp("bisos.marmee"),
]

pipxPkgsList = [
    pp("bisos.marmee"),
]

pkgsSeed.setup(
    aptPkgsList=aptPkgsList,
    pipPkgsList=pipPkgsList,
    pipxPkgsList=pipxPkgsList,
)

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "cmndWithArgs" :extent "verify" :comment "stdin as input" :parsMand "" :parsOpt "" :argsMin 1 :argsMax 9999 :pyInv "methodInvokeArg"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<cmndWithArgs>>  *stdin as input*  =verify= argsMin=1 argsMax=9999 ro=cli pyInv=methodInvokeArg   [[elisp:(org-cycle)][| ]]
#+end_org """
class cmndWithArgs(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 9999,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             argsList: typing.Optional[list[str]]=None,  # CsArgs
             methodInvokeArg: typing.Any=None,   # pyInv Argument
    ) -> b.op.Outcome:
        """stdin as input"""
        failed = b_io.eh.badOutcome
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] This is an example of a CmndSvc with args  and/or stdin.

        #+end_org """)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  exmpl-seeded-cmnds.cs --par1Example="par1Mantory" --par2Example="par2Optional" -i parsArgsStdinCmndResult arg1 argTwo
#+end_src
#+RESULTS:
: cmndArgs= arg1  argTwo
: stdin instead of methodInvokeArg =
: cmndParams= par1Mantory par2Optional
: cmnd results come here
        #+end_org """)

        if self.justCaptureP(): return cmndOutcome


        action = self.cmndArgsGet("0", cmndArgsSpecDict, argsList)
        actionArgs = self.cmndArgsGet("1&9999", cmndArgsSpecDict, argsList)

        actionArgsStr = ""
        for each in actionArgs:
            actionArgsStr = actionArgsStr + " " + each

        actionAndArgs = f"""{action} {actionArgsStr}"""


        b.comment.orgMode(""" #+begin_org
*****  [[elisp:(org-cycle)][| *Note:* | ]] Next we take in stdin, when interactive.
After that, we print the results and then provide a result in =cmndOutcome=.
        #+end_org """)

        if not methodInvokeArg:
            methodInvokeArg = b_io.stdin.read()

        print(f"cmndArgs= {actionAndArgs}")
        print(f"stdin instead of methodInvokeArg = {methodInvokeArg}")

        return cmndOutcome.set(
            opError=b.op.OpError.Success,
            opResults="cmnd results come here",
        )

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self,):
        """  #+begin_org
*** [[elisp:(org-cycle)][| *cmndArgsSpec:* | ]] First arg defines rest
        #+end_org """

        cmndArgsSpecDict = cs.arg.CmndArgsSpecDict()
        cmndArgsSpecDict.argsDictAdd(
            argPosition="0",
            argName="action",
            argChoices=['echo', 'encrypt', 'ls', 'date'],
            argDescription="Action to be specified by rest"
        )
        cmndArgsSpecDict.argsDictAdd(
            argPosition="1&9999",
            argName="actionArgs",
            argChoices=[],
            argDescription="Rest of args for use by action"
        )

        return cmndArgsSpecDict

def examples_csu() -> None:
    """Common Usage Examples for this Command-Service Unit"""

    cmnd = cs.examples.cmndEnter

    cs.examples.menuChapter('*Cmnds, PyInv, With Params, Args, Stdin Producing Outcome*')

    csWrapper = "echo From Stdin HereComes Some ClearText | "
    cmndArgs = "echo some thing"

    cmnd('cmndWithArgs', args=cmndArgs, comment=" # Uses args")

    cs.examples.menuSection('*Stdin in addition to args or instead of args*')

    cmnd('cmndWithArgs', wrapper=csWrapper, args=cmndArgs, comment=" # Both stdin and args are used")



# cmndsSeed.register(
#     commonParamsFuncs=[commonParamsSpecify,],
#     examplesFuncsList=[examples_csu,],
# )

# cmndsSeed.plantWithWhich("seedCmnds.cs")
