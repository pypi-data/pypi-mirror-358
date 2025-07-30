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
** This File: /bisos/git/auth/bxRepos/bisos-pip/siteReg/py3/bisos/siteReg/siteRegDaemonSysd.py
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:python:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['siteRegDaemonSysd'], }
csInfo['version'] = '202305114503'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'siteRegDaemonSysd-Panel.org'
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
*** TODO Extract and absorb and communicate https://github.com/gongzhitaao/GnusSolution
#+end_org """

####+BEGIN: b:prog:file/orgTopControls :outLevel 1
""" #+begin_org
* [[elisp:(org-cycle)][| Controls |]] :: [[elisp:(delete-other-windows)][(1)]] | [[elisp:(show-all)][Show-All]]  [[elisp:(org-shifttab)][Overview]]  [[elisp:(progn (org-shifttab) (org-content))][Content]] | [[file:Panel.org][Panel]] | [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] | [[elisp:(bx:org:run-me)][Run]] | [[elisp:(bx:org:run-me-eml)][RunEml]] | [[elisp:(progn (save-buffer) (kill-buffer))][S&Q]]  [[elisp:(save-buffer)][Save]]  [[elisp:(kill-buffer)][Quit]] [[elisp:(org-cycle)][| ]]
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
from bisos.common import csParam

import collections
####+END:

import collections

import collections
import pathlib
import os
# import shutil

# from bisos.bpo import bpoRunBases
# from bisos.bpo import bpo

# from bisos.currents import currentsConfig

from bisos.debian import configFile
from bisos.debian import bifSystemd

from bisos import b

####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "Classes" :anchor ""  :extraInfo "InMail_Control"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _Classes_: |]]  InMail_Control  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: b:py3:class/decl :className "ConfigFile_sysdSiteReg" :superClass "configFile.ConfigFile" :comment "" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /ConfigFile_sysdSiteReg/  superClass=configFile.ConfigFile  [[elisp:(org-cycle)][| ]]
#+end_org """
class ConfigFile_sysdSiteReg(configFile.ConfigFile):
####+END:
    """ #+begin_org
** [[elisp:(org-cycle)][| DocStr| ]]  InMail Service Access Instance Class for an Accessible Abstract Service.
    #+end_org """

####+BEGIN: b:py3:cs:method/typing :methodName "configFilePath" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /configFilePath/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def configFilePath(
####+END:
            self,
    ) -> pathlib.Path:
        """ #+begin_org
*** [[elisp:(org-cycle)][| DocStr| ]]  Return path NOTYET
        #+end_org """
        serviceFilePath = sysdUnitSiteReg.serviceFilePath()
        return serviceFilePath

####+BEGIN: b:py3:cs:method/typing :methodName "configFileStrOfflineimap" :methodType "" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /configFileStrOfflineimap/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def configFileStrOfflineimap(
####+END
            self,
    ) -> str:
        """ #+begin_org
*** [[elisp:(org-cycle)][| DocStr| ]]  Returns string NOTYET
        #+end_org """
        templateStr = """
[Unit]
Description=Offlineimap Service
Documentation=man:offlineimap(1)

[Service]
ExecStart=/usr/bin/offlineimap -u basic
Restart=on-failure
RestartSec=60

[Install]
WantedBy=default.target
"""
        return templateStr


####+BEGIN: b:py3:cs:method/typing :methodName "configFileStr" :methodType "" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /configFileStr/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def configFileStr(
####+END
            self,
    ) -> str:
        """ #+begin_org
*** [[elisp:(org-cycle)][| DocStr| ]]  Returns string NOTYET
        #+end_org """
        templateStr = """
[Unit]
Description=SiteReg Service
Documentation=man:siteReg(1)

[Service]
ExecStart=/bisos/venv/py3/dev-bisos3/bin/python3 /bisos/git/auth/bxRepos/bisos-pip/siteReg/py3/bin/siteRegDaemonSysd.cs -i sysdCmndSiteReg
Restart=always
RestartSec=60

[Install]
WantedBy=default.target
"""
        return templateStr

####+BEGIN: bx:cs:py3:section :title "Exported Instances"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Exported Instances*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

sysdConfigSiteReg = ConfigFile_sysdSiteReg("NOTYET")
sysdUnitSiteReg = bifSystemd.UserUnit("siteReg")

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
    def menuItem(verbosity): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity=verbosity) # 'little' or 'none'
    # def execLineEx(cmndStr): cs.examples.execInsert(execLine=cmndStr)
    #
    configFile.examples_csu(concreteConfigFile='sysdConfigSiteReg', sectionTitle="default")
    bifSystemd.examples_csuUserUnit(userUnitInstanceName='sysdUnitSiteReg', sectionTitle="default")

    cs.examples.menuChapter('*SiteReg Daemon Full Update*')

    cmndName = "siteRegDaemonFullUpdate" ;  cmndArgs = ""
    cps=cpsInit(); menuItem(verbosity='none') ; menuItem(verbosity='full')

    cmndName = "sysdCmndSiteReg" ;  cmndArgs = ""
    cps=cpsInit(); menuItem(verbosity='none') ; menuItem(verbosity='full')


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "siteRegDaemonFullUpdate" :extent "verify" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<siteRegDaemonFullUpdate>>  =verify= ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class siteRegDaemonFullUpdate(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
    ) -> b.op.Outcome:

        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Return a dict of parName:parValue as results
        #+end_org """)

        sysdConfigSiteReg.configFileUpdate()

        path = sysdConfigSiteReg.configFilePath()

        if rtInv.outs:
            b_io.tm.here(f"configFilePath={path}")
            if os.path.isfile(path):
                if b.subProc.Op(outcome=cmndOutcome, log=1).bash(
                        f"""ls -l {path}""",
                ).isProblematic():  return(b_io.eh.badOutcome(cmndOutcome))
            else:
               print(f"""{path}""")

        sysdUnitSiteReg.reload()  # to have systemd aware of the unit files

        sysdUnitSiteReg.start()

        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=None,
        )

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "sysdCmndSiteReg" :extent "verify" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<sysdCmndSiteReg>>  =verify= ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class sysdCmndSiteReg(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
    ) -> b.op.Outcome:

        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Return a dict of parName:parValue as results
        #+end_org """)

        print("Main Command And Logs")

        if rtInv.outs:
            b_io.tm.here(f"configFilePath")

        if b.subProc.Op(outcome=cmndOutcome, log=1).bash(
f"""/bisos/venv/py3/dev-bisos3/bin/python3 /bisos/git/auth/bxRepos/bisos-pip/siteReg/py3/bin/siteRegOfflineimap.cs --bpoId="piu_mbFullUsage" --envRelPath="aas/siteReg/gmail/mohsen.byname"  -i offlineimapRun""",
        ).isProblematic():  return(b_io.eh.badOutcome(cmndOutcome))

        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=None,
        )


####+BEGIN: b:py3:cs:framework/endOfFile :basedOn "classification"
""" #+begin_org
* [[elisp:(org-cycle)][| *End-Of-Editable-Text* |]] :: emacs and org variables and control parameters
#+end_org """

#+STARTUP: showall

### local variables:
### no-byte-compile: t
### end:
####+END:
