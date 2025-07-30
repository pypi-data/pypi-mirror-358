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
** This File: /bisos/git/auth/bxRepos/bisos-pip/debian/py3/bisos/debian/configFile.py
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:python:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
from enum import verify
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['configFile'], }
csInfo['version'] = '202305114855'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'configFile-Panel.org'
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

from bisos.basics import pyRunAs

import pathlib
import __main__

import os
import abc

import os
# import subprocess

import logging

log = logging.getLogger(__name__)

from bisos.common import csParam

####+BEGIN: bx:cs:py3:section :title "Configuration File Manager"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Configuration File Manager*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:class/decl :className "ConfigFile" :superClass "abc.ABC" :comment "Config Content" :classType "abs"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-abs    [[elisp:(outline-show-subtree+toggle)][||]] /ConfigFile/  superClass=abc.ABC =Config Content=  [[elisp:(org-cycle)][| ]]
#+end_org """
class ConfigFile(abc.ABC):
####+END:
    """
**
"""

####+BEGIN: b:py3:cs:method/typing :methodName "__init__" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /__init__/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def __init__(
####+END:
            self,
            name: typing.AnyStr = "",
    ):
        self.name = name

####+BEGIN: b:py3:cs:method/typing :methodName "configFilePath" :deco "abc.abstractmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /configFilePath/  deco=abc.abstractmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @abc.abstractmethod
    def configFilePath(
####+END:
            self,
    ) -> pathlib.Path:
        """ #+begin_org
*** [[elisp:(org-cycle)][| DocStr| ]]  Return Path of the config file.
        #+end_org """
        return pathlib.Path(f"abstractmethod")

####+BEGIN: b:py3:cs:method/typing :methodName "configFileStr" :deco "abc.abstractmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /configFileStr/  deco=abc.abstractmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @abc.abstractmethod
    def configFileStr(
####+END:
            self,
    ) -> str:
        """ #+begin_org
*** [[elisp:(org-cycle)][| DocStr| ]]  Return the config file as string.
        #+end_org """
        templateStr = """
"""
        return templateStr

####+BEGIN: b:py3:cs:method/typing :methodName "configFileUpdate" :methodType "eType" :retType "" :deco "default" :argsList ""
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-eType [[elisp:(outline-show-subtree+toggle)][||]] /configFileUpdate/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def configFileUpdate(
####+END
            self,
            runAs="user"
    ):
        """ #+begin_org
*** [[elisp:(org-cycle)][| DocStr| ]]
        #+end_org """

        contentStr = self.configFileStr()
        destPath = self.configFilePath()

        with open(destPath, "w") as thisFile:
            thisFile.write(f"{contentStr}\n")


####+BEGIN: b:py3:cs:method/typing :methodName "configFileKeepUpdate" :methodType "eType" :retType "" :deco "default" :argsList ""
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-eType [[elisp:(outline-show-subtree+toggle)][||]] /configFileKeepUpdate/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def configFileKeepUpdate(
####+END
            self,
    ):
        """ #+begin_org
*** [[elisp:(org-cycle)][| DocStr| ]]  
        #+end_org """
        # print _contentStr


####+BEGIN: b:py3:cs:method/typing :methodName "configFileRead" :methodType "eType" :retType "" :deco "default" :argsList ""
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-eType [[elisp:(outline-show-subtree+toggle)][||]] /configFileRead/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def configFileRead(
####+END
            self,
            runAs="user",
    ):
        """ #+begin_org
*** [[elisp:(org-cycle)][| DocStr| ]]  Read in from configFilePath
        #+end_org """

        destPath = self.configFilePath()

        if runAs == "user":
            with open(destPath, "w") as thisFile:
                result = thisFile.read()
        elif runAs == "root":
            result = pyRunAs.as_root_readFromFile(destPath)
        else:
            b_io.eh.problem_usageError(f"Bad runAs={runAs}")

        return result

####+BEGIN: b:py3:cs:method/typing :methodName "configFileVerify" :methodType "eType" :retType "" :deco "default" :argsList ""
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-eType [[elisp:(outline-show-subtree+toggle)][||]] /configFileVerify/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def configFileVerify(
####+END
            self,
            runAs="user",
    ):
        """ #+begin_org
*** [[elisp:(org-cycle)][| DocStr| ]]  Read in from configFilePath and verify that it is same as stdout.
        #+end_org """

        readStr = self.configFileRead()
        contentStr = self.configFileStr(runAs=runAs)

        if readStr == contentStr:
            return True
        else:
            return False


####+BEGIN: b:py3:cs:method/typing :methodName "configFileDelete" :methodType "eType" :retType "" :deco "default" :argsList ""
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-eType [[elisp:(outline-show-subtree+toggle)][||]] /configFileDelete/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def configFileDelete(
####+END
            self,
            runAs="user",
    ):
        """ #+begin_org
*** [[elisp:(org-cycle)][| DocStr| ]]  Delete  configFilePath
        #+end_org """

        destPath = self.configFilePath()

        if runAs == "user":
            destPath.unlink()
        elif runAs == "root":
            pyRunAs.as_root_deleteFile(destPath)
        else:
            b_io.eh.problem_usageError(f"Bad runAs={runAs}")


####+BEGIN: b:py3:cs:method/typing :methodName "configFileStdout" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /configFileStdout/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def configFileStdout(
####+END
            self,
    ):
        """ #+begin_org
*** [[elisp:(org-cycle)][| DocStr| ]]  Look in control dir for file params.
        #+end_org """
        contentStr = self.configFileStr()
        print(contentStr)

####+BEGIN: bx:dblock:python:func :funcName "commonParamsSpecify" :funcType "ParSpec" :retType "" :deco "" :argsList "csParams"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-ParSpec  [[elisp:(outline-show-subtree+toggle)][||]] /commonParamsSpecify/ retType= argsList=(csParams)  [[elisp:(org-cycle)][| ]]
#+end_org """
def commonParamsSpecify(
    csParams,
):
####+END:
    csParams.parDictAdd(
        parName='runAs',
        parDescription="The user to run as. Typically one of user, root or bisos",
        parDataType=None,
        parDefault="user",
        parChoices=["any"],
        # parScope=icm.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--runAs',
    )


####+BEGIN: b:py3:cs:func/typing :funcName "clsGet_Ok2Del" :funcType "extTyped" :deco "track"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-extTyped [[elisp:(outline-show-subtree+toggle)][||]] /clsGet_Ok2Del/  deco=track  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def clsGet_Ok2Del(
####+END:
        arg1: str,
):
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ]
    #+end_org """
    

    #        thisCls = getattr(__main__, cls)
    from bisos.debian import bifSystemd_csu   # here, not no top -- otherwise circular
    thisCls = getattr(bifSystemd_csu, cls)


####+BEGIN: b:py3:cs:func/typing :funcName "examples_csu" :funcType "eType" :retType "" :deco "default" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-eType  [[elisp:(outline-show-subtree+toggle)][||]] /examples_csu/  deco=default  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def examples_csu(
####+END:
        concreteConfigFile: typing.AnyStr = "",
        sectionTitle: typing.AnyStr = "",
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Examples of Service Access Instance Commands.
    #+end_org """

    od = collections.OrderedDict
    cmnd = cs.examples.cmndEnter
    literal = cs.examples.execInsert

    thisCls = getattr(__main__, str(concreteConfigFile))

    # from bisos.debian import bifSystemd_csu   # here, not no top -- otherwise circular
    # thisCls = getattr(bifSystemd_csu, str(concreteConfigFile))
    # print(thisCls)

    filePath = getattr(thisCls, f"configFilePath")()

    concreteConfigFilePars = od([('cls', concreteConfigFile),])
    concreteConfigFileRootPars = od([('cls', concreteConfigFile), ('runAs', "root")])

    cs.examples.menuChapter(f'*Config Content {filePath}*')

    cmnd('configFileStdout', pars=concreteConfigFilePars, comment=f" # That which will be stored in configFile")

    cmnd('configFilePath', pars=concreteConfigFilePars, comment=f" # ls -l {filePath}")
    cmnd('configFilePath', pars=concreteConfigFileRootPars, comment=f" # sudo ls -l {filePath}")

    cmnd('configFileUpdate', pars=concreteConfigFilePars, comment=f" # write stdout  to {filePath}")
    cmnd('configFileUpdate', pars=concreteConfigFileRootPars, comment=f" # write stdout  to {filePath}")

    cmnd('configFileCat', pars=concreteConfigFilePars, comment=f" # cat {filePath}")
    cmnd('configFileCat', pars=concreteConfigFileRootPars, comment=f" # sudo cat {filePath}")

    cmnd('configFileVerify', pars=concreteConfigFilePars, comment=f" # are stdout and {filePath} the same")
    cmnd('configFileVerify', pars=concreteConfigFileRootPars, comment=f" # are stdout and {filePath} the same")

    cmnd('configFileDelete', pars=concreteConfigFilePars, comment=f" # delete {filePath}")
    cmnd('configFileDelete', pars=concreteConfigFileRootPars, comment=f" # sudo delete {filePath}")


####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "CmndSvcs" :anchor ""  :extraInfo "File Parameters Get/Set -- Commands"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _CmndSvcs_: |]]  File Parameters Get/Set -- Commands  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "configFileStdout" :extent "verify" :parsMand "cls" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<configFileStdout>>  =verify= parsMand=cls ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class configFileStdout(cs.Cmnd):
    cmndParamsMandatory = [ 'cls', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             cls: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        callParamsDict = {'cls': cls, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        cls = csParam.mappedValue('cls', cls)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Return a dict of parName:parValue as results
        #+end_org """)

        thisCls = getattr(__main__, cls)
        thisCls.configFileStdout()

        return cmndOutcome

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "configFilePath" :extent "verify" :parsMand "cls" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<configFilePath>>  =verify= parsMand=cls ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class configFilePath(cs.Cmnd):
    cmndParamsMandatory = [ 'cls', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             cls: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        callParamsDict = {'cls': cls, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        cls = csParam.mappedValue('cls', cls)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Return a dict of parName:parValue as results
        #+end_org """)

        thisCls = getattr(__main__, cls)
        path = thisCls.configFilePath()

        if rtInv.outs:
            b_io.tm.here(f"configFilePath={path}")
            if os.path.isfile(path):
                if b.subProc.Op(outcome=cmndOutcome, log=1).bash(
                        f"""ls -l {path}""",
                ).isProblematic():  return(b_io.eh.badOutcome(cmndOutcome))
            else:
               print(f"""{path}""")

        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=path,
        )

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "configFileUpdate" :extent "verify" :parsMand "cls" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<configFileUpdate>>  =verify= parsMand=cls ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class configFileUpdate(cs.Cmnd):
    cmndParamsMandatory = [ 'cls', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             cls: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        callParamsDict = {'cls': cls, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        cls = csParam.mappedValue('cls', cls)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Return a dict of parName:parValue as results
        #+end_org """)

        thisCls = getattr(__main__, cls)
        thisCls.configFileUpdate()

        if rtInv.outs:
            b_io.tm.here(f"configFileUpdate")

        return cmndOutcome

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "configFileCat" :extent "verify" :parsMand "cls" :parsOpt "runAs" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<configFileCat>>  =verify= parsMand=cls parsOpt=runAs ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class configFileCat(cs.Cmnd):
    cmndParamsMandatory = [ 'cls', ]
    cmndParamsOptional = [ 'runAs', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             cls: typing.Optional[str]=None,  # Cs Mandatory Param
             runAs: typing.Optional[str]=None,  # Cs Optional Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'cls': cls, 'runAs': runAs, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        cls = csParam.mappedValue('cls', cls)
        runAs = csParam.mappedValue('runAs', runAs)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Return a dict of parName:parValue as results
        #+end_org """)

        thisCls = getattr(__main__, cls)
        fileAsStr = thisCls.configFileRead(runAs=runAs)

        print(fileAsStr)

        return cmndOutcome

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "configFileVerify" :extent "verify" :parsMand "cls" :parsOpt "runAs" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<configFileVerify>>  =verify= parsMand=cls parsOpt=runAs ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class configFileVerify(cs.Cmnd):
    cmndParamsMandatory = [ 'cls', ]
    cmndParamsOptional = [ 'runAs', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             cls: typing.Optional[str]=None,  # Cs Mandatory Param
             runAs: typing.Optional[str]=None,  # Cs Optional Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'cls': cls, 'runAs': runAs, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        cls = csParam.mappedValue('cls', cls)
        runAs = csParam.mappedValue('runAs', runAs)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Return a dict of parName:parValue as results
        #+end_org """)

        thisCls = getattr(__main__, cls)
        verify = thisCls.configFileVerify(runAs=runAs)

        print(f"{verify}")

        return cmndOutcome

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "configFileDelete" :extent "verify" :parsMand "cls" :parsOpt "runAs" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<configFileDelete>>  =verify= parsMand=cls parsOpt=runAs ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class configFileDelete(cs.Cmnd):
    cmndParamsMandatory = [ 'cls', ]
    cmndParamsOptional = [ 'runAs', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             cls: typing.Optional[str]=None,  # Cs Mandatory Param
             runAs: typing.Optional[str]=None,  # Cs Optional Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'cls': cls, 'runAs': runAs, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        cls = csParam.mappedValue('cls', cls)
        runAs = csParam.mappedValue('runAs', runAs)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Return a dict of parName:parValue as results
        #+end_org """)

        thisCls = getattr(__main__, cls)
        thisCls.configFileDelete(runAs=runAs)

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
