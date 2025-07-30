# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: A =CS-Lib= for Managing RO (Remote Operation) Control File Parameters as a ClsFp
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
** This File: /bisos/git/bxRepos/bisos-pip/siteRegistrars/py3/bisos/siteRegistrars/perfSiteRegContainerConf.py
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:python:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['perfSiteRegContainerConf'], }
csInfo['version'] = '202401295255'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'perfSiteRegContainerConf-Panel.org'
csInfo['groupingType'] = 'IcmGroupingType-pkged'
csInfo['cmndParts'] = 'IcmCmndParts[common] IcmCmndParts[param]'
####+END:

""" #+begin_org
* [[elisp:(org-cycle)][| ~Description~ |]] :: [[file:/bisos/git/auth/bxRepos/blee-binders/bisos-core/PyFwrk/bisos-pip/bisos.cs/_nodeBase_/fullUsagePanel-en.org][PyFwrk bisos.b.cs Panel For RO]] ||
Module description comes here.
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

import pathlib
import __main__
import os
# import abc

# from bisos.usgAcct import usgAcct
from bisos.platform import platformBases

####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "CSU" :anchor ""  :extraInfo "Command Services Section"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _CSU_: |]]  Command Services Section  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:


####+BEGIN: b:py3:cs:func/typing :funcName "examples_csu" :funcType "eType" :retType "" :deco "default" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-eType  [[elisp:(outline-show-subtree+toggle)][||]] /examples_csu/  deco=default  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def examples_csu(
####+END:
        sectionTitle: typing.AnyStr = '',
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Examples of Service Access Instance Commands.
    #+end_org """

    def cpsInit(): return collections.OrderedDict()
    def menuItem(verbosity): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity=verbosity) # 'little' or 'none'

    if sectionTitle == 'default':
        cs.examples.menuChapter('*Performer Site Registrar Container Configuration*')

    icmWrapper = ""
    cmndName = "perfSiteRegContainerConf_set"
    cps = cpsInit() ; cps['regContainersBpoId'] = 'pmc_clusterNeda-containers'
    cmndArgs = "" ;

    cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='none', icmWrapper=icmWrapper)

    #cmndName = "pyCmndInvOf_parsArgsStdinCmndResult" ; cps = cpsInit() ; cmndArgs = "" ;
    #menuItem(verbosity='none')

    cs.examples.menuChapter('FileParams Access And Management*')

    icmWrapper = ""
    cmndName = "perfSiteRegContainerConf_fps"
    cps = cpsInit()
    cmndArgs = "list" ;
    cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='none', icmWrapper=icmWrapper)

    icmWrapper = ""
    cmndName = "perfSiteRegContainerConf_fps"
    cps = cpsInit()
    cmndArgs = "menu" ;
    cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='none', icmWrapper=icmWrapper)

####+BEGIN: b:py3:cs:func/args :funcName "commonParamsSpecify" :comment "Params Spec for: --aipxBase --aipxRoot" :funcType "FmWrk" :retType "Void" :deco "" :argsList "icmParams"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-A-FmWrk  [[elisp:(outline-show-subtree+toggle)][||]] /commonParamsSpecify/ deco=  [[elisp:(org-cycle)][| ]] =Params Spec for: --aipxBase --aipxRoot=  [[elisp:(org-cycle)][| ]]
#+end_org """
def commonParamsSpecify(
    icmParams,
):
####+END:
    """
** --regContainersBpoId
    """

    RegContainerPerfConf_FPs.fps_asCsParamsAdd(icmParams,)


####+BEGIN: bx:dblock:python:class :className "RegContainerPerfConf_FPs" :superClass "b.fpCls.BaseDir" :comment "" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /RegContainerPerfConf_FPs/ b.fpCls.BaseDir  [[elisp:(org-cycle)][| ]]
#+end_org """
class RegContainerPerfConf_FPs(b.fpCls.BaseDir):
####+END:
    """
** Abstraction of the
"""
####+BEGIN: b:py3:cs:method/typing :methodName "__init__" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /__init__/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def __init__(
####+END:
            self,
            fpBase: str="",
    ):
        self.fpBase = fpBase

        if fpBase:
            self.fpBase = fpBase
            fileSysPath = fpBase
        else:
            fileSysPath = self.basePath_obtain()

        super().__init__(fileSysPath,)


####+BEGIN: b:py3:cs:method/typing :methodName "fps_asCsParamsAdd" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /fps_asCsParamsAdd/  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def fps_asCsParamsAdd(
####+END:
            icmParams,
    ):
        """staticmethod: takes in icmParms and augments it with fileParams. returns icmParams."""
        icmParams.parDictAdd(
            parName='regContainersBpoId',
            parDescription="",
            parDataType=None,
            parDefault=None,
            parChoices=list(),
            #parScope=icm.ICM_ParamScope.TargetParam,  # type: ignore
            argparseShortOpt=None,
            argparseLongOpt='--regContainersBpoId',
        )

        return icmParams

####+BEGIN: b:py3:cs:method/typing :methodName "fps_manifestDictBuild" :deco ""
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /fps_manifestDictBuild/   [[elisp:(org-cycle)][| ]]
    #+end_org """
    def fps_manifestDictBuild(
####+END:
            self,
    ):
        """ ConcreteMethod based on abstract pattern
        """
        csParams = cs.G.icmParamDictGet()
        self._manifestDict = {}
        paramsList = [
                'regContainersBpoId',
        ]
        for eachParam in paramsList:
            thisCsParam = csParams.parNameFind(eachParam)   # type: ignore
            thisFpCmndParam = b.fpCls.FpCmndParam(
                cmndParam=thisCsParam,
                fileParam=None,
            )
            self._manifestDict[eachParam] = thisFpCmndParam

        return self._manifestDict

####+BEGIN: b:py3:cs:method/typing :methodName "fps_absBasePath" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /fps_absBasePath/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def fps_absBasePath(
####+END:
           self,
    ):
        return typing.cast(str, self.basePath_obtain())

####+BEGIN: b:py3:cs:method/typing :methodName "basePath_obtain" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /basePath_obtain/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def basePath_obtain(
####+END:
           self,
    ) -> pathlib.Path:

        # fpsBase = usgAcct.UsgAcctBposNamed.read('sites/selected').joinpath('registrars/container/perf.fps')

        siteBase = platformBases.siteBasePath()
        # /bisos/site/registrars/container/perf.fps
        fpsBase = siteBase.joinpath('registrars/container/perf.fps')

        assert fpsBase.exists()
        return fpsBase

####+BEGIN: b:py3:cs:method/typing :methodName "basePath_update" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /basePath_update/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def basePath_update(
####+END:
           self,
    ) -> pathlib.Path:
        basePath = self.basePath_obtain()
        basePath.mkdir(parents=True, exist_ok=True)
        return basePath


####+BEGIN: b:py3:cs:method/typing :methodName "fps_baseMake" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /fps_baseMake/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def fps_baseMake(
####+END:
            self,
    ):
        #palsControlPath = self.basePath_obtain()
        #fpsPath = self.basePath_obtain()
        #self.fpsBaseInst = repoLiveParams.PalsRepo_LiveParams_FPs(
        #    fpsPath,
        #)
        #return self.fpsBaseInst
        pass


####+BEGIN: bx:cs:py3:section :title "CS ro_sap Cmnds"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *CS ro_sap Cmnds*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "perfSiteRegContainerConf_set" :ro "noCli" :noMapping "t" :comment "" :parsMand "regContainersBpoId" :parsOpt "" :argsMin 0 :argsMax 0
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<perfSiteRegContainerConf_set>>  =verify= parsMand=regContainersBpoId ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class perfSiteRegContainerConf_set(cs.Cmnd):
    cmndParamsMandatory = [ 'regContainersBpoId', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}
    rtInvConstraints = cs.rtInvoker.RtInvoker.new_noRo() # NO RO From CLI

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             regContainersBpoId: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'regContainersBpoId': regContainersBpoId, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
####+END:
        """\
***** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Creates path for ro_sap and updates FPs
        """

        confFps = b.pattern.sameInstance(RegContainerPerfConf_FPs,)

        confFps.fps_setParam('regContainersBpoId', regContainersBpoId)

        return(cmndOutcome)

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "perfSiteRegContainerConf_fps" :comment ""  :extent "noVerify" :ro "noCli" :parsMand "" :parsOpt "" :argsMin 1 :argsMax 9999 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<perfSiteRegContainerConf_fps>>  =noVerify= argsMin=1 argsMax=9999 ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class perfSiteRegContainerConf_fps(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 9999,}
    rtInvConstraints = cs.rtInvoker.RtInvoker.new_noRo() # NO RO From CLI

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  A starting point command.
        #+end_org """)

        cmndArgsSpecDict = self.cmndArgsSpec()

        action = self.cmndArgsGet("0", cmndArgsSpecDict, argsList)
        actionArgs = self.cmndArgsGet("1&9999", cmndArgsSpecDict, argsList)

        confFps = b.pattern.sameInstance(RegContainerPerfConf_FPs,)

        if action == "list":
            # print(f"With fpBase={roSapPath} and cls={RegContainerPerfConf_FPs} name={sapBaseFps.__class__.__name__}.")
            if b.fpCls.fpParamsReveal(cmndOutcome=cmndOutcome).cmnd(
                    rtInv=rtInv,
                    cmndOutcome=cmndOutcome,
                    fpBase="",
                    cls=confFps.__class__.__name__,
                    argsList=['getExamples'],
            ).isProblematic(): return(b_io.EH_badOutcome(cmndOutcome))

        elif action == "menu":
            print(f"With fpBase={roSapPath} and cls={RegContainerPerfConf_FPs} NOTYET.")
        else:
            print(f"bad input {action}")

        return(cmndOutcome)

####+BEGIN: b:py3:cs:method/args :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
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
            argName="action",
            argChoices=['list', 'menu',],
            argDescription="Action to be specified by rest"
        )
        cmndArgsSpecDict.argsDictAdd(
            argPosition="1&9999",
            argName="actionArgs",
            argChoices=[],
            argDescription="Rest of args for use by action"
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
