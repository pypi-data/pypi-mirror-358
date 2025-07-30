#!/bisos/venv/py3/dev-bisos3/bin/python
# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: A replacement module for qmail-remote with a complete Python SMTP implementation.
#+end_org """

####+BEGIN: b:py3:cs:file/dblockControls :classification "cs-mu"
""" #+begin_org
* [[elisp:(org-cycle)][| /Control Parameters Of This File/ |]] :: dblk ctrls classifications=cs-mu
#+BEGIN_SRC emacs-lisp
(setq-local b:dblockControls t) ; (setq-local b:dblockControls nil)
(put 'b:dblockControls 'py3:cs:Classification "cs-mu") ; one of cs-mu, cs-u, cs-lib, bpf-lib, pyLibPure
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
** This File: /bisos/git/auth/bxRepos/bisos-pip/marmee/py3/bin/qmail-remote.cs
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:py3:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['qmail-remote'], }
csInfo['version'] = '202210150153'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'qmail-remote-Panel.org'
csInfo['groupingType'] = 'IcmGroupingType-pkged'
csInfo['cmndParts'] = 'IcmCmndParts[common] IcmCmndParts[param]'
####+END:

""" #+begin_org
* [[elisp:(org-cycle)][| ~Description~ |]] :: A replacement module for qmail-remote
Module description comes here.
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

####+BEGIN: b:py3:file/workbench :outLevel 1
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
** Imports Based On Classification=cs-mu
#+end_org """
from bisos import b
from bisos.b import cs
from bisos.b import b_io

import collections
####+END:

import os

import sys
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

import tempfile


""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] ~csuList emacs-list Specifications~  [[elisp:(blee:org:code-block/above-run)][ /Eval Below/ ]] [[elisp:(org-cycle)][| ]]
#+BEGIN_SRC emacs-lisp
(setq  b:py:cs:csuList
  (list
   "bisos.b.cs.ro"
   "bisos.csPlayer.bleep"
   "bisos.marmee.gmailOauth2"
   "bisos.marmee.aasOutMailFps"
 ))
#+END_SRC
#+RESULTS:
| bisos.b.cs.ro | bisos.csPlayer.bleep | bisos.marmee.gmailOauth2 | bisos.marmee.aasOutMailFps |
#+end_org """

####+BEGIN: b:py3:cs:framework/csuListProc :pyImports t :csuImports t :csuParams t
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] =Process CSU List= with /4/ in csuList pyImports=t csuImports=t csuParams=t
#+end_org """

from bisos.b.cs import ro
from bisos.csPlayer import bleep
from bisos.marmee import gmailOauth2
from bisos.marmee import aasOutMailFps


csuList = [ 'bisos.b.cs.ro', 'bisos.csPlayer.bleep', 'bisos.marmee.gmailOauth2', 'bisos.marmee.aasOutMailFps', ]

g_importedCmndsModules = cs.csuList_importedModules(csuList)

def g_extraParams():
    csParams = cs.param.CmndParamDict()
    cs.csuList_commonParamsSpecify(csuList, csParams)
    cs.argsparseBasedOnCsParams(csParams)

####+END:

Oauth = namedtuple(
    "Oauth", "request_url, client_id, client_secret, username, user_refresh_token"
)
Account = namedtuple(
    "Account", "username, refresh_token, address, port, use_ssl, use_tls"
)


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "examples" :cmndType ""  :comment "FrameWrk: ICM Examples" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<examples>>  *FrameWrk: ICM Examples*  =verify= ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class examples(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
    ) -> b.op.Outcome:
        """FrameWrk: ICM Examples"""
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
####+END:
        cmndOutcome = self.getOpOutcome()
        # def cpsInit(): return collections.OrderedDict()
        # def menuItem(verbosity): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity=verbosity) # 'little' or 'none'
        # def extMenuItem(verbosity): cs.examples.cmndInsert(cmndName, cps, cmndArgs, icmName=icmExName, verbosity=verbosity) # 'little' or 'none'
        def execLineEx(cmndStr): cs.examples.execInsert(execLine=cmndStr)

        #logControler = b_io.log.Control()
        #logControler.loggerSetLevel(20)

        cs.examples.myName(cs.G.icmMyName(), cs.G.icmMyFullName())

        cs.examples.commonBrief()

        bleep.examples_csBasic()

        cs.examples.menuChapter('*Qmail Remote From Stdin*')

        myName = cs.G.icmMyName()
        execLineEx(f"""{myName} gmail.com mohsen.byname@gmail.com  mohsen.byname@gmail.com < ~/example.mail""")
        execLineEx(f"""sudo -u qmailr {myName} gmail.com mohsen.byname@gmail.com  mohsen.byname@gmail.com < ~/example.mail""")
        execLineEx(f"""{myName} one two < /etc/motd""")
        execLineEx(f"""ls -t /tmp/* | head -20 | grep qmail-remote- | head -1""")        
        execLineEx(f"""sudo cat $(ls -t /tmp/* | head -20 | grep qmail-remote- | head -1)""")        

        return(cmndOutcome)

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "noCmndProcessor" :cmndType ""  :comment "No Cmnds Dispatch" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 4 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<noCmndProcessor>>  *No Cmnds Dispatch*  =verify= argsMax=4 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class noCmndProcessor(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 4,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:
        """No Cmnds Dispatch"""
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
####+END:
        """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Dispatch examples cmnd when nor args, otherwiseprocess args as qmail-remote does.
        #+end_org """

        if argsList:
            #print(f"argsList={argsList}")
            qmailRemote(argsList)
        else:
            examples().cmnd(rtInv, cmndOutcome)

        return(cmndOutcome)


####+BEGIN: b:py3:cs:func/typing :funcName "record_inMail" :funcType "ExtTyp" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-ExtTyp [[elisp:(outline-show-subtree+toggle)][||]] /record_inMail/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def record_inMail(
####+END:
        mailInput: str,
        argsList: list[str],
) -> None:
    """#+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Record the incoming mail based on pid.
    #+end_org """

    uid = os.getuid()
    pid = os.getpid()

    fd, tmpPath = tempfile.mkstemp(suffix=".mail", prefix="qmail-remote-in-")
    try:
        with os.fdopen(fd, 'w') as tmp:
            tmp.write(f"argsList={argsList}\n")
            tmp.write(mailInput)
    finally:
        #os.remove(tmpPath)
        #print(f"{tmpPath}")
        pass

####+BEGIN: b:py3:cs:func/typing :funcName "record_outMsg" :funcType "ExtTyp" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-ExtTyp [[elisp:(outline-show-subtree+toggle)][||]] /record_outMsg/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def record_outMsg(
####+END:
        msg,
) -> None:
    """#+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Record the incoming mail based on pid.
    #+end_org """

    uid = os.getuid()
    pid = os.getpid()

    fd, tmpPath = tempfile.mkstemp(suffix=".mail", prefix="qmail-remote-out-")
    try:
        with os.fdopen(fd, 'w') as tmp:
            tmp.write(msg.as_string())
    finally:
        #os.remove(tmpPath)
        #print(f"{tmpPath}")
        pass



####+BEGIN: b:py3:cs:func/typing :funcName "qmailRemote" :funcType "ExtTyp" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-ExtTyp [[elisp:(outline-show-subtree+toggle)][||]] /qmailRemote/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def qmailRemote(
####+END:
        argsList: list[str],
) -> None:
    """#+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] This =qmailRemote= is a plugin replacement (a wrapper) for qmail-remote.

As such see the qmail-remote man page for additional details.

qmail-remote reads a mail message from its input and sends the message to one or
more recipients (sepcified in ~argsList~) at a remote host.

The remote host is qmail-remote's first argument (~argsList[0]~),  _host_.

qmail-remote sends the message to _host_, or to a mail exchanger for _host_ listed
in the Domain Name System, via SMTP. Host can be either a fully-qualified domain
name or an IP address enclosed in brackets. The envelope recipient addresses are
listed as _recip_ arguments  (~argsList[2:]~) to qmail-remote.

The envelope sender address is listed as _sender_ (~argsList[1]~).
    #+end_org """


    body = sys.stdin.read()

    record_inMail(body, argsList)

    arg_host = argsList[0]
    arg_sender = argsList[1]

    arg_recipients = []
    for each in argsList[2:]:
        arg_recipients.append(each)

    #print(f"host={arg_host} sender={arg_sender} recipients={arg_recipients}")

    fromaddr = None
    toaddrs = list()

    email_parser = Parser()
    msg = email_parser.parsestr(body)

    tos = list()
    ccs = list()
    bccs = list()

    fromaddr = parseaddr(msg["from"])[1]

    tos = getaddresses(msg.get_all("to", []))
    ccs = getaddresses(msg.get_all("cc", []))
    bccs = getaddresses(msg.get_all("bcc", []))
    resent_tos = getaddresses(msg.get_all("resent-to", []))
    resent_ccs = getaddresses(msg.get_all("resent-cc", []))
    resent_bccs = getaddresses(msg.get_all("resent-bcc", []))

    tos = [x[1] for x in tos + resent_tos]
    ccs = [x[1] for x in ccs + resent_ccs]
    bccs = [x[1] for x in bccs + resent_bccs]

    if msg.get_all("bcc", False):
        msg.replace_header("bcc", None)  # wipe out from message

    bpoId = msg.get_all("x-bpoid")
    if not bpoId:
        raise KeyError("Missing BpoId")

    bpoRunEnv = msg.get_all("x-bporunenv")
    if not bpoRunEnv:
        raise KeyError("Missing BpoRunEnv")

    print(f"bpoId={bpoId} bpoRunEnv={bpoRunEnv}")

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

    request_url = "https://accounts.google.com/o/oauth2/token"
    client_id = credsFps.fps_getParam('googleCreds_client_id').parValueGet()
    client_secret = credsFps.fpCrypt_getParam('googleCreds_client_secret').parValueGet().decode("utf-8")
    refresh_token = credsFps.fpCrypt_getParam('googleCreds_refresh_token').parValueGet().decode("utf-8")

    userName = outMailFps.fps_getParam('outMail_userName').parValueGet()
    address = outMailFps.fps_getParam('outMail_smtpServer').parValueGet()
    port = outMailFps.fps_getParam('outMail_port').parValueGet()
    use_ssl = outMailFps.fps_getParam('outMail_useSsl').parValueGet()
    #use_tls = outMailFps.fps_getParam('outMail_useTls').parValueGet()
    use_tls = "False"

    if use_ssl == "True": use_ssl = True
    if use_ssl == "False": use_ssl = False
    if use_tls == "True": use_tls = True
    if use_tls == "False": use_tls = False

    oauth = Oauth(
        request_url, client_id, client_secret, userName, refresh_token
    )

    acct = Account(
            userName, refresh_token, address, port, use_ssl, use_tls
    )

    #if args.debug:
        #print("Sending from:", fromaddr)
        #print("Sending to:", toaddrs)
    #sender(fromaddr, tos + ccs + bccs, msg, oauth, acct, args.debug)
    #sender(arg_sender, tos + ccs + bccs, msg, oauth, acct)

    # x822out.clean(msg)

    sender(arg_sender, argsList, msg, oauth, acct)



####+BEGIN: b:py3:cs:func/typing :funcName "oauth_handler" :funcType "ExtTyp" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-ExtTyp [[elisp:(outline-show-subtree+toggle)][||]] /oauth_handler/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def oauth_handler(
####+END:
        oauth,
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """
    params = dict()
    params["client_id"] = oauth.client_id
    params["client_secret"] = oauth.client_secret
    params["refresh_token"] = oauth.user_refresh_token
    params["grant_type"] = "refresh_token"

    response = urllib.request.urlopen(
         oauth.request_url, urllib.parse.urlencode(params).encode("utf-8")
    ).read()

    resp = json.loads(response)
    access_token = resp["access_token"]

    auth_string = "user=%s\1auth=Bearer %s\1\1" % (oauth.username, access_token)
    auth_string = str(base64.b64encode(auth_string.encode("utf-8")), "utf-8")
    return auth_string


####+BEGIN: b:py3:cs:func/typing :funcName "sender" :funcType "ExtTyp" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-ExtTyp [[elisp:(outline-show-subtree+toggle)][||]] /sender/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def sender(
####+END:
        fromaddr,
        toaddrs,
        msg,
        oauth,
        acct,
        debug=False,
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] submissionStaged envlpOriginator, envlpRecipients, msg
    #+end_org """


    record_outMsg(msg)

    out("KSubmission Faked: ")
    zero()

    return

    if acct.use_ssl:
        server = smtplib.SMTP_SSL(host=acct.address, port=acct.port)
    else:
        server = smtplib.SMTP(host=acct.address, port=acct.port)

    server.set_debuglevel(debug)

    if acct.use_tls:
        server.starttls()

    server.ehlo_or_helo_if_needed()

    auth = oauth_handler(oauth)
    server.docmd("AUTH", "XOAUTH2 %s" % auth)

    #server.sendmail(fromaddr, toaddrs, msg.as_string())

    server.quit()

    out("KSubmission involved: ")
    if acct.use_ssl:
        out("SSL -- ")
    if acct.use_tls:
        out("TLS -- ")
    out("OAUTH2")
    zero()

####+BEGIN: b:py3:cs:orgItem/basic :type "=PurePy=    " :title "*Functions: out,zero,temp_dns,temp_control*" :comment "Taken from C Sources"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  =PurePy=    [[elisp:(outline-show-subtree+toggle)][||]] *Functions: out,zero,temp_dns,temp_control* Taken from C Src  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

def out(str): sys.stdout.write(str)
def zero():  sys.stdout.write("\0")
def zerodie(): sys.stdout.write("\0")
def outsafe(str): sys.stdout.write(str)
def temp_nomem(): out("ZOut of memory. (#4.3.0)\n") ; zerodie()

def temp_oserr():
    out("Z\
System resources temporarily unavailable. (#4.3.0)\n")
    zerodie()

def temp_noconn():
    out("Z\
Sorry, I wasn't able to establish an SMTP connection. (#4.4.1)\n")
    zerodie()

def temp_read():
    out("ZUnable to read message. (#4.3.0)\n")
    zerodie()

def temp_dnscanon():
    out("Z\
CNAME lookup failed temporarily. (#4.4.3)\n")
    zerodie()

def temp_dns():
    out("Z\
Sorry, I couldn't find any host by that name. (#4.1.2)\n")
    zerodie()

def temp_chdir():
    out("Z\
Unable to switch to home directory. (#4.3.0)\n")
    zerodie()

def temp_control():
    out("Z\
Unable to read control files. (#4.3.0)\n")
    zerodie()

def perm_partialline():
    out("D\
SMTP cannot transfer messages with partial final lines. (#5.6.2)\n")
    zerodie()

def perm_usage():
    out("D\
I (qmail-remote) was invoked improperly. (#5.3.5)\n")
    zerodie()

def perm_dns(host):
    out("D\
Sorry, I couldn't find any host named ")
    outsafe(host);
    out(". (#5.1.2)\n")
    zerodie()

def  perm_nomx():
    out("D\
Sorry, I couldn't find a mail exchanger or IP address. (#5.4.4)\n");
    zerodie()

def perm_ambigmx():
    out("D\
Sorry. Although I'm listed as a best-preference MX or A for that host,\n\
it isn't in my control/locals file, so I don't treat it as local. (#5.4.6)\n");
    zerodie()

####+BEGIN: b:py3:cs:func/typing :funcName "outsmtptext" :funcType "extTyp" :deco "track" :comment "Incomplete"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyp [[elisp:(outline-show-subtree+toggle)][||]] /outsmtptext/  Incomplete deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def outsmtptext(
####+END:
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Place Holder
    #+end_org """
    out("KRemote host said: ")
    #out("NotYet: Somthing like: 250 ok 1495256578 qp 14280")
    out("250 ok --And more Text Comes Here")
    zero()

####+BEGIN: b:py3:cs:framework/main :csInfo "csInfo" :noCmndEntry "noCmndProcessor" :extraParamsHook "g_extraParams" :importedCmndsModules "g_importedCmndsModules"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] =g_csMain= (csInfo, _noCmndProcessor_, g_extraParams, g_importedCmndsModules)
#+end_org """

if __name__ == '__main__':
    cs.main.g_csMain(
        csInfo=csInfo,
        noCmndEntry=noCmndProcessor,  # specify a Cmnd name
        extraParamsHook=g_extraParams,
        importedCmndsModules=g_importedCmndsModules,
    )

####+END:

####+BEGIN: b:py3:cs:framework/endOfFile :basedOn "classification"
""" #+begin_org
* [[elisp:(org-cycle)][| *End-Of-Editable-Text* |]] :: emacs and org variables and control parameters
#+end_org """

#+STARTUP: showall

### local variables:
### no-byte-compile: t
### end:
####+END:
