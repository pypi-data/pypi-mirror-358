# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: A =CmndSvc= for
#+end_org """

####+BEGIN: b:py3:cs:file/dblockControls :classification "cs-u"
""" #+begin_org
* [[elisp:(org-cycle)][| /Control Parameters Of This File/ |]] :: dblk ctrls classifications=cs-u
#+BEGIN_SRC emacs-lisp
(setq-local b:dblockControls t) ; (setq-local b:dblockControls nil)
(put 'b:dblockControls 'py3:cs:Classification "cs-u") ; one of cs-mu, cs-u, cs-lib, b-lib, pyLibPure
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
** This File: /bisos/git/auth/bxRepos/bisos-pip/marmee/py3/bisos/marmee/x822In.py
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:py3:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['x822In'], }
csInfo['version'] = '202210204409'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'x822In-Panel.org'
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

import sys
import os

import collections

from unisos import ucf
from unisos import icm

from bisos.csPlayer import bleep

from bisos.currents import bxCurrentsConfig

from unisos.x822Msg import msgOut
#from bxMsg import msgIn
#from bxMsg import msgLib

from bisos.marmee import marmeAcctsLib
from bisos.marmee import marmeSendLib
from bisos.marmee import marmeTrackingLib

import re

import email
import mailbox

import flufl.bounce

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase




####+BEGIN: bx:dblock:python:subSection :title "Topic SubSection"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ================ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]          *Topic SubSection*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Enum         ::  DsnType    [[elisp:(org-cycle)][| ]]
"""
DsnType = ucf.Enum(
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
@io.track.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
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
@io.track.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
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




####+BEGIN: b:py3:cs:framework/endOfFile :basedOn "classification"
""" #+begin_org
* [[elisp:(org-cycle)][| *End-Of-Editable-Text* |]] :: emacs and org variables and control parameters
#+end_org """

#+STARTUP: showall

### local variables:
### no-byte-compile: t
### end:
####+END:
