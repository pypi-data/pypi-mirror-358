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
** This File: /bisos/git/bxRepos/bisos-pip/siteRegistrars/py3/bisos/siteRegistrars/perfSiteRegBox.py
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

from bisos.siteRegistrars import invSiteRegBox
from bisos.siteRegistrars import perfSiteRegBoxConf
from bisos.siteRegistrars import boxRegfps
from bisos.bpo import bpo

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

svcName = "csSiteRegBox"
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

    if (thisUniqueBoxId := invSiteRegBox.thisBoxUUID().cmnd(
            rtInv=cs.RtInvoker.new_py(), cmndOutcome=b.op.Outcome(),
    ).results) == None: return(b_io.eh.badOutcome(cmndOutcome))

    if (boxNus := box_unitsFind().cmnd(
            rtInv=cs.RtInvoker.new_py(), cmndOutcome=b.op.Outcome(),
            argsList=["uniqueBoxId", thisUniqueBoxId],
    ).results) == None: return(b_io.eh.badOutcome(cmndOutcome))

    thisBoxNu = boxNus[0]
    # thisBoxNu = thisBoxPath[0].name
    thisBoxName = f"box{thisBoxNu}"

    unitsPars = collections.OrderedDict([])
    unitBasePars = collections.OrderedDict([('boxNu', thisBoxNu)])
    createPars = collections.OrderedDict([('boxNu', thisBoxNu), ('uniqueBoxId', thisUniqueBoxId), ('boxName', thisBoxName)])
    addPars = collections.OrderedDict([])
    #findArgs = f"uniqueBoxId {thisUniqueBoxId}"

    ro_unitsPars = cs.examples.perfNameParsInsert(unitsPars, perfName)
    ro_unitBasePars = cs.examples.perfNameParsInsert(unitBasePars, perfName)
    ro_createPars = cs.examples.perfNameParsInsert(createPars, perfName)
    ro_addPars = cs.examples.perfNameParsInsert(addPars, perfName)

    if sectionTitle == 'default':
        cs.examples.menuChapter('*Performer Only Commands*')

    #cmnd("someExample", pars=od([('boxNu', thisBoxNu)]), args="some args", verb=['none', 'full'])

    cmnd('config_siteBoxesBaseObtain')

    cmnd('box_unitCreate', pars=od([('boxNu', thisBoxNu), ('uniqueBoxId', thisUniqueBoxId), ('boxName', thisBoxName)]))
    cmnd('box_unitRead', pars=unitBasePars)
    cmnd('box_unitUpdate', pars=createPars)
    cmnd('box_unitDelete', pars=unitBasePars)
    cmnd('box_unitId', pars=unitBasePars, comment="# E.g., PML-1099")
    cmnd('ro_box_add', pars=addPars)

    cs.examples.menuSection('*Performer Only Units (all units) Commands*')

    cmnd('box_unitsNextNu', pars=unitsPars)
    cmnd('box_unitsList', pars=unitsPars)
    cmnd('box_unitsFind', pars=unitsPars, args=f"boxId {thisBoxNu}")
    cmnd('box_unitsFind', pars=unitsPars, args=f"uniqueBoxId {thisUniqueBoxId}")

    cs.examples.menuSection('*Performer Only Repos Commands*')

    cmnd('box_repoPull', pars=unitsPars)
    cmnd('box_repoPush', pars=unitsPars)
    cmnd('box_repoLock', pars=unitsPars)
    cmnd('box_repoUnlock', pars=unitsPars)

    cs.examples.menuSection('*RO Service Commands*')

    cmnd('ro_box_add', pars=ro_addPars)
    cmnd('box_unitRead', pars=ro_unitBasePars)
    cmnd('box_unitUpdate', pars=ro_createPars)
    cmnd('box_unitDelete', pars=ro_unitBasePars)
    cmnd('box_unitsFind', pars=ro_unitsPars, args=f"boxId {thisBoxNu}")
    cmnd('box_unitsFind', pars=ro_unitsPars, args=f"uniqueBoxId {thisUniqueBoxId}")
    cmnd('box_unitsList', pars=ro_unitsPars)

    cs.examples.menuSection('*Box ID Mapping Commands*')

    cmnd('withBoxIdGetBase', args=f"PML-1006", comment="# inverse of -i box_unitId")



####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "Configuration: Performer Only CmndSvcs" :anchor ""  :extraInfo "Command Services Section"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _Configuration: Performer Only CmndSvcs_: |]]  Command Services Section  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "config_siteBoxesBaseObtain" :comment "" :extent "verify" :ro "noCli" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<config_siteBoxesBaseObtain>>  =verify= ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class config_siteBoxesBaseObtain(cs.Cmnd):
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
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Outcome: Boxes base directory. NOTYET, should become configurable
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  svcSiteRegBox.cs -i config_siteBoxesBaseObtain
#+end_src
#+RESULTS:
:
: /bxo/iso/pmb_clusterNeda-boxes/boxes
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        confFps = perfSiteRegBoxConf.RegBoxPerfConf_FPs()
        boxsBpoId_fp =  confFps.fps_getParam('regBoxesBpoId')
        boxsBpoPath = bpo.bpoBaseDir_obtain(boxsBpoId_fp.parValueGet())
        siteBoxesBase = pathlib.Path(boxsBpoPath).joinpath('boxes') # Result

        return cmndOutcome.set(opResults=siteBoxesBase,)


####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "Performer Only CmndSvcs" :anchor ""  :extraInfo "Command Services Section"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _Performer Only CmndSvcs_: |]]  Command Services Section  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:



####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "box_unitCreate" :comment "" :extent "verify" :ro "noCli" :parsMand "boxNu uniqueBoxId" :parsOpt "boxName" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<box_unitCreate>>  =verify= parsMand=boxNu uniqueBoxId parsOpt=boxName ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class box_unitCreate(cs.Cmnd):
    cmndParamsMandatory = [ 'boxNu', 'uniqueBoxId', ]
    cmndParamsOptional = [ 'boxName', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}
    rtInvConstraints = cs.rtInvoker.RtInvoker.new_noRo() # NO RO From CLI

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             boxNu: typing.Optional[str]=None,  # Cs Mandatory Param
             uniqueBoxId: typing.Optional[str]=None,  # Cs Mandatory Param
             boxName: typing.Optional[str]=None,  # Cs Optional Param
    ) -> b.op.Outcome:

        callParamsDict = {'boxNu': boxNu, 'uniqueBoxId': uniqueBoxId, 'boxName': boxName, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        boxNu = csParam.mappedValue('boxNu', boxNu)
        uniqueBoxId = csParam.mappedValue('uniqueBoxId', uniqueBoxId)
        boxName = csParam.mappedValue('boxName', boxName)
####+END:
        if self.cmndDocStr(""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  A starting point command.
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  svcSiteRegBox.cs --boxNu=10002  --uniqueBoxId=4c4c4544-0034-3310-8051-b5c04f335832 --boxName=box1014 -i box_unitCreate
#+end_src
#+RESULTS:
:
: FileParam.writeTo path=/bxo/iso/pmb_clusterNeda-boxes/boxes/10002/boxNu/value value=10002
: FileParam.writeTo path=/bxo/iso/pmb_clusterNeda-boxes/boxes/10002/uniqueBoxId/value value=4c4c4544-0034-3310-8051-b5c04f335832
: FileParam.writeTo path=/bxo/iso/pmb_clusterNeda-boxes/boxes/10002/boxId/value value=box1014
: box1014
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        regfps = boxRegfps.Box_RegFPs(
            unitNu=boxNu,
        )

        boxName = regfps.unitCreate(uniqueBoxId, boxName)

        return cmndOutcome.set(opResults=boxName,)

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "box_unitRead" :comment "" :extent "verify" :ro "" :parsMand "boxNu" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<box_unitRead>>  =verify= parsMand=boxNu   [[elisp:(org-cycle)][| ]]
#+end_org """
class box_unitRead(cs.Cmnd):
    cmndParamsMandatory = [ 'boxNu', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             boxNu: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        callParamsDict = {'boxNu': boxNu, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        boxNu = csParam.mappedValue('boxNu', boxNu)
####+END:
        if self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Given boxNu, uniqueBoxId and optionally boxName, update the info if missing. Report if inconsistent.
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  svcSiteRegBox.cs  --boxNu=1006  -i box_unitRead
#+end_src
#+RESULTS:
:
: {'uniqueBoxId': '4c4c4544-0059-5110-8051-c6c04f564831', 'boxId': 'box1006', 'boxNu': '1006'}
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        regfps = boxRegfps.Box_RegFPs(
            unitNu=boxNu,
        )

        dictOfFpsValue = regfps.unitRead()

        return cmndOutcome.set(opResults=dictOfFpsValue,)


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "box_unitUpdate" :comment "" :extent "verify" :ro "" :parsMand "boxNu boxName" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<box_unitUpdate>>  =verify= parsMand=boxNu boxName   [[elisp:(org-cycle)][| ]]
#+end_org """
class box_unitUpdate(cs.Cmnd):
    cmndParamsMandatory = [ 'boxNu', 'boxName', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             boxNu: typing.Optional[str]=None,  # Cs Mandatory Param
             boxName: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'boxNu': boxNu, 'boxName': boxName, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        boxNu = csParam.mappedValue('boxNu', boxNu)
        boxName = csParam.mappedValue('boxName', boxName)
####+END:
        if self.cmndDocStr(""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  NOTYET, Incomplete
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  svcSiteRegBox.cs  --boxNu=1099 -i box_unitUpdate
#+end_src
#+RESULTS:
:
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        regfps = boxRegfps.Box_RegFPs(
            unitNu=boxNu,
        )

        boxId = regfps.unitUpdate(boxName)

        return cmndOutcome.set(opResults=boxId,)


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "box_unitDelete" :comment "" :extent "verify" :ro "" :parsMand "boxNu" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<box_unitDelete>>  =verify= parsMand=boxNu   [[elisp:(org-cycle)][| ]]
#+end_org """
class box_unitDelete(cs.Cmnd):
    cmndParamsMandatory = [ 'boxNu', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             boxNu: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        callParamsDict = {'boxNu': boxNu, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        boxNu = csParam.mappedValue('boxNu', boxNu)
####+END:
        if self.cmndDocStr(""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  A starting point command.
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  svcSiteRegBox.cs --boxNu=1099 -i box_unitDelete
#+end_src
#+RESULTS:
:
: Cmnd -- No Results
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        regfps = boxRegfps.Box_RegFPs(
            unitNu=boxNu,
        )

        boxId = regfps.unitDelete()

        return cmndOutcome.set(opResults=boxId,)


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "box_unitId" :comment "" :extent "verify" :ro "" :parsMand "boxNu" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<box_unitId>>  =verify= parsMand=boxNu   [[elisp:(org-cycle)][| ]]
#+end_org """
class box_unitId(cs.Cmnd):
    cmndParamsMandatory = [ 'boxNu', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             boxNu: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        callParamsDict = {'boxNu': boxNu, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        boxNu = csParam.mappedValue('boxNu', boxNu)
####+END:
        if self.cmndDocStr(""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  A starting point command.
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  svcSiteRegBox.cs --boxNu=1099 -i box_unitId
#+end_src
#+RESULTS:
:
: PML-1099
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        regfps = boxRegfps.Box_RegFPs(
            unitNu=boxNu,
        )

        boxId = regfps.unitId()

        return cmndOutcome.set(opResults=boxId,)



####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "box_unitsNextNu" :comment "" :extent "verify" :ro "noCli" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<box_unitsNextNu>>  =verify= ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class box_unitsNextNu(cs.Cmnd):
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
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  result: List of all boxes
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  svcSiteRegBox.cs  -i box_unitsNextNu
#+end_src
#+RESULTS:
:
: 10000
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        regUnits = boxRegfps.Box_RegFPs(
            unitNu=0,
        )

        nextUnitNu  = regUnits.unitsNextNu()

        return cmndOutcome.set(opResults=nextUnitNu,)

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "box_unitsList" :comment "" :extent "verify" :ro "" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<box_unitsList>>  =verify=   [[elisp:(org-cycle)][| ]]
#+end_org """
class box_unitsList(cs.Cmnd):
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
        if self.cmndDocStr(""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  result: List of all boxes
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  svcSiteRegBox.cs -i box_unitsList
#+end_src
#+RESULTS:
:
: [{'boxId': 'box1014', 'boxNu': '10002', 'uniqueBoxId': '4c4c4544-0034-3310-8051-b5c04f335832'}, {'uniqueBoxId': None, 'boxId': 'box1001', 'boxNu': '1001'}, {'uniqueBoxId': '4c4c4544-0051-3210-804e-b5c04f334b31', 'boxId': 'box1002', 'boxNu': '1002'}, {'uniqueBoxId': '4c4c4544-0057-4e10-8050-b9c04f355031', 'boxId': 'box1003', 'boxNu': '1003'}, {'uniqueBoxId': '4c4c4544-0053-3110-8031-b2c04f395931', 'boxId': 'box1004', 'boxNu': '1004'}, {'uniqueBoxId': '4c4c4544-0052-4c10-8059-c2c04f333832', 'boxId': 'box1005', 'boxNu': '1005'}, {'uniqueBoxId': '4c4c4544-0059-5110-8051-c6c04f564831', 'boxId': 'box1006', 'boxNu': '1006'}, {'uniqueBoxId': '00:16:3e:f4:7c:9e', 'boxId': 'box1007', 'boxNu': '1007'}, {'uniqueBoxId': '00:16:3e:ce:81:5a', 'boxId': 'box1008', 'boxNu': '1008'}, {'uniqueBoxId': '7d752880-1dde-11b2-8000-be639716ec5e', 'boxId': 'box1009', 'boxNu': '1009'}, {'uniqueBoxId': '27dda700-1dd2-11b2-8000-c3f6017670d5', 'boxId': 'box1010', 'boxNu': '1010'}, {'uniqueBoxId': '00:16:3e:21:8d:ba', 'boxId': 'box1011', 'boxNu': '1011'}, {'uniqueBoxId': '0003cf76-0a32-3332-ffff-382c4a7df064', 'boxId': 'box1012', 'boxNu': '1012'}, {'uniqueBoxId': '4c4c4544-0037-3510-804c-b4c04f365a31', 'boxId': 'box1013', 'boxNu': '1013'}, {'uniqueBoxId': '4c4c4544-0034-3310-8051-b5c04f335832', 'boxId': 'box1014', 'boxNu': '1014'}, {'uniqueBoxId': '4c4c4544-0034-3310-8051-b5c04f335836', 'boxId': 'box1015', 'boxNu': '1015'}, {}, {'boxId': 'box1014', 'boxNu': '9999', 'uniqueBoxId': '4c4c4544-0034-3310-8051-b5c04f335832'}]
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        regUnits = boxRegfps.Box_RegFPs(
            unitNu=0,
        )

        unitsList = regUnits.unitsList()

        return cmndOutcome.set(opResults=unitsList,)


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "box_unitsFind" :comment "" :extent "verify" :ro "" :parsMand "" :parsOpt "" :argsMin 2 :argsMax 2 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<box_unitsFind>>  =verify= argsMin=2 argsMax=2   [[elisp:(org-cycle)][| ]]
#+end_org """
class box_unitsFind(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 2, 'Max': 2,}

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
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  result: boxBaseDir corresponding to uniqueBoxId
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  svcSiteRegBox.cs  -i box_unitsFind boxId box1014
#+end_src
#+RESULTS:
:
: Key Not Found in unit Dictionary: 'boxId'
: [PosixPath('/bxo/iso/pmb_clusterNeda-boxes/boxes/10002'), PosixPath('/bxo/iso/pmb_clusterNeda-boxes/boxes/1014'), PosixPath('/bxo/iso/pmb_clusterNeda-boxes/boxes/9999')]
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        cmndArgsSpecDict = self.cmndArgsSpec()
        parName = self.cmndArgsGet("0", cmndArgsSpecDict, argsList)
        parValue = self.cmndArgsGet("1", cmndArgsSpecDict, argsList)

        regUnits = boxRegfps.Box_RegFPs(
            unitNu=0,
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



####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "box_repoPull" :comment "" :extent "verify" :ro "noCli" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<box_repoPull>>  =verify= ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class box_repoPull(cs.Cmnd):
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
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Runs: echo siteBoxesBase | bx-gitRepos -i gitRemPull
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  svcSiteRegBox.cs -i box_repoPull
#+end_src
#+RESULTS:
:
: ** cmnd= echo /bxo/iso/pmc_clusterNeda-boxs/assign/Pure/Mobile/LinuxU | echo bx-gitRepos -i gitRemPull
: bx-gitRepos -i gitRemPull
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        regUnits = boxRegfps.Box_RegFPs(
            unitNu=0,
        )

        regUnits.repoPull(cmndOutcome)

        return cmndOutcome


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "box_repoPush" :comment "" :extent "verify" :ro "noCli" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<box_repoPush>>  =verify= ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class box_repoPush(cs.Cmnd):
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
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Runs: echo siteBoxesBase | bx-gitRepos -i  addCommitPush all
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  svcSiteRegBox.cs -i box_repoPush
#+end_src
#+RESULTS:
:
: ** cmnd= echo /bxo/iso/pmc_clusterNeda-boxs/assign/Pure/Mobile/LinuxU | echo bx-gitRepos -i addCommitPush all
: bx-gitRepos -i addCommitPush all
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        regUnits = boxRegfps.Box_RegFPs(
            unitNu=0,
        )

        regUnits.repoPush(cmndOutcome)

        return cmndOutcome

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "box_repoLock" :comment "" :extent "verify" :ro "noCli" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<box_repoLock>>  =verify= ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class box_repoLock(cs.Cmnd):
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
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] NOTYET, Lock a write transaction using https://docs.gitlab.com/ee/user/project/file_lock.html
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  svcSiteRegBox.cs -i box_repoLock
#+end_src
#+RESULTS:
:
: OpError.Success
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        regUnits = boxRegfps.Box_RegFPs(
            unitNu=0,
        )

        regUnits.repoLock(cmndOutcome)

        return cmndOutcome


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "box_repoUnlock" :comment "" :extent "verify" :ro "noCli" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<box_repoUnlock>>  =verify= ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class box_repoUnlock(cs.Cmnd):
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
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] NOTYET, Unlock a write transaction using https://docs.gitlab.com/ee/user/project/file_lock.html
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  svcSiteRegBox.cs -i box_repoUnlock
#+end_src
#+RESULTS:
:
: OpError.Success
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        regUnits = boxRegfps.Box_RegFPs(
            unitNu=0,
        )

        regUnits.repoUnlock(cmndOutcome)

        return cmndOutcome


####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "RO Service Commands" :anchor ""  :extraInfo "Command Services Section"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _RO Service Commands_: |]]  Command Services Section  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "ro_box_add" :comment "" :extent "verify" :ro "cli" :parsMand "uniqueBoxId" :parsOpt "boxName " :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<ro_box_add>>  =verify= parsMand=uniqueBoxId parsOpt=boxName  ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class ro_box_add(cs.Cmnd):
    cmndParamsMandatory = [ 'uniqueBoxId', ]
    cmndParamsOptional = [ 'boxName', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             uniqueBoxId: typing.Optional[str]=None,  # Cs Mandatory Param
             boxName: typing.Optional[str]=None,  # Cs Optional Param
    ) -> b.op.Outcome:

        callParamsDict = {'uniqueBoxId': uniqueBoxId, 'boxName': boxName, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        uniqueBoxId = csParam.mappedValue('uniqueBoxId', uniqueBoxId)
        boxName = csParam.mappedValue('boxName', boxName)
####+END:
        if self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  if boxName has not been specified, it become of the form boxXXX
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  svcSiteRegBox.cs --uniqueBoxId=4c4c4544-0034-3310-8051-b5c04f335832 --boxName=box1999 -i ro_box_add
#+end_src
#+RESULTS:
:
: box1999 has already been registered [PosixPath('/bxo/iso/pmc_clusterNeda-boxs/assign/Pure/Mobile/LinuxU/1100')]
: Cmnd -- No Results
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        regUnits = boxRegfps.Box_RegFPs(
            unitNu=0,
        )

        foundList = regUnits.unitsFind(parName='uniqueBoxId', parValue=uniqueBoxId)

        if foundList:
            b_io.ann.note(f"{uniqueBoxId} has already been registered {foundList}")
            return(cmndOutcome)

        nextUnitNu = regUnits.unitsNextNu()

        regfps = boxRegfps.Box_RegFPs(
            unitNu=nextUnitNu,
        )

        if not boxName:
            boxName = f"box{nextUnitNu}"

        regfps.unitCreate(uniqueBoxId, boxName)

        return cmndOutcome.set(opResults=nextUnitNu,)

####+BEGIN: b:py3:cs:framework/endOfFile :basedOn "classification"
""" #+begin_org
* [[elisp:(org-cycle)][| *End-Of-Editable-Text* |]] :: emacs and org variables and control parameters
#+end_org """

#+STARTUP: showall

### local variables:
### no-byte-compile: t
### end:
####+END:
