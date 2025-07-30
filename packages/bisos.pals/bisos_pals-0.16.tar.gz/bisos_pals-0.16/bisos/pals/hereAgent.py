# -*- coding: utf-8 -*-
"""\
* *[Summary]* :: An =ICM-Lib= for providing plone3 service instances.
"""

import typing


csInfo: typing.Dict[str, typing.Any] = { 'moduleDescription': """
*       [[elisp:(org-show-subtree)][|=]]  [[elisp:(org-cycle)][| *Description:* | ]]
**  [[elisp:(org-cycle)][| ]]  [Xref]          :: *[Related/Xrefs:]*  <<Xref-Here->>  -- External Documents  [[elisp:(org-cycle)][| ]]

**  [[elisp:(org-cycle)][| ]]   Model and Terminology                                      :Overview:
*** concept             -- Description of concept
**      [End-Of-Description]
""", }

csInfo['moduleUsage'] = """
*       [[elisp:(org-show-subtree)][|=]]  [[elisp:(org-cycle)][| *Usage:* | ]]
**      How-Tos:
**      Import it, include it in g_importedCmndsModules and include its params in g_paramsExtraSpecify.
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
csInfo['moduleName'] = "hereAgent"
####+END:

####+BEGIN: bx:cs:py:version-timestamp :style "date"
csInfo['version'] = "202502115709"
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
*  This file:/bisos/git/bxRepos/bisos-pip/pals/py3/bisos/pals/hereAgent.py :: [[elisp:(org-cycle)][| ]]
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

####+BEGIN: b:py3:cs:framework/imports :basedOn "classification"
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
import shutil
import invoke
# import tempfile


# from bisos.icm import clsMethod
# from bisos.icm import fp

from bisos.bpo import bpo
from bisos.pals import palsBpo
from bisos.pals import palsSis
from bisos.pals import palsThere

from bisos.pals import siJekyll

####+BEGIN: bx:cs:py3:section :title " /Imported Commands Modules/ "
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] * /Imported Commands Modules/ *  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

g_importedCmndsModules = [       # Enumerate modules from which CMNDs become invokable
    'bisos.csPlayer.bleep',
    'bisos.pals.hereAgent',
    'bisos.pals.palsBases',
    'bisos.pals.palsThere',
    'bisos.pals.siJekyll',
]


####+BEGIN: bx:cs:python:func :funcName "g_paramsExtraSpecify" :comment "FWrk: ArgsSpec" :funcType "FrameWrk" :retType "Void" :deco "" :argsList "parser"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-FrameWrk [[elisp:(outline-show-subtree+toggle)][||]] /g_paramsExtraSpecify/ =FWrk: ArgsSpec= retType=Void argsList=(parser)  [[elisp:(org-cycle)][| ]]
#+end_org """
def g_paramsExtraSpecify(
    parser,
):
####+END:
    """Module Specific Command Line Parameters.
    g_argsExtraSpecify is passed to G_main and is executed before argsSetup (can not be decorated)
    """
    G = cs.globalContext.get()
    csParams = cs.CmndParamDict()

    bleep.commonParamsSpecify(csParams)

    clsMethod.commonParamsSpecify(csParams)  # --cls, --method

    bpo.commonParamsSpecify(csParams)
    palsSis.commonParamsSpecify(csParams)

    palsThere.commonParamsSpecify(csParams)

    cs.argsparseBasedOnCsParams(parser, csParams)

    # So that it can be processed later as well.
    G.icmParamDictSet(csParams)

    return


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "examples" :cmndType "Cmnd-FWrk"  :comment "FrameWrk: ICM Examples" :parsMand "" :parsOpt "bpoId si" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-Cmnd-FWrk [[elisp:(outline-show-subtree+toggle)][||]] <<examples>>  *FrameWrk: ICM Examples*  =verify= parsOpt=bpoId si ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class examples(cs.Cmnd):
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
        """FrameWrk: ICM Examples"""
        failed = b_io.eh.badOutcome
        callParamsDict = {'bpoId': bpoId, 'si': si, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        bpoId = csParam.mappedValue('bpoId', bpoId)
        si = csParam.mappedValue('si', si)
####+END:

        def cpsInit(): return collections.OrderedDict()
        def menuItem(verbosity, **kwArgs): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity=verbosity, **kwArgs)
        # def execLineEx(cmndStr): cs.examples.execInsert(execLine=cmndStr)

        oneBpo = "pmi_ByD-100001"
        oneSiRelPath = "plone3/main"

        if bpoId: oneBpo = bpoId
        if si: oneSiRelPath = si

        cs.examples.myName(cs.G.icmMyName(), cs.G.icmMyFullName())

        cs.examples.commonBrief()

        bleep.examples_csBasic()

        cs.examples.menuChapter('*Examples For Specified Params*')

        cmndName = "examples" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['si'] = oneSiRelPath
        menuItem(verbosity='none', comment="# For specified bpoId and si")

        cs.examples.menuChapter('*Full Actions*')

        cmndName = "fullUpdate" ; cmndArgs = "" ; cps=cpsInit()
        menuItem(verbosity='little', comment="# empty place holder")

        palsThere.thereExamples().cmnd()

        absorbedPals = palsThere.PalsAbsorbed(os.getcwd())

        if absorbedPals.si_svcProv == 'plone3':
            from bisos.pals import siPlone3
            siPlone3.hereExamples().cmnd(bpoId=absorbedPals.bpoId,
                                        si=absorbedPals.si_instRelPath)
        elif absorbedPals.si_svcProv == 'geneweb':
            from bisos.pals import siGeneweb
            siGeneweb.hereExamples().cmnd(bpoId=absorbedPals.bpoId,
                                          si=absorbedPals.si_instRelPath)
        elif absorbedPals.si_svcProv == 'jekyll':
            from bisos.pals import siJekyll
            siJekyll.hereExamples().cmnd(bpoId=absorbedPals.bpoId,
                                         si=absorbedPals.si_instRelPath)
        elif absorbedPals.si_svcProv == 'apache2':
            from bisos.pals import siApache2
            siApache2.hereExamples().cmnd(bpoId=absorbedPals.bpoId,
                                         si=absorbedPals.si_instRelPath)
        else:
            b_io.eh.problem_notyet("")


        if absorbedPals.sivd_svcProv == 'sivd_apache2':
            from bisos.pals import sivdApache2
            sivdApache2.hereExamples().cmnd(bpoId=absorbedPals.bpoId,
                                        si=absorbedPals.si_instRelPath)
        elif absorbedPals.sivd_svcProv == 'sivd_qmail':
            from bisos.pals import sivdQmail
            sivdQmail.hereExamples().cmnd(bpoId=absorbedPals.bpoId,
                                          si=absorbedPals.si_instRelPath)
        else:
            b_io.eh.problem_notyet("")

        return(cmndOutcome)


####+BEGIN: bx:cs:py3:section :title "ICM Example Commands"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *ICM Example Commands*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "svcExamples" :cmndType "ICM-Ex-Cmnd"  :comment "FrameWrk: ICM Examples" :parsMand "bpoId si" :parsOpt "" :argsMin 0 :argsMax 999 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-ICM-Ex-Cmnd [[elisp:(outline-show-subtree+toggle)][||]] <<svcExamples>>  *FrameWrk: ICM Examples*  =verify= parsMand=bpoId si argsMax=999 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class svcExamples(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'si', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 999,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Mandatory Param
             si: typing.Optional[str]=None,  # Cs Mandatory Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:
        """FrameWrk: ICM Examples"""
        failed = b_io.eh.badOutcome
        callParamsDict = {'bpoId': bpoId, 'si': si, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        bpoId = csParam.mappedValue('bpoId', bpoId)
        si = csParam.mappedValue('si', si)
####+END:

        def cpsInit(): return collections.OrderedDict()
        def menuItem(verbosity, **kwArgs): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity=verbosity, **kwArgs)
        #def execLineEx(cmndStr): cs.examples.execInsert(execLine=cmndStr)

        oneBpo = bpoId
        oneSiRelPath = si

        cs.examples.myName(cs.G.icmMyName(), cs.G.icmMyFullName())

        cs.examples.commonBrief()

        bleep.examples_csBasic()

        cs.examples.menuChapter('*Full Actions*')

        cmndName = "fullUpdate" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['si'] = oneSiRelPath
        menuItem(verbosity='little', comment="NOTYET")

        return(cmndOutcome)


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "digestedSvcsExamples" :cmndType "ICM-Ex-Cmnd"  :comment "FrameWrk: ICM Examples" :parsMand "" :parsOpt "bpoId" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-ICM-Ex-Cmnd [[elisp:(outline-show-subtree+toggle)][||]] <<digestedSvcsExamples>>  *FrameWrk: ICM Examples*  =verify= parsOpt=bpoId ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class digestedSvcsExamples(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'bpoId', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Optional Param
    ) -> b.op.Outcome:
        """FrameWrk: ICM Examples"""
        failed = b_io.eh.badOutcome
        callParamsDict = {'bpoId': bpoId, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        bpoId = csParam.mappedValue('bpoId', bpoId)
####+END:

        def cpsInit(): return collections.OrderedDict()
        def menuItem(verbosity, **kwArgs): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity=verbosity, **kwArgs)
        # def execLineEx(cmndStr): cs.examples.execInsert(execLine=cmndStr)

        oneBpo = bpoId

        # logControler = b_io.log.Control()
        # logControler.loggerSetLevel(20)

        cs.examples.menuChapter('*Pals BPO-Info*')

        cmndArgs = "" ;  cps=cpsInit() ; cps['bpoId'] = oneBpo ;
        cmndName = "examples" ; menuItem(icmName="palsBpoManage.py",  verbosity='none')
        cmndName = "enabledSisInfo" ; menuItem(icmName="palsBpoManage.py",  verbosity='little')

        cs.examples.menuChapter('*Existing PALS-VirDom-SIs Example-Cmnds*')

        thisBpo = palsBpo.obtainBpo(oneBpo,)
        thisBpo.sis.sisDigest()

        cmndArgs = "" ; cps=cpsInit() ; cps['bpoId'] = oneBpo ;

        for eachSiPath in thisBpo.sis.svcInst_primary_enabled:
            eachSiId = palsSis.siPathToSiId(oneBpo, eachSiPath,)
            if "plone3" in eachSiId:
                cps['si'] = eachSiId
                cmndName = "configExamples" ; menuItem(verbosity='none', comment="# actions impacting plone site")
                cmndName = "setupExamples" ; menuItem(verbosity='none', comment="# create siBases, etc")

        return(cmndOutcome)


####+BEGIN: bx:cs:py3:section :title "ICM Commands"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *ICM Commands*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fullUpdate" :comment "" :parsMand "bpoId si" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fullUpdate>>  =verify= parsMand=bpoId si ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class fullUpdate(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'si', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Mandatory Param
             si: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'bpoId': bpoId, 'si': si, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        bpoId = csParam.mappedValue('bpoId', bpoId)
        si = csParam.mappedValue('si', si)
####+END:
        docStr = """
***** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Preformed fullActions, AcctCreat, NonInteractive, ReposCreate
***** TODO Not implemeted yet.
        """
        if self.docStrClassSet(docStr,): return cmndOutcome

        return icm.opSuccessAnNoResult(cmndOutcome)

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
