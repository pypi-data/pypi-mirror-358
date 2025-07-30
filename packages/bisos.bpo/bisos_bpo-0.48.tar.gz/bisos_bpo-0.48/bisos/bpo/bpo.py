# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: A =CS-Lib= for creating and managing symetric gpg  encryption/decryption.
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
** This File: /bisos/git/auth/bxRepos/bisos-pip/bpo/py3/bisos/bpo/bpo.py
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:python:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['bpo'], }
csInfo['version'] = '202210010431'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'bpo-Panel.org'
csInfo['groupingType'] = 'IcmGroupingType-pkged'
csInfo['cmndParts'] = 'IcmCmndParts[common] IcmCmndParts[param]'
####+END:

""" #+begin_org
* /[[elisp:(org-cycle)][| Description |]]/ :: [[file:/bisos/git/auth/bxRepos/blee-binders/bisos-core/PyFwrk/bisos.crypt/_nodeBase_/fullUsagePanel-en.org][PyFwrk bisos.crypt Panel]]
Module description comes here.
** Relevant Panels:
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

import os
import enum

from bisos.basics import pattern

from bisos.bpo import bpoRepo

####+BEGIN: bx:dblock:python:section :title "Enumerations"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Enumerations*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:

####+BEGIN: bx:dblock:python:enum :enumName "bpoId_Type" :comment ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Enum       [[elisp:(outline-show-subtree+toggle)][||]] /bpoId_Type/  [[elisp:(org-cycle)][| ]]
#+end_org """
@enum.unique
class bpoId_Type(enum.Enum):
####+END:
    path = 'path'   # FoeignBpo
    homeDir = 'homeDir'
    acctId = 'acctId'
    genericName = 'genericName'  # ByN
    objId = 'objId'
    relObjId = 'relObjId'

####+BEGIN: bx:dblock:python:enum :enumName "bpo_Type" :comment ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Enum       [[elisp:(outline-show-subtree+toggle)][||]] /bpo_Type/  [[elisp:(org-cycle)][| ]]
#+end_org """
@enum.unique
class bpo_Type(enum.Enum):
####+END:
    project = 'project'
    pals = 'pals'

####+BEGIN: bx:dblock:python:enum :enumName "bpo_Purpose" :comment ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Enum       [[elisp:(outline-show-subtree+toggle)][||]] /bpo_Purpose/  [[elisp:(org-cycle)][| ]]
#+end_org """
@enum.unique
class bpo_Purpose(enum.Enum):
####+END:
    info = 'info'
    materialize = 'materialize'



####+BEGIN: bx:dblock:python:func :funcName "bpoId_Type_obtain" :funcType "Obtain" :retType "str" :deco "" :argsList "bpoId"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-Obtain   [[elisp:(outline-show-subtree+toggle)][||]] /bpoId_Type_obtain/ retType=str argsList=(bpoId)  [[elisp:(org-cycle)][| ]]
#+end_org """
def bpoId_Type_obtain(
    bpoId,
):
####+END:
    """
** NOT yet -- ea-NUM means old ByStarUid, A pure number means nativeSO. nonNumber means foreignBxO
"""
    # icm.unusedSuppress(bpoId)
    return bpoId_Type.acctId


####+BEGIN: b:py3:cs:func/typing :funcName "bpoBaseDir_obtain" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /bpoBaseDir_obtain/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def bpoBaseDir_obtain(
####+END:
        bpoId: str,
) -> str:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    bpoBaseDir = ""
    idType = bpoId_Type_obtain(bpoId)

    if idType == bpoId_Type.path:
        bpoBaseDir = bpoId
    elif idType == bpoId_Type.homeDir:
        bpoBaseDir = bpoId
    elif idType == bpoId_Type.acctId:
        bpoBaseDir = os.path.expanduser(f"~{bpoId}")
        if bpoBaseDir == format(f"~{bpoId}"):
            b_io.eh.problem_usageError(f"bpoId={bpoId} is not a valid account")
            bpoBaseDir = ""
    else:
        b_io.eh.problem_usageError("")

    return bpoBaseDir


####+BEGIN: b:py3:cs:func/typing :funcName "idEffective" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /idEffective/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def idEffective(
####+END:
        bpoId: str,
) -> str:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    effectiveId = ""
    if bpoId == "cur":
        b_io.eh.problem_usageError("NOTYET")
    else:
        effectiveId = bpoId
    return effectiveId


####+BEGIN: bx:dblock:python:subSection :title "Class Definitions"

####+END:

####+BEGIN: b:py3:class/decl :className "EffectiveBpos" :superClass "object" :comment "" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /EffectiveBpos/  superClass=object  [[elisp:(org-cycle)][| ]]
#+end_org """
class EffectiveBpos(object):
####+END:
    """
** Only one instance is created for a given BpoId.
"""
    effectiveBposList = {}

    @staticmethod
    def addBpo(
            bpoId,
            bpo,
    ):
        # print(f"ccc Adding bpoId={bpoId} bpo={bpo}")
        __class__.effectiveBposList.update({bpoId: bpo})
        return None

    @staticmethod
    def givenBpoIdObtainBpo(
            bpoId,
            BpoClass,
    ):
        if bpoId in __class__.effectiveBposList:
            return __class__.effectiveBposList[bpoId]
        else:
            # return BpoClass(bpoId)
            return pattern.sameInstance(BpoClass, bpoId)  # In the __init__ of BpoClass there should be a addBpo

    @staticmethod
    def givenBpoIdGetBpo(
            bpoId,
    ):
        """Should be renamed to givenBpoIdFindBpo"""
        # print(f"aaa bpoId={bpoId}")
        if bpoId in __class__.effectiveBposList:
            return __class__.effectiveBposList[bpoId]
        else:
            # b_io.eh.problem_usageError("")
            return None

    @staticmethod
    def givenBpoIdGetBpoOrNone(
            bpoId,
    ):
        # print(f"bbb bpoId={bpoId}")
        if bpoId in __class__.effectiveBposList:
            return __class__.effectiveBposList[bpoId]
        else:
            return None

####+BEGIN: b:py3:cs:func/typing :funcName "givenPathObtainBpoId" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /givenPathObtainBpoId/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def givenPathObtainBpoId(
####+END:
        inPath: str,
) -> str:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    bpoId = ""

    subjectPath = os.path.realpath(inPath)
    pathComps = subjectPath.split('/')
    if pathComps[1] == "bxo" and pathComps[2] == "r3" and pathComps[3] == "iso":
        bpoId = pathComps[4]
    return bpoId



####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "obtainBpoIdFromFps" :comment "" :extent "verify" :ro "cli" :parsMand "" :parsOpt "" :argsMin 1 :argsMax 1 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<obtainBpoIdFromFps>>  =verify= argsMin=1 argsMax=1 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class obtainBpoIdFromFps(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 1,}

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
        if self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  argsList[0] should be base of a bpo. Then use rbxe/bxeDesc to construct bpoId
        #+end_org """): return(cmndOutcome)

        if argsList is None:
            return failed(cmndOutcome)
        inPath = argsList[0]

        try:
            fileParam = b.fp.FileParamReadFromPath(f"{inPath}/rbxe/bxeDesc/bxePrefix")
        except IOError:
            cmndOutcome.set(opError="IOError", opErrInfo=f"Missing parRoot={parRoot} parName={parName}")
            return failed(cmndOutcome)
        bxePrefix = fileParam.parValueGet()

        try:
            fileParam = b.fp.FileParamReadFromPath(f"{inPath}/rbxe/bxeDesc/name/")
        except IOError:
            cmndOutcome.set(opError="IOError", opErrInfo=f"Missing parRoot={parRoot} parName={parName}")
            return failed(cmndOutcome)
        name = fileParam.parValueGet()

        siteBpoId = f"{bxePrefix}_{name}"

        return cmndOutcome.set(
            opResults=siteBpoId,
        )



####+BEGIN: b:py3:cs:func/typing :funcName "givenPathObtainRelPath" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /givenPathObtainRelPath/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def givenPathObtainRelPath(
####+END:
        inPath: str,
) -> str:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """

    retVal = ""

    subjectPath = os.path.realpath(inPath)
    pathComps = subjectPath.split('/')
    if pathComps[1] == "bxo" and pathComps[2] == "r3" and pathComps[3] == "iso":
        bpoId = pathComps[4]
    else:
        b_io.eh.problem_usageError("")
        return retVal

    pathComps.pop(0)  # /
    pathComps.pop(0)
    pathComps.pop(0)
    pathComps.pop(0)
    pathComps.pop(0)

    retVal = '/'.join(pathComps)

    return retVal



####+BEGIN: bx:cs:python:func :funcName "obtainBpo" :funcType "anyOrNone" :retType "bool" :deco "" :argsList "bpoId"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /obtainBpo/ retType=bool argsList=(bpoId)  [[elisp:(org-cycle)][| ]]
#+end_org """
def obtainBpo(
    bpoId,
):
####+END:
    return EffectiveBpos.givenBpoIdObtainBpo(bpoId, Bpo)


####+BEGIN: b:py3:class/decl :className "Bpo" :superClass "object" :comment "ByStar Portable Object -- to be subclassed" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /Bpo/  superClass=object =ByStar Portable Object -- to be subclassed=  [[elisp:(org-cycle)][| ]]
#+end_org """
class Bpo(object):
####+END:
    """
** Abstraction of the base ByStar Portable Object
"""
    def __init__(
            self,
            bpoId,
    ):
        '''Constructor'''

        self.baseDir = bpoBaseDir_obtain(bpoId)
        if not self.baseDir:
            b_io.eh.problem_usageError(f"Missing baseDir for bpoId={bpoId}")
            return

        EffectiveBpos.addBpo(bpoId, self)

        self.bpoId = bpoId
        self.bpoName = bpoId
        self.bpoBaseDir = bpoBaseDir_obtain(bpoId)

        self.repo_rbxe = bpoRepo.BpoRepo_Rbxe(bpoId)
        self.repo_bxeTree = bpoRepo.BpoRepo_BxeTree(bpoId)



####+BEGIN: b:py3:class/decl :className "BpoBases" :superClass "object" :comment "A BPO Repository -- to be subclassed" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /BpoBases/  superClass=object =A BPO Repository -- to be subclassed=  [[elisp:(org-cycle)][| ]]
#+end_org """
class BpoBases(object):
####+END:
    """
** Abstraction of the base ByStar Portable Object
"""

    def __init__(
            self,
            bpoId,
    ):
        self.bpo = EffectiveBpos.givenBpoIdGetBpo(bpoId)
        if not self.bpo:
            b_io.eh.critical_usageError(f"Missing BPO for {bpoId}")
            return

        self.bpoId = self.bpo.bpoId
        self.bpoName = self.bpo.bpoName
        self.bpoBaseDir = self.bpo.baseDir

        # print(self.bpo)
        # print(self.bpo.__dict__)

    def bases_update(self,):
        self.varBase_update()
        self.tmpBase_update()
        return

    def varBase_update(self,):
        return "NOTYET"

    def varBase_obtain(self,):
        return os.path.join(self.bpo.baseDir, "var") # type: ignore

    def tmpBase_update(self,):
        return "NOTYET"

    def tmpBase_obtain(self,):
        return os.path.join(self.bpo.baseDir, "tmp") # type: ignore



####+BEGIN: b:py3:class/decl  :className "BpoRepo" :superClass "object" :comment "A BPO Repository -- to be subclassed" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /BpoRepo/  superClass=object =A BPO Repository -- to be subclassed=  [[elisp:(org-cycle)][| ]]
#+end_org """
class BpoRepo(object):
####+END:
    """
** Abstraction of the base ByStar Portable Object
"""

    def __init__(
            self,
            bpoId,
    ):
        self.bpo = EffectiveBpos.givenBpoIdGetBpo(bpoId)
        if not self.bpo:
            # icm.EH_critical_usageError(f"Missing BPO for {bpoId}")
            return



####+BEGIN: b:py3:class/decl  :className "BpoRepo_Rbxe" :superClass "object" :comment "A BPO Repository -- to be subclassed" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /BpoRepo_Rbxe/  superClass=object =A BPO Repository -- to be subclassed=  [[elisp:(org-cycle)][| ]]
#+end_org """
class BpoRepo_Rbxe(object):
####+END:
    """
** Abstraction of the base ByStar Portable Object
"""
    def __init__(
            self,
            bpoId,
    ):
        super().__init__(bpoId)
        if not EffectiveBpos.givenBpoIdGetBpo(bpoId):
            # icm.EH_critical_usageError(f"Missing BPO for {bpoId}")
            return

    def info(self,):
        print(f"rbxeInfo bpoId={self.bpo.bpoId}") # type: ignore


####+BEGIN: b:py3:class/decl  :className "BpoRepo_BxeTree" :superClass "object" :comment "A BPO Repository -- to be subclassed" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /BpoRepo_BxeTree/  superClass=object =A BPO Repository -- to be subclassed=  [[elisp:(org-cycle)][| ]]
#+end_org """
class BpoRepo_BxeTree(object):
####+END:
    """
** Abstraction of the base ByStar Portable Object
"""
    def __init__(
            self,
            bpoId,
    ):
        super().__init__(bpoId)
        if not EffectiveBpos.givenBpoIdGetBpo(bpoId):
            # icm.EH_critical_usageError(f"Missing BPO for {bpoId}")
            return

    def info(self,):
        print("bxeTreeInfo")



####+BEGIN: bx:cs:py3:section :title "Common Parameters Specification"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Common Parameters Specification*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: bx:dblock:python:func :funcName "commonParamsSpecify" :funcType "ParSpec" :retType "" :deco "" :argsList "csParams"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-ParSpec  [[elisp:(outline-show-subtree+toggle)][||]] /commonParamsSpecify/ retType= argsList=(csParams)  [[elisp:(org-cycle)][| ]]
#+end_org """
def commonParamsSpecify(
    csParams,
):
####+END:
    csParams.parDictAdd(
        parName='bpoId',
        parDescription="Bx Portable ObjectId",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        # parScope=icm.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--bpoId',
    )
    csParams.parDictAdd(
        parName='envRelPath',
        parDescription="Environment Relative Path",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        # parScope=icm.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--envRelPath',
    )


####+BEGIN: bx:cs:py3:section :title "CS-Lib Examples"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *CS-Lib Examples*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: bx:dblock:python:func :funcName "examples_bpo_basicAccess" :comment "Show/Verify/Update For relevant PBDs" :funcType "examples" :retType "none" :deco "" :argsList "oneBpo"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-examples [[elisp:(outline-show-subtree+toggle)][||]] /examples_bpo_basicAccess/ =Show/Verify/Update For relevant PBDs= retType=none argsList=(oneBpo)  [[elisp:(org-cycle)][| ]]
#+end_org """
def examples_bpo_basicAccess(
    oneBpo,
):
####+END:
    """
** Common examples.
"""
    def cpsInit(): return collections.OrderedDict()
    def menuItem(verbosity): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity=verbosity) # 'little' or 'none'
    # def execLineEx(cmndStr): cs.examples.execInsert(execLine=cmndStr)

    #oneBpo = "pmi_ByD-100001"

    # def moduleOverviewMenuItem(overviewCmndName):
    #     cs.examples.menuChapter('* =Module=  Overview (desc, usage, status)')
    #     cmndName = "overview_bxpBaseDir" ; cmndArgs = "moduleDescription moduleUsage moduleStatus" ;
    #     cps = collections.OrderedDict()
    #     cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='none') # 'little' or 'none'

    # moduleOverviewMenuItem(bpo_libOverview)

    cs.examples.menuChapter('*General BPO Access And Management Commands*')

    cmndName = "bpoIdTypeObtain"
    cmndArgs = ""
    cps = cpsInit() ; cps['bpoId'] = oneBpo
    menuItem(verbosity='none')
    # menuItem(verbosity='full')

    cmndName = "bpoBaseDirObtain"
    cmndArgs = ""
    cps = cpsInit() ; cps['bpoId'] = oneBpo
    menuItem(verbosity='none')
    # menuItem(verbosity='full')

    cmndName = "forPathObtainBpoId"
    cmndArgs = "~/bpos/usageEnvs/fullUse/aas/"
    cps = cpsInit()
    menuItem(verbosity='none')




####+BEGIN: bx:dblock:python:section :title "ICM Commands"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *ICM Commands*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "bpoIdTypeObtain" :comment "Returns the type of bpoId" :parsMand "bpoId" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<bpoIdTypeObtain>>  =verify= parsMand=bpoId ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class bpoIdTypeObtain(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        callParamsDict = {'bpoId': bpoId, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
####+END:
        retVal = bpoId_Type_obtain(bpoId)

        if rtInv.outs:
            b_io.ann.write(f"{retVal}")

        return cmndOutcome.set(
            opError=b.op.notAsFailure(retVal),
            opResults=retVal,
        )

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "bpoBaseDirObtain" :parsMand "bpoId" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<bpoBaseDirObtain>>  =verify= parsMand=bpoId ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class bpoBaseDirObtain(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        callParamsDict = {'bpoId': bpoId, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
####+END:
        retVal = bpoBaseDir_obtain(bpoId)

        if rtInv.outs:
            b_io.ann.write(f"{retVal}")

        return cmndOutcome.set(
            opError=b.op.notAsFailure(retVal),
            opResults=retVal,
        )

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "forPathObtainBpoId" :parsMand "" :parsOpt "" :argsMin 1 :argsMax 1 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<forPathObtainBpoId>>  =verify= argsMin=1 argsMax=1 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class forPathObtainBpoId(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 1,}

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
        retVal = givenPathObtainBpoId(argsList[0])

        # print(retVal)

        return cmndOutcome.set(
            opError=b.op.notAsFailure(retVal),
            opResults=retVal,
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
