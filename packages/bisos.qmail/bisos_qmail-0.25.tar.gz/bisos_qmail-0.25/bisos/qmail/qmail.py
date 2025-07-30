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
** This File: /bisos/git/auth/bxRepos/bisos-pip/marmee/py3/bisos/marmee/aasInMailOfflineimap.py
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


####+BEGIN: b:py3:cs:orgItem/basic :type "=PyImports= " :title "*Py Library IMPORTS*" :comment "-- with classification based framework/imports"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  =PyImports=  [[elisp:(outline-show-subtree+toggle)][||]] *Py Library IMPORTS* -- with classification based framework/imports  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:framework/imports :basedOn "classification"
""" #+begin_org
** Imports Based On Classification=cs-lib
#+end_org """
from bisos import b
from bisos.b import cs
from bisos.b import b_io

####+END:

import collections

import collections
import pathlib
import os
#import shutil

from bisos.common import csParam

# from bisos.qmail import maildrop

from bisos.basics import pyRunAs
from bisos.basics import basics
# from bisos.common import lines

from bisos.qmail import qmailControl

import enum
import pathlib

import pwd


####+BEGIN: bx:dblock:python:section :title "Enumerations"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Enumerations*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:

####+BEGIN: bx:dblock:python:enum :enumName "qmailCmndExit_Code" :comment ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Enum       [[elisp:(outline-show-subtree+toggle)][||]] /qmailCmndExit_Code/  [[elisp:(org-cycle)][| ]]
#+end_org """
@enum.unique
class qmailCmndExit_Code(enum.Enum):
####+END:
    qmailCmndExitSuccess=0
    qmailCmndExitSuccessFinish=99
    qmailCmndExitFailHard=100
    qmailCmndExitFailSoft=111

####+BEGIN: bx:dblock:python:enum :enumName "acctAddr_Type" :comment ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Enum       [[elisp:(outline-show-subtree+toggle)][||]] /acctAddr_Type/  [[elisp:(org-cycle)][| ]]
#+end_org """
@enum.unique
class acctAddr_Type(enum.Enum):
####+END:
    finalDelivery = 'finalDelivery'



####+BEGIN: bx:cs:py3:section :title "Public Classes"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Public Functions*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:


####+BEGIN: b:py3:class/decl :className "QmailInstallationSingleton" :superClass "object" :comment "Abstraction of a  Interface" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /QmailInstallationSingleton/  superClass=object =Abstraction of a  Interface=  [[elisp:(org-cycle)][| ]]
#+end_org """
class QmailInstallationSingleton(object):
####+END:
    """
** Abstraction of
"""
    _instance = None

    # Singleton using New
    def __new__(cls):
        if cls._instance is None:
            # print('Creating the object')
            cls._instance = super(QmailInstallationSingleton, cls).__new__(cls)
            # Put any initialization here.
        return cls._instance

    def __init__(
            self,
    ):
        self._varDir = pathlib.Path("MISSING")
        varDir =  pathlib.Path("/var/qmail")
        if varDir.is_dir():
            self._varDir = varDir
        else:
            varDir =  pathlib.Path("/var/lib/qmail")
            if varDir.is_dir():
                self._varDir = varDir

        self._binBaseDir = pathlib.Path("MISSING")
        binBaseDir =  pathlib.Path("/var/qmail/bin")
        if binBaseDir.is_dir():
            self._binBaseDir = binBaseDir
        else:
            if pathlib.Path("/usr/sbin/qmail-inject").is_file():
                self._binBaseDir = pathlib.Path("/usr/sbin")

        self._controlBaseDir = pathlib.Path("MISSING")
        controlBaseDir =  pathlib.Path("/var/qmail/control")
        if controlBaseDir.is_dir():
            self._controlBaseDir = controlBaseDir
        else:
            controlBaseDir =  pathlib.Path("/etc/qmail")
            if controlBaseDir.is_dir():
                self._controlBaseDir = controlBaseDir

        self._usersBaseDir = self._varDir.joinpath("users")

    def fullProgPath(self, progName: str,):
        return str(self._binBaseDir.joinpath(progName))

    @property
    def varDir(self) -> pathlib.Path:
        return self._varDir

    @property
    def binBaseDir(self) -> pathlib.Path:
        return self._binBaseDir

    @property
    def controlBaseDir(self) -> pathlib.Path:
        return self._controlBaseDir

    @property
    def usersBaseDir(self) -> pathlib.Path:
        return self._usersBaseDir


installation = QmailInstallationSingleton()


####+BEGIN: b:py3:class/decl :className "LocalDeliveryAcct" :superClass "object" :comment "Abstraction of a qmail delivery account a set of statics" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /LocalDeliveryAcct/  superClass=object =Abstraction of a qmail delivery account a set of statics=  [[elisp:(org-cycle)][| ]]
#+end_org """
class LocalDeliveryAcct(object):
####+END:
    """
** Abstraction of a Local Delivery Acct
"""

    def __init__(
            self,
    ):
        pass

####+BEGIN: b:py3:cs:method/typing :methodName "ensureUsersBaseDir" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /ensureUsersBaseDir/  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def ensureUsersBaseDir(
####+END:
            inOutcome: b.op.Outcome | None =None,
    )-> b.op.Outcome:

        if inOutcome is None:
            outcome = b.op.Outcome()
        else:
            outcome = inOutcome

        result: typing.Any = None

        if installation.usersBaseDir.is_dir():
            result = f"""usersBaseDir={str(installation.usersBaseDir)} exists, creation skipped"""
            return outcome.set(opResults=result)

        pyRunAs.as_root_osSystem(
            f"""mkdir {str(installation.usersBaseDir)}"""
        )
        pyRunAs.as_root_osSystem(
            f"""chmod 755 {str(installation.usersBaseDir)}"""
        )

        includePath = installation.usersBaseDir.joinpath("include")
        if not includePath.is_file():
            basics.File.writeWithStr(includePath, "", perhapsAsRoot=True)

        assignPath = installation.usersBaseDir.joinpath("assign")
        if not assignPath.is_file():
            basics.File.writeWithStr(assignPath, "", perhapsAsRoot=True)

        result = f"""Created usersBaseDir={str(installation.usersBaseDir)}"""
        return outcome.set(opResults=result)


####+BEGIN: b:py3:cs:method/typing :methodName "newUserProc" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /newUserProc/  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def newUserProc(
####+END:
            inOutcome: b.op.Outcome | None =None,
    )-> b.op.Outcome:

        results: str = ""

        if inOutcome is None:
            outcome = b.op.Outcome()
            if outcome.results:
                results = outcome.results
        else:
            outcome = inOutcome

        qmailPw2uProgram = installation.binBaseDir.joinpath("qmail-pw2u")
        qmailNewuProgram = installation.binBaseDir.joinpath("qmail-newu")

        if b.subProc.Op(outcome=outcome, uid="root", log=1).bash(
                f"""\
cat /etc/passwd | {qmailPw2uProgram}  > {installation.usersBaseDir}/assign
{qmailNewuProgram}
""",
        ).isProblematic():  return(b_io.eh.badOutcome(outcome))

        results = results + "LocalDeliveryAcct.newUserProc: processed users\n"
        return outcome.set(opResults=results)

####+BEGIN: b:py3:cs:method/typing :methodName "add" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /add/  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def add(
####+END:
            user: str,
            inOutcome: b.op.Outcome | None =None,
    )-> b.op.Outcome:

        results: str = ""

        if inOutcome is None:
            outcome = b.op.Outcome()
            if outcome.results:
                results = outcome.results
        else:
            outcome = inOutcome

        try:
            pwd.getpwnam(user)
        except KeyError:
            outcome.error = 1
            outcome.errInfo = "Missing Passwd Account"
            return outcome

        LocalDeliveryAcct.ensureUsersBaseDir()

        includePath = installation.usersBaseDir.joinpath("include")
        if basics.FileLine.isIn(includePath, user):
            results = f"""basics.FileLine.isIn: {user} already in {includePath}, Addition skipped"""
            return outcome.set(opResults=results)

        basics.FileLine.appendIfNotThere(includePath, user, perhapsAsRoot=True)

        LocalDeliveryAcct.newUserProc(outcome)

        results = outcome.results + f"""LocalDeliveryAcct.add: Added {user} to {includePath}"""
        return outcome.set(opResults=results)

####+BEGIN: b:py3:cs:method/typing :methodName "delete" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /delete/  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def delete(
####+END:
            user: str,
            inOutcome: b.op.Outcome | None =None,
    )-> b.op.Outcome:

        results: str = ""

        if inOutcome is None:
            outcome = b.op.Outcome()
            if outcome.results:
                results = outcome.results
        else:
            outcome = inOutcome

        try:
            pwd.getpwnam(user)
        except KeyError:
            outcome.error = 1
            outcome.errInfo = "Missing Passwd Account"
            return outcome

        LocalDeliveryAcct.ensureUsersBaseDir()

        includePath = installation.usersBaseDir.joinpath("include")
        if not basics.FileLine.isIn(includePath, user):
            results = f"""basics.FileLine.isIn: {user} not in {includePath}, deletion skipped"""
            return outcome.set(opResults=results)

        basics.FileLine.remove(includePath, user, perhapsAsRoot=True)

        LocalDeliveryAcct.newUserProc(outcome)

        results = outcome.results + f"""LocalDeliveryAcct.add: removed {user} from {includePath}"""
        return outcome.set(opResults=results)

####+BEGIN: b:py3:cs:method/typing :methodName "verify" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /verify/  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def verify(
####+END:
            user: str,
            inOutcome: b.op.Outcome | None =None,
    )-> b.op.Outcome:

        results: str = ""

        if inOutcome is None:
            outcome = b.op.Outcome()
            if outcome.results:
                results = outcome.results
        else:
            outcome = inOutcome

        try:
            pwd.getpwnam(user)
        except KeyError:
            outcome.error = 1
            outcome.errInfo = "Missing Passwd Account"
            return outcome

        assignPath = installation.usersBaseDir.joinpath("assign")
        if basics.FileLine.isIn(assignPath, f":{user}:"):
            results = f"""LocalDeliveryAcct.verify: {user} is in {assignPath}"""
            return outcome.set(opResults=results)
        else:
            outcome.error = 2
            outcome.errInfo = "Not in assign file"
            return outcome

####+BEGIN: b:py3:cs:method/typing :methodName "mainDomainGet" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /mainDomainGet/  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def mainDomainGet(
####+END:
            inOutcome: b.op.Outcome | None =None,
    )-> b.op.Outcome:

        results: str = ""

        if inOutcome is None:
            outcome = b.op.Outcome()
            if outcome.results:
                results = outcome.results
        else:
            outcome = inOutcome

        results = qmailControl.QCFV_QmailSend().locals
        return outcome.set(opResults=results)


####+BEGIN: b:py3:class/decl :className "LocalDeliveryAction" :superClass "object" :comment "Invoke qmail-local with static methods" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /LocalDeliveryAction/  superClass=object =Invoke qmail-local with static methods=  [[elisp:(org-cycle)][| ]]
#+end_org """
class LocalDeliveryAction(object):
####+END:
    """
** Abstraction of a Local Delivery Acct
"""

    def __init__(
            self,
    ):
        pass

####+BEGIN: b:py3:cs:method/typing :methodName "testShow" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /testShow/  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def testShow(
####+END:
            inOutcome: b.op.Outcome | None =None,
    )-> b.op.Outcome:
        """
  mmaQmail_dotQmailFile=${opAcct_homeDir}/.qmail
  typeset dotQmailFile=${mmaQmail_dotQmailFile}

  EH_assert [[ -f ${dotQmailFile}-${localPart} ]]

  opDo eval "qmail-local -n ${opAcct_name} ${opAcct_homeDir} ${opAcct_name} '-' '${localPart}' '' '' ${dotQmailFile}"
        """

        if inOutcome is None:
            outcome = b.op.Outcome()
        else:
            outcome = inOutcome

        result: typing.Any = None
        return outcome.set(opResults=result)


####+BEGIN: b:py3:class/decl :className "Maildir" :superClass "object" :comment "Abstraction of Maildir CRUD" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /Maildir/  superClass=object =Abstraction of Maildir CRUD=  [[elisp:(org-cycle)][| ]]
#+end_org """
class Maildir(object):
####+END:
    """
** Abstraction of Maildir CRUD
"""

    def __init__(
            self,
    ):
        pass

####+BEGIN: b:py3:cs:method/typing :methodName "create" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /create/  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def create(
####+END:
            qAddrAcct: str,
            maildirsList: list[str],
            inOutcome: b.op.Outcome | None =None,
    )-> b.op.Outcome:
        """
        maildirFullPath = pathlib.Path(os.path.join(dataBase, 'maildir'))

        if not maildirFullPath.is_dir():
            maildirFullPath.mkdir(parents=True, exist_ok=True)

        for eachMaildir in maildirNames:
            hereMaildirMainBase = maildirFullPath.joinpath(eachMaildir)

            if not hereMaildirMainBase.joinpath('new').is_dir():
                if not (resStr := b.subProc.WOpW(invedBy=self, log=1).bash(
                    f'maildirmake {hereMaildirMainBase}',
                ).stdout):
                    b_io.eh.badOutcome(cmndOutcome)
                    #return(b_io.eh.badOutcome(cmndOutcome))
        """

        if inOutcome is None: outcome = b.op.Outcome()
        else: outcome = inOutcome

        result: typing.Any = None

        for eachMaildir in maildirsList:
            hereMaildirMainBase = pathlib.Path(eachMaildir)

            if not hereMaildirMainBase.joinpath('new').is_dir():
                if not (resStr := b.subProc.WOpW(invedBy=None, log=1).bash(
                    f'maildirmake {hereMaildirMainBase}',
                ).stdout):
                    b_io.eh.badOutcome(outcome)

        return outcome.set(opResults=result)

####+BEGIN: b:py3:cs:method/typing :methodName "verify" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /verify/  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def verify(
####+END:
            qAddrAcct: str,
            maildirsList: list[str],
            inOutcome: b.op.Outcome | None =None,
    )-> b.op.Outcome:
        """
        """

        return "NOTYET"

        if inOutcome is None: outcome = b.op.Outcome()
        else: outcome = inOutcome

        result: typing.Any = None

        for eachMaildir in maildirsList:
            hereMaildirMainBase = pathlib.Path(eachMaildir)

            if not hereMaildirMainBase.joinpath('new').is_dir():
                if not (resStr := b.subProc.WOpW(invedBy=None, log=1).bash(
                    f'maildirmake {hereMaildirMainBase}',
                ).stdout):
                    b_io.eh.badOutcome(outcome)

        return outcome.set(opResults=result)

####+BEGIN: b:py3:cs:method/typing :methodName "delete" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /delete/  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def delete(
####+END:
            qAddrAcct: str,
            maildirsList: list[str],
            inOutcome: b.op.Outcome | None =None,
    )-> b.op.Outcome:
        """
        """

        return "NOTYET"
        
        if inOutcome is None: outcome = b.op.Outcome()
        else: outcome = inOutcome

        result: typing.Any = None

        for eachMaildir in maildirsList:
            hereMaildirMainBase = pathlib.Path(eachMaildir)

            if not hereMaildirMainBase.joinpath('new').is_dir():
                if not (resStr := b.subProc.WOpW(invedBy=None, log=1).bash(
                    f'maildirmake {hereMaildirMainBase}',
                ).stdout):
                    b_io.eh.badOutcome(outcome)

        return outcome.set(opResults=result)


####+BEGIN: b:py3:class/decl :className "DotQmailFile" :superClass "object" :comment "Abstraction of a dotQmail" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /DotQmailFile/  superClass=object =Abstraction of a dotQmail=  [[elisp:(org-cycle)][| ]]
#+end_org """
class DotQmailFile(object):
####+END:
    """
** Abstraction of a dotQmail
"""

    def __init__(
            self,
            qAddrAcct,
            localPart,
    ):

        self.qAddrAcct = qAddrAcct
        self.localPart = localPart

####+BEGIN: b:py3:cs:method/typing :methodName "acctPath" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /acctPath/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def acctPath(
####+END:
            self,
    ) -> pathlib.Path:
        return pathlib.Path(os.path.expanduser(f'~{self.qAddrAcct}'))

####+BEGIN: b:py3:cs:method/typing :methodName "nameOfLocalPart" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /nameOfLocalPart/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def nameOfLocalPart(
####+END:
            self,
    ) -> pathlib.Path:
        if self.localPart =="":
            return pathlib.Path(f".qmail")
        else:
            return pathlib.Path(f".qmail-{self.localPart}")

####+BEGIN: b:py3:cs:method/typing :methodName "filePath" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /filePath/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def filePath(
####+END:
            self,
    ) -> pathlib.Path:
        return (
            self.acctPath().joinpath(
               self.nameOfLocalPart()
            )
        )

####+BEGIN: b:py3:cs:method/typing :methodName "contentRead" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /contentRead/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def contentRead(
####+END:
            self,
    ) -> str:
        return (
            pyRunAs.as_root_readFromFile(
                self.filePath()
            )
        )

####+BEGIN: b:py3:cs:method/typing :methodName "contentWrite" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /contentWrite/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def contentWrite(
####+END:
            self,
            content: str,
            inOutcome: b.op.Outcome | None =None,
    )-> b.op.Outcome:
        """
        """
        if inOutcome is None: outcome = b.op.Outcome()
        else: outcome = inOutcome.adopt()

        result: typing.Any = None

        pyRunAs.as_root_writeToFile(
            self.filePath(),
            content,
        )
        pyRunAs.as_root_osSystem(
            f"""chown {self.qAddrAcct} {self.filePath()}"""
        )
        pyRunAs.as_root_osSystem(
            f"""chmod 600 {self.filePath()}"""
        )

        outcome.report(f"Wrote dotQmail={self.filePath()}")

        os.system(f"ls -l {self.filePath()}")

        outcome.set(opResults=result)


####+BEGIN: b:py3:cs:method/typing :methodName "addMaildirLine" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /addMaildirLine/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def addMaildirLine(
####+END:
            self,
            maildirPath: str,
            inOutcome: b.op.Outcome | None =None,
    )-> b.op.Outcome:
        """
        """
        if inOutcome is None: outcome = b.op.Outcome()
        else: outcome = inOutcome.adopt()

        result: typing.Any = None

        if not self.filePath().is_file():
            basics.File.writeWithStr(self.filePath(), "", perhapsAsRoot=True)
        else:
            if basics.FileLine.isIn(self.filePath(), maildirPath, perhapsAsRoot=True):
                outcome.report(f"""basics.FileLine.isIn: {maildirPath} already in {self.filePath()}, Addition skipped""")
                return outcome.set(opResults=result)

        basics.FileLine.appendIfNotThere(self.filePath(), maildirPath, perhapsAsRoot=True)

        pyRunAs.as_root_osSystem(
            f"""chown {self.qAddrAcct} {self.filePath()}"""
        )
        pyRunAs.as_root_osSystem(
            f"""chmod 600 {self.filePath()}"""
        )
        outcome.report(f"""Added {maildirPath} to {self.filePath()}""")
        return outcome.set(opResults=result)

####+BEGIN: b:py3:cs:method/typing :methodName "addForwardLine" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /addForwardLine/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def addForwardLine(
####+END:
            self,
            destAddr: str,
            inOutcome: b.op.Outcome | None =None,
    )-> b.op.Outcome:
        """
        """
        if inOutcome is None: outcome = b.op.Outcome()
        else: outcome = inOutcome.adopt()

        result: typing.Any = None

        if not self.filePath().is_file():
            basics.File.writeWithStr(self.filePath(), "", perhapsAsRoot=True)
        else:
            if basics.FileLine.isIn(self.filePath(), destAddr, perhapsAsRoot=True):
                outcome.report(f"""basics.FileLine.isIn: {destAddr} already in {self.filePath()}, Addition skipped""")
                return outcome.set(opResults=result)

        basics.FileLine.appendIfNotThere(self.filePath(), f"&{destAddr}", perhapsAsRoot=True)

        pyRunAs.as_root_osSystem(
            f"""chown {self.qAddrAcct} {self.filePath()}"""
        )
        pyRunAs.as_root_osSystem(
            f"""chmod 600 {self.filePath()}"""
        )
        outcome.report(f"""Added {destAddr} to {self.filePath()}""")
        return outcome.set(opResults=result)


####+BEGIN: b:py3:cs:method/typing :methodName "deleteLine" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /deleteLine/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def deleteLine(
####+END:
           self,
            line: str,
            inOutcome: b.op.Outcome | None =None,
    )-> b.op.Outcome:
        """
        """
        if inOutcome is None: outcome = b.op.Outcome()
        else: outcome = inOutcome.adopt()

        result: typing.Any = None


        result = basics.FileLine.remove(self.filePath(), line, perhapsAsRoot=True)

        pyRunAs.as_root_osSystem(
            f"""chown {self.qAddrAcct} {self.filePath()}"""
        )
        pyRunAs.as_root_osSystem(
            f"""chmod 600 {self.filePath()}"""
        )
        if result == True:
            outcome.report(f"""Removed  {line} from {self.filePath()}""")
        else:
            outcome.report(f"""{self.filePath()} does not contain {line}, removal skipped""")

        return outcome.set(opResults=result)



####+BEGIN: b:py3:cs:method/typing :methodName "deliveryStatus" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /deliveryStatus/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def deliveryStatus(
####+END:
            self,
    ) -> None:
        """
  findResult=$( find ${opAcct_homeDir} -maxdepth 0 -perm -01000 )
  if [[ ${findResult} == ${opAcct_homeDir} ]] ; then
    ANT_raw "Sticky Bit Set, Delivery is On Hold"
    opDo ls -ld ${opAcct_homeDir}
  else
    ANT_raw "Sticky Bit NOT Set, Normal Delivery"
    opDo ls -ld ${opAcct_homeDir}
  fi
         """
        pass

####+BEGIN: b:py3:cs:method/typing :methodName "deliveryPause" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /deliveryPause/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def deliveryPause(
####+END:
            self,
    ) -> None:
        """
          opDo chmod +t ${opAcct_homeDir}
  opDo ls -ld ${opAcct_homeDir}
         """
        pass

####+BEGIN: b:py3:cs:method/typing :methodName "deliveryResume" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /deliveryResume/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def deliveryResume(
####+END:
            self,
    ) -> None:
        """
          opDo chmod -t ${opAcct_homeDir}
  opDo ls -ld ${opAcct_homeDir}
         """
        pass


####+BEGIN: b:py3:class/decl :className "VirDomEntry" :superClass "object" :comment "Abstraction of a VidrDom Entry" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /VirDomEntry/  superClass=object =Abstraction of a VidrDom Entry=  [[elisp:(org-cycle)][| ]]
#+end_org """
class VirDomEntry(object):
####+END:
    """
** Abstraction of a Local Delivery Acct
"""

    def __init__(
            self,
    ):
        pass

####+BEGIN: b:py3:cs:method/typing :methodName "add" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /add/  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def add(
####+END:
            virDomName: str,
            virDomAcct: str,
    )-> b.op.Outcome:
        outcome = b.op.Outcome()

        if b.subProc.Op(outcome=outcome, uid="root", log=1).bash(
                f"""\
  if USER_isInPasswdFile ${2} ; then
    FN_lineAddToFile "^${1}:${2}\$" "${1}:${2}" ${qmailVirDomFile}
  else
    print "$0: Skipping ${2} because it is not in the passwd file"
    return 2
  fi

  #grep ${2} ${qmailVirDomFile}

  print "pkill -HUP 'qmail-send'"
  pkill -HUP 'qmail-send'
""",
        ).isProblematic():  return(b_io.eh.badOutcome(outcome))
        return outcome

####+BEGIN: b:py3:cs:method/typing :methodName "delete" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /delete/  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def delete(
####+END:
            virDomName: str,
            virDomAcct: str,
    )-> b.op.Outcome:
        outcome = b.op.Outcome()

        if b.subProc.Op(outcome=outcome, uid="root", log=1).bash(
                f"""\
  if USER_isInPasswdFile ${2} ; then
    FN_lineRemoveFromFile "^${1}:${2}\$" ${qmailVirDomFile}
  else
    print "$0: Skipping ${2} because it is not in the passwd file"
    return 2
  fi

  #grep ${2} ${qmailVirDomFile}

  print "pkill -HUP 'qmail-send'"
  pkill -HUP 'qmail-send'
""",
        ).isProblematic():  return(b_io.eh.badOutcome(outcome))
        return outcome


####+BEGIN: b:py3:cs:method/typing :methodName "acctGet" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /acctGet/  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def acctGet(
####+END:
            user: str,
    )-> b.op.Outcome:
        outcome = b.op.Outcome()

        if b.subProc.Op(outcome=outcome, uid="root", log=1).bash(
                f"""\
  typeset acctName=`egrep "^$1:" ${qmailVirDomFile} | cut -d : -f 2`

  if [[ "${acctName}_" == "_" ]] ; then
    EH_problem "$1 not found in ${qmailVirDomFile}"
    return 1
  fi

  print ${acctName}
""",
        ).isProblematic():  return(b_io.eh.badOutcome(outcome))
        return outcome

####+BEGIN: b:py3:cs:method/typing :methodName "domainGet" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /domainGet/  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def domainGet(
####+END:
            user: str,
    )-> b.op.Outcome:
        outcome = b.op.Outcome()

        if b.subProc.Op(outcome=outcome, uid="root", log=1).bash(
                f"""\
   typeset domainName=`egrep ":$1$" ${qmailVirDomFile} | cut -d : -f 1`

  if [[ "${domainName}_" == "_" ]] ; then
    EH_problem "$1 not found in ${qmailVirDomFile}"
    return 1
  fi

  print ${domainName}
""",
        ).isProblematic():  return(b_io.eh.badOutcome(outcome))
        return outcome



####+BEGIN: b:py3:class/decl :className "RcpthostsEntry" :superClass "object" :comment "Abstraction of RcpthostsEntry" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /RcpthostsEntry/  superClass=object =Abstraction of RcpthostsEntry=  [[elisp:(org-cycle)][| ]]
#+end_org """
class RcpthostsEntry(object):
####+END:
    """
** Abstraction of RcpthostsEntry
"""

    def __init__(
            self,
    ):
        pass

####+BEGIN: b:py3:cs:method/typing :methodName "add" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /add/  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def add(
####+END:
            user: str,
    )-> b.op.Outcome:
        outcome = b.op.Outcome()

        if b.subProc.Op(outcome=outcome, uid="root", log=1).bash(
                f"""\
  FN_lineAddToFile "^${1}\$" "${1}"  ${qmailControlBaseDir}/rcpthosts

""",
        ).isProblematic():  return(b_io.eh.badOutcome(outcome))
        return outcome

####+BEGIN: b:py3:cs:method/typing :methodName "delete" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /delete/  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def delete(
####+END:
            user: str,
    )-> b.op.Outcome:
        outcome = b.op.Outcome()

        if b.subProc.Op(outcome=outcome, uid="root", log=1).bash(
                f"""\
  FN_lineRemoveFromFile "^${1}\$" ${qmailControlBaseDir}/rcpthosts
""",
        ).isProblematic():  return(b_io.eh.badOutcome(outcome))
        return outcome

####+BEGIN: b:py3:cs:method/typing :methodName "verify" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /verify/  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def verify(
####+END:
            user: str,
    )-> b.op.Outcome:
        outcome = b.op.Outcome()

        if b.subProc.Op(outcome=outcome, uid="root", log=1).bash(
                f"""\
echo NOTYET
""",
        ).isProblematic():  return(b_io.eh.badOutcome(outcome))
        return outcome

####+BEGIN: b:py3:class/decl :className "VirDom" :superClass "object" :comment "Abstraction of a Virtual Domain" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /VirDom/  superClass=object =Abstraction of a Virtual Domain=  [[elisp:(org-cycle)][| ]]
#+end_org """
class VirDom(object):
####+END:
    """
** Abstraction of a Virtual Domain
"""

    def __init__(
            self,
    ):
        pass

####+BEGIN: b:py3:cs:method/typing :methodName "update" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /update/  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def update(
####+END:
            virDomName: str,
            virDomAcct: str,
    )-> b.op.Outcome:
        outcome = b.op.Outcome()

        if b.subProc.Op(outcome=outcome, uid="root", log=1).bash(
                f"""\
  opDoRet mmaQmailLocDeliveryAcctAdd ${2}
  opDoRet mmaQmailVirDomEntryAdd ${1} ${2}
  opDoRet mmaQmailRcpthostsEntryAdd ${1}
""",
        ).isProblematic():  return(b_io.eh.badOutcome(outcome))
        return outcome

####+BEGIN: b:py3:cs:method/typing :methodName "delete" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /delete/  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def delete(
####+END:
            virDomName: str,
            virDomAcct: str,
    )-> b.op.Outcome:
        outcome = b.op.Outcome()

        if b.subProc.Op(outcome=outcome, uid="root", log=1).bash(
                f"""\
  opDoRet mmaQmailLocDeliveryAcctDelete ${2}
  opDoRet mmaQmailVirDomEntryDelete ${1} ${2}
  opDoRet mmaQmailRcpthostsEntryDelete ${1}
 """,
        ).isProblematic():  return(b_io.eh.badOutcome(outcome))
        return outcome


####+BEGIN: b:py3:cs:method/typing :methodName "acctGet" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /acctGet/  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def acctGet(
####+END:
            user: str,
    )-> b.op.Outcome:
        outcome = b.op.Outcome()

        if b.subProc.Op(outcome=outcome, uid="root", log=1).bash(
                f"""\
  typeset acctName=`egrep "^$1:" ${qmailVirDomFile} | cut -d : -f 2`

  if [[ "${acctName}_" == "_" ]] ; then
    EH_problem "$1 not found in ${qmailVirDomFile}"
    return 1
  fi

  print ${acctName}
""",
        ).isProblematic():  return(b_io.eh.badOutcome(outcome))
        return outcome

####+BEGIN: b:py3:cs:method/typing :methodName "domainGet" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /domainGet/  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def domainGet(
####+END:
            user: str,
    )-> b.op.Outcome:
        outcome = b.op.Outcome()

        if b.subProc.Op(outcome=outcome, uid="root", log=1).bash(
                f"""\
   typeset domainName=`egrep ":$1$" ${qmailVirDomFile} | cut -d : -f 1`

  if [[ "${domainName}_" == "_" ]] ; then
    EH_problem "$1 not found in ${qmailVirDomFile}"
    return 1
  fi

  print ${domainName}
""",
        ).isProblematic():  return(b_io.eh.badOutcome(outcome))
        return outcome



####+BEGIN: b:py3:cs:framework/endOfFile :basedOn "classification"
""" #+begin_org
* [[elisp:(org-cycle)][| *End-Of-Editable-Text* |]] :: emacs and org variables and control parameters
#+end_org """

#+STARTUP: showall

### local variables:
### no-byte-compile: t
### end:
####+END:
