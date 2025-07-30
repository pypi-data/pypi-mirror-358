# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: A =CS-Lib=
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
** This File: /bisos/git/bxRepos/bisos-pip/qmail/py3/bisos/qmail/qmailControl.py
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:python:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['marmeeQmail'], }
csInfo['version'] = '202212053620'
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

import sys
import collections

import collections
import pathlib
# import os
#import shutil

#from bisos.bpo import bpoRunBases
#from bisos.bpo import bpo

# from bisos.common import csParam

#from bisos.marmee import aasInMailControl
#from bisos.marmee import aasInMailFps
#from bisos.marmee import aasOutMailFps

# from bisos.qmail import maildrop

import enum


####+BEGIN: bx:dblock:python:section :title "Enumerations"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Enumerations*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:

####+BEGIN: bx:dblock:python:enum :enumName "acctAddr_Type" :comment ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Enum       [[elisp:(outline-show-subtree+toggle)][||]] /acctAddr_Type/  [[elisp:(org-cycle)][| ]]
#+end_org """
@enum.unique
class acctAddr_Type(enum.Enum):
####+END:
    finalDelivery= 'finalDelivery'

####+BEGIN: bx:cs:py3:section :title "Public Functions"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Public Functions*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:func/typing :funcName "controledQmailPrograms" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /controledQmailPrograms/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def controledQmailPrograms(
####+END:
) -> list[str]:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    progsList: list[str] = [
        "Global",
        "QmailInject",
        "QmailSend",
        "QmailRemote",
        "QmailSmtpd",
    ]

    return progsList


####+BEGIN: b:py3:cs:func/typing :funcName "meAsFqdnOnSys" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /meAsFqdnOnSys/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def meAsFqdnOnSys(
####+END:
) -> str:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    import socket
    fqdn = socket.getfqdn()
    return fqdn

####+BEGIN: bx:cs:py3:section :title "Public Classes"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Public Classes*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:


####+BEGIN: b:py3:class/decl :className "QmailControlFV" :superClass "object" :comment "Abstraction of a  Qmail Control File Variable" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /QmailControlFV/  superClass=object =Abstraction of a  Qmail Control File Variable=  [[elisp:(org-cycle)][| ]]
#+end_org """
class QmailControlFV(object):
####+END:
    """
** Abstraction of a Qmail Control File Variable
"""

    def __init__(
            self,
            qmailControlBaseDir: str="/var/qmail/control",
    ):
        self.qmailControlBaseDir = pathlib.Path(qmailControlBaseDir)

####+BEGIN: b:py3:cs:method/typing :methodName "fvSet" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /fvSet/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def fvSet(
####+END:
            self,
            fvName: str,
            fvValue: str,
    ) -> pathlib.Path:

        return b.fv.writeToBaseDir(self.qmailControlBaseDir, fvName, fvValue)

####+BEGIN: b:py3:cs:method/typing :methodName "fvGet" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /fvGet/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def fvGet(
####+END:
            self,
            fvName: str,
    ) -> str | None:

        fvGot = b.fv.readFromBaseDir(self.qmailControlBaseDir, fvName)
        return fvGot.rstrip()

####+BEGIN: b:py3:cs:method/typing :methodName "fvsDictSet" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /fvsDictSet/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def fvsDictSet(
####+END:
            self,
            fvsDict: typing.Dict[str, str],
    ) -> str | None:

        for fvName, fvValue in fvsDict.items():
            if fvValue  != "":
                self.fvSet(fvName, fvValue)

####+BEGIN: b:py3:cs:method/typing :methodName "fvsDictCurGet" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /fvsDictCurGet/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def fvsDictCurGet(
####+END:
            self,
            fvsDict: typing.Dict[str, str],
    ) -> typing.Dict[str, str]:

        result = {}

        for fvName, fvValueIn in fvsDict.items():
            fvValueCur = self.fvGet(fvName,)
            result[fvName] = fvValueCur

        return result


####+BEGIN: b:py3:class/decl :className "QCFV_Global" :superClass "QmailControlFV" :comment "" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /QCFV_Global/  superClass=QmailControlFV  [[elisp:(org-cycle)][| ]]
#+end_org """
class QCFV_Global(QmailControlFV):
####+END:
    """
** Abstraction of a Qmail Control File Variable
"""

    def __init__(
            self,
            qmailControlBaseDir: str="/var/qmail/control",
    ):
        super().__init__(qmailControlBaseDir,)

    @property
    def me(self):
        return self.fvGet("me")

    @me.setter
    def me(self, value):
        return self.fvSet("me", value)

####+BEGIN: b:py3:cs:method/typing :methodName "fvsDefaultDict" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /fvsDefaultDict/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def fvsDefaultDict(
####+END:
            self,
    ) -> typing.Dict[str, str]:

        sysFqdn = meAsFqdnOnSys()
        fvs = {
            "me": sysFqdn,
        }

        return fvs


####+BEGIN: b:py3:class/decl :className "QCFV_QmailInject" :superClass "QmailControlFV" :comment "" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /QCFV_QmailInject/  superClass=QmailControlFV  [[elisp:(org-cycle)][| ]]
#+end_org """
class QCFV_QmailInject(QmailControlFV):
####+END:
    """
** Abstraction of a Qmail Control File Variable
"""

    def __init__(
            self,
            qmailControlBaseDir: str="/var/qmail/control",
    ):
        super().__init__(qmailControlBaseDir,)

    @property
    def defaulthost(self):
        return self.fvGet("defaulthost")

    @defaulthost.setter
    def defaulthost(self, value):
        return self.fvSet("defaulthost", value)

####+BEGIN: b:py3:cs:method/typing :methodName "fvsDefaultDict" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /fvsDefaultDict/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def fvsDefaultDict(
####+END:
            self,
    ) -> typing.Dict[str, str]:

        globals = QCFV_Global()
        me = globals.me
        if me is None:
            return {}

        fvs = {
            "defaultdomain": me,
            "defaulthost": me,
            "idhost": me,
            "plusdomain": me,
        }

        return fvs


####+BEGIN: b:py3:class/decl :className "QCFV_QmailSend" :superClass "QmailControlFV" :comment "" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /QCFV_QmailSend/  superClass=QmailControlFV  [[elisp:(org-cycle)][| ]]
#+end_org """
class QCFV_QmailSend(QmailControlFV):
####+END:
    """
** Abstraction of a Qmail Control File Variable
"""

    def __init__(
            self,
            qmailControlBaseDir: str="/var/qmail/control",
    ):
        super().__init__(qmailControlBaseDir,)

    @property
    def bouncefrom(self):
        return self.fvGet("bouncefrom")

    @bouncefrom.setter
    def bouncefrom(self, value):
        return self.fvSet("bouncefrom", value)

    @property
    def locals(self):
        return self.fvGet("locals")

    @locals.setter
    def locals(self, value):
        return self.fvSet("locals", value)


####+BEGIN: b:py3:cs:method/typing :methodName "fvsDefaultDict" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /fvsDefaultDict/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def fvsDefaultDict(
####+END:
            self,
    ) -> typing.Dict[str, str]:

        globals = QCFV_Global()
        me = globals.me
        if me is None:
            return {}

        fvs = {
            "bouncefrom": "mailer-daemon",
            "bouncehost": me,
            "concurrencylocal": "10",
            "concurrencyremote": "20",
            "doublebouncehost": me,
            "doublebounceto": "postmaster",
            "envnoathost": me,
            "locals": me,
            "percenthack": "",
            "queuelifetime": "604800",
            "virtualdomains": "",
        }

        return fvs


####+BEGIN: b:py3:class/decl :className "QCFV_QmailRemote" :superClass "QmailControlFV" :comment "" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /QCFV_QmailRemote/  superClass=QmailControlFV  [[elisp:(org-cycle)][| ]]
#+end_org """
class QCFV_QmailRemote(QmailControlFV):
####+END:
    """
** Abstraction of a Qmail Control File Variable
"""

    def __init__(
            self,
            qmailControlBaseDir: str="/var/qmail/control",
    ):
        super().__init__(qmailControlBaseDir,)

####+BEGIN: b:py3:cs:method/typing :methodName "fvsDefaultDict" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /fvsDefaultDict/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def fvsDefaultDict(
####+END:
            self,
    ) -> typing.Dict[str, str]:

        globals = QCFV_Global()
        me = globals.me
        if me is None:
            return {}

        fvs = {
            "helohost": me,
            "smtproutes": "",
            "timeoutconnect": "60",
            "timeoutremote": "1200",
         }

        return fvs


####+BEGIN: b:py3:class/decl :className "QCFV_QmailSmtpd" :superClass "QmailControlFV" :comment "" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /QCFV_QmailSmtpd/  superClass=QmailControlFV  [[elisp:(org-cycle)][| ]]
#+end_org """
class QCFV_QmailSmtpd(QmailControlFV):
####+END:
    """
** Abstraction of a Qmail Control File Variable
"""

    def __init__(
            self,
            qmailControlBaseDir: str="/var/qmail/control",
    ):
        super().__init__(qmailControlBaseDir,)

####+BEGIN: b:py3:cs:method/typing :methodName "fvsDefaultDict" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /fvsDefaultDict/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def fvsDefaultDict(
####+END:
            self,
    ) -> typing.Dict[str, str]:

        globals = QCFV_Global()
        me = globals.me
        if me is None:
            return {}

        fvs = {
            "badmailfrom": "",
            "databytes": "",
            "localiphost": me,
            "rcpthosts": "",
            "morercpthosts": "cdbformat",
            "smtpgreeting": me,
            "timeoutsmtpd": "1200",
        }

        return fvs




####+BEGIN: bx:cs:py3:section :title "Common Parameters Specification"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Common Parameters Specification*  [[elisp:(org-cycle)][| ]]
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
    pass

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
        qmailFlavor: str = "wasQmail",
        sectionTitle: typing.AnyStr = "",
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Examples of Service Access Instance Commands.
    #+end_org """

    od = collections.OrderedDict
    cmnd = cs.examples.cmndEnter
    literal = cs.examples.execInsert

    # perfNamePars = od([('perfName', "HSS-1012"),])
    #cmnd('cmdbSummary', pars=perfNamePars, comment=" # remote obtain facter data, use it to summarize for cmdb")

    sysFqdn = meAsFqdnOnSys()

    cs.examples.menuChapter('=Qmail Control Me (as Sys-FQDN)=')

    cmnd('qmailControl_meAsFqdnOnSys', comment=f" # Based on System config, control/me={sysFqdn}")
    literal("hostname --fqdn", comment=" # usually used as control/me")
    cmnd('qmailControl_fvCurGet', args="me", comment=" # fvName")
    cmnd('qmailControl_fvCurSet', args=f"me {sysFqdn}", comment=" # fvName")

    cs.examples.menuChapter('=Qmail Control Programs=')

    cmnd('qmailControl_programs', comment=" # List of programs to which qmailControl FVs apply")

    cs.examples.menuChapter('=Qmail Control Defaults Show=')

    cmnd('qmailControl_defaultsShow', args="all", comment=" # Defaults For: QmailInject, QmailSend")
    cmnd('qmailControl_defaultsShow', args="QmailInject", comment=" # Defaults For QmailInject")
    cmnd('qmailControl_defaultsShow', args="QmailSmtpd", comment=" # Defaults For QmailSmtpd")

    cs.examples.menuChapter('=Qmail Control Defaults Set=')

    cmnd('qmailControl_defaultsSet', args="all", comment=" # Defaults For: QmailInject, QmailSend")
    cmnd('qmailControl_defaultsSet', args="QmailInject", comment=" # Defaults For QmailInject")
    cmnd('qmailControl_defaultsSet', args="QmailSmtpd", comment=" # Defaults For QmailSmtpd")

    cs.examples.menuChapter('=Qmail File Variables Get Current Values=')

    cmnd('qmailControl_fvsCurGet', args="all", comment=" # Defaults For: QmailInject, QmailSend")
    cmnd('qmailControl_fvsCurGet', args="QmailInject", comment=" # Defaults For QmailInject")
    cmnd('qmailControl_fvsCurGet', args="QmailSmtpd", comment=" # Defaults For QmailSmtpd")

    cs.examples.menuChapter('=Qmail File Variable  Get Each=')

    cmnd('qmailControl_fvCurGet', args="me", comment=" # fvName")
    cmnd('qmailControl_fvCurGet', args="Global me", comment=" # Arg1 is one of: Global, QmailInject, QmailSend")

    cs.examples.menuChapter('=Qmail File Variable Set Each=')

    cmnd('qmailControl_fvCurSet', args="me someValue", comment=" # fvName")
    cmnd('qmailControl_fvCurSet', args="Global me someValue", comment=" # Arg1 is one of: Global, QmailInject, QmailSend")

    cs.examples.menuChapter('=Qmail File Variable Default Show Each=')

    cmnd('qmailControl_fvDefaultShow', args="me", comment=" # fvName")
    cmnd('qmailControl_fvDefaultShow', args="Global me", comment=" # Arg1 is one of: Global, QmailInject, QmailSend")

    cs.examples.menuChapter('=Raw Qmail Commands (qmail-showctl)=')

    literal("/var/qmail/bin/qmail-showctl", comment=" # part of qmail")

    cs.examples.menuChapter('=Qmail Control Full Update (set all default FVs)=')

    cmnd('qmailControl_fullUpdate', comment=f" # set all default FVs based on {sysFqdn}")


####+BEGIN: bx:cs:py3:section :title "CS-Commands"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *CS-Commands*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "qmailControl_fullUpdate" :comment "" :extent "verify" :parsMand "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<qmailControl_fullUpdate>>  =verify= ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class qmailControl_fullUpdate(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] CS wrapper for meAsFqdnOnSys
        #+end_org """)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  qmailControl.cs -i qmailControl_meAsFqdnOnSys
#+end_src
#+RESULTS:
: /bin/sh: 2: qmailControl.cs: not found
        #+end_org """)

        qmailControl_defaultsSet().pyCmnd(argsList=["all"])
        return(cmndOutcome)

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "qmailControl_meAsFqdnOnSys" :comment "" :extent "verify" :parsMand "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<qmailControl_meAsFqdnOnSys>>  =verify= ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class qmailControl_meAsFqdnOnSys(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] CS wrapper for meAsFqdnOnSys
        #+end_org """)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  qmailControl.cs -i qmailControl_meAsFqdnOnSys
#+end_src
#+RESULTS:
: /bin/sh: 2: qmailControl.cs: not found
        #+end_org """)

        return(cmndOutcome.set(opResults=meAsFqdnOnSys()))


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "qmailControl_programs" :comment "" :extent "verify" :parsMand "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<qmailControl_programs>>  =verify= ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class qmailControl_programs(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]
*** qmailControl_defaultsShow all /QmailInject
*** -
        #+end_org """)

        return(cmndOutcome.set(opResults=controledQmailPrograms()))


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "qmailControl_defaultsShow" :comment "" :extent "verify" :parsMand "" :argsMin 1 :argsMax 9999 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<qmailControl_defaultsShow>>  =verify= argsMin=1 argsMax=9999 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class qmailControl_defaultsShow(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 9999,}

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
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]
*** qmailControl_defaultsShow all /QmailInject
*** -
        #+end_org """)

        cmndArgsSpecDict = self.cmndArgsSpec()
        cmndArgs = self.cmndArgsGet("0&9999", cmndArgsSpecDict, argsList)

        result = "Success"

        if len(cmndArgs):
            if cmndArgs[0] == "all":
                cmndArgsSpec = cmndArgsSpecDict.argPositionFind("0&9999")
                argChoices = cmndArgsSpec.argChoicesGet()
                argChoices.pop(0)
                cmndArgs= argChoices

        for each in cmndArgs:
            thisModule = sys.modules[__name__]
            try:
                eachFvs = getattr(thisModule, f"QCFV_{each}")()
            except:
                b_io.eh.problem_usageError(f"{each} -- Un Known")
                result = "Failure"
                continue
            fvs = eachFvs.fvsDefaultDict()
            print(f"* {each} -- {fvs}")

        return(cmndOutcome.set(opResults=result))


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
            argName="cmndArgs",
            argDefault=None,
            argChoices=['all',] + controledQmailPrograms(),
            argDescription="List of qmail Programs"
        )

        return cmndArgsSpecDict

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "qmailControl_defaultsSet" :comment "" :extent "verify" :parsMand "" :argsMin 1 :argsMax 9999 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<qmailControl_defaultsSet>>  =verify= argsMin=1 argsMax=9999 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class qmailControl_defaultsSet(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 9999,}

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
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]
*** qmailControl_defaultsShow all /QmailInject
*** -
        #+end_org """)

        cmndArgsSpecDict = self.cmndArgsSpec()
        cmndArgs = self.cmndArgsGet("0&9999", cmndArgsSpecDict, argsList)

        result = "Success"

        if len(cmndArgs):
            if cmndArgs[0] == "all":
                cmndArgsSpec = cmndArgsSpecDict.argPositionFind("0&9999")
                argChoices = cmndArgsSpec.argChoicesGet()
                argChoices.pop(0)
                cmndArgs= argChoices

        for each in cmndArgs:
            thisModule = sys.modules[__name__]
            try:
                eachFvs = getattr(thisModule, f"QCFV_{each}")()
            except:
                b_io.eh.problem_usageError(f"{each} -- Un Known")
                result = "Failure"
                continue
            
            fvsDefault = eachFvs.fvsDefaultDict()

            qmailControlFV = QmailControlFV()
            qmailControlFV.fvsDictSet(fvsDefault)

            print(f"* Setting Defaults For {each}")

        return(cmndOutcome.set(opResults=result))


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
            argName="cmndArgs",
            argDefault=None,
            argChoices=['all',] + controledQmailPrograms(),
            argDescription="List of qmail Programs"
        )

        return cmndArgsSpecDict


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "qmailControl_fvsCurGet" :comment "" :extent "verify" :parsMand "" :argsMin 1 :argsMax 9999 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<qmailControl_fvsCurGet>>  =verify= argsMin=1 argsMax=9999 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class qmailControl_fvsCurGet(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 9999,}

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
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]
*** qmailControl_defaultsShow all /QmailInject
*** -
        #+end_org """)

        cmndArgsSpecDict = self.cmndArgsSpec()
        cmndArgs = self.cmndArgsGet("0&9999", cmndArgsSpecDict, argsList)

        result = "Success"

        if len(cmndArgs):
            if cmndArgs[0] == "all":
                cmndArgsSpec = cmndArgsSpecDict.argPositionFind("0&9999")
                argChoices = cmndArgsSpec.argChoicesGet()
                argChoices.pop(0)
                cmndArgs= argChoices

        for each in cmndArgs:
            thisModule = sys.modules[__name__]
            try:
                eachFvs = getattr(thisModule, f"QCFV_{each}")()
            except:
                b_io.eh.problem_usageError(f"{each} -- Un Known")
                result = "Failure"
                continue
            fvs = eachFvs.fvsDictCurGet(eachFvs.fvsDict())
            print(f"* {each} -- {fvs}")

        return(cmndOutcome.set(opResults=result))


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
            argName="cmndArgs",
            argDefault=None,
            argChoices=['all', 'QmailInject', 'QmailSend',],
            argDescription="List of qmail Programs"
        )

        return cmndArgsSpecDict


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "qmailControl_fvCurGet" :comment "" :extent "verify" :parsMand "" :argsMin 1 :argsMax 2 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<qmailControl_fvCurGet>>  =verify= argsMin=1 argsMax=9999 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class qmailControl_fvCurGet(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 9999,}

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
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]
*** qmailControl_defaultsShow all /QmailInject
*** -
        #+end_org """)

        cmndArgsSpecDict = self.cmndArgsSpec()
        cmndArgs = self.cmndArgsGet("0&2", cmndArgsSpecDict, argsList)

        qmailProgName: str | None  = None

        if len(cmndArgs) == 2:
            qmailProgName = cmndArgs[0]
            fvName = cmndArgs[1]
        elif len(cmndArgs) == 1:
            fvName = cmndArgs[0]
        else:
            b_io.eh.critical_oops()

        if qmailProgName is not None:
            # Validate if fvName is one of qmailProgName
            thisModule = sys.modules[__name__]
            try:
                defaultFvs = getattr(thisModule, f"QCFV_{qmailProgName}")()
            except:
                b_io.eh.problem_usageError(f"{qmailProgName} -- Un-Known qmailProgramName")
                return(cmndOutcome.set(opResults=None))
            else:
                if not fvName in defaultFvs.fvsDefaultDict():
                    b_io.eh.problem_usageError(f"{fvName} is not a File Variable of {qmailProgName}")
                    return(cmndOutcome.set(opResults=None))

        qmailControlFV = QmailControlFV()
        result = qmailControlFV.fvGet(fvName)

        return(cmndOutcome.set(opResults=result))


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
            argPosition="0&1",
            argName="progOrFvName",
            argDefault=None,
            argChoices=[],
            argDescription=""
        )
        cmndArgsSpecDict.argsDictAdd(
            argPosition="1&2",
            argName="fvName",
            argDefault=None,
            argChoices=[],
            argDescription=""
        )

        return cmndArgsSpecDict



####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "qmailControl_fvCurSet" :comment "" :extent "verify" :parsMand "" :argsMin 2 :argsMax 3 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<qmailControl_fvCurSet>>  =verify= argsMin=2 argsMax=3 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class qmailControl_fvCurSet(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 2, 'Max': 3,}

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
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]
*** qmailControl_defaultsShow all /QmailInject
*** -
        #+end_org """)

        cmndArgsSpecDict = self.cmndArgsSpec()
        cmndArgs = self.cmndArgsGet("0&3", cmndArgsSpecDict, argsList)

        qmailProgName: str | None  = None

        if len(cmndArgs) == 3:
            qmailProgName = cmndArgs[0]
            fvName = cmndArgs[1]
            fvValue = cmndArgs[2]
        elif len(cmndArgs) == 2:
            fvName = cmndArgs[0]
            fvValue = cmndArgs[1]
        else:
            b_io.eh.critical_oops()

        if qmailProgName is not None:
            # Validate if fvName is one of qmailProgName
            thisModule = sys.modules[__name__]
            try:
                defaultFvs = getattr(thisModule, f"QCFV_{qmailProgName}")()
            except:
                b_io.eh.problem_usageError(f"{qmailProgName} -- Un-Known qmailProgramName")
                return(cmndOutcome.set(opResults=None))
            else:
                if not fvName in defaultFvs.fvsDefaultDict():
                    b_io.eh.problem_usageError(f"{fvName} is not a File Variable of {qmailProgName}")
                    return(cmndOutcome.set(opResults=None))

        qmailControlFV = QmailControlFV()
        result = qmailControlFV.fvSet(fvName, fvValue)

        return(cmndOutcome.set(opResults=result))


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
            argPosition="0&1",
            argName="progOrFvName",
            argDefault=None,
            argChoices=[],
            argDescription=""
        )
        cmndArgsSpecDict.argsDictAdd(
            argPosition="1&3",
            argName="fvName",
            argDefault=None,
            argChoices=[],
            argDescription=""
        )

        return cmndArgsSpecDict


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "qmailControl_fvDefaultShow" :comment "" :extent "verify" :parsMand "" :argsMin 1 :argsMax 2 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<qmailControl_fvDefaultShow>>  =verify= argsMin=1 argsMax=2 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class qmailControl_fvDefaultShow(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 2,}

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
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]
*** qmailControl_defaultsShow all /QmailInject
*** -
        #+end_org """)

        cmndArgsSpecDict = self.cmndArgsSpec()
        cmndArgs = self.cmndArgsGet("0&2", cmndArgsSpecDict, argsList)

        result = "Success"

        qmailProgName: str | None  = None

        if len(cmndArgs) == 2:
            qmailProgName = cmndArgs[0]
            fvName = cmndArgs[1]
        elif len(cmndArgs) == 1:
            fvName = cmndArgs[0]
        else:
            b_io.eh.critical_oops()

        if qmailProgName is not None:
            # Validate if fvName is one of qmailProgName
            thisModule = sys.modules[__name__]
            try:
                defaultFvs = getattr(thisModule, f"QCFV_{qmailProgName}")()
            except:
                b_io.eh.problem_usageError(f"{qmailProgName} -- Un-Known qmailProgramName")
                return(cmndOutcome.set(opResults=None))
            else:
                if not fvName in defaultFvs.fvsDefaultDict():
                    b_io.eh.problem_usageError(f"{fvName} is not a File Variable of {qmailProgName}")
                    return(cmndOutcome.set(opResults=None))

        for each in controledQmailPrograms():
            thisModule = sys.modules[__name__]
            try:
                eachFvs = getattr(thisModule, f"QCFV_{each}")()
            except:
                b_io.eh.problem_usageError(f"{each} -- Un Known")
                result = "Failure"
                continue
            fvs = eachFvs.fvsDefaultDict()
            if fvName in fvs:
                print(f"* {each} -- {fvName} {fvs[fvName]}")

        return(cmndOutcome.set(opResults=result))


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
            argPosition="0&1",
            argName="progOrFvName",
            argDefault=None,
            argChoices=[],
            argDescription=""
        )
        cmndArgsSpecDict.argsDictAdd(
            argPosition="1&2",
            argName="fvName",
            argDefault=None,
            argChoices=[],
            argDescription=""
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
