#!/bin/env python
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
** This File: /bisos/git/auth/bxRepos/bisos-pip/marmee/py3/bin/marmeeSend.cs
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:py3:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['marmeeSend'], }
csInfo['version'] = '202502120253'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'marmeeSend-Panel.org'
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

####+BEGINNOT: b:py3:cs:framework/imports :basedOn "classification"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] *Imports* =Based on Classification=cs-u=
#+end_org """
from bisos import b
from bisos.b import cs
from bisos.b import b_io
from bisos.common import csParam

import collections
####+END:

import sys
import os

import email
#import mailbox
#import smtplib

#import flufl.bounce

from email.mime.text import MIMEText
#from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from bisos.marmee import x822Lib
from bisos.marmee import x822In
from bisos.marmee import x822Out

#
# Above should replace below NOTYET 2025 -- 
#
# from uni sos.x822Msg import msgOut
# from uni sos.x822Msg import msgIn
##from uni sos.x822Msg import msgLib


####+BEGINNOT: bx:dblock:global:file-insert :file "/libre/ByStar/InitialTemplates/update/sw/icm/py/curGetBxOSr.py"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children 10)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-BxoIdSr   :: /curGet_{bxoId,sr}/ retType=str argsList=nil  [[elisp:(org-cycle)][| ]]
"""

def curGet_bxoId(): return "" # bxCurrentsConfig.bxoId_fpObtain(configBaseDir=None)
def curGet_sr(): return "" # bxCurrentsConfig.sr_fpObtain(configBaseDir=None)
def cmndParsCurBxoSr(cps): cps['bxoId'] = curGet_bxoId(); cps['sr'] = curGet_sr()

####+END:


""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] ~csuList emacs-list Specifications~  [[elisp:(blee:org:code-block/above-run)][ /Eval Below/ ]] [[elisp:(org-cycle)][| ]]
#+BEGIN_SRC emacs-lisp
(setq  b:py:cs:csuList
  (list
   "bisos.b.cs.ro"
   "bisos.csPlayer.bleep"
   "bisos.marmee.marmeeSend"
 ))
#+END_SRC
#+RESULTS:
| bisos.b.cs.ro | bisos.csPlayer.bleep | bisos.marmee.marmeeSend |
#+end_org """

####+BEGIN: b:py3:cs:framework/csuListProc :pyImports t :csuImports t :csuParams t
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] =Process CSU List= with /3/ in csuList pyImports=t csuImports=t csuParams=t
#+end_org """

from bisos.b.cs import ro
from bisos.csPlayer import bleep
from bisos.marmee import marmeeSend


csuList = [ 'bisos.b.cs.ro', 'bisos.csPlayer.bleep', 'bisos.marmee.marmeeSend', ]

g_importedCmndsModules = cs.csuList_importedModules(csuList)

def g_extraParams():
    csParams = cs.param.CmndParamDict()
    cs.csuList_commonParamsSpecify(csuList, csParams)
    cs.argsparseBasedOnCsParams(csParams)

####+END:

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


####+BEGIN: bx:cs:py3:section :title "CS-Commands"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *CS-Commands*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

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

        # icm.ex_gCommon()

        bleep.examples_csBasic()

#         """
# **  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Examples   ::  General Dev and Testing IIFs [[elisp:(org-cycle)][| ]]
# """
#         cs.examples.menuChapter('*General Dev and Testing IIFs*')

#         cmndName = "unitTest" ; cmndArgs = "" ; cps = collections.OrderedDict()
#         cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='none')


        """
**  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Examples   ::  Default Mail From Complete File [[elisp:(org-cycle)][| ]]
"""

        fromLine = "mohsen.byname@gmail.com"
        toLine = fromLine
        marmeeSend.examples_csu(fromLine, toLine, sectionTitle="default")

        b.niche.examplesNicheRun("usageEnvs")

        return(cmndOutcome)


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "sendFromPartialFileWithPars" :comment "" :parsMand "" :parsOpt "outMailAcct inFile sendingMethod" :argsMin 0 :argsMax 0 :pyInv "msg"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<sendFromPartialFileWithPars>>  =verify= parsOpt=outMailAcct inFile sendingMethod ro=cli pyInv=msg   [[elisp:(org-cycle)][| ]]
#+end_org """
class sendFromPartialFileWithPars(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'outMailAcct', 'inFile', 'sendingMethod', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             outMailAcct: typing.Optional[str]=None,  # Cs Optional Param
             inFile: typing.Optional[str]=None,  # Cs Optional Param
             sendingMethod: typing.Optional[str]=None,  # Cs Optional Param
             msg: typing.Any=None,   # pyInv Argument
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'outMailAcct': outMailAcct, 'inFile': inFile, 'sendingMethod': sendingMethod, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        outMailAcct = csParam.mappedValue('outMailAcct', outMailAcct)
        inFile = csParam.mappedValue('inFile', inFile)
        sendingMethod = csParam.mappedValue('sendingMethod', sendingMethod)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Submit a message using inFile and pars: outMailAcct, submissionMethod.
        Augment with delivery/non-delivery requests and track.
        #+end_org """)

        G = cs.globalContext.get()

        if not msg:
            if inFile:
                msg = msgIn.getMsgFromFile(inFile)
            else:
                # Stdin then
                msg = msgIn.getMsgFromStdin()

        b_io.tm.here(msgOut.strLogMessage(
            "Msg As Input:", msg,))

        if not sendingMethod:
            sendingMethod = msgOut.SendingMethod.submit
        if msgOut.sendingMethodSet(msg, sendingMethod).isProblematic():
            return msgOut.sendingMethodSet(msg, sendingMethod)

        print(G.usageParams.runMode)

        if msgOut.sendingRunControlSet(msg, G.usageParams.runMode).isProblematic():
            return msgOut.sendingRunControlSet(msg, G.usageParams.runMode)


        envelopeAddr = msg['From']
        recipientsList = msg['To']

        msgOut.envelopeAddrSet(
            msg,
            mailBoxAddr=envelopeAddr,  # Mandatory
        )

        msgOut.crossRefInfo(
            msg,
            crossRefInfo="XrefForStatusNotifications"  # Mandatory
        )
        msgOut.nonDeliveryNotificationRequetsForTo(
            msg,
            recipientsList=recipientsList,
            notifyTo=envelopeAddr,
        )
        msgOut.nonDeliveryNotificationActions(
            msg,
            coRecipientsList=recipientsList,
        )
        msgOut.deliveryNotificationRequetsForTo(
            msg,
            recipientsList=recipientsList,
            notifyTo=envelopeAddr,
        )
        msgOut.dispositionNotificationRequetsForTo(
            msg,
            recipientsList=recipientsList,
            notifyTo=envelopeAddr,
        )

        if msgOut.sendingMethodSet(msg, sendingMethod).isProblematic():
            return b_io.eh.badLastOutcome()

        if not marmeSendLib.bx822Set_sendWithEnabledAcct(msg, sendingMethod):
            return b_io.eh.badOutcome(cmndOutcome)

        cmndOutcome = marmeSendLib.sendCompleteMessage().cmnd(
            interactive=False,
            msg=msg,
        )

        return cmndOutcome


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "msgSend_basic" :comment "" :parsMand "bxoId sr fromLine toLine" :parsOpt "sendingMethod" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<msgSend_basic>>  =verify= parsMand=bxoId sr fromLine toLine parsOpt=sendingMethod ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class msgSend_basic(cs.Cmnd):
    cmndParamsMandatory = [ 'bxoId', 'sr', 'fromLine', 'toLine', ]
    cmndParamsOptional = [ 'sendingMethod', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bxoId: typing.Optional[str]=None,  # Cs Mandatory Param
             sr: typing.Optional[str]=None,  # Cs Mandatory Param
             fromLine: typing.Optional[str]=None,  # Cs Mandatory Param
             toLine: typing.Optional[str]=None,  # Cs Mandatory Param
             sendingMethod: typing.Optional[str]=None,  # Cs Optional Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'bxoId': bxoId, 'sr': sr, 'fromLine': fromLine, 'toLine': toLine, 'sendingMethod': sendingMethod, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        bxoId = csParam.mappedValue('bxoId', bxoId)
        sr = csParam.mappedValue('sr', sr)
        fromLine = csParam.mappedValue('fromLine', fromLine)
        toLine = csParam.mappedValue('toLine', toLine)
        sendingMethod = csParam.mappedValue('sendingMethod', sendingMethod)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]
        #+end_org """)

        if not sendingMethod:
            sendingMethod = msgOut.SendingMethod.submit

        msg = MIMEMultipart()

        msg['From'] = fromLine
        msg['To'] = toLine

        msg['Subject'] = """Example Of A Simple And Untracked Message"""

        msg.preamble = 'Multipart massage.\n'

        part = MIMEText(
            """
This is a simple example message with a simple attachment
being sent using the current enabled controlledProfile and mailAcct.

On the sending end, use mailAcctsManage.py with
-i enabledControlProfileSet and -i enabledMailAcctSet
to select the outgoing profile. The current settings are:
    ControlProfile={controlProfile}  -- MailAcct={mailAcct}

This message is then submitted for sending with sendCompleteMessage().cmnd(msg)

Please find example of an attached file\n
            """.format(
                controlProfile=marmeAcctsLib.enabledControlProfileObtain(),
                mailAcct=marmeAcctsLib.enabledInMailAcctObtain()
            )
        )
        msg.attach(part)

        part = MIMEBase('application', "octet-stream")
        part.set_payload(open("/etc/resolv.conf", "rb").read())
        encoders.encode_base64(part)

        part.add_header('Content-Disposition', 'attachment; filename="/etc/resolv.conf"')

        msg.attach(part)

        if msgOut.sendingMethodSet(msg, sendingMethod).isProblematic():
            return b_io.eh.badLastOutcome()

        if not marmeSendLib.bx822Set_sendWithEnabledAcct(
                msg=msg,
                sendingMethod=sendingMethod,
                bxoId=bxoId,
                sr=sr,
        ):
            return b_io.eh.badOutcome(cmndOutcome)

        cmndOutcome = marmeSendLib.sendCompleteMessage().cmnd(
            interactive=False,
            msg=msg,
            bxoId=bxoId,
            sr=sr,
        )

        return cmndOutcome

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "msgSend_tracked" :comment "" :parsMand "bxoId sr fromLine toLine" :parsOpt "sendingMethod" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<msgSend_tracked>>  =verify= parsMand=bxoId sr fromLine toLine parsOpt=sendingMethod ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class msgSend_tracked(cs.Cmnd):
    cmndParamsMandatory = [ 'bxoId', 'sr', 'fromLine', 'toLine', ]
    cmndParamsOptional = [ 'sendingMethod', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bxoId: typing.Optional[str]=None,  # Cs Mandatory Param
             sr: typing.Optional[str]=None,  # Cs Mandatory Param
             fromLine: typing.Optional[str]=None,  # Cs Mandatory Param
             toLine: typing.Optional[str]=None,  # Cs Mandatory Param
             sendingMethod: typing.Optional[str]=None,  # Cs Optional Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'bxoId': bxoId, 'sr': sr, 'fromLine': fromLine, 'toLine': toLine, 'sendingMethod': sendingMethod, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        bxoId = csParam.mappedValue('bxoId', bxoId)
        sr = csParam.mappedValue('sr', sr)
        fromLine = csParam.mappedValue('fromLine', fromLine)
        toLine = csParam.mappedValue('toLine', toLine)
        sendingMethod = csParam.mappedValue('sendingMethod', sendingMethod)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]
        #+end_org """)

        #G = cs.globalContext.get()

        if not sendingMethod:
            sendingMethod = msgOut.SendingMethod.submit

        msg = email.message.Message()  #msg = MIMEText() # MIMEMultipart()

        msg['From'] = fromLine
        msg['To'] = toLine

        msg['Subject'] = """Example Of A Simple And Tracked Message"""

        envelopeAddr = fromLine

        if msgOut.sendingMethodSet(msg, sendingMethod).isProblematic():
            return msgOut.sendingMethodSet(msg, sendingMethod)

        msg.add_header('Content-Type', 'text')
        msg.set_payload(
            """
This is a simple example message with a simple attachment
being sent using the current enabled controlledProfile and mailAcct.

On the sending end, use mailAcctsManage.py with
-i enabledControlProfileSet and -i enabledMailAcctSet
to select the outgoing profile. The current settings are:
    ControlProfile={controlProfile}  -- MailAcct={mailAcct}

This message is then submitted for sending with sendCompleteMessage().cmnd(msg)

            """.format(
                controlProfile=marmeAcctsLib.enabledControlProfileObtain(
                    curGet_bxoId(),
                    curGet_sr(),
                ),
                mailAcct=marmeAcctsLib.enabledInMailAcctObtain(
                    curGet_bxoId(),
                    curGet_sr(),
                )
            )
        )


        #
        ###########################
        #
        # Above is the real content of the email.
        #
        # We now augment the message with:
        #   - explicit envelope address -- To be used for Delivery-Status-Notifications (DSN)
        #   - The email is be tagged for crossReferencing when DSN is received (e.g. with peepid)
        #   - Request that non-delivery-reports be acted upon and sent to co-recipients
        #   - Explicit delivery-reports are requested
        #   - Explicit read-receipts are requested
        #   - Injection/Submission parameters are specified
        # The message is then sent out
        #

        msgOut.envelopeAddrSet(
            msg,
            mailBoxAddr=envelopeAddr,  # Mandatory
        )

        #
        # peepId will be used to crossRef StatusNotifications
        #
        msgOut.crossRefInfo(
            msg,
            crossRefInfo="XrefForStatusNotifications"  # Mandatory
        )

        #
        # Delivery Status Notifications will be sent to notifyTo=envelopeAddr
        #
        msgOut.nonDeliveryNotificationRequetsForTo(
            msg,
            notifyTo=envelopeAddr,
        )

        #
        # In case of Non-Delivery, coRecipientsList will be informed
        #
        msgOut.nonDeliveryNotificationActions(
            msg,
            coRecipientsList=[toLine],
        )

        #
        # Explicit Delivery Report is requested
        #
        msgOut.deliveryNotificationRequetsForTo(
            msg,
            recipientsList=[toLine],
            notifyTo=envelopeAddr,
        )

        #
        # Explicit Read Receipt is requested
        #
        msgOut.dispositionNotificationRequetsForTo(
            msg,
            recipientsList=[toLine],
            notifyTo=envelopeAddr,
        )

        if msgOut.sendingMethodSet(msg, sendingMethod).isProblematic():
            return b_io.eh.badLastOutcome()

        if not marmeSendLib.bx822Set_sendWithEnabledAcct(
                msg=msg,
                sendingMethod=sendingMethod,
                bxoId=bxoId,
                sr=sr,
        ):
            return b_io.eh.badOutcome(cmndOutcome)

        cmndOutcome = marmeSendLib.sendCompleteMessage().cmnd(
            interactive=False,
            msg=msg,
            bxoId=bxoId,
            sr=sr,
        )

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
