#!/bin/env python
# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: A =CmndSvc= for installing MARMEE related packages through bisos.binsprep.
#+end_org """

####+BEGIN: b:py3:cs:file/dblockControls :classification "cs-mu"
""" #+begin_org
* [[elisp:(org-cycle)][| /Control Parameters Of This File/ |]] :: dblk ctrls classifications=cs-mu
#+BEGIN_SRC emacs-lisp
(setq-local b:dblockControls t) ; (setq-local b:dblockControls nil)
(put 'b:dblockControls 'py3:cs:Classification "cs-mu") ; one of cs-mu, cs-u, cs-lib, bpf-lib, pyLibPure
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
** This File: /bisos/git/auth/bxRepos/bisos-pip/marmee/py3/bin/marmeeBinsPrep.cs
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:python:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['marmeeBinsPrep'], }
csInfo['version'] = '202212024932'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'marmeeBinsPrep-Panel.org'
csInfo['groupingType'] = 'IcmGroupingType-pkged'
csInfo['cmndParts'] = 'IcmCmndParts[common] IcmCmndParts[param]'
####+END:

csInfo['moduleDescription'] = """ #+begin_org
* [[elisp:(org-cycle)][| ~Description~ |]] :: [[file:/bisos/git/auth/bxRepos/blee-binders/bisos-core/COMEEGA/_nodeBase_/fullUsagePanel-en.org][BISOS COMEEGA Panel]]
A =CmndSvc= for for setting up Marmee (Multi-Account Resident Mail Exchange Environment) AAS (Accessible Abstract Service).
Manages Mail Account Profiles. Sets up currents. Works with -niche.
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
** Imports Based On Classification=cs-mu
#+end_org """
from bisos import b
from bisos.b import cs
from bisos.b import b_io

import collections
####+END:

from bisos.currents import currentsConfig
from bisos.common import csParam

import sys
import os
import pathlib

# from bisos.marmee import marmeAcctsLib, marmeeCurrentsLib
from bisos.currents import currentsConfig

""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] ~csuList emacs-list Specifications~  [[elisp:(blee:org:code-block/above-run)][ /Eval Below/ ]] [[elisp:(org-cycle)][| ]]
#+BEGIN_SRC emacs-lisp
(setq  b:py:cs:csuList
  (list
   "bisos.b.cs.ro"
   "bisos.csPlayer.bleep"
   ;; "bisos.marmee.marmeAcctsLib"
   "bisos.bpo.bpo"
   "bisos.bpo.bpoRunBases"
   ;; "bisos.marmee.marmeeCurrentsLib"
   "bisos.b.fpCls"
   "bisos.b.clsMethod_csu"
   "bisos.marmee.aasInMailFps"
   "bisos.marmee.aasOutMailFps"
   "bisos.marmee.aasMailFps"
   "bisos.marmee.marmeeMaildir"
   "bisos.marmee.maildrop"
   "bisos.marmee.marmeeQmailHere"
   "bisos.marmee.qmailOrAcct"
   "bisos.qmail.qmail_csu"
 ))
#+END_SRC
#+RESULTS:
| bisos.b.cs.ro | bisos.csPlayer.bleep | bisos.bpo.bpo | bisos.bpo.bpoRunBases | bisos.b.fpCls | bisos.b.clsMethod_csu | bisos.marmee.aasInMailFps | bisos.marmee.aasOutMailFps | bisos.marmee.aasMailFps | bisos.marmee.marmeeMaildir | bisos.marmee.maildrop | bisos.marmee.marmeeQmailHere | bisos.marmee.qmailOrAcct | bisos.qmail.qmail_csu |
#+end_org """

####+BEGIN: b:py3:cs:framework/csuListProc :pyImports t :csuImports t :csuParams t
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] =Process CSU List= with /14/ in csuList pyImports=t csuImports=t csuParams=t
#+end_org """

from bisos.b.cs import ro
from bisos.csPlayer import bleep
from bisos.bpo import bpo
from bisos.bpo import bpoRunBases
from bisos.b import fpCls
from bisos.b import clsMethod_csu
from bisos.marmee import aasInMailFps
from bisos.marmee import aasOutMailFps
from bisos.marmee import aasMailFps
from bisos.marmee import marmeeMaildir
from bisos.marmee import maildrop
from bisos.marmee import marmeeQmailHere
from bisos.marmee import qmailOrAcct
from bisos.qmail import qmail_csu


csuList = [ 'bisos.b.cs.ro', 'bisos.csPlayer.bleep', 'bisos.bpo.bpo', 'bisos.bpo.bpoRunBases', 'bisos.b.fpCls', 'bisos.b.clsMethod_csu', 'bisos.marmee.aasInMailFps', 'bisos.marmee.aasOutMailFps', 'bisos.marmee.aasMailFps', 'bisos.marmee.marmeeMaildir', 'bisos.marmee.maildrop', 'bisos.marmee.marmeeQmailHere', 'bisos.marmee.qmailOrAcct', 'bisos.qmail.qmail_csu', ]

g_importedCmndsModules = cs.csuList_importedModules(csuList)

def g_extraParams():
    csParams = cs.param.CmndParamDict()
    cs.csuList_commonParamsSpecify(csuList, csParams)
    cs.argsparseBasedOnCsParams(csParams)

####+END:

####+BEGIN: b:py3:cs:main/exposedSymbols :classes ("aasInMailFps.AasInMail_FPs" "aasOutMailFps.AasOutMail_FPs" "aasMailFps.AasMail_FPs")
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] ~Exposed Symbols List Specification~ with /3/ in Classes List
#+end_org """

AasInMail_FPs = aasInMailFps.AasInMail_FPs # exec/eval-ed as __main__.ClassName
AasOutMail_FPs = aasOutMailFps.AasOutMail_FPs # exec/eval-ed as __main__.ClassName
AasMail_FPs = aasMailFps.AasMail_FPs # exec/eval-ed as __main__.ClassName

####+END:


####+BEGIN: blee:bxPanel:foldingSection :outLevel 1 :title "CmndSvc-s" :extraInfo "class someCommand(cs.Cmnd)"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*       [[elisp:(outline-show-subtree+toggle)][| *CmndSvc-s:* |]]  class someCommand(cs.Cmnd)  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "examples" :cmndType ""  :comment "FrameWrk: ICM Examples" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<examples>>  *FrameWrk: ICM Examples*  =verify= ro=cli   [[elisp:(org-cycle)][| ]]
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
        self.cmndDocStr(f""" #+begin_org *
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Conventional top level example.
        #+end_org """)

####+BEGIN: b:py3:cs:module/cur_paramsAssign  :curParsList ("aasMarmee_base" "aasMarmee_bpoId")
        """ #+begin_org
***  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Currents   [[elisp:(outline-show-subtree+toggle)][||]] ~cur_examples~ (aasMarmee_base aasMarmee_bpoId)
        #+end_org """
        _parNamesList = [ 'aasMarmee_base', 'aasMarmee_bpoId',]
        if not (curParsDictValue := currentsConfig.curParsGetAsDictValue_wOp(_parNamesList, outcome=cmndOutcome).results): return(cmndOutcome)
        cur_aasMarmee_base = curParsDictValue['aasMarmee_base']
        cur_aasMarmee_bpoId = curParsDictValue['aasMarmee_bpoId']
        def cur_examples():
            cs.examples.execInsert(execLine='bx-currents.cs')
            cs.examples.execInsert(execLine='bx-currents.cs -i usgCursParsGet')
            for each in _parNamesList:
                cs.examples.execInsert(execLine=f'bx-currents.cs -v 20 -i usgCursParsSet {each}={curParsDictValue[each]}')
####+END:

        cs.examples.myName(cs.G.icmMyName(), cs.G.icmMyFullName())
        cs.examples.commonBrief()

        # bleep.examples_csBasic()

        # cs.examples.menuChapter('*Currents Examples Settings*')
        # cur_examples()

        # cur_marmeeEnvRelPath = f"aas/marmee/qmailHere/alias"
        cur_marmeeEnvRelPath = f"aas/marmee/qmailHere"

        bpoRunBases.examples_bpo_runBases(cur_aasMarmee_bpoId, f"aas/marmee/qmailHere/bystar", sectionTitle="default")
        # bpoRunBases.examples_bpo_runBases(cur_aasMarmee_bpoId, f"aas/marmee/qmailHere/bisos")
        # bpoRunBases.examples_bpo_runBases(cur_aasMarmee_bpoId, f"aas/marmee/qmailHere/bystar")

        # marmeeQmail.examples_csu(cur_aasMarmee_bpoId, cur_marmeeEnvRelPath, cur_aasMarmee_base, sectionTitle="default")

        marmeeMaildir.examples_csu(cur_aasMarmee_bpoId, cur_marmeeEnvRelPath, cur_aasMarmee_base, sectionTitle="default")

        # maildrop.examples_csu(cur_aasMarmee_bpoId, cur_marmeeEnvRelPath, cur_aasMarmee_base, sectionTitle="default")

        # qmailOrAcct.examples_csu(qmailAcct="alias", qmailAddr="postmaster", sectionTitle="default")

        p = pathlib.Path(f"~{cur_aasMarmee_bpoId}").expanduser().joinpath(f"aas/marmee/qmailHere")
        marmeeQmailHere.examples_csu(cur_aasMarmee_bpoId, marmeeBase=str(p), sectionTitle="default")

        # b.niche.examplesNicheRun("usageEnvs")

        return(cmndOutcome)



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
