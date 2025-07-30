# -*- coding: utf-8 -*-
"""\
* *[IcmLib]* :: Sets-up/updates pals, palsSivd and palsSi bases by creating links to var,tmp, etc.
"""

import typing

csInfo: typing.Dict[str, typing.Any] = { 'moduleDescription': ["""
*       [[elisp:(org-show-subtree)][|=]]  [[elisp:(org-cycle)][| *Description:* | ]]
**  [[elisp:(org-cycle)][| ]]  [Xref]          :: *[Related/Xrefs:]*  <<Xref-Here->>  -- External Documents  [[elisp:(org-cycle)][| ]]

**  [[elisp:(org-cycle)][| ]]   Model and Terminology                                      :Overview:
*** concept             -- Desctiption of concept
**      [End-Of-Description]
"""], }

csInfo['moduleUsage'] = """
*       [[elisp:(org-show-subtree)][|=]]  [[elisp:(org-cycle)][| *Usage:* | ]]

**      How-Tos:
**      [End-Of-Usage]
"""

csInfo['moduleStatus'] = """
*       [[elisp:(org-show-subtree)][|=]]  [[elisp:(org-cycle)][| *Status:* | ]]
**  [[elisp:(org-cycle)][| ]]  [Info]          :: *[Current-Info:]* Status/Maintenance -- General TODO List [[elisp:(org-cycle)][| ]]
** TODO [[elisp:(org-cycle)][| ]]  Current     :: For now it is an ICM. Turn it into ICM-Lib. [[elisp:(org-cycle)][| ]]
**      [End-Of-Status]
"""

"""
*  [[elisp:(org-cycle)][| *ICM-INFO:* |]] :: Author, Copyleft and Version Information
"""
####+BEGIN: bx:cs:py:name :style "fileName"
csInfo['moduleName'] = "palsThere"
####+END:

####+BEGIN: bx:cs:py:version-timestamp :style "date"
csInfo['version'] = "202502113103"
####+END:

####+BEGIN: bx:cs:py:status :status "Production"
csInfo['status']  = "Production"
####+END:

csInfo['credits'] = ""

####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/bisos/apps/defaults/update/sw/icm/py/csInfo-mbNedaGplByStar.py"
csInfo['authors'] = "[[http://mohsen.1.banan.byname.net][Mohsen Banan]]"
csInfo['copyright'] = "Copyright 2017, [[http://www.neda.com][Neda Communications, Inc.]]"
csInfo['licenses'] = "[[https://www.gnu.org/licenses/agpl-3.0.en.html][Affero GPL]]", "Libre-Halaal Services License", "Neda Commercial License"
csInfo['maintainers'] = "[[http://mohsen.1.banan.byname.net][Mohsen Banan]]"
csInfo['contacts'] = "[[http://mohsen.1.banan.byname.net/contact]]"
csInfo['partOf'] = "[[http://www.by-star.net][Libre-Halaal ByStar Digital Ecosystem]]"
####+END:

csInfo['panel'] = "{}-Panel.org".format(csInfo['moduleName'])
csInfo['groupingType'] = "IcmGroupingType-pkged"
csInfo['cmndParts'] = "IcmCmndParts[common] IcmCmndParts[param]"


####+BEGIN: bx:cs:python:top-of-file :partof "bystar" :copyleft "halaal+minimal"
""" #+begin_org
*  This file:/bisos/git/bxRepos/bisos-pip/pals/py3/bisos/pals/palsThere.py :: [[elisp:(org-cycle)][| ]]
 is part of The Libre-Halaal ByStar Digital Ecosystem. http://www.by-star.net
 *CopyLeft*  This Software is a Libre-Halaal Poly-Existential. See http://www.freeprotocols.org
 A Python Interactively Command Module (PyICM).
 Best Developed With COMEEGA-Emacs And Best Used With Blee-ICM-Players.
 *WARNING*: All edits wityhin Dynamic Blocks may be lost.
#+end_org """
####+END:

####+BEGIN: bx:cs:python:topControls :partof "bystar" :copyleft "halaal+minimal"
""" #+begin_org
*  [[elisp:(org-cycle)][|/Controls/| ]] :: [[elisp:(org-show-subtree)][|=]]  [[elisp:(show-all)][Show-All]]  [[elisp:(org-shifttab)][Overview]]  [[elisp:(progn (org-shifttab) (org-content))][Content]] | [[file:Panel.org][Panel]] | [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] | [[elisp:(bx:org:run-me)][Run]] | [[elisp:(bx:org:run-me-eml)][RunEml]] | [[elisp:(delete-other-windows)][(1)]] | [[elisp:(progn (save-buffer) (kill-buffer))][S&Q]]  [[elisp:(save-buffer)][Save]]  [[elisp:(kill-buffer)][Quit]] [[elisp:(org-cycle)][| ]]
** /Version Control/ ::  [[elisp:(call-interactively (quote cvs-update))][cvs-update]]  [[elisp:(vc-update)][vc-update]] | [[elisp:(bx:org:agenda:this-file-otherWin)][Agenda-List]]  [[elisp:(bx:org:todo:this-file-otherWin)][ToDo-List]]
#+end_org """
####+END:
####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/bisos/apps/defaults/software/plusOrg/dblock/inserts/pyWorkBench.org"
"""
*  /Python Workbench/ ::  [[elisp:(org-cycle)][| ]]  [[elisp:(python-check (format "/bisos/venv/py3/bisos3/bin/python -m pyclbr %s" (bx:buf-fname))))][pyclbr]] || [[elisp:(python-check (format "/bisos/venv/py3/bisos3/bin/python -m pydoc ./%s" (bx:buf-fname))))][pydoc]] || [[elisp:(python-check (format "/bisos/pipx/bin/pyflakes %s" (bx:buf-fname)))][pyflakes]] | [[elisp:(python-check (format "/bisos/pipx/bin/pychecker %s" (bx:buf-fname))))][pychecker (executes)]] | [[elisp:(python-check (format "/bisos/pipx/bin/pycodestyle %s" (bx:buf-fname))))][pycodestyle]] | [[elisp:(python-check (format "/bisos/pipx/bin/flake8 %s" (bx:buf-fname))))][flake8]] | [[elisp:(python-check (format "/bisos/pipx/bin/pylint %s" (bx:buf-fname))))][pylint]]  [[elisp:(org-cycle)][| ]]
"""
####+END:

####+BEGIN: bx:cs:python:icmItem :itemType "=Imports=" :itemTitle "*IMPORTS*"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  =Imports=  [[elisp:(outline-show-subtree+toggle)][||]] *IMPORTS*  [[elisp:(org-cycle)][| ]]
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


import os
# import pwd
# import grp
import collections
# import enum
#

#import traceback

import pathlib


# from bisos.platform import bxPlatformConfig
# from bisos.platform import bxPlatformThis

# from bisos.basics import pattern

from bisos.bpo import bpo
from bisos.pals import palsBpo
from bisos.pals import palsSis
# from bisos.icm import fpath

####+BEGIN: bx:cs:py3:section :title "BaseGet Functions"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *BaseGet Functions*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:func/args :funcName "palsBaseThere" :funcType "" :retType "" :deco "" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-A-       [[elisp:(outline-show-subtree+toggle)][||]] /palsBaseThere/ deco=  [[elisp:(org-cycle)][| ]]  [[elisp:(org-cycle)][| ]]
#+end_org """
def palsBaseThere():
####+END:
    print("PROBLEM NOTYET. Look for this in old code.")

####+BEGIN: bx:dblock:python:func :funcName "commonParamsSpecify" :funcType "ParSpec" :retType "" :deco "" :argsList "csParams"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-ParSpec  [[elisp:(outline-show-subtree+toggle)][||]] /commonParamsSpecify/ retType= argsList=(csParams)  [[elisp:(org-cycle)][| ]]
#+end_org """
def commonParamsSpecify(
    csParams,
):
####+END:
    csParams.parDictAdd(
        parName='there',
        parDescription="Path to There",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        # parScope=icm.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--there',
    )


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "thereExamples" :cmndType "Cmnd-FWrk"  :comment "FrameWrk: ICM Examples" :parsMand "" :parsOpt "there" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-Cmnd-FWrk [[elisp:(outline-show-subtree+toggle)][||]] <<thereExamples>>  *FrameWrk: ICM Examples*  =verify= parsOpt=there ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class thereExamples(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'there', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             there: typing.Optional[str]=None,  # Cs Optional Param
    ) -> b.op.Outcome:
        """FrameWrk: ICM Examples"""
        failed = b_io.eh.badOutcome
        callParamsDict = {'there': there, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        there = csParam.mappedValue('there', there)
####+END:
        def cpsInit(): return collections.OrderedDict()
        def menuItem(verbosity, **kwArgs): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity=verbosity, **kwArgs)
        # def execLineEx(cmndStr): cs.examples.execInsert(execLine=cmndStr)

        therePath = os.getcwd()
        if there: therePath = there

        cs.examples.menuChapter('*PalsAbsorb There*')

        cmndName = "palsAbsorbHere" ; cmndArgs = "" ; cps=cpsInit() ; menuItem(verbosity='little')
        cmndArgs = "palsId" ; menuItem(verbosity='little')

        cmndName = "palsAbsorbThere" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['there'] = therePath ; menuItem(verbosity='little')
        cmndArgs = "instRelPath" ; menuItem(verbosity='little')

        return(cmndOutcome)




####+BEGIN: bx:cs:py3:section :title "BaseGet Classes"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *BaseGet Classes*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:



####+BEGIN: b:py3:class/decl :className "BpoAbsorbed" :superClass "" :comment "Is super class for PalsAbsorbed" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /BpoAbsorbed/  superClass=object =Is super class for PalsAbsorbed=  [[elisp:(org-cycle)][| ]]
#+end_org """
class BpoAbsorbed(object):
####+END:
    """
** Based on therePath, corresponding Bpo is identified and absorbed.
*** TODO Common bpo repositories need to be analyzed and absorbed as well.
"""
    def __init__(
            self,
            therePath,
    ):
        pathList = pathlib.Path(therePath).parts

        if len(pathList) < 5:
            b_io.eh.problem_usageError(f"bad input: {therePath}")
            raise ValueError
        if pathList[0] != "/":
            b_io.eh.problem_usageError(f"bad input: {therePath}")
            raise ValueError
        if pathList[1] != "bxo":
            b_io.eh.problem_usageError(f"bad input: {therePath}")
            raise ValueError
        if pathList[2] != "r3":
            b_io.eh.problem_usageError(f"bad input: {therePath}")
            raise ValueError
        if pathList[3] != "iso":
            b_io.eh.problem_usageError(f"bad input: {therePath}")
            raise ValueError

        self._bpoId = pathList[4]
        self._bpoHome = os.path.expanduser(f"~{self._bpoId}")

    @property
    def bpoId(self) -> str:
        return self._bpoId

    @property
    def bpoHome(self) -> str:
        return self._bpoHome


####+BEGIN: b:py3:class/decl :className "PalsAbsorbed" :superClass "BpoAbsorbed" :comment "Absorbes si, sivd, etc." :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /PalsAbsorbed/  superClass=BpoAbsorbed =Absorbes si, sivd, etc.=  [[elisp:(org-cycle)][| ]]
#+end_org """
class PalsAbsorbed(BpoAbsorbed):
####+END:
    """
** Based on therePath, corresponding Bpo is identified and absorbed.
*** TODO Common bpo repositories need to be analyzed and absorbed as well.
"""
    def __init__(
            self,
            therePath,
    ):
        super().__init__(therePath)

        self.siEffective = None
        self.sivdEffective = None

        pathList = pathlib.Path(therePath).parts

        # >= 5
        self._palsId = self.bpoId
        self._palsHome = self.bpoHome

        self._si_svcProv = ""
        self._si_svcInst = ""

        self._sivd_svcProv = ""
        self._sivd_svcType = ""
        self._sivd_svcInst = ""

        self._liveParams = ""

        self._si_instRelPath = ""
        self._sivd_instRelPath = ""

        if len(pathList) > 5:
            sansSi = pathList[5].removeprefix("si_")
            sansSivd = pathList[5].removeprefix("sivd_")

            if sansSi in palsSis.PalsSis.svcProv_primary_available():
                self._si_svcProv = sansSi
            elif sansSivd in palsSis.PalsSis.svcProv_virDom_available():
                self._sivd_SvcProv = sansSivd
            elif pathList[5] == "liveParams":
                self._liveParams = pathList[5]
            else:
                b_io.eh.problem_usageError(f"bad input: {therePath}")
                return

        if len(pathList) > 6:
            if self._si_svcProv:
                self._si_svcInst = pathList[6]
                self._si_instRelPath = f"{self._si_svcProv}/{pathList[6]}"
            elif self._sivd_svcProv:
                self._sivd_svcType = pathList[6]
            else:
                b_io.eh.problem_usageError(f"bad input: {therePath}")
                return

        if len(pathList) > 7:
            if self._sivd_svcProv:
                self._sivd_svcInst = pathList[7]
                self._sivd_instRelPath = f"{pathList[5]}/{pathList[6]}/{pathList[7]}"
            else:
                b_io.eh.problem_usageError(f"bad input: {therePath}")
                return

    @property
    def palsId(self) -> str:
        return self._palsId

    @property
    def palsHome(self) -> str:
        return self._palsHome

    @property
    def si_svcProv(self) -> str:
        return self._si_svcProv

    @property
    def si_svcInst(self) -> str:
        return self._si_svcInst

    @property
    def si_instRelPath(self) -> str:
        return self._si_instRelPath

    @property
    def sivd_svcProv(self) -> str:
        return self._sivd_svcProv

    @property
    def sivd_svcType(self) -> str:
        return self._sivd_svcType

    @property
    def sivd_svcInst(self) -> str:
        return self._sivd_svcInst

    @property
    def sivd_instRelPath(self) -> str:
        return self._sivd_instRelPath

    def getAttrByName(self,
                      name: str,
                      ):
        if name == 'palsId':
            return self.palsId
        if name == 'instRelPath':
            if self.sivd_instRelPath:
                return self.sivd_instRelPath
            elif self.si_instRelPath:
                return self.si_instRelPath
            else:
                return  "Missing instRelPath"

        else:
            return "Unknown"


####+BEGIN: bx:cs:py3:section :title "ICM Commands"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *ICM Commands*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "palsAbsorbThere" :parsMand "there" :parsOpt "" :argsMin 0 :argsMax 5 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<palsAbsorbThere>>  =verify= parsMand=there argsMax=5 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class palsAbsorbThere(cs.Cmnd):
    cmndParamsMandatory = [ 'there', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 5,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             there: typing.Optional[str]=None,  # Cs Mandatory Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'there': there, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        there = csParam.mappedValue('there', there)
####+END:
        docStr = """
***** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Preformed fullActions, AcctCreat, NonInteractive, ReposCreate
***** TODO Not implemeted yet.
        """
        if self.docStrClassSet(docStr,): return cmndOutcome

        absorbedPals = PalsAbsorbed(there)

        cmndArgs = list(self.cmndArgsGet("0&5", cmndArgsSpecDict, argsList))  # type: ignore
        #

        if len(cmndArgs):
            if cmndArgs[0] == "all":
                cmndArgsSpec = cmndArgsSpecDict.argPositionFind("0&5")
                argChoices = cmndArgsSpec.argChoicesGet()
                argChoices.pop(0)
                cmndArgs= argChoices
        if len(cmndArgs) <= 2:
            for each in cmndArgs:
                print(f"""{absorbedPals.getAttrByName(each,)}""")
        else:
            print(f"palsId={absorbedPals.palsId}")
            print(f"sivd_svcProv={absorbedPals.sivd_svcProv}")
            print(f"si_svcProv={absorbedPals.si_svcProv}")
            print(f"si_svcInst={absorbedPals.si_svcInst}")
            print(f"si_instRelPath={absorbedPals.si_instRelPath}")

        return b.op.successAndNoResult(cmndOutcome)


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
            argPosition="0&5",
            argName="cmndArgs",
            argDefault='all',
            argChoices=['all', 'palsId', 'instRelPath', 'other',],
            argDescription="Rest of args for use by action"
        )

        return cmndArgsSpecDict


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "palsAbsorbHere" :comment "" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 5 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<palsAbsorbHere>>  =verify= argsMax=5 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class palsAbsorbHere(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 5,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
####+END:
        docStr = """
***** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Preformed fullActions, AcctCreat, NonInteractive, ReposCreate
***** TODO Not implemeted yet.
        """
        if self.docStrClassSet(docStr,): return cmndOutcome

        cmndOutcome = palsAbsorbThere().cmnd(
             there=os.getcwd(),
             argsList=effectiveArgsList,
        )

        return b.op.successAnNoResult(cmndOutcome)

####+BEGIN: bx:cs:py3:section :title "End Of Editable Text"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *End Of Editable Text*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/bisos/apps/defaults/software/plusOrg/dblock/inserts/endOfFileControls.org"
#+STARTUP: showall
####+END:
