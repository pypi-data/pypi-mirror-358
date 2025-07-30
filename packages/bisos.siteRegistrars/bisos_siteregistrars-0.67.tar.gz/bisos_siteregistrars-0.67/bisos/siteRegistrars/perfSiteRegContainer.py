# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: =CS-Lib= A RO service for registration of Containers at a site.
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


# from bisos import siteRegistrars

from bisos.siteRegistrars import invSiteRegContainer
from bisos.siteRegistrars import perfSiteRegContainerConf
from bisos.siteRegistrars import containerRegfps
from bisos.bpo import bpo
from bisos.cntnr import cntnrCharName

import pwd
import pathlib

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

# NOTYET, Perhaps duplicate

# G = cs.globalContext.get()
# icmRunArgs = G.icmRunArgsGet()


svcName = "csSiteRegContainer"

# roSiteRegistrarSapPath = cs.ro.SapBase_FPs.svcNameToRoSapPath(svcName)  # static method

cs.invOutcomeReportControl(cmnd=True, ro=True)

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

    thisModel = 'Pure'
    thisAbode = 'Mobile'
    thisPurpose = 'LinuxU'
    thisBoxNu = 'box1014'
    thisContainerNu = '1099'

    unitsPars = collections.OrderedDict([('model', thisModel), ('abode', thisAbode), ('purpose', thisPurpose)])
    unitBasePars = collections.OrderedDict([('model', thisModel), ('abode', thisAbode), ('purpose', thisPurpose), ('containerNu', thisContainerNu)])
    createPars = collections.OrderedDict([('model', thisModel), ('abode', thisAbode), ('purpose', thisPurpose), ('containerNu', thisContainerNu), ('boxNu', thisBoxNu)])
    addPars = collections.OrderedDict([('model', thisModel), ('abode', thisAbode), ('purpose', thisPurpose), ('boxNu', thisBoxNu)])

    ro_perfName = collections.OrderedDict([('perfName', perfName),])
    ro_unitsPars = cs.examples.perfNameParsInsert(unitsPars, perfName)
    ro_unitBasePars = cs.examples.perfNameParsInsert(unitBasePars, perfName)
    ro_createPars = cs.examples.perfNameParsInsert(createPars, perfName)
    ro_addPars = cs.examples.perfNameParsInsert(addPars, perfName)

    if sectionTitle == 'default':
        cs.examples.menuChapter('*Performer Only Commands*')

    #cmnd("someExample", pars=od([('boxNu', thisBoxNu)]), args="some args", verb=['none', 'full'])

    cmnd('config_siteContainersBaseObtain')
    cmnd('container_locateInAll', args=f"boxId {thisBoxNu}")
    cmnd('container_unitsListAll',)

    cmnd('container_unitCreate', pars=createPars)
    cmnd('container_unitRead', pars=unitBasePars)
    cmnd('container_unitUpdate', pars=createPars)
    cmnd('container_unitDelete', pars=unitBasePars)
    cmnd('container_unitId', pars=unitBasePars, comment="# E.g., PML-1099")
    cmnd('ro_container_add', pars=addPars)

    cs.examples.menuSection('*Performer Only Units (all units) Commands*')

    cmnd('container_unitsNextNu', pars=unitsPars)
    cmnd('container_unitsList', pars=unitsPars)
    cmnd('container_unitsFind', pars=unitsPars, args=f"boxId {thisBoxNu}")

    cs.examples.menuSection('*Performer Only Repos Commands*')

    cmnd('container_repoPull', pars=unitsPars)
    cmnd('container_repoPush', pars=unitsPars)
    cmnd('container_repoLock', pars=unitsPars)
    cmnd('container_repoUnlock', pars=unitsPars)

    cs.examples.menuSection(f'*RO Service Commands -- {perfName}*')

    cmnd('ro_container_add', pars=ro_addPars)
    cmnd('container_unitRead', pars=ro_unitBasePars)
    cmnd('container_unitUpdate', pars=ro_createPars)
    cmnd('container_unitDelete', pars=ro_unitBasePars)
    cmnd('container_unitsFind', pars=ro_unitsPars, args=f"boxId {thisBoxNu}")
    cmnd('container_unitsList', pars=ro_unitsPars, comment="| pyLiteralTo.cs -i stdinToBlack")

    perfName = 'svcSiteRegistrars'

    cs.examples.menuSection(f'*RO Service Commands -- {perfName}*')

    ro_perfName = collections.OrderedDict([('perfName', perfName),])
    ro_unitsPars = cs.examples.perfNameParsInsert(unitsPars, perfName)
    ro_unitBasePars = cs.examples.perfNameParsInsert(unitBasePars, perfName)
    ro_createPars = cs.examples.perfNameParsInsert(createPars, perfName)
    ro_addPars = cs.examples.perfNameParsInsert(addPars, perfName)

    cmnd('ro_container_add', pars=ro_addPars)
    cmnd('container_unitRead', pars=ro_unitBasePars)
    cmnd('container_unitUpdate', pars=ro_createPars)
    cmnd('container_unitDelete', pars=ro_unitBasePars)
    cmnd('container_unitsFind', pars=ro_unitsPars, args=f"boxId {thisBoxNu}")
    cmnd('container_unitsList', pars=ro_unitsPars, comment="| pyLiteralTo.cs -i stdinToBlack")
    cmnd('container_unitsListAll', pars=ro_perfName, comment="| pyLiteralTo.cs -i stdinToBlack")

    cs.examples.menuSection('*Container ID Mapping Commands*')

    cmnd('withContainerIdGetBase', args=f"PML-1006", comment="# inverse of -i container_unitId")


####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "Configuration: Performer Only CmndSvcs" :anchor ""  :extraInfo "Command Services Section"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _Configuration: Performer Only CmndSvcs_: |]]  Command Services Section  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "config_siteContainersBaseObtain" :comment "" :extent "verify" :ro "noCli" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<config_siteContainersBaseObtain>>  =verify= ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class config_siteContainersBaseObtain(cs.Cmnd):
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
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Outcome: Containers base directory. NOTYET, should become configurable
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  csSiteRegContainer.cs -i config_siteContainersBaseObtain
#+end_src
#+RESULTS:
:
: /bxo/iso/pmc_clusterNeda-containers/assign
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        confFps = perfSiteRegContainerConf.RegContainerPerfConf_FPs()
        containersBpoId_fp =  confFps.fps_getParam('regContainersBpoId')
        containersBpoPath = bpo.bpoBaseDir_obtain(containersBpoId_fp.parValueGet())
        siteContainersBase = pathlib.Path(containersBpoPath).joinpath('assign') # Result

        return cmndOutcome.set(opResults=siteContainersBase,)


####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "Performer Only CmndSvcs" :anchor ""  :extraInfo "Command Services Section"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _Performer Only CmndSvcs_: |]]  Command Services Section  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:



####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "container_unitCreate" :comment "" :extent "verify" :ro "noCli" :parsMand "model abode purpose containerNu boxNu" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<container_unitCreate>>  =verify= parsMand=model abode purpose containerNu boxNu ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class container_unitCreate(cs.Cmnd):
    cmndParamsMandatory = [ 'model', 'abode', 'purpose', 'containerNu', 'boxNu', ]
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
             containerNu: typing.Optional[str]=None,  # Cs Mandatory Param
             boxNu: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        callParamsDict = {'model': model, 'abode': abode, 'purpose': purpose, 'containerNu': containerNu, 'boxNu': boxNu, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        model = csParam.mappedValue('model', model)
        abode = csParam.mappedValue('abode', abode)
        purpose = csParam.mappedValue('purpose', purpose)
        containerNu = csParam.mappedValue('containerNu', containerNu)
        boxNu = csParam.mappedValue('boxNu', boxNu)
####+END:
        if self.cmndDocStr(""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  A starting point command.
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  csSiteRegContainer.cs --model=Pure --abode=Mobile --purpose=LinuxU --containerNu=1099 --boxNu=box1014 -i perf_containerUnitCreate
#+end_src
#+RESULTS:
:
: FileParam.writeTo path=/bxo/iso/pmc_clusterNeda-containers/assign/Pure/Mobile/LinuxU/1099/model/value value=Pure
: FileParam.writeTo path=/bxo/iso/pmc_clusterNeda-containers/assign/Pure/Mobile/LinuxU/1099/function/value value=LinuxU
: FileParam.writeTo path=/bxo/iso/pmc_clusterNeda-containers/assign/Pure/Mobile/LinuxU/1099/abode/value value=Mobile
: FileParam.writeTo path=/bxo/iso/pmc_clusterNeda-containers/assign/Pure/Mobile/LinuxU/1099/containerNu/value value=1099
: FileParam.writeTo path=/bxo/iso/pmc_clusterNeda-containers/assign/Pure/Mobile/LinuxU/1099/containerId/value value=PML-1099
: FileParam.writeTo path=/bxo/iso/pmc_clusterNeda-containers/assign/Pure/Mobile/LinuxU/1099/boxId/value value=box1014
: PML-1099
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        regfps = containerRegfps.Container_RegFPs(
            model=model,
            abode=abode,
            purpose=purpose,
            nu=containerNu,
        )

        containerId = regfps.unitCreate(boxNu)

        return cmndOutcome.set(opResults=containerId,)

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "container_unitRead" :comment "" :extent "verify" :ro "" :parsMand "model abode purpose containerNu" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<container_unitRead>>  =verify= parsMand=model abode purpose containerNu   [[elisp:(org-cycle)][| ]]
#+end_org """
class container_unitRead(cs.Cmnd):
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
    ) -> b.op.Outcome:

        callParamsDict = {'model': model, 'abode': abode, 'purpose': purpose, 'containerNu': containerNu, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        model = csParam.mappedValue('model', model)
        abode = csParam.mappedValue('abode', abode)
        purpose = csParam.mappedValue('purpose', purpose)
        containerNu = csParam.mappedValue('containerNu', containerNu)
####+END:
        if self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Given boxNu, uniqBoxId and optionally boxName, update the info if missing. Report if inconsistent.
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  csSiteRegContainer.cs --model=Pure --abode=Mobile --purpose=LinuxU --containerNu=1006  -i container_unitRead
#+end_src
#+RESULTS:
:
: {'function': 'LinuxU', 'abode': 'Mobile', 'boxId': 'box1014', 'containerId': 'PML-1006', 'model': 'Pure', 'containerNu': '1006'}
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        regfps = containerRegfps.Container_RegFPs(
            model=model,
            abode=abode,
            purpose=purpose,
            nu=containerNu,
        )

        dictOfFpsValue = regfps.unitRead()

        return cmndOutcome.set(opResults=dictOfFpsValue,)


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "container_unitUpdate" :comment "" :extent "verify" :ro "" :parsMand "model abode purpose containerNu boxNu" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<container_unitUpdate>>  =verify= parsMand=model abode purpose containerNu boxNu   [[elisp:(org-cycle)][| ]]
#+end_org """
class container_unitUpdate(cs.Cmnd):
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
    ) -> b.op.Outcome:

        callParamsDict = {'model': model, 'abode': abode, 'purpose': purpose, 'containerNu': containerNu, 'boxNu': boxNu, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        model = csParam.mappedValue('model', model)
        abode = csParam.mappedValue('abode', abode)
        purpose = csParam.mappedValue('purpose', purpose)
        containerNu = csParam.mappedValue('containerNu', containerNu)
        boxNu = csParam.mappedValue('boxNu', boxNu)
####+END:
        if self.cmndDocStr(""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  A starting point command.
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  csSiteRegContainer.cs --model=Pure --abode=Mobile --purpose=LinuxU --containerNu=1099 --boxNu=box1014 -i perf_containerUnitCreate
#+end_src
#+RESULTS:
:
: FileParam.writeTo path=/bxo/iso/pmc_clusterNeda-containers/assign/Pure/Mobile/LinuxU/1099/model/value value=Pure
: FileParam.writeTo path=/bxo/iso/pmc_clusterNeda-containers/assign/Pure/Mobile/LinuxU/1099/function/value value=LinuxU
: FileParam.writeTo path=/bxo/iso/pmc_clusterNeda-containers/assign/Pure/Mobile/LinuxU/1099/abode/value value=Mobile
: FileParam.writeTo path=/bxo/iso/pmc_clusterNeda-containers/assign/Pure/Mobile/LinuxU/1099/containerNu/value value=1099
: FileParam.writeTo path=/bxo/iso/pmc_clusterNeda-containers/assign/Pure/Mobile/LinuxU/1099/containerId/value value=PML-1099
: FileParam.writeTo path=/bxo/iso/pmc_clusterNeda-containers/assign/Pure/Mobile/LinuxU/1099/boxId/value value=box1014
: PML-1099
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        regfps = containerRegfps.Container_RegFPs(
            model=model,
            abode=abode,
            purpose=purpose,
            nu=containerNu,
        )

        containerId = regfps.unitUpdate(boxNu)

        return cmndOutcome.set(opResults=containerId,)


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "container_unitDelete" :comment "" :extent "verify" :ro "" :parsMand "model abode purpose containerNu" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<container_unitDelete>>  =verify= parsMand=model abode purpose containerNu   [[elisp:(org-cycle)][| ]]
#+end_org """
class container_unitDelete(cs.Cmnd):
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
    ) -> b.op.Outcome:

        callParamsDict = {'model': model, 'abode': abode, 'purpose': purpose, 'containerNu': containerNu, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        model = csParam.mappedValue('model', model)
        abode = csParam.mappedValue('abode', abode)
        purpose = csParam.mappedValue('purpose', purpose)
        containerNu = csParam.mappedValue('containerNu', containerNu)
####+END:
        if self.cmndDocStr(""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  A starting point command.
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  csSiteRegContainer.cs --model=Pure --abode=Mobile --purpose=LinuxU --containerNu=1099 -i container_unitDelete
#+end_src
#+RESULTS:
:
: Cmnd -- No Results
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        regfps = containerRegfps.Container_RegFPs(
            model=model,
            abode=abode,
            purpose=purpose,
            nu=containerNu,
        )

        containerId = regfps.unitDelete()

        return cmndOutcome.set(opResults=containerId,)


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "container_unitId" :comment "" :extent "verify" :ro "" :parsMand "model abode purpose containerNu" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<container_unitId>>  =verify= parsMand=model abode purpose containerNu   [[elisp:(org-cycle)][| ]]
#+end_org """
class container_unitId(cs.Cmnd):
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
    ) -> b.op.Outcome:

        callParamsDict = {'model': model, 'abode': abode, 'purpose': purpose, 'containerNu': containerNu, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        model = csParam.mappedValue('model', model)
        abode = csParam.mappedValue('abode', abode)
        purpose = csParam.mappedValue('purpose', purpose)
        containerNu = csParam.mappedValue('containerNu', containerNu)
####+END:
        if self.cmndDocStr(""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  A starting point command.
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  csSiteRegContainer.cs --model=Pure --abode=Mobile --purpose=LinuxU --containerNu=1099 -i container_unitId
#+end_src
#+RESULTS:
:
: PML-1099
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        regfps = containerRegfps.Container_RegFPs(
            model=model,
            abode=abode,
            purpose=purpose,
            nu=containerNu,
        )

        containerId = regfps.unitId()

        return cmndOutcome.set(opResults=containerId,)



####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "container_unitsNextNu" :comment "" :extent "verify" :ro "noCli" :parsMand "model abode purpose" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<container_unitsNextNu>>  =verify= parsMand=model abode purpose ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class container_unitsNextNu(cs.Cmnd):
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

        callParamsDict = {'model': model, 'abode': abode, 'purpose': purpose, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        model = csParam.mappedValue('model', model)
        abode = csParam.mappedValue('abode', abode)
        purpose = csParam.mappedValue('purpose', purpose)
####+END:
        if self.cmndDocStr(""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  result: List of all boxes
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  csSiteRegContainer.cs --model=Pure --abode=Mobile --purpose=LinuxU -i container_unitsNextNu
#+end_src
#+RESULTS:
:
: 1100
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        regUnits = containerRegfps.Container_RegFPs(
            model=model,
            abode=abode,
            purpose=purpose,
            nu=None,
        )

        nextUnitNu  = regUnits.nextUnitNu()

        return cmndOutcome.set(opResults=nextUnitNu,)

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "container_unitsList" :comment "" :extent "verify" :ro "" :parsMand "model abode purpose" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<container_unitsList>>  =verify= parsMand=model abode purpose   [[elisp:(org-cycle)][| ]]
#+end_org """
class container_unitsList(cs.Cmnd):
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
    ) -> b.op.Outcome:

        callParamsDict = {'model': model, 'abode': abode, 'purpose': purpose, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        model = csParam.mappedValue('model', model)
        abode = csParam.mappedValue('abode', abode)
        purpose = csParam.mappedValue('purpose', purpose)
####+END:
        if self.cmndDocStr(""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  result: List of all boxes
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  csSiteRegContainer.cs --model=Pure --abode=Mobile --purpose=LinuxU -i container_unitsList
#+end_src
#+RESULTS:
:
: [{'function': 'LinuxU', 'abode': 'Mobile', 'boxId': 'box1007', 'containerId': 'PML-1001', 'model': 'Pure', 'containerNu': '1001'}, {'function': 'LinuxU', 'abode': 'Mobile', 'boxId': 'box1008', 'containerId': 'PML-1002', 'model': 'Pure', 'containerNu': '1002'}, {'function': 'LinuxU', 'abode': 'Mobile', 'boxId': 'box1010', 'containerId': 'PML-1003', 'model': 'Pure', 'containerNu': '1003'}, {'function': 'LinuxU', 'abode': 'Mobile', 'boxId': 'box1012', 'containerId': 'PML-1004', 'model': 'Pure', 'containerNu': '1004'}, {'function': 'LinuxU', 'abode': 'Mobile', 'boxId': 'box1011', 'containerId': 'PML-1005', 'model': 'Pure', 'containerNu': '1005'}, {'function': 'LinuxU', 'abode': 'Mobile', 'boxId': 'box1014', 'containerId': 'PML-1006', 'model': 'Pure', 'containerNu': '1006'}, {'function': 'LinuxU', 'abode': 'Mobile', 'boxId': 'box1014', 'containerId': 'PML-1099', 'model': 'Pure', 'containerNu': '1099'}]
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        regUnits = containerRegfps.Container_RegFPs(
            model=model,
            abode=abode,
            purpose=purpose,
            nu=0,
        )

        unitsList = regUnits.unitsList()

        return cmndOutcome.set(opResults=unitsList,)


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "container_unitsFind" :comment "" :extent "verify" :ro "" :parsMand "model abode purpose" :parsOpt "" :argsMin 2 :argsMax 2 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<container_unitsFind>>  =verify= parsMand=model abode purpose argsMin=2 argsMax=2   [[elisp:(org-cycle)][| ]]
#+end_org """
class container_unitsFind(cs.Cmnd):
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
    ) -> b.op.Outcome:

        callParamsDict = {'model': model, 'abode': abode, 'purpose': purpose, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        model = csParam.mappedValue('model', model)
        abode = csParam.mappedValue('abode', abode)
        purpose = csParam.mappedValue('purpose', purpose)
####+END:
        if self.cmndDocStr(""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  result: boxBaseDir corresponding to uniqBoxId
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  csSiteRegContainer.cs --model=Pure --abode=Mobile --purpose=LinuxU -i container_unitsFind boxId box1014
#+end_src
#+RESULTS:
:
: [PosixPath('/bxo/iso/pmc_clusterNeda-containers/assign/Pure/Mobile/LinuxU/1006'), PosixPath('/bxo/iso/pmc_clusterNeda-containers/assign/Pure/Mobile/LinuxU/1099')]
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        cmndArgsSpecDict = self.cmndArgsSpec()
        parName = self.cmndArgsGet("0", cmndArgsSpecDict, argsList)
        parValue = self.cmndArgsGet("1", cmndArgsSpecDict, argsList)

        regUnits = containerRegfps.Container_RegFPs(
            model=model,
            abode=abode,
            purpose=purpose,
            nu=0,
        )

        foundList = regUnits.unitsFind(parName=parName, parValue=parValue)

        result = [ each.name for each in foundList ]

        return cmndOutcome.set(opResults=result,)

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
            argName="parName",
            argChoices=[],
            argDescription="Name of File Parameter to search for."
        )
        cmndArgsSpecDict.argsDictAdd(
            argPosition="1",
            argName="parValue",
            argChoices=[],
            argDescription="Value of File Parameter to search for."
        )
        return cmndArgsSpecDict


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "container_locateInAll" :comment "" :extent "verify" :ro "" :parsMand "" :parsOpt "" :argsMin 2 :argsMax 2 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<container_locateInAll>>  =verify= argsMin=2 argsMax=2   [[elisp:(org-cycle)][| ]]
#+end_org """
class container_locateInAll(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 2, 'Max': 2,}

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
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  result: boxBaseDir corresponding to uniqBoxId
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  csSiteRegContainer.cs --model=Pure --abode=Mobile --purpose=LinuxU -i container_unitsFind boxId box1014
#+end_src
#+RESULTS:
:
: [PosixPath('/bxo/iso/pmc_clusterNeda-containers/assign/Pure/Mobile/LinuxU/1006'), PosixPath('/bxo/iso/pmc_clusterNeda-containers/assign/Pure/Mobile/LinuxU/1099')]
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        cmndArgsSpecDict = self.cmndArgsSpec()
        parName = self.cmndArgsGet("0", cmndArgsSpecDict, argsList)
        parValue = self.cmndArgsGet("1", cmndArgsSpecDict, argsList)

        if (siteContainersBase := config_siteContainersBaseObtain().cmnd(
                rtInv=cs.RtInvoker.new_py(), cmndOutcome=cmndOutcome,
        ).results) == None : return(b_io.eh.badOutcome(cmndOutcome))

        allFiles = siteContainersBase.glob(f"**/{parName}")

        foundCcNames = []  # contaienr character names

        for eachFile in allFiles:
            fpsBase = eachFile.parent
            regFps = containerRegfps.Container_RegFPs(fpBase=fpsBase)
            storedFp = regFps.fps_getParam(parName)
            storedValue = storedFp.parValueGet()
            if storedValue == parValue:
                ccn = cntnrCharName.ContainerCharName().setContainerCharName_withPath(fpsBase)
                ccnDict = ccn.ccnDict
                foundCcNames.append(ccnDict)

        return cmndOutcome.set(opResults=foundCcNames,)


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "container_unitsListAll" :comment "" :extent "verify" :ro "" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<container_unitsListAll>>  =verify=   [[elisp:(org-cycle)][| ]]
#+end_org """
class container_unitsListAll(cs.Cmnd):
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
        if self.cmndDocStr(""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  result: boxBaseDir corresponding to uniqBoxId
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  csSiteRegContainer.cs --model=Pure --abode=Mobile --purpose=LinuxU -i container_unitsFind boxId box1014
#+end_src
#+RESULTS:
:
: [PosixPath('/bxo/iso/pmc_clusterNeda-containers/assign/Pure/Mobile/LinuxU/1006'), PosixPath('/bxo/iso/pmc_clusterNeda-containers/assign/Pure/Mobile/LinuxU/1099')]
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        if (siteContainersBase := config_siteContainersBaseObtain().cmnd(
                rtInv=cs.RtInvoker.new_py(), cmndOutcome=cmndOutcome,
        ).results) == None : return(b_io.eh.badOutcome(cmndOutcome))

        allFiles = siteContainersBase.glob(f"**/containerNu")

        results = []  # contaienr character names

        for eachFile in allFiles:
            fpsBase = eachFile.parent
            regFps = containerRegfps.Container_RegFPs(fpBase=fpsBase)
            dictOfFpsValue = regFps.unitRead()
            results.append(dictOfFpsValue)

        return cmndOutcome.set(opResults=results,)


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "container_repoPull" :comment "" :extent "verify" :ro "noCli" :parsMand "model abode purpose" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<container_repoPull>>  =verify= parsMand=model abode purpose ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class container_repoPull(cs.Cmnd):
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

        callParamsDict = {'model': model, 'abode': abode, 'purpose': purpose, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        model = csParam.mappedValue('model', model)
        abode = csParam.mappedValue('abode', abode)
        purpose = csParam.mappedValue('purpose', purpose)
####+END:
        if self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Runs: echo siteContainersBase | bx-gitRepos -i gitRemPull
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  csSiteRegContainer.cs --model=Pure --abode=Mobile --purpose=LinuxU -i container_repoPull
#+end_src
#+RESULTS:
:
: ** cmnd= echo /bxo/iso/pmc_clusterNeda-containers/assign/Pure/Mobile/LinuxU | echo bx-gitRepos -i gitRemPull
: bx-gitRepos -i gitRemPull
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        regUnits = containerRegfps.Container_RegFPs(
            model=model,
            abode=abode,
            purpose=purpose,
            nu=0,
        )

        regUnits.repoPull(cmndOutcome)

        return cmndOutcome


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "container_repoPush" :comment "" :extent "verify" :ro "noCli" :parsMand "model abode purpose" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<container_repoPush>>  =verify= parsMand=model abode purpose ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class container_repoPush(cs.Cmnd):
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

        callParamsDict = {'model': model, 'abode': abode, 'purpose': purpose, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        model = csParam.mappedValue('model', model)
        abode = csParam.mappedValue('abode', abode)
        purpose = csParam.mappedValue('purpose', purpose)
####+END:
        if self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Runs: echo siteContainersBase | bx-gitRepos -i  addCommitPush all
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  csSiteRegContainer.cs --model=Pure --abode=Mobile --purpose=LinuxU -i container_repoPush
#+end_src
#+RESULTS:
:
: ** cmnd= echo /bxo/iso/pmc_clusterNeda-containers/assign/Pure/Mobile/LinuxU | echo bx-gitRepos -i addCommitPush all
: bx-gitRepos -i addCommitPush all
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        regUnits = containerRegfps.Container_RegFPs(
            model=model,
            abode=abode,
            purpose=purpose,
            nu=0,
        )

        regUnits.repoPush(cmndOutcome)

        return cmndOutcome

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "container_repoLock" :comment "" :extent "verify" :ro "noCli" :parsMand "model abode purpose" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<container_repoLock>>  =verify= parsMand=model abode purpose ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class container_repoLock(cs.Cmnd):
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

        callParamsDict = {'model': model, 'abode': abode, 'purpose': purpose, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        model = csParam.mappedValue('model', model)
        abode = csParam.mappedValue('abode', abode)
        purpose = csParam.mappedValue('purpose', purpose)
####+END:
        if self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] NOTYET, Lock a write transaction using https://docs.gitlab.com/ee/user/project/file_lock.html
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  csSiteRegContainer.cs --model=Pure --abode=Mobile --purpose=LinuxU -i container_repoLock
#+end_src
#+RESULTS:
:
: OpError.Success
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        regUnits = containerRegfps.Container_RegFPs(
            model=model,
            abode=abode,
            purpose=purpose,
            nu=0,
        )

        regUnits.repoLock(cmndOutcome)

        return cmndOutcome


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "container_repoUnlock" :comment "" :extent "verify" :ro "noCli" :parsMand "model abode purpose" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<container_repoUnlock>>  =verify= parsMand=model abode purpose ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class container_repoUnlock(cs.Cmnd):
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

        callParamsDict = {'model': model, 'abode': abode, 'purpose': purpose, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        model = csParam.mappedValue('model', model)
        abode = csParam.mappedValue('abode', abode)
        purpose = csParam.mappedValue('purpose', purpose)
####+END:
        if self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] NOTYET, Unlock a write transaction using https://docs.gitlab.com/ee/user/project/file_lock.html
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  csSiteRegContainer.cs --model=Pure --abode=Mobile --purpose=LinuxU -i container_repoUnlock
#+end_src
#+RESULTS:
:
: OpError.Success
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        regUnits = containerRegfps.Container_RegFPs(
            model=model,
            abode=abode,
            purpose=purpose,
            nu=0,
        )

        regUnits.repoUnlock(cmndOutcome)

        return cmndOutcome


####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "RO Service Commands" :anchor ""  :extraInfo "Command Services Section"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _RO Service Commands_: |]]  Command Services Section  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "ro_container_add" :comment "" :extent "verify" :ro "cli" :parsMand "model abode purpose boxNu" :parsOpt "containerNu" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<ro_container_add>>  =verify= parsMand=model abode purpose boxNu parsOpt=containerNu ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class ro_container_add(cs.Cmnd):
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
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  NOTYET, First Implement Find
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  csSiteRegContainer.cs --model=Pure --abode=Mobile --purpose=LinuxU --boxNu=box1999 -i ro_container_add
#+end_src
#+RESULTS:
:
: box1999 has already been registered [PosixPath('/bxo/iso/pmc_clusterNeda-containers/assign/Pure/Mobile/LinuxU/1100')]
: Cmnd -- No Results
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        regUnits = containerRegfps.Container_RegFPs(
            model=model,
            abode=abode,
            purpose=purpose,
            nu=0,
        )

        if boxNu != 'virt':
            foundList = regUnits.unitsFind(parName='boxId', parValue=boxNu)

            if foundList:
                b_io.ann.note(f"{boxNu} has already been registered {foundList}")
                return(cmndOutcome)

        if not containerNu:
            containerNu = regUnits.unitsNextNu()

        regfps = containerRegfps.Container_RegFPs(
            model=model,
            abode=abode,
            purpose=purpose,
            nu=containerNu,
        )

        containerId = regfps.unitCreate(boxNu)

        return cmndOutcome.set(opResults=containerId,)

####+BEGIN: b:py3:cs:cmnd/alias :cmndName "ro_container_read" :existingName "container_unitRead" :comment ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndAlias  [[elisp:(outline-show-subtree+toggle)][||]] <<ro_container_read>> is /alias/ for [[container_unitRead]]  [[elisp:(org-cycle)][| ]]
#+end_org """
ro_container_read = type('ro_container_read', container_unitRead.__bases__, dict(container_unitRead.__dict__))
####+END:

####+BEGIN: b:py3:cs:cmnd/alias :cmndName "ro_container_update" :existingName "container_unitUpdate" :comment ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndAlias  [[elisp:(outline-show-subtree+toggle)][||]] <<ro_container_update>> is /alias/ for [[container_unitUpdate]]  [[elisp:(org-cycle)][| ]]
#+end_org """
ro_container_update = container_unitUpdate
####+END:

####+BEGIN: b:py3:cs:cmnd/alias :cmndName "ro_container_delete" :existingName "container_unitDelete" :comment ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndAlias  [[elisp:(outline-show-subtree+toggle)][||]] <<ro_container_delete>> is /alias/ for [[container_unitDelete]]  [[elisp:(org-cycle)][| ]]
#+end_org """
ro_container_delete = container_unitDelete
####+END:

####+BEGIN: b:py3:cs:cmnd/alias :cmndName "ro_container_find" :existingName "container_unitsFind" :comment ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndAlias  [[elisp:(outline-show-subtree+toggle)][||]] <<ro_container_find>> is /alias/ for [[container_unitsFind]]  [[elisp:(org-cycle)][| ]]
#+end_org """
ro_container_find = container_unitsFind
####+END:

####+BEGIN: b:py3:cs:cmnd/alias :cmndName "ro_container_list" :existingName "container_unitsList" :comment ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndAlias  [[elisp:(outline-show-subtree+toggle)][||]] <<ro_container_list>> is /alias/ for [[container_unitsList]]  [[elisp:(org-cycle)][| ]]
#+end_org """
ro_container_list = container_unitsList
####+END:

####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "Performer Facilities" :anchor ""  :extraInfo "Command Services Section Examples"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _Performer Facilities_: |]]  Command Services Section Examples  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "withContainerIdGetBase" :comment "" :extent "verify" :ro "noCli" :parsMand "" :parsOpt "" :argsMin 1 :argsMax 1 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<withContainerIdGetBase>>  =verify= argsMin=1 argsMax=1 ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class withContainerIdGetBase(cs.Cmnd):
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

        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
####+END:
        if self.cmndDocStr(""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  csSiteRegContainer.cs -i withContainerIdGetBase PML-1006
#+end_src
#+RESULTS:
:
: 
: /bxo/iso/pmc_clusterNeda-containers/assign/Pure/Mobile/LinuxU/1006
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

        if (siteContainersBase := config_siteContainersBaseObtain().cmnd(
                rtInv=cs.RtInvoker.new_py(), cmndOutcome=cmndOutcome,
        ).results) == None : return(b_io.eh.badOutcome(cmndOutcome))


        result = siteContainersBase.joinpath(f"{thisModel}/{thisAbode}/{thisPurpose}/{containerNu}")

        # print(f"{result} {thisModel} {containerNu}")

        assert result.exists()

        return cmndOutcome.set(opResults=result,)

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


####+BEGIN: b:py3:cs:framework/endOfFile :basedOn "classification"
""" #+begin_org
* [[elisp:(org-cycle)][| *End-Of-Editable-Text* |]] :: emacs and org variables and control parameters
#+end_org """

#+STARTUP: showall

### local variables:
### no-byte-compile: t
### end:
####+END:
