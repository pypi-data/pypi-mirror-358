# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: A =CS-Lib= for Managing MARMEE AAS (Abstracted Accessible Service) Control File Parameters
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
* *[[elisp:(org-cycle)][| Proclamations |]]* :: Libre-Halaal Software --- Part Of Blee ---  Poly-COMEEGA Format.
** This is Libre-Halaal Software. © Libre-Halaal Foundation. Subject to AGPL.
** It is not part of Emacs. It is part of Blee.
** Best read and edited  with Poly-COMEEGA (Polymode Colaborative Org-Mode Enhance Emacs Generalized Authorship)
#+end_org """
####+END:

####+BEGIN: b:prog:file/particulars :authors ("./inserts/authors-mb.org")
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars |]]* :: Authors, version
** This File: NOTYET
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:python:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['ro'], }
csInfo['version'] = '202209130210'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'ro-Panel.org'
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

from bisos.bpo import bpo
from bisos.bpo import bpoFpsCls
from bisos.bpo import bpoFps_csu
# from bisos.common import csParam

import pathlib
import os
# import abc

####+BEGIN: bx:cs:py3:section :title "Service Specification"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Service Specification*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "CSU" :anchor ""  :extraInfo "Command Services Section"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _CSU_: |]]  Command Services Section  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:


####+BEGIN: b:py3:cs:func/args :funcName "commonParamsSpecify" :comment "" :funcType "FmWrk" :retType "Void" :deco "" :argsList "csParams"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-A-FmWrk  [[elisp:(outline-show-subtree+toggle)][||]] /commonParamsSpecify/ deco=  [[elisp:(org-cycle)][| ]]  [[elisp:(org-cycle)][| ]]
#+end_org """
def commonParamsSpecify(
    csParams: cs.CmndParamDict,
):
####+END:
    """
** Invoked class's static method.
    """

    site_RegistrarsBoxPerf_FPs.fps_asCsParamsAdd(csParams,)


####+BEGIN: bx:dblock:python:class :className "site_RegistrarsBoxPerf_FPs" :superClass "bpoFpsCls.BpoFpsCls" :comment "" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /site_RegistrarsBoxPerf_FPs/ bpoFpsCls.BpoFpsCls  [[elisp:(org-cycle)][| ]]
#+end_org """
class site_RegistrarsBoxPerf_FPs(bpoFpsCls.BpoFpsCls):
####+END:
    """
** Abstraction of the PalsBase for LiveTargets
"""
####+BEGIN: b:py3:cs:method/typing :methodName "__init__" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /__init__/ deco=default  deco=default   [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def __init__(
####+END:
            self,
            bpoId: str = "",
            bpoFpsRelPath: os.PathLike = pathlib.Path("registrars/box/perf.fps",),
            fpBase: os.PathLike = pathlib.Path("_null_",),
    ):
        """ #+begin_org
** fpBase is used with getattr of bpoFpsRelPath is a specific repo -- site_registrarsBoxPerf_fps
        #+end_org """

        if fpBase != pathlib.Path("_null_"):
            super().__init__(fpBase=str(fpBase))
        else:
            super().__init__(bpoId=bpoId, bpoFpsRelPath=bpoFpsRelPath)



####+BEGIN: b:py3:cs:method/typing :methodName "fps_asCsParamsAdd" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /fps_asCsParamsAdd/ deco=staticmethod  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def fps_asCsParamsAdd(
####+END:
            csParams: cs.CmndParamDict,
    ) -> cs.CmndParamDict:
        """Conrete - staticmethod: takes in csParms and augments it with fileParams. returns csParams."""
        # return csParams
        csParams.parDictAdd(
            parName='site_registrarsBoxPerf_regBoxesBpoId',
            parDescription="",
            fileParName="regBoxesBpoId",
            fileParInit="unSetBpoId",
            argparseLongOpt='--site_registrarsBoxPerf_regBoxesBpoId',
        )
        return csParams

####+BEGIN: b:py3:cs:method/typing :methodName "fps_manifestDict" :deco ""
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /fps_manifestDict/ deco=    [[elisp:(org-cycle)][| ]]
    #+end_org """
    def fps_manifestDictBuild(
####+END:
            self,
    ):
        """ ConcreteMethod based on abstract pattern
        """
        self._cmndParPrefix = "site_registrarsBoxPerf_"
        csParams = cs.G.icmParamDictGet()
        self._manifestDict = {}
        paramsList = []
        for cmndParam in csParams.parDictGet():
            if self._cmndParPrefix in cmndParam:
                paramsList.append(cmndParam)
        for eachParam in paramsList:
            thisCsParam = csParams.parNameFind(eachParam)   # type: ignore
            fileParName = self.cmndParNameToFileParName(eachParam, thisCsParam)
            thisFpCmndParam = b.fpCls.FpCmndParam(
                cmndParam=thisCsParam,
                fileParam=b.fp.FileParam(
                    parName=fileParName,
                    storeBase=self.basePath_obtain(),
                )
            )
            self._manifestDict[eachParam] = thisFpCmndParam

        return self._manifestDict


####+BEGIN: b:py3:cs:func/typing :funcName "examples_csu" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /examples_csu/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def examples_csu(
####+END:
        csName: str='',
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Basic example command.
    #+end_org """

    #od = collections.OrderedDict
    cmnd = cs.examples.cmndEnter
    # literal = cs.examples.execInsert

    if csName == '':
        cs.examples.menuChapter('=Get and  Set Parameters=')

    siteBpoId = bpo.forPathObtainBpoId().pyCmnd(argsList=["/bisos/site"]).results
    bpoFps = site_RegistrarsBoxPerf_FPs(bpoId=str(siteBpoId))
    fpBase  = bpoFps.basePath_obtain()
    fileParsDict = b.fp_csu.fpBaseParsGetAsDictValue().pyCmnd(fpBase=fpBase).results
    argChoices = fileParsDict.keys()

    for thisArg in argChoices:
        cmnd('parGet', csName=csName, args=thisArg, comment=" # PRIMARY -- Read Value of FileParam")
        curVal = parGet().pyCmnd(argsList=[thisArg]).results
        cmnd('parSet', csName=csName, args=f"{thisArg} {curVal}", comment=" # PRIMARY -- Write Value of FileParam -- Edit Current Value")

    if csName:
        cmnd('bpoFpsFullReport', csName=csName, comment=" # Produce a full report")

####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "CmndSvc" :anchor ""  :extraInfo "Command Services Section"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _Invoker Only CmndSvc_: |]]  Command Services Section  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "bpoFpsFullReport" :comment "" :extent "verify" :ro "noCli" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<bpoFpsFullReport>>  =verify= ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class bpoFpsFullReport(cs.Cmnd):
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
        if self.cmndDocStr(""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Given one fileParamName, get its value
        #+end_org """): return(cmndOutcome)

        siteBpoId = bpo.forPathObtainBpoId().pyCmnd(argsList=["/bisos/site"]).results

        bpoFps_csu.bpoFpsClsFullReport().pyCmnd(
            rtInv=rtInv,
            bpoId=siteBpoId,
            cls="site_RegistrarsBoxPerf_FPs"
        )

        return cmndOutcome


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "parGet" :comment "" :extent "verify" :ro "noCli" :parsMand "" :parsOpt "" :argsMin 1 :argsMax 1 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<parGet>>  =verify= argsMin=1 argsMax=1 ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class parGet(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 1,}
    rtInvConstraints = cs.rtInvoker.RtInvoker.new_noRo() # NO RO From CLI

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             argsList: list[str]=[],  # CsArgs
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
####+END:
        if self.cmndDocStr(""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Given one fileParamName, get its value
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  platfSiteBootstrap-fps.cs  -i parGet acct
#+end_src
#+RESULTS:
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        siteBpoId = bpo.forPathObtainBpoId().pyCmnd(argsList=["/bisos/site"]).results
        bpoFps = site_RegistrarsBoxPerf_FPs(bpoId=str(siteBpoId))

        fileParamName = self.cmndArgsGet("0", cmndArgsSpecDict, argsList)

        fileCmndParamName = f"{bpoFps._cmndParPrefix}{fileParamName}"

        parValue = bpoFps.fps_getParam(fileCmndParamName)

        return cmndOutcome.set(opResults=parValue.parValueGet(),)

####+BEGIN: b:py3:cs:method/typing :methodName "cmndArgsSpec" :methodType "ArgsSpec" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-ArgsSpec [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(
####+END:
            self,
) -> cs.arg.CmndArgsSpecDict:
        """ #+begin_org
*** [[elisp:(org-cycle)][| *cmndArgsSpec:* |]] Command Argument Specifications. argChoices derived from bpoFpsCls.
        #+end_org """

        siteBpoId = bpo.forPathObtainBpoId().pyCmnd(argsList=["/bisos/site"]).results
        bpoFps = site_RegistrarsBoxPerf_FPs(bpoId=str(siteBpoId))
        fpBase  = bpoFps.basePath_obtain()
        fileParsDict = b.fp_csu.fpBaseParsGetAsDictValue().pyCmnd(fpBase=fpBase).results
        argChoices = fileParsDict.keys()

        cmndArgsSpecDict = cs.arg.CmndArgsSpecDict()
        cmndArgsSpecDict.argsDictAdd(
            argPosition="0",
            argName="fileParamName",
            argChoices=argChoices,
            argDescription="fileParamName not fileCmndParamName"
        )
        return cmndArgsSpecDict

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "parSet" :comment "" :extent "verify" :ro "noCli" :parsMand "" :parsOpt "" :argsMin 2 :argsMax 2 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<parSet>>  =verify= argsMin=2 argsMax=2 ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class parSet(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 2, 'Max': 2,}
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
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Given one fileParamName, get its value
        #+end_org """): return(cmndOutcome)

        self.captureRunStr(""" #+begin_org
#+begin_src sh :results output :session shared
  platfSiteBootstrap-fps.cs  -i parGet acct
#+end_src
#+RESULTS:
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        siteBpoId = bpo.forPathObtainBpoId().pyCmnd(argsList=["/bisos/site"]).results
        bpoFps = site_RegistrarsBoxPerf_FPs(bpoId=str(siteBpoId))

        fileParamName = self.cmndArgsGet("0", cmndArgsSpecDict, argsList)
        fileParamValue = self.cmndArgsGet("1", cmndArgsSpecDict, argsList)

        # fileCmndParamName = f"{bpoFps._cmndParPrefix}{fileParamName}"

        parValue = bpoFps.fps_setParam(fileParamName, fileParamValue)

        return cmndOutcome.set(opResults=fileParamValue,)

####+BEGIN: b:py3:cs:method/typing :methodName "cmndArgsSpec" :methodType "ArgsSpec" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-ArgsSpec [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(
####+END:
            self,
) -> cs.arg.CmndArgsSpecDict:
        """ #+begin_org
*** [[elisp:(org-cycle)][| *cmndArgsSpec:* |]] Command Argument Specifications. argChoices derived from bpoFpsCls.
        #+end_org """

        siteBpoId = bpo.forPathObtainBpoId().pyCmnd(argsList=["/bisos/site"]).results
        bpoFps = site_RegistrarsBoxPerf_FPs(bpoId=str(siteBpoId))
        fpBase  = bpoFps.basePath_obtain()
        fileParsDict = b.fp_csu.fpBaseParsGetAsDictValue().pyCmnd(fpBase=fpBase).results
        argChoices = fileParsDict.keys()

        cmndArgsSpecDict = cs.arg.CmndArgsSpecDict()
        cmndArgsSpecDict.argsDictAdd(
            argPosition="0",
            argName="fileParamName",
            argChoices=argChoices,
            argDescription="fileParamName not fileCmndParamName"
        )
        cmndArgsSpecDict.argsDictAdd(
            argPosition="1",
            argName="fileParamValue",
            argDescription="fileParamValue used in bpoFps.fps_getParam"
        )

        return cmndArgsSpecDict


####+BEGIN: b:py3:cs:framework/endOfFile :basedOn "classification"
""" #+begin_org
* *[[elisp:(org-cycle)][| ~End-Of-Editable-Text~ |]]* :: emacs and org variables and control parameters
#+end_org """

#+STARTUP: showall

### local variables:
### no-byte-compile: t
### end:
####+END:
