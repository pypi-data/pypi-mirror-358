# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: A =CS-Lib= for InMail Abstracted Accessible Service (aas) Offline Imap.
#+end_org """

####+BEGIN: b:py3:cs:file/dblockControls :classification "cs-u"
""" #+begin_org
* [[elisp:(org-cycle)][| /Control Parameters Of This File/ |]] :: dblk ctrls classifications=cs-u
#+BEGIN_SRC emacs-lisp
(setq-local b:dblockControls t) ; (setq-local b:dblockControls nil)
(put 'b:dblockControls 'py3:cs:Classification "cs-u") ; one of cs-mu, cs-u, cs-lib, bpf-lib, pyLibPure
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
** This File: /bisos/git/auth/bxRepos/bisos-pip/qmail/py3/bisos/qmail/qmailRemote.py
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:python:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing

csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['qmailRemote'], }
csInfo['version'] = '202212122335'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'qmailRemote-Panel.org'
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
** Imports Based On Classification=cs-u
#+end_org """
from bisos import b
from bisos.b import cs
from bisos.b import b_io

import collections
####+END:

import collections

import collections
import pathlib
import os
#import shutil

from bisos.bpo import bpoRunBases
from bisos.bpo import bpo

from bisos.common import csParam

#from bisos.marmee import aasInMailControl
from bisos.marmee import aasInMailFps
from bisos.marmee import aasOutMailFps
from bisos.marmee import aasMailFps
from bisos.marmee import gmailOauth2
from bisos.marmee import x822Lib

from bisos.qmail import qmailRemoteWrapper

import sys
import pwd

from email.message import EmailMessage
from email.parser import Parser
from email.utils import parseaddr, getaddresses
from os.path import expanduser
from configparser import ConfigParser
from collections import namedtuple

import smtplib
import http
import urllib
import urllib.request
import requests
import json
import base64
import enum

import tempfile

####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "CmndSvcs" :anchor ""  :extraInfo "Command Services Section"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _CmndSvcs_: |]]  Command Services Section  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:


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
        sectionTitle: typing.AnyStr = "",
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Examples of Service Access Instance Commands.
    #+end_org """

    def cpsInit(): return collections.OrderedDict()
    def menuItem(verbosity, **kwArgs): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity=verbosity, **kwArgs) # 'little' or 'none'
    def execLineEx(cmndStr): cs.examples.execInsert(execLine=cmndStr)

    if sectionTitle == "default":
        cs.examples.menuChapter('*Qmail Inject From Stdin*')

    myName = cs.G.icmMyName()
    execLineEx(f"""{myName} -- -n < ~/example.mail""")
    execLineEx(f"""ls -t /tmp/* | head -20 | grep qmail-inject- | head -1""")
    execLineEx(f"""sudo cat $(ls -t /tmp/* | head -20 | grep qmail-inject- | head -1)""")

    cmndName = "qmailInjectCmnd" ;  cmndArgs = "-- -n"
    cps=cpsInit(); cps['runMode'] = "runDebug"
    menuItem(verbosity='none', icmWrapper="cat ~/example.mail | ")
    menuItem(verbosity='full', icmWrapper="cat ~/example.mail | ")

    cmndName = "monolithicSend" ;  cmndArgs = "-- -n"
    cps=cpsInit(); cps['runMode'] = "runDebug"
    menuItem(verbosity='none', icmWrapper="cat ~/example.mail | ")
    menuItem(verbosity='full', icmWrapper="cat ~/example.mail | ")


####+BEGIN: bx:cs:py3:section :title "CS-Params  --- Place Holder, Empty"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *CS-Params  --- Place Holder, Empty*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "Functions" :anchor ""  :extraInfo "maildrop stdout/update"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _Functions_: |]]  maildrop stdout/update  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: bx:dblock:python:enum :enumName "MetaQmailQueueOfQmailInject" :comment "Enum Values: "
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Enum       [[elisp:(outline-show-subtree+toggle)][||]] /MetaQmailQueueOfQmailInject/ =Enum Values: fullRun, dryRun, runDebug=  [[elisp:(org-cycle)][| ]]
#+end_org """
@enum.unique
class MetaQmailQueueOfQmailInject(enum.Enum):
####+END:
    defaultQmailInject='defaultQmailInject',
    pythonQmailRemote='pythonQmailRemote',
    defaultQmailRemote='defaultQmailRemote',


####+BEGIN: b:py3:cs:func/typing :funcName "handOffToMetaQmailQueue" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /handOffToMetaQmailQueue/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def handOffToMetaQmailQueue(
####+END:
        msg,
        metaQmailQueueOfQmailInject:  str,
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] We are simulating the end handoff stage of qmailInject
    in submission context.
    Should be converted to be an operation
    #+end_org """

    senderAddr = x822Lib.msgSender(msg)
    senderHost = senderAddr.split('@')[1]
    allRecipients = x822Lib.msgAllRecipients(msg)
    #print(allRecipients)

    qmailRemoteArgs = [senderHost, senderAddr,]

    for eachRecipient in allRecipients:
        qmailRemoteArgs.append(eachRecipient[1])


    #b_io.tm.here("qmail Inject \n{msgStr}".format(msgStr=msg.as_string()))
    outcome = b.op.Outcome()

    injectionProgramCmnd = ""
    injectionProgramArgs = []

    if metaQmailQueueOfQmailInject == MetaQmailQueueOfQmailInject.defaultQmailInject.value[0]:
        injectionProgramCmnd =  "qmail-inject-bisos.cs"
        if cs.runArgs.isRunModeDryRun():
            injectionProgramArgs.append('-n')
    elif metaQmailQueueOfQmailInject == MetaQmailQueueOfQmailInject.defaultQmailRemote.value[0]:
        injectionProgramCmnd =  "qmail-remote-bisos.cs"
        injectionProgramArgs =  qmailRemoteArgs
    elif metaQmailQueueOfQmailInject == MetaQmailQueueOfQmailInject.pythonQmailRemote.value[0]:
        qmailRemoteWrapper.qmailRemoteWithMsg(msg, qmailRemoteArgs)
    else:
        print(f"NOTYET {metaQmailQueueOfQmailInject}")
        return(b_io.eh.badOutcome(outcome))

    if injectionProgramCmnd:
        commandLine = injectionProgramCmnd + " " +  " ".join(injectionProgramArgs)
        # print(commandLine)

        if b.subProc.Op(outcome=outcome, log=1).bash(
            f"""{commandLine}""",
            stdin=msg.as_string(),
        ).isProblematic():
            print(outcome.stderr)
            return(b_io.eh.badOutcome(outcome))

        #if outcome.stdout: icm.ANN_note("Stdout: " +  outcome.stdout)
        #if outcome.stderr: icm.ANN_note("Stderr: " +  outcome.stderr)


    return outcome.set(
        opError=b.OpError.Success,
        opResults=None,
    )


####+BEGIN: bx:cs:py3:section :title "CS-Commands"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *CS-Commands*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "prepAndQmailInject" :cmndType ""  :comment "Inject as a cmnd" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 9999 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<prepAndQmailInject>>  *Inject as a cmnd*  =verify= argsMax=9999 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class prepAndQmailInject(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 9999,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:
        """Inject as a cmnd"""
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
####+END:
        """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Interface to qmailInject but through a cmnd
        #+end_org """

        mailInput = b_io.stdin.read()
        qmailInject(mailInput, argsList)

        return(cmndOutcome)

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "monolithicSend" :cmndType ""  :comment "Inject as a cmnd" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 9999 :pyInv "mailInput"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<monolithicSend>>  *Inject as a cmnd*  =verify= argsMax=9999 ro=cli pyInv=mailInput   [[elisp:(org-cycle)][| ]]
#+end_org """
class monolithicSend(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 9999,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             argsList: typing.Optional[list[str]]=None,  # CsArgs
             mailInput: typing.Any=None,   # pyInv Argument
    ) -> b.op.Outcome:
        """Inject as a cmnd"""
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
####+END:
        """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Was previously called prepAndQmailRemote
        #+end_org """

        if not mailInput:
            mailInput = b_io.stdin.read()
        msg = qmailInjectPrep(mailInput, argsList)

        handOffToMetaQmailQueue(
            msg,
            MetaQmailQueueOfQmailInject.pythonQmailRemote.value[0],
        )

        return(cmndOutcome)


####+BEGIN: b:py3:cs:func/typing :funcName "qmailInjectPrep" :funcType "ExtTyp" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-ExtTyp [[elisp:(outline-show-subtree+toggle)][||]] /qmailInjectPrep/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def qmailInjectPrep(
####+END:
        mailInput: str,
        argsList: list[str],
) -> EmailMessage:
    """#+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] This =qmailInject= is a plugin replacement (a wrapper) for qmail-remote.

    #+end_org """


    body = mailInput

    fd, tmpPath = tempfile.mkstemp(suffix=".mail", prefix="qmail-inject-")
    try:
        with os.fdopen(fd, 'w') as tmp:
            tmp.write(f"argsList={argsList}\n")
            tmp.write(body)
    finally:
        #os.remove(tmpPath)
        #print(f"{tmpPath}")
        pass

    msgParser = Parser()
    msg = msgParser.parsestr(body)

    fromaddr = parseaddr(msg["from"])[1]

    uid = os.getuid()
    pid = os.getpid()

    uidName = pwd.getpwuid(uid)[0]

    aasMarmeeBase = aasMailFps.marmeeBaseForUsageAcct(
        uidName,
    )

    marmee_bpoId, marmee_bpoRunEnv = aasOutMailFps.marmeeAasOutMailAddrFind(
        aasMarmeeBase,
        fromaddr,
    )

    bpoId = msg.get_all("x-bpoid")
    if not bpoId:
        msg['X-bpoId'] = marmee_bpoId
        bpoId = [marmee_bpoId]

    bpoRunEnv = msg.get_all("x-bporunenv")
    if not bpoRunEnv:
        msg['X-bpoRunEnv'] = marmee_bpoRunEnv
        bpoRunEnv = [marmee_bpoRunEnv]

    #print(f"bpoId={bpoId} bpoRunEnv={bpoRunEnv}")

    outMailFps = b.pattern.sameInstance(
        aasOutMailFps.AasOutMail_FPs,
        bpoId=bpoId[0],
        envRelPath=bpoRunEnv[0],
    )

    credsFps = b.pattern.sameInstance(
        gmailOauth2.AasMail_googleCreds_FPs,
        bpoId=bpoId[0],
        envRelPath=bpoRunEnv[0],
    )
    client_id = credsFps.fps_getParam('googleCreds_client_id').parValueGet()
    client_secret = credsFps.fpCrypt_getParam('googleCreds_client_secret').parValueGet().decode("utf-8")
    refresh_token = credsFps.fpCrypt_getParam('googleCreds_refresh_token').parValueGet().decode("utf-8")

    msg['X-Oauth2-Client-Id'] = client_id
    msg['X-Oauth2-Client-Secret'] = client_secret
    msg['X-Oauth2-Refresh-Token'] = refresh_token

    #print(msg)

    return msg


####+BEGIN: b:py3:cs:func/typing :funcName "prepedQmailSubProc" :funcType "ExtTyp" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-ExtTyp [[elisp:(outline-show-subtree+toggle)][||]] /prepedQmailInvoke/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def prepedQmailInvoke(
####+END:
        msg: EmailMessage,
        injectionProgram,
        injectionProgramArgs,
) -> None:
    """#+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] This =qmailInject= is a plugin replacement (a wrapper) for qmail-remote.
    #+end_org """

    outcome = x822Out.injectMsgWithQmailVariant(
        msg,
        injectionProgram,
        injectionProgramArgs,
    )

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
