#!/bin/env python
# -*- coding: utf-8 -*-
"""\
* *[Summary]* :: An =ICM=: a beginning template for development of new ICMs.
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
** TODO [[elisp:(org-cycle)][| ]]  Current         :: Just getting started [[elisp:(org-cycle)][| ]]
**      [End-Of-Status]
"""

"""
*  [[elisp:(org-cycle)][| *ICM-INFO:* |]] :: Author, Copyleft and Version Information
"""
####+BEGIN: bx:cs:py:name :style "fileName"
csInfo['moduleName'] = "sivdApache2"
####+END:

####+BEGIN: bx:cs:py:version-timestamp :style "date"
csInfo['version'] = "202502114244"
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
*  This file:/bisos/git/bxRepos/bisos-pip/pals/py3/bisos/pals/sivdApache2.py :: [[elisp:(org-cycle)][| ]]
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

import collections
import os
import shutil
import invoke
# import tempfile

from bisos.basics import pyRunAs

from bisos.bpo import bpo
from bisos.pals import palsBpo
from bisos.pals import palsSis
from bisos.pals import repoProfile
from bisos.pals import palsBases

# from bisos.icm import shRun

####+BEGIN: bx:cs:py3:section :title "ICM Example Commands"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *ICM Example Commands*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "svcExamples" :cmndType "ICM-Ex-Cmnd"  :comment "FrameWrk: ICM Examples" :parsMand "bpoId sivd" :parsOpt "" :argsMin 0 :argsMax 999 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-ICM-Ex-Cmnd [[elisp:(outline-show-subtree+toggle)][||]] <<svcExamples>>  *FrameWrk: ICM Examples*  =verify= parsMand=bpoId sivd argsMax=999 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class svcExamples(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'sivd', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 999,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Mandatory Param
             sivd: typing.Optional[str]=None,  # Cs Mandatory Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:
        """FrameWrk: ICM Examples"""
        failed = b_io.eh.badOutcome
        callParamsDict = {'bpoId': bpoId, 'sivd': sivd, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        bpoId = csParam.mappedValue('bpoId', bpoId)
        sivd = csParam.mappedValue('sivd', sivd)
####+END:

        def cpsInit(): return collections.OrderedDict()
        def menuItem(verbosity): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity=verbosity) # 'little' or 'none'
        #def execLineEx(cmndStr): cs.examples.execInsert(execLine=cmndStr)

        oneBpo = bpoId
        oneSiRelPath = sivd


        logControler = b_io.log.Control()
        logControler.loggerSetLevel(20)

        cs.examples.myName(cs.G.icmMyName(), cs.G.icmMyFullName())

        cs.examples.commonBrief()

        bleep.examples_csBasic()

        cs.examples.menuChapter('*Full Actions*')

        cmndName = "fullUpdate" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['si'] = oneSiRelPath
        menuItem(verbosity='none')

        cmndName = "fullDelete" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['sivd'] = oneSiRelPath
        menuItem(verbosity='none')

        cmndName = "serviceDelete" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['sivd'] = oneSiRelPath
        menuItem(verbosity='none')

        cs.examples.menuChapter('*siBaseStart -- Initialize siBaseDir*')

        cmndName = "siBaseStart" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['sivd'] = oneSiRelPath
        menuItem(verbosity='none')

        cmndName = "sivdBaseUpdate" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['sivd'] = oneSiRelPath
        menuItem(verbosity='none')

        cs.examples.menuChapter('*dbaseInitialContent for Bystar Account*')

        cmndName = "palsBpoInfo" ; cmndArgs = "notyet" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['sivd'] = oneSiRelPath
        menuItem(verbosity='none')
        menuItem(verbosity='full')

        # ${G_myName} ${extraInfo} -p bpoId="${oneBystarAcct}" -p ss=${oneSr} -p dbase=banan -i imagesList | bueGimpManage.sh -h -v -n showRun -i scaleReplaceHeightTo 200
        # $( examplesSeperatorChapter "Access, Verification And Test" )
        # ${G_myName} ${extraInfo} -i  visitUrl

        return(cmndOutcome)


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "configExamples" :cmndType "ICM-Ex-Cmnd"  :comment "FrameWrk: ICM Examples" :parsMand "bpoId sivd" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-ICM-Ex-Cmnd [[elisp:(outline-show-subtree+toggle)][||]] <<configExamples>>  *FrameWrk: ICM Examples*  =verify= parsMand=bpoId sivd ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class configExamples(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'sivd', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Mandatory Param
             sivd: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:
        """FrameWrk: ICM Examples"""
        failed = b_io.eh.badOutcome
        callParamsDict = {'bpoId': bpoId, 'sivd': sivd, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        bpoId = csParam.mappedValue('bpoId', bpoId)
        sivd = csParam.mappedValue('sivd', sivd)
####+END:

        def cpsInit(): return collections.OrderedDict()
        def menuItem(verbosity): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity=verbosity) # 'little' or 'none'
        #def execLineEx(cmndStr): cs.examples.execInsert(execLine=cmndStr)

        oneBpo = bpoId
        oneSiRelPath = sivd

        # logControler = b_io.log.Control()
        # logControler.loggerSetLevel(20)

        cs.examples.myName(cs.G.icmMyName(), cs.G.icmMyFullName())

        cs.examples.commonBrief()

        bleep.examples_csBasic()

        cs.examples.menuChapter('*Service Config Actions*')

        cmndName = "sivd_configStdout" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['sivd'] = oneSiRelPath
        menuItem(verbosity='little')

        cmndName = "sivd_configUpdate" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['sivd'] = oneSiRelPath
        menuItem(verbosity='little')

        cmndName = "sivd_configVerify" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['sivd'] = oneSiRelPath
        menuItem(verbosity='little')

        cmndName = "sivd_configInfo" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['sivd'] = oneSiRelPath
        menuItem(verbosity='little')

        cmndName = "sivd_configDelete" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['sivd'] = oneSiRelPath
        menuItem(verbosity='little')

        return(cmndOutcome)


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "setupExamples" :cmndType "ICM-Ex-Cmnd"  :comment "FrameWrk: ICM Examples" :parsMand "bpoId sivd" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-ICM-Ex-Cmnd [[elisp:(outline-show-subtree+toggle)][||]] <<setupExamples>>  *FrameWrk: ICM Examples*  =verify= parsMand=bpoId sivd ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class setupExamples(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'sivd', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Mandatory Param
             sivd: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:
        """FrameWrk: ICM Examples"""
        failed = b_io.eh.badOutcome
        callParamsDict = {'bpoId': bpoId, 'sivd': sivd, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        bpoId = csParam.mappedValue('bpoId', bpoId)
        sivd = csParam.mappedValue('sivd', sivd)
####+END:

        def cpsInit(): return collections.OrderedDict()
        def menuItem(verbosity): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity=verbosity) # 'little' or 'none'
        #def execLineEx(cmndStr): cs.examples.execInsert(execLine=cmndStr)

        oneBpo = bpoId
        oneSiRelPath = sivd

        # logControler = b_io.log.Control()
        # logControler.loggerSetLevel(20)

        cs.examples.myName(cs.G.icmMyName(), cs.G.icmMyFullName())

        cs.examples.commonBrief()

        bleep.examples_csBasic()

        cs.examples.menuChapter('*Service Setup Actions*')

        cmndName = "basesUpdateSivd" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['sivd'] = oneSiRelPath
        menuItem(verbosity='none')

        return(cmndOutcome)



####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "digestedSvcsExamples" :cmndType "ICM-Ex-Cmnd"  :comment "FrameWrk: ICM Examples" :parsMand "" :parsOpt "bpoId" :argsMin 0 :argsMax 999 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-ICM-Ex-Cmnd [[elisp:(outline-show-subtree+toggle)][||]] <<digestedSvcsExamples>>  *FrameWrk: ICM Examples*  =verify= parsOpt=bpoId argsMax=999 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class digestedSvcsExamples(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'bpoId', ]
    cmndArgsLen = {'Min': 0, 'Max': 999,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Optional Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:
        """FrameWrk: ICM Examples"""
        failed = b_io.eh.badOutcome
        callParamsDict = {'bpoId': bpoId, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        bpoId = csParam.mappedValue('bpoId', bpoId)
####+END:

        def cpsInit(): return collections.OrderedDict()
        def menuItem(verbosity): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity=verbosity) # 'little' or 'none'
        # def execLineEx(cmndStr): cs.examples.execInsert(execLine=cmndStr)
        def extMenuItem(verbosity): cs.examples.cmndInsert(cmndName, cps, cmndArgs, icmName=icmExName, verbosity=verbosity) # 'little' or 'none'

        oneBpo = bpoId

        # logControler = b_io.log.Control()
        # logControler.loggerSetLevel(20)

        cs.examples.menuChapter('*Digest-SIs Example-Cmnds*')

        icmExName = "palsBpoManage.py" ; cmndName = "enabledSisInfo" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ;
        extMenuItem(verbosity='none')

        cs.examples.menuChapter('*PALS-SIs Example-Cmnds*')

        thisBpo = palsBpo.obtainBpo(oneBpo,)
        thisBpo.sis.sisDigest()

        icmExName = "palsSiPlone3.py" ; cmndName = "examples" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ;

        for eachSiPath in thisBpo.sis.svcInst_primary_enabled:
            cps['si'] = palsSis.siPathToSiId(oneBpo, eachSiPath,)
            extMenuItem(verbosity='none')

        cs.examples.menuChapter('*Existing PALS-VirDom-SIs Example-Cmnds*')

        cmndName = "configExamples" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ;

        for eachSivdPath in thisBpo.sis.svcInst_virDom_enabled:
            cps['sivd'] = palsSis.siPathToSiId(oneBpo, eachSivdPath,)
            menuItem(verbosity='none')

        cs.examples.menuChapter('*Missing PALS-VirDom-SIs Example-Cmnds*')

        cmndName = "setupExamples" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ;

        for eachSiPath in thisBpo.sis.svcInst_primary_enabled:
            eachSiId = palsSis.siPathToSiId(oneBpo, eachSiPath,)
            for eachSivdPath in thisBpo.sis.svcInst_virDom_enabled:
                eachSivdId = palsSis.siPathToSiId(oneBpo, eachSivdPath,)
                if eachSiId in eachSivdId:
                    # print(f"skipping over {eachSiId} in {eachSivdId}")
                    break
                else:
                    missingSivdId = "apache2/{eachSiId}".format(eachSiId=eachSiId)
                    cps['sivd'] = missingSivdId
                    menuItem(verbosity='none')


        return(cmndOutcome)


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
            argPosition="0&999",
            argName="actionPars",
            argChoices='any',
            argDescription="Rest of args for use by action"
        )

        return cmndArgsSpecDict


####+BEGIN: bx:cs:py3:section :title "ICM Commands"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *ICM Commands*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fullUpdate" :comment "" :parsMand "bpoId sivd" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fullUpdate>>  =verify= parsMand=bpoId sivd ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class fullUpdate(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'sivd', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Mandatory Param
             sivd: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'bpoId': bpoId, 'sivd': sivd, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        bpoId = csParam.mappedValue('bpoId', bpoId)
        sivd = csParam.mappedValue('sivd', sivd)
####+END:

        print("NOTYET -- To be implemented.")

        return cmndOutcome.set(
            opError=b.OpError.Success,  # type: ignore
            opResults=None,
        )


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "siBaseStart" :comment "" :parsMand "bpoId sivd" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<siBaseStart>>  =verify= parsMand=bpoId sivd ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class siBaseStart(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'sivd', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Mandatory Param
             sivd: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'bpoId': bpoId, 'sivd': sivd, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        bpoId = csParam.mappedValue('bpoId', bpoId)
        sivd = csParam.mappedValue('sivd', sivd)
####+END:

        print(f"""{bpoId} {sivd}""")
        primInstanceBaseDir = palsSis.sivd_primInstanceBaseDir(bpoId, sivd)
        if not os.path.exists(primInstanceBaseDir):
            b_io.eh.critical_usageError(f"primInstanceBaseDir={primInstanceBaseDir} should have existed.")
            return cmndOutcome.set(
                opError=icm.OpError.Failure,  # type: ignore
                opResults=None,
            )

        svcInstanceBaseDir = palsSis.sivd_instanceBaseDir(bpoId, sivd)
        if not os.path.exists(svcInstanceBaseDir):
            os.makedirs(svcInstanceBaseDir)

        print(f"svcInstanceBaseDir={svcInstanceBaseDir}")

        bsiAgentFile = os.path.join(svcInstanceBaseDir, "bsiAgent.sh")

        shutil.copyfile("/bisos/apps/defaults/pals/si/common/bsiAgent.sh", bsiAgentFile)

        siInfoBase = os.path.join(svcInstanceBaseDir, "siInfo")

        if not os.path.exists(siInfoBase): os.makedirs(siInfoBase)

        icm.b.fp.FileParamWriteTo(siInfoBase, 'svcCapability', __file__) # NOTYET, last part

        c = invoke.context.Context(config=None)

        with c.cd(svcInstanceBaseDir):
            c.run("bxtStartCommon.sh  -v -n showRun -i startObjectGen auxLeaf")


        c.run(f"ls -ld {primInstanceBaseDir}")

        return cmndOutcome.set(
            opError=b.OpError.Success,  # type: ignore
            opResults=None,
        )


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "sivdBaseUpdate" :comment "Place holder for logBase as root" :parsMand "bpoId sivd" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<sivdBaseUpdate>>  *Place holder for logBase as root*  =verify= parsMand=bpoId sivd ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class sivdBaseUpdate(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'sivd', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Mandatory Param
             sivd: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:
        """Place holder for logBase as root"""
        failed = b_io.eh.badOutcome
        callParamsDict = {'bpoId': bpoId, 'sivd': sivd, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        bpoId = csParam.mappedValue('bpoId', bpoId)
        sivd = csParam.mappedValue('sivd', sivd)
####+END:

        if palsBases.basesUpdateSivd(cmndOutcome=cmndOutcome).cmnd(
                bpoId=bpoId,
                sivd=sivd,
        ).isProblematic(): return(io.eh.badOutcome(cmndOutcome))

        return cmndOutcome.set(
            opError=b.OpError.Success,  # type: ignore
            opResults=None,
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
            argPosition="0",
            argName='dbaseName',
            argChoices='any',
            argDescription="Name of the geneweb database",
        )

        return cmndArgsSpecDict


####+BEGIN: bx:cs:py3:section :title "Class Definitions"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Class Definitions*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:class/decl :className "A2SivdRepo" :superClass "bpo.BpoRepo" :comment "Expected to be subclassed" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /A2SivdRepo/  superClass=bpo.BpoRepo =Expected to be subclassed=  [[elisp:(org-cycle)][| ]]
#+end_org """
class A2SivdRepo(bpo.BpoRepo):
####+END:
    """
** Refers to the entirety of bpo/apache2 repo.
"""
    def __init__(
            self,
            bpoId,
    ):
        super().__init__(bpoId)
        if not bpo.EffectiveBpos.givenBpoIdGetBpo(bpoId):
            b_io.eh.critical_usageError(f"Missing BPO for {bpoId}")
            return

    def repoBase(self,):
        return os.path.join(self.bpo.baseDir, "apache2") # type: ignore


####+BEGIN: b:py3:class/decl :className "AaSivdRepo_Apache2" :superClass "palsSis.SiRepo" :comment "Expected to be subclassed" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /AaSivdRepo_Apache2/  superClass=palsSis.SiRepo =Expected to be subclassed=  [[elisp:(org-cycle)][| ]]
#+end_org """
class AaSivdRepo_Apache2(palsSis.SiRepo):
####+END:
    """
** Abstraction of the base ByStar Portable Object
"""
    def __init__(
            self,
            bpoId,
            siPath,
    ):
        # print("eee  AaSivdRepo_Apache2")
        if palsSis.EffectiveSis.givenSiPathGetSiObjOrNone(bpoId, siPath,):
            b_io.eh.critical_usageError(f"Duplicate Attempt At Singleton Creation bpoId={bpoId}, siPath={siPath}")
        else:
            super().__init__(bpoId, siPath,) # includes: EffectiveSis.addSi(bpoId, siPath, self,)


    def obtainFromFPs(self,):
        pass


####+BEGIN: b:py3:class/decl :className "A2_Svc_Type" :superClass "palsSis.SiVirDomSvcType" :comment "Expected to be subclassed" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /A2_Svc_Type/  superClass=palsSis.SiVirDomSvcType =Expected to be subclassed=  [[elisp:(org-cycle)][| ]]
#+end_org """
class A2_Svc_Type(palsSis.SiVirDomSvcType):
####+END:
    """
** Abstraction of the base ByStar Portable Object
"""
    def __init__(
            self,
            bpoId,
            siPath,
    ):
        # print("fff  A2_Svc_Type")
        if palsSis.EffectiveSis.givenSiPathGetSiObjOrNone(bpoId, siPath,):
            b_io.eh.critical_usageError(f"Duplicate Attempt At Singleton Creation bpoId={bpoId}, siPath={siPath}")
        else:
            super().__init__(bpoId, siPath,) # includes: EffectiveSis.addSi(bpoId, siPath, self,)


####+BEGIN: b:py3:class/decl :className "A2_Svc_Inst" :superClass "palsSis.SiSvcInst" :comment "Expected to be subclassed" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /A2_Svc_Inst/  superClass=palsSis.SiSvcInst =Expected to be subclassed=  [[elisp:(org-cycle)][| ]]
#+end_org """
class A2_Svc_Inst(palsSis.SiSvcInst):
####+END:
    """
** Abstraction of the base ByStar Portable Object
"""
    def __init__(
            self,
            bpoId,
            siPath,
    ):
        # print("ggg  A2_Svc_Inst")
        if palsSis.EffectiveSis.givenSiPathGetSiObjOrNone(bpoId, siPath,):
            b_io.eh.critical_usageError(f"Duplicate Attempt At Singleton Creation bpoId={bpoId}, siPath={siPath}")
        else:
            super().__init__(bpoId, siPath,) # includes: EffectiveSis.addSi(bpoId, siPath, self,)

    def obtainFromFPs(self,):
        pass


####+BEGIN: b:py3:class/decl :className "A2_Plone3_Type" :superClass "A2_Svc_Type" :comment "Expected to be subclassed" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /A2_Plone3_Type/  superClass=A2_Svc_Type =Expected to be subclassed=  [[elisp:(org-cycle)][| ]]
#+end_org """
class A2_Plone3_Type(A2_Svc_Type):
####+END:
    """
** Abstraction of the base ByStar Portable Object
"""

    def __init__(
        self,
            bpoId,
            siPath,
    ):
        # print("hhh  A2_Plone3_Type")
        if palsSis.EffectiveSis. givenSiPathGetSiObjOrNone(bpoId, siPath,):
            b_io.eh.critical_usageError(f"Duplicate Attempt At Singleton Creation bpoId={bpoId}, siPath={siPath}")
        else:
            super().__init__(bpoId, siPath,) # includes: EffectiveSis.addSi(bpoId, siPath, self,)


    def obtainFromFPs(self,):
        pass

    def domainShow(self,):
        pass

    def stdout(self,):
        pass


####+BEGIN: b:py3:class/decl :className "A2_Plone3_Inst" :superClass "A2_Svc_Inst" :comment "Expected to be subclassed" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /A2_Plone3_Inst/  superClass=A2_Svc_Inst =Expected to be subclassed=  [[elisp:(org-cycle)][| ]]
#+end_org """
class A2_Plone3_Inst(A2_Svc_Inst):
####+END:
    """
** Abstraction of the base ByStar Portable Object
"""
    def __init__(
        self,
            bpoId,
            siPath,
    ):
        # print("iii  A2_Plone3_Inst")
        if palsSis.EffectiveSis. givenSiPathGetSiObjOrNone(bpoId, siPath,):
            b_io.eh.critical_usageError(f"Duplicate Attempt At Singleton Creation bpoId={bpoId}, siPath={siPath}")
        else:
            super().__init__(bpoId, siPath,) # includes: EffectiveSis.addSi(bpoId, siPath, self,)

    def obtainFromFPs(self,):
        pass

    def setVar(self, value,):
        self.setMyVar = value

    def domainShow(self,):
        pass

    def stdout(self,):
        pass




####+BEGIN: b:py3:class/decl :className "A2_Geneweb_VirDom" :superClass "A2_Svc_Type" :comment "Expected to be subclassed" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /A2_Geneweb_VirDom/  superClass=A2_Svc_Type =Expected to be subclassed=  [[elisp:(org-cycle)][| ]]
#+end_org """
class A2_Geneweb_VirDom(A2_Svc_Type):
####+END:
    """
** Abstraction of the base ByStar Portable Object
"""

    def __init__(
        self,
    ):
        pass

    def obtainFromFPs(self,):
        pass

    def domainShow(self,):
        pass

    def stdout(self,):
        pass



####+BEGIN: bx:cs:py3:section :title "Function Definitions"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Function Definitions*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:


####+BEGINNOT: bx:cs:python:func :funcName "listOfA2VirDomTypes" :funcType "anyOrNone" :retType "List" :deco "" :argsList ""
"""
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Func-anyOrNone :: /listOfA2VirDomSvcs/ retType=bool argsList=nil  [[elisp:(org-cycle)][| ]]
"""
def listOfA2VirDomTypes() -> typing.List:
####+END:
    return (
        [
            'plone3',
            'geneweb',
            'squirrelmail',
            'django',
            'gitweb',
            'gitolite',
            'gallery',
            'jekyll',
            'www',
        ]
    )


####+BEGIN: bx:cs:python:func :funcName "digestAtVirDomSvcProv" :funcType "anyOrNone" :retType "" :deco "" :argsList "bpoId siRepoBase"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /digestAtVirDomSvcProv/ retType= argsList=(bpoId siRepoBase)  [[elisp:(org-cycle)][| ]]
#+end_org """
def digestAtVirDomSvcProv(
    bpoId,
    siRepoBase,
):
####+END:
    """
** TODO: Needs to be commented, generalized and re-written.
    """
    b_io.tm.here("Incomplete")
    palsSis.createSiObj(bpoId, siRepoBase, AaSivdRepo_Apache2)

    thisBpo = palsBpo.obtainBpo(bpoId,)

    for each in listOfA2VirDomTypes():
            siRepoPath = os.path.join(siRepoBase, each)
            if os.path.isdir(siRepoPath):
                if each == "plone3" or each == "jekyll":
                    plone3SvcTypeObj = palsSis.createSiObj(bpoId, siRepoPath, A2_Plone3_Type)
                    digestAtVirDomSvcType(bpoId, siRepoPath, plone3SvcTypeObj)
                    thisBpo.sis.svcType_virDom_enabled.append(siRepoPath)

                b_io.tm.here(f"is {siRepoPath}")
            else:
                b_io.tm.here(f"is NOT {siRepoPath} -- skipped")


####+BEGIN: bx:cs:python:func :funcName "digestAtVirDomSvcType" :funcType "anyOrNone" :retType "" :deco "" :argsList "bpoId siRepoBase svcTypeObj"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /digestAtVirDomSvcType/ retType= argsList=(bpoId siRepoBase svcTypeObj)  [[elisp:(org-cycle)][| ]]
#+end_org """
def digestAtVirDomSvcType(
    bpoId,
    siRepoBase,
    svcTypeObj,
):
####+END:
    b_io.tm.here("Incomplete")

    #palsBpo.createSiObj(bpoId, siRepoBase, AaSivdRepo_Apache2) # BAD USAGE

    thisBpo = palsBpo.obtainBpo(bpoId,)

    for (_, dirNames, _,) in os.walk(siRepoBase):
        for each in dirNames:
            if each == "siInfo":
                continue
            # verify that it is a svcInstance
            siRepoPath = os.path.join(siRepoBase, each)
            digestVirDomSvcInstance(bpoId, siRepoPath, svcTypeObj, each)
            thisBpo.sis.svcInst_virDom_enabled.append(siRepoPath)
        break


####+BEGIN: bx:cs:python:func :funcName "digestVirDomSvcInstance" :funcType "anyOrNone" :retType "" :deco "" :argsList "bpoId siRepoBase svcTypeObj instanceName"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /digestVirDomSvcInstance/ retType= argsList=(bpoId siRepoBase svcTypeObj instanceName)  [[elisp:(org-cycle)][| ]]
#+end_org """
def digestVirDomSvcInstance(
    bpoId,
    siRepoBase,
    svcTypeObj,
    instanceName,
):
####+END:
    b_io.tm.here("Incomplete")

    #thisSi = palsSis.createSiObj(bpoId, siRepoBase, A2_Plone3_Inst)

    #thisSi.setVar(22)

    b_io.tm.here(f"bpoId={bpoId}, siRepoBase={siRepoBase}, svcTypeObj={svcTypeObj} instanceName={instanceName}")


####+BEGIN: bx:cs:python:func :funcName "sivdAsTag" :funcType "anyOrNone" :retType "" :deco "" :argsList "bpoId siRepoBase svcTypeObj instanceName"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /sivdAsTag/ retType= argsList=(bpoId siRepoBase svcTypeObj instanceName)  [[elisp:(org-cycle)][| ]]
#+end_org """
def sivdAsTag(
    bpoId,
    siRepoBase,
    svcTypeObj,
    instanceName,
):
####+END:
    virDomProvider = palsSis.si_svcName(sivd,)
    primarySvcName = palsSis.sivd_virDomSvcName(sivd,)
    primaryInstanceName = palsSis.si_instanceName(sivd,)

    b_io.tm.here(f"virDomProvider={virDomProvider} primarySvcName={primarySvcName} primaryInstanceName={primaryInstanceName}")

    if not virDomProvider in palsSis.PalsSis.svcProv_virDom_available():
        return b_io.eh.problem_usageError(
            f"Unexepected virDomProvider={virDomProvider}"
        )
    if not primarySvcName in palsSis.PalsSis.svcProv_primary_available():
        return b_io.eh.problem_usageError(
            f"Unexepected primarySvcName={primarySvcName}"
        )

    virDomProvTag=""
    if virDomProvider == "apache2":
        virDomProvTag = "a2"
    elif virDomProvider == "qmail":
        virDomProvTag = "qm"
    else:
        return b_io.eh.critical_oops("Implementation Error")

    capitalizedPrimarySvcName = primarySvcName[0].upper() + primarySvcName[1:]

    return f"""{virDomProvTag}{capitalizedPrimarySvcName}"""


####+BEGIN: b:py3:cs:func/typing :funcName "writeToFileAsRoot" :funcType "" :retType "" :deco "pyRunAs.User(\"root\")" :argsList ""  :comment "_ALERT_"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-       [[elisp:(outline-show-subtree+toggle)][||]] /writeToFileAsRoot/  _ALERT_ deco=pyRunAs.User("root")  [[elisp:(org-cycle)][| ]]
#+end_org """
@pyRunAs.User("root")
def writeToFileAsRoot(
####+END:
        destFilePath,
        inBytes,
):
    with open(destFilePath, "w") as thisFile:
        thisFile.write(inBytes + '\n')



####+BEGIN: bx:cs:py3:section :title "sivd_config Abstracted Facilities"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *sivd_config Abstracted Facilities*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "sivd_configStdout" :comment "" :parsMand "bpoId sivd" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<sivd_configStdout>>  =verify= parsMand=bpoId sivd ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class sivd_configStdout(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'sivd', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Mandatory Param
             sivd: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'bpoId': bpoId, 'sivd': sivd, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        bpoId = csParam.mappedValue('bpoId', bpoId)
        sivd = csParam.mappedValue('sivd', sivd)
####+END:
        virDomProvider = palsSis.si_svcName(sivd,)
        primarySvcName = palsSis.sivd_virDomSvcName(sivd,)
        primaryInstanceName = palsSis.si_instanceName(sivd,)

        b_io.tm.here(f"virDomProvider={virDomProvider} primarySvcName={primarySvcName} primaryInstanceName={primaryInstanceName}")

        if not virDomProvider in palsSis.PalsSis.svcProv_virDom_available():
            return icm.io.eh.problem_usageError(
                f"Unexepected virDomProvider={virDomProvider}"
            )
        if not primarySvcName in palsSis.PalsSis.svcProv_primary_available():
            return icm.io.eh.problem_usageError(
                f"Unexepected primarySvcName={primarySvcName}"
            )

        thisBpo = palsBpo.obtainBpo(bpoId,)
        #liveParamsInst = pattern.sameInstance(baseLiveTargets.PalsBase_LiveParams, bpoId)

        palsProfile = repoProfile.PalsRepo_Profile(bpoId)
        bpoFpsBaseInst = palsProfile.fps_baseMake()

        baseDomain = bpoFpsBaseInst.fps_getParam('baseDomain').parValueGet()
        #bystarType = bpoFpsBaseInst.fps_getParam('bystarType').parValueGet()
        #correspondingEntity = bpoFpsBaseInst.fps_getParam('correspondingEntity').parValueGet()

        siBaseDomain = "www.{baseDomain}".format(baseDomain=baseDomain)

        bpoBasePath = thisBpo.baseDir
        bpoSivdBasePath = palsSis.sivd_instanceBaseDir(
            bpoId,
            sivd,
        )

        configTemplateFuncName = f"{sivdAsTag(sivd,)}_configTemplate"

        if not configTemplateFuncName in globals():
            return b_io.eh.critical_oops(f"Implementation Error -- Missing {configTemplateFuncName}")

        # globals()[key] is equivalent of getattr for current module
        resStr = globals()[configTemplateFuncName]().format(
            baseDomain=baseDomain,
            siBaseDomain=siBaseDomain,
            bpoBasePath=bpoBasePath,
            bpoSivdBasePath=bpoSivdBasePath,
        )

        if rtInv.outs:
            print(resStr)

        cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=resStr
        )

        return resStr

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "sivd_configUpdate" :comment "" :parsMand "" :parsOpt "bpoId sivd" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<sivd_configUpdate>>  =verify= parsOpt=bpoId sivd ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class sivd_configUpdate(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'bpoId', 'sivd', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Optional Param
             sivd: typing.Optional[str]=None,  # Cs Optional Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'bpoId': bpoId, 'sivd': sivd, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        bpoId = csParam.mappedValue('bpoId', bpoId)
        sivd = csParam.mappedValue('sivd', sivd)
####+END:

        if not (resStr := sivd_configStdout(cmndOutcome=cmndOutcome).cmnd(
            interactive=False,
            bpoId=bpoId,
            sivd=sivd,
        )):  return(io.eh.badOutcome(cmndOutcome))


        palsProfile = repoProfile.PalsRepo_Profile(bpoId)
        bpoFpsBaseInst = palsProfile.fps_baseMake()

        baseDomain = bpoFpsBaseInst.fps_getParam('baseDomain').parValueGet()
        siBaseDomain = "www.{baseDomain}".format(baseDomain=baseDomain)

        configFilePath = sivd_configFilePath(siBaseDomain,)

        writeToFileAsRoot(configFilePath, resStr)

        if rtInv.outs:
            shRun.cmnds(f"""ls -l {configFilePath}""",
                       outcome=cmndOutcome,).log()

        shRun.sudoCmnds(f"""a2ensite {siBaseDomain}.conf""",
                        outcome=cmndOutcome,).log()

        shRun.sudoCmnds(f"""/etc/init.d/apache2 force-reload""",
                        outcome=cmndOutcome,).log()

        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=siBaseDomain,
        )


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "sivd_configVerify" :comment "" :parsMand "" :parsOpt "bpoId sivd" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<sivd_configVerify>>  =verify= parsOpt=bpoId sivd ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class sivd_configVerify(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'bpoId', 'sivd', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Optional Param
             sivd: typing.Optional[str]=None,  # Cs Optional Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'bpoId': bpoId, 'sivd': sivd, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        bpoId = csParam.mappedValue('bpoId', bpoId)
        sivd = csParam.mappedValue('sivd', sivd)
####+END:
        return


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "sivd_configInfo" :comment "" :parsMand "" :parsOpt "bpoId si" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<sivd_configInfo>>  =verify= parsOpt=bpoId si ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class sivd_configInfo(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'bpoId', 'si', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Optional Param
             si: typing.Optional[str]=None,  # Cs Optional Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'bpoId': bpoId, 'si': si, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        bpoId = csParam.mappedValue('bpoId', bpoId)
        si = csParam.mappedValue('si', si)
####+END:
        return


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "sivd_configDelete" :comment "" :parsMand "" :parsOpt "bpoId si" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<sivd_configDelete>>  =verify= parsOpt=bpoId si ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class sivd_configDelete(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'bpoId', 'si', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Optional Param
             si: typing.Optional[str]=None,  # Cs Optional Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'bpoId': bpoId, 'si': si, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        bpoId = csParam.mappedValue('bpoId', bpoId)
        si = csParam.mappedValue('si', si)
####+END:
        return


####+BEGIN: b:py3:cs:func/typing :funcName "sivd_configFilePath" :funcType "anyOrNone" :retType "bool" :deco "" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /sivd_configFilePath/   [[elisp:(org-cycle)][| ]]
#+end_org """
def sivd_configFilePath(
####+END:
        siBaseDomain,
):

    result = os.path.join(
        "/etc/apache2/sites-available",
        "{siBaseDomain}.conf".format(siBaseDomain=siBaseDomain),
    )
    return result

####+BEGIN: bx:cs:py3:section :title "Apache2-PrimaryService Specific Facilities"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Apache2-PrimaryService Specific Facilities*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: bx:cs:python:func :funcName "a2Plone3_configTemplate" :funcType "anyOrNone" :retType "bool" :deco "" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /a2Plone3_configTemplate/ retType=bool argsList=nil  [[elisp:(org-cycle)][| ]]
#+end_org """
def a2Plone3_configTemplate():
####+END:
    templateStr = """
# VirtualHost for {siBaseDomain} Generated by G_myName:G_thisFunc on dateTag -- Do Not Hand Edit

<VirtualHost *:80>
    ServerName  {siBaseDomain}
    ServerAlias {baseDomain}
    ServerAdmin webmaster@{baseDomain}

    RewriteEngine On
    RewriteRule ^/(.*) http://127.0.0.1:8080/VirtualHostBase/http/{siBaseDomain}:80/{baseDomain}/VirtualHostRoot/\$1 [L,P]

    DocumentRoot {bpoSivdBasePath}/var/htdocs
    #ScriptAlias /cgi-bin/ "{bpoSivdBasePath}/cgi-bin/"
    ErrorLog {bpoSivdBasePath}/log/error_log
    CustomLog {bpoSivdBasePath}/log/access_log common

        <Directory />
                Options FollowSymLinks
                AllowOverride All
        </Directory>
        <Directory {bpoSivdBasePath}/htdocs>
                Options Indexes FollowSymLinks MultiViews
                AllowOverride All
                Order allow,deny
                allow from all
        </Directory>

        <Proxy "*">
	        Order deny,allow
	        Allow from all
        </Proxy>
</VirtualHost>
"""
    return templateStr

####+BEGIN: bx:cs:python:func :funcName "a2Jekyll_configTemplate" :funcType "anyOrNone" :retType "bool" :deco "" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /a2Jekyll_configTemplate/ retType=bool argsList=nil  [[elisp:(org-cycle)][| ]]
#+end_org """
def a2Jekyll_configTemplate():
####+END:
    templateStr = """

# VirtualHost for {siBaseDomain} Generated by G_myName:G_thisFunc on dateTag -- Do Not Hand Edit

<VirtualHost *:80>
    ServerName  {siBaseDomain}
    ServerAlias {baseDomain}
    ServerAdmin webmaster@{baseDomain}

    DocumentRoot {bpoSivdBasePath}/var/site
    #ScriptAlias /cgi-bin/ "{bpoSivdBasePath}/cgi-bin/"
    ErrorLog {bpoSivdBasePath}/log/error_log
    CustomLog {bpoSivdBasePath}/log/access_log common

    <Directory />
        Require all granted
    </Directory>

    <Directory {bpoSivdBasePath}/var/site>
        Options +Indexes +FollowSymLinks +MultiViews
        AllowOverride All
        Order allow,deny
        allow from all
    </Directory>
</VirtualHost>
"""
    return templateStr


####+BEGIN: bx:cs:py3:section :title "Supporting Classes And Functions"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Supporting Classes And Functions*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:
"""
*       /Empty/  [[elisp:(org-cycle)][| ]]
"""

####+BEGIN: bx:cs:py3:section :title "Common/Generic Facilities -- Library Candidates"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Common/Generic Facilities -- Library Candidates*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:
"""
*       /Empty/  [[elisp:(org-cycle)][| ]]
"""

####+BEGIN: bx:cs:py3:section :title "Unused Facilities -- Temporary Junk Yard"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Unused Facilities -- Temporary Junk Yard*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:
"""
*       /Empty/  [[elisp:(org-cycle)][| ]]
"""

####+BEGIN: bx:cs:py3:section :title "End Of Editable Text"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *End Of Editable Text*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/bisos/apps/defaults/software/plusOrg/dblock/inserts/endOfFileControls.org"
#+STARTUP: showall
####+END:
