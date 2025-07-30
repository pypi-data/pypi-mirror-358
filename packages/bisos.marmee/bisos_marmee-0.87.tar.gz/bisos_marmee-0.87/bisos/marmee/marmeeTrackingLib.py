# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: A =CS-Lib= for Tracking MARMEE processed Messages.
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
** This File: /bisos/git/auth/bxRepos/bisos-pip/marmee/py3/bisos/marmee/marmeeTrackingLib.py
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:py3:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['marmeeTrackingLib'], }
csInfo['version'] = '202210201255'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'marmeeTrackingLib-Panel.org'
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
* [[elisp:(org-cycle)][| Controls |]] :: [[elisp:(delete-other-windows)][(1)]] | [[elisp:(show-all)][Show-All]]  [[elisp:(org-shifttab)][Overview]]  [[elisp:(progn (org-shifttab) (org-content))][Content]] | [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] | [[elisp:(bx:org:run-me)][Run]] | [[elisp:(bx:org:run-me-eml)][RunEml]] | [[elisp:(progn (save-buffer) (kill-buffer))][S&Q]]  [[elisp:(save-buffer)][Save]]  [[elisp:(kill-buffer)][Quit]] [[elisp:(org-cycle)][| ]]
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
** Imports Based On Classification=cs-u
#+end_org """
from bisos import b
from bisos.b import cs
from bisos.b import b_io

import collections
####+END:

#from bisos.marmee import marmeAcctsLib
#from bisos.currents import bxCurrentsConfig

from datetime import datetime
import time


####+BEGIN: bx:cs:python:section :title "Common Module Conventions (BxoIdSr)"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Common Module Conventions (BxoIdSr)*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:

####+BEGINNOT: bx:dblock:global:file-insert :file "/libre/ByStar/InitialTemplates/update/sw/icm/py/curGetBxOSr.py"
####+END:


####+BEGIN: bx:cs:python:section :title "Obtain ICM-Package Run-Time Bases"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Obtain ICM-Package Run-Time Bases*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:

####+BEGIN: bx:cs:python:func :funcName "trackDeliveryBaseDirGet" :funcType "anyOrNone" :retType "bool" :deco "" :argsList "bxoId sr"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /trackDeliveryBaseDirGet/ retType=bool argsList=(bxoId sr)  [[elisp:(org-cycle)][| ]]
#+end_org """
def trackDeliveryBaseDirGet(
    bxoId,
    sr,
):
####+END:
    return(
        marmeAcctsLib.logBaseDirGet(
            bxoId=bxoId,
            sr=sr,
        )
    )


####+BEGIN: bx:cs:python:func :funcName "trackDeliveryLogFileGet" :funcType "anyOrNone" :retType "bool" :deco "" :argsList "bxoId sr"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /trackDeliveryLogFileGet/ retType=bool argsList=(bxoId sr)  [[elisp:(org-cycle)][| ]]
#+end_org """
def trackDeliveryLogFileGet(
    bxoId,
    sr,
):
####+END:
    return(
        os.path.join(
            trackDeliveryBaseDirGet(
                bxoId=bxoId,
                sr=sr,
            ),
            "marmeTrackDelivery.log",
        )
    )




####+BEGIN: bx:cs:python:section :title "Common Examples Section"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Common Examples Section*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:


####+BEGIN: bx:cs:python:func :funcName "examples_deliveryTrackings" :funcType "anyOrNone" :retType "bool" :deco "" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /examples_deliveryTrackings/ retType=bool argsList=nil  [[elisp:(org-cycle)][| ]]
#+end_org """
def examples_deliveryTrackings():
####+END:
    """."""

    def cpsInit(): return collections.OrderedDict()
    def menuItem(verbosity): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity=verbosity) # 'little' or 'none'
    def execLineEx(cmndStr): cs.examples.execInsert(execLine=cmndStr)

    cs.examples.menuChapter('* =INFO=  Delivery Trackings Show*')

    cmndName = "deliveryTrackingsShow" ; cmndArgs = ""
    cps=cpsInit(); # cmndParsCurBxoSr(cps);
    menuItem(verbosity='none') ;  menuItem(verbosity='little')

    return


####+BEGIN: bx:cs:python:section :title "Common ICMs Section"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Common ICMs Section*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:



####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "deliveryTrackingsShow" :comment "" :parsMand "bxoId sr" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<deliveryTrackingsShow>>  =verify= parsMand=bxoId sr ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class deliveryTrackingsShow(cs.Cmnd):
    cmndParamsMandatory = [ 'bxoId', 'sr', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bxoId: typing.Optional[str]=None,  # Cs Mandatory Param
             sr: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        callParamsDict = {'bxoId': bxoId, 'sr': sr, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
####+END:

        trackDeliveryLogFile = trackDeliveryLogFileGet(
            bxoId=bxoId,
            sr=sr,
        )

        b_io.tm.here(trackDeliveryLogFile)

        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=None,
        )

####+BEGIN: bx:cs:python:section :title "Delivery Recording Interface"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Delivery Recording Interface*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:

####+BEGIN: b:py3:cs:func/args :funcName "deliveryEventRecord" :funcType "void" :retType "bool" :deco "default" :argsList "bxoId sr eventId msgId eventInfoStr"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-A-void   [[elisp:(outline-show-subtree+toggle)][||]] /deliveryEventRecord/ deco=default  [[elisp:(org-cycle)][| ]] deco=default  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def deliveryEventRecord(
    bxoId,
    sr,
    eventId,
    msgId,
    eventInfoStr,
):
####+END:

    trackDeliveryLogFile = trackDeliveryLogFileGet(
        bxoId=bxoId,
        sr=sr,
    )

    ts = time.time()
    dateTag = datetime.fromtimestamp(ts).strftime('%y%m%d%H%M%S')

    if not msgId:
        msgId="BlankMsgId"

    with open(trackDeliveryLogFile,'a') as f:
        f.write(
            "{date}:{msgId}:{eventId}:{eventInfoStr}\n"
            .format(
                date=dateTag,
                msgId=msgId,
                eventId=eventId,
                eventInfoStr=eventInfoStr,
            )
        )


####+BEGIN: bx:cs:python:section :title "deliveryEvent_ State Transition Events Interface"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *deliveryEvent_ State Transition Events Interface*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:

####+BEGIN: b:py3:cs:func/args :funcName "deliveryEvent_injectBefore" :funcType "void" :retType "bool" :deco "default" :argsList "bxoId sr msg"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-A-void   [[elisp:(outline-show-subtree+toggle)][||]] /deliveryEvent_injectBefore/ deco=default  [[elisp:(org-cycle)][| ]] deco=default  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def deliveryEvent_injectBefore(
    bxoId,
    sr,
    msg,
):
####+END:

    eventId = "injectBefore"
    msgId = msg['Message-ID']
    eventInfoStr = ""

    deliveryEventRecord(
        bxoId,
        sr,
        eventId,
        msgId,
        eventInfoStr,
    )

####+BEGIN: b:py3:cs:func/args :funcName "deliveryEvent_injectAfter" :funcType "void" :retType "bool" :deco "default" :argsList "bxoId sr msg"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-A-void   [[elisp:(outline-show-subtree+toggle)][||]] /deliveryEvent_injectAfter/ deco=default  [[elisp:(org-cycle)][| ]] deco=default  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def deliveryEvent_injectAfter(
    bxoId,
    sr,
    msg,
):
####+END:

    eventId = "injectAfter"
    msgId = msg['Message-ID']
    eventInfoStr = ""

    deliveryEventRecord(
        bxoId,
        sr,
        eventId,
        msgId,
        eventInfoStr,
    )

####+BEGIN: b:py3:cs:func/args :funcName "deliveryEvent_submissionConfirmed" :funcType "void" :retType "bool" :deco "default" :argsList "bxoId sr msg"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-A-void   [[elisp:(outline-show-subtree+toggle)][||]] /deliveryEvent_submissionConfirmed/ deco=default  [[elisp:(org-cycle)][| ]] deco=default  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def deliveryEvent_submissionConfirmed(
    bxoId,
    sr,
    msg,
):
####+END:

    eventId = "submissionConfirmed"
    msgId = msg['Message-ID']
    eventInfoStr = ""

    deliveryEventRecord(
        bxoId,
        sr,
        eventId,
        msgId,
        eventInfoStr,
    )


####+BEGIN: b:py3:cs:func/args :funcName "deliveryEvent_submissionFailed" :funcType "void" :retType "bool" :deco "default" :argsList "bxoId sr msg"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-A-void   [[elisp:(outline-show-subtree+toggle)][||]] /deliveryEvent_submissionFailed/ deco=default  [[elisp:(org-cycle)][| ]] deco=default  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def deliveryEvent_submissionFailed(
    bxoId,
    sr,
    msg,
):
####+END:

    eventId = "submissionFailed"
    msgId = msg['Message-ID']
    eventInfoStr = ""

    deliveryEventRecord(
        bxoId,
        sr,
        eventId,
        msgId,
        eventInfoStr,
    )



####+BEGIN: b:py3:cs:func/args :funcName "deliveryEvent_tmpNdr" :funcType "void" :retType "bool" :deco "default" :argsList "bxoId sr msg"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-A-void   [[elisp:(outline-show-subtree+toggle)][||]] /deliveryEvent_tmpNdr/ deco=default  [[elisp:(org-cycle)][| ]] deco=default  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def deliveryEvent_tmpNdr(
    bxoId,
    sr,
    msg,
):
####+END:
    """Used To Be trackEnvTmpNdr"""

    eventId = "tmpNdr"
    msgId = msg['Message-ID']
    eventInfoStr = ""

    deliveryEventRecord(
        bxoId,
        sr,
        eventId,
        msgId,
        eventInfoStr,
    )

####+BEGIN: b:py3:cs:func/args :funcName "deliveryEvent_permNdr" :funcType "void" :retType "bool" :deco "default" :argsList "bxoId sr msg"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-A-void   [[elisp:(outline-show-subtree+toggle)][||]] /deliveryEvent_permNdr/ deco=default  [[elisp:(org-cycle)][| ]] deco=default  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def deliveryEvent_permNdr(
    bxoId,
    sr,
    msg,
):
####+END:
    """Used To Be trackEnvPermNdr"""

    eventId = "permNdr"
    msgId = msg['Message-ID']
    eventInfoStr = ""

    deliveryEventRecord(
        bxoId,
        sr,
        eventId,
        msgId,
        eventInfoStr,
    )



####+BEGIN: b:py3:cs:func/args :funcName "deliveryEvent_deliveryReport" :funcType "void" :retType "bool" :deco "default" :argsList "bxoId sr msg"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-A-void   [[elisp:(outline-show-subtree+toggle)][||]] /deliveryEvent_deliveryReport/ deco=default  [[elisp:(org-cycle)][| ]] deco=default  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def deliveryEvent_deliveryReport(
    bxoId,
    sr,
    msg,
):
####+END:
    """Used To Be trackEnvDeliveryReport"""

    eventId = "deliveryReport"
    msgId = msg['Message-ID']
    eventInfoStr = ""

    deliveryEventRecord(
        bxoId,
        sr,
        eventId,
        msgId,
        eventInfoStr,
    )


####+BEGIN: b:py3:cs:func/args :funcName "deliveryEvent_receiptNotification" :funcType "void" :retType "bool" :deco "default" :argsList "bxoId sr msg"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-A-void   [[elisp:(outline-show-subtree+toggle)][||]] /deliveryEvent_receiptNotification/ deco=default  [[elisp:(org-cycle)][| ]] deco=default  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def deliveryEvent_receiptNotification(
    bxoId,
    sr,
    msg,
):
####+END:
    """Used To Be trackEnvFromReceiptNotification"""

    eventId = "receiptNotification"
    msgId = msg['Message-ID']
    eventInfoStr = ""

    deliveryEventRecord(
        bxoId,
        sr,
        eventId,
        msgId,
        eventInfoStr,
    )


####+BEGIN: b:py3:cs:func/args :funcName "deliveryEvent_coRecipientNotified" :funcType "void" :retType "bool" :deco "default" :argsList "bxoId sr msg"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-A-void   [[elisp:(outline-show-subtree+toggle)][||]] /deliveryEvent_coRecipientNotified/ deco=default  [[elisp:(org-cycle)][| ]] deco=default  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def deliveryEvent_coRecipientNotified(
    bxoId,
    sr,
    msg,
):
####+END:
    """Used To Be trackSentCoRecipient"""

    eventId = "coRecipientNotified"
    msgId = msg['Message-ID']
    eventInfoStr = ""

    deliveryEventRecord(
        bxoId,
        sr,
        eventId,
        msgId,
        eventInfoStr,
    )


####+BEGIN: bx:cs:python:section :title "deliveryEvent_ Locating Interface"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *deliveryEvent_ Locating Interface*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || IIF       ::  givenTrackIdGetMsgId    [[elisp:(org-cycle)][| ]]
"""
def givenTrackIdGetMsgId(
    msg,
):
    """
** NOTYET
"""
    return


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || IIF       ::  givenTrackIdGetState    [[elisp:(org-cycle)][| ]]
"""
def givenTrackIdGetState(
    msg,
):
    """
** NOTYET
"""
    return


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || IIF       ::  givenMsgIdGetTrackId    [[elisp:(org-cycle)][| ]]
"""
def givenMsgIdGetTrackId(
    msg,
):
    """
** NOTYET
"""
    return



####+BEGIN: b:py3:cs:framework/endOfFile :basedOn "classification"
""" #+begin_org
* [[elisp:(org-cycle)][| *End-Of-Editable-Text* |]] :: emacs and org variables and control parameters
#+end_org """

#+STARTUP: showall

### local variables:
### no-byte-compile: t
### end:
####+END:
