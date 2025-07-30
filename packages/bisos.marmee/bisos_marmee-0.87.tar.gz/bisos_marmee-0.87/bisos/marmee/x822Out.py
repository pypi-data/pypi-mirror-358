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
**  [[elisp:(org-cycle)][| ]]   Model and Terminology                                      :Overview:
This module is part of BISOS and its primary documentation is in  http://www.by-star.net/PLPC/180047
** :Documentation: Authorative [[file:/lcnt/lgpc/bystar/permanent/facilities/marmee]]
** :Web:  http://www.by-star.net/PLPC/180051
** :Overview: (Functional Specification)
    msgOut is a library (set of facilities) that provide for
    composition and submission of email messages based on the
    *Mail Gui To Mail Submit Client Software Pipeline*
    model.
    During mail-composition, a number of mail-headers are
    added to the email header.
    When the email is to be sent, all the necessary information
    for the mail submission client is within the email headers.
    Standard capabilities of X822 Mail Submit Pipeline (X822-MSP) are:
      - Envelope-Addr specification
      - Deleivery-Status-Notifications Request  (bounce addresses and delivery reports)
      - Disposition-Notifications  (read-receipts)
      - Flexible Parameterized Message Submission (host, ssl, user, passwd)
** :SendingModel:
    Sending is the act of delivering the message to another
    process for the purpose of transfer.
    Sending can be one of:
*** Injection -- using the command line and pipes
*** Submission -- using a protocol (smtp, etc.)
** :CompositionModel: (Mail User Agent)
   The msg itself is used as a container to gether and carry
   all parameters and all requests for the message submission.
   The following local header fields are recognized:
*** BX-Non-Delivery-Notification
**** BX-Non-Delivery-Notification-Req-PerRecipient:
**** BX-Non-Delivery-Notification-Req-For:
**** BX-Non-Delivery-Notification-Req-To:
**** X-B-Non-Delivery-Notification-Actions:
*** BX-Delivery-Notification
**** BX-Delivery-Notification-Req-PerRecipient:
**** BX-Delivery-Notification-Req-For:
**** BX-Delivery-Notification-Req-To:
*** BX-Disposition-Notification
**** BX-Disposition-Notification-Req-PerRecipient:
**** BX-Disposition-Notification-Req-For:
**** BX-Disposition-Notification-Req-To:
*** X-B-Envelope-Addr:
*** X-B-CrossRef:
*** BX-Sending
**** BX-Sending-Method:          # inject, submit
**** BX-Sending-Run-Control:   # dryrun, debug
*** BX-MTA-Injection -- Obsoleted
**** BX-MTA-Injection-Plugins:   # for composite injection profile
**** BX-MTA-Injection-Method:    # inject, submit
**** BX-MTA-Injection-Control:   # dryrun, debug
*** BX-MTA-Rem
**** BX-MTA-Rem-Protocol:        # smtp
**** BX-MTA-Rem-Host:
**** BX-MTA-Rem-PortNu:
**** BX-MTA-Rem-User:
**** BX-MTA-Rem-Passwd:
**** BX-MTA-Rem-LinkConfidentiality:  ssl/tls
**** BX-MTA-Rem-CertFile:
**** BX-MTA-Rem-KeyFile:
**** BX-MTA-Submission-Pre-Plugins:    # executed before send
**** BX-MTA-Submission-Post-Plugins:   # executed after send for error reporting
** :SubmissionModel: (Mail Transfer Agent)
*** BX-MTA-Submission-Pre-Plugins are executued in order specified.
*** All the BX- headers are recognized and converted to params
*** Where appropriate BX- headers are converted to standard headers.
*** Some BX- headers are stripped
*** Complete SMTP Submit Protocol based on the email.smtp python library is executed.
*** BX-MTA-Submission-Post-Plugins are executued in order specified.
**      [End-Of-Description]

*       [[elisp:(org-show-subtree)][|=]]  [[elisp:(org-cycle)][| *Usage:* | ]]

**      How-Tos:
**      :Order: Of Invokations At Message Composition and Message Submission
*** import msgOut
*** envelopeAddrSet()
*** crossRefInfo()
*** nonDeliveryNotificationRequetsForTo()
*** deliveryNotificationRequetsForTo()
*** dispositionNotificationRequetsForTo()
*** injectionParams()
*** injectBasedOnHeadersInfo()
**      :Examples:
*** See msgOutExample.py

**      [End-Of-Usage]
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

import sys
import copy

import email
import smtplib

import enum

####+BEGIN: b:py3:cs:orgItem/basic :type "=Facility=  " :title "*Common Facilities*" :comment ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  =Facility=   [[elisp:(outline-show-subtree+toggle)][||]] *Common Facilities*   [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:func/typing :funcName "envelopeAddrSet" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /envelopeAddrSet/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def envelopeAddrSet(
####+END:
        msg,
        mailBoxAddr,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Set the msg's envelope address to mailBoxAddr, but only if it had not been previously set.
This will be used for delivery-reports and non-delivery-reports.
    #+end_org """

    if not 'X-B-Envelope-Addr' in msg:
        if mailBoxAddr:
            msg['X-B-Envelope-Addr'] = mailBoxAddr

    return

####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "Delivery Status Notification And Disposition Report Requests" :anchor "" :extraInfo ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _Delivery Status Notification And Disposition Report Requests_: |]]    [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END

####+BEGIN: b:py3:cs:func/typing :funcName "dispositionNotificationRequetsForTo" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /dispositionNotificationRequetsForTo/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def dispositionNotificationRequetsForTo(
####+END:
        msg,
        recipientsList=None,
        notifyTo=None,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Request Receipt-Nofications for each of recipientsList. Notifications are to be sent to notifyTo address.
    #+end_org """
    if recipientsList:
        msg['BX-Disposition-Notification-Req-For'] = ", ".join(recipientsList)

    if notifyTo:
        msg['BX-Disposition-Notification-Req-To'] = notifyTo

    return

####+BEGIN: b:py3:cs:func/typing :funcName "dispositionNotificationRequetsPerRecipient" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /dispositionNotificationRequetsPerRecipient/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def dispositionNotificationRequetsPerRecipient(
####+END:
        msg,
        perRecipientsList=None,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Place Holder.
    #+end_org """
    return

####+BEGIN: b:py3:cs:func/typing :funcName "deliveryNotificationRequetsForTo" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /deliveryNotificationRequetsForTo/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def deliveryNotificationRequetsForTo(
####+END:
        msg,
        recipientsList=None,
        notifyTo=None,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Request Delivery-Reports for each of recipientsList. Notifications are to be sent to notifyTo address.
    #+end_org """
    if recipientsList:
        msg['BX-Delivery-Notification-Req-For'] = ", ".join(recipientsList)

    if notifyTo:
        msg['BX-Delivery-Notification-Req-To'] = notifyTo

    return


####+BEGIN: b:py3:cs:func/typing :funcName "deliveryNotificationRequetsPerRecipient" :funcType "extTyped" :deco "track" :comment "Place Holder"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /deliveryNotificationRequetsPerRecipient/  Place Holder deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def deliveryNotificationRequetsPerRecipient(
####+END:
        msg,
        perRecipientsList=None,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Place Holder
    #+end_org """
    return

####+BEGIN: b:py3:cs:func/typing :funcName "nonDeliveryNotificationRequetsForTo" :funcType "extTyped" :deco "track" :comment ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /nonDeliveryNotificationRequetsForTo/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def nonDeliveryNotificationRequetsForTo(
####+END:
        msg,
        recipientsList=None,
        notifyTo=None,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Request Non-Delivery-Reports for each of recipientsList. Notifications are to be sent to notifyTo address.
    #+end_org """
    if recipientsList:
        msg['BX-Non-Delivery-Notification-Req-For'] = ", ".join(recipientsList)

    if notifyTo:
        msg['BX-Non-Delivery-Notification-Req-To'] = notifyTo

    return


####+BEGIN: b:py3:cs:func/typing :funcName "nonDeliveryNotificationRequetsPerRecipient" :funcType "extTyped" :deco "track" :comment "Place Holder"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /nonDeliveryNotificationRequetsPerRecipient/  Place Holder deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def nonDeliveryNotificationRequetsPerRecipient(
####+END:
        msg,
        perRecipientsList=None,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Place Holder
    #+end_org """
    return

####+BEGIN: b:py3:cs:func/typing :funcName "nonDeliveryNotificationActions" :funcType "extTyped" :deco "track" :comment ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /nonDeliveryNotificationActions/  Place Holder deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def nonDeliveryNotificationActions(
####+END:
        msg,
        coRecipientsList=None,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Based on action and address, process the Non-Delivery-Notification and notify each of coRecipientsList.
    #+end_org """

    if coRecipientsList:
        msg['X-B-Non-Delivery-Notification-Actions'] = ", ".join(coRecipientsList)

    return

####+BEGIN: b:py3:cs:func/typing :funcName "crossRefInfo" :funcType "extTyped" :deco "track" :comment ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /crossRefInfo/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def crossRefInfo(
####+END:
        msg,
        crossRefInfo,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Set the crossRefInfo. E.g., X-B-CrossRef: someDataBaseId.
    #+end_org """
    if crossRefInfo:
        msg['X-B-CrossRef'] = crossRefInfo

    return

####+BEGIN: b:py3:cs:func/typing :funcName "dispositionNotificationHeaders" :funcType "extTyped" :deco "track" :comment ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /dispositionNotificationHeaders/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def dispositionNotificationHeaders(
####+END:
        msg,
        notifyTo,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Disposition-Notification-To is from RFC-8098 -- Return-Receipt-To is non standard but used.
    #+end_org """
    msg['Disposition-Notification-To'] = notifyTo
    msg['Return-Receipt-To'] = notifyTo


####+BEGIN: b:py3:cs:func/typing :funcName "deliveryNotificationHeaders" :funcType "extTyped" :deco "track" :comment ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /deliveryNotificationHeaders/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def deliveryNotificationHeaders(
####+END:
        msg,
        recipientsList,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Notice-Requested-Upon-Delivery-To (NRUDT) as specified in: https://tools.ietf.org/html/draft-bernstein-nrudt-02
NRUDT is supported by the qreceipt program in the qmail package.

This header line can be shared and does not need to have
its own uniq msg.
    #+end_org """
    if recipientsList:
        if 'Notice-Requested-Upon-Delivery-To' in msg:
            b_io.tm.here("Notice-Requested-Upon-Delivery-To -- existed. It has not been updated.")
        else:
            msg['Notice-Requested-Upon-Delivery-To'] = ", ".join(recipientsList)
    return

####+BEGIN: b:py3:cs:orgItem/basic :type "=SendMethod= " :title "*Mail Sending Method Selection -- Injection or Submit*" :comment "General"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  =SendMethod=  [[elisp:(outline-show-subtree+toggle)][||]] *Mail Sending Method Selection -- Injection or Submit* General  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:


####+BEGIN: bx:dblock:python:enum :enumName "SendingMethod" :comment "inject or submit"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Enum       [[elisp:(outline-show-subtree+toggle)][||]] /SendingMethod/ =inject or submit=  [[elisp:(org-cycle)][| ]]
#+end_org """
@enum.unique
class SendingMethod(enum.Enum):
####+END:
    inject='inject',
    submit='submit',

####+BEGIN: bx:dblock:python:enum :enumName "SendingRunControl" :comment "Enum Values: fullRun, dryRun, runDebug"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Enum       [[elisp:(outline-show-subtree+toggle)][||]] /SendingRunControl/ =Enum Values: fullRun, dryRun, runDebug=  [[elisp:(org-cycle)][| ]]
#+end_org """
@enum.unique
class SendingRunControl(enum.Enum):
####+END:
    fullRun='fullRun',
    dryRun='dryRun',
    runDebug='runDebug',


####+BEGIN: b:py3:cs:func/typing :funcName "sendingMethodSet" :funcType "extTyped" :deco "track" :comment "sendingMethodSet -- Header Tagging as (inject, submit, etc)"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /sendingMethodSet/  sendingMethodSet -- Header Tagging as (inject, submit, etc) deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def sendingMethodSet(
####+END:
        msg,
        sendingMethodStr,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Set BX-Sending-Method in X822-MSP.
    #+end_org """
    opRes = b.op.Outcome()
    if enumFromStrWhenValid('SendingMethod', sendingMethodStr) == None:
        return icm.eh_problem_usageError_wOp(opRes, sendingMethodStr)
    if not 'BX-Sending-Method' in msg:
        msg['BX-Sending-Method'] = sendingMethodStr

    return opRes


""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /sendingMethodSet/  sendingMethodSet -- Header Tagging as (inject, submit, etc) deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def sendingMethodSet(
####+END:
        msg,
        sendingRunControl,
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Set the msg's envelope address to mailBoxAddr. This will be used for delivery-reports and non-delivery-reports.
    #+end_org """
    opRes = b.op.Outcome()
    if enumFromStrWhenValid('SendingRunControl', sendingRunControl) == None:
        return (
            b_io.eh.problem_usageError_wOp(opRes, sendingRunControl)
        )
    msg['BX-Sending-Run-Control'] = sendingRunControl
    return opRes


####+BEGIN: b:py3:cs:orgItem/basic :type "=injection= " :title "*Msg Injection (Request Parameters)*" :comment "General"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  =injection=  [[elisp:(outline-show-subtree+toggle)][||]] *Msg Injection (Request Parameters)* General  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

def enumFromStrWhenValid(
        enumTypeStr,
        enumValueStr,
):
    """Given a string, return the Enum's value if valid. Applies to current module because of exec.

Usage: Should be checked against None.  if .enumFromStrWhenValid() == None: badInput()
"""
    enumRes = None
    try:
        #print "{0}.{1}".format(enumTypeStr, enumValueStr)
        exec("enumRes = {0}.{1}".format(enumTypeStr, enumValueStr))
    except AttributeError:
        #print enumValueStr
        return None
    else:
        #print  enumRes
        return enumRes


####+BEGIN: bx:dblock:python:enum :enumName "InjectionProgram" :comment "Enum values of qmail, qmailBisos, sendmail"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Enum       [[elisp:(outline-show-subtree+toggle)][||]] /InjectionProgram/ =Enum values of qmail, qmailBisos, sendmail=  [[elisp:(org-cycle)][| ]]
#+end_org """
@enum.unique
class InjectionProgram(enum.Enum):
####+END:
    qmail='qmail',
    qmailBisos='qmailBisos',
    qmailRemoteBisos='qmailRemoteBisos',
    qmailRemote='qmailRemote',
    sendmail='sendmail',

####+BEGIN: b:py3:cs:func/typing :funcName "injectionProgramSet" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /injectionProgramSet/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def injectionProgramSet(
####+END:
        msg,
        injectionProgram,
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Set the msg's envelope address to mailBoxAddr. This will be used for delivery-reports and non-delivery-reports.
    #+end_org """
    opOutcome = b.op.Outcome()
    if enumFromStrWhenValid('InjectionProgram', injectionProgram) == None:
        return (
            b_io.eh.problem_usageError(injectionProgram)
        )
    msg['BX-Injection-Program'] = injectionProgram
    return opOutcome

####+BEGIN: b:py3:cs:func/typing :funcName "injectionParams" :funcType "extTyped" :deco "track" :comment "Header Tag All Injection Params"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /injectionParams/  Header Tag All Injection Params deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def injectionParams(
####+END:
        msg,
        sendingRunControl=SendingRunControl.fullRun,
        injectionProgram=InjectionProgram.qmail
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Set necessary  injectionParams, to be used by sendBasedOnHeadersInfo.
    #+end_org """

    if sendingMethodSet(msg, SendingMethod.inject).isProblematic():
        return icm.eh_badLastOutcome()

    if sendingRunControlSet(msg, sendingRunControl).isProblematic():
        return icm.eh_badLastOutcome()

    if injectionProgramSet(msg, injectionProgram).isProblematic():
        return icm.eh_badLastOutcome()

    return icm.opSuccess()

####+BEGIN: b:py3:cs:orgItem/basic :type "=Submission= " :title "*Msg Submission (Request Parameters)*" :comment "General"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  =Submission=  [[elisp:(outline-show-subtree+toggle)][||]] *Msg Submission (Request Parameters)* General  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:


####+BEGIN: bx:dblock:python:enum :enumName "MtaRemProtocol" :comment "Enum values of: smtp, smtp_ssl, smtp_tls"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Enum       [[elisp:(outline-show-subtree+toggle)][||]] /MtaRemProtocol/ =Enum values of: smtp, smtp_ssl, smtp_tls=  [[elisp:(org-cycle)][| ]]
#+end_org """
@enum.unique
class MtaRemProtocol(enum.Enum):
####+END:
    smtp='smtp',
    smtp_ssl='smtp_ssl',
    smtp_tls='smtp_tls',

####+BEGIN: b:py3:cs:func/typing :funcName "mtaRemProtocolSet" :funcType "extTyped" :deco "track" :comment "Header Tagging mtaRemProtocol"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /mtaRemProtocolSet/  Header Tagging mtaRemProtocol deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def mtaRemProtocolSet(
####+END:
        msg,
        mtaRemProtocolStr,
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Header Tagging mtaRemProtocol
    #+end_org """

    opRes = b.op.Outcome()
    if enumFromStrWhenValid('MtaRemProtocol', mtaRemProtocolStr) == None:
        return (
            icm.eh_problem_usageError_wOp(opRes, mtaRemProtocolStr)
        )
    msg['BX-MTA-Rem-Protocol'] = mtaRemProtocolStr
    return opRes

####+BEGIN: b:py3:cs:func/typing :funcName "submitParams" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /submitParams/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def submitParams(
####+END:
        msg,
        sendingRunControl=SendingRunControl.fullRun,
        mtaRemProtocol=None,          # smtp
        mtaRemHost=None,              # Remote Host To Submit to (could be localhost)
        mtaRemPort=None,
        mtaRemUser=None,
        mtaRemPasswd=None,
        mtaRemCerts=None,
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Set necessary  injectionParams, to be used by sendBasedOnHeadersInfo. Header Tag All Submit Params.
    #+end_org """

    if sendingMethodSet(msg, SendingMethod.submit).isProblematic():
        return icm.eh_badLastOutcome()

    if sendingRunControlSet(msg, sendingRunControl).isProblematic():
        return icm.eh_badLastOutcome()

    if mtaRemProtocolSet(msg, mtaRemProtocol).isProblematic():
        return icm.eh_badLastOutcome()

    if not 'BX-MTA-Rem-Host' in msg:
        if mtaRemHost:
            msg['BX-MTA-Rem-Host'] = mtaRemHost

    if not 'BX-MTA-Rem-PortNu' in msg:
        if mtaRemPort:
            msg['BX-MTA-Rem-PortNu'] = mtaRemPort

    if not 'BX-MTA-Rem-User' in msg:
        if mtaRemUser:
            msg['BX-MTA-Rem-User'] = mtaRemUser

    if not 'BX-MTA-Rem-Passwd' in msg:
        if mtaRemPasswd:
            msg['BX-MTA-Rem-Passwd'] = mtaRemPasswd

    if mtaRemCerts:
        msg['BX-MTA-Rem-Certificates'] = mtaRemCerts

    return

####+BEGIN: b:py3:cs:orgItem/basic :type "=Facilities= " :title "*Send Based On Headers*" :comment "General"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  =Facilities=  [[elisp:(outline-show-subtree+toggle)][||]] *Send Based On Headers* General  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:func/typing :funcName "sendBasedOnHeadersInfo" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /sendBasedOnHeadersInfo/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def sendBasedOnHeadersInfo(
####+END:
        msg,
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Submit or Inject msg using information contained in the header.
** Overview

Dispatch to recipients based on tailored Msg and tailored submission info.
Processes headers and creates two classes,
    - MsgForRecipient
    - OptionsForRecipient
Given a msg and recipients from MsgForRecipient
    - find common options for common recipients
    - Submit based on msg and options
    #+end_org """

    bx822Set_setMandatoryFields(msg,)

    if 'BX-Sending-Method' in msg:
        sendingMethod = msg['BX-Sending-Method']
    else:
        return b_io.eh.problem_info("BX-Sending-Method")

    if sendingMethod == SendingMethod.inject:
        opOutcome = injectBasedOnHeadersInfo(msg,)

    elif sendingMethod == SendingMethod.submit:
        opOutcome = submitBasedOnHeadersInfo(msg,)

    else:
        return (io.eh.problem_info("Bad Usage"))

    return opOutcome

####+BEGIN: b:py3:cs:func/typing :funcName "mailHeadersPipelineClean" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /mailHeadersPipelineClean/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def mailHeadersPipelineClean(
####+END:
        msg,
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Given a msg, at the end of mailHeadersPipeline cleanup (strip BX-)the headers.

    We want to make sure that msg's header does not contains any extra
    headers that are publicly visible and that are not needed.

    The X-B- header lines are public and should not be stripped.

    #+end_org """

    toBeStrippedHeaders = [
        'BX-Non-Delivery-Notification-Req-To',
        'BX-Disposition-Notification-Req-For',
        'BX-Disposition-Notification-Req-To',
        'BX-Delivery-Notification-Req-For',
        'BX-Delivery-Notification-Req-To',
        'BX-MTA-Injection-Method',
        'BX-MTA-Injection-Control',
        'X-bpoId',
        'X-bpoRunEnv',
        'X-Oauth2-Client-Id',
        'X-Oauth2-Client-Secret',
        'X-Oauth2-Refresh-Token',
    ]

    for each in toBeStrippedHeaders:
        if each in msg:
            del msg[each]


####+BEGIN: b:py3:cs:orgItem/basic :type "=inject=" :title "*Inject Based On Headers*" :comment ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  =inject=   [[elisp:(outline-show-subtree+toggle)][||]] *Inject Based On Headers*   [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:func/typing :funcName "injectBasedOnHeadersInfo" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /injectBasedOnHeadersInfo/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def injectBasedOnHeadersInfo(
####+END:
        msg: str,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Dispatch based on BX-Injection-Program -- sendmail or qmail().
    #+end_org """

    if 'BX-Injection-Program' in msg:
        injectionProgram = msg['BX-Injection-Program']
    else:
        injectionProgram = InjectionProgram.qmail
        #return b_io.eh.problem_info("BX-Injection-Program")

    if injectionProgram == InjectionProgram.qmail:
        opOutcome = injectMsgWithQmail(msg,)

    elif injectionProgram == InjectionProgram.qmail:
        opOutcome = injectMsgWithSendmail(msg,)

    else:
        return (
            b_io.eh.problem_info("Bad Usage")
        )

    return opOutcome

####+BEGIN: b:py3:cs:func/typing :funcName "injectMsgWithQmailVariant" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /injectMsgWithQmailVariant/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def injectMsgWithQmailVariant(
####+END:
        msg,
        injectionProgram: str=InjectionProgram.qmailBisos.value[0],
        qmailRemoteArgs: list[str]=[],
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Should be converted to be an operation
    #+end_org """

    #b_io.tm.here("qmail Inject \n{msgStr}".format(msgStr=msg.as_string()))
    outcome = b.op.Outcome()

    #print(msg)

    injectionProgramArgs = []

    # print(InjectionProgram.qmail.value[0])
    # print(injectionProgram)

    #print(InjectionProgram.qmailBisos.value[0])
    if injectionProgram == InjectionProgram.qmailBisos.value[0]:
        injectionProgramCmnd =  "qmail-inject-bisos.cs"
        if cs.runArgs.isRunModeDryRun():
            injectionProgramArgs.append('-n')
    elif injectionProgram == InjectionProgram.qmail.value[0]:
        injectionProgramCmnd =  "/var/qmail/bin/qmail-inject"
        if cs.runArgs.isRunModeDryRun():
            injectionProgramArgs.append('-n')
    elif injectionProgram == InjectionProgram.qmailRemoteBisos.value[0]:
        injectionProgramCmnd =  "qmail-remote-bisos.cs"
        injectionProgramArgs =  qmailRemoteArgs
    elif injectionProgram == InjectionProgram.qmailRemote.value[0]:
        injectionProgramCmnd =  "qmail-remote"
        injectionProgramArgs =  qmailRemoteArgs
    else:
        print(f"NOTYET {injectionProgram}")
        return(b_io.eh.badOutcome(outcome))

    commandLine = injectionProgramCmnd + " " +  " ".join(injectionProgramArgs)

    print(commandLine)

    if b.subProc.Op(outcome=outcome, log=1).bash(
        f"""{commandLine}""",
        stdin=msg.as_string(),
    ).isProblematic():
        print(outcome.stderr)
        return(b_io.eh.badOutcome(outcome))

    #if outcome.stdout: icm.ANN_note("Stdout: " +  outcome.stdout)
    #if outcome.stderr: icm.ANN_note("Stderr: " +  outcome.stderr)


    return outcome.set(
        opError=b.OpError.Success,
        opResults=None,
    )

####+BEGIN: b:py3:cs:orgItem/basic :type "=inject=" :title "*Submit Based On Headers*" :comment ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  =inject=   [[elisp:(outline-show-subtree+toggle)][||]] *Submit Based On Headers*   [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:


####+BEGIN: b:py3:cs:func/typing :funcName "submitBasedOnHeadersInfo" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /submitBasedOnHeadersInfo/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def submitBasedOnHeadersInfo(
####+END:
        msg: str,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] ** Submit or Inject msg using information contained in the header.

** Overview

Dispatch to recipients based on tailored Msg and tailored submission info.
Processes headers and creates two classes,
    - MsgForRecipient
    - OptionsForRecipient
Given a msg and recipients from MsgForRecipient
    - find common options for common recipients
    - Submit based on msg and options
    #+end_org """

    if 'X-B-Envelope-Addr' in msg:
        envelopeAddr = msg['X-B-Envelope-Addr']
    else:
        envelopeAddr = msg['From']

    allRecipients = msgLib.msgAllRecipients(
        msg,
    )
    allRecipientsSet = set()
    for thisRecipient in allRecipients:
        allRecipientsSet.add(thisRecipient[1])

    msgForRecipient = MsgForRecipient()

    notificationAddrsSet = set()

    if 'BX-Disposition-Notification-Req-For' in msg:
        addrs =  email.utils.getaddresses(
            msg.get_all('BX-Disposition-Notification-Req-For', [])
        )
        for each in addrs:
            if each[1] in allRecipientsSet:
                notificationAddrsSet.add(each[1])
            else:
                b_io.eh.problem_info("{each} is not a msg's recipient".format(each=each[1]))

        if 'BX-Disposition-Notification-Req-To' in msg:
            addrs =  msg.get_all('BX-Disposition-Notification-Req-To', [])
            notifyTo =  addrs[0]
            #del msg['BX-Disposition-Notification-Req-To']
        else:
            notifyTo = envelopeAddr

        for eachRecipientAddr in notificationAddrsSet:
            msgWithNotifyTo = getMsgWithDispositionNotifyTo(
                msgForRecipient,
                notifyTo,
            )
            if msgWithNotifyTo:
                msgForRecipient.addMsgForRcipient(
                    msgWithNotifyTo,
                    eachRecipientAddr,
                )
            else:
                # It must be a deepcopy -- not just copy
                msgCopy = copy.deepcopy(msg)
                dispositionNotificationHeaders(
                    msgCopy,
                    notifyTo,
                )
                msgForRecipient.addMsgForRcipient(
                    msgCopy,
                    eachRecipientAddr,
                )

    #
    # All other recipients are associated with the common msg.
    #
    defaultMsgRecipients = allRecipientsSet - notificationAddrsSet
    for eachRecipientAddr in defaultMsgRecipients:
        msgForRecipient.addMsgForRcipient(
            msg,
            eachRecipientAddr,
        )

    recipientsWithDeliveryNotificationReqSet = set()

    if 'BX-Delivery-Notification-Req-For' in msg:
        addrs =  email.utils.getaddresses(
            msg.get_all('BX-Delivery-Notification-Req-For', [])
        )
        for each in addrs:
            if each[1] in allRecipientsSet:
                recipientsWithDeliveryNotificationReqSet.add(each[1])
            else:
                b_io.eh.problem_info("{each} is not a msg's recipient".format(each=each[1]))

        for eachRecipient in recipientsWithDeliveryNotificationReqSet:
            msgOfRecipient = msgForRecipient.getMessageForRecipient(
                eachRecipient,
            )
            if msgOfRecipient:
                #
                # This header line can be shared and does not need to have
                # its own uniq msg.
                #
                deliveryNotificationHeaders(
                    msgOfRecipient,
                    recipientsWithDeliveryNotificationReqSet,
                )

            else:
                b_io.eh.problem_info("OOPS")
    #
    # With each copy of the message, we determine which
    # recipients are using that copy. We then determine
    # of those recipients which want delivery-reports and which
    # don't. We then do one submission with delivery-reqs and one without.
    #
    for eachMsg in msgForRecipient.getAllMsgs():
        msgRecipientsList = msgForRecipient.getAllRecipientsForMsg(eachMsg)

        msgRecipientsWithDeliveryNotification = set.intersection(
            set(msgRecipientsList),
            recipientsWithDeliveryNotificationReqSet,
        )

        if msgRecipientsWithDeliveryNotification:
            submitMsgToRecipients(
                eachMsg,
                msgRecipientsWithDeliveryNotification,
                deliveryNotificationRequest=True,
            )

        msgRecipientsWithoutDeliveryNotification = set(msgRecipientsList) - msgRecipientsWithDeliveryNotification

        if msgRecipientsWithoutDeliveryNotification:
            submitMsgToRecipients(
                eachMsg,
                msgRecipientsWithoutDeliveryNotification,
                deliveryNotificationRequest=False,
            )

####+BEGIN: b:py3:cs:func/typing :funcName "strLogMessage" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /strLogMessage/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def strLogMessage(
####+END:
        headerStr: str,
        msg: str,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Return a string to be used with log_here()
    #+end_org """
    return (
        "{headerStr}\n{msgStr}".format(
            headerStr=headerStr,
            msgStr=msg.as_string(),
        )
    )

####+BEGIN: b:py3:cs:func/typing :funcName "runningWithDebugOn" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /runningWithDebugOn/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def runningWithDebugOn(
####+END:
        msg: str,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]  Return True if runMode==dryRun or runMode=runDebug
    #+end_org """
    if 'BX-Sending-Run-Control' in msg:
        sendingRunControl = msg['BX-Sending-Run-Control']
    else:
        # We are not going to check G.usageParams.runMode
        # because this library is not tied to ICMs
        return False

    if enumFromStrWhenValid('SendingRunControl', sendingRunControl) == None:
        # Unknown is considered DryRun -- to be safe
        return True
    else:
        sendingRunControl = enumFromStrWhenValid('SendingRunControl', sendingRunControl)

    if sendingRunControl == SendingRunControl.dryRun:
        return True
    elif sendingRunControl == SendingRunControl.runDebug:
        return True
    elif sendingRunControl == SendingRunControl.fullRun:
        return False
    else:
        b_io.eh.critical_oops("Impossible")
        return True

####+BEGIN: b:py3:cs:func/typing :funcName "runningWithDryrun" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /runningWithDryrun/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def runningWithDryrun(
####+END:
        msg: str,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]  Return True if runMode==dryRun
    #+end_org """
    if 'BX-Sending-Run-Control' in msg:
        sendingRunControl = msg['BX-Sending-Run-Control']
    else:
        # We are not going to check G.usageParams.runMode
        # because this library is not tied to ICMs
        return False


    if enumFromStrWhenValid('SendingRunControl', sendingRunControl) == None:
        # Unknown is considered DryRun -- to be safe
        return True
    else:
        sendingRunControl = enumFromStrWhenValid('SendingRunControl', sendingRunControl)

    if sendingRunControl == SendingRunControl.dryRun:
        return True
    elif sendingRunControl == SendingRunControl.runDebug:
        return False
    elif sendingRunControl == SendingRunControl.fullRun:
        return False
    else:
        b_io.eh.critical_oops("Impossible")
        return True

####+BEGIN: b:py3:cs:func/typing :funcName "submitMsgToRecipients" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /submitMsgToRecipients/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def submitMsgToRecipients(
####+END:
        msg: str,
        recipients,
        deliveryNotificationRequest=False,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]  Given a msg with needed BX-MTA-Rem headers submit msg to recipients and perhaps request delivery notifications.
    #+end_org """

    b_io.tm.here(strLogMessage(
        "Msg Before Any Header Cleanups", msg,))

    opRes = b.op.Outcome()

    # if 'BX-MTA-Injection-Control' in msg:
    #     injectionControl = msg['BX-MTA-Injection-Control']
    #     if not isValidInjectionControl(injectionControl):
    #         b_io.eh.problem_info(injectionControl)
    #         return
    # else:
    #     b_io.eh.problem_info("BX-MTA-Injection-Control")

    if 'X-B-Envelope-Addr' in msg:
        envelopeAddr = msg['X-B-Envelope-Addr']
        #del msg['X-B-Envelope-Addr']
    else:
        envelopeAddr = msg['From']

    if 'BX-MTA-Rem-Protocol' in msg:
        mtaRemProtocol = msg['BX-MTA-Rem-Protocol']
        #del msg['BX-MTA-Rem-Protocol']
        if enumFromStrWhenValid('MtaRemProtocol', mtaRemProtocol) == None:
            return (
                icm.eh_problem_usageError_wOp(opRes, mtaRemProtocol)
            )
        else:
            mtaRemProtocol =  enumFromStrWhenValid('MtaRemProtocol', mtaRemProtocol)
    else:
        return b_io.eh.problem_info("BX-MTA-Rem-Protocol")

    mtaRemHost = "localhost"
    if 'BX-MTA-Rem-Host' in msg:
        mtaRemHost = msg['BX-MTA-Rem-Host']
        del msg['BX-MTA-Rem-Host']

    mtaRemPort = None
    if 'BX-MTA-Rem-PortNu' in msg:
        mtaRemPort = msg['BX-MTA-Rem-PortNu']
        del msg['BX-MTA-Rem-PortNu']

    mtaRemUser = None
    if 'BX-MTA-Rem-User' in msg:
        mtaRemUser = msg['BX-MTA-Rem-User']
        del msg['BX-MTA-Rem-User']

    mtaRemPasswd = None
    if 'BX-MTA-Rem-Passwd' in msg:
        mtaRemPasswd = msg['BX-MTA-Rem-Passwd']
        del msg['BX-MTA-Rem-Passwd']

    #mtaRemLinkConfidentiality = None
    #if 'BX-MTA-Rem-LinkConfidentiality' in msg:
    #    mtaRemLinkConfidentiality = msg['BX-MTA-Rem-LinkConfidentiality']
    #    del msg['BX-MTA-Rem-LinkConfidentiality']

    mtaRemCertFile = None
    if 'BX-MTA-Rem-CertFile' in msg:
        mtaRemCertFile = msg['BX-MTA-Rem-CertFile']
        del msg['BX-MTA-Rem-CertFile']

    mtaRemKeyFile = None
    if 'BX-MTA-Rem-KeyFile' in msg:
        mtaRemKeyFile = msg['BX-MTA-Rem-KeyFile']
        del msg['BX-MTA-Rem-KeyFile']

    #
    mailHeadersPipelineClean(msg)

    if runningWithDebugOn(msg):
        b_io.tm.here("================")
        b_io.tm.here("envelopeAddr= {envelopeAddr}".format(envelopeAddr=envelopeAddr))
        b_io.tm.here("recipients= {recipients}".format(recipients=recipients))
        b_io.tm.here("deliveryNotificationRequest= {deliveryNotificationRequest}".format(deliveryNotificationRequest=deliveryNotificationRequest))
        b_io.tm.here("---------------")

        b_io.tm.here(strLogMessage(
            "Final Msg As Being Submitted/Injected/Dryruned", msg,))

        if runningWithDryrun(msg):
            b_io.ann.here("DryRun of submitMsgToRecipients -- -v 20 for details")
            b_io.tm.here("DryRun of submitMsgToRecipients")
            return

    b_io.tm.here("")

    def smtpExceptionInfo(e):
        print('got', e.__class__)
        outString = format(e)
        print(outString)
        #errcode = getattr(e, 'smtp_code', -1)
        #errmsg = getattr(e, 'smtp_error', 'ignore')
        return

    try:

        if mtaRemProtocol == MtaRemProtocol.smtp:
            if not mtaRemPort:
                mtaRemPort = 25
            b_io.tm.here("Protocol=smtp -- remHost={remHost} -- portNu={portNu}".format(
                remHost=mtaRemHost, portNu=mtaRemPort,))

            smtpConn = smtplib.SMTP(
                mtaRemHost,
                port=mtaRemPort,
            )
        elif mtaRemProtocol == MtaRemProtocol.smtp_ssl:
            if not mtaRemPort:
                mtaRemPort = 465
            b_io.tm.here("Protocol=smtp_ssl -- remHost={remHost} -- portNu={portNu}".format(
                remHost=mtaRemHost, portNu=mtaRemPort,))

            smtpConn = smtplib.SMTP_SSL(
                mtaRemHost,
                port=mtaRemPort,
            )
        elif mtaRemProtocol == MtaRemProtocol.smtp_tls:
            if not mtaRemPort:
                mtaRemPort = 587
            b_io.tm.here("Protocol=smtp_tls -- remHost={remHost} -- portNu={portNu}".format(
                remHost=mtaRemHost, portNu=mtaRemPort,))
            b_io.tm.here("Not Fully Implemented/Tested. Will use certFile={} keyFile={}".format(
                mtaRemCertFile,  mtaRemKeyFile,))

            smtpConn = smtplib.SMTP_SSL(
                mtaRemHost,
                port=mtaRemPort,
            )

            #smtpConn.starttls()
        else:
            b_io.eh.critical_oops("Coding Error")
            return

    except smtplib.SMTPConnectError as e:
        smtpExceptionInfo(e)
        return None

    b_io.tm.here("")

    #
    #
    #
    if runningWithDebugOn(msg):
        smtpConn.set_debuglevel(True)


    if mtaRemUser and mtaRemPasswd:
        try:
            smtpConn.login(
                mtaRemUser,
                mtaRemPasswd,
            )
        except smtplib.SMTPHeloError as e:   # The server didn't reply properly to the helo greeting.
            smtpExceptionInfo(e)
            return None

        except smtplib.SMTPAuthenticationError as e: # The server didn't accept the username/password combination.
            smtpExceptionInfo(e)
            return None

        except smtplib.SMTPNotSupportedError as e:  # The AUTH command is not supported by the server.
            smtpExceptionInfo(e)
            return None

        except smtplib. SMTPException as e:  # No suitable authentication method was found.
            smtpExceptionInfo(e)
            return None

    else:
        b_io.eh.problem_usageError(
            "Missing --User={user} Passwd={passwd}".format(
                user=mtaRemUser, passwd=mtaRemPasswd,))

    b_io.tm.here("")

    #
    # If needed, we logged in. Ready to sendmail()
    #

    try:
        if deliveryNotificationRequest == True:
            failedRecipients = smtpConn.sendmail(
                envelopeAddr,
                recipients,
                msg.as_string(),
                mail_options=[],
                rcpt_options=[
                    "NOTIFY=FAILURE,SUCCESS,DELAY",
                ]
            )
        else:
            failedRecipients = smtpConn.sendmail(
                envelopeAddr,
                recipients,
                msg.as_string(),
            )

    except smtplib.SMTPHeloError as e:   # The server didn't reply properly to the helo greeting.
        smtpExceptionInfo(e)
        return None

    except smtplib.SMTPRecipientsRefused as e: # The server rejected ALL recipients (no mail was sent).
        smtpExceptionInfo(e)
        errcode = getattr(e, 'smtp_code', -1)
        errmsg = getattr(e, 'smtp_error', 'ignore')
        refused = []
        for r in recipients:
            refused[r] = (errcode, errmsg)
        return refused

    except smtplib.SMTPSenderRefused as e:  # The server didn't accept the from_addr.
        smtpExceptionInfo(e)
        return None

    except smtplib.SMTPNotSupportedError as e:  # The mail_options parameter includes 'SMTPUTF8' but the SMTPUTF8 extension is not supported by the server.
        smtpExceptionInfo(e)
        return None

    except smtplib.SMTPDataError as e:  # The server replied with an unexpected error code (other than a refusal of a recipient).
        smtpExceptionInfo(e)
        return None

    else:
        return failedRecipients

    finally:
        try:
            smtpConn.quit()
        except smtplib.SMTPServerDisconnected as e:   # Connection unexpectedly closed
            smtpExceptionInfo(e)
            return None

####+BEGIN: b:py3:cs:orgItem/basic :type "=inject=" :title "*Per Recipient Replicated Msg Customization And Management*" :comment ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  =inject=   [[elisp:(outline-show-subtree+toggle)][||]] *Per Recipient Replicated Msg Customization And Management*   [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:


####+BEGIN: b:py3:class/decl :className "MsgForRecipient" :superClass "object" :comment "ByStar Portable Object -- to be subclassed" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /MsgForRecipient/  superClass=object =ByStar Portable Object -- to be subclassed=  [[elisp:(org-cycle)][| ]]
#+end_org """
class MsgForRecipient(object):
####+END:
     """
**  Singleton Class: maintain cross-refs for Msgs customized for Recipients.

     Every recipient is associated with a Msg.
     msgRecipientsDict[msg] maps to a set of recipients.
"""
     msgRecipientsDict = dict()         #  msg, recipientAddrList

     def __init__(self):
         pass

     def addMsgForRcipient(self,
                           msg,
                           recipient,
     ):
         if msg in self.__class__.msgRecipientsDict:
             if recipient in self.__class__.msgRecipientsDict[msg]:
                 pass
             else:
                 self.__class__.msgRecipientsDict[msg].add(recipient)
         else:
             self.__class__.msgRecipientsDict[msg]=set([recipient])


     def getAllRecipientsForMsg(self,
                                msg,
     ):
         if msg in self.__class__.msgRecipientsDict:
             return self.__class__.msgRecipientsDict[msg]
         else:
             b_io.eh.problem_info()
             return None

     def getAllMsgs(self,
     ):
         return list(self.__class__.msgRecipientsDict.keys())

     def getMessageForRecipient(self,
                                recipient,
     ):
         #b_io.tm.here(self.__class__.msgRecipientsDict)
         for eachMsg in self.__class__.msgRecipientsDict:
             recipientsList = self.__class__.msgRecipientsDict[eachMsg]
             if recipient in recipientsList:
                 return eachMsg
         return None

####+BEGIN: b:py3:cs:func/typing :funcName "getMsgWithDispositionNotifyTo" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /getMsgWithDispositionNotifyTo/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def getMsgWithDispositionNotifyTo(
####+END:
        msgForRecipient,
        notifyTo,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Return msg or None. Find msg for msgForRecipient whose Disposition-Notification-To is notifyTo.
    #+end_org """

    for msg in msgForRecipient.getAllMsgs():
        if 'Disposition-Notification-To' in msg:
            dispositionNotifyTo = msg['Disposition-Notification-To']
            if dispositionNotifyTo == notifyTo:
                return msg
    return None

####+BEGIN: b:py3:cs:orgItem/basic :type "=bx822=" :title "*Mandatory Bx822 Fields Set*" :comment ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  =inject=   [[elisp:(outline-show-subtree+toggle)][||]] *Mandatory Bx822 Fields Set*   [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:func/typing :funcName "bx822Set_setMandatoryFields" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /bx822Set_setMandatoryFields/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def bx822Set_setMandatoryFields(
####+END:
        msg,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Mail Sending Agent's Final Setups: Date, Message-ID, User-Agent, if needed
    #+end_org """

    if not 'Date' in msg:
        msg['Date'] = email.utils.formatdate(localtime = 1)

    if not 'Message-ID' in msg:
        msg['Message-ID'] = email.utils.make_msgid()

    return None


####+BEGIN: b:py3:cs:framework/endOfFile :basedOn "classification"
""" #+begin_org
* [[elisp:(org-cycle)][| *End-Of-Editable-Text* |]] :: emacs and org variables and control parameters
#+end_org """

#+STARTUP: showall

### local variables:
### no-byte-compile: t
### end:
####+END:
