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
** This File: /bisos/git/bxRepos/bisos-pip/siteRegistrars/py3/bisos/siteRegistrars/invSiteRegBox.py
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

    csParams.parDictAdd(
        parName='boxNu',
        parDescription="Box Number",
        parDataType=None,
        #parDefault='ParOne',
        parDefault=None,
        parChoices=["any"],
        # parScope=icm.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--boxNu',
    )
    csParams.parDictAdd(
        parName='uniqueBoxId',
        parDescription="uniqueBoxId",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        # parScope=icm.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--uniqueBoxId',
    )

    csParams.parDictAdd(
        parName='boxName',
        parDescription="Box Name",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        # parScope=icm.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--boxName',
    )

    csParams.parDictAdd(
        parName='rosmuControl',
        parDescription="ROS Multi-Unit Sel -- Registrars Base.",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        # parScope=icm.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--rosmuControl',
    )


####+BEGIN: b:py3:cs:orgItem/section :title "CSU-Lib Executions" :comment "-- cs.invOutcomeReportControl"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *CSU-Lib Executions* -- cs.invOutcomeReportControl  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

# svcName = "svcSiteRegBox"
svcName = "svcSiteRegistrars"
#roSiteRegistrarSapPath = cs.ro.SapBase_FPs.svcNameToRoSapPath(svcName, rosmu="svcInvSiteRegBox.cs")  # static method

# roSiteRegistrarSapPath = cs.ro.SapBase_FPs.perfNameToRoSapPath("svcSiteRegistrars", rosmu="svcInvSiteRegContainer.cs")  # static method

cs.invOutcomeReportControl(cmnd=True, ro=True)


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

    perfName = 'localhost'

    if (thisUniqueBoxId := thisBoxUUID().cmnd(
            rtInv=cs.RtInvoker.new_py(), cmndOutcome=b.op.Outcome(),
    ).results) == None: return(b_io.eh.badOutcome(cmndOutcome))

    # if (thisBoxPath := perf_boxFind().cmnd(
    #         rtInv=cs.RtInvoker.new_py(), cmndOutcome=b.op.Outcome(),
    #         uniqueBoxId=thisUniqueBoxId,
    # ).results) == None: return(b_io.eh.badOutcome(cmndOutcome))

    thisBoxPath = pathlib.Path("/xx/boxes/1005")

    thisBoxNu = thisBoxPath.name
    thisBoxName = f"box{thisBoxNu}"

    unitsPars = collections.OrderedDict([])
    unitBasePars = collections.OrderedDict([('boxNu', thisBoxNu)])
    createPars = collections.OrderedDict([('boxNu', thisBoxNu), ('uniqueBoxId', thisUniqueBoxId), ('boxName', thisBoxName)])
    addPars = collections.OrderedDict([('uniqueBoxId', thisUniqueBoxId), ('boxName', thisBoxName)])
    findArgs = f"uniqueBoxId {thisUniqueBoxId}"


    if sectionTitle == 'default': cs.examples.menuChapter('*Invoker Only Commands*')

    cmnd('runningInChromeOsContainer')
    cmnd('thisBoxUUID')

    cmnd('thisBox_findNu')
    cmnd('thisBox_assign', comment=" # Assign a number to this box, if needed.")
    cmnd('thisBox_read')
    cmnd('thisBox_update', pars=od([('boxName', 'someBoxName')]))

    if sectionTitle == 'default': cs.examples.menuChapter('*Remote Operations -- Box Invoker Management*')

    cmnd('reg_sapCreateBox', pars=od([('perfName', 'csSiteRegBox')]))
    print(f"""csRo-manage.cs --svcName="svcSiteRegBox" --perfName="csSiteRegBox" --rosmu="svcSiteRegBox.cs"  -i ro_fps list""")

    cmnd('reg_sapCreateBox', pars=od([('perfName', 'svcSiteRegistrars')]))
    print(f"""csRo-manage.cs --svcName="svcSiteRegBox" --perfName='svcSiteRegistrars' --rosmu="svcSiteRegistrars.cs"  -i ro_fps list""")

    # print(f"""svcSiteRegBox.cs --perfName="siteRegistrar" -i csPerformer  & # in background Start rpyc CS Service""")

    if sectionTitle == 'default': cs.examples.menuChapter('*Registrar Svc Commands -- perfName=siteRegistrar*')

    cmnd('reg_box_add', pars=addPars)
    cmnd('reg_box_read', pars=unitBasePars)
    cmnd('reg_box_update', pars=createPars)
    cmnd('reg_box_delete', pars=unitBasePars)
    cmnd('reg_box_find', pars=unitsPars, args=f"boxId {thisBoxNu}")
    cmnd('reg_box_find', pars=unitsPars, args=findArgs,)
    cmnd('reg_box_list', pars=unitsPars)


####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "Support Functions" :anchor ""  :extraInfo "Command Services Section"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _Support Functions_: |]]  Command Services Section  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: b:py3:cs:func/typing :funcName "perfNameGet" :comment "~Either of exampleRegistrar or siteRegistrar~"  :funcType "eType" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-eType  [[elisp:(outline-show-subtree+toggle)][||]] /perfNameGet/  ~Either of exampleRegistrar or siteRegistrar~ deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def perfNameGet(
####+END:
) -> str:
    """ #+begin_org*
*  [[elisp:(org-cycle)][| *DocStr | ]]
    #+end_org """

    return  'siteRegistrar'


####+BEGIN: b:py3:cs:func/typing :funcName "roSiteRegistrarSapPath_obtain" :comment "~Either of exampleRegistrar or siteRegistrar~"  :funcType "eType" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-eType  [[elisp:(outline-show-subtree+toggle)][||]] /roSiteRegistrarSapPath_obtain/  ~Either of exampleRegistrar or siteRegistrar~ deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def roSiteRegistrarSapPath_obtain(
####+END:
) -> str:
    """ #+begin_org*
*  [[elisp:(org-cycle)][| *DocStr | ]]
    #+end_org """

    return  cs.ro.SapBase_FPs.perfNameToRoSapPath("svcSiteRegistrars", rosmu="svcInvSiteRegContainer.cs")  # static method



####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "Invoker Only CmndSvc" :anchor ""  :extraInfo "Command Services Section"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _Invoker Only CmndSvc_: |]]  Command Services Section  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "runningInChromeOsContainer" :comment "" :extent "verify" :ro "noCli" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<runningInChromeOsContainer>>  =verify= ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class runningInChromeOsContainer(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}
    rtInvConstraints = cs.rtInvoker.RtInvoker.new_noRo() # NO RO From CLI

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
    ) -> b.op.Outcome:

        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
####+END:
        if self.cmndDocStr(""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Only true if running in a ChromeOs container where android-root user exists.
        #+end_org """): return(cmndOutcome)

        result: bool = False

        try:
            pwd.getpwnam('android-root')
            result = True
        except KeyError:
            # b_io.pr(f"Not Running In A ChromeOs Container")
            result = False

        return cmndOutcome.set(opResults=result,)

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "thisBoxUUID" :comment "" :extent "verify" :ro "noCli" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<thisBoxUUID>>  =verify= ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class thisBoxUUID(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}
    rtInvConstraints = cs.rtInvoker.RtInvoker.new_noRo() # NO RO From CLI

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
    ) -> b.op.Outcome:

        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
####+END:
        if self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Result: dmidecode -s system-uuid or macAddress when in ChromeOsContainer.
        #+end_org """): return(cmndOutcome)

        boxUniqId: str = ""  #  result

        if (inChromeOsContainer := runningInChromeOsContainer().cmnd(
                rtInv=cs.RtInvoker.new_py(), cmndOutcome=cmndOutcome,
        ).results) == None: return(b_io.eh.badOutcome(cmndOutcome))

        if inChromeOsContainer:
            if (boxUniqId := b.subProc.WOpW(invedBy=self, log=0, uid="root").bash(
                    f"""l3Admin.sh -i givenInterfaceGetMacAddr eth0""",
            ).stdoutRstrip) == None: return(b_io.eh.badOutcome(cmndOutcome))
        else:
            if (boxUniqId := b.subProc.WOpW(invedBy=self, log=0, uid="root").bash(
                    f"""dmidecode -s system-uuid""",
            ).stdoutRstrip) == None: return(b_io.eh.badOutcome(cmndOutcome))

        return cmndOutcome.set(
            opResults=f"{boxUniqId}",
        )

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "thisBox_findNu" :comment "" :extent "verify" :ro "noCli" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<thisBox_findNu>>  =verify= ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class thisBox_findNu(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}
    rtInvConstraints = cs.rtInvoker.RtInvoker.new_noRo() # NO RO From CLI

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
    ) -> b.op.Outcome:

        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
####+END:
        if self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Equivalent of: -i reg_box_find $( -i thisBoxUUID ). Result: boxNu
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  svcInvSiteRegBox.cs -i thisBox_findNu
#+end_src
#+RESULTS:
: roInvokeCmndAtSap at /bisos/var/cs/ro/sap/csInvSiteRegBox.cs/siteRegistrar/rpyc/default of box_unitsFind with {'argsList': ['uniqueBoxId', '4c4c4544-0043-3510-8052-b9c04f4c4e31'], 'rtInv': <bisos.b.cs.rtInvoker.RtInvoker object at 0x7fba029cd750>, 'cmndOutcome': <bisos.b.op.Outcome object at 0x7fba0205d050>}
: [PosixPath('/bxo/iso/pmb_clusterNeda-boxes/boxes/1017')]
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        if (uniqueBoxId := thisBoxUUID().pyWCmnd(cmndOutcome,).results) == None:
            return(b_io.eh.badOutcome(cmndOutcome))

        if (boxNus := reg_box_find().pyWCmnd(cmndOutcome,
            pyKwArgs={'argsList': ['uniqueBoxId', f"{uniqueBoxId}"]}
        ).results) == None: return(b_io.eh.badOutcome(cmndOutcome))

        return cmndOutcome.set(opResults=boxNus,)

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "thisBox_assign" :comment "" :extent "verify" :ro "noCli" :parsMand "" :parsOpt "boxName" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<thisBox_assign>>  =verify= parsOpt=boxName ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class thisBox_assign(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'boxName', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}
    rtInvConstraints = cs.rtInvoker.RtInvoker.new_noRo() # NO RO From CLI

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             boxName: typing.Optional[str]=None,  # Cs Optional Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'boxName': boxName, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        boxName = csParam.mappedValue('boxName', boxName)
####+END:
        if self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Result: dmidecode -s system-uuid or macAddress when in ChromeOsContainer.
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  svcInvSiteRegBox.cs -i thisBox_assign
#+end_src
#+RESULTS:
: roInvokeCmndAtSap at /bisos/var/cs/ro/sap/csInvSiteRegBox.cs/siteRegistrar/rpyc/default of box_unitsFind with {'argsList': ['uniqueBoxId', '4c4c4544-0043-3510-8052-b9c04f4c4e31'], 'rtInv': <bisos.b.cs.rtInvoker.RtInvoker object at 0x7f74d5f049d0>, 'cmndOutcome': <bisos.b.op.Outcome object at 0x7f74d5455110>}
: [PosixPath('/bxo/iso/pmb_clusterNeda-boxes/boxes/1017')]
: This box ([PosixPath('/bxo/iso/pmb_clusterNeda-boxes/boxes/1017')]) has already been registered -- addition skipped
: 0
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        assignedBoxNu = "0"

        if (uniqueBoxId := thisBoxUUID().pyWCmnd(cmndOutcome,).results) == None: return failed(cmndOutcome)

        if (boxNus := reg_box_find().pyWCmnd(cmndOutcome,
            pyKwArgs={'argsList': ['uniqueBoxId', f"{uniqueBoxId}"]}
        ).results) == None: return(b_io.eh.badOutcome(cmndOutcome))

        if len(boxNus) == 0:
            if (assignedBoxNu :=reg_box_add().pyWCmnd(cmndOutcome,
                    pyKwArgs={'uniqueBoxId': uniqueBoxId,}
            ).results) == None: return(b_io.eh.badOutcome(cmndOutcome))
        else:
            b_io.ann.note(f"This box ({boxNus}) has already been registered -- addition skipped")

        return cmndOutcome.set(
            opResults=f"{assignedBoxNu}",
        )


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "thisBox_read" :comment "" :extent "verify" :ro "noCli" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<thisBox_read>>  =verify= ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class thisBox_read(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}
    rtInvConstraints = cs.rtInvoker.RtInvoker.new_noRo() # NO RO From CLI

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
        if self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Result: dmidecode -s system-uuid or macAddress when in ChromeOsContainer.
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  svcInvSiteRegBox.cs -i thisBox_assign
#+end_src
#+RESULTS:
: roInvokeCmndAtSap at /bisos/var/cs/ro/sap/csInvSiteRegBox.cs/siteRegistrar/rpyc/default of box_unitsFind with {'argsList': ['uniqueBoxId', '4c4c4544-0043-3510-8052-b9c04f4c4e31'], 'rtInv': <bisos.b.cs.rtInvoker.RtInvoker object at 0x7f74d5f049d0>, 'cmndOutcome': <bisos.b.op.Outcome object at 0x7f74d5455110>}
: [PosixPath('/bxo/iso/pmb_clusterNeda-boxes/boxes/1017')]
: This box ([PosixPath('/bxo/iso/pmb_clusterNeda-boxes/boxes/1017')]) has already been registered -- addition skipped
: 0
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        assignedBoxNu = "0"

        if (uniqueBoxId := thisBoxUUID().pyWCmnd(cmndOutcome,).results) == None: return failed(cmndOutcome)

        if (boxNus := reg_box_find().pyWCmnd(cmndOutcome,
            pyKwArgs={'argsList': ['uniqueBoxId', f"{uniqueBoxId}"]}
        ).results) == None: return(b_io.eh.badOutcome(cmndOutcome))

        if len(boxNus) != 0:
            if (readResult :=reg_box_read().pyWCmnd(cmndOutcome,
                    pyKwArgs={'boxNu': boxNus[0],}
            ).results) == None: return(b_io.eh.badOutcome(cmndOutcome))
        else:
            b_io.ann.note(f"This box ({boxNus}) has not been registered -- operation skipped")

        return cmndOutcome.set(
            opResults=f"{readResult}",
        )


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "thisBox_update" :comment "" :extent "verify" :ro "noCli" :parsMand "boxName" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<thisBox_update>>  =verify= parsMand=boxName ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class thisBox_update(cs.Cmnd):
    cmndParamsMandatory = [ 'boxName', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}
    rtInvConstraints = cs.rtInvoker.RtInvoker.new_noRo() # NO RO From CLI

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             boxName: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'boxName': boxName, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        boxName = csParam.mappedValue('boxName', boxName)
####+END:
        if self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Result: dmidecode -s system-uuid or macAddress when in ChromeOsContainer.
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  svcInvSiteRegBox.cs -i thisBox_assign
#+end_src
#+RESULTS:
: roInvokeCmndAtSap at /bisos/var/cs/ro/sap/csInvSiteRegBox.cs/siteRegistrar/rpyc/default of box_unitsFind with {'argsList': ['uniqueBoxId', '4c4c4544-0043-3510-8052-b9c04f4c4e31'], 'rtInv': <bisos.b.cs.rtInvoker.RtInvoker object at 0x7f74d5f049d0>, 'cmndOutcome': <bisos.b.op.Outcome object at 0x7f74d5455110>}
: [PosixPath('/bxo/iso/pmb_clusterNeda-boxes/boxes/1017')]
: This box ([PosixPath('/bxo/iso/pmb_clusterNeda-boxes/boxes/1017')]) has already been registered -- addition skipped
: 0
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        assignedBoxNu = "0"

        if (uniqueBoxId := thisBoxUUID().pyWCmnd(cmndOutcome,).results) == None: return failed(cmndOutcome)

        if (boxNus := reg_box_find().pyWCmnd(cmndOutcome,
            pyKwArgs={'argsList': ['uniqueBoxId', f"{uniqueBoxId}"]}
        ).results) == None: return(b_io.eh.badOutcome(cmndOutcome))

        if len(boxNus) != 0:
            if (readResult :=reg_box_update().pyWCmnd(cmndOutcome,
                    pyKwArgs={'boxNu': boxNus[0], 'boxName': boxName}
            ).results) == None: return(b_io.eh.badOutcome(cmndOutcome))
        else:
            b_io.ann.note(f"This box ({boxNus}) has not been registered -- operation skipped")

        return cmndOutcome.set(
            opResults=f"{readResult}",
        )




####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "Invoke Service Commands At Site Registrar" :anchor ""  :extraInfo "Command Services Section"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _Invoke Service Commands At Site Registrar_: |]]  Command Services Section  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

#BEGIN: b:py3:cs:cmnd/classHead :cmndName "reg_sapCreateBox" :ro "noCli" :noMapping "t" :comment "" :parsMand "perfName" :parsOpt "rosmuControl" :argsMin 0 :argsMax 0

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "reg_sapCreateBox" :ro "noCli" :comment "" :parsMand "perfName" :parsOpt "rosmuControl" :argsMin 0 :argsMax 0
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<reg_sapCreateBox>>  =verify= parsMand=perfName parsOpt=rosmuControl ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class reg_sapCreateBox(cs.Cmnd):
    cmndParamsMandatory = [ 'perfName', ]
    cmndParamsOptional = [ 'rosmuControl', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}
    rtInvConstraints = cs.rtInvoker.RtInvoker.new_noRo() # NO RO From CLI

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             perfName: typing.Optional[str]=None,  # Cs Mandatory Param
             rosmuControl: typing.Optional[str]=None,  # Cs Optional Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'perfName': perfName, 'rosmuControl': rosmuControl, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        perfName = csParam.mappedValue('perfName', perfName)
        rosmuControl = csParam.mappedValue('rosmuControl', rosmuControl)
####+END:
        """\
***** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Invoked both by invoker and performer. Creates path for ro_sap and updates FPs
        """
        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  svcInvSiteRegBox.cs --rosmu svcSiteRegistrars.cs -i reg_sapCreateBox
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
            rosmuSel = "default"
            rosmuControl = 'bisos'

            confFps = invSiteRegBoxConf.RegBoxInvConf_FPs()
            ipAddrs_fp =  confFps.fps_getParam('regBoxPerfAddrs')
            ipAddrStr = ipAddrs_fp.parValueGet()
            ipAddrs = ast.literal_eval(ipAddrStr)
            perfIpAddr = ipAddrs[0]

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


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "reg_box_add" :comment "" :extent "verify" :ro "cli" :parsMand "uniqueBoxId" :parsOpt "boxName" :argsMin 0 :argsMax 0 :pyInv "pyKwArgs"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<reg_box_add>>  =verify= parsMand=uniqueBoxId parsOpt=boxName ro=cli pyInv=pyKwArgs   [[elisp:(org-cycle)][| ]]
#+end_org """
class reg_box_add(cs.Cmnd):
    cmndParamsMandatory = [ 'uniqueBoxId', ]
    cmndParamsOptional = [ 'boxName', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             uniqueBoxId: typing.Optional[str]=None,  # Cs Mandatory Param
             boxName: typing.Optional[str]=None,  # Cs Optional Param
             pyKwArgs: typing.Any=None,   # pyInv Argument
    ) -> b.op.Outcome:

        callParamsDict = {'uniqueBoxId': uniqueBoxId, 'boxName': boxName, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        uniqueBoxId = csParam.mappedValue('uniqueBoxId', uniqueBoxId)
        boxName = csParam.mappedValue('boxName', boxName)
####+END:
        if self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Re-invokero_box_add with KwArgs, therefore pyKwArgs are needed.
        #+end_org """): return(cmndOutcome)


        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  svcInvSiteRegBox.cs --uniqueBoxId 4c4c4544-0043-3510-8052-b9c04f4c4e31 -i reg_box_add
#+end_src
#+RESULTS:
: roInvokeCmndAtSap at /bisos/var/cs/ro/sap/csInvSiteRegBox.cs/siteRegistrar/rpyc/default of ro_box_add with {'uniqueBoxId': '4c4c4544-0043-3510-8052-b9c04f4c4e31', 'boxName': None, 'rtInv': <bisos.b.cs.rtInvoker.RtInvoker object at 0x7fb936e51dd0>, 'cmndOutcome': <bisos.b.op.Outcome object at 0x7fb9369c9390>}
: Cmnd -- No Results
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        cmndClass = perfSiteRegBox.ro_box_add
        if pyKwArgs:
            cmndKwArgs = pyKwArgs
        else:
            cmndKwArgs = self.cmndCallTimeKwArgs()

        rpycInvResult =  cs.ro.roInvokeCmndAtSap(
            roSiteRegistrarSapPath_obtain(),
            rtInv,
            cmndOutcome,
            cmndClass,
            ** cmndKwArgs,
        )

        return cmndOutcome

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "reg_box_read" :comment "" :extent "verify" :ro "cli" :parsMand "boxNu" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv "pyKwArgs"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<reg_box_read>>  =verify= parsMand=boxNu ro=cli pyInv=pyKwArgs   [[elisp:(org-cycle)][| ]]
#+end_org """
class reg_box_read(cs.Cmnd):
    cmndParamsMandatory = [ 'boxNu', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             boxNu: typing.Optional[str]=None,  # Cs Mandatory Param
             pyKwArgs: typing.Any=None,   # pyInv Argument
    ) -> b.op.Outcome:

        callParamsDict = {'boxNu': boxNu, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        boxNu = csParam.mappedValue('boxNu', boxNu)
####+END:
        if self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Re-invokes box_unitsFind with KwArgs, therefore pyKwArgs are needed.
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  svcInvSiteRegBox.cs --boxNu 1006 -i reg_box_read
#+end_src
#+RESULTS:
: roInvokeCmndAtSap at /bisos/var/cs/ro/sap/csInvSiteRegBox.cs/siteRegistrar/rpyc/default of box_unitRead with {'boxNu': '1006', 'rtInv': <bisos.b.cs.rtInvoker.RtInvoker object at 0x7f33e2bc4950>, 'cmndOutcome': <bisos.b.op.Outcome object at 0x7f33e2bc4910>}
: {'uniqueBoxId': '4c4c4544-0059-5110-8051-c6c04f564831', 'boxId': 'box1006', 'boxNu': '1006'}
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        cmndClass = perfSiteRegBox.box_unitRead
        if pyKwArgs:
            cmndKwArgs = pyKwArgs
        else:
            cmndKwArgs = self.cmndCallTimeKwArgs()

        rpycInvResult =  cs.ro.roInvokeCmndAtSap(
            roSiteRegistrarSapPath_obtain(),
            rtInv,
            cmndOutcome,
            cmndClass,
            ** cmndKwArgs,
        )

        return cmndOutcome


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "reg_box_update" :comment "" :extent "verify" :ro "cli" :parsMand "boxNu boxName" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv "pyKwArgs"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<reg_box_update>>  =verify= parsMand=boxNu boxName ro=cli pyInv=pyKwArgs   [[elisp:(org-cycle)][| ]]
#+end_org """
class reg_box_update(cs.Cmnd):
    cmndParamsMandatory = [ 'boxNu', 'boxName', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             boxNu: typing.Optional[str]=None,  # Cs Mandatory Param
             boxName: typing.Optional[str]=None,  # Cs Mandatory Param
             pyKwArgs: typing.Any=None,   # pyInv Argument
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'boxNu': boxNu, 'boxName': boxName, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        boxNu = csParam.mappedValue('boxNu', boxNu)
        boxName = csParam.mappedValue('boxName', boxName)
####+END:
        if self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  A starting point command.
        #+end_org """): return(cmndOutcome)

        cmndClass = perfSiteRegBox.box_unitUpdate
        if pyKwArgs:
            cmndKwArgs = pyKwArgs
        else:
            cmndKwArgs = self.cmndCallTimeKwArgs()

        rpycInvResult =  cs.ro.roInvokeCmndAtSap(
            roSiteRegistrarSapPath_obtain(),
            rtInv,
            cmndOutcome,
            cmndClass,
            ** cmndKwArgs,
        )

        return cmndOutcome

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "reg_box_delete" :comment "" :extent "verify" :ro "cli" :parsMand "boxNu" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv "pyKwArgs"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<reg_box_delete>>  =verify= parsMand=boxNu ro=cli pyInv=pyKwArgs   [[elisp:(org-cycle)][| ]]
#+end_org """
class reg_box_delete(cs.Cmnd):
    cmndParamsMandatory = [ 'boxNu', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             boxNu: typing.Optional[str]=None,  # Cs Mandatory Param
             pyKwArgs: typing.Any=None,   # pyInv Argument
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'boxNu': boxNu, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        boxNu = csParam.mappedValue('boxNu', boxNu)
####+END:
        if self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  A starting point command.
        #+end_org """): return(cmndOutcome)

        cmndClass = perfSiteRegBox.box_unitDelete
        if pyKwArgs:
            cmndKwArgs = pyKwArgs
        else:
            cmndKwArgs = self.cmndCallTimeKwArgs()

        rpycInvResult =  cs.ro.roInvokeCmndAtSap(
            roSiteRegistrarSapPath_obtain(),
            rtInv,
            cmndOutcome,
            cmndClass,
            ** cmndKwArgs,
        )

        return cmndOutcome

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "reg_box_find" :comment "" :extent "verify" :ro "cli" :parsMand "" :parsOpt ""  :argsMin 2 :argsMax 2 :pyInv "pyKwArgs"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<reg_box_find>>  =verify= argsMin=2 argsMax=2 ro=cli pyInv=pyKwArgs   [[elisp:(org-cycle)][| ]]
#+end_org """
class reg_box_find(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 2, 'Max': 2,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             argsList: typing.Optional[list[str]]=None,  # CsArgs
             pyKwArgs: typing.Any=None,   # pyInv Argument
    ) -> b.op.Outcome:

        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
####+END:
        if self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Re-invokes box_unitsFind with KwArgs, therefore pyKwArgs are needed.
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  svcInvSiteRegBox.cs -i reg_box_find uniqueBoxId someBox
#+end_src
#+RESULTS:
: roInvokeCmndAtSap at /bisos/var/cs/ro/sap/csInvSiteRegBox.cs/siteRegistrar/rpyc/default of box_unitsFind with {'argsList': ['uniqueBoxId', 'someBox'], 'rtInv': <bisos.b.cs.rtInvoker.RtInvoker object at 0x7f5a28f9ba50>, 'cmndOutcome': <bisos.b.op.Outcome object at 0x7f5a28f9ba10>}
: []
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        cmndClass = perfSiteRegBox.box_unitsFind
        if pyKwArgs:
            cmndKwArgs = pyKwArgs
        else:
            cmndKwArgs = self.cmndCallTimeKwArgs()

        rpycInvResult =  cs.ro.roInvokeCmndAtSap(
            roSiteRegistrarSapPath_obtain(),
            rtInv,
            cmndOutcome,
            cmndClass,
            ** cmndKwArgs,
        )

        return cmndOutcome

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "reg_box_list" :comment "" :extent "verify" :ro "cli" parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv "pyKwArgs"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<reg_box_list>>  =verify= ro=cli pyInv=pyKwArgs   [[elisp:(org-cycle)][| ]]
#+end_org """
class reg_box_list(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             pyKwArgs: typing.Any=None,   # pyInv Argument
    ) -> b.op.Outcome:

        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
####+END:
        if self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]   Re-invokes box_unitsList with KwArgs, therefore pyKwArgs are needed.
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  svcInvSiteRegBox.cs -i reg_box_list
#+end_src

#+RESULTS:
: roInvokeCmndAtSap at /bisos/var/cs/ro/sap/csInvSiteRegBox.cs/siteRegistrar/rpyc/default of box_unitsList with {'rtInv': <bisos.b.cs.rtInvoker.RtInvoker object at 0x7f258e26ffd0>, 'cmndOutcome': <bisos.b.op.Outcome object at 0x7f258d76ee50>}

        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        cmndClass = perfSiteRegBox.box_unitsList
        if pyKwArgs:
            cmndKwArgs = pyKwArgs
        else:
            cmndKwArgs = self.cmndCallTimeKwArgs()

        rpycInvResult =  cs.ro.roInvokeCmndAtSap(
            roSiteRegistrarSapPath_obtain(),
            rtInv,
            cmndOutcome,
            cmndClass,
            ** cmndKwArgs,
        )

        return cmndOutcome


####+BEGIN: b:py3:cs:framework/endOfFile :basedOn "classification"
""" #+begin_org
* [[elisp:(org-cycle)][| *End-Of-Editable-Text* |]] :: emacs and org variables and control parameters
#+end_org """

#+STARTUP: showall

### local variables:
### no-byte-compile: t
### end:
####+END:
