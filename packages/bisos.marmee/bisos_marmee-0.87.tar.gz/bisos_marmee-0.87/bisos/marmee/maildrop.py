# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: A =CS-Lib= maildrop.
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
* *[[elisp:(org-cycle)][| Proclamations |]]* :: Libre-Halaal Software --- Part Of BISOS ---  Poly-COMEEGA Format.
** This is Libre-Halaal Software. © Neda Communications, Inc. Subject to AGPL.
** It is part of BISOS (ByStar Internet Services OS)
** Best read and edited  with Blee in Poly-COMEEGA (Polymode Colaborative Org-Mode Enhance Emacs Generalized Authorship)
#+end_org """
####+END:

####+BEGIN: b:prog:file/particulars :authors ("./inserts/authors-mb.org")
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars |]]* :: Authors, version
** This File: /bisos/git/auth/bxRepos/bisos-pip/marmee/py3/bisos/marmee/aasInMailOfflineimap.py
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:python:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['marmeeQmail'], }
csInfo['version'] = '202212053620'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'marmeeQmail-Panel.org'
csInfo['groupingType'] = 'IcmGroupingType-pkged'
csInfo['cmndParts'] = 'IcmCmndParts[common] IcmCmndParts[param]'
####+END:

csInfo['description'] = """ #+begin_org
* /[[elisp:(org-cycle)][| Description |]]/ :: [[file:/bisos/git/auth/bxRepos/blee-binders/bisos-core/COMEEGA/_nodeBase_/fullUsagePanel-en.org][BISOS COMEEGA Panel]]
Module description comes here.
** Relevant Panels:
** Status: In use with blee3
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
** Imports Based On Classification=cs-lib
#+end_org """
from bisos import b
from bisos.b import cs
from bisos.b import b_io

####+END:

import collections

import collections
import pathlib
import os
#import shutil

from bisos.bpo import bpoRunBases
from bisos.bpo import bpo

from bisos.common import csParam

#from bisos.marmee import aasInMailControl
from bisos.marmee import aasInMailFps
from bisos.marmee import aasOutMailFps

from bisos.basics import pyRunAs

from bisos.marmee import qmailOrAcct

####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "CmndSvcs" :anchor ""  :extraInfo "Command Services Section"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _CmndSvcs_: |]]  Command Services Section  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:


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
        bpoId: str,
        envRelPath: str,
        marmeeBase: typing.Optional[str],
        sectionTitle: typing.AnyStr = "",
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Examples of Service Access Instance Commands.
    #+end_org """

    def cpsInit(): return collections.OrderedDict()
    def menuItem(verbosity): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity=verbosity) # 'little' or 'none'
    # def execLineEx(cmndStr): cs.examples.execInsert(execLine=cmndStr)

    if sectionTitle == "default":
        cs.examples.menuChapter('*Mail Drop Utilities*')

    if marmeeBase == None:
        return

    #cs.examples.menuChapter('*Maildrop  Action*')

    icmWrapper = "" ;  cmndName = "maildropToRunEnvFromOrAcctAddrs"
    cps = cpsInit() ; cps['bpoId'] = bpoId ; cps['envRelPath'] = envRelPath
    cmndArgs = "main alias postmaster"
    cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='none', icmWrapper=icmWrapper)


####+BEGIN: bx:cs:py3:section :title "CS-Params  --- Place Holder, Empty"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *CS-Params  --- Place Holder, Empty*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "Functions" :anchor ""  :extraInfo "maildrop stdout/update"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _Functions_: |]]  maildrop stdout/update  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: b:py3:cs:func/typing :funcName "maildropTemplateStr" :funcType "eType" :deco "default"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-eType  [[elisp:(outline-show-subtree+toggle)][||]] /maildropTemplateStr/  deco=default  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def maildropTemplateStr(
####+END:
) -> str:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr* | ] Returns Template As String
    #+end_org """

    templateStr = """
# MACHINE GENERATED with {G_myName} and {m_myName} on {dateTag}
# -- DO NOT HAND EDIT
#filter rules for maildrop
#make sure this file is without any group and world permissions

to {destinationMaildirPath}

"""
    return templateStr

####+BEGIN: b:py3:cs:func/typing :funcName "maildropStr" :funcType "eType" :deco "default"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-eType  [[elisp:(outline-show-subtree+toggle)][||]] /maildropStr/  deco=default  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def maildropStr(
####+END:
        destMaildirPath: str,
) -> str:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr* | ] Returns Template As String
    #+end_org """

    resStr = maildropTemplateStr().format(
        destinationMaildirPath=destMaildirPath,
        G_myName="NOTYET",
        m_myName="NOTYET",
        dateTag="NOTYET",
    )
    return resStr

####+BEGIN: b:py3:cs:func/typing :funcName "maildropFileUpdate" :funcType "eType" :deco "default"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-eType  [[elisp:(outline-show-subtree+toggle)][||]] /maildropFileUpdate/  deco=default  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def maildropFileUpdate(
####+END:
        destMaildirPath: str,
        fileName: str,
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr* | ] Returns Template As String
    #+end_org """

    resStr = maildropStr(destMaildirPath)
    print(resStr)

####+BEGIN: b:py3:cs:func/typing :funcName "maildropFileName" :funcType "eType" :deco "default"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-eType  [[elisp:(outline-show-subtree+toggle)][||]] /maildropFileName/  deco=default  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def maildropFileName(
####+END:
        mailAddr: str,
) -> pathlib.Path:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr* | ] Returns Template As String
    #+end_org """
    return pathlib.Path(f".maildrop-{mailAddr}")


####+BEGIN: bx:cs:py3:section :title "CS-Commands"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *CS-Commands*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "maildropToRunEnvFromOrAcctAddrs" :comment "" :extent "verify" :parsMand "bpoId envRelPath" :argsMin 3 :argsMax 9999 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<maildropToRunEnvFromOrAcctAddrs>>  =verify= parsMand=bpoId envRelPath argsMin=3 argsMax=9999 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class maildropToRunEnvFromOrAcctAddrs(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'envRelPath', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 3, 'Max': 9999,}

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
        bpoId = csParam.mappedValue('bpoId', bpoId)
        envRelPath = csParam.mappedValue('envRelPath', envRelPath)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] arg0 is destintation maildir. arg1 is a qmailOrAcct arg2-N are qmailOrAcctAddrs
        In qmailOrAcct for each specified qmailOrAcctAddr, we update the ~qmailOrAcct/.maildrop.qmailOrAcctAddr
        Permissions are expected to have been fully relaxed in the destination maildir so that qmailOrAcct can write there.


            #os.system(f'ls -l maildropRelPath')
            #print(resStr)

            #return(cmndOutcome)


        #+end_org """)

        cmndArgsSpecDict = self.cmndArgsSpec()
        destMaildirName = self.cmndArgsGet("0", cmndArgsSpecDict, argsList)
        qmailAcct = self.cmndArgsGet("1", cmndArgsSpecDict, argsList)
        qmailAddrs = self.cmndArgsGet("2&9999", cmndArgsSpecDict, argsList)

        # print(f"{maildirName} {qmailAddrs}")

        runEnvBases = b.pattern.sameInstance(
            bpoRunBases.BpoRunEnvBases,
            bpoId,
            envRelPath,
        )
        runEnvBases.basesUpdate()
        dataBase = runEnvBases.dataBasePath_obtain()

        maildirFullPath = pathlib.Path(os.path.join(dataBase, 'maildir'))

        destMaildirPath = maildirFullPath.joinpath(destMaildirName)

        qmailAcctPath = pathlib.Path(os.path.expanduser(f'~{qmailAcct}'))
        #qmailAcctPath = qmailOrAcct.acctPathForQmailAcct(qmailAcct)

        for eachQmailAddr in qmailAddrs:
            maildropAsStr = maildropStr(destMaildirPath)
            maildropRelPath = maildropFileName(eachQmailAddr)
            maildropPath = qmailAcctPath.joinpath(maildropRelPath)
            pyRunAs.as_root_writeToFile(
                maildropPath,
                maildropAsStr
            )
            pyRunAs.as_root_osSystem(
                f"""chown {qmailAcct} {maildropPath}"""
            )
            pyRunAs.as_root_osSystem(
                f"""chmod 600 {maildropPath}"""
            )
            os.system(f"ls -l {maildropPath}")

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
            argName="destMaildirName",
            argChoices=[],
            argDescription="Destination Maildir Name"
        )
        cmndArgsSpecDict.argsDictAdd(
            argPosition="1",
            argName="qmailAcct",
            argChoices=[],
            argDescription="qmail OR Account"
        )
        return cmndArgsSpecDict
        cmndArgsSpecDict.argsDictAdd(
            argPosition="2&9999",
            argName="qmailAddrs",
            argChoices=[],
            argDescription="qmail Addresses"
        )
        return cmndArgsSpecDict


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "OK2Del_maildropToRunEnvFromOrAcctAddrs" :comment "" :extent "verify" :parsMand "bpoId envRelPath" :argsMin 3 :argsMax 9999 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<OK2Del_maildropToRunEnvFromOrAcctAddrs>>  =verify= parsMand=bpoId envRelPath argsMin=3 argsMax=9999 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class OK2Del_maildropToRunEnvFromOrAcctAddrs(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'envRelPath', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 3, 'Max': 9999,}

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
        bpoId = csParam.mappedValue('bpoId', bpoId)
        envRelPath = csParam.mappedValue('envRelPath', envRelPath)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] arg0 is destintation maildir. arg1 is a qmailOrAcct arg2-N are qmailOrAcctAddrs
        Permissions are fully relaxed in the destination maildir so that qmailOrAcct can write there.
        In qmailOrAcct for each specified qmailOrAcctAddr, we update the ~qmailOrAcct/.maildrop.qmailOrAcctAddr
        #+end_org """)

        cmndArgsSpecDict = self.cmndArgsSpec()
        destMaildirName = self.cmndArgsGet("0", cmndArgsSpecDict, argsList)
        qmailOrAcct = self.cmndArgsGet("1", cmndArgsSpecDict, argsList)
        qmailAddrs = self.cmndArgsGet("2&9999", cmndArgsSpecDict, argsList)

        # print(f"{maildirName} {qmailAddrs}")

        runEnvBases = b.pattern.sameInstance(
            bpoRunBases.BpoRunEnvBases,
            bpoId,
            envRelPath,
        )
        runEnvBases.basesUpdate()
        dataBase = runEnvBases.dataBasePath_obtain()

        maildirFullPath = pathlib.Path(os.path.join(dataBase, 'maildir'))

        destMaildirPath = maildirFullPath.joinpath(destMaildirName)

        aliasBasePath = pathlib.Path(os.path.expanduser(f'~{qmailOrAcct}'))

        for eachQmailAddr in qmailAddrs:
            for eachDotQmail in aliasBasePath.iterdir():
                if eachDotQmail.name.startswith(f".qmail-{eachQmailAddr}"):
                    print(f"{eachDotQmail.name}")
                    if not (resStr := b.subProc.WOpW(invedBy=self, log=0).bash(
                        f"""sudo cat  {eachDotQmail}""",
                    ).stdout):  return(b_io.eh.badOutcome(cmndOutcome))
                    print(resStr)
                    if not str(destMaildirPath) in resStr:
                        print(f"NOTYET Write {destMaildirPath}")
                    resStr = maildropStr(destMaildirPath)
                    print(resStr)
                    break

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
            argName="destMaildirName",
            argChoices=[],
            argDescription="Destination Maildir Name"
        )
        cmndArgsSpecDict.argsDictAdd(
            argPosition="1",
            argName="qmailOrAcct",
            argChoices=[],
            argDescription="qmail OR Account"
        )
        return cmndArgsSpecDict
        cmndArgsSpecDict.argsDictAdd(
            argPosition="2&9999",
            argName="qmailAddrs",
            argChoices=[],
            argDescription="qmail Addresses"
        )
        return cmndArgsSpecDict



####+BEGIN: b:py3:cs:framework/endOfFile :basedOn "classification"
""" #+begin_org
* [[elisp:(org-cycle)][| *End-Of-Editable-Text* |]] :: emacs and org variables and control parameters
#+end_org """

#+STARTUP: showall

### local variables:
### no-byte-compile: t
### end:
####+END:
