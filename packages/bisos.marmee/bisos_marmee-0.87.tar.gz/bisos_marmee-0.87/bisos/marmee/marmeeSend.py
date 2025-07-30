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

from bisos.common import csParam
from bisos.marmee import x822Out

import sys
import email

#from datetime import datetime

#import re
#import pprint

import email
#import mailbox
#import smtplib

#import flufl.bounce

from unisos.x822Msg import msgOut
from unisos.x822Msg import msgIn

from email.mime.text import MIMEText
#from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders



####+BEGIN: bx:cs:py3:section :title "Common Parameters Specification"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Common Parameters Specification*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: bx:dblock:python:func :funcName "commonParamsSpecify" :funcType "ParSpec" :retType "" :deco "" :argsList "csParams"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-ParSpec  [[elisp:(outline-show-subtree+toggle)][||]] /commonParamsSpecify/ retType= argsList=(csParams)  [[elisp:(org-cycle)][| ]]
#+end_org """
def commonParamsSpecify(
    csParams,
):
####+END:
    csParams.parDictAdd(
        parName='fromLine',
        parDescription="From Line",
        parDataType=None,
        parDefault="someFrom@example.com",
        parChoices=["from@example.com", "UserInput"],
        parScope=cs.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--fromLine',
        )

    csParams.parDictAdd(
        parName='toLine',
        parDescription="To Line",
        parDataType=None,
        parDefault="someTo@example.com",
        parChoices=["to@example.com", "UserInput"],
        parScope=cs.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--toLine',
    )


####+BEGIN: bx:cs:py3:section :title "CS-Lib Examples"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *CS-Lib Examples*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:


####+BEGIN: b:py3:cs:func/typing :funcName "examples_csu" :funcType "eType" :retType "" :deco "default" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-eType  [[elisp:(outline-show-subtree+toggle)][||]] /examples_csu/  deco=default  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def examples_csu(
####+END:
        fromLine: str,
        toLine: str,
        sectionTitle: typing.AnyStr = "",
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Examples of Service Access Instance Commands.
    #+end_org """

    def cpsInit(): return collections.OrderedDict()
    def menuItem(verbosity): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity=verbosity) # 'little' or 'none'
    # def execLineEx(cmndStr): cs.examples.execInsert(execLine=cmndStr)


    def cmndParsCurBpoAndEnvRelPath(cps): cps['fromLine'] = fromLine ; cps['toLine'] = toLine

    def cmndParsToLocal(cps): cps['fromLine'] = "postmaster@HSS-1013.intra" ; cps['toLine'] = "postmaster@HSS-1013.intra"

    if sectionTitle == "default":
        cs.examples.menuChapter('*MARMEE SendMail --- Send*')

    #if bpoId == None:
        #return

    cs.examples.menuChapter('*Send Supplied Message*')

    cmndName = "bisosSendSuppliedMsg" ;  cmndArgs = ""
    cps=cpsInit(); cmndParsCurBpoAndEnvRelPath(cps);
    menuItem(verbosity='none') ; menuItem(verbosity='full')

    cs.examples.menuChapter('*Send Probe Message --- Expect Delivery*')

    cmndName = "bisosSendProbeMsg" ;  cmndArgs = ""
    cps=cpsInit(); cmndParsCurBpoAndEnvRelPath(cps);
    menuItem(verbosity='none') ; menuItem(verbosity='full')

    cmndName = "bisosSendProbeMsg" ;  cmndArgs = "inject qmail"
    cps=cpsInit(); cmndParsCurBpoAndEnvRelPath(cps);
    cps['runMode'] = "runDebug"
    menuItem(verbosity='none') ; menuItem(verbosity='full')

    cmndName = "bisosSendProbeMsg" ;  cmndArgs = ""
    cps=cpsInit(); cmndParsCurBpoAndEnvRelPath(cps);
    cps['runMode'] = "dryRun"
    menuItem(verbosity='none') ; menuItem(verbosity='full')

    cmndName = "bisosSendProbeMsg" ;  cmndArgs = "inject qmail"
    cps=cpsInit(); cmndParsToLocal(cps);
    menuItem(verbosity='none') ; menuItem(verbosity='full')


    # marmeeSend.cs --fromLine="postmaster@HSS-1013.intra" --toLine="postmaster@HSS-1013.intra" -i bisosSendProbeMsg inject qmail


####+BEGIN: bx:dblock:python:section :title "Support Functions For MsgProcs"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Support Functions For MsgProcs*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "bisosSendSuppliedMsg" :comment "" :parsMand "fromLine toLine" :parsOpt "inFile" :argsMin 0 :argsMax 0 :pyInv "msg"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<bisosSendSuppliedMsg>>  =verify= parsMand=fromLine toLine parsOpt=inFile ro=cli pyInv=msg   [[elisp:(org-cycle)][| ]]
#+end_org """
class bisosSendSuppliedMsg(cs.Cmnd):
    cmndParamsMandatory = [ 'fromLine', 'toLine', ]
    cmndParamsOptional = [ 'inFile', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             fromLine: typing.Optional[str]=None,  # Cs Mandatory Param
             toLine: typing.Optional[str]=None,  # Cs Mandatory Param
             inFile: typing.Optional[str]=None,  # Cs Optional Param
             msg: typing.Any=None,   # pyInv Argument
    ) -> b.op.Outcome:

        callParamsDict = {'fromLine': fromLine, 'toLine': toLine, 'inFile': inFile, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        fromLine = csParam.mappedValue('fromLine', fromLine)
        toLine = csParam.mappedValue('toLine', toLine)
        inFile = csParam.mappedValue('inFile', inFile)
####+END:
        G = cs.globalContext.get()

        if not msg:
            if inFile:
                msg = msgIn.getMsgFromFile(inFile)
            else:
                # Stdin then
                msg = msgIn.getMsgFromStdin()
        else:
            # non-interactive call with msg
            if not bxoId:
                b_io.eh.problem_usageError("")
                return cmndOutcome

        b_io.tm.here(msgOut.strLogMessage(
            "Msg As Input:", msg,))

        b_io.tm.here(G.icmRunArgsGet().runMode)

        outcome = msgOut.sendingRunControlSet(msg, G.icmRunArgsGet().runMode)
        if outcome.isProblematic(): return(io.eh.badOutcome(outcome))

        bx822Set_setMandatoryFields(msg)

        outcome = bx822Get_sendingFieldsPipelineLoad(
            bxoId,
            sr,
            msg,
        )
        if outcome.isProblematic(): return(io.eh.badOutcome(outcome))

        if outcome.results != "INCOMPLETE":
            b_io.tm.here("Complete Message Being Sent")
            return (
                msgOut.sendBasedOnHeadersInfo(msg)
            )

        b_io.tm.here("Incomplete Message -- using qmail+dryrun")

        msgOut.injectionParams(
            msg,
            injectionProgram=msgOut.InjectionProgram.qmail,
            sendingRunControl=msgOut.SendingRunControl.dryRun,
        )

        return msgOut.sendBasedOnHeadersInfo(msg)

        # return cmndOutcome.set(
        #     opError=b.OpError.Success,
        #     opResults=None,
        # )



####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "bisosSendProbeMsg" :comment "" :parsMand "fromLine toLine" :parsOpt "inFile" :argsMin 1 :argsMax 2 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<bisosSendProbeMsg>>  =verify= parsMand=fromLine toLine parsOpt=inFile argsMin=1 argsMax=2 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class bisosSendProbeMsg(cs.Cmnd):
    cmndParamsMandatory = [ 'fromLine', 'toLine', ]
    cmndParamsOptional = [ 'inFile', ]
    cmndArgsLen = {'Min': 1, 'Max': 2,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             fromLine: typing.Optional[str]=None,  # Cs Mandatory Param
             toLine: typing.Optional[str]=None,  # Cs Mandatory Param
             inFile: typing.Optional[str]=None,  # Cs Optional Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        callParamsDict = {'fromLine': fromLine, 'toLine': toLine, 'inFile': inFile, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        fromLine = csParam.mappedValue('fromLine', fromLine)
        toLine = csParam.mappedValue('toLine', toLine)
        inFile = csParam.mappedValue('inFile', inFile)
####+END:

        # if not sendingMethod:
        #     sendingMethod = msgOut.SendingMethod.submit

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


This message is then submitted for sending with sendCompleteMessage().cmnd(msg)

Please find example of an attached file\n
            """)

        msg.attach(part)

        part = MIMEBase('application', "octet-stream")
        part.set_payload(open("/etc/resolv.conf", "rb").read())
        encoders.encode_base64(part)

        part.add_header('Content-Disposition', 'attachment; filename="/etc/resolv.conf"')

        msg.attach(part)

        cmndArgsSpecDict = self.cmndArgsSpec()

        sendingMethod = self.cmndArgsGet("0", cmndArgsSpecDict, argsList)
        sendingMethodInfo = self.cmndArgsGet("1", cmndArgsSpecDict, argsList)

        if sendingMethod == x822Out.SendingMethod.inject.value[0]:
            x822Out.injectMsgWithQmailVariant(msg, injectionProgram=sendingMethodInfo)
            # x822Out.injectMsgWithQmailVariant(msg)
        elif sendingMethod == x822Out.SendingMethod.submit:
            print("NOTYET")
        else:
            print(f"NOTYET, bad sending method={sendingMethod}")

        return


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
            argName="sendingMethod",
            argChoices=['inject', 'submit',],
            argDescription="Action to be specified by rest"
        )
        cmndArgsSpecDict.argsDictAdd(
            argPosition="1",
            argName="sendingMethodInfo",
            argChoices=[],
            argDescription="Rest of args for use by action"
        )

        return cmndArgsSpecDict



"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func         ::  bx822Set_sendWithEnabledAcct    [[elisp:(org-cycle)][| ]]
"""
def bx822Set_sendWithEnabledAcct(
        bxoId,
        sr,
        msg,
        sendingMethod,
):
    """
** Setup BX-Send-WithControlProfile and BX-Send-WithAcctName to enabledAcct
"""
    if sendingMethod == msgOut.SendingMethod.inject:
        return True
    elif sendingMethod == msgOut.SendingMethod.submit:
        if not 'BX-Send-WithControlProfile' in msg:
            msg['BX-Send-WithControlProfile'] = marmeAcctsLib.enabledControlProfileObtain(
                bxoId=bxoId,
                sr=sr,
            )
        if not 'BX-Send-WithAcctName' in msg:
            msg['BX-Send-WithAcctName'] = marmeAcctsLib.enabledInMailAcctObtain(
                bxoId=bxoId,
                sr=sr,
            )
        return True
    else:
        return False


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func         ::  bx822Set_setMandatoryFields    [[elisp:(org-cycle)][| ]]
"""
def bx822Set_setMandatoryFields(
    msg,
):
    """
** Mail Sending Agent's Final Setups: Date, Message-ID, User-Agent, if needed
"""
    if not 'Date' in msg:
        msg['Date'] = email.utils.formatdate(localtime = 1)

    if not 'Message-ID' in msg:
        msg['Message-ID'] = email.utils.make_msgid()

    if not 'User-Agent' in msg:
        msg['User-Agent'] = "Marme/VersionNu"

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func         ::  bx822Get_sendingFieldsPipelineLoad    [[elisp:(org-cycle)][| ]]
"""
def bx822Get_sendingFieldsPipelineLoad(
    bxoId,
    sr,
    msg,
):
    """
** Look for BX-Send-WithAcctName or BX-Send-WithBaseDir, and based on those prep the Bx822 fields.
"""
    opOutcome = b.op.Outcome()
    if 'BX-Send-WithAcctName' in msg:
        controlProfile = msg['BX-Send-WithControlProfile']
        outMailAcct = msg['BX-Send-WithAcctName']
        return (
            msgSendingPipelineLoadFromAcct(
                bxoId,
                sr,
                msg,
                controlProfile,
                outMailAcct,
            ))
    elif 'BX-Send-WithBaseDir' in msg:
        acctBaseDir = msg['BX-Send-WithBaseDir']
        return (
            msgSendingPipelineLoadFromAcctBaseDir(
                msg,
                acctBaseDir,
            ))
    else:
        return opOutcome.set(opResults='INCOMPLETE')


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func         ::  msgSendingPipelineLoadFromAcct    [[elisp:(org-cycle)][| ]]
"""

def msgSendingPipelineLoadFromAcct(
        bxoId,
        sr,
        msg,
        controlProfile,
        outMailAcct,
):
    """
** Just call with obtained base for acct.
    """
    acctBaseDir = marmeAcctsLib.outMailAcctDirGet(
        controlProfile,
        outMailAcct,
        bxoId=bxoId,
        sr=sr,
    )
    return (
        msgSendingPipelineLoadFromAcctBaseDir(
            msg,
            acctBaseDir,
        ))

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func         ::  msgSendingPipelineLoadFromAcctBaseDir    [[elisp:(org-cycle)][| ]]
"""

def msgSendingPipelineLoadFromAcctBaseDir(
        msg,
        acctBaseDir,
):
    """
** Read File Params for mailAcct and set X822-MSP params accordingly
    """
    opOutcome = b.op.Outcome()
    #print acctBaseDir
    #G = cs.globalContext.get()

    outcome = icm.FP_readTreeAtBaseDir().cmnd(
        interactive=False,
        FPsDir=os.path.join(acctBaseDir, 'access'),
    )
    fp_access_dict = outcome.results

    outcome = icm.FP_readTreeAtBaseDir().cmnd(
        interactive=False,
        FPsDir=os.path.join(acctBaseDir, 'controllerInfo'),
    )
    #fp_controllerInfo_dict = outcome.results

    outcome = icm.FP_readTreeAtBaseDir().cmnd(
        interactive=False,
        FPsDir=os.path.join(acctBaseDir, 'submission'),
    )
    fp_submission_dict = outcome.results

    envelopeAddr = fp_submission_dict["envelopeAddr"].parValueGet()

    msgOut.envelopeAddrSet(
        msg,
        mailBoxAddr=envelopeAddr,  # Mandatory
    )

    sendingMethod = fp_submission_dict["sendingMethod"].parValueGet()

    if msgOut.sendingMethodSet(msg, sendingMethod).isProblematic():
        return b_io.eh.badLastOutcome()

    if sendingMethod == msgOut.SendingMethod.inject:
        return opOutcome

    #
    # So, It is a submission
    #
    # NOTYET, below should be split and use
    #  msgOut.submitParamsNOT()
    #

    try:
        mtaRemHost = fp_access_dict["mtaRemHost"].parValueGet()
    except  KeyError:
        return icm.eh_problem_usageError_wOp(opOutcome, "Missing BX-MTA-Rem-Host")

    try:
        userName = fp_access_dict["userName"].parValueGet()
    except  KeyError:
        return icm.eh_problem_usageError_wOp(opOutcome, "Missing BX-MTA-Rem-User")

    try:
        userPasswd = fp_access_dict["userPasswd"].parValueGet()
    except  KeyError:
        return icm.eh_problem_usageError_wOp(opOutcome, "Missing BX-MTA-Rem-Passwd")

    try:
        remProtocol = fp_access_dict["mtaRemProtocol"].parValueGet()
    except  KeyError:
        return icm.eh_problem_usageError_wOp(opOutcome, "Missing BX-MTA-Rem-Protocol")

    try:
        remPortNu = fp_access_dict["mtaRemPortNu"].parValueGet()
    except  KeyError:
        remPortNu = None

    msgOut.submitParams(
        msg,
        mtaRemProtocol=remProtocol,          # smtp
        mtaRemHost=mtaRemHost,              # Remote Host To Submit to (could be localhost)
        mtaRemPort=remPortNu,
        mtaRemUser=userName,
        mtaRemPasswd=userPasswd,
        mtaRemCerts=None,
    )

    return opOutcome



####+BEGIN: b:py3:cs:framework/endOfFile :basedOn "classification"
""" #+begin_org
* [[elisp:(org-cycle)][| *End-Of-Editable-Text* |]] :: emacs and org variables and control parameters
#+end_org """

#+STARTUP: showall

### local variables:
### no-byte-compile: t
### end:
####+END:
