# -*- coding: utf-8 -*-
"""\
* *[Summary]* :: A /library/ Beginning point for development of new ICM oriented libraries.
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
csInfo['moduleName'] = "palsSis"
####+END:

####+BEGIN: bx:cs:py:version-timestamp :style "date"
csInfo['version'] = "202502112219"
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
*  This file:/bisos/git/bxRepos/bisos-pip/pals/py3/bisos/pals/palsSis.py :: [[elisp:(org-cycle)][| ]]
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

from deprecated import deprecated

from bisos.platform import bxPlatformConfig
# from bisos.platform import bxPlatformThis

from bisos.bpo import bpo
from bisos.pals import palsBpo

####+BEGIN: bx:dblock:python:func :funcName "si_svcName" :funcType "Obtain" :retType "str" :deco "" :argsList "si"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-Obtain   [[elisp:(outline-show-subtree+toggle)][||]] /si_svcName/ retType=str argsList=(si)  [[elisp:(org-cycle)][| ]]
#+end_org """
def si_svcName(
    si,
):
####+END:
    """
** Return svcName based on si. Applies to primary and virdom.
    """
    siList = si.split('/')
    return siList[0]

####+BEGIN: bx:dblock:python:func :funcName "si_instanceName" :funcType "Obtain" :retType "str" :deco "" :argsList "si"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-Obtain   [[elisp:(outline-show-subtree+toggle)][||]] /si_instanceName/ retType=str argsList=(si)  [[elisp:(org-cycle)][| ]]
#+end_org """
def si_instanceName(
    si,
):
####+END:
    """
** Return service instance. Applies to primary and virdom.
    """
    siList = si.split('/')
    return siList[-1]

####+BEGIN: bx:dblock:python:func :funcName "sivd_virDomSvcName" :funcType "Obtain" :retType "str" :deco "" :argsList "si"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-Obtain   [[elisp:(outline-show-subtree+toggle)][||]] /sivd_virDomSvcName/ retType=str argsList=(si)  [[elisp:(org-cycle)][| ]]
#+end_org """
def sivd_virDomSvcName(
    si,
):
####+END:
    """
** If a virDom, return service name for virDom.
    """
    siList = si.split('/')
    virDomName = siList[1]
    if virDomName == si_instanceName(si):
        return ""
    else:
        return virDomName

####+BEGIN: bx:dblock:python:func :funcName "si_svcBaseDir" :funcType "Obtain" :retType "str" :deco "" :argsList "bpoId si"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-Obtain   [[elisp:(outline-show-subtree+toggle)][||]] /si_svcBaseDir/ retType=str argsList=(bpoId si)  [[elisp:(org-cycle)][| ]]
#+end_org """
def si_svcBaseDir(
    bpoId,
    si,
):
####+END:
    """
** Return full path of the svc base dir. Eg. ~bpoId/si_svcName.
    """
    bpoBaseDir = bpo.bpoBaseDir_obtain(bpoId)
    siServiceName = si_svcName(si)
    return (
        os.path.join(
            bpoBaseDir,
            format(f"si_{siServiceName}"),
        )
    )

####+BEGIN: bx:dblock:python:func :funcName "sivd_svcBaseDir" :funcType "Obtain" :retType "str" :deco "" :argsList "bpoId si"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-Obtain   [[elisp:(outline-show-subtree+toggle)][||]] /sivd_svcBaseDir/ retType=str argsList=(bpoId si)  [[elisp:(org-cycle)][| ]]
#+end_org """
def sivd_svcBaseDir(
    bpoId,
    si,
):
####+END:
    """
** Return full path of the svc base dir. Eg. ~bpoId/si_svcName.
    """
    bpoBaseDir = bpo.bpoBaseDir_obtain(bpoId)
    siServiceName = si_svcName(si)
    return (
        os.path.join(
            bpoBaseDir,
            format(f"sivd_{siServiceName}"),
        )
    )


####+BEGIN: bx:dblock:python:func :funcName "sivd_virDomSvcBaseDir" :funcType "Obtain" :retType "str" :deco "" :argsList "bpoId si"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-Obtain   [[elisp:(outline-show-subtree+toggle)][||]] /sivd_virDomSvcBaseDir/ retType=str argsList=(bpoId si)  [[elisp:(org-cycle)][| ]]
#+end_org """
def sivd_virDomSvcBaseDir(
    bpoId,
    si,
):
####+END:
    """
** Return full path of the svc base dir. Eg ~bpoId/si_apache2/svcVirDom.
    """
    svcVirDomName = sivd_virDomSvcName(si)
    svcBaseDir = sivd_svcBaseDir(bpoId, si)
    return (
        os.path.join(
            svcBaseDir,
            svcVirDomName,
        )
    )

####+BEGIN: bx:dblock:python:func :funcName "si_instanceBaseDir" :funcType "Obtain" :retType "str" :deco "" :argsList "bpoId si"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-Obtain   [[elisp:(outline-show-subtree+toggle)][||]] /si_instanceBaseDir/ retType=str argsList=(bpoId si)  [[elisp:(org-cycle)][| ]]
#+end_org """
def si_instanceBaseDir(
    bpoId,
    si,
):
####+END:
    """
** Return full path of serviceInstance. Eg. ~bpoId/si_plone3/main
    """
    svcInstance = si_instanceName(si)
    svcVirDomName = sivd_virDomSvcName(si)
    if svcInstance == svcVirDomName:
        virDomSvcBaseDir = sivd_virDomSvcBaseDir(bpoId, si)
        return (
            os.path.join(
                virDomSvcBaseDir,
                svcInstance,
            )
        )
    else:
        svcBaseDir = si_svcBaseDir(bpoId, si)
        return (
            os.path.join(
                svcBaseDir,
                svcInstance,
            )
        )

####+BEGIN: bx:dblock:python:func :funcName "sivd_instanceBaseDir" :funcType "Obtain" :retType "str" :deco "" :argsList "bpoId si"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-Obtain   [[elisp:(outline-show-subtree+toggle)][||]] /sivd_instanceBaseDir/ retType=str argsList=(bpoId si)  [[elisp:(org-cycle)][| ]]
#+end_org """
def sivd_instanceBaseDir(
    bpoId,
    si,
):
####+END:
    """
** Return full path of serviceInstance. Eg. ~bpoId/si_plone3/main
    """
    svcInstance = si_instanceName(si)
    svcVirDomName = sivd_virDomSvcName(si)
    if svcInstance == svcVirDomName:
        # Not a virDom
        svcBaseDir = si_svcBaseDir(bpoId, si)
        return (
            os.path.join(
                svcBaseDir,
                svcInstance,
            )
        )
    else:
        virDomSvcBaseDir = sivd_virDomSvcBaseDir(bpoId, si)
        return (
            os.path.join(
                virDomSvcBaseDir,
                svcInstance,
            )
        )


####+BEGIN: bx:dblock:python:func :funcName "sivd_primSvcBaseDir" :funcType "Obtain" :retType "str" :deco "" :argsList "bpoId si"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-Obtain   [[elisp:(outline-show-subtree+toggle)][||]] /sivd_primSvcBaseDir/ retType=str argsList=(bpoId si)  [[elisp:(org-cycle)][| ]]
#+end_org """
def sivd_primSvcBaseDir(
    bpoId,
    si,
):
####+END:
    """
** For a virDom, return path to Primary svc base dir.
    """
    bpoBaseDir = bpo.bpoBaseDir_obtain(bpoId)
    svcVirDomName = sivd_virDomSvcName(si)
    return (
        os.path.join(
            bpoBaseDir,
            format(f"si_{svcVirDomName}"),
        )
    )


####+BEGIN: bx:dblock:python:func :funcName "sivd_primInstanceBaseDir" :funcType "Obtain" :retType "str" :deco "" :argsList "bpoId si"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-Obtain   [[elisp:(outline-show-subtree+toggle)][||]] /sivd_primInstanceBaseDir/ retType=str argsList=(bpoId si)  [[elisp:(org-cycle)][| ]]
#+end_org """
def sivd_primInstanceBaseDir(
    bpoId,
    si,
):
####+END:
    """
** For a virDom, return path to Primary svc instance base dir.
    """
    svcInstance = si_instanceName(si)
    primSvcBaseDir = sivd_primSvcBaseDir(bpoId, si)

    return (
        os.path.join(
            primSvcBaseDir,
            svcInstance,
        )
    )

####+BEGIN: bx:dblock:python:func :funcName "bpoSi_runBaseObtain_root" :funcType "obtain" :retType "bool" :deco "" :argsList "bpoId si"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-obtain   [[elisp:(outline-show-subtree+toggle)][||]] /bpoSi_runBaseObtain_root/ retType=bool argsList=(bpoId si)  [[elisp:(org-cycle)][| ]]
#+end_org """
def bpoSi_runBaseObtain_root(
    bpoId,
    si,
):
####+END:
    # icm.unusedSuppress(si)
    return(
        os.path.join(
            str(bxPlatformConfig.rootDir_deRun_fpObtain(configBaseDir=None,)),
            "bisos/r3/bpo",
            str(bpoId),
        )
    )

####+BEGIN: bx:dblock:python:func :funcName "bpoSi_runBaseObtain_var" :funcType "obtain" :retType "bool" :deco "" :argsList "bpoId si"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-obtain   [[elisp:(outline-show-subtree+toggle)][||]] /bpoSi_runBaseObtain_var/ retType=bool argsList=(bpoId si)  [[elisp:(org-cycle)][| ]]
#+end_org """
def bpoSi_runBaseObtain_var(
    bpoId,
    si,
):
####+END:
    return(
        os.path.join(
            bpoSi_runBaseObtain_root(
                bpoId,
                si,
            ),
            "var"
        )
    )

####+BEGIN: bx:dblock:python:func :funcName "bpoSi_runBaseObtain_tmp" :funcType "obtain" :retType "bool" :deco "" :argsList "bpoId si"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-obtain   [[elisp:(outline-show-subtree+toggle)][||]] /bpoSi_runBaseObtain_tmp/ retType=bool argsList=(bpoId si)  [[elisp:(org-cycle)][| ]]
#+end_org """
def bpoSi_runBaseObtain_tmp(
    bpoId,
    si,
):
####+END:
    return(
        os.path.join(
            bpoSi_runBaseObtain_root(
                bpoId,
                si,
            ),
            "tmp"
        )
    )

####+BEGIN: bx:dblock:python:func :funcName "bpoSi_runBaseObtain_log" :funcType "obtain" :retType "bool" :deco "" :argsList "bpoId si"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-obtain   [[elisp:(outline-show-subtree+toggle)][||]] /bpoSi_runBaseObtain_log/ retType=bool argsList=(bpoId si)  [[elisp:(org-cycle)][| ]]
#+end_org """
def bpoSi_runBaseObtain_log(
    bpoId,
    si,
):
####+END:
    return(
        os.path.join(
            bpoSi_runBaseObtain_root(
                bpoId,
                si,
            ),
            "log"
        )
    )


####+BEGIN: b:py3:class/decl :className "EffectiveSis" :superClass "object" :comment "" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /EffectiveSis/  superClass=object  [[elisp:(org-cycle)][| ]]
#+end_org """
class EffectiveSis(object):
####+END:
    """
** Only one instance is created for a given BpoId and an SiPath.
"""

    effectiveSisList = {}

    @staticmethod
    def addSi(
            bpoId,
            siPath,
            siObj
    ):
        b_io.tm.here(f"Adding bpoId={bpoId} siPath={siPath} siObj={siObj}")
        thisBpo = palsBpo.obtainBpo(bpoId,)
        if not thisBpo:
            return None
        #thisBpo.sis.effectiveSisList.update({siPath: siObj})
        __class__.effectiveSisList.update({siPath: siObj})


    @staticmethod
    def withSiPathCreateSiObj(
            bpoId,
            siPath,
            SiClass,
    ):
        """Is invoked from Digest with appropriate Class. Returns and siObj."""
        thisBpo = palsBpo.obtainBpo(bpoId,)
        if not thisBpo:
            return None

        if siPath in __class__.effectiveSisList:
            b_io.eh.problem_usageError(f"bpoId={bpoId} -- siPath={siPath} -- SiClass={SiClass}")
            b_io.eh.problem_usageError(siPath)
            b_io.eh.critical_oops("")
            return __class__.effectiveSisList[siPath]
        else:
            return SiClass(bpoId, siPath) # results in addSi()

    @staticmethod
    def givenSiPathFindSiObj(
            bpoId,
            siPath,
    ):
        """Should really not fail."""
        thisBpo = palsBpo.obtainBpo(bpoId,)
        if not thisBpo:
            return None

        if siPath in __class__.effectiveSisList:
            return __class__.effectiveSisList[siPath]
        else:
            b_io.eh.problem_usageError("")
            return None

    @staticmethod
    def givenSiPathGetSiObjOrNone(
            bpoId,
            siPath,
    ):
        """Expected to perhaps fail."""
        thisBpo = palsBpo.obtainBpo(bpoId,)
        if not thisBpo:
            return None

        if siPath in __class__.effectiveSisList:
            return __class__.effectiveSisList[siPath]
        else:
            return None


####+BEGIN: bx:cs:python:func :funcName "createSiObj" :funcType "anyOrNone" :retType "bool" :deco "" :argsList "bpoId siPath SiClass"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /createSiObj/ retType=bool argsList=(bpoId siPath SiClass)  [[elisp:(org-cycle)][| ]]
#+end_org """
def createSiObj(
    bpoId,
    siPath,
    SiClass,
):
####+END:
    """Just an alias."""
    return EffectiveSis.withSiPathCreateSiObj(bpoId, siPath, SiClass)


####+BEGIN: bx:cs:python:func :funcName "siIdToSiPath" :funcType "anyOrNone" :retType "bool" :deco "" :argsList "bpoId siId"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /siIdToSiPath/ retType=bool argsList=(bpoId siId)  [[elisp:(org-cycle)][| ]]
#+end_org """
def siIdToSiPath(
    bpoId,
    siId,
):
####+END:
    """"Returns siPath"""
    thisBpo = palsBpo.obtainBpo(bpoId,)
    siPath = os.path.join(thisBpo.baseDir, "si_{siId}".format(siId=siId))
    return siPath


####+BEGIN: bx:cs:python:func :funcName "siPathToSiId" :funcType "anyOrNone" :retType "bool" :deco "" :argsList "bpoId siPath"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /siPathToSiId/ retType=bool argsList=(bpoId siPath)  [[elisp:(org-cycle)][| ]]
#+end_org """
def siPathToSiId(
    bpoId,
    siPath,
):
####+END:
    """"Returns siPath"""
    result = ""
    thisBpo = palsBpo.obtainBpo(bpoId,)
    siPathPrefix = os.path.join(thisBpo.baseDir, "si_")
    sivdPathPrefix = os.path.join(thisBpo.baseDir, "sivd_")
    if siPathPrefix in siPath:
        result = siPath.replace(siPathPrefix, '')
    elif sivdPathPrefix in siPath:
        result = siPath.replace(sivdPathPrefix, '')
    else:
        b_io.eh.critical_oops(f"bpoId={bpoId} -- siPath={siPath}")
    return result


####+BEGIN: bx:cs:python:func :funcName "sis_virDom_digest" :funcType "anyOrNone" :retType "bool" :deco "" :argsList "bpoId virDomSvcProv siRepoPath"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /sis_virDom_digest/ retType=bool argsList=(bpoId virDomSvcProv siRepoPath)  [[elisp:(org-cycle)][| ]]
#+end_org """
def sis_virDom_digest(
    bpoId,
    virDomSvcProv,
    siRepoPath,
):
####+END:
    """Using virDom Svc Provider."""
    thisBpo = palsBpo.obtainBpo(bpoId,)
    thisBpo.sis.svcProv_virDom_enabled.append(siRepoPath)
    if virDomSvcProv == "apache2":
        # We need to Create the virDomProvider object
        from bisos.pals import sivdApache2
        sivdApache2.digestAtVirDomSvcProv(bpoId, siRepoPath)


####+BEGIN: bx:cs:python:func :funcName "sis_prim_digestOBSOLETED" :funcType "anyOrNone" :retType "bool" :deco "" :argsList "bpoId primSvcProv siRepoPath"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /sis_prim_digestOBSOLETED/ retType=bool argsList=(bpoId primSvcProv siRepoPath)  [[elisp:(org-cycle)][| ]]
#+end_org """
def sis_prim_digestOBSOLETED(
    bpoId,
    primSvcProv,
    siRepoPath,
):
####+END:
    """Using Primary Svc Provider.
** TODO This should be automated so that addition of new SIs don't require any edits.
    """
    thisBpo = palsBpo.obtainBpo(bpoId,)
    thisBpo.sis.svcProv_primary_enabled.append(siRepoPath)
    if primSvcProv == "plone3":
        from bisos.pals import siPlone3
        siPlone3.digestAtSvcProv(bpoId, siRepoPath)
    elif primSvcProv == "geneweb":
        from bisos.pals import siGeneweb
        siGeneweb.digestAtSvcProv(bpoId, siRepoPath)
    elif primSvcProv == "jekyll":
        from bisos.pals import siJekyll
        siJekyll.digestAtSvcProv(bpoId, siRepoPath)
    elif primSvcProv == "apache2":
        from bisos.pals import siApache2
        siApache2.digestAtSvcProv(bpoId, siRepoPath)
    else:
        b_io.eh.problem_notyet("")


####+BEGIN: bx:cs:python:func :funcName "sis_prim_digest" :funcType "anyOrNone" :retType "bool" :deco "" :argsList "bpoId primSvcProv siRepoPath"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /sis_prim_digest/ retType=bool argsList=(bpoId primSvcProv siRepoPath)  [[elisp:(org-cycle)][| ]]
#+end_org """
def sis_prim_digest(
    bpoId,
    primSvcProv,
    siRepoPath,
):
####+END:
    """Using Primary Svc Provider.
** TODO This should be automated so that addition of new SIs don't require any edits.
    """
    thisBpo = palsBpo.obtainBpo(bpoId,)
    thisBpo.sis.svcProv_primary_enabled.append(siRepoPath)
    if primSvcProv == "plone3":
        from bisos.pals import siPlone3
        sis_digestAtSvcProv(bpoId, siRepoPath, siPlone3.SiRepo_Plone3, siPlone3.Plone3_Inst)
    elif primSvcProv == "geneweb":
        from bisos.pals import siGeneweb
        sis_digestAtSvcProv(bpoId, siRepoPath, siGeneweb.SiRepo_Geneweb, siGeneweb.Geneweb_Inst)
    elif primSvcProv == "jekyll":
        from bisos.pals import siJekyll
        sis_digestAtSvcProv(bpoId, siRepoPath, siJekyll.SiRepo_Jekyll, siJekyll.Jekyll_Inst)
    elif primSvcProv == "apache2":
        from bisos.pals import siApache2
        sis_digestAtSvcProv(bpoId, siRepoPath, siApache2.SiRepo_Apache2, siApache2.Apache2_Inst)
    else:
        b_io.eh.problem_notyet("")


####+BEGIN: b:py3:cs:func/typing :funcName "sis_digestAtSvcProv" :funcType "" :retType "" :deco "" :argsList "bpoId siRepoBase"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-       [[elisp:(outline-show-subtree+toggle)][||]] /sis_digestAtSvcProv/   [[elisp:(org-cycle)][| ]]
#+end_org """
def sis_digestAtSvcProv(
####+END:
        bpoId,
        siRepoBase,
        siRepoTypeClass,
        siInstanceClass,
):
    b_io.tm.here("Incomplete")
    createSiObj(bpoId, siRepoBase, siRepoTypeClass)

    thisBpo = palsBpo.obtainBpo(bpoId,)

    for (_, dirNames, _,) in os.walk(siRepoBase):
        for each in dirNames:
            if each == "siInfo":
                continue
            # verify that it is a svcInstance
            siRepoPath = os.path.join(siRepoBase, each)
            sis_digestPrimSvcInstance(bpoId, siRepoPath, each, siInstanceClass,)
            thisBpo.sis.svcInst_primary_enabled.append(siRepoPath,)
        break


####+BEGIN: b:py3:cs:func/typing :funcName "sis_digestPrimSvcInstance" :funcType "" :retType "" :deco "" :argsList "bpoId siRepoBase instanceName"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-       [[elisp:(outline-show-subtree+toggle)][||]] /sis_digestPrimSvcInstance/   [[elisp:(org-cycle)][| ]]
#+end_org """
def sis_digestPrimSvcInstance(
####+END:
        bpoId,
        siRepoBase,
        instanceName,
        siInstanceClass,
):
    b_io.tm.here("Incomplete")

    thisSi = createSiObj(bpoId, siRepoBase, siInstanceClass)

    thisSi.setVar(22) # type: ignore

    b_io.tm.here(f"bpoId={bpoId}, siRepoBase={siRepoBase}, instanceName={instanceName}")



####+BEGIN: b:py3:class/decl :className "PalsSis" :superClass "object" :comment "Context For All Sis" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /PalsSis/  superClass=object =Context For All Sis=  [[elisp:(org-cycle)][| ]]
#+end_org """
class PalsSis(object):
####+END:
    """
** Context For All Sis
"""

####+BEGIN: b:py3:cs:method/typing :methodName "__init__" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /__init__/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def __init__(
####+END:
            self,
            bpoId,
    ):
        siPath = "."
        b_io.tm.here("bpoId={bpoId}")
        if EffectiveSis. givenSiPathGetSiObjOrNone(bpoId, siPath,):
            b_io.eh.critical_usageError(f"Duplicate Attempt At Singleton Creation bpoId={bpoId}, siPath={siPath}")
        else:
            EffectiveSis.addSi(bpoId, siPath, self,)

        self.bpoId = bpoId
        self.thisBpo = palsBpo.obtainBpo(bpoId,)

        self.effectiveSisList = {}  # NOTYET, perhaps obsoleted

        self.svcProv_primary_enabled = []
        self.svcInst_primary_enabled = []

        self.svcProv_virDom_enabled = []
        self.svcType_virDom_enabled = []
        self.svcInst_virDom_enabled = []

####+BEGIN: b:py3:cs:method/typing :methodName "sisDigest" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /sisDigest/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def sisDigest(
####+END:
            self,
    ):
        """Based on known si_s, locate and digest SIs."""
        siRepoPath = ""
        for each in self.svcProv_virDom_available():
            siRepoPath = os.path.join(self.thisBpo.baseDir, "sivd_{each}".format(each=each))
            if os.path.isdir(siRepoPath):
                sis_virDom_digest(self.bpoId, each, siRepoPath)
                b_io.tm.here(f"is {siRepoPath}")
            else:
                b_io.tm.here(f"is NOT {siRepoPath} -- skipped")

        for each in self.svcProv_primary_available():
            siRepoPath = os.path.join(self.thisBpo.baseDir, "si_{each}".format(each=each))
            if os.path.isdir(siRepoPath):
                sis_prim_digest(self.bpoId, each, siRepoPath)
                b_io.tm.here(f"is {siRepoPath}")
            else:
                b_io.tm.here(f"is NOT {siRepoPath} -- skipped")

####+BEGIN: b:py3:cs:method/typing :methodName "svcProv_virDom_available" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /svcProv_virDom_available/  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def svcProv_virDom_available(
####+END:
    ):
        """List of Available Virtual Domain Service Providers"""
        return (
            [
                'apache2',
                'qmail',
            ]
        )

####+BEGIN: b:py3:cs:method/typing :methodName "svcProv_primary_available" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /svcProv_primary_available/  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def svcProv_primary_available(
####+END:
    ):
        """List of Available Primary Service Providers"""
        return (
            [
                'plone3',
                'geneweb',
                'jekyll',
                'apache2',
            ]
        )

####+BEGIN: b:py3:class/decl :className "SiRepo" :superClass "bpo.BpoRepo" :comment "Expected to be subclassed" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /SiRepo/  superClass=bpo.BpoRepo =Expected to be subclassed=  [[elisp:(org-cycle)][| ]]
#+end_org """
class SiRepo(bpo.BpoRepo):
####+END:
    """
** Abstraction of the base ByStar Portable Object
"""
    def __init__(
            self,
            bpoId,
            siPath,
    ):
        b_io.tm.here("bpoId={bpoId}")
        if EffectiveSis. givenSiPathGetSiObjOrNone(bpoId, siPath,):
            b_io.eh.critical_usageError(f"Duplicate Attempt At Singleton Creation bpoId={bpoId}, siPath={siPath}")
        else:
            EffectiveSis.addSi(bpoId, siPath, self,)


####+BEGIN: b:py3:class/decl :className "SiVirDomSvcType" :superClass "object" :comment "Expected to be subclassed" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /SiVirDomSvcType/  superClass=object =Expected to be subclassed=  [[elisp:(org-cycle)][| ]]
#+end_org """
class SiVirDomSvcType(object):
####+END:
    """
** Abstraction of the base ByStar Portable Object
"""
    def __init__(
            self,
            bpoId,
            siPath,
    ):
        EffectiveSis.addSi(bpoId, siPath, self,)

####+BEGIN: b:py3:class/decl :className "SiSvcInst" :superClass "object" :comment "Expected to be subclassed" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /SiSvcInst/  superClass=object =Expected to be subclassed=  [[elisp:(org-cycle)][| ]]
#+end_org """
class SiSvcInst(object):
####+END:
    """
** Abstraction of the base ByStar Portable Object
"""
    def __init__(
            self,
            bpoId,
            siPath,
    ):
        EffectiveSis.addSi(bpoId, siPath, self,)

####+BEGIN: b:py3:class/decl :className "SivdSvcInst" :superClass "object" :comment "Expected to be subclassed" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /SivdSvcInst/  superClass=object =Expected to be subclassed=  [[elisp:(org-cycle)][| ]]
#+end_org """
class SivdSvcInst(object):
####+END:
    """
** Abstraction of the base ByStar Portable Object
"""
    def __init__(
            self,
            bpoId,
            siPath,
    ):
        EffectiveSis.addSi(bpoId, siPath, self,)



####+BEGIN: bx:cs:py3:section :title "Service Intsance Lists -- Depracted"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Service Intsance Lists -- Depracted*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: bx:dblock:python:func :funcName "svcProv_virDom_list" :funcType "ParSpec" :retType "List" :deco "deprecated(\"moved to PalsSis\")" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-ParSpec  [[elisp:(outline-show-subtree+toggle)][||]] /svcProv_virDom_list/ retType=List argsList=nil deco=deprecated("moved to PalsSis")  [[elisp:(org-cycle)][| ]]
#+end_org """
@deprecated("moved to PalsSis")
def svcProv_virDom_list():
####+END:
    """List of Virtual Domain Service Providers"""
    return (
        [
            'apache2',
            'qmail',
        ]
    )

####+BEGIN: bx:dblock:python:func :funcName "svcProv_prim_list" :funcType "ParSpec" :retType "List" :deco "deprecated(\"moved to PalsSis\")" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-ParSpec  [[elisp:(outline-show-subtree+toggle)][||]] /svcProv_prim_list/ retType=List argsList=nil deco=deprecated("moved to PalsSis")  [[elisp:(org-cycle)][| ]]
#+end_org """
@deprecated("moved to PalsSis")
def svcProv_prim_list():
####+END:
    """List of Primary Service Providers"""
    return (
        [
            'plone3',
            'geneweb',
        ]
    )


####+BEGIN: bx:cs:py3:section :title "Common Parameters Specification -- For --si and --sivd"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Common Parameters Specification -- For --si and --sivd*  [[elisp:(org-cycle)][| ]]
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
        parName='si',
        parDescription="Service Instances Relative Path (plone3/main)",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        # parScope=icm.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--si',
    )
    csParams.parDictAdd(
        parName='sivd',
        parDescription="Service Instances Virtual Domain Relative Path (apache2/plone3/main)",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        # parScope=icm.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--sivd',
    )


####+BEGIN: bx:cs:py3:section :title "Common Examples Sections"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Common Examples Sections*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:


####+BEGIN: bx:dblock:python:func :funcName "examples_aaBpo_basicAccessOBSOLETED" :comment "Show/Verify/Update For relevant PBDs" :funcType "examples" :retType "none" :deco "" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-examples [[elisp:(outline-show-subtree+toggle)][||]] /examples_aaBpo_basicAccessOBSOLETED/ =Show/Verify/Update For relevant PBDs= retType=none argsList=nil  [[elisp:(org-cycle)][| ]]
#+end_org """
def examples_aaBpo_basicAccessOBSOLETED():
####+END:
    """
** Common examples.
"""
    def cpsInit(): return collections.OrderedDict()
    def menuItem(verbosity): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity=verbosity) # 'little' or 'none'
    # def execLineEx(cmndStr): cs.examples.execInsert(execLine=cmndStr)

    oneBpo = "pmi_ByD-100001"
    oneSiRelPath = "plone3/main"

    # def moduleOverviewMenuItem(overviewCmndName):
    #     cs.examples.menuChapter('* =Module=  Overview (desc, usage, status)')
    #     cmndName = "overview_bxpBaseDir" ; cmndArgs = "moduleDescription moduleUsage moduleStatus" ;
    #     cps = collections.OrderedDict()
    #     cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='none') # 'little' or 'none'

    # moduleOverviewMenuItem(bpo_libOverview)

    cs.examples.menuChapter(' =Bpo+Sr Info Base Roots=  *bpoSi Control Roots*')

    cmndName = "bpoSiFullPathBaseDir" ; cmndArgs = "" ;
    cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['si'] = oneSiRelPath
    menuItem(verbosity='little')


    cs.examples.menuChapter(' =Bpo+Sr Info Base Roots=  *bpoSi Control Roots*')

    cmndName = "bpoSiRunRootBaseDir" ; cmndArgs = "" ;
    cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['si'] = oneSiRelPath
    menuItem(verbosity='little')

    cmndName = "bpoSiRunRootBaseDir" ; cmndArgs = "all" ;
    cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['si'] = oneSiRelPath
    menuItem(verbosity='little')

    cmndName = "bpoSiRunRootBaseDir" ; cmndArgs = "var" ;
    cps=cpsInit() ; cps['bpoId'] = oneBpo ; cps['si'] = oneSiRelPath
    menuItem(verbosity='little')


####+BEGIN: bx:cs:py3:section :title "ICM Commands"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *ICM Commands*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "bpoSiFullPathBaseDir" :parsMand "bpoId si" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<bpoSiFullPathBaseDir>>  =verify= parsMand=bpoId si ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class bpoSiFullPathBaseDir(cs.Cmnd):
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
        retVal = siFullPathBaseDir_obtain(
            bpoId=bpoId,
            siRelPath=si,
        )

        if rtInv.outs:
            b_io.ann.write("{}".format(retVal))

        return cmndOutcome.set(
            opError=b.op.notAsFailure(retVal),
            opResults=retVal,
        )


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "bpoSiRunRootBaseDir" :parsMand "bpoId si" :parsOpt "" :argsMin 0 :argsMax 3 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<bpoSiRunRootBaseDir>>  =verify= parsMand=bpoId si argsMax=3 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class bpoSiRunRootBaseDir(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'si', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 3,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Mandatory Param
             si: typing.Optional[str]=None,  # Cs Mandatory Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'bpoId': bpoId, 'si': si, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        bpoId = csParam.mappedValue('bpoId', bpoId)
        si = csParam.mappedValue('si', si)
####+END:
        docStr = """\
***** TODO [[elisp:(org-cycle)][| *CmndDesc:* | ]] Is this dead code?
        """
        if self.docStrClassSet(docStr,): return cmndOutcome

        cmndArgs = list(self.cmndArgsGet("0&2", cmndArgsSpecDict, argsList)) # type: ignore

        if len(cmndArgs):
            if cmndArgs[0] == "all":
                cmndArgsSpec = cmndArgsSpecDict.argPositionFind("0&2")
                argChoices = cmndArgsSpec.argChoicesGet()
                argChoices.pop(0)
                cmndArgs= argChoices

        retVal = bpoSi_runBaseObtain_root(
            bpoId=bpoId,
            si=si,
        )

        if rtInv.outs:
            b_io.ann.write("{}".format(retVal))
            for each in cmndArgs:
                if each == "var":
                    b_io.ann.write("{each}".format(each=bpoSi_runBaseObtain_var(bpoId, si)))
                elif each == "tmp":
                    b_io.ann.write("{each}".format(each=bpoSi_runBaseObtain_tmp(bpoId, si)))
                elif each == "log":
                    b_io.ann.write("{each}".format(each=bpoSi_runBaseObtain_log(bpoId, si)))
                else:
                    b_io.eh.problem_usageError("")

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
            argPosition="0&2",
            argName="cmndArgs",
            argDefault=None,
            argChoices=['all', 'var', 'tmp', 'log',],
            argDescription="Rest of args for use by action"
        )

        return cmndArgsSpecDict


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "siInvoke" :comment "invokes specified method" :parsMand "bpoId si method" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<siInvoke>>  *invokes specified method*  =verify= parsMand=bpoId si method ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class siInvoke(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'si', 'method', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Mandatory Param
             si: typing.Optional[str]=None,  # Cs Mandatory Param
             method: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:
        """invokes specified method"""
        failed = b_io.eh.badOutcome
        callParamsDict = {'bpoId': bpoId, 'si': si, 'method': method, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        bpoId = csParam.mappedValue('bpoId', bpoId)
        si = csParam.mappedValue('si', si)
        method = csParam.mappedValue('method', method)
####+END:
        docStr = """\
***** TODO [[elisp:(org-cycle)][| *CmndDesc:* | ]] Allows for invocation a method corresponding to EffectiveSis.givenSiPathFindSiObj
        """
        if self.docStrClassSet(docStr,): return cmndOutcome

        thisBpo = palsBpo.obtainBpo(bpoId,)
        thisBpo.sis.sisDigest()

        siPath = siIdToSiPath(bpoId, si)
        thisSi = EffectiveSis.givenSiPathFindSiObj(bpoId, siPath,)
        if not thisSi:
            return cmndOutcome.set(opError=io.eh.critical_usageError(f"missing thisSi={thisSi}"))

        cmnd = "thisSi.{method}()".format(method=method)
        b_io.tm.here(f"cmnd={cmnd}")
        eval(cmnd)

        return b.op.successAndNoResult(cmndOutcome)


####+BEGIN: bx:cs:py3:section :title "Common/Generic Facilities -- Library Candidates"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Common/Generic Facilities -- Library Candidates*  [[elisp:(org-cycle)][| ]]
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
