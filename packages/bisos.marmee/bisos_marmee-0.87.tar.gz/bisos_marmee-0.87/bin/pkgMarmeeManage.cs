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
** This File: /bisos/git/auth/bxRepos/bisos-pip/marmee/py3/bin/pkgMarmeManage.cs
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:py3:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['pkgMarmeManage'], }
csInfo['version'] = '202209284907'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'pkgMarmeManage-Panel.org'
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

from  bisos.platform import bxPlatformThis
from  bisos.platform import bxPlatformConfig

from bisos.marmee import marmeePkgThis

import os

""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] ~csuList emacs-list Specifications~  [[elisp:(blee:org:code-block/above-run)][ /Eval Below/ ]] [[elisp:(org-cycle)][| ]]
#+BEGIN_SRC emacs-lisp
(setq  b:py:cs:csuList
  (list
   "bisos.b.cs.ro"
   "bisos.csPlayer.bleep"
 ))
#+END_SRC
#+RESULTS:
| bisos.b.cs.ro | bisos.csPlayer.bleep |
#+end_org """

####+BEGIN: b:py3:cs:framework/csuListProc :pyImports t :csuImports t :csuParams t
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] =Process CSU List= with /2/ in csuList pyImports=t csuImports=t csuParams=t
#+end_org """

from bisos.b.cs import ro
from bisos.csPlayer import bleep


csuList = [ 'bisos.b.cs.ro', 'bisos.csPlayer.bleep', ]

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


####+BEGIN: bx:cs:python:func :funcName "canon_pythonPkgsSpec" :funcType "anyOrNone" :retType "bool" :deco "" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /canon_pythonPkgsSpec/ retType=bool argsList=nil  [[elisp:(org-cycle)][| ]]
#+end_org """
def canon_pythonPkgsSpec():
####+END:
    pkgs = collections.OrderedDict()
    pkgs["notmuch"] = None
    pkgs["flufl.bounce"] = "2.3"
    return pkgs

####+BEGIN: bx:cs:python:func :funcName "canon_linuxPkgsSpec" :funcType "anyOrNone" :retType "bool" :deco "" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /canon_linuxPkgsSpec/ retType=bool argsList=nil  [[elisp:(org-cycle)][| ]]
#+end_org """
def canon_linuxPkgsSpec():
####+END:
    pkgs = collections.OrderedDict()
    pkgs["offlineimap"] = None
    return pkgs


####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "CmndSvcs" :anchor ""  :extraInfo "Command Services Section"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _CmndSvcs_: |]]  Command Services Section  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "examples" :extent "verify" :ro "noCli" :comment "FrameWrk: CS-Main-Examples" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
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


####+BEGIN: bx:cs:python:cmnd:subSection :title "Dev And Testing"

####+END:

        cs.examples.menuChapter('*General Dev and Testing IIFs*')

        cmndName = "unitTest"

        cmndArgs = ""
        cps = cpsInit() ; # cps['icmsPkgName'] = icmsPkgName
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='little')
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='full')

        cs.examples.menuChapter('*BinsPreps*')

        cmndName="binsPreps" ; cps = cpsInit() ; cmndArgs = ""
        menuItem(verbosity='none')

        cmndName="binsPrepsCurInfo" ; cps = cpsInit() ; cmndArgs = ""
        menuItem(verbosity='none')

        cs.examples.menuSection('*Install ICMs Needed Linux Packages*')

        cmndName="canon_linuxPkgInstall" ; cps = cpsInit() ; cmndArgs = ""
        menuItem(verbosity='none')

        cs.examples.menuSection('*Install ICMs Needed Python Packages*')

        cmndName="canon_pythonPkgInstall" ; cps = cpsInit() ; cmndArgs = ""
        menuItem(verbosity='none')

        #
        # ICMs PKG Information
        #

        icmsPkgInfoBaseDir = marmeePkgThis.pkgBase_configDir()
        icmsPkgModuleBaseDir = marmeePkgThis.pkgBase_baseDir()

        #
        # icmsPkgLib needs to be absrobed. NOTYET. 20250212
        #

        # icmsPkgLib.examples_pkgInfoParsFull(
        #     icmsPkgNameSpecification(),
        #     icmsPkgInfoBaseDir=icmsPkgInfoBaseDir,
        #     icmsPkgModuleBaseDir=icmsPkgModuleBaseDir,
        #     icmsPkgControlBaseDir=icmsPkgControlBaseDirDefault(),
        #     icmsPkgRunBaseDir=icmsPkgRunBaseDirDefault(),
        # )

        b.ignore(ro.__doc__,)  # We are not using these modules, but they are auto imported.

        return(cmndOutcome)

####+BEGIN: bx:cs:py3:section :title "CS-Commands"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *CS-Commands*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: bx:cs:python:section :title "ICM Commands"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *ICM Commands*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:


####+BEGIN: bx:cs:python:section :title "Platform FPs"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Platform FPs*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:


configBaseDir = bxPlatformThis.pkgBase_configDir()

#platformConfigFpBase = bxPlatformConfig.configPkgInfoFpBaseDir_obtain(configBaseDir)
bisosUserName = bxPlatformConfig.bisosUserName_fpObtain(configBaseDir)
bisosGroupName = bxPlatformConfig.bisosGroupName_fpObtain(configBaseDir)
#platformControlBaseDir = bxPlatformConfig.platformControlBaseDir_fpObtain(configBaseDir)

#icm.unusedSuppressForEval(moduleDescription, moduleUsage, moduleStatus)

#b_io.ann.write(configBaseDir)
#b_io.ann.here(platformConfigFpBase)
#b_io.ann.here(bisosUserName)
#b_io.ann.here(bisosGroupName)
#b_io.ann.here(platformControlBaseDir)



"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || IIF       ::  icmsPkgNameSpecification    [[elisp:(org-cycle)][| ]]
"""
def icmsPkgNameSpecification():    return "marme.dev"

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || IIF       ::  icmsPkgControlBaseDirDefault    [[elisp:(org-cycle)][| ]]
"""
#def icmsPkgControlBaseDirDefault():    return os.path.abspath("../../marme.control")
#def icmsPkgControlBaseDirDefault():    return os.path.abspath("/de/bx/nne/mcm0/Sync/marme.control")
#def icmsPkgControlBaseDirDefault():    return os.path.abspath(os.path.join(platformControlBaseDir, "pkgs", "marme"))
def icmsPkgControlBaseDirDefault():    return os.path.abspath(os.path.join("NOTYET", "pkgs", "marme"))

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || IIF       ::  icmsPkgRunBaseDirDefault    [[elisp:(org-cycle)][| ]]
"""
def icmsPkgRunBaseDirDefault():    return os.path.expanduser("~/byStarRunEnv")

####+BEGIN: b:py3:cs:cmnd/classHead :modPrefix "new" :cmndName "binsPreps" :comment "" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<binsPreps>>  =verify= ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class binsPreps(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
    ) -> b.op.Outcome:

        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
####+END:
        pkgsList = canon_pythonPkgsSpec()
        for pkgName in pkgsList:
            pkgVersion = pkgsList[pkgName]
            canon_pythonPkgInstall(pkgName, pkgVersion)

        pkgsList = canon_linuxPkgsSpec()
        for pkgName in pkgsList:
            pkgVersion = pkgsList[pkgName]
            canon_linuxPkgInstall(pkgName, pkgVersion)


        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=None,
        )

####+BEGIN: b:py3:cs:cmnd/classHead :modPrefix "new" :cmndName "binsPrepsCurInfo" :comment "" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<binsPrepsCurInfo>>  =verify= ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class binsPrepsCurInfo(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
    ) -> b.op.Outcome:

        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
####+END:
        #G = cs.globalContext.get()
        #g_runArgs = G.icmRunArgsGet()

        #
        # Python Packages
        #
        pkgsList = canon_pythonPkgsSpec()
        for pkgName in pkgsList:
            # Not all packages ahve __version__ so this is not reliable
            #exec("import {pyModule}".format(pyModule=each))
            #exec("print {pyModule}.__version__".format(pyModule=each))

            installedVer = pythonPkg_versionGet(pkgName)

            installedLoc = pythonPkg_locationGet(pkgName)

            b_io.ann.write(
                "Python:: pkgName={pkgName} -- expectedVer={expectedVer} -- installedVer={installedVer} -- installedLoc={installedLoc}"
                .format(pkgName=pkgName,
                        expectedVer=pkgsList[pkgName],
                        installedVer=installedVer,
                        installedLoc=installedLoc,
                ))

        #
        # Linux Packages
        #
        pkgsList = canon_linuxPkgsSpec()
        for pkgName in pkgsList:

            installedVer = linuxPkg_versionGet(pkgName)

            b_io.ann.write(
                "Linux::  pkgName={pkgName} -- expectedVer={expectedVer} -- installedVer={installedVer}"
                .format(pkgName=pkgName,
                        expectedVer=pkgsList[pkgName],
                        installedVer=installedVer,
                ))

        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=None,
        )


####+BEGIN: bx:cs:python:section :title "Supporting Classes And Functions"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Supporting Classes And Functions*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:
"""
*       /Empty/  [[elisp:(org-cycle)][| ]]
"""


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || IIF       ::  canon_linuxPkgInstall    [[elisp:(org-cycle)][| ]]
"""
def canon_linuxPkgInstall(
        pkgName,
        pkgVersion,
):
    """
** Install a given Linux pkg based on its canonical name and version.
"""
    distroName = platform.linux_distribution()[0]

    if  distroName == "Ubuntu":
        return linuxPkgInstall_aptGet(pkgName, pkgVersion)
    elif distroName == "Redhat":
        return linuxPkgInstall_yum(pkgName, pkgVersion)
    elif distroName == "CentOS Linux":
        return linuxPkgInstall_yum(pkgName, pkgVersion)
    else:
        b_io.eh.problem_info("Unsupported Distribution == {}".format(distroName))
        return

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || IIF       ::  linuxPkgInstall_ubuntu    [[elisp:(org-cycle)][| ]]
"""
def linuxPkgInstall_aptGet(
        pkgName,
        pkgVersion,
):
    """
** Install a given linux pkg with apt-get based on its canonical name and version.
"""
    installedVersion = linuxPkg_versionGet(pkgName)
    if pkgVersion:
        if installedVersion == pkgVersion:
            b_io.ann.write("Linux::  {pkgName} ver={ver} (as expected) is already installed -- skipped".format(
                pkgName=pkgName, ver=installedVersion))
            return
        else:
            outcome = icm.subProc_bash(
                """echo NOTYET pip install {pkgName}=={pkgVersion}"""
                .format(pkgName=pkgName, pkgVersion=pkgVersion)
            ).log()
            if outcome.isProblematic(): return b_io.eh.badOutcome(outcome)
            resultStr = outcome.stdout.strip()
            b_io.ann.write(resultStr)
            return

    installedVersion = linuxPkg_versionGet(pkgName)
    if installedVersion:
        b_io.ann.write("Linux::  {pkgName} ver={ver} (as any) is already installed -- skipped".format(
            pkgName=pkgName, ver=installedVersion))
        return
    else:
        outcome = icm.subProc_bash(
            """sudo apt-get install {pkgName}"""
            .format(pkgName=pkgName)
        ).log()
        if outcome.isProblematic(): return b_io.eh.badOutcome(outcome)
        resultStr = outcome.stdout.strip()
        b_io.ann.write(resultStr)
        return


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || IIF       ::  linuxPkgInstall_redhat    [[elisp:(org-cycle)][| ]]
"""
def linuxPkgInstall_yum(
        pkgName,
        pkgVersion,
):
    """
** Install a given linux pkg with yum based on its canonical name and version.
"""

    outcome = icm.subProc_bash(
        """sudo yum install {pkgName}"""
        .format(pkgName=pkgName)
    ).log()
    if outcome.isProblematic(): return b_io.eh.badOutcome(outcome)
    resultStr = outcome.stdout.strip()
    b_io.ann.write(resultStr)
    return


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || IIF       ::  linuxPkg_versionGet    [[elisp:(org-cycle)][| ]]
"""
def linuxPkg_versionGet(
        pkgName,
):
    """
** Return version as string if Python pkgName is installed
** Return None if Python pkgName is not installed
"""
    dpkgQueryOpts = """dpkg-query --show --showformat='${db:Status-Status}\n'"""
    outcome = icm.subProc_bash(
        """{dpkgQueryOpts} {pkgName}"""
        .format(dpkgQueryOpts=dpkgQueryOpts, pkgName=pkgName)
    ).log()
    if outcome.isProblematic():
        b_io.eh.badOutcome(outcome)
        return None

    resultStr = outcome.stdout.strip()
    if resultStr == "":
        return None

    dpkgQueryOpts = """dpkg-query --show --showformat='${Version}\n'"""
    outcome = icm.subProc_bash(
        """{dpkgQueryOpts} {pkgName}"""
        .format(dpkgQueryOpts=dpkgQueryOpts, pkgName=pkgName)
    ).log()
    if outcome.isProblematic():
        b_io.eh.badOutcome(outcome)
        return None

    resultStr = outcome.stdout.strip()
    if resultStr == "":
        return None
    else:
        return resultStr



"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || IIF       ::  canon_pythonPkgInstall    [[elisp:(org-cycle)][| ]]
"""
def canon_pythonPkgInstall(
        pkgName,
        pkgVersion,
):
    """
** Install a given Python pkg based on its canonical name and version.
"""
    return pythonPkg_install_pip(pkgName, pkgVersion)

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || IIF       ::  pythonPkg_install_ubuntu    [[elisp:(org-cycle)][| ]]
"""
def pythonPkg_install_pip(
        pkgName,
        pkgVersion,
):
    """
** Install a given Python pkg based on its canonical name and version.
If version is specified,  the package is installed or updated to that version.
If version is None,
    if package is already installed no action is taken
    if package is not installed, the latest is installed
"""
    installedVersion = pythonPkg_versionGet(pkgName)
    if pkgVersion:
        if installedVersion == pkgVersion:
            b_io.ann.write("Python:: {pkgName} ver={ver} (as expected) is already installed -- skipped".format(
                pkgName=pkgName, ver=installedVersion))
            return
        else:
            outcome = icm.subProc_bash(
                """echo pip install {pkgName}=={pkgVersion}"""
                .format(pkgName=pkgName, pkgVersion=pkgVersion)
            ).log()
            if outcome.isProblematic(): return b_io.eh.badOutcome(outcome)
            resultStr = outcome.stdout.strip()
            b_io.ann.write(resultStr)
            return

    installedVersion = pythonPkg_versionGet(pkgName)
    if installedVersion:
        b_io.ann.write("Python:: {pkgName} ver={ver} (as any) is already installed -- skipped".format(
            pkgName=pkgName, ver=installedVersion))
        return
    else:
        outcome = icm.subProc_bash(
            """echo pip install {pkgName}"""
            .format(pkgName=pkgName)
        ).log()
        if outcome.isProblematic(): return b_io.eh.badOutcome(outcome)
        resultStr = outcome.stdout.strip()
        b_io.ann.write(resultStr)
        return


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || IIF       ::  pythonPkg_versionGet    [[elisp:(org-cycle)][| ]]
"""
def pythonPkg_versionGet(
        pkgName,
):
    """
** Return version as string if Python pkgName is installed
** Return None if Python pkgName is not installed
"""
    outcome = icm.subProc_bash(
        """pip show {pkg} | egrep '^Version' | cut -d ':' -f 2"""
        .format(pkg=pkgName)
    ).log()
    if outcome.isProblematic():
        b_io.eh.badOutcome(outcome)
        return None

    resultStr = outcome.stdout.strip()
    if resultStr == "":
        return None
    else:
        return resultStr

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || IIF       ::  pythonPkg_locationGet    [[elisp:(org-cycle)][| ]]
"""
def pythonPkg_locationGet(
        pkgName,
):
    """
** Return location as string if Python pkgName is installed
** Return None if Python pkgName is not installed
"""
    outcome = icm.subProc_bash(
        """pip show {pkg} | egrep '^Location' | cut -d ':' -f 2"""
        .format(pkg=pkgName)
    ).log()
    if outcome.isProblematic():
        b_io.eh.badOutcome(outcome)
        return None

    resultStr = outcome.stdout.strip()
    if resultStr == "":
        return None
    else:
        return resultStr





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
