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
csInfo['moduleName'] = "palsBases"
####+END:

####+BEGIN: bx:cs:py:version-timestamp :style "date"
csInfo['version'] = "202502111206"
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
*  This file:/bisos/git/bxRepos/bisos-pip/pals/py3/bisos/pals/palsBases.py :: [[elisp:(org-cycle)][| ]]
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
# import collections
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

####+BEGIN: bx:cs:py3:section :title "Pals Bases Classes"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Pals Bases Classes*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:


####+BEGIN: b:py3:class/decl :className "PalsBases" :superClass "object" :comment "Bases of a palsBpo" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /PalsBases/  superClass=object =Bases of a palsBpo=  [[elisp:(org-cycle)][| ]]
#+end_org """
class PalsBases(object):
####+END:
    """
** Abstraction of the base ByStar Portable Object
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
            palsBpo,
    ):
        self.bpoId = bpoId
        self.palsBpo = palsBpo

####+BEGIN: b:py3:cs:method/typing :methodName "basesUpdate" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /basesUpdate/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def basesUpdate(
####+END:
            self,
    ):
        self.varBasePath_update()
        self.controlBasePath_update()
        self.logBasePath_update()
        self.curBasePath_update()
        self.tmpBasePath_update()
        return


####+BEGIN: b:py3:cs:method/typing :methodName "varBasePath_update" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /varBasePath_update/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def varBasePath_update(
####+END:
            self,
    ) -> pathlib.Path:

        actualBasePath = pathlib.Path(
            os.path.join(
                "/var/bisos/bpo/var",
                self.bpoId,
                "bpo",
            )
        )
        actualBasePath.mkdir(parents=True, exist_ok=True)
        bpoBasePath  = self.varBasePath_obtain()

        return fpath.symlinkUpdate(actualBasePath, bpoBasePath)


####+BEGIN: b:py3:cs:method/typing :methodName "varBasePath_obtain" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /varBasePath_obtain/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def varBasePath_obtain(
####+END:
            self,
    ) -> pathlib.Path:
        return (
            pathlib.Path(
                os.path.join(
                    self.palsBpo.bpoBaseDir, "var"
                )
            )
        )


####+BEGIN: b:py3:cs:method/typing :methodName "controlBasePath_update" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /controlBasePath_update/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def controlBasePath_update(
####+END:
            self,
    ) -> pathlib.Path:

        actualBasePath = pathlib.Path(
            os.path.join(
                "/var/bisos/bpo/control",
                self.bpoId,
                "bpo",
            )
        )
        actualBasePath.mkdir(parents=True, exist_ok=True)
        bpoBasePath  = self.controlBasePath_obtain()

        if not os.path.isdir(bpoBasePath):
            return fpath.symlinkUpdate(actualBasePath, bpoBasePath)


####+BEGIN: b:py3:cs:method/typing :methodName "controlBasePath_obtain" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /controlBasePath_obtain/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def controlBasePath_obtain(
####+END:
            self,
    ) -> pathlib.Path:
        return (
            pathlib.Path(
                os.path.join(
                    self.palsBpo.bpoBaseDir, "control"
                )
            )
        )


####+BEGIN: b:py3:cs:method/typing :methodName "logBasePath_update" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /logBasePath_update/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def logBasePath_update(
####+END:
           self,
    ) -> pathlib.Path:

        actualBasePath = pathlib.Path(
            os.path.join(
                "/var/bisos/bpo/log",
                self.bpoId,
                "bpo",
            )
        )
        actualBasePath.mkdir(parents=True, exist_ok=True)
        bpoBasePath  = self.logBasePath_obtain()

        return fpath.symlinkUpdate(actualBasePath, bpoBasePath)


####+BEGIN: b:py3:cs:method/typing :methodName "logBasePath_obtain" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /logBasePath_obtain/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def logBasePath_obtain(
####+END:
            self,
    ) -> pathlib.Path:
        return (
            pathlib.Path(
                os.path.join(
                    self.palsBpo.bpoBaseDir, "log"
                )
            )
        )


####+BEGIN: b:py3:cs:method/typing :methodName "tmpBasePath_update" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /tmpBasePath_update/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def tmpBasePath_update(
####+END:
          self,
    ) -> pathlib.Path:

        actualBasePath = pathlib.Path(
            os.path.join(
                "/tmp/bisos",
            )
        )
        actualBasePath.mkdir(parents=True, exist_ok=True)
        bpoBasePath  = self.tmpBasePath_obtain()

        return fpath.symlinkUpdate(actualBasePath, bpoBasePath)

####+BEGIN: b:py3:cs:method/typing :methodName "tmpBasePath_obtain" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /tmpBasePath_obtain/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def tmpBasePath_obtain(
####+END:
            self,
    ) -> pathlib.Path:
        return (
            pathlib.Path(
                os.path.join(
                    self.palsBpo.bpoBaseDir, "tmp"
                )
            )
        )


####+BEGIN: b:py3:cs:method/typing :methodName "curBasePath_update" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /curBasePath_update/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def curBasePath_update(
####+END:
          self,
    ) -> pathlib.Path:

        actualBasePath = pathlib.Path(
            os.path.join(
                "/var/bisos/bpo/cur",
                self.bpoId,
                "bpo",
            )
        )
        actualBasePath.mkdir(parents=True, exist_ok=True)
        bpoBasePath  = self.curBasePath_obtain()

        return fpath.symlinkUpdate(actualBasePath, bpoBasePath)

####+BEGIN: b:py3:cs:method/typing :methodName "curBasePath_obtain" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /curBasePath_obtain/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def curBasePath_obtain(
####+END:
            self,
    ) -> pathlib.Path:
        return (
            pathlib.Path(
                os.path.join(
                    self.palsBpo.bpoBaseDir, "cur"
                )
            )
        )


####+BEGIN: b:py3:class/decl :className "PalsSivdBases" :superClass "object" :comment "Bases of a palsBpo" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /PalsSivdBases/  superClass=object =Bases of a palsBpo=  [[elisp:(org-cycle)][| ]]
#+end_org """
class PalsSivdBases(object):
####+END:
    """
** Abstraction of the base ByStar Portable Object
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
            palsBpo,
            sivdId,
    ):
        self.bpoId = bpoId
        self.palsBpo = palsBpo
        self.sivdId = sivdId
        self.palsBases = PalsBases(bpoId, palsBpo)

####+BEGIN: b:py3:cs:method/typing :methodName "basesUpdate" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /basesUpdate/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def basesUpdate(
####+END:
            self,
    ):
        self.varBasePath_update()
        self.controlBasePath_update()
        self.logBasePath_update()
        self.curBasePath_update()
        self.tmpBasePath_update()
        return


####+BEGIN: b:py3:cs:method/typing :methodName "varBasePath_update" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /varBasePath_update/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def varBasePath_update(
####+END:
            self,
    ) -> pathlib.Path:

        actualBasePath = pathlib.Path(
            os.path.join(
                "/var/bisos/bpo/var",
                self.bpoId,
                "bpo",
                self.sivdId,
            )
        )
        actualBasePath.mkdir(parents=True, exist_ok=True)
        bpoBasePath  = self.varBasePath_obtain()

        return fpath.symlinkUpdate(actualBasePath, bpoBasePath)


####+BEGIN: b:py3:cs:method/typing :methodName "varBasePath_obtain" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /varBasePath_obtain/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def varBasePath_obtain(
####+END:
            self,
    ) -> pathlib.Path:
        return (
            pathlib.Path(
                os.path.join(
                    palsSis.sivd_instanceBaseDir(
                        self.bpoId,
                        self.sivdId,
                    ),
                    "var",
                )
            )
        )


####+BEGIN: b:py3:cs:method/typing :methodName "controlBasePath_update" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /controlBasePath_update/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def controlBasePath_update(
####+END:
            self,
    ) -> pathlib.Path:

        actualBasePath = pathlib.Path(
            os.path.join(
                "/var/bisos/bpo/control",
                self.bpoId,
                "bpo",
                self.sivdId,
            )
        )
        actualBasePath.mkdir(parents=True, exist_ok=True)
        bpoBasePath  = self.controlBasePath_obtain()

        return fpath.symlinkUpdate(actualBasePath, bpoBasePath)


####+BEGIN: b:py3:cs:method/typing :methodName "controlBasePath_obtain" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /controlBasePath_obtain/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def controlBasePath_obtain(
####+END:
            self,
    ) -> pathlib.Path:
        return (
            pathlib.Path(
                os.path.join(
                    palsSis.sivd_instanceBaseDir(
                        self.bpoId,
                        self.sivdId,
                    ),
                    "control",
                )
            )
        )


####+BEGIN: b:py3:cs:method/typing :methodName "logBasePath_update" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /logBasePath_update/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def logBasePath_update(
####+END:
           self,
    ) -> pathlib.Path:

        actualBasePath = pathlib.Path(
            os.path.join(
                "/var/bisos/bpo/log",
                self.bpoId,
                "bpo",
                self.sivdId,
            )
        )
        actualBasePath.mkdir(parents=True, exist_ok=True)
        bpoBasePath  = self.logBasePath_obtain()

        return fpath.symlinkUpdate(actualBasePath, bpoBasePath)


####+BEGIN: b:py3:cs:method/typing :methodName "logBasePath_obtain" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /logBasePath_obtain/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def logBasePath_obtain(
####+END:
            self,
    ) -> pathlib.Path:
        return (
            pathlib.Path(
                os.path.join(
                    palsSis.sivd_instanceBaseDir(
                        self.bpoId,
                        self.sivdId,
                    ),
                    "log"
                )
            )
        )


####+BEGIN: b:py3:cs:method/typing :methodName "tmpBasePath_update" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /tmpBasePath_update/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def tmpBasePath_update(
####+END:
          self,
    ) -> pathlib.Path:

        actualBasePath = pathlib.Path(
            os.path.join(
                "/tmp/bisos",
            )
        )
        actualBasePath.mkdir(parents=True, exist_ok=True)
        bpoBasePath  = self.tmpBasePath_obtain()

        return fpath.symlinkUpdate(actualBasePath, bpoBasePath)

####+BEGIN: b:py3:cs:method/typing :methodName "tmpBasePath_obtain" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /tmpBasePath_obtain/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def tmpBasePath_obtain(
####+END:
            self,
    ) -> pathlib.Path:
        return (
            pathlib.Path(
                os.path.join(
                    palsSis.sivd_instanceBaseDir(
                        self.bpoId,
                        self.sivdId,
                    ),
                    "tmp",
                )
            )
        )


####+BEGIN: b:py3:cs:method/typing :methodName "curBasePath_update" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /curBasePath_update/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def curBasePath_update(
####+END:
          self,
    ) -> pathlib.Path:

        actualBasePath = pathlib.Path(
            os.path.join(
                "/var/bisos/bpo/cur",
                self.bpoId,
                "bpo",
                self.sivdId,
            )
        )
        actualBasePath.mkdir(parents=True, exist_ok=True)
        bpoBasePath  = self.curBasePath_obtain()

        return fpath.symlinkUpdate(actualBasePath, bpoBasePath)

####+BEGIN: b:py3:cs:method/typing :methodName "curBasePath_obtain" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /curBasePath_obtain/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def curBasePath_obtain(
####+END:
            self,
    ) -> pathlib.Path:
        return (
            pathlib.Path(
                os.path.join(
                    palsSis.sivd_instanceBaseDir(
                        self.bpoId,
                        self.sivdId,
                    ),
                    "cur",
                )
            )
        )



####+BEGIN: b:py3:class/decl :className "PalsSiBases" :superClass "object" :comment "Bases of a palsBpo" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /PalsSiBases/  superClass=object =Bases of a palsBpo=  [[elisp:(org-cycle)][| ]]
#+end_org """
class PalsSiBases(object):
####+END:
    """
** Abstraction of the base ByStar Portable Object
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
            palsBpo,
            siId,
    ):
        self.bpoId = bpoId
        self.palsBpo = palsBpo
        self.siId = siId
        self.palsBases = PalsBases(bpoId, palsBpo)

####+BEGIN: b:py3:cs:method/typing :methodName "basesUpdate" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /basesUpdate/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def basesUpdate(
####+END:
            self,
    ):
        self.varBasePath_update()
        self.controlBasePath_update()
        self.logBasePath_update()
        self.curBasePath_update()
        self.tmpBasePath_update()
        return


####+BEGIN: b:py3:cs:method/typing :methodName "varBasePath_update" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /varBasePath_update/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def varBasePath_update(
####+END:
            self,
    ) -> pathlib.Path:

        actualBasePath = pathlib.Path(
            os.path.join(
                "/var/bisos/bpo/var",
                self.bpoId,
                "bpo",
                self.siId,
            )
        )
        actualBasePath.mkdir(parents=True, exist_ok=True)
        bpoBasePath  = self.varBasePath_obtain()

        return fpath.symlinkUpdate(actualBasePath, bpoBasePath)


####+BEGIN: b:py3:cs:method/typing :methodName "varBasePath_obtain" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /varBasePath_obtain/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def varBasePath_obtain(
####+END:
            self,
    ) -> pathlib.Path:
        return (
            pathlib.Path(
                os.path.join(
                    palsSis.si_instanceBaseDir(
                        self.bpoId,
                        self.siId,
                    ),
                    "var",
                )
            )
        )


####+BEGIN: b:py3:cs:method/typing :methodName "controlBasePath_update" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /controlBasePath_update/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def controlBasePath_update(
####+END:
            self,
    ) -> pathlib.Path:

        actualBasePath = pathlib.Path(
            os.path.join(
                "/var/bisos/bpo/control",
                self.bpoId,
                "bpo",
                self.siId,
            )
        )
        actualBasePath.mkdir(parents=True, exist_ok=True)
        bpoBasePath  = self.controlBasePath_obtain()

        return fpath.symlinkUpdate(actualBasePath, bpoBasePath)


####+BEGIN: b:py3:cs:method/typing :methodName "controlBasePath_obtain" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /controlBasePath_obtain/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def controlBasePath_obtain(
####+END:
            self,
    ) -> pathlib.Path:
        return (
            pathlib.Path(
                os.path.join(
                    palsSis.si_instanceBaseDir(
                        self.bpoId,
                        self.siId,
                    ),
                    "control",
                )
            )
        )


####+BEGIN: b:py3:cs:method/typing :methodName "logBasePath_update" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /logBasePath_update/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def logBasePath_update(
####+END:
           self,
    ) -> pathlib.Path:

        actualBasePath = pathlib.Path(
            os.path.join(
                "/var/bisos/bpo/log",
                self.bpoId,
                "bpo",
                self.siId,
            )
        )
        actualBasePath.mkdir(parents=True, exist_ok=True)
        bpoBasePath  = self.logBasePath_obtain()

        return fpath.symlinkUpdate(actualBasePath, bpoBasePath)


####+BEGIN: b:py3:cs:method/typing :methodName "logBasePath_obtain" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /logBasePath_obtain/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def logBasePath_obtain(
####+END:
            self,
    ) -> pathlib.Path:
        return (
            pathlib.Path(
                os.path.join(
                    palsSis.si_instanceBaseDir(
                        self.bpoId,
                        self.siId,
                    ),
                    "log"
                )
            )
        )


####+BEGIN: b:py3:cs:method/typing :methodName "tmpBasePath_update" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /tmpBasePath_update/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def tmpBasePath_update(
####+END:
          self,
    ) -> pathlib.Path:

        actualBasePath = pathlib.Path(
            os.path.join(
                "/tmp/bisos",
            )
        )
        actualBasePath.mkdir(parents=True, exist_ok=True)
        bpoBasePath  = self.tmpBasePath_obtain()

        return fpath.symlinkUpdate(actualBasePath, bpoBasePath)

####+BEGIN: b:py3:cs:method/typing :methodName "tmpBasePath_obtain" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /tmpBasePath_obtain/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def tmpBasePath_obtain(
####+END:
            self,
    ) -> pathlib.Path:
        return (
            pathlib.Path(
                os.path.join(
                    palsSis.si_instanceBaseDir(
                        self.bpoId,
                        self.siId,
                    ),
                    "tmp",
                )
            )
        )


####+BEGIN: b:py3:cs:method/typing :methodName "curBasePath_update" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /curBasePath_update/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def curBasePath_update(
####+END:
          self,
    ) -> pathlib.Path:

        actualBasePath = pathlib.Path(
            os.path.join(
                "/var/bisos/bpo/cur",
                self.bpoId,
                "bpo",
                self.siId,
            )
        )
        actualBasePath.mkdir(parents=True, exist_ok=True)
        bpoBasePath  = self.curBasePath_obtain()

        return fpath.symlinkUpdate(actualBasePath, bpoBasePath)

####+BEGIN: b:py3:cs:method/typing :methodName "curBasePath_obtain" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /curBasePath_obtain/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def curBasePath_obtain(
####+END:
            self,
    ) -> pathlib.Path:
        return (
            pathlib.Path(
                os.path.join(
                    palsSis.si_instanceBaseDir(
                        self.bpoId,
                        self.siId,
                    ),
                    "cur",
                )
            )
        )


####+BEGIN: bx:cs:py3:section :title "ICM Commands"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *ICM Commands*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "basesUpdate" :parsMand "bpoId" :parsOpt "" :argsMin 0 :argsMax 5 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<basesUpdate>>  =verify= parsMand=bpoId argsMax=5 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class basesUpdate(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 5,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Mandatory Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'bpoId': bpoId, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        bpoId = csParam.mappedValue('bpoId', bpoId)
####+END:

        cmndArgs = list(self.cmndArgsGet("0&5", cmndArgsSpecDict, argsList)) # type: ignore

        if len(cmndArgs):
            if  cmndArgs[0] == "all":
                cmndArgsSpec = cmndArgsSpecDict.argPositionFind("0&5")
                argChoices = cmndArgsSpec.argChoicesGet()
                argChoices.pop(0)
                cmndArgs= argChoices

        thisBpo = palsBpo.obtainBpo(bpoId,)

        for each in cmndArgs:
            try:
                baseUpdateMethod = getattr(thisBpo.bases, "{each}BasePath_update".format(each=each))
                palsBpoBase = baseUpdateMethod()
                print(palsBpoBase)
            except AttributeError:
                b_io.eh.critical_exception("")
                continue

        return cmndOutcome


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
            argChoices=['all', 'var', 'tmp', 'log', 'control', 'cur'],
            argDescription="Rest of args for use by action"
        )

        return cmndArgsSpecDict



####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "basesUpdateSivd" :parsMand "bpoId sivd" :parsOpt "" :argsMin 0 :argsMax 5 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<basesUpdateSivd>>  =verify= parsMand=bpoId sivd argsMax=5 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class basesUpdateSivd(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'sivd', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 5,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Mandatory Param
             sivd: typing.Optional[str]=None,  # Cs Mandatory Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'bpoId': bpoId, 'sivd': sivd, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        bpoId = csParam.mappedValue('bpoId', bpoId)
        sivd = csParam.mappedValue('sivd', sivd)
####+END:

        cmndArgs = list(self.cmndArgsGet("0&5", cmndArgsSpecDict, argsList)) # type: ignore

        if len(cmndArgs):
            if  cmndArgs[0] == "all":
                cmndArgsSpec = cmndArgsSpecDict.argPositionFind("0&5")
                argChoices = cmndArgsSpec.argChoicesGet()
                argChoices.pop(0)
                cmndArgs= argChoices

        thisBpo = palsBpo.obtainBpo(bpoId,)

        thisPalsSivdBases = PalsSivdBases(bpoId, thisBpo, sivd)

        for each in cmndArgs:
            try:
                baseUpdateMethod = getattr(thisPalsSivdBases, "{each}BasePath_update".format(each=each))
                palsBpoBase = baseUpdateMethod()
                print(palsBpoBase)
            except AttributeError:
                b_io.eh.critical_exception("")
                continue

        return cmndOutcome


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
            argChoices=['all', 'var', 'tmp', 'log', 'control', 'cur'],
            argDescription="Rest of args for use by action"
        )

        return cmndArgsSpecDict


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "basesUpdateSi" :parsMand "bpoId si" :parsOpt "" :argsMin 0 :argsMax 5 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<basesUpdateSi>>  =verify= parsMand=bpoId si argsMax=5 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class basesUpdateSi(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'si', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 5,}

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

        cmndArgs = list(self.cmndArgsGet("0&5", cmndArgsSpecDict, argsList)) # type: ignore

        if len(cmndArgs):
            if  cmndArgs[0] == "all":
                cmndArgsSpec = cmndArgsSpecDict.argPositionFind("0&5")
                argChoices = cmndArgsSpec.argChoicesGet()
                argChoices.pop(0)
                cmndArgs= argChoices

        thisBpo = palsBpo.obtainBpo(bpoId,)

        thisPalsSiBases = PalsSiBases(bpoId, thisBpo, si)

        for each in cmndArgs:
            try:
                baseUpdateMethod = getattr(thisPalsSiBases, "{each}BasePath_update".format(each=each))
                palsBpoBase = baseUpdateMethod()
                print(palsBpoBase)
            except AttributeError:
                b_io.eh.critical_exception("")
                continue

        return cmndOutcome


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
            argChoices=['all', 'var', 'tmp', 'log', 'control', 'cur'],
            argDescription="Rest of args for use by action"
        )

        return cmndArgsSpecDict


"""
***** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Returns the full path of the Sr baseDir.
"""


####+BEGIN: bx:cs:py3:section :title "End Of Editable Text"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *End Of Editable Text*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/bisos/apps/defaults/software/plusOrg/dblock/inserts/endOfFileControls.org"
#+STARTUP: showall
####+END:
