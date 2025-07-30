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

#from bisos.bpo import bpoRunBases
#from bisos.bpo import bpo

from bisos.common import csParam

#from bisos.marmee import aasInMailControl
#from bisos.marmee import aasInMailFps
#from bisos.marmee import aasOutMailFps

# from bisos.qmail import maildrop
from bisos.qmail import qmail
from bisos.qmail import qmailControl

from bisos.common import lines

import enum


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
    csParams.parDictAdd(
        parName='qAddrAcct',
        parDescription="Qmail O/R Account",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        # parScope=icm.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--qAddrAcct',
    )
    csParams.parDictAdd(
        parName='localPart',
        parDescription="Qmail O/R Account Address",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        # parScope=icm.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--localPart',
    )
    csParams.parDictAdd(
        parName='qmailAcct',
        parDescription="Qmail O/R Account",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        # parScope=icm.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--qmailAcct',
    )
    csParams.parDictAdd(
        parName='qmailAddr',
        parDescription="Qmail O/R Account Address",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        # parScope=icm.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--qmailAddr',
    )
    csParams.parDictAdd(
        parName='maildir',
        parDescription="Directory path to Maildir",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        # parScope=icm.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--maildir',
    )


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
        qmailAcct: str = "alias",
        qmailAddr: str = "postmaster",
        sectionTitle: typing.AnyStr = "",
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Examples of Service Access Instance Commands.
    #+end_org """

    od = collections.OrderedDict
    cmnd = cs.examples.cmndEnter
    literal = cs.examples.execInsert

    includePath = qmail.installation.usersBaseDir.joinpath("include")
    assignPath = qmail.installation.usersBaseDir.joinpath("assign")

    dotQmailParams = od([('qAddrAcct', qmailAcct), ('localPart', qmailAddr),])

    #cmnd('cmdbSummary', pars=perfNamePars, comment=" # remote obtain facter data, use it to summarize for cmdb")

    cs.examples.menuChapter('*BxQmail Account And Addrs Utilities*')

    # cmnd('qmailAcctAddr_maildropUpdate', pars=acctAddr, comment=f" # Based on System config, control/me=")

    cs.examples.menuChapter('*LocalDeliveryAcct*')

    cmnd('localDeliveryAcct', args="ensureUsersBaseDir", comment=f" # create usersBaseDir={str(qmail.installation.usersBaseDir)} if needed")
    cmnd('localDeliveryAcct', args="newUserProc", comment=f" # Runs qmail-pw2u and  qmail-newu")
    cmnd('localDeliveryAcct', args="add alias", comment=f" # Adds user  to {includePath} and newUserProc")
    cmnd('localDeliveryAcct', args="add bisos", comment=f" # Adds user to {includePath} and newUserProc")
    cmnd('localDeliveryAcct', args="delete bisos", comment=f" # Deletes user from {includePath} and newUserProc")
    cmnd('localDeliveryAcct', args="verify bisos", comment=f" # Verifies user is in {assignPath}")
    cmnd('localDeliveryAcct', args="mainDomainGet", comment=f" # control/locals={qmailControl.QCFV_QmailSend().locals}")
    literal(f"ls -l {qmail.installation.usersBaseDir}/*")
    literal(f"find {qmail.installation.usersBaseDir} -type f -print | grep -v cdb  | xargs grep ^")

    cs.examples.menuChapter('*Maildir of qAddrAcct*')

    qAddrAcctMaildirParams = od([('qAddrAcct', qmailAcct), ('maildir', "./Maildir/"),])
    cmnd('maildir', args="create", pars=qAddrAcctMaildirParams, comment=f" # ")
    cmnd('maildir', args="delete", pars=qAddrAcctMaildirParams, comment=f" # ")
    cmnd('maildir', args="verify", pars=qAddrAcctMaildirParams, comment=f" # ")

    cs.examples.menuChapter('*DotQmail*')

    dotQmailMaildirParams = od([('qAddrAcct', qmailAcct), ('localPart', qmailAddr), ('maildir', "./Maildir/"),])

    cmnd('dotQmailFile', args="read", pars=dotQmailParams, comment=f" # ")
    cmnd('dotQmailFile', args="write", pars=dotQmailParams, comment=f" # Not Yet")
    cmnd('dotQmailFile', args="addMaildirLine", pars=dotQmailMaildirParams, comment=f" # ")
    cmnd('dotQmailFile', args="addForwardLine 'destEmailComesHere'", pars=dotQmailParams, comment=f" # ")
    cmnd('dotQmailFile', args="deleteLine 'destEmailComesHere'", pars=dotQmailParams, comment=f" # ")

    cs.examples.menuChapter('*VirDomEntry*')

    cmnd('virDomEntry', args="add", comment=f" # ")
    cmnd('virDomEntry', args="delete", comment=f" # ")
    cmnd('virDomEntry', args="acctGet", comment=f" # ")
    cmnd('virDomEntry', args="domainGet", comment=f" # ")

    cs.examples.menuChapter('*RcpthostsEntry*')

    cmnd('rcpthostsEntry', args="add", comment=f" # ")
    cmnd('rcpthostsEntry', args="delete", comment=f" # ")
    cmnd('rcpthostsEntry', args="acctGet", comment=f" # ")
    cmnd('rcpthostsEntry', args="domainGet", comment=f" # ")

    cs.examples.menuChapter('*VirDom*')

    cmnd('virDom', args="update", comment=f" # ")
    cmnd('virDom', args="delete", comment=f" # ")
    cmnd('virDom', args="acctGet", comment=f" # ")
    cmnd('virDom', args="domainGet", comment=f" # ")

    cs.examples.menuChapter('*Direct Commands*')

    literal("hostname --fqdn", comment=" # usually used as control/me")


####+BEGIN: bx:cs:py3:section :title "CS-Commands"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *CS-Commands*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "qmailAcctAddr_maildropUpdate" :comment "" :extent "verify" :parsMand "qmailAcct qmailAddr" :argsMin 1 :argsMax 1 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<qmailAcctAddr_maildropUpdate>>  =verify= parsMand=qmailAcct qmailAddr argsMin=1 argsMax=1 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class qmailAcctAddr_maildropUpdate(cs.Cmnd):
    cmndParamsMandatory = [ 'qmailAcct', 'qmailAddr', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 1,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             qmailAcct: typing.Optional[str]=None,  # Cs Mandatory Param
             qmailAddr: typing.Optional[str]=None,  # Cs Mandatory Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        callParamsDict = {'qmailAcct': qmailAcct, 'qmailAddr': qmailAddr, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        qmailAcct = csParam.mappedValue('qmailAcct', qmailAcct)
        qmailAddr = csParam.mappedValue('qmailAddr', qmailAddr)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] For dotQmail specified by qmailAcct and qmailAddr, update maildrop to maildropQmailAddr.
*** Make sure that file corresponing to =maildropQmailAddr= exists.
*** Read in qmailAcctAddr.
*** Update maildrop line in qmailAcctAddr file.
*** -
        #+end_org """)

        cmndArgsSpecDict = self.cmndArgsSpec()
        maildropQmailAddr = self.cmndArgsGet("0", cmndArgsSpecDict, argsList)

        qmailAcctAddr = qmail.AcctAddr(qmailAcct, qmailAddr)
        qmailAcctPath = qmailAcctAddr.acctPath()

        maildropRelPath = maildrop.maildropFileName(qmailAddr)
        maildropPath = qmailAcctPath.joinpath(maildropRelPath)

        if not maildropPath.exists():
            print(f"Missing {maildropPath}")
            return b_io.eh.badOutcome(cmndOutcome)

        maildropLine = f"""| maildrop {maildropRelPath}"""

        dotQmailContent = qmailAcctAddr.dotQmailFileContentRead()
        dotQmailLinesObj = lines.Lines(inContent=dotQmailContent)
        updatedDotQmailLines = dotQmailLinesObj.addIfNotThere(maildropLine)

        updatedDotQmailContent = '\n'.join(updatedDotQmailLines)
        qmailAcctAddr.dotQmailFileContentWrite(updatedDotQmailContent)

        return(cmndOutcome)


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
            argPosition="0",
            argName="maildropQmailAddr",
            argChoices=[],
            argDescription="Maildrop File Identifier"
        )
        return cmndArgsSpecDict


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "localDeliveryAcct" :comment "" :extent "verify" :parsMand "" :argsMin 1 :argsMax 4 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<localDeliveryAcct>>  =verify= argsMin=1 argsMax=4 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class localDeliveryAcct(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 4,}

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
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] For dotQmail specified by qmailAcct and qmailAddr, update maildrop to maildropQmailAddr.
*** Make sure that file corresponing to =maildropQmailAddr= exists.
*** Read in qmailAcctAddr.
*** Update maildrop line in qmailAcctAddr file.
*** -
        #+end_org """)

        cmndArg = self.cmndArgsGet("0", cmndArgsSpecDict, argsList)
        restArgs = self.cmndArgsGet("1&9999", cmndArgsSpecDict, argsList)

        result: typing.Any = None

        if cmndArg == 'ensureUsersBaseDir':
            cmndOutcome = qmail.LocalDeliveryAcct.ensureUsersBaseDir()
        elif cmndArg == 'newUserProc':
            cmndOutcome = qmail.LocalDeliveryAcct.newUserProc()
        elif cmndArg == 'add':
            cmndOutcome = qmail.LocalDeliveryAcct.add(restArgs[0])
        elif cmndArg == 'delete':
            cmndOutcome = qmail.LocalDeliveryAcct.delete(restArgs[0])
        elif cmndArg == 'verify':
            cmndOutcome = qmail.LocalDeliveryAcct.verify(restArgs[0])
        elif cmndArg == 'mainDomainGet':
            cmndOutcome = qmail.LocalDeliveryAcct.mainDomainGet()
        else:
            b_io.eh.critical_usageError(f"Unknown cmndArg={cmndArg}")

        return(cmndOutcome)


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
            argPosition="0",
            argName="cmndArg",
            argChoices=[],
            argDescription="Command which may need restOfArgs"
        )
        cmndArgsSpecDict.argsDictAdd(
            argPosition="1&9999",
            argName="restOfArgs",
            argChoices=[],
            argDescription="Rest of args which may be specific to each command"
        )
        return cmndArgsSpecDict


    ####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "maildir" :comment "" :extent "verify" :parsMand "qAddrAcct" :argsMin 1 :argsMax 9999 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<maildir>>  =verify= parsMand=qAddrAcct argsMin=1 argsMax=9999 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class maildir(cs.Cmnd):
    cmndParamsMandatory = [ 'qAddrAcct', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 9999,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             qAddrAcct: typing.Optional[str]=None,  # Cs Mandatory Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'qAddrAcct': qAddrAcct, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        qAddrAcct = csParam.mappedValue('qAddrAcct', qAddrAcct)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] For dotQmail specified by qmailAcct and qmailAddr, update maildrop to maildropQmailAddr.
*** Make sure that file corresponing to =maildropQmailAddr= exists.
*** Read in qmailAcctAddr.
*** Update maildrop line in qmailAcctAddr file.
*** -
        #+end_org """)

        cmndArg = self.cmndArgsGet("0", cmndArgsSpecDict, argsList)
        restArgs = self.cmndArgsGet("1&9999", cmndArgsSpecDict, argsList)

        result: typing.Any = None

        if cmndArg == 'create':
            cmndOutcome = qmail.Maildir.create(qAddrAcct, restArgs)
        elif cmndArg == 'delete':
            cmndOutcome = qmail.Maildir.delete(qAddrAcct, restArgs)
        elif cmndArg == 'verify':
            cmndOutcome = qmail.Maildir.verify(qAddrAcct, restArgs)
        else:
            b_io.eh.critical_usageError(f"Unknown cmndArg={cmndArg}")

        return(cmndOutcome)


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
            argPosition="0",
            argName="cmndArg",
            argChoices=[],
            argDescription="Command which may need restOfArgs"
        )
        cmndArgsSpecDict.argsDictAdd(
            argPosition="1&9999",
            argName="restOfArgs",
            argChoices=[],
            argDescription="Rest of args which may be specific to each command"
        )
        return cmndArgsSpecDict

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "dotQmailFile" :comment "" :extent "verify" :parsMand "qAddrAcct localPart" :parsOpt "maildir" :argsMin 1 :argsMax 4 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<dotQmailFile>>  =verify= parsMand=qAddrAcct localPart parsOpt=maildir argsMin=1 argsMax=4 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class dotQmailFile(cs.Cmnd):
    cmndParamsMandatory = [ 'qAddrAcct', 'localPart', ]
    cmndParamsOptional = [ 'maildir', ]
    cmndArgsLen = {'Min': 1, 'Max': 4,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             qAddrAcct: typing.Optional[str]=None,  # Cs Mandatory Param
             localPart: typing.Optional[str]=None,  # Cs Mandatory Param
             maildir: typing.Optional[str]=None,  # Cs Optional Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'qAddrAcct': qAddrAcct, 'localPart': localPart, 'maildir': maildir, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        qAddrAcct = csParam.mappedValue('qAddrAcct', qAddrAcct)
        localPart = csParam.mappedValue('localPart', localPart)
        maildir = csParam.mappedValue('maildir', maildir)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] For dotQmail specified by qmailAcct and qmailAddr, update maildrop to maildropQmailAddr.
*** Make sure that file corresponing to =maildropQmailAddr= exists.
*** Read in qmailAcctAddr.
*** Update maildrop line in qmailAcctAddr file.
*** -
        #+end_org """)

        cmndArg = self.cmndArgsGet("0", cmndArgsSpecDict, argsList)
        restArgs = self.cmndArgsGet("1&9999", cmndArgsSpecDict, argsList)

        result: typing.Any = None

        dotQmail = qmail.DotQmailFile(qAddrAcct, localPart)

        if cmndArg == 'read':
            result = dotQmail.contentRead()
            cmndOutcome.set(opResults=result)
        elif cmndArg == 'addMaildirLine':
            cmndOutcome = dotQmail.addMaildirLine(maildir, cmndOutcome)
        elif cmndArg == 'addForwardLine':
            cmndOutcome = dotQmail.addForwardLine(restArgs[0], cmndOutcome)
        elif cmndArg == 'deleteLine':
            cmndOutcome = dotQmail.deleteLine(restArgs[0], cmndOutcome)
        else:
            b_io.eh.critical_usageError(f"Unknown cmndArg={cmndArg}")

        return(cmndOutcome)


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
            argPosition="0",
            argName="cmndArg",
            argChoices=[],
            argDescription="Command which may need restOfArgs"
        )
        cmndArgsSpecDict.argsDictAdd(
            argPosition="1&9999",
            argName="restOfArgs",
            argChoices=[],
            argDescription="Rest of args which may be specific to each command"
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
