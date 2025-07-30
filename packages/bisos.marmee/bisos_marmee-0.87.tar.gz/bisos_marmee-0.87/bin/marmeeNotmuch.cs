#!/bin/env python
# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: A =CmndSvc= for Notmuch based user agent
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
** This File: /bisos/git/auth/bxRepos/bisos-pip/marmee/py3/bin/marmeeNotmuch.cs
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:py3:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['marmeeNotmuch'], }
csInfo['version'] = '202210211556'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'marmeeNotmuch-Panel.org'
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
** Imports Based On Classification=cs-mu
#+end_org """
from bisos import b
from bisos.b import cs
from bisos.b import b_io

import collections
####+END:

import os
import pathlib

from bisos.marmee import marmeePkgThis
from bisos.currents import currentsConfig

# from bisos.bpo import bpo
from bisos.bpo import bpoRunBases


""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] ~csuList emacs-list Specifications~  [[elisp:(blee:org:code-block/above-run)][ /Eval Below/ ]] [[elisp:(org-cycle)][| ]]
#+BEGIN_SRC emacs-lisp
(setq  b:py:cs:csuList
  (list
   "bisos.b.cs.ro"
   "bisos.csPlayer.bleep"
   "bisos.bpo.bpo"
   "bisos.marmee.aasInMailFps"
 ))
#+END_SRC
#+RESULTS:
| bisos.b.cs.ro | bisos.csPlayer.bleep | bisos.bpo.bpo | bisos.marmee.aasInMailFps |
#+end_org """

####+BEGIN: b:py3:cs:framework/csuListProc :pyImports t :csuImports t :csuParams t
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] =Process CSU List= with /4/ in csuList pyImports=t csuImports=t csuParams=t
#+end_org """

from bisos.b.cs import ro
from bisos.csPlayer import bleep
from bisos.bpo import bpo
from bisos.marmee import aasInMailFps


csuList = [ 'bisos.b.cs.ro', 'bisos.csPlayer.bleep', 'bisos.bpo.bpo', 'bisos.marmee.aasInMailFps', ]

g_importedCmndsModules = cs.csuList_importedModules(csuList)

def g_extraParams():
    csParams = cs.param.CmndParamDict()
    cs.csuList_commonParamsSpecify(csuList, csParams)
    cs.argsparseBasedOnCsParams(csParams)

####+END:

####+BEGIN: b:py3:cs:main/exposedSymbols :classes ()
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] ~Exposed Symbols List Specification~ with /0/ in Classes List
#+end_org """
####+END:

####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "CmndSvcs" :anchor ""  :extraInfo "Command Services Section"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _CmndSvcs_: |]]  Command Services Section  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "examples" :extent "verify" :ro "noCli" :comment "FrameWrk: CS-Main-Examples" :parsMand "" :parsOpt "" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<examples>>  *FrameWrk: CS-Main-Examples*  =verify= argsMin=0 argsMax=0 ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class examples(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}
    rtInvConstraints = cs.rtInvoker.RtInvoker.new_noRo() # NO RO From CLI

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:
        """FrameWrk: CS-Main-Examples"""
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Conventional top level example.
        #+end_org """)

####+BEGIN: b:py3:cs:module/cur_paramsAssign  :curParsList ("aasMarmee_bpoId" "aasMarmee_envRelPath")
        """ #+begin_org
***  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Currents   [[elisp:(outline-show-subtree+toggle)][||]] ~cur_examples~ (aasMarmee_bpoId aasMarmee_envRelPath)
        #+end_org """
        _parNamesList = [ 'aasMarmee_bpoId', 'aasMarmee_envRelPath',]
        if not (curParsDictValue := currentsConfig.curParsGetAsDictValue_wOp(_parNamesList, outcome=cmndOutcome).results): return(cmndOutcome)
        cur_aasMarmee_bpoId = curParsDictValue['aasMarmee_bpoId']
        cur_aasMarmee_envRelPath = curParsDictValue['aasMarmee_envRelPath']
        def cur_examples():
            cs.examples.execInsert(execLine='bx-currents.cs')
            cs.examples.execInsert(execLine='bx-currents.cs -i usgCursParsGet')
            for each in _parNamesList:
                cs.examples.execInsert(execLine=f'bx-currents.cs -v 20 -i usgCursParsSet {each}={curParsDictValue[each]}')
####+END:


        def cpsInit(): return collections.OrderedDict()
        def menuItem(verbosity): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity=verbosity) # 'little' or 'none'
        def execLineEx(cmndStr): cs.examples.execInsert(execLine=cmndStr)

        bpoId = cur_aasMarmee_bpoId
        envRelPath = cur_aasMarmee_envRelPath

        def cmndParsCurBpoAndEnvRelPath(cps): cps['bpoId'] = cur_aasMarmee_bpoId ; cps['envRelPath'] = cur_aasMarmee_envRelPath


        cs.examples.myName(cs.G.icmMyName(), cs.G.icmMyFullName())

        cs.examples.commonBrief()

        bleep.examples_csBasic()

        cs.examples.menuChapter('*Currents Examples Settings*')
        cur_examples()


        # defaultMailDom = marmeAcctsLib.enabledInMailAcctObtain(
        #     bpoId=curGet_bpoId(),
        #     sr=curGet_sr(),
        # )

####+BEGIN: bx:cs:python:cmnd:subSection :title "Dev And Testing"

####+END:
        #cs.examples.menuChapter('*General Dev and Testing IIFs*')

        cs.examples.menuChapter('*Config File Creation Facilities*')

        cs.examples.menuSection('*Automated Config File Creation Facilities*')

        cmndName = "notmuchConfigUpdate" ; cmndArgs = ""
        cps=cpsInit(); cmndParsCurBpoAndEnvRelPath(cps);
        menuItem(verbosity='none') # ; menuItem(verbosity='full')

        cmndName = "notmuchConfigStdout" ; cmndArgs = ""
        cps=cpsInit(); cmndParsCurBpoAndEnvRelPath(cps);
        menuItem(verbosity='none') # ; menuItem(verbosity='full')

        configFile = notmuchConfigPathObtain(bpoId, envRelPath)
        b_io.ann.write(f"""ls -l {configFile}""")
        b_io.ann.write(f"""cat {configFile}""")

        cs.examples.menuSection('*Interactive Config File Creation Facilities*')

        cmndName = "runNotmuch" ; cmndArgs = "setup" ;
        cps=cpsInit() ;  cmndParsCurBpoAndEnvRelPath(cps);
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='basic',
                             comment='# Creates/Edits notmuch-config', icmWrapper=None, icmName=None)

        cs.examples.menuSection('*Show/List Config Parameter Settings*')

        cmndName = "runNotmuch" ; cmndArgs = "config list" ;
        cps=cpsInit() ;  cmndParsCurBpoAndEnvRelPath(cps);
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='basic',
                             comment='# Shows Key aspects of notmuch-config', icmWrapper=None, icmName=None)


        cs.examples.menuChapter('*Run notmuch -- new, Search*')

        cmndName = "runNotmuch" ; cmndArgs = "new" ;
        cps=cpsInit() ;  cmndParsCurBpoAndEnvRelPath(cps);
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='basic',
                             comment='# Refresh the index', icmWrapper=None, icmName=None)


        cmndName = "runNotmuch" ; cmndArgs = '''-- search --format=text --output=files "from:"''' ;
        cps=cpsInit() ;  cmndParsCurBpoAndEnvRelPath(cps);
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='basic',
                             comment='# Search Based on from', icmWrapper=None, icmName=None)

        cmndName = "runNotmuch" ; cmndArgs = '''-- search --format=text --output=files "from:"''' ;
        cps=cpsInit() ;  cmndParsCurBpoAndEnvRelPath(cps);
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='none',
                             comment='# Search Based on from', icmWrapper='echo', icmName=None)

        cmndName = "runNotmuch" ; cmndArgs = '''-- search "from:"''' ;
        cps=cpsInit() ;  cmndParsCurBpoAndEnvRelPath(cps);
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='basic',
                             comment='# Search Based on from', icmWrapper=None, icmName=None)

        cmndName = "runNotmuch" ; cmndArgs = '''-- search "from:"''' ;
        cps=cpsInit() ;  cmndParsCurBpoAndEnvRelPath(cps);
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='none',
                             comment='# Search Based on from', icmWrapper='echo', icmName=None)

        cmndName = "runNotmuch" ; cmndArgs = '''-- search --format=text --output=files "from:" | grep Inbox | xargs egrep "^Subject:"''' ;
        cps=cpsInit() ;  cmndParsCurBpoAndEnvRelPath(cps);
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='basic',
                             comment='# Search Based on from', icmWrapper=None, icmName=None)

        cmndName = "runNotmuch" ; cmndArgs = '''-- search --format=text --output=files "from:" | grep Inbox | xargs egrep "^Subject:"''' ;
        cps=cpsInit() ;  cmndParsCurBpoAndEnvRelPath(cps);
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='none',
                             comment='# Search Based on from', icmWrapper="echo", icmName=None)

        cmndName = "runNotmuch" ; cmndArgs = '''-- search --output=files "to: example.com"''' ;
        cps=cpsInit() ;  cmndParsCurBpoAndEnvRelPath(cps);
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='none',
                             comment='# Search Based on from', icmWrapper="echo", icmName=None)


        b.ignore(ro.__doc__,)  # We are not using these modules, but they are auto imported.

        return(cmndOutcome)

####+BEGIN: bx:icm:py3:section :title "CS-Commands"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *CS-Commands*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :modPrefix "new" :cmndName "notmuchConfigUpdate" :comment "" :parsMand "bpoId envRelPath" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<notmuchConfigUpdate>>  =verify= parsMand=bpoId envRelPath ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class notmuchConfigUpdate(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'envRelPath', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Mandatory Param
             envRelPath: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        callParamsDict = {'bpoId': bpoId, 'envRelPath': envRelPath, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
####+END:
        cmndOutcome = notmuchConfigStdout().pyCmnd(
            bpoId=bpoId,
            envRelPath=envRelPath,
        )
        if cmndOutcome.isProblematic(): return(b_io.eh.badOutcome(cmndOutcome))
        configFileStr = cmndOutcome.stdout

        configFilePath = notmuchConfigPathObtain(bpoId, envRelPath,)

        with open(configFilePath, "w") as thisFile:
            thisFile.write(f"{configFileStr}\n")

        if rtInv.outs:
            b_io.ann.here(f"configFilePath={configFilePath}")

        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=None,
        )

####+BEGIN: b:py3:cs:cmnd/classHead :modPrefix "new" :cmndName "notmuchConfigStdout" :comment "" :parsMand "bpoId envRelPath" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<notmuchConfigStdout>>  =verify= parsMand=bpoId envRelPath ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class notmuchConfigStdout(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'envRelPath', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Mandatory Param
             envRelPath: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        callParamsDict = {'bpoId': bpoId, 'envRelPath': envRelPath, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  A starting point command.
        #+end_org """)

        templateFile = os.path.join(
            marmeePkgThis.pkgBase_baseDir(),
            "inputs",
            "notmuch/_notmuch-config.template",
        )

        runEnvBases = b.pattern.sameInstance(
            bpoRunBases.BpoRunEnvBases,
            bpoId,
            envRelPath,
        )
        dataBase = runEnvBases.dataBasePath_obtain()

        mailDirPath = os.path.join(dataBase, 'maildir')

        firstName="FirstName"
        lastName="LastName"

        if b.subProc.WOpW(invedBy=self, log=0).bash(
                f"""\
cat {templateFile} | \
        sed \
            -e "s@%mailDirPath%@{mailDirPath}@g" \
            -e "s@%firstName%@{firstName}@g" \
            -e "s@%lastName%@{lastName}@g"
"""
        ).isProblematic():  return(b_io.eh.badOutcome(cmndOutcome))

        if rtInv.outs:
            b_io.ann.write(cmndOutcome.stdout)

        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=cmndOutcome.stdout
        )

####+BEGIN: b:py3:cs:cmnd/classHead :modPrefix "new" :cmndName "runNotmuch" :comment "" :parsMand "bpoId envRelPath" :parsOpt "" :argsMin 0 :argsMax 1000 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<runNotmuch>>  =verify= parsMand=bpoId envRelPath argsMax=1000 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class runNotmuch(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'envRelPath', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 1000,}

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
####+END:
        cmndArgs = self.cmndArgsGet("0&-1", cmndArgsSpecDict, argsList)
        joinedArgs = ' '.join(cmndArgs)

        configFile = notmuchConfigPathObtain(bpoId, envRelPath)

        if b.subProc.WOpW(invedBy=self, log=1).bash(
                f"""notmuch --config={configFile} {joinedArgs}"""
        ).isProblematic():  return(b_io.eh.badOutcome(cmndOutcome))

        return cmndOutcome.set(
            opError=b.OpError.Success,
            #opResults=outcome.stdout
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
            argChoices='any',
            argDescription="Rest of args for use by action"
        )

        return cmndArgsSpecDict


####+BEGIN: b:py3:cs:func/typing :funcName "notmuchConfigPathObtain" :funcType "anyOrNone" :retType "bool" :deco "default" :argsList "inMailAcct bpoId=None sr=None"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /notmuchConfigPathObtain/  deco=default  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def notmuchConfigPathObtain(
####+END:
        bpoId,
        envRelPath,
):

    runEnvBases = b.pattern.sameInstance(
        bpoRunBases.BpoRunEnvBases,
        bpoId,
        envRelPath,
    )
    varBase = runEnvBases.varBasePath_obtain()
    varControlBase = pathlib.Path(pathlib.PurePath(varBase, 'control'))
    varControlBase.mkdir(parents=True, exist_ok=True)
    return pathlib.Path(pathlib.PurePath(varControlBase, '_notmuch-config'))

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
