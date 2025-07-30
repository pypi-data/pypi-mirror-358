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
from bisos.siteRegistrars import invSiteRegContainer

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
    pass

####+BEGIN: b:py3:cs:orgItem/section :title "CSU-Lib Executions" :comment "-- cs.invOutcomeReportControl"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *CSU-Lib Executions* -- cs.invOutcomeReportControl  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

svcName = "svcSiteRegContainer"

# roSiteRegistrarSapPath = cs.ro.SapBase_FPs.svcNameToRoSapPath(svcName)  # static method executes

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

    # def cpsInit(): return collections.OrderedDict()
    # def menuItem(verbosity): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity=verbosity) # 'little' or 'none'

    cmndOutcome = b.op.Outcome()

    od = collections.OrderedDict
    cmnd = cs.examples.cmndEnter

    #unitsPars = collections.OrderedDict([('model', thisModel), ('abode', thisAbode), ('purpose', thisPurpose)])
    #unitBasePars = collections.OrderedDict([('model', thisModel), ('abode', thisAbode), ('purpose', thisPurpose), ('containerNu', thisContainerNu)])
    #createPars = unitBasePars.copy()
    #createPars.update([('boxNu', thisBoxNu)])

    thisSysPars = collections.OrderedDict([('model', 'Host'), ('abode', 'Shield'), ('purpose', 'Server'),])

    #ro_unitsPars = cs.examples.perfNameParsInsert(unitsPars, perfName)
    #ro_unitBasePars = cs.examples.perfNameParsInsert(unitBasePars, perfName)
    #ro_createPars = cs.examples.perfNameParsInsert(createPars, perfName)

    cmnd('cntnrThis_locateBoxInAllCntnrs')
    cmnd('cntnrThis_regName')
    cmnd('cntnrThis_regBpoId')

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "cntnrThis_locateBoxInAllCntnrs" :comment "" :extent "verify" :ro "noCli" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<cntnrThis_locateBoxInAllCntnrs>>  =verify= ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class cntnrThis_locateBoxInAllCntnrs(cs.Cmnd):
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

        if (containers := invSiteRegContainer.thisSys_locateBoxInAll().pyWCmnd(cmndOutcome,).results) == None: return failed(cmndOutcome)

        return cmndOutcome.set(opResults=f"{containers}",)

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "cntnrThis_regName" :comment "" :extent "verify" :ro "noCli" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<cntnrThis_regName>>  =verify= ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class cntnrThis_regName(cs.Cmnd):
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

        if (containers := invSiteRegContainer.thisSys_locateBoxInAll().pyWCmnd(cmndOutcome,)
            .results) == None: return failed(cmndOutcome)
        
        if len(containers) == 1:
            cntnrName = cntnrCharName.ContainerCharName(ccnDict=containers[0])
            name = cntnrName.initialsName()
        elif len(containers) == 0:
            name = ""
        else:
            # b_io.eh_problem("More than onecontainer")
            name = "MultipleContainersMatchedForName"

        return cmndOutcome.set(opResults=name,)

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "cntnrThis_regBpoId" :comment "" :extent "verify" :ro "noCli" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<cntnrThis_regBpoId>>  =verify= ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class cntnrThis_regBpoId(cs.Cmnd):
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
  cntnrCharBox.cs  -i charBox_bpoId
#+end_src
#+RESULTS:
:
: bash: cntnrCharBox.cs: command not found
        #+end_org """)
        if self.justCaptureP(): return cmndOutcome

        if (containers := invSiteRegContainer.thisSys_locateBoxInAll().pyWCmnd(cmndOutcome,)
            .results) == None: return failed(cmndOutcome)

        if len(containers) == 1:
            cntnrName = cntnrCharName.ContainerCharName(ccnDict=containers[0])
            bpoId = cntnrName.bpoId()
        elif len(containers) == 0:
            bpoId = ""
        else:
            # b_io.eh_problem("More than onecontainer")
            bpoId = "MultipleContainersMatchedForBpoId"

        return cmndOutcome.set(opResults=bpoId,)


####+BEGIN: b:py3:cs:framework/endOfFile :basedOn "classification"
""" #+begin_org
* [[elisp:(org-cycle)][| *End-Of-Editable-Text* |]] :: emacs and org variables and control parameters
#+end_org """

#+STARTUP: showall

### local variables:
### no-byte-compile: t
### end:
####+END:
