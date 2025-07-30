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
** This File: /bisos/git/bxRepos/bisos-pip/siteRegistrars/py3/bisos/siteRegistrars/csSiteRegContainer.py
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGINNOT: b:py3:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['csSiteRegContainer'], }
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
from bisos.siteRegistrars import invSiteRegContainerConf

from bisos.siteRegistrars import invSiteRegBox

from bisos.cntnr import cntnrCharName

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
        parName='containerNu',
        parDescription="One of: LinuxU, Server",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        # parScope=icm.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--containerNu',
    )
    csParams.parDictAdd(
        parName='model',
        parDescription="One of: Host, Pure, Guest",
        parDataType=None,
        #parDefault='ParOne',
        parDefault=None,
        parChoices=["any"],
        # parScope=icm.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--model',
    )
    csParams.parDictAdd(
        parName='abode',
        parDescription="One of: Shield, Internet",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        # parScope=icm.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--abode',
    )
    csParams.parDictAdd(
        parName='purpose',
        parDescription="One of: LinuxU, Server",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        # parScope=icm.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--purpose',
    )
    csParams.parDictAdd(
        parName='boxNu',
        parDescription="One of: LinuxU, Server",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        # parScope=icm.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--boxNu',
    )



####+BEGIN: b:py3:cs:orgItem/section :title "CSU-Lib Executions" :comment "-- cs.invOutcomeReportControl"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *CSU-Lib Executions* -- cs.invOutcomeReportControl  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

# svcName = "svcSiteRegContainer"
svcName = "svcSiteRegistrars"

# roSiteRegistrarSapPath = cs.ro.SapBase_FPs.svcNameToRoSapPath(svcName, rosmu="svcInvSiteRegContainer.cs")  # static method
# roSiteRegistrarSapPath = cs.ro.SapBase_FPs.perfNameToRoSapPath("svcSiteRegistrars")  # static method

cs.invOutcomeReportControl(cmnd=True, ro=True)


####+BEGIN: b:py3:cs:orgItem/section :title "Performer Modules Import" :comment "-- After Common Definitions"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Performer Modules Import* -- After Common Definitions  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

from bisos.siteRegistrars import perfSiteRegContainer

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

    # def cpsInit(): return collections.OrderedDict()
    # def menuItem(verbosity): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity=verbosity) # 'little' or 'none'

    rosmu = cs.G.icmMyName()
    cmndOutcome = b.op.Outcome()

    od = collections.OrderedDict
    cmnd = cs.examples.cmndEnter

    perfName = 'localhost'

    thisModel = 'Pure'
    thisAbode = 'Mobile'
    thisPurpose = 'LinuxU'
    thisBoxNu = 'box1014'
    thisContainerNu = '1099'

    unitsPars = collections.OrderedDict([('model', thisModel), ('abode', thisAbode), ('purpose', thisPurpose)])
    unitBasePars = collections.OrderedDict([('model', thisModel), ('abode', thisAbode), ('purpose', thisPurpose), ('containerNu', thisContainerNu)])
    createPars = unitBasePars.copy()
    createPars.update([('boxNu', thisBoxNu)])

    thisSysPars = collections.OrderedDict([('model', 'Host'), ('abode', 'Shield'), ('purpose', 'Server'),])

    ro_unitsPars = cs.examples.perfNameParsInsert(unitsPars, perfName)
    ro_unitBasePars = cs.examples.perfNameParsInsert(unitBasePars, perfName)
    ro_createPars = cs.examples.perfNameParsInsert(createPars, perfName)

    cs.examples.menuSection('*RO Service Commands*')

    if sectionTitle == 'default': cs.examples.menuChapter('*Remote Operations -- Container Invoker Management*')

    cmnd('reg_sapCreateContainer', pars=od([('perfName', 'svcSiteRegContainer')]))
    # print(f"""csRo-manage.cs --svcName="svcSiteRegContainer" --perfName="svcSiteRegContainer"  --rosmu="svcSiteRegContainer.cs"  -i ro_fps list""")
    print(f"""csRo-manage.cs --svcName="svcSiteRegContainer" --perfName="svcSiteRegContainer"  --rosmu="{rosmu}"  -i ro_fps list""")

    cmnd('reg_sapCreateContainer', pars=od([('perfName', 'svcSiteRegistrars')]))
    # print(f"""csRo-manage.cs --svcName="svcSiteRegistrars" --perfName="svcSiteRegistrars" --rosmu="svcSiteRegistrars.cs"  -i ro_fps list""")
    print(f"""csRo-manage.cs --svcName="svcSiteRegistrars" --perfName="svcSiteRegistrars" --rosmu="{rosmu}"  -i ro_fps list""")

    # print(f"""csSiteRegContainer.cs --perfName="siteRegistrar" -i csPerformer  & # in background Start rpyc CS Service""")

    if sectionTitle == 'default': cs.examples.menuChapter('*Registrar Svc Commands -- perfName=siteRegistrar*')

    cmnd('reg_container_add', pars=unitBasePars)
    cmnd('reg_container_read', pars=unitBasePars)
    cmnd('reg_container_update', pars=createPars)
    cmnd('reg_container_delete', pars=unitBasePars)
    cmnd('reg_container_find', pars=unitsPars, args=f"boxId {thisBoxNu}")
    cmnd('reg_container_locateInAll', args=f"boxId {thisBoxNu}")
    cmnd('reg_container_list', pars=unitsPars)
    cmnd('reg_container_unitsListAll',)

    if sectionTitle == 'default': cs.examples.menuChapter('*ThisSys Facilities*')

    cmnd('thisSys_locateBoxInAll')
    print(f"""svcInvSiteRegContainer.cs  -i thisSys_locateBoxInAll  2> /dev/null  | pyLiteralToBash.cs  -i stdinToBash""")
    cmnd('thisSys_findContainer', pars=thisSysPars,)
    cmnd('thisSys_assignContainer', pars=thisSysPars,)
    cmnd('withContainerIdRead', args=f"HSS-1006",)

    if sectionTitle == 'default': cs.examples.menuChapter('*Guest (Virtual) Facilities*')
    cmnd('virt_assignContainer', pars=collections.OrderedDict([('model', 'Virt'), ('abode', 'Shield'), ('purpose', 'Server'),]))


####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "Support Functions" :anchor ""  :extraInfo "Command Services Section"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _Support Functions_: |]]  Command Services Section  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

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

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "thisSys_locateBoxInAll" :comment "" :extent "verify" :ro "noCli" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<thisSys_locateBoxInAll>>  =verify= ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class thisSys_locateBoxInAll(cs.Cmnd):
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
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Equivalent of: -i reg_box_find $( -i thisBoxUUID ). Result: boxNu
       NOTYET csSiteRegContainer.cs --model=Pure --abode=Mobile --purpose=LinuxU -i container_unitsFind boxId box1014
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  svcInvSiteRegContainer.cs --model=Pure --abode=Mobile --purpose=LinuxU -i thisSys_findContainer
#+end_src
#+RESULTS:
: roInvokeCmndAtSap at /bisos/var/cs/ro/sap/csInvSiteRegContainer.cs/csSiteRegBox/rpyc/default of box_unitsFind with {'argsList': ['uniqueBoxId', '4c4c4544-0043-3510-8052-b9c04f4c4e31'], 'rtInv': <bisos.b.cs.rtInvoker.RtInvoker object at 0x7fb82dc55c50>, 'cmndOutcome': <bisos.b.op.Outcome object at 0x7fb82d25dcd0>}
: roInvokeCmndAtSap at /bisos/var/cs/ro/sap/csInvSiteRegContainer.cs/csSiteRegContainer/rpyc/default of container_unitsFind with {'model': 'Pure', 'abode': 'Mobile', 'purpose': 'LinuxU', 'argsList': ['boxId', 'box['], 'rtInv': <bisos.b.cs.rtInvoker.RtInvoker object at 0x7fb82e19c8d0>, 'cmndOutcome': <bisos.b.op.Outcome object at 0x7fb82d25dcd0>}
: []
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome
        
        if (boxNus := invSiteRegBox.thisBox_findNu().pyWCmnd(cmndOutcome,).results) == None: return failed(cmndOutcome)
        # boxNus = ast.literal_eval(boxNus)

        cmndOutcome.set(opResults=list(),)
        
        if len(boxNus) == 0:
            b_io.ann.note("No boxnu has been assigned to this system.")
            return failed(cmndOutcome)

        boxNu = boxNus[0]

        if (containers := reg_container_locateInAll().pyWCmnd(cmndOutcome,
            pyKwArgs={'argsList': ['boxId', f"{boxNu}"]},
        ).results) == None: return failed(cmndOutcome)

        if len(containers) == 0:
            # Temporary -- To Deal with old Data
            if (containers := reg_container_locateInAll().pyWCmnd(cmndOutcome,
                pyKwArgs={'argsList': ['boxId', f"box{boxNu}"]},
            ).results) == None: return failed(cmndOutcome)

        return cmndOutcome.set(opResults=containers,)


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "thisSys_findContainer" :comment "" :extent "verify" :ro "noCli" :parsMand "model abode purpose" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<thisSys_findContainer>>  =verify= parsMand=model abode purpose ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class thisSys_findContainer(cs.Cmnd):
    cmndParamsMandatory = [ 'model', 'abode', 'purpose', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}
    rtInvConstraints = cs.rtInvoker.RtInvoker.new_noRo() # NO RO From CLI

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             model: typing.Optional[str]=None,  # Cs Mandatory Param
             abode: typing.Optional[str]=None,  # Cs Mandatory Param
             purpose: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'model': model, 'abode': abode, 'purpose': purpose, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        model = csParam.mappedValue('model', model)
        abode = csParam.mappedValue('abode', abode)
        purpose = csParam.mappedValue('purpose', purpose)
####+END:
        if self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Equivalent of: -i reg_box_find $( -i thisBoxUUID ). Result: boxNu
       NOTYET csSiteRegContainer.cs --model=Pure --abode=Mobile --purpose=LinuxU -i container_unitsFind boxId box1014
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  svcInvSiteRegContainer.cs --model=Pure --abode=Mobile --purpose=LinuxU -i thisSys_findContainer
#+end_src
#+RESULTS:
: roInvokeCmndAtSap at /bisos/var/cs/ro/sap/csInvSiteRegContainer.cs/csSiteRegBox/rpyc/default of box_unitsFind with {'argsList': ['uniqueBoxId', '4c4c4544-0043-3510-8052-b9c04f4c4e31'], 'rtInv': <bisos.b.cs.rtInvoker.RtInvoker object at 0x7fb82dc55c50>, 'cmndOutcome': <bisos.b.op.Outcome object at 0x7fb82d25dcd0>}
: roInvokeCmndAtSap at /bisos/var/cs/ro/sap/csInvSiteRegContainer.cs/csSiteRegContainer/rpyc/default of container_unitsFind with {'model': 'Pure', 'abode': 'Mobile', 'purpose': 'LinuxU', 'argsList': ['boxId', 'box['], 'rtInv': <bisos.b.cs.rtInvoker.RtInvoker object at 0x7fb82e19c8d0>, 'cmndOutcome': <bisos.b.op.Outcome object at 0x7fb82d25dcd0>}
: []
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        
        if (boxNus := invSiteRegBox.thisBox_findNu().pyWCmnd(cmndOutcome,).results) == None: return failed(cmndOutcome)
        # boxNus = ast.literal_eval(boxNus)
        containers = []
        
        if len(boxNus) == 0:
            # Should log here, not note.
            # b_io.ann.note("No boxnu has been assigned to this system.")
            return cmndOutcome.set(opResults=f"{containers}",)

        boxNu = boxNus[0]

        if (containers := reg_container_find().pyWCmnd(cmndOutcome,
            pyKwArgs={'model': model, 'abode': abode, 'purpose': purpose, 'argsList': ['boxId', f"{boxNu}"]},
        ).results) == None: return failed(cmndOutcome)

        return cmndOutcome.set(opResults=f"{containers}",)

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "thisSys_assignContainer" :comment "" :noMapping "t" :extent "verify" :ro "noCli" :parsMand "model abode purpose" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<thisSys_assignContainer>>  =verify= parsMand=model abode purpose ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class thisSys_assignContainer(cs.Cmnd):
    cmndParamsMandatory = [ 'model', 'abode', 'purpose', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}
    rtInvConstraints = cs.rtInvoker.RtInvoker.new_noRo() # NO RO From CLI

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             model: typing.Optional[str]=None,  # Cs Mandatory Param
             abode: typing.Optional[str]=None,  # Cs Mandatory Param
             purpose: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'model': model, 'abode': abode, 'purpose': purpose, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
####+END:
        if self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Equivalent of: -i reg_box_find $( -i thisBoxUUID ). Result: boxNu
       NOTYET csSiteRegContainer.cs --model=Pure --abode=Mobile --purpose=LinuxU -i container_unitsFind boxId box1014
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  svcInvSiteRegContainer.cs --model=Pure --abode=Mobile --purpose=LinuxU -i thisSys_assignContainer
#+end_src
#+RESULTS:
: roInvokeCmndAtSap at /bisos/var/cs/ro/sap/csInvSiteRegContainer.cs/csSiteRegBox/rpyc/default of box_unitsFind with {'argsList': ['uniqueBoxId', '4c4c4544-0043-3510-8052-b9c04f4c4e31'], 'rtInv': <bisos.b.cs.rtInvoker.RtInvoker object at 0x7f2e7ba72d90>, 'cmndOutcome': <bisos.b.op.Outcome object at 0x7f2e7ba721d0>}
: roOutcomeOf box_unitsFind::  ['1017']
: roInvokeCmndAtSap at /bisos/var/cs/ro/sap/csInvSiteRegContainer.cs/csSiteRegContainer/rpyc/default of container_unitsFind with {'model': 'Pure', 'abode': 'Mobile', 'purpose': 'LinuxU', 'argsList': ['boxId', '1017'], 'rtInv': <bisos.b.cs.rtInvoker.RtInvoker object at 0x7f2e7ba70510>, 'cmndOutcome': <bisos.b.op.Outcome object at 0x7f2e7ba721d0>}
: roOutcomeOf container_unitsFind::  ['1102']
: ['1102'] has already been registered.
: 0
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome


        if (boxNus := invSiteRegBox.thisBox_findNu().pyWCmnd(cmndOutcome,).results) == None: return failed(cmndOutcome)
        # boxNus = ast.literal_eval(boxNus)

        if len(boxNus) == 0:
            if (boxNus := invSiteRegBox.thisBox_assign().pyWCmnd(cmndOutcome,).results) == None: return failed(cmndOutcome)
            # boxNus = ast.literal_eval(boxNus)


        if len(boxNus) == 0: return failed(cmndOutcome)

        boxNu = boxNus[0]

        if (containers := reg_container_find().pyWCmnd(cmndOutcome,
            pyKwArgs={'model': model, 'abode': abode, 'purpose': purpose, 'argsList': ['boxId', f"{boxNu}"]},
        ).results) == None: return failed(cmndOutcome)

        if len(containers) == 0:
            if (containerId := reg_container_add().pyWCmnd(
                    cmndOutcome,
                    pyKwArgs={'model': model, 'abode': abode, 'purpose': purpose, 'boxNu': boxNu},
            ).results) == None: return failed(cmndOutcome)
        else:
            b_io.ann.note(f"{containers} has already been registered.")
            if (containerDict := reg_container_read().pyWCmnd(
                    cmndOutcome,
                    pyKwArgs={'model': model, 'abode': abode, 'purpose': purpose, 'containerNu': containers[0]},
            ).results) == None: return failed(cmndOutcome)

            containerId = containerDict['containerId']

        return cmndOutcome.set(opResults=f"{containerId}",)


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "virt_assignContainer" :comment "" :extent "verify" :ro "noCli" :parsMand "model abode purpose" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<virt_assignContainer>>  =verify= parsMand=model abode purpose ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class virt_assignContainer(cs.Cmnd):
    cmndParamsMandatory = [ 'model', 'abode', 'purpose', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}
    rtInvConstraints = cs.rtInvoker.RtInvoker.new_noRo() # NO RO From CLI

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             model: typing.Optional[str]=None,  # Cs Mandatory Param
             abode: typing.Optional[str]=None,  # Cs Mandatory Param
             purpose: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'model': model, 'abode': abode, 'purpose': purpose, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        model = csParam.mappedValue('model', model)
        abode = csParam.mappedValue('abode', abode)
        purpose = csParam.mappedValue('purpose', purpose)
####+END:
        if self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Equivalent of: -i reg_box_find $( -i thisBoxUUID ). Result: boxNu
       NOTYET csSiteRegContainer.cs --model=Pure --abode=Mobile --purpose=LinuxU -i container_unitsFind boxId box1014
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  svcInvSiteRegContainer.cs --model=Pure --abode=Mobile --purpose=LinuxU -i thisSys_assignContainer
#+end_src
#+RESULTS:
: roInvokeCmndAtSap at /bisos/var/cs/ro/sap/csInvSiteRegContainer.cs/csSiteRegBox/rpyc/default of box_unitsFind with {'argsList': ['uniqueBoxId', '4c4c4544-0043-3510-8052-b9c04f4c4e31'], 'rtInv': <bisos.b.cs.rtInvoker.RtInvoker object at 0x7f2e7ba72d90>, 'cmndOutcome': <bisos.b.op.Outcome object at 0x7f2e7ba721d0>}
: roOutcomeOf box_unitsFind::  ['1017']
: roInvokeCmndAtSap at /bisos/var/cs/ro/sap/csInvSiteRegContainer.cs/csSiteRegContainer/rpyc/default of container_unitsFind with {'model': 'Pure', 'abode': 'Mobile', 'purpose': 'LinuxU', 'argsList': ['boxId', '1017'], 'rtInv': <bisos.b.cs.rtInvoker.RtInvoker object at 0x7f2e7ba70510>, 'cmndOutcome': <bisos.b.op.Outcome object at 0x7f2e7ba721d0>}
: roOutcomeOf container_unitsFind::  ['1102']
: ['1102'] has already been registered.
: 0
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        if model != 'Virt':
            return failed(cmndOutcome)

        if (containerId := reg_container_add().pyWCmnd(
                cmndOutcome,
                pyKwArgs={'model': model, 'abode': abode, 'purpose': purpose, 'boxNu': 'virt'},
        ).results) == None: return failed(cmndOutcome)

        return cmndOutcome.set(opResults=f"{containerId}",)


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "withContainerIdRead" :comment "" :extent "verify" :ro "noCli" :parsMand "" :parsOpt "" :argsMin 1 :argsMax 1 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<withContainerIdRead>>  =verify= argsMin=1 argsMax=1 ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class withContainerIdRead(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 1,}
    rtInvConstraints = cs.rtInvoker.RtInvoker.new_noRo() # NO RO From CLI

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
        if self.cmndDocStr(""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  svcInvSiteRegContainer.cs -i withContainerIdRead HSS-1006
#+end_src
#+RESULTS:
: roInvokeCmndAtSap at /bisos/var/cs/ro/sap/csInvSiteRegContainer.cs/csSiteRegContainer/rpyc/default of container_unitRead with {'model': 'Host', 'abode': 'Shield', 'purpose': 'Server', 'containerNu': '1006', 'rtInv': <bisos.b.cs.rtInvoker.RtInvoker object at 0x7f20e70dd750>, 'cmndOutcome': <bisos.b.op.Outcome object at 0x7f20e657a550>}
: roOutcomeOf container_unitRead::  {'function': 'Server', 'abode': 'Shield', 'boxId': '1017', 'containerId': 'HSS-1006', 'model': 'Host', 'containerNu': '1006'}
: Host/Shield/Server/1006
: {'function': 'Server', 'abode': 'Shield', 'boxId': '1017', 'containerId': 'HSS-1006', 'model': 'Host', 'containerNu': '1006'}
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        cmndArgsSpecDict = self.cmndArgsSpec()
        cmndsArgs = self.cmndArgsGet("0", cmndArgsSpecDict, argsList)

        modelInitial = cmndsArgs[0]
        abodeInitial = cmndsArgs[1]
        purposeInitial = cmndsArgs[2]

        thisModel = cntnrCharName.Models(modelInitial).name
        thisAbode = cntnrCharName.Abodes(abodeInitial).name
        thisPurpose = cntnrCharName.Purposes(purposeInitial).name

        #print(getattr(cntnrCharName.Models, f'{thisModel}').value)

        splited = cmndsArgs.split('-')
        containerNu = splited[1]

        if (readResults := reg_container_read().pyWCmnd(
                cmndOutcome,
                pyKwArgs={'model': thisModel, 'abode': thisAbode, 'purpose': thisPurpose, 'containerNu': containerNu},
        ).results) == None: return failed(cmndOutcome)

        return cmndOutcome.set(opResults=readResults,)

####+BEGIN: b:py3:cs:method/args :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self, ):
####+END:
        """
***** Cmnd Args Specification  -- Each As Any.
"""
        cmndArgsSpecDict = cs.arg.CmndArgsSpecDict()
        cmndArgsSpecDict.argsDictAdd(
            argPosition="0",
            argName="cmndArgs",
            argChoices=[],
            argDescription="List Of CmndArgs To Be Processed. Each As Any."
        )

        return cmndArgsSpecDict

    
####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "Invoke Service Commands At Site Registrar" :anchor ""  :extraInfo "Command Services Section"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _Invoke Service Commands At Site Registrar_: |]]  Command Services Section  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "reg_sapCreateContainer" :ro "noCli" :noMapping "t" :comment "" :parsMand "perfName" :parsOpt "rosmuControl" :argsMin 0 :argsMax 0
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<reg_sapCreateContainer>>  =verify= parsMand=perfName parsOpt=rosmuControl ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class reg_sapCreateContainer(cs.Cmnd):
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
####+END:
        """\
***** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Creates path for ro_sap and updates FPs
        """
        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
svcInvSiteRegContainer.cs --perfName=svcSiteRegistrars -i reg_sapCreateContainer
#+end_src
#+RESULTS:
#+begin_example
None
FileParam.writeTo path=/bisos/var/cs/ro/sap/svcInvSiteRegContainer.cs/svcSiteRegistrars/svcSiteRegistrars/rpyc/perfIpAddr/value value=192.168.0.153
FileParam.writeTo path=/bisos/var/cs/ro/sap/svcInvSiteRegContainer.cs/svcSiteRegistrars/svcSiteRegistrars/rpyc/perfPortNu/value value=22222003
FileParam.writeTo path=/bisos/var/cs/ro/sap/svcInvSiteRegContainer.cs/svcSiteRegistrars/svcSiteRegistrars/rpyc/accessControl/value value=placeholder
FileParam.writeTo path=/bisos/var/cs/ro/sap/svcInvSiteRegContainer.cs/svcSiteRegistrars/svcSiteRegistrars/rpyc/perfName/value value=svcSiteRegistrars
FileParam.writeTo path=/bisos/var/cs/ro/sap/svcInvSiteRegContainer.cs/svcSiteRegistrars/svcSiteRegistrars/rpyc/perfModel/value value=rpyc
FileParam.writeTo path=/bisos/var/cs/ro/sap/svcInvSiteRegContainer.cs/svcSiteRegistrars/svcSiteRegistrars/rpyc/rosmu/value value=svcInvSiteRegContainer.cs
FileParam.writeTo path=/bisos/var/cs/ro/sap/svcInvSiteRegContainer.cs/svcSiteRegistrars/svcSiteRegistrars/rpyc/rosmuSel/value value=default
FileParam.writeTo path=/bisos/var/cs/ro/sap/svcInvSiteRegContainer.cs/svcSiteRegistrars/svcSiteRegistrars/rpyc/rosmuControl/value value=bisos
FileParam.writeTo path=/bisos/var/cs/ro/sap/svcInvSiteRegContainer.cs/svcSiteRegistrars/svcSiteRegistrars/rpyc/perfIpAddr/value value=192.168.0.90
FileParam.writeTo path=/bisos/var/cs/ro/sap/svcInvSiteRegContainer.cs/svcSiteRegistrars/svcSiteRegistrars/rpyc/perfPortNu/value value=22222003
FileParam.writeTo path=/bisos/var/cs/ro/sap/svcInvSiteRegContainer.cs/svcSiteRegistrars/svcSiteRegistrars/rpyc/accessControl/value value=placeholder
FileParam.writeTo path=/bisos/var/cs/ro/sap/svcInvSiteRegContainer.cs/svcSiteRegistrars/svcSiteRegistrars/rpyc/perfName/value value=svcSiteRegistrars
FileParam.writeTo path=/bisos/var/cs/ro/sap/svcInvSiteRegContainer.cs/svcSiteRegistrars/svcSiteRegistrars/rpyc/perfModel/value value=rpyc
FileParam.writeTo path=/bisos/var/cs/ro/sap/svcInvSiteRegContainer.cs/svcSiteRegistrars/svcSiteRegistrars/rpyc/rosmu/value value=svcInvSiteRegContainer.cs
FileParam.writeTo path=/bisos/var/cs/ro/sap/svcInvSiteRegContainer.cs/svcSiteRegistrars/svcSiteRegistrars/rpyc/rosmuSel/value value=default
FileParam.writeTo path=/bisos/var/cs/ro/sap/svcInvSiteRegContainer.cs/svcSiteRegistrars/svcSiteRegistrars/rpyc/rosmuControl/value value=bisos
/bisos/var/cs/ro/sap/svcInvSiteRegContainer.cs/svcSiteRegistrars/svcSiteRegistrars/rpyc
#+end_example
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        perfModel = "rpyc"
        rosmu = cs.G.icmMyName()

        print(rosmuControl)

        if rosmuControl:
            perfName = "exampleRegistrar"
            rosmuSel = 'default'  #  A file path to
            perfIpAddr = "localhost"
        else:
            rosmuSel = "default"
            rosmuControl = 'bisos'

            confFps = invSiteRegContainerConf.RegContainerInvConf_FPs()
            ipAddrs_fp =  confFps.fps_getParam('regContainerPerfAddrs')
            ipAddrStr = ipAddrs_fp.parValueGet()
            ipAddrs = ast.literal_eval(ipAddrStr)  # Produces list of strings
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

        if (boxSapPath := invSiteRegBox.reg_sapCreateBox().pyWCmnd(cmndOutcome,
                                                                   perfName=perfName,
                                                                   rosmuControl=None,
        ).results) == None: return failed(cmndOutcome)


        return cmndOutcome.set(opResults=sapPath,)


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "reg_container_add" :comment "" :extent "verify" :ro "cli" :parsMand "model abode purpose boxNu" :parsOpt "containerNu" :argsMin 0 :argsMax 0 :pyInv "pyKwArgs"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<reg_container_add>>  =verify= parsMand=model abode purpose boxNu parsOpt=containerNu ro=cli pyInv=pyKwArgs   [[elisp:(org-cycle)][| ]]
#+end_org """
class reg_container_add(cs.Cmnd):
    cmndParamsMandatory = [ 'model', 'abode', 'purpose', 'boxNu', ]
    cmndParamsOptional = [ 'containerNu', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             model: typing.Optional[str]=None,  # Cs Mandatory Param
             abode: typing.Optional[str]=None,  # Cs Mandatory Param
             purpose: typing.Optional[str]=None,  # Cs Mandatory Param
             boxNu: typing.Optional[str]=None,  # Cs Mandatory Param
             containerNu: typing.Optional[str]=None,  # Cs Optional Param
             pyKwArgs: typing.Any=None,   # pyInv Argument
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'model': model, 'abode': abode, 'purpose': purpose, 'boxNu': boxNu, 'containerNu': containerNu, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        model = csParam.mappedValue('model', model)
        abode = csParam.mappedValue('abode', abode)
        purpose = csParam.mappedValue('purpose', purpose)
        boxNu = csParam.mappedValue('boxNu', boxNu)
        containerNu = csParam.mappedValue('containerNu', containerNu)
####+END:
        if self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  A starting point command.
        #+end_org """): return(cmndOutcome)

        cmndClass = perfSiteRegContainer.ro_container_add
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

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "reg_container_read" :comment "" :extent "verify" :ro "cli" :parsMand "model abode purpose containerNu" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv "pyKwArgs"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<reg_container_read>>  =verify= parsMand=model abode purpose containerNu ro=cli pyInv=pyKwArgs   [[elisp:(org-cycle)][| ]]
#+end_org """
class reg_container_read(cs.Cmnd):
    cmndParamsMandatory = [ 'model', 'abode', 'purpose', 'containerNu', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             model: typing.Optional[str]=None,  # Cs Mandatory Param
             abode: typing.Optional[str]=None,  # Cs Mandatory Param
             purpose: typing.Optional[str]=None,  # Cs Mandatory Param
             containerNu: typing.Optional[str]=None,  # Cs Mandatory Param
             pyKwArgs: typing.Any=None,   # pyInv Argument
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'model': model, 'abode': abode, 'purpose': purpose, 'containerNu': containerNu, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        model = csParam.mappedValue('model', model)
        abode = csParam.mappedValue('abode', abode)
        purpose = csParam.mappedValue('purpose', purpose)
        containerNu = csParam.mappedValue('containerNu', containerNu)
####+END:
        if self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  A starting point command.
        #+end_org """): return(cmndOutcome)

        cmndClass = perfSiteRegContainer.container_unitRead
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


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "reg_container_update" :comment "" :extent "verify" :ro "cli" :parsMand "model abode purpose containerNu boxNu" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv "pyKwArgs"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<reg_container_update>>  =verify= parsMand=model abode purpose containerNu boxNu ro=cli pyInv=pyKwArgs   [[elisp:(org-cycle)][| ]]
#+end_org """
class reg_container_update(cs.Cmnd):
    cmndParamsMandatory = [ 'model', 'abode', 'purpose', 'containerNu', 'boxNu', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             model: typing.Optional[str]=None,  # Cs Mandatory Param
             abode: typing.Optional[str]=None,  # Cs Mandatory Param
             purpose: typing.Optional[str]=None,  # Cs Mandatory Param
             containerNu: typing.Optional[str]=None,  # Cs Mandatory Param
             boxNu: typing.Optional[str]=None,  # Cs Mandatory Param
             pyKwArgs: typing.Any=None,   # pyInv Argument
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'model': model, 'abode': abode, 'purpose': purpose, 'containerNu': containerNu, 'boxNu': boxNu, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        model = csParam.mappedValue('model', model)
        abode = csParam.mappedValue('abode', abode)
        purpose = csParam.mappedValue('purpose', purpose)
        containerNu = csParam.mappedValue('containerNu', containerNu)
        boxNu = csParam.mappedValue('boxNu', boxNu)
####+END:
        if self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  A starting point command.
        #+end_org """): return(cmndOutcome)

        cmndClass = perfSiteRegContainer.container_unitUpdate
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

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "reg_container_delete" :comment "" :extent "verify" :ro "cli" :parsMand "model abode purpose containerNu" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv "pyKwArgs"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<reg_container_delete>>  =verify= parsMand=model abode purpose containerNu ro=cli pyInv=pyKwArgs   [[elisp:(org-cycle)][| ]]
#+end_org """
class reg_container_delete(cs.Cmnd):
    cmndParamsMandatory = [ 'model', 'abode', 'purpose', 'containerNu', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             model: typing.Optional[str]=None,  # Cs Mandatory Param
             abode: typing.Optional[str]=None,  # Cs Mandatory Param
             purpose: typing.Optional[str]=None,  # Cs Mandatory Param
             containerNu: typing.Optional[str]=None,  # Cs Mandatory Param
             pyKwArgs: typing.Any=None,   # pyInv Argument
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'model': model, 'abode': abode, 'purpose': purpose, 'containerNu': containerNu, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        model = csParam.mappedValue('model', model)
        abode = csParam.mappedValue('abode', abode)
        purpose = csParam.mappedValue('purpose', purpose)
        containerNu = csParam.mappedValue('containerNu', containerNu)
####+END:
        if self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  A starting point command.
        #+end_org """): return(cmndOutcome)

        cmndClass = perfSiteRegContainer.container_unitDelete
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


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "reg_container_find" :comment "" :extent "verify" :ro "cli" :parsMand "model abode purpose" :parsOpt ""  :argsMin 2 :argsMax 2 :pyInv "pyKwArgs"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<reg_container_find>>  =verify= parsMand=model abode purpose argsMin=2 argsMax=2 ro=cli pyInv=pyKwArgs   [[elisp:(org-cycle)][| ]]
#+end_org """
class reg_container_find(cs.Cmnd):
    cmndParamsMandatory = [ 'model', 'abode', 'purpose', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 2, 'Max': 2,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             model: typing.Optional[str]=None,  # Cs Mandatory Param
             abode: typing.Optional[str]=None,  # Cs Mandatory Param
             purpose: typing.Optional[str]=None,  # Cs Mandatory Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
             pyKwArgs: typing.Any=None,   # pyInv Argument
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'model': model, 'abode': abode, 'purpose': purpose, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        model = csParam.mappedValue('model', model)
        abode = csParam.mappedValue('abode', abode)
        purpose = csParam.mappedValue('purpose', purpose)
####+END:
        if self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  A starting point command.
        #+end_org """): return(cmndOutcome)

        cmndClass = perfSiteRegContainer.container_unitsFind
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


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "reg_container_locateInAll" :comment "" :extent "verify" :ro "cli" :parsMand "" :parsOpt ""  :argsMin 2 :argsMax 2 :pyInv "pyKwArgs"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<reg_container_locateInAll>>  =verify= argsMin=2 argsMax=2 ro=cli pyInv=pyKwArgs   [[elisp:(org-cycle)][| ]]
#+end_org """
class reg_container_locateInAll(cs.Cmnd):
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

        failed = b_io.eh.badOutcome
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
####+END:
        if self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  A starting point command.
        #+end_org """): return(cmndOutcome)

        cmndClass = perfSiteRegContainer.container_locateInAll
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


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "reg_container_unitsListAll" :comment "" :extent "verify" :ro "cli" :parsMand "" :parsOpt ""  :argsMin 0 :argsMax 0 :pyInv "pyKwArgs"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<reg_container_unitsListAll>>  =verify= ro=cli pyInv=pyKwArgs   [[elisp:(org-cycle)][| ]]
#+end_org """
class reg_container_unitsListAll(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             pyKwArgs: typing.Any=None,   # pyInv Argument
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
####+END:
        if self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  A starting point command.
        #+end_org """): return(cmndOutcome)

        cmndClass = perfSiteRegContainer.container_unitsListAll
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



####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "reg_container_list" :comment "" :extent "verify" :ro "cli" :parsMand "model abode purpose" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv "pyKwArgs"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<reg_container_list>>  =verify= parsMand=model abode purpose ro=cli pyInv=pyKwArgs   [[elisp:(org-cycle)][| ]]
#+end_org """
class reg_container_list(cs.Cmnd):
    cmndParamsMandatory = [ 'model', 'abode', 'purpose', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             model: typing.Optional[str]=None,  # Cs Mandatory Param
             abode: typing.Optional[str]=None,  # Cs Mandatory Param
             purpose: typing.Optional[str]=None,  # Cs Mandatory Param
             pyKwArgs: typing.Any=None,   # pyInv Argument
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'model': model, 'abode': abode, 'purpose': purpose, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        model = csParam.mappedValue('model', model)
        abode = csParam.mappedValue('abode', abode)
        purpose = csParam.mappedValue('purpose', purpose)
####+END:
        if self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  A starting point command.
        #+end_org """): return(cmndOutcome)

        cmndClass = perfSiteRegContainer.container_unitsList
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
