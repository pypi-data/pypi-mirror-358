# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: A =CS-Lib= for InMail Abstracted Accessible Service (aas) Offline Imap.
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
csInfo['version'] = '202212061422'
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
** Imports Based On Classification=cs-u
#+end_org """
from bisos import b
from bisos.b import cs
from bisos.b import b_io

import collections
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
from bisos.marmee import marmeeMaildir

from bisos.qmail import qmail

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
        oneBpo: str,
        oneEnvRelPath: str = "aas/marmee/qmailHere",
        marmeeBase: typing.Optional[str] = None,
        sectionTitle: typing.AnyStr = "",
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Examples of Service Access Instance Commands.
    #+end_org """


    if sectionTitle == "default":
        cs.examples.menuChapter('*Here qmail Config Utilities*')

    if marmeeBase == None:
        return

    od = collections.OrderedDict
    cmnd = cs.examples.cmndEnter
    # literal = cs.examples.execInsert

    cs.examples.menuSection('*Here qmail Access Account Update*')

    bpoAndRelPathPars = od([('bpoId', oneBpo), ('envRelPath', oneEnvRelPath),])
    marmeeBasePars = od([('aasMarmeeBase', marmeeBase),])

    cmnd('marmeeQmailAcctUpdate', args="bystar", pars=marmeeBasePars, comment=f" # ")

    # cs.examples.menuSection('*qmailHere Create/Update .qmail File*')

    # bpoAndRelPathPars = od([('bpoId', oneBpo), ('envRelPath', oneEnvRelPath),])
    # marmeeBasePars = od([('aasMarmeeBase', marmeeBase),])

    # cmnd('marmeeQmailHereDotQmail', args="bisos", pars=marmeeBasePars, comment=f" # ")
    # cmnd('marmeeQmailHereDotQmail', args="bystar", pars=marmeeBasePars, comment=f" # ")

    cs.examples.menuSection('*Marmee (QmailHere) dotQmail Maildir*')

    cmnd('marmeeDotQmailMaildir', args="", comment=f" #  ",
         pars=od([('qAddrAcct', "bystar"),
                  ('localPart', "BLANK"),
                  ('maildir', "/bxo/iso/piu_mbFullUsage/aas/marmee/qmailHere/bystar/data/maildir/main/"),
                  ])
         )
    cmnd('marmeeDotQmailMaildir', args="", comment=f" #  ",
         pars=od([('qAddrAcct', "bystar"),
                  ('localPart', "bisos"),
                  ('maildir', "/bxo/iso/piu_mbFullUsage/aas/marmee/qmailHere/bystar/data/maildir/bisos/"),
                  ])
         )
    cmnd('marmeeDotQmailMaildir', args="", comment=f" #  ",
         pars=od([('qAddrAcct', "bystar"),
                  ('localPart', "alias"),
                  ('maildir', "/bxo/iso/piu_mbFullUsage/aas/marmee/qmailHere/bystar/data/maildir/alias/"),
                  ])
         )

    cs.examples.menuSection('*Marmee (QmailHere) ALIAS dotQmail Forwards*')

    cmnd('marmeeDotQmailForwardTo', pars=od([('qAddrAcct', "alias"), ('localPart', "postmaster"),]), args="bystar-alias", comment=f" #  ",)
    cmnd('marmeeDotQmailForwardTo', pars=od([('qAddrAcct', "alias"), ('localPart', "root"),]), args="bystar-alias", comment=f" #  ",)
    cmnd('marmeeDotQmailForwardTo', pars=od([('qAddrAcct', "alias"), ('localPart', "mailer-daemon"),]), args="bystar-alias", comment=f" #  ",)

    cs.examples.menuSection('*Marmee (QmailHere) BISOS dotQmail Forwards*')

    cmnd('marmeeDotQmailForwardTo', pars=od([('qAddrAcct', "bisos"), ('localPart', "BLANK"),]), args="bystar-bisos", comment=f" #  ",)

    cs.examples.menuSection('*Full Update*')

    cmnd('marmeeQmailHereFullUpdate', args="", pars=od([('bpoId', oneBpo),]),  comment=f" # ")

    # #cs.examples.menuChapter('*Gmail Config Utilities*')

    # cmndName = "marmeeQmailAcctUpdate" ;  cmndArgs = "alias"
    # cps=cpsInit(); cps['aasMarmeeBase'] = marmeeBase
    # menuItem(verbosity='none') #; menuItem(verbosity='full')

####+BEGIN: bx:cs:py3:section :title "CS-Params  --- Place Holder, Empty"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *CS-Params  --- Place Holder, Empty*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:


####+BEGIN: bx:cs:py3:section :title "CS-Commands"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *CS-Commands*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "marmeeQmailHereFullUpdate" :comment "Full Update qAddrAcct" :extent "verify" :parsMand "bpoId" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<marmeeQmailHereFullUpdate>>  *Full Update qAddrAcct*  =verify= parsMand=bpoId ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class marmeeQmailHereFullUpdate(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:
        """Full Update qAddrAcct"""
        failed = b_io.eh.badOutcome
        callParamsDict = {'bpoId': bpoId, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        bpoId = csParam.mappedValue('bpoId', bpoId)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]
        #+end_org """)

        #
        print(f"Full Update")


        if bpoRunBases.bpoRunEnvBasesUpdate().pyWCmnd(
                cmndOutcome,
                bpoId=bpoId,
                envRelPath="aas/marmee/qmailHere/bystar",
                argsList=[],
        ).isProblematic():  failed(cmndOutcome)

        if marmeeMaildir.envMaildirCreate().pyWCmnd(
                cmndOutcome,
                bpoId=bpoId,
                envRelPath="aas/marmee/qmailHere/bystar",
                argsList=["main", "alias", "bisos",],
        ).isProblematic():  failed(cmndOutcome)

        bpoBase = pathlib.Path(bpo.bpoBaseDir_obtain(bpoId))
        aasMarmeeBase = bpoBase.joinpath("aas/marmee/qmailHere")

        if marmeeQmailAcctUpdate().pyWCmnd(
                cmndOutcome,
                aasMarmeeBase=aasMarmeeBase,
                argsList=["bystar"],
        ).isProblematic():  failed(cmndOutcome)

        maildir = bpoBase.joinpath("aas/marmee/qmailHere/bystar/data/maildir/main")
        if marmeeDotQmailMaildir().pyWCmnd(
               cmndOutcome,
               qAddrAcct="bystar",
               localPart="BLANK",
               maildir=f"{maildir}/",
        ).isProblematic():  failed(cmndOutcome)

        maildir = bpoBase.joinpath("aas/marmee/qmailHere/bystar/data/maildir/bisos")
        if marmeeDotQmailMaildir().pyWCmnd(
               cmndOutcome,
               qAddrAcct="bystar",
               localPart="bisos",
               maildir=f"{maildir}/",
        ).isProblematic():  failed(cmndOutcome)

        maildir = bpoBase.joinpath("aas/marmee/qmailHere/bystar/data/maildir/alias")
        if marmeeDotQmailMaildir().pyWCmnd(
               cmndOutcome,
               qAddrAcct="bystar",
               localPart="alias",
               maildir=f"{maildir}/",
        ).isProblematic():  failed(cmndOutcome)

        if marmeeDotQmailForwardTo().pyWCmnd(
                cmndOutcome,
                qAddrAcct="alias",
                localPart="postmaster",
                argsList=["bystar-alias"],
        ).isProblematic():  failed(cmndOutcome)

        if marmeeDotQmailForwardTo().pyWCmnd(
                cmndOutcome,
                qAddrAcct="alias",
                localPart="root",
                argsList=["bystar-alias"],
        ).isProblematic():  failed(cmndOutcome)

        if marmeeDotQmailForwardTo().pyWCmnd(
                cmndOutcome,
                qAddrAcct="alias",
                localPart="mailer-daemon",
                argsList=["bystar-alias"],
        ).isProblematic():  failed(cmndOutcome)

        if marmeeDotQmailForwardTo().pyWCmnd(
                cmndOutcome,
                qAddrAcct="bisos",
                localPart="BLANK",
                argsList=["bystar-bisos"],
        ).isProblematic():  failed(cmndOutcome)

        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=True,
        )

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "marmeeDotQmailMaildir" :comment "Create/Update .qmail for qAddrAcct" :extent "verify" :parsMand "qAddrAcct localPart maildir" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<marmeeDotQmailMaildir>>  *Create/Update .qmail for qAddrAcct*  =verify= parsMand=qAddrAcct localPart maildir ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class marmeeDotQmailMaildir(cs.Cmnd):
    cmndParamsMandatory = [ 'qAddrAcct', 'localPart', 'maildir', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             qAddrAcct: typing.Optional[str]=None,  # Cs Mandatory Param
             localPart: typing.Optional[str]=None,  # Cs Mandatory Param
             maildir: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:
        """Create/Update .qmail for qAddrAcct"""
        failed = b_io.eh.badOutcome
        callParamsDict = {'qAddrAcct': qAddrAcct, 'localPart': localPart, 'maildir': maildir, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        qAddrAcct = csParam.mappedValue('qAddrAcct', qAddrAcct)
        localPart = csParam.mappedValue('localPart', localPart)
        maildir = csParam.mappedValue('maildir', maildir)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]
        #+end_org """)

        if localPart == "BLANK": localPart = ""

        dotQmailFile = qmail.DotQmailFile(qAddrAcct, localPart)

        dotQmailFile.addMaildirLine(maildir, inOutcome=cmndOutcome,)

        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=True,
        )

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "marmeeDotQmailForwardTo" :comment "Add forward lines" :extent "verify" :parsMand "qAddrAcct localPart" :parsOpt "" :argsMin 1 :argsMax 9999 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<marmeeDotQmailForwardTo>>  *Add forward lines*  =verify= parsMand=qAddrAcct localPart argsMin=1 argsMax=9999 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class marmeeDotQmailForwardTo(cs.Cmnd):
    cmndParamsMandatory = [ 'qAddrAcct', 'localPart', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 9999,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             qAddrAcct: typing.Optional[str]=None,  # Cs Mandatory Param
             localPart: typing.Optional[str]=None,  # Cs Mandatory Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:
        """Add forward lines"""
        failed = b_io.eh.badOutcome
        callParamsDict = {'qAddrAcct': qAddrAcct, 'localPart': localPart, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        qAddrAcct = csParam.mappedValue('qAddrAcct', qAddrAcct)
        localPart = csParam.mappedValue('localPart', localPart)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]
        #+end_org """)

        if localPart == "BLANK": localPart = ""

        dotQmailFile = qmail.DotQmailFile(qAddrAcct, localPart)

        fwdAddrs = self.cmndArgsGet("0&9999", cmndArgsSpecDict, argsList)

        for eachAddr in fwdAddrs:
            dotQmailFile.addForwardLine(eachAddr, inOutcome=cmndOutcome,)

        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=True,
        )

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
            argPosition="0&9999",
            argName="qmailAccts",
            argChoices=[],
            argDescription="qmail Accounts"
        )

        return cmndArgsSpecDict



####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "marmeeQmailAcctUpdate" :comment "" :extent "verify" :parsMand "aasMarmeeBase" :parsOpt "" :argsMin 1 :argsMax 9999 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<marmeeQmailAcctUpdate>>  =verify= parsMand=aasMarmeeBase argsMin=1 argsMax=9999 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class marmeeQmailAcctUpdate(cs.Cmnd):
    cmndParamsMandatory = [ 'aasMarmeeBase', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 9999,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             aasMarmeeBase: typing.Optional[str]=None,  # Cs Mandatory Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        callParamsDict = {'aasMarmeeBase': aasMarmeeBase, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        aasMarmeeBase = csParam.mappedValue('aasMarmeeBase', aasMarmeeBase)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]
        #+end_org """)

        cmndArgsSpecDict = self.cmndArgsSpec()
        qmailAccts = self.cmndArgsGet("0&9999", cmndArgsSpecDict, argsList)

        # qmailBasePath = pathlib.Path(aasMarmeeBase).joinpath('qmail')
        qmailBasePath = pathlib.Path(aasMarmeeBase)

        for eachAcct in qmailAccts:
            controlBasePath = qmailBasePath.joinpath(eachAcct).joinpath('control')
            #print(controlBasePath)
            inMailFpsBase = controlBasePath.joinpath('inMail/fp')
            inMailFpsInst = b.pattern.sameInstance(aasInMailFps.AasInMail_FPs, fpBase=inMailFpsBase)
            inMailFpsInst.fps_setParam('userName', eachAcct)
            inMailFpsInst.fps_setParam('svcProvider', 'qmail')
            inMailFpsInst.fps_setParam('svcInstance', eachAcct)

            outMailFpsBase = controlBasePath.joinpath('outMail/fp')
            outMailFpsInst = b.pattern.sameInstance(aasOutMailFps.AasOutMail_FPs, fpBase=outMailFpsBase)
            outMailFpsInst.fps_setParam('outMail_useSsl', 'True')
            outMailFpsInst.fps_setParam('outMail_port', '465')
            outMailFpsInst.fps_setParam('outMail_smtpServer', 'NOTYET')
            outMailFpsInst.fps_setParam('outMail_userName', f"{eachAcct}@NOTYET")

        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=True,
        )

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
            argPosition="0&9999",
            argName="qmailAccts",
            argChoices=[],
            argDescription="qmail Accounts"
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
