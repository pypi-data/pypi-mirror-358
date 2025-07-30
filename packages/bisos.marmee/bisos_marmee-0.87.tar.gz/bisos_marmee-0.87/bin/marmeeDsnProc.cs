#!/bin/env python
# -*- coding: utf-8 -*-

import sys
print("OBSOLETED -- To Be Revisited")
sys.exit()

""" #+begin_org
* ~[Summary]~ :: A =CmndSvc= for Process Incoming DSN (Delivery Status Notifications)
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
** This File: /bisos/git/bxRepos/bisos-pip/marmee/py3/bin/marmeeDsnProc.cs
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:py3:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['marmeeDsnProc'], }
csInfo['version'] = '202502124523'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'marmeeDsnProc-Panel.org'
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

####+BEGIN: b:py3:cs:framework/imports :basedOn "classification"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] *Imports* =Based on Classification=cs-u=
#+end_org """
from bisos import b
from bisos.b import cs
from bisos.b import b_io
from bisos.common import csParam

import collections
####+END:

import enum

import sys
import os

from bisos.currents import bxCurrentsConfig

# from uni sos.x822Msg import msgOut
#from bxMsg import msgIn
#from bxMsg import msgLib

# from bisos.marmee import marmeAcctsLib
# from bisos.marmee import marmeSendLib
# from bisos.marmee import marmeTrackingLib

import re

import email
import mailbox

import flufl.bounce

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase


""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] ~csuList emacs-list Specifications~  [[elisp:(blee:org:code-block/above-run)][ /Eval Below/ ]] [[elisp:(org-cycle)][| ]]
#+BEGIN_SRC emacs-lisp
(setq  b:py:cs:csuList
  (list
   "bisos.b.cs.ro"
   "bisos.csPlayer.bleep"
   "bisos.marmee.marmeeTrackingLib"
 ))
#+END_SRC
#+RESULTS:
| bisos.b.cs.ro | bisos.csPlayer.bleep | bisos.marmee.marmeeTrackingLib |
#+end_org """

####+BEGIN: b:py3:cs:framework/csuListProc :pyImports t :csuImports t :csuParams t
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] =Process CSU List= with /3/ in csuList pyImports=t csuImports=t csuParams=t
#+end_org """

from bisos.b.cs import ro
from bisos.csPlayer import bleep
from bisos.marmee import marmeeTrackingLib


csuList = [ 'bisos.b.cs.ro', 'bisos.csPlayer.bleep', 'bisos.marmee.marmeeTrackingLib', ]

g_importedCmndsModules = cs.csuList_importedModules(csuList)

def g_extraParams():
    csParams = cs.param.CmndParamDict()
    cs.csuList_commonParamsSpecify(csuList, csParams)
    cs.argsparseBasedOnCsParams(csParams)

####+END:


####+BEGIN: bx:cs:python:func :funcName "g_argsExtraSpecify" :comment "FrameWrk: ArgsSpec" :funcType "FrameWrk" :retType "Void" :deco "" :argsList "parser"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-FrameWrk [[elisp:(outline-show-subtree+toggle)][||]] /g_argsExtraSpecify/ =FrameWrk: ArgsSpec= retType=Void argsList=(parser)  [[elisp:(org-cycle)][| ]]
#+end_org """
def g_argsExtraSpecify(
    parser,
):
####+END:
    """Module Specific Command Line Parameters.
    g_argsExtraSpecify is passed to G_main and is executed before argsSetup (can not be decorated)
    """
    G = cs.globalContext.get()
    csParams = cs.CmndParamDict()

    csParams.parDictAdd(
        parName='moduleVersion',
        parDescription="Module Version",
        parDataType=None,
        parDefault=None,
        parChoices=list(),
        parScope=cs.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--version',
    )

    csParams.parDictAdd(
        parName='inFile',
        parDescription="Input File",
        parDataType=None,
        parDefault=None,
        parChoices=["someFile", "UserInput"],
        parScope=cs.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--inFile',
    )

    bleep.commonParamsSpecify(csParams)
    marmeAcctsLib.commonParamsSpecify(csParams)

    cs.argsparseBasedOnCsParams(parser, csParams)

    # So that it can be processed later as well.
    G.icmParamDictSet(csParams)

    return


####+BEGIN: b:py3:cs:main/exposedSymbols :classes ()
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] ~CS Controls and Exposed Symbols List Specification~ with /0/ in Classes List
#+end_org """
####+END:

####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "CmndSvcs" :anchor ""  :extraInfo "Command Services Section"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _CmndSvcs_: |]]  Command Services Section  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "examplesOther" :extent "verify" :ro "noCli" :comment "FrameWrk: CS-Main-Examples" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<examplesOther>>  *FrameWrk: CS-Main-Examples*  =verify= ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class examplesOther(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}
    rtInvConstraints = cs.rtInvoker.RtInvoker.new_noRo() # NO RO From CLI

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
    ) -> b.op.Outcome:
        """FrameWrk: CS-Main-Examples"""
        failed = b_io.eh.badOutcome
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
####+END:
        self.cmndDocStr(f""" #+begin_org ***** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Conventional top level example.
        #+end_org """)

        def cpsInit(): return collections.OrderedDict()
        def menuItem(verbosity): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity=verbosity) # 'little' or 'none'
        def execLineEx(cmndStr): cs.examples.execInsert(execLine=cmndStr)

        #logControler = b_io.log.Control()
        #logControler.loggerSetLevel(20)

        cs.examples.myName(cs.G.icmMyName(), cs.G.icmMyFullName())

        cs.examples.commonBrief()

        bleep.examples_csBasic()

        marmeeTrackingLib.examples_deliveryTrackings()

        b.ignore(ro.__doc__,)  # We are not using these modules, but they are auto imported.

        return(cmndOutcome)



####+BEGIN: b:py3:cs:cmnd/classHead :modPrefix "new" :cmndName "examples" :cmndType "ICM-Cmnd-FWrk"  :comment "FrameWrk: ICM Examples" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-ICM-Cmnd-FWrk [[elisp:(outline-show-subtree+toggle)][||]] <<examples>>  *FrameWrk: ICM Examples*  =verify= ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class examples(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
    ) -> b.op.Outcome:
        """FrameWrk: ICM Examples"""
        failed = b_io.eh.badOutcome
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
####+END:
        def cpsInit(): return collections.OrderedDict()
        def menuItem(verbosity): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity=verbosity) # 'little' or 'none'
        def execLineEx(cmndStr): cs.examples.execInsert(execLine=cmndStr)

        logControler = b_io.log.Control()
        logControler.loggerSetLevel(20)

        cs.examples.myName(cs.G.icmMyName(), cs.G.icmMyFullName())

        cs.examples.commonBrief()

        bleep.examples_csBasic()

####+BEGIN: bx:cs:python:cmnd:subSection :title "Real Invokations"

####+END:

        cs.examples.menuChapter('*Real Invokations*')

        cmndName = "maildirApplyToMsg"
        cmndArgs = "dsnProcessAndRefile"
        cps = collections.OrderedDict(); cmndParsCurBxoSr(cps) # ; cps['runMode'] = 'dryRun' COMMENTED-OUT
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, icmWrapper=None, verbosity='little')

        cs.examples.cmndInsert(cmndName, cps, cmndArgs, icmWrapper="echo", verbosity='full')

####+BEGIN: bx:cs:python:cmnd:subSection :title "Examples   ::  Testing -- /DryRun/ -- devTest -- Maildir Apply To Message Processor"

####+END:

        cs.examples.menuChapter('*Testing -- /DryRun/ -- devTest -- Maildir Apply To Message Processor*')

        # menuLine = """--runMode dryRun --inMailAcct={inMailAcct} --inMbox={inMbox} {cmndAction} {cmndArgs}""".format(
        #    inMailAcct=inMailAcct, inMbox=inMbox, cmndAction=cmndAction, cmndArgs=cmndArgs)

        cmndName = "maildirApplyToMsg"
        cmndArgs = "msgDisect"
        cps = collections.OrderedDict(); cmndParsCurBxoSr(cps) ; #cps['controlProfile'] = enabledControlProfile ; cps['inMailAcct'] = enabledMailAcct
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, icmWrapper=None, verbosity='little')

        cmndName = "maildirApplyToMsg"
        cmndArgs = "dsnReportLong"
        cps = collections.OrderedDict(); cmndParsCurBxoSr(cps) ; #cps['controlProfile'] = enabledControlProfile ; cps['inMailAcct'] = enabledMailAcct
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, icmWrapper=None, verbosity='little')

        cmndName = "maildirApplyToMsg"
        cmndArgs = "dsnProcessAndRefile"
        cps = collections.OrderedDict(); cmndParsCurBxoSr(cps) ; cps['runMode'] = 'dryRun'
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, icmWrapper=None, verbosity='little')

        cmndName = "maildirApplyToMsg"
        cmndArgs = "dsnTestSendToCoRecipients"
        cps = collections.OrderedDict(); cmndParsCurBxoSr(cps) ; cps['runMode'] = 'dryRun'
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, icmWrapper=None, verbosity='little')

        cmndName = "maildirApplyToMsg"
        cmndArgs = "dsnTestSendToCoRecipients"
        cps = collections.OrderedDict(); cmndParsCurBxoSr(cps) ; cps['runMode'] = 'runDebug'
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, icmWrapper=None, verbosity='little')

        cmndName = "maildirApplyToMsg"
        cmndArgs = "dsnTestSendToCoRecipients"
        cps = collections.OrderedDict(); cmndParsCurBxoSr(cps) ; cps['runMode'] = 'fullRun'
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, icmWrapper=None, verbosity='little')

####+BEGIN: bx:cs:python:cmnd:subSection :title "From  marmeAcctsLib.py"

####+END:

        marmeAcctsLib.examples_controlProfileManage()

        #marmeAcctsLib.examples_marmeAcctsLibControls()

        marmeAcctsLib.examples_select_mailBox()

        marmeAcctsLib.examples_inMailAcctAccessPars()

        marmeAcctsLib.examples_outMailAcctAccessPars()



    
####+BEGIN: bx:cs:py3:section :title "CS-Commands"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *CS-Commands*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "someCmnd" :comment "" :extent "verify" :ro "cli" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<someCmnd>>  =verify= ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class someCmnd(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  A starting point command.
        #+end_org """)

        if b.subProc.WOpW(invedBy=self, log=1).bash(
                f"""echo hello World""",
        ).isProblematic():  return(b_io.eh.badOutcome(cmndOutcome))

        return(cmndOutcome)


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "maildirApplyToMsg" :comment "" :parsMand "" :parsOpt "bxoId sr controlProfile inMailAcct inMbox" :argsMin 1 :argsMax 1000 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<maildirApplyToMsg>>  =verify= parsOpt=bxoId sr controlProfile inMailAcct inMbox argsMin=1 argsMax=1000 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class maildirApplyToMsg(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'bxoId', 'sr', 'controlProfile', 'inMailAcct', 'inMbox', ]
    cmndArgsLen = {'Min': 1, 'Max': 1000,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bxoId: typing.Optional[str]=None,  # Cs Optional Param
             sr: typing.Optional[str]=None,  # Cs Optional Param
             controlProfile: typing.Optional[str]=None,  # Cs Optional Param
             inMailAcct: typing.Optional[str]=None,  # Cs Optional Param
             inMbox: typing.Optional[str]=None,  # Cs Optional Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'bxoId': bxoId, 'sr': sr, 'controlProfile': controlProfile, 'inMailAcct': inMailAcct, 'inMbox': inMbox, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        bxoId = csParam.mappedValue('bxoId', bxoId)
        sr = csParam.mappedValue('sr', sr)
        controlProfile = csParam.mappedValue('controlProfile', controlProfile)
        inMailAcct = csParam.mappedValue('inMailAcct', inMailAcct)
        inMbox = csParam.mappedValue('inMbox', inMbox)
####+END:
        #cmndArgsSpec = {0: ['msgDisect', 'coRecepientNdr']}

        cmndArgs = self.cmndArgsGet("0&-1", cmndArgsSpecDict, argsList)

        inMailDir = marmeAcctsLib.getPathForAcctMbox(
            controlProfile,
            inMailAcct,
            inMbox,
            bxoId=bxoId,
            sr=sr,
        )

        b_io.tm.here(inMailDir)

        mbox = mailbox.Maildir(
            inMailDir,
            factory=None,  # important!! default does not work
        )

        for msgProc in cmndArgs:

            #b_io.ann.here("thisArg={thisArg}".format(thisArg=msgProc))

            #for msg in mbox:
            for key in mbox.keys():
                try:
                    msg = mbox[key]
                except email.errors.MessageParseError:
                    b_io.eh.problem_info(msg)
                    continue                # The message is malformed. Just leave it.

                try:
                    eval(msgProc + '(bxoId, sr, inMailDir, mbox, key, msg)')
                except Exception as e:
                    b_io.eh.critical_exception(e)
                    b_io.eh.problem_info("Invalid Action: {msgProc}"
                                        .format(msgProc=msgProc))
                    raise   # NOTYET, in production, the raise should be commented out

        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=None,
        )

####+BEGIN: b:py3:cs:method/args :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self, ):
####+END:
        """
***** Cmnd Args Specification
"""
        cmndArgsSpecDict = cs.CmndArgsSpecDict()
        cmndArgsSpecDict.argsDictAdd(
            argPosition="0&-1",
            argName="cmndArgs",
            argDefault=None,
            argChoices=['msgDisect', 'coRecepientNdr'],
            argDescription="Rest of args for use by action"
        )

        return cmndArgsSpecDict

def msgDisect(
    bxoId,
    sr,
    maildir,
    mbox,
    key,
    inMsg,
):
    """ """
    for part in inMsg.walk():
        print(part.get_content_type())

    return


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Msg-Apply    ::  dsnReportLong    [[elisp:(org-cycle)][| ]]
"""
def dsnReportLong(
    bxoId,
    sr,
    maildir,
    mbox,
    key,
    inMsg,
):
    """ """
    tempFailedRecipients, permFailedRecipients = flufl.bounce.all_failures(inMsg)

    failedMsg = fromNonDeliveryReportGetFailedMsg(
        inMsg,
        tempFailedRecipients,
        permFailedRecipients,
    )

    coRecipients = fromFailedMsgGetCoRecipients(
        failedMsg,
        tempFailedRecipients,
        permFailedRecipients,
    )

    dsnType = msgDsnTypeDetect(
        inMsg,
        failedMsg,
        tempFailedRecipients,
        permFailedRecipients,
        coRecipients,
    )

    dsnTypeReports(inMsg, dsnType, "long")


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Msg-Apply    ::  dsnTestSendToCoRecipients    [[elisp:(org-cycle)][| ]]
"""
def dsnTestSendToCoRecipients(
        bxoId,
        sr,
        maildir,
        mbox,
        key,
        inMsg,
):
    """
** inMsg is analyzed to see if it contains a bounce. based on that it is catgorized as one of the following:
"""
    dsnProcessAndRefileWithGivenActions(
        bxoId,
        sr,
        maildir,
        mbox,
        key,
        inMsg,
        action_deliveryReport=None,
        action_receiptNotification=None,
        action_ndrNoCoRecipients=None,
        action_ndrWithCoRecipients=msgSend_test_permanentNdrToCoRecipients,
        action_tmpNonDeliveryReport=None,
        action_notADsn=None,
    )



"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Msg-Apply    ::  dsnProcessAndRefile    [[elisp:(org-cycle)][| ]]
"""
def dsnProcessAndRefile(
    bxoId,
    sr,
    maildir,
    mbox,
    key,
    inMsg,
):
    """
** inMsg is analyzed to see if it contains a bounce. based on that it is catgorized as one of the following:
"""
    dsnProcessAndRefileWithGivenActions(
        bxoId,
        sr,
        maildir,
        mbox,
        key,
        inMsg,
        action_deliveryReport=None,
        action_receiptNotification=None,
        action_ndrNoCoRecipients=None,
        action_ndrWithCoRecipients=msgSend_test_permanentNdrToCoRecipients,
        action_tmpNonDeliveryReport=None,
        action_notADsn=None,
    )

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func         ::  dsnProcessAndRefileWithGivenActions    [[elisp:(org-cycle)][| ]]
"""
def dsnProcessAndRefileWithGivenActions(
        bxoId,
        sr,
        maildir,
        mbox,
        key,
        inMsg,
        action_deliveryReport=None,
        action_receiptNotification=None,
        action_ndrNoCoRecipients=None,
        action_ndrWithCoRecipients=None,
        action_tmpNonDeliveryReport=None,
        action_notADsn=None,
):
    """
** inMsg is analyzed to see if it contains a bounce. based on that it is catgorized as one of the following:
*** envNotADsn: If it is not a Delivery Status Notification (DSN) it is filed
*** envTmpNdr:  A temporary Non-Delivery Report (NDR)
*** envNdrNoCoRecip:  A permanent Non-Delivery Report without any co-recipients
*** envNdrWithCoRecipNotified: A permanent NDR with co-recipients that were notified
*** envNdrWithCoRecip: A permanent NDR with co-recipients that were not notified
*** envDr:  A Delivery Report
*** envRn: A Recipt Notification
"""
    G = cs.globalContext.get()
    runMode = G.icmRunArgsGet().runMode

    tempFailedRecipients, permFailedRecipients = flufl.bounce.all_failures(inMsg)

    failedMsg = fromNonDeliveryReportGetFailedMsg(
        inMsg,
        tempFailedRecipients,
        permFailedRecipients,
    )

    coRecipients = fromFailedMsgGetCoRecipients(
        failedMsg,
        tempFailedRecipients,
        permFailedRecipients,
    )

    dsnType = msgDsnTypeDetect(
        inMsg,
        failedMsg,
        tempFailedRecipients,
        permFailedRecipients,
        coRecipients,
    )

    dsnTypeReports(inMsg, dsnType, "short")


    if dsnType == DsnType.deliveryReport:
        if action_deliveryReport:
            action_deliveryReport(
                inMsg,
                failedMsg,
                tempFailedRecipients,
                permFailedRecipients,
                coRecipients,
                dsnType,
            )

    elif dsnType == DsnType.receiptNotification:
        if action_receiptNotification:
            action_receiptNotification(
                inMsg,
                failedMsg,
                tempFailedRecipients,
                permFailedRecipients,
                coRecipients,
                dsnType,
            )

    elif dsnType == DsnType.ndrNoCoRecipients:
        if runMode == 'dryRun':
            pass
        elif runMode == 'runDebug':
            pass
        elif  runMode == 'fullRun':
            if action_ndrNoCoRecipients:
                action_ndrNoCoRecipients(
                    bxoId,
                    sr,
                    inMsg,
                    failedMsg,
                    tempFailedRecipients,
                    permFailedRecipients,
                    coRecipients,
                    dsnType,
                )

            msgMoveToFolder("envNdrNoCoRecip", maildir, mbox, key, inMsg,)
            marmeTrackingLib.deliveryEvent_permNdr(
                bxoId,
                sr,
                inMsg,
            )
        else:
            b_io.eh.critical_oops()


    elif dsnType == DsnType.ndrWithCoRecipients:
        if runMode == 'dryRun':
            pass
        elif runMode == 'runDebug':
            if action_ndrWithCoRecipients:
                action_ndrWithCoRecipients(
                    bxoId,
                    sr,
                    inMsg,
                    failedMsg,
                    tempFailedRecipients,
                    permFailedRecipients,
                    coRecipients,
                    dsnType,
                )
        elif  runMode == 'fullRun':
            if action_ndrWithCoRecipients:
                action_ndrWithCoRecipients(
                    bxoId,
                    sr,
                    inMsg,
                    failedMsg,
                    tempFailedRecipients,
                    permFailedRecipients,
                    coRecipients,
                    dsnType,
                )
            msgMoveToFolder("envNdrWithCoRecipNotified", maildir, mbox, key, inMsg,)
            marmeTrackingLib.deliveryEvent_coRecipientNotified(
                bxoId,
                sr,
                inMsg,
            )
        else:
            b_io.eh.critical_oops()

    elif dsnType == DsnType.tmpNonDeliveryReport:
        if runMode == 'dryRun':
            pass
        elif runMode == 'runDebug':
            if action_tmpNonDeliveryReport:
                action_tmpNonDeliveryReport(
                    bxoId,
                    sr,
                    inMsg,
                    failedMsg,
                    tempFailedRecipients,
                    permFailedRecipients,
                    coRecipients,
                    dsnType,
                )
        elif  runMode == 'fullRun':
            if action_tmpNonDeliveryReport:
                action_tmpNonDeliveryReport(
                    bxoId,
                    sr,
                    inMsg,
                    failedMsg,
                    tempFailedRecipients,
                    permFailedRecipients,
                    coRecipients,
                    dsnType,
                )
            msgMoveToFolder("envTmpNdr", maildir, mbox, key, inMsg,)
            marmeTrackingLib.deliveryEvent_tmpNdr(
                bxoId,
                sr,
                inMsg,
            )
        else:
            b_io.eh.critical_oops()


    elif dsnType == DsnType.notADsn:
        if runMode == 'dryRun':
            pass
        elif runMode == 'runDebug':
            if action_notADsn:
                action_notADsn(
                    inMsg,
                    failedMsg,
                    tempFailedRecipients,
                    permFailedRecipients,
                    coRecipients,
                    dsnType,
                )
        elif  runMode == 'fullRun':
            if action_notADsn:
                action_notADsn(
                    inMsg,
                    failedMsg,
                    tempFailedRecipients,
                    permFailedRecipients,
                    coRecipients,
                    dsnType,
                )
            msgMoveToFolder("envNotADsn", maildir, mbox, key, inMsg,)

    else:
        b_io.eh.critical_oops()



"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(delete-other-windows)][(1)]]      *DSN (Delivery Status Notification) Type Processors*
"""


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Enum         ::  DsnType    [[elisp:(org-cycle)][| ]]
"""
DsnType = enum.Enum(
    deliveryReport='deliveryReport',
    receiptNotification='receiptNotification',
    ndrNoCoRecipients='ndrNoCoRecipients',
    ndrWithCoRecipients='ndrWithCoRecipients',
    tmpNonDeliveryReport='tmpNonDeliveryReport',
    notADsn='notADsn',
)


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func         ::  msgDsnTypeDetect    [[elisp:(org-cycle)][| ]]
"""
def msgDsnTypeDetect(
    inMsg,
    failedMsg,
    tempFailedRecipients,
    permFailedRecipients,
    coRecipients,
):
    """
** Returns a DsnType.
"""
    if tempFailedRecipients:
        return DsnType.tmpNonDeliveryReport

    elif permFailedRecipients:
        if coRecipients:
            return DsnType.ndrWithCoRecipients
        else:
            return DsnType.ndrNoCoRecipients

    # Delivery Report Needs To Be Detected

    # Receipt Notification Needs To Be Detected

    elif inMsg['subject'] == "Delivery delay notification":
        return DsnType.tmpNonDeliveryReport

    else:
        return DsnType.notADsn

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func         ::  dsnTypeShortReport    [[elisp:(org-cycle)][| ]]
"""
def dsnTypeShortReport(
        inMsg,
        typeStr,
):
    icm.ANN_note("""{typeStr:15}:: {msgId}""".format(
        typeStr=typeStr, msgId=str(inMsg['message-id']),))


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func         ::  dsnTypeLongReport    [[elisp:(org-cycle)][| ]]
"""
@io.track.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def dsnTypeLongReport(
        inMsg,
        typeStr,
):
    icm.ANN_note("""{typeStr:20}:: {msgId} -- {date} -- {subject}""".format(
        typeStr=typeStr, msgId=str(inMsg['message-id']),
        date=str(inMsg['date']), subject=str(inMsg['subject']),
        ))


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func         ::  dsnTypeReports    [[elisp:(org-cycle)][| ]]
"""
@io.track.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def dsnTypeReports(
    inMsg,
    dsnType,
    reportType,
):

    def dsnTypeStrReport(
            inMsg,
            typeStr,
            reportType,
    ):
        if reportType == "short":
            dsnTypeShortReport(inMsg, typeStr,)
        elif reportType == "long":
            dsnTypeLongReport(inMsg, typeStr,)
        else:
            b_io.eh.critical_oops()

    if dsnType == DsnType.deliveryReport:
        dsnTypeStrReport(inMsg, "Delivery Report", reportType,)

    elif dsnType == DsnType.receiptNotification:
        dsnTypeStrReport(inMsg, "Receipt Notification", reportType,)

    elif dsnType == DsnType.ndrNoCoRecipients:
        dsnTypeStrReport(inMsg, "ndrNoCoRecipients", reportType,)

    elif dsnType == DsnType.ndrWithCoRecipients:
        dsnTypeStrReport(inMsg, "ndrWithCoRecipients", reportType,)

    elif dsnType == DsnType.tmpNonDeliveryReport:
        dsnTypeStrReport(inMsg, "tmpNonDeliveryReport", reportType,)

    elif dsnType == DsnType.notADsn:
        dsnTypeStrReport(inMsg, "Not A DSN", reportType,)

    else:
        b_io.eh.critical_oops()



"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(delete-other-windows)][(1)]]      *Support Functions For MsgProcs*
"""

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func         ::  fromNonDeliveryReportGetFailedMsg    [[elisp:(org-cycle)][| ]]
"""
@io.track.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def fromNonDeliveryReportGetFailedMsg(
    nonDeliveryReportMsg,
    tempFailedRecipients,
    permFailedRecipients,
):
    """
** returns the extracted failed message from the non-delivery-report. Or None.
"""

    if not (tempFailedRecipients or permFailedRecipients):
        # This is NOT a nonDeliveryReport
        return None

    #
    # Get the failed message as an attachement
    #
    for part in nonDeliveryReportMsg.walk():
        if part.get_content_type() == 'message/rfc822':
            failedMsgList = part.get_payload()
            if failedMsgList:
                #for failedMsg in failedMsgList:
                nuOfFailedMsgs = len(failedMsgList)
                if nuOfFailedMsgs != 1:
                    b_io.eh.problem_info("More Then One -- Expected One")
                    return None
                else:
                    return failedMsgList[0]

    #
    # So,the failed message was not included and is part of the body.
    #

    #scre = re.compile(b'mail to the following recipients could not be delivered')
    scre = re.compile(b'-- The header and top 20 lines of the message follows --')

    msg = nonDeliveryReportMsg
    failedMsgStr = ""
    found = False
    for line in msg.get_payload(decode=True).splitlines():
        if scre.search(line):
            found = "gotIt"
            continue
        if found == "gotIt":  # This consumes an empty line
            found = True
            continue
        if found == True:
            failedMsgStr = failedMsgStr + line + '\n'

    if found:
        return email.message_from_string(failedMsgStr)
    else:
        return None

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func         ::  fromFailedMsgGetCoRecipients    [[elisp:(org-cycle)][| ]]
"""
@io.track.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def fromFailedMsgGetCoRecipients(
    failedMsg,
    tempFailedRecipients,
    permFailedRecipients,
):
    """
** Return list of CoRecipients or None
"""
    if not (tempFailedRecipients or permFailedRecipients):
        # This is NOT a nonDeliveryReport
        return None

    if not failedMsg:
        b_io.eh.critical_unassigedError("UnFound FailedMsg")
        return None

    allRecipients= None

    tos = failedMsg.get_all('to', [])
    ccs = failedMsg.get_all('cc', [])
    resent_tos = failedMsg.get_all('resent-to', [])
    resent_ccs = failedMsg.get_all('resent-cc', [])
    allRecipients = email.utils.getaddresses(tos + ccs + resent_tos + resent_ccs)

    if not allRecipients:
        b_io.eh.problem_unassignedError("allRecipients is None")
        return None

    allRecipientsSet = set()
    for thisRecipient in allRecipients:
        allRecipientsSet.add(thisRecipient[1])

    failedRecipients = tempFailedRecipients | permFailedRecipients

    coRecipientsSet = allRecipientsSet - failedRecipients

    if coRecipientsSet:
        return coRecipientsSet
    else:
        return None


"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(delete-other-windows)][(1)]]      *Msg ReFiling*
"""


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func         ::  msgMoveToFolder    [[elisp:(org-cycle)][| ]]
"""
@io.track.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def msgMoveToFolder(
        destFolder,
        srcMaildir,
        srcMbox,
        srcKey,
        srcMsg,
):
    """
** Given a srcMbox and a srcMsg, move it to the specified  destination.
"""
    srcMailBase = os.path.dirname(srcMaildir)

    destMbox = mailbox.Maildir(
            os.path.join(srcMailBase, destFolder),
            factory=None,  # important!! default does not work
    )

    # Write copy to disk before removing original.
    # If there's a crash, you might duplicate a message, but
    # that's better than losing a message completely.
    destMbox.lock()
    destMbox.add(srcMsg)
    destMbox.flush()
    destMbox.unlock()

    # Remove original message
    srcMbox.lock()
    srcMbox.discard(srcKey)
    srcMbox.flush()
    srcMbox.unlock()

    destMbox.close()



"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(delete-other-windows)][(1)]]      *Msg Sending*
"""

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Msg-Send     ::  msgSend_test_permanentNdrToCoRecepiets    [[elisp:(org-cycle)][| ]]
"""
@io.track.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def msgSend_test_permanentNdrToCoRecipients(
        bxoId,
        sr,
        inMsg,
        failedMsg,
        tempFailedRecipients,
        permFailedRecipients,
        coRecipients,
        dsnType,
):
    """ Given a nonDeliveryReportMsg, We focus on the failedMsg
    """

    testToLine = "test@mohsen.banan.1.byname.net"


    failedRecipients = tempFailedRecipients | permFailedRecipients

    failedFromLine = failedMsg['From']
    failedSubjectLine = failedMsg['Subject']
    failedDateLine = failedMsg['date']

    msg = MIMEMultipart()

    msg['Date'] = email.utils.formatdate(localtime = 1)
    msg['Message-ID'] = email.utils.make_msgid()

    msg['Subject'] = """Co-Recipient Non-Delivery-Report  -- Was: {failedSubjectLine}""".format(
        failedSubjectLine=failedSubjectLine)

    msg['From'] = failedFromLine

    toLine = ""

    for thisRecipient in coRecipients:
        if toLine:
            toLine = toLine + ', ' + thisRecipient
        else:
            toLine = thisRecipient

    msg['To'] = testToLine


    msg.preamble = 'Multipart massage.\n'

    #pp = pprint.PrettyPrinter(indent=4)

    mailBodyStr = """\

Real To Line: {toLine}

A previous message
    Dated: {failedDateLine}
    To: {failedRecipients}
for which you were also a recipient, failed.

This is to let you know that we have received a non-delivery-report (bounce message)
for that email and since you were also a recepient of that email, we are letting you
know that {failedRecipients} did not recieve that email.

A full copy of the non-delivery-report that we received is attached.

This is a machine generated email and is purely informational.


    """.format(
        failedDateLine=failedDateLine,
        toLine=toLine,
        failedRecipients=" ".join(failedRecipients),
    )

    part = MIMEText(mailBodyStr)
    msg.attach(part)

    part = MIMEBase('message', "rfc822")
    part.set_payload(inMsg.as_string())
    #Encoders.encode_base64(part)

    msg.attach(part)

    sendingMethod = msgOut.SendingMethod.submit

    if msgOut.sendingMethodSet(msg, sendingMethod).isProblematic():
        return b_io.eh.badLastOutcome()

    if not marmeSendLib.bx822Set_sendWithEnabledAcct(bxoId, sr, msg, sendingMethod):
        return b_io.eh.problem_info("")

    cmndOutcome = marmeSendLib.sendCompleteMessage().cmnd(
        interactive=False,
        bxoId=bxoId,
        sr=sr,
        msg=msg,
    )

    return cmndOutcome




"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Msg-Send     ::  msgSend_permanentNdrToCoRecepiets    [[elisp:(org-cycle)][| ]]
"""
@io.track.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def msgSend_permanentNdrToCoRecepietsObsoleted(
        failedRecipients,
        nonDeliveryReportMsg,
):
    """ Given a nonDeliveryReportMsg, We focus on the failedMsg
    """



    allRecipients= None

    failedMsgWasFound = False

    for part in nonDeliveryReportMsg.walk():
        if part.get_content_type() == 'message/rfc822':
            failedMsgList = part.get_payload()
            failedMsgWasFound = True
            for failedMsg in failedMsgList:
                tos = failedMsg.get_all('to', [])
                ccs = failedMsg.get_all('cc', [])
                resent_tos = failedMsg.get_all('resent-to', [])
                resent_ccs = failedMsg.get_all('resent-cc', [])
                allRecipients = email.utils.getaddresses(tos + ccs + resent_tos + resent_ccs)
                failedFromLine = failedMsg['From']
                failedSubjectLine = failedMsg['Subject']
                failedDateLine = failedMsg['date']

            break

    if failedMsgWasFound is False:
        #io.eh.problem_unassignedError("Failed Message Was UnFound")
        return

    if not allRecipients:
        b_io.eh.problem_unassignedError("Failed Message Is Missing All Recipients")
        return

    allRecipientsSet = set()
    for thisRecipient in allRecipients:
        allRecipientsSet.add(thisRecipient[1])

    coRecipientsSet = allRecipientsSet - failedRecipients

    msg = MIMEMultipart()

    msg['Date'] = email.utils.formatdate(localtime = 1)
    msg['Message-ID'] = email.utils.make_msgid()

    msg['Subject'] = """Co-Recipient Non-Delivery-Report  -- Was: {failedSubjectLine}""".format(
        failedSubjectLine=failedSubjectLine)

    msg['From'] = failedFromLine

    toLine = ""

    for thisRecipient in coRecipientsSet:
        if toLine:
            toLine = toLine + ', ' + thisRecipient
        else:
            toLine = thisRecipient

    msg['To'] = "test@mohsen.banan.1.byname.net"


    msg.preamble = 'Multipart massage.\n'

    #pp = pprint.PrettyPrinter(indent=4)

    mailBodyStr = """\

Real To Line: {toLine}

A previous message
    Dated: {failedDateLine}
    To: {failedRecipients}
for which you were also a recipient, failed.

This is to let you know that we have received a non-delivery-report (bounce message)
for that email and since you were also a recepient of that email, we are letting you
know that {failedRecipients} did not recieve that email.

A full copy of the non-delivery-report that we received is attached.

This is a machine generated email and is purely informational.


    """.format(
        failedDateLine=failedDateLine,
        toLine=toLine,
        failedRecipients=" ".join(failedRecipients),
    )

    part = MIMEText(mailBodyStr)
    msg.attach(part)

    part = MIMEBase('message', "rfc822")
    part.set_payload(failedMsg.as_string())
    #Encoders.encode_base64(part)

    #part.add_header('Content-Disposition', 'attachment; filename="/etc/resolv.conf"')

    msg.attach(part)

    # msgSend_submitWith_byName_sa20000(
    #     msg=msg,
    #     envelopeAddr="test@mohsen.banan.1.byname.net",
    #     recipients=["test@mohsen.banan.1.byname.net"],
    # )

    return


####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "Main" :anchor ""  :extraInfo "Framework Dblock"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _Main_: |]]  Framework Dblock  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: b:py3:cs:framework/main :csInfo "csInfo" :noCmndEntry "examples" :extraParamsHook "g_extraParams" :importedCmndsModules "g_importedCmndsModules"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] =g_csMain= (csInfo, _examples_, g_extraParams, g_importedCmndsModules)
#+end_org """

if __name__ == '__main__':
    cs.main.g_csMain(
        csInfo=csInfo,
        noCmndEntry=examples,  # specify a Cmnd name
        extraParamsHook=g_extraParams,
        importedCmndsModules=g_importedCmndsModules,
    )

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
