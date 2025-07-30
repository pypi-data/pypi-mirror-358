# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: =CS-Lib= A RO service for registration of Boxes at a site.
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
** This File: /bisos/git/bxRepos/bisos-pip/siteRegistrars/py3/bisos/siteRegistrars/perfSap.py
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGINNOT: b:py3:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['csSiteRegBox'], }
csInfo['version'] = '202401192758'
csInfo['status']  = 'inUse'
csInfo['panel'] = "[[../../panels/_nodeBase_/fullUsagePanel-en.org]]"
csInfo['groupingType'] = 'IcmGroupingType-pkged'
csInfo['cmndParts'] = 'IcmCmndParts[common] IcmCmndParts[param]'
####+END:

""" #+begin_org
* [[elisp:(org-cycle)][| ~Description~ |]] :: [[file:/bisos/git/auth/bxRepos/blee-binders/bisos-core/PyFwrk/bisos-pip/bisos.cs/_nodeBase_/fullUsagePanel-en.org][BISOS CmndSvcs Panel]]   [[elisp:(org-cycle)][| ]]
** TODO Document this module.
** TODO Add sectioning for Invoker and performer.
** Relevant Panels:
** Status: In use with BISOS
** /[[elisp:(org-cycle)][| Planned Improvements |]]/ :
*** TODO complete fileName in particulars.
#+end_org """

####+BEGIN: b:prog:file/orgTopControls :outLevel 1
""" #+begin_org
* [[elisp:(org-cycle)][| Controls |]] :: [[elisp:(delete-other-windows)][(1)]] | [[elisp:(show-all)][Show-All]]  [[elisp:(org-shifttab)][Overview]]  [[elisp:(progn (org-shifttab) (org-content))][Content]] | [[file:Panel.org][Panel]] | [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] | [[elisp:(bx:org:run-me)][Run]] | [[elisp:(bx:org:run-me-eml)][RunEml]] | [[elisp:(progn (save-buffer) (kill-buffer))][S&Q]]  [[elisp:(save-buffer)][Save]]  [[elisp:(kill-buffer)][Quit]] [[elisp:(org-cycle)][| ]]
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
** Imports Based On Classification=cs-u
#+end_org """
from bisos import b
from bisos.b import cs
from bisos.b import b_io
from bisos.common import csParam

import collections
####+END:

from bisos.banna import bannaPortNu
from bisos.siteRegistrars import invSiteRegBoxConf
from bisos.siteRegistrars import perfSiteRegBox

import pwd
import pathlib
import ast

import enum

####+BEGIN: b:py3:cs:orgItem/section :title "Common Parameters Specification" :comment "based on cs.param.CmndParamDict -- As expected from CSU-s"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Common Parameters Specification* based on cs.param.CmndParamDict -- As expected from CSU-s  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:func/typing :funcName "commonParamsSpecify" :comment "~CSU Specification~" :funcType "ParSpc" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-ParSpc [[elisp:(outline-show-subtree+toggle)][||]] /commonParamsSpecify/  ~CSU Specification~  [[elisp:(org-cycle)][| ]]
#+end_org """
def commonParamsSpecify(
####+END:
        csParams: cs.param.CmndParamDict,
) -> None:
    pass

####+BEGIN: b:py3:cs:orgItem/section :title "CSU-Lib Executions" :comment "-- cs.invOutcomeReportControl"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *CSU-Lib Executions* -- cs.invOutcomeReportControl  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:


####+BEGIN: bx:dblock:python:section :title "Enumerations"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Enumerations*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:

####+BEGIN: b:py3:cs:orgItem/section :title "CSU-Lib Examples" :comment "-- Providing examples_csu"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *CSU-Lib Examples* -- Providing examples_csu  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:func/typing :funcName "examples_csu" :comment "~CSU Specification~" :funcType "eType" :retType "" :deco "default" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-eType  [[elisp:(outline-show-subtree+toggle)][||]] /examples_csu/  ~CSU Specification~ deco=default  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def examples_csu(
####+END:
        sectionTitle: typing.AnyStr = '',
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr* |]] Examples of Service Access Instance Commands.
    #+end_org """

    cmndOutcome = b.op.Outcome()

    od = collections.OrderedDict
    cmnd = cs.examples.cmndEnter

    myName = cs.G.icmMyName()

    if myName == 'svcPerfSiteRegistrars.cs':
        svcName = 'svcSiteRegistrars'
        perfName = 'svcSiteRegistrars'
    elif myName == 'svcSiteRegistrars.cs':
        svcName = 'svcSiteRegistrars'
        perfName = 'svcSiteRegistrars'
    elif myName == 'svcSiteRegBox.cs':
        svcName = 'svcSiteRegBox'
        perfName = 'svcSiteRegBox'
    elif myName == 'svcSiteRegContainer.cs':
        svcName = 'svcSiteRegContainer'
        perfName = 'svcSiteRegContainer'
    else:
        svcName = 'MissingSvcName'
        perfName = 'MissingPerfName'

    if sectionTitle == 'default': cs.examples.menuChapter('*Remote Operations -- Performer SAP Create and Manage*')

    cmnd('perf_sapCreate', pars=od([('svcName', svcName), ('perfName', perfName), ('rosmu', myName)]))

    print(f"""csRo-manage.cs --svcName={svcName} --perfName={perfName} --rosmu={myName}  -i ro_fps list""")

    cmnd('csPerformer', pars=od([('svcName', svcName)]), comment="&  #  in background Start rpyc CS Service" )

    # print(f"""svcSiteRegBox.cs --perfName="siteRegistrar" -i csPerformer  & # in background Start rpyc CS Service""")


####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "Invoke Service Commands At Site Registrar" :anchor ""  :extraInfo "Command Services Section"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _Invoke Service Commands At Site Registrar_: |]]  Command Services Section  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "perf_sapCreate" :ro "noCli" :comment "" :parsMand "svcName perfName" :parsOpt "rosmuControl" :argsMin 0 :argsMax 0
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<perf_sapCreate>>  =verify= parsMand=svcName perfName parsOpt=rosmuControl ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class perf_sapCreate(cs.Cmnd):
    cmndParamsMandatory = [ 'svcName', 'perfName', ]
    cmndParamsOptional = [ 'rosmuControl', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}
    rtInvConstraints = cs.rtInvoker.RtInvoker.new_noRo() # NO RO From CLI

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             svcName: typing.Optional[str]=None,  # Cs Mandatory Param
             perfName: typing.Optional[str]=None,  # Cs Mandatory Param
             rosmuControl: typing.Optional[str]=None,  # Cs Optional Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'svcName': svcName, 'perfName': perfName, 'rosmuControl': rosmuControl, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        svcName = csParam.mappedValue('svcName', svcName)
        perfName = csParam.mappedValue('perfName', perfName)
        rosmuControl = csParam.mappedValue('rosmuControl', rosmuControl)
####+END:
        """\
***** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Invoked both by invoker and performer. Creates path for ro_sap and updates FPs
        """
        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  svcSiteRegistrars.cs --rosmu svcSiteRegistrars.cs -i reg_sapCreateBox
#+end_src
#+RESULTS:
#+begin_example

FileParam.writeTo path=/bisos/var/cs/ro/sap/svcSiteRegistrars.cs/siteRegistrar/rpyc/default/perfIpAddr/value value=localhost
FileParam.writeTo path=/bisos/var/cs/ro/sap/svcSiteRegistrars.cs/siteRegistrar/rpyc/default/perfPortNu/value value=22222003
FileParam.writeTo path=/bisos/var/cs/ro/sap/svcSiteRegistrars.cs/siteRegistrar/rpyc/default/accessControl/value value=placeholder
FileParam.writeTo path=/bisos/var/cs/ro/sap/svcSiteRegistrars.cs/siteRegistrar/rpyc/default/perfName/value value=siteRegistrar
FileParam.writeTo path=/bisos/var/cs/ro/sap/svcSiteRegistrars.cs/siteRegistrar/rpyc/default/perfModel/value value=rpyc
FileParam.writeTo path=/bisos/var/cs/ro/sap/svcSiteRegistrars.cs/siteRegistrar/rpyc/default/rosmu/value value=svcSiteRegistrars.cs
FileParam.writeTo path=/bisos/var/cs/ro/sap/svcSiteRegistrars.cs/siteRegistrar/rpyc/default/rosmuSel/value value=default
FileParam.writeTo path=/bisos/var/cs/ro/sap/svcSiteRegistrars.cs/siteRegistrar/rpyc/default/rosmuControl/value value=bisos
/bisos/var/cs/ro/sap/svcSiteRegistrars.cs/siteRegistrar/rpyc/default
#+end_example

#+begin_src sh :results output :session shared
  svcSiteRegistrars.cs -i reg_sapCreateBox
#+end_src
#+RESULTS:
:
: bash: svcSiteRegistrars.cs: command not found
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        perfModel = "rpyc"
        rosmu = cs.G.icmMyName()

        if rosmuControl:
            perfName = "exampleRegistrar"
            rosmuSel = 'default'  #  A file path to
            perfIpAddr = "localhost"
        else:
            perfName = perfName
            rosmuSel = "default"
            rosmuControl = 'bisos'
            perfIpAddr = "localhost"

        if rosmu == 'svcPerfSiteRegistrars.cs':
            portName = 'svcSiteRegistrars.cs'
        else:
            portName = myName

        if (perfPortList := bannaPortNu.bannaPortNuOf().pyWCmnd(cmndOutcome,
                argsList=[perfName]
        ).results) == None : return failed(cmndOutcome)

        perfPortNu = perfPortList[0]

        sapBaseFps = b.pattern.sameInstance(cs.ro.SapBase_FPs, rosmu=rosmu, svcName=svcName, perfName=perfName, perfModel=perfModel, rosmuSel=rosmuSel)

        sapBaseFps.fps_setParam('perfIpAddr', perfIpAddr)
        sapBaseFps.fps_setParam('perfPortNu', perfPortNu)
        sapBaseFps.fps_setParam('accessControl', "placeholder")
        sapBaseFps.fps_setParam('perfName', perfName)
        sapBaseFps.fps_setParam('perfModel', perfModel)
        sapBaseFps.fps_setParam('rosmu', rosmu)
        sapBaseFps.fps_setParam('rosmuSel', rosmuSel)
        sapBaseFps.fps_setParam('rosmuControl', rosmuControl)

        sapPath = sapBaseFps.basePath_obtain()

        return cmndOutcome.set(opResults=sapPath,)


####+BEGIN: b:py3:cs:framework/endOfFile :basedOn "classification"
""" #+begin_org
* [[elisp:(org-cycle)][| *End-Of-Editable-Text* |]] :: emacs and org variables and control parameters
#+end_org """

#+STARTUP: showall

### local variables:
### no-byte-compile: t
### end:
####+END:
