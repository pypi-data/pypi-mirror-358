# -*- coding: utf-8 -*-
"""\
* *[IcmLib]* :: For providing jekyll service instances.
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
csInfo['moduleName'] = "siJekyll"
####+END:

####+BEGIN: bx:cs:py:version-timestamp :style "date"
csInfo['version'] = "202502113807"
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
*  This file:/bisos/git/bxRepos/bisos-pip/pals/py3/bisos/pals/siJekyll.py :: [[elisp:(org-cycle)][| ]]
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


# from bisos.icm import clsMethod
# from bisos.icm import fp

from bisos.bpo import bpo
from bisos.pals import palsBpo
from bisos.pals import palsSis
from bisos.pals import palsBases

from bisos import b


####+BEGIN: bx:cs:python:icmItem :itemType "=ImportICMs=" :itemTitle "*Imported Commands Modules*"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  =ImportICMs= [[elisp:(outline-show-subtree+toggle)][||]] *Imported Commands Modules*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

g_importedCmndsModules = [       # Enumerate modules from which CMNDs become invokable
    'bisos.csPlayer.bleep',
    'bisos.pals.siJekyll',
    'bisos.pals.palsBases',
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
        docStr = """\
***** [[elisp:(org-cycle)][| *CmndDesc:* | ]] ICM examples, all on one place.
        """
        if self.docStrClassSet(docStr,): return cmndOutcome

        def cpsInit(): return collections.OrderedDict()
        def menuItem(verbosity, **kwArgs): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity=verbosity, **kwArgs)
        # def execLineEx(cmndStr): cs.examples.execInsert(execLine=cmndStr)

        oneBpo = "pmi_ByD-100001"
        oneSiRelPath = "jekyll/main"

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

        cmndName = "fullUpdate" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['si'] = oneSiRelPath
        menuItem(verbosity='little', comment="# empty place holder")

        cs.examples.menuChapter('*siBaseStart -- Initialize siBaseDir*')

        cmndName = "siBaseAssemble" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['si'] = oneSiRelPath
        menuItem(verbosity='little', comment="# needs more testing")

        cmndName = "siBaseUpdate" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['si'] = oneSiRelPath
        menuItem(verbosity='little', comment="# siBaseAssemble + palsBases.basesUpdateSi (logs,data)")

        cs.examples.menuChapter('*Jekyll Site Initializations*')

        cmndName = "siInvoke" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['si'] = oneSiRelPath ; cps['method'] = 'jekyllSiteAdd'
        menuItem(verbosity='little', comment="# general purpose testing")
        menuItem(verbosity='full', comment="# general purpose testing")

        digestedSvcsExamples().cmnd(bpoId=oneBpo,)

        return(cmndOutcome)

####+BEGIN: bx:cs:py3:section :title "ICM Example Commands"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *ICM Example Commands*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "svcExamples" :cmndType "ICM-Ex-Cmnd"  :comment "Full Action Examples" :parsMand "bpoId si" :parsOpt "" :argsMin 0 :argsMax 999 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-ICM-Ex-Cmnd [[elisp:(outline-show-subtree+toggle)][||]] <<svcExamples>>  *Full Action Examples*  =verify= parsMand=bpoId si argsMax=999 ro=cli   [[elisp:(org-cycle)][| ]]
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
        """Full Action Examples"""
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

        cmndName = "fullDelete" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['si'] = oneSiRelPath
        menuItem(verbosity='little', comment="NOTYET")

        cmndName = "serviceDelete" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['si'] = oneSiRelPath
        menuItem(verbosity='little', comment="NOTYET")

        return(cmndOutcome)


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "configExamples" :cmndType "ICM-Ex-Cmnd"  :comment "configUpdate etc" :parsMand "bpoId si" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-ICM-Ex-Cmnd [[elisp:(outline-show-subtree+toggle)][||]] <<configExamples>>  *configUpdate etc*  =verify= parsMand=bpoId si ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class configExamples(cs.Cmnd):
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
        """configUpdate etc"""
        failed = b_io.eh.badOutcome
        callParamsDict = {'bpoId': bpoId, 'si': si, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
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

        cs.examples.menuChapter('*Service Config Actions*')

        cmndName = "jekyll_configUpdate" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['si'] = oneSiRelPath
        menuItem(verbosity='little', comment="# Place Holder")

        return(cmndOutcome)


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "setupExamples" :cmndType "ICM-Ex-Cmnd"  :comment "baseUpdate, etc" :parsMand "bpoId si" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-ICM-Ex-Cmnd [[elisp:(outline-show-subtree+toggle)][||]] <<setupExamples>>  *baseUpdate, etc*  =verify= parsMand=bpoId si ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class setupExamples(cs.Cmnd):
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
        """baseUpdate, etc"""
        failed = b_io.eh.badOutcome
        callParamsDict = {'bpoId': bpoId, 'si': si, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        bpoId = csParam.mappedValue('bpoId', bpoId)
        si = csParam.mappedValue('si', si)
####+END:

        def cpsInit(): return collections.OrderedDict()
        def menuItem(verbosity, **kwArgs): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity=verbosity, **kwArgs)
        #def execLineEx(cmndStr): cs.examples.execInsert(execLine=cmndStr)

        oneBpo = bpoId
        oneSiRelPath = si

        # logControler = b_io.log.Control()
        # logControler.loggerSetLevel(20)

        cs.examples.myName(cs.G.icmMyName(), cs.G.icmMyFullName())

        cs.examples.commonBrief()

        bleep.examples_csBasic()

        cs.examples.menuChapter('*Service Setup Actions*')

        cmndName = "basesUpdateSi" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['si'] = oneSiRelPath
        menuItem(verbosity='little', comment="# to be tested")

        return(cmndOutcome)


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "hereExamples" :cmndType "ICM-Ex-Cmnd"  :comment "baseUpdate, etc" :parsMand "bpoId si" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-ICM-Ex-Cmnd [[elisp:(outline-show-subtree+toggle)][||]] <<hereExamples>>  *baseUpdate, etc*  =verify= parsMand=bpoId si ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class hereExamples(cs.Cmnd):
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
        """baseUpdate, etc"""
        failed = b_io.eh.badOutcome
        callParamsDict = {'bpoId': bpoId, 'si': si, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        bpoId = csParam.mappedValue('bpoId', bpoId)
        si = csParam.mappedValue('si', si)
####+END:
        docStr = """
***** [[elisp:(org-cycle)][| *CmndDesc:* | ]] To be inserted in hereAgent.py menus.
        """
        if self.docStrClassSet(docStr,): return cmndOutcome

        def cpsInit(): return collections.OrderedDict()
        def menuItem(verbosity, **kwArgs): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity=verbosity, **kwArgs)
        #def execLineEx(cmndStr): cs.examples.execInsert(execLine=cmndStr)

        oneBpo = bpoId
        oneSiRelPath = si

        cs.examples.menuChapter('*SiJekyll Here Actions*')

        cmndName = "siJekyll_siteDumpAndTriggers" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['si'] = oneSiRelPath
        menuItem(verbosity='little', comment="# needs to be followed by triggers")

        cmndName = "siJekyll_siteDump" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['si'] = oneSiRelPath
        menuItem(verbosity='little', comment="# needs to be followed by triggers")

        cmndName = "siJekyll_siteTriggers" ; cmndArgs = "" ;
        cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['si'] = oneSiRelPath
        menuItem(verbosity='little', comment="# args ro be added")


        return(cmndOutcome)



####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "digestedSvcsExamples" :cmndType "ICM-Ex-Cmnd"  :comment "Examples lines for each digested svc" :parsMand "" :parsOpt "bpoId" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-ICM-Ex-Cmnd [[elisp:(outline-show-subtree+toggle)][||]] <<digestedSvcsExamples>>  *Examples lines for each digested svc*  =verify= parsOpt=bpoId ro=cli   [[elisp:(org-cycle)][| ]]
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
        """Examples lines for each digested svc"""
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
            if "jekyll" in eachSiId:
                cps['si'] = eachSiId
                cmndName = "configExamples" ; menuItem(verbosity='none', comment="# actions impacting plone site")
                cmndName = "setupExamples" ; menuItem(verbosity='none', comment="# create siBases, etc")

        return(cmndOutcome)


####+BEGIN: bx:cs:py3:section :title "ICM Commands"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *ICM Commands*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fullUpdate" :comment "Place Holder" :parsMand "bpoId si" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fullUpdate>>  *Place Holder*  =verify= parsMand=bpoId si ro=cli   [[elisp:(org-cycle)][| ]]
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
        """Place Holder"""
        failed = b_io.eh.badOutcome
        callParamsDict = {'bpoId': bpoId, 'si': si, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        bpoId = csParam.mappedValue('bpoId', bpoId)
        si = csParam.mappedValue('si', si)
####+END:

        return cmndOutcome.set(
            opError=b.OpError.Success,  # type: ignore
            opResults=None,
        )


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "siBaseAssemble" :comment "Assemble a base for si" :parsMand "bpoId si" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<siBaseAssemble>>  *Assemble a base for si*  =verify= parsMand=bpoId si ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class siBaseAssemble(cs.Cmnd):
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
        """Assemble a base for si"""
        failed = b_io.eh.badOutcome
        callParamsDict = {'bpoId': bpoId, 'si': si, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        bpoId = csParam.mappedValue('bpoId', bpoId)
        si = csParam.mappedValue('si', si)
####+END:
        docStr = """\
***** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Initial action that creates the siRepo
        """
        if self.docStrClassSet(docStr,): return cmndOutcome

        thisBpo = palsBpo.obtainBpo(bpoId,)
        if not thisBpo:
            return cmndOutcome.set(opError=io.eh.critical_usageError(f"missing bpoId={bpoId}"))

        svcProvBaseDir = palsSis.si_svcBaseDir(bpoId, si)
        if not os.path.exists(svcProvBaseDir):
            os.makedirs(svcProvBaseDir)
            # NOTYET, addition of siInfo for svcProvider
        else:
            b_io.tm.here(f"svcProvBaseDir={svcProvBaseDir} exists, creation skipped.")

        svcInstanceBaseDir = palsSis.si_instanceBaseDir(bpoId, si)
        if not os.path.exists(svcInstanceBaseDir):
            os.makedirs(svcInstanceBaseDir)
        else:
            b_io.tm.here(f"svcInstanceBaseDir={svcInstanceBaseDir} exists, creation skipped.")

        b_io.tm.here(f"svcInstanceBaseDir={svcInstanceBaseDir} being updated.")

        thisBpo.sis.sisDigest()

        siPath = palsSis.siIdToSiPath(bpoId, si)
        thisSi = palsSis.EffectiveSis.givenSiPathFindSiObj(bpoId, siPath,)

        thisSi.assemble() # type: ignore

        return icm.opSuccessAnNoResult(cmndOutcome)


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "siBaseUpdate" :comment "Place holder for logBase as root" :parsMand "bpoId si" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<siBaseUpdate>>  *Place holder for logBase as root*  =verify= parsMand=bpoId si ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class siBaseUpdate(cs.Cmnd):
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
        """Place holder for logBase as root"""
        failed = b_io.eh.badOutcome
        callParamsDict = {'bpoId': bpoId, 'si': si, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        bpoId = csParam.mappedValue('bpoId', bpoId)
        si = csParam.mappedValue('si', si)
####+END:
        docStr = """\
***** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Uses palsBases.basesUpdateSi to create var,log, bases.
        """
        if self.docStrClassSet(docStr,): return cmndOutcome

        if siBaseAssemble(cmndOutcome=cmndOutcome).cmnd(
                bpoId=bpoId,
                si=si,
        ).isProblematic(): return(io.eh.badOutcome(cmndOutcome))

        if palsBases.basesUpdateSi(cmndOutcome=cmndOutcome).cmnd(
                bpoId=bpoId,
                si=si,
        ).isProblematic(): return(io.eh.badOutcome(cmndOutcome))

        return b.op.successAnNoResult(cmndOutcome)


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "siJekyll_siteCreate" :comment "" :parsMand "bpoId si" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<siJekyll_siteCreate>>  =verify= parsMand=bpoId si ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class siJekyll_siteCreate(cs.Cmnd):
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
        docStr = """\
***** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Uses palsBases.basesUpdateSi to create var,log, bases.
        """
        if self.docStrClassSet(docStr,): return cmndOutcome

        jekyllInstance = Jekyll_Inst(bpoId, si)

        dataDir = os.path.join(jekyllInstance.siPath, "data")
        b.dir.createIfNotThere(dataDir)

        inDirSubProc = b.subProc.WOpW(invedBy=self, cd=dataDir)

        # site is the name of the site being created
        if inDirSubProc.bash(f"""jekyll new site""",
        ).isProblematic():  return(io.eh.badOutcome(cmndOutcome))

        if inDirSubProc.bash(f"""ls -ld site""",
        ).isProblematic():  return(io.eh.badOutcome(cmndOutcome))

        return icm.opSuccessAnNoResult(cmndOutcome)


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "siJekyll_siteDumpAndTriggers" :comment "" :parsMand "bpoId si" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<siJekyll_siteDumpAndTriggers>>  =verify= parsMand=bpoId si ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class siJekyll_siteDumpAndTriggers(cs.Cmnd):
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
        docStr = """\
***** TODO [[elisp:(org-cycle)][| *CmndDesc:* | ]] Status: Has not been tested yet.
        """
        if self.docStrClassSet(docStr,): return cmndOutcome

        if siJekyll_siteDump(cmndOutcome=cmndOutcome).cmnd(
                bpoId=bpoId,
                si=si,
        ).isProblematic(): return(io.eh.badOutcome(cmndOutcome))

        if siJekyll_siteTriggers(cmndOutcome=cmndOutcome).cmnd(
                bpoId=bpoId,
                si=si,
        ).isProblematic(): return(io.eh.badOutcome(cmndOutcome))

        return icm.opSuccessAnNoResult(cmndOutcome)


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "siJekyll_siteDump" :comment "" :parsMand "bpoId si" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<siJekyll_siteDump>>  =verify= parsMand=bpoId si ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class siJekyll_siteDump(cs.Cmnd):
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
        docStr = """\
***** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Uses palsBases.basesUpdateSi to create var,log, bases.
***** TODO du_jekyll/sites/main/dump needs to be created and parameterized.
        """
        if self.docStrClassSet(docStr,): return cmndOutcome

        jekyllInstance  = Jekyll_Inst(bpoId, si)

        palsBaseDir = bpo.bpoBaseDir_obtain(bpoId,)
        dumpDir = os.path.join(palsBaseDir, "du_jekyll/sites/main/dump")

        siteDir = os.path.join(jekyllInstance.siPath, "data/site")

        inDirSubProc = b.subProc.WOpW(invedBy=self, cd=siteDir)
        # Build as a pure html site
        if inDirSubProc.bash(f"""bundle exec jekyll build -d {dumpDir}""",
        ).isProblematic():  return(io.eh.badOutcome(cmndOutcome))

        return icm.opSuccessAnNoResult(cmndOutcome)

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "siJekyll_siteTriggers" :comment "" :parsMand "bpoId si" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<siJekyll_siteTriggers>>  =verify= parsMand=bpoId si ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class siJekyll_siteTriggers(cs.Cmnd):
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
        docStr = """\
***** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Triggers can be specified as destination args.
        """
        if self.docStrClassSet(docStr,): return cmndOutcome

        if b.subProc.WOpW(invedBy=self,).bash(
                f"""cntnrGitShTriggers.py -i gitSh_invoker_trigger_jekyll /tmp/trigger-jekyll""",
        ).isProblematic():  return(io.eh.badOutcome(cmndOutcome))

        return icm.opSuccessAnNoResult(cmndOutcome)


####+BEGIN: bx:cs:py3:section :title "Supporting Classes And Functions"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Supporting Classes And Functions*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:class/decl :className "SiRepo_Jekyll" :superClass "palsSis.SiRepo" :comment "Expected to be subclassed" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /SiRepo_Jekyll/  superClass=palsSis.SiRepo =Expected to be subclassed=  [[elisp:(org-cycle)][| ]]
#+end_org """
class SiRepo_Jekyll(palsSis.SiRepo):
####+END:
    """
** Abstraction of the base ByStar Portable Object
"""
    def __init__(
            self,
            bpoId,
            siPath,
    ):
        # print("eee  SiRepo_Jekyll")
        if palsSis.EffectiveSis.givenSiPathGetSiObjOrNone(bpoId, siPath,):
            b_io.eh.critical_usageError(f"Duplicate Attempt At Singleton Creation bpoId={bpoId}, siPath={siPath}")
        else:
            super().__init__(bpoId, siPath,) # includes: EffectiveSis.addSi(bpoId, siPath, self,)


    def obtainFromFPs(self,):
        pass


####+BEGIN: b:py3:class/decl :className "Jekyll_Inst" :superClass "palsSis.SiSvcInst" :comment "Expected to be subclassed" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /Jekyll_Inst/  superClass=palsSis.SiSvcInst =Expected to be subclassed=  [[elisp:(org-cycle)][| ]]
#+end_org """
class Jekyll_Inst(palsSis.SiSvcInst):
####+END:
    """
** Abstraction of the base ByStar Portable Object
"""
    def __init__(
            self,
            bpoId,
            si,
    ):
        if palsSis.EffectiveSis.givenSiPathGetSiObjOrNone(bpoId, si,):
            b_io.eh.critical_usageError(f"Duplicate Attempt At Singleton Creation bpoId={bpoId}, siPath={si}")
        else:
            super().__init__(bpoId, si,) # includes: EffectiveSis.addSi(bpoId, siPath, self,)

        self.bpo = palsBpo.obtainBpo(bpoId,)
        self.siPath = palsSis.siIdToSiPath(bpoId, si,)
        self.siId = si
        self.invContext = invoke.context.Context(config=None)

    def obtainFromFPs(self,):
        pass

    def setVar(self, value,):
        self.setMyVar = value

    def domainShow(self,):
        pass

    def stdout(self,):
        pass

    def assemble(self,):
        svcInstanceBaseDir = self.siPath
        bsiAgentFile = os.path.join(svcInstanceBaseDir, "bsiAgent.sh")

        shutil.copyfile("/bisos/apps/defaults/pals/si/common/bsiAgent.sh", bsiAgentFile)

        siInfoBase = os.path.join(svcInstanceBaseDir, "siInfo")

        if not os.path.exists(siInfoBase): os.makedirs(siInfoBase)

        icm.b.fp.FileParamWriteTo(siInfoBase, 'svcCapability', __file__) # NOTYET, last part

        invContext = invoke.context.Context(config=None)

        with invContext.cd(svcInstanceBaseDir):
            invContext.run("bxtStartCommon.sh  -v -n showRun -i startObjectGen auxLeaf")



####+BEGIN: b:py3:cs:func/typing :funcName "digestAtSvcProv_obsoleted" :funcType "" :retType "" :deco "" :argsList "bpoId siRepoBase"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-       [[elisp:(outline-show-subtree+toggle)][||]] /digestAtSvcProv_obsoleted/   [[elisp:(org-cycle)][| ]]
#+end_org """
def digestAtSvcProv_obsoleted(
####+END:
     bpoId,
     siRepoBase,
):
    b_io.tm.here("Incomplete")
    palsSis.createSiObj(bpoId, siRepoBase, SiRepo_Jekyll)

    thisBpo = palsBpo.obtainBpo(bpoId,)

    for (_, dirNames, _,) in os.walk(siRepoBase):
        for each in dirNames:
            if each == "siInfo":
                continue
            # verify that it is a svcInstance
            siRepoPath = os.path.join(siRepoBase, each)
            digestPrimSvcInstance_obsoleted(bpoId, siRepoPath, each,)
            thisBpo.sis.svcInst_primary_enabled.append(siRepoPath,)
        break


####+BEGIN: b:py3:cs:func/typing :funcName "digestPrimSvcInstance_obsoleted" :funcType "" :retType "" :deco "" :argsList "bpoId siRepoBase instanceName"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-       [[elisp:(outline-show-subtree+toggle)][||]] /digestPrimSvcInstance_obsoleted/   [[elisp:(org-cycle)][| ]]
#+end_org """
def digestPrimSvcInstance_obsoleted(
####+END:
    bpoId,
    siRepoBase,
    instanceName,
):
    b_io.tm.here("Incomplete")

    thisSi = palsSis.createSiObj(bpoId, siRepoBase, Jekyll_Inst)

    thisSi.setVar(22) # type: ignore

    b_io.tm.here(f"bpoId={bpoId}, siRepoBase={siRepoBase}, instanceName={instanceName}")


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
