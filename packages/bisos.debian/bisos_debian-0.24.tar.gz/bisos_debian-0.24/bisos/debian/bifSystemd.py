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
** This File: /bisos/git/auth/bxRepos/bisos-pip/debian/py3/bisos/debian/bifSystemd.py
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:python:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['bifSystemd'], }
csInfo['version'] = '202305113150'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'bifSystemd-Panel.org'
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

import os
import subprocess

from bisos.basics import pyRunAs

import logging

log = logging.getLogger(__name__)

####+BEGIN: bx:cs:py3:section :title "Systemd Unit"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Systemd Unit*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:



####+BEGIN: b:py3:class/decl :className "SysUnit" :superClass "" :comment "Systemd System Unit" :classType ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-       [[elisp:(outline-show-subtree+toggle)][||]] /SysUnit/  superClass=object =Systemd System Unit=  [[elisp:(org-cycle)][| ]]
#+end_org """
class SysUnit(object):
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
            name,
            type="service",
    ):

        self.name = name
        self.serviceName = f"{name}.{type}"
        self.serviceFilePath()

        # try:
        #     self._systemctl(['--help'])
        # except FileNotFoundError as e:
        #     log.error("Unable to find systemctl!")
        #     raise(e)
        log.debug("Initialized systemd.Unit for '{name}' with type '{type}'".format(name=name, type=type))


####+BEGIN: b:py3:cs:method/typing :methodName "serviceFilePath" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /serviceFilePath/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def serviceFilePath(
####+END
            self,
    ) -> pathlib.Path:
        """ #+begin_org
*** [[elisp:(org-cycle)][| DocStr| ]]  Look in control dir for file params.
        #+end_org """
        self._serviceFilePath = os.path.join("/etc/systemd/system", self.serviceName)
        return pathlib.Path(f"{self._serviceFilePath}")

####+BEGIN: b:py3:cs:method/typing :methodName "serviceFileVerify" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /serviceFileVerify/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def serviceFileVerify(
####+END
            self,
    ):
        """ #+begin_org
*** [[elisp:(org-cycle)][| DocStr| ]]  Look in control dir for file params.
        #+end_org """
        print(f"NOTYET, verify that serviceFilePath exists")
        #return pathlib.Path(f"{self.serviceFilePath}")

####+BEGIN: b:py3:cs:method/typing :methodName "ensure" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /ensure/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def ensure(
####+END
            self,
            restart=True,
            enable=True,
    ):

        self.serviceFileVerify()
        self.reload()
        if restart:
            self.restart()
        if enable:
            self.enable()

####+BEGIN: b:py3:cs:method/typing :methodName "remove" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /remove/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def remove(
####+END
            self,
    ):
        try:
            if self._serviceFilePath.is_file():
                self.stop()
                self.disable()
        except subprocess.CalledProcessError:
            pass

        log.info(f"Removing service file for {self.name} from {self._serviceFilePath}")
        try:
            self._serviceFilePath.unlink()
            log.debug("Successfully removed service file")
        except FileNotFoundError:
            log.debug("No service file found")
        self.reload()

####+BEGIN: b:py3:cs:method/typing :methodName "_systemctl" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /_systemctl/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def _systemctl(
####+END
            self,
            args,
    ):
        sudoSubCommands = [ "start", "stop", "restart",  "daemon-reload", "enable", "disable" ]
        needsSudo = ""

        sysdCmnd = args.split()[0]

        if sysdCmnd in sudoSubCommands:
            needsSudo = "sudo "

        if b.subProc.Op(outcome=None, log=1).bash(
                f"""{needsSudo}systemctl {args}""",
        ).isProblematic():  return(None)


####+BEGIN: b:py3:cs:method/typing :methodName "_systemctlOld" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /_systemctlOld/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def _systemctlOld(
####+END
            self,
            args,
            stderr=None,
    ):
        try:
            subprocess.check_output(["systemctl --user"] + args, stderr=stderr)
        except subprocess.CalledProcessError as e:
            log.warning("Failed to run systemctl with parameters {args}".format(args=args))
            if e.args[0] == 5:
                raise(
                    FileNotFoundError(
                        "Unable to find specified system service (args: {})".format(str(args))
                        )
                    ) from None
            else:
                raise(e)

####+BEGIN: b:py3:cs:method/typing :methodName "reload" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /reload/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def reload(
####+END:
            self,
    ):
        log.info("Reloading daemon files")
        self._systemctl("daemon-reload")

####+BEGIN: b:py3:cs:method/typing :methodName "status" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /status/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def status(
####+END:
            self,
    ):
        log.info(f"Status {self.serviceName}")
        self._systemctl(f"status {self.serviceName}")


####+BEGIN: b:py3:cs:method/typing :methodName "restart" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /restart/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def restart(
####+END:
            self,
    ):
        log.info(f"Restarting {self.serviceName}")
        self._systemctl(f"restart {self.serviceName}")

####+BEGIN: b:py3:cs:method/typing :methodName "stop" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /stop/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def stop(
####+END:
            self,
    ):
        log.info(f"Stopping {self.serviceName}")
        self._systemctl(f"stop {self.serviceName}")

####+BEGIN: b:py3:cs:method/typing :methodName "start" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /start/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def start(
####+END:
            self,
    ):
        log.info(f"Starting {self.serviceName}")
        self._systemctl(f"start {self.serviceName}")

####+BEGIN: b:py3:cs:method/typing :methodName "enable" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /enable/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def enable(
####+END:
            self,
    ):
        log.info(f"Enabling {self.serviceName}")
        self._systemctl(f"enable {self.serviceName}")

####+BEGIN: b:py3:cs:method/typing :methodName "disable" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /disable/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def disable(
####+END:
            self,
    ):
        log.info(f"Disabling {self.serviceName}")
        self._systemctl(f"disable {self.serviceName}")

####+BEGIN: b:py3:cs:method/typing :methodName "show" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /show/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def show(
####+END:
            self,
    ):
        log.info(f"Showing {self.serviceName}")
        self._systemctl(f"show {self.serviceName}")

####+BEGIN: b:py3:cs:method/typing :methodName "journalLogs" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /journalLogs/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def journalLogs(
####+END:
            self,
    ):
        log.info(f"Journal Logs {self.serviceName}")
        if b.subProc.Op(outcome=None, log=1).bash(
                f"""journalctl -u {self.serviceName} | tail -200""",
        ).isProblematic():  return(None)


####+BEGIN: b:py3:class/decl :className "UserUnit" :superClass "" :comment "Systemd User Unit" :classType ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-       [[elisp:(outline-show-subtree+toggle)][||]] /UserUnit/  superClass=object =Systemd User Unit=  [[elisp:(org-cycle)][| ]]
#+end_org """
class UserUnit(object):
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
            name,
            type="service",
    ):

        self.name = name
        self.serviceName = f"{name}.{type}"
        # self._serviceFilePath = os.path.join("/etc/systemd/system", self.serviceName)
        self.serviceFilePath()

        # try:
        #     self._systemctl(['--help'])
        # except FileNotFoundError as e:
        #     log.error("Unable to find systemctl!")
        #     raise(e)
        log.debug("Initialized systemd.Unit for '{name}' with type '{type}'".format(name=name, type=type))


####+BEGIN: b:py3:cs:method/typing :methodName "serviceFilePath" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /serviceFilePath/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def serviceFilePath(
####+END
            self,
    ) -> pathlib.Path:
        """ #+begin_org
*** [[elisp:(org-cycle)][| DocStr| ]]  Look in control dir for file params.
        #+end_org """
        home = pathlib.Path.home()
        # ~/.config/systemd/user/
        self._serviceFilePath = home.joinpath(f".config/systemd/user/{self.serviceName}")
        return pathlib.Path(f"{self._serviceFilePath}")

####+BEGIN: b:py3:cs:method/typing :methodName "serviceFileVerify" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /serviceFileVerify/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def serviceFileVerify(
####+END
            self,
    ):
        """ #+begin_org
*** [[elisp:(org-cycle)][| DocStr| ]]  Look in control dir for file params.
        #+end_org """
        print(f"NOTYET, verify that serviceFilePath exists")
        #return pathlib.Path(f"{self.serviceFilePath}")

####+BEGIN: b:py3:cs:method/typing :methodName "ensure" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /ensure/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def ensure(
####+END
            self,
            restart=True,
            enable=True,
    ):

        self.serviceFileVerify()
        self.reload()
        if restart:
            self.restart()
        if enable:
            self.enable()

####+BEGIN: b:py3:cs:method/typing :methodName "remove" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /remove/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def remove(
####+END
            self,
    ):
        try:
            if self._serviceFilePath.is_file():
                self.stop()
                self.disable()
        except subprocess.CalledProcessError:
            pass

        log.info(f"Removing service file for {self.name} from {self._serviceFilePath}")
        try:
            self._serviceFilePath.unlink()
            log.debug("Successfully removed service file")
        except FileNotFoundError:
            log.debug("No service file found")
        self.reload()

####+BEGIN: b:py3:cs:method/typing :methodName "_systemctl" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /_systemctl/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def _systemctl(
####+END
            self,
            args,
    ):
        if b.subProc.Op(outcome=None, log=1).bash(
                f"""systemctl --user {args}""",
        ).isProblematic():  return(None)

####+BEGIN: b:py3:cs:method/typing :methodName "_systemctlOld" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /_systemctlOld/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def _systemctlOld(
####+END
            self,
            args,
            stderr=None,
    ):
        try:
            subprocess.check_output(["systemctl --user"] + args, stderr=stderr)
        except subprocess.CalledProcessError as e:
            log.warning("Failed to run systemctl with parameters {args}".format(args=args))
            if e.args[0] == 5:
                raise(
                    FileNotFoundError(
                        "Unable to find specified system service (args: {})".format(str(args))
                        )
                    ) from None
            else:
                raise(e)

####+BEGIN: b:py3:cs:method/typing :methodName "reload" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /reload/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def reload(
####+END:
            self,
    ):
        log.info("Reloading daemon files")
        self._systemctl("daemon-reload")

####+BEGIN: b:py3:cs:method/typing :methodName "status" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /status/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def status(
####+END:
            self,
    ):
        log.info(f"Status {self.serviceName}")
        self._systemctl(f"status {self.serviceName}")


####+BEGIN: b:py3:cs:method/typing :methodName "restart" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /restart/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def restart(
####+END:
            self,
    ):
        log.info(f"Restarting {self.serviceName}")
        self._systemctl(f"restart {self.serviceName}")

####+BEGIN: b:py3:cs:method/typing :methodName "stop" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /stop/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def stop(
####+END:
            self,
    ):
        log.info(f"Stopping {self.serviceName}")
        self._systemctl(f"stop {self.serviceName}")

####+BEGIN: b:py3:cs:method/typing :methodName "start" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /start/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def start(
####+END:
            self,
    ):
        log.info(f"Starting {self.serviceName}")
        self._systemctl(f"start {self.serviceName}")

####+BEGIN: b:py3:cs:method/typing :methodName "enable" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /enable/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def enable(
####+END:
            self,
    ):
        log.info(f"Enabling {self.serviceName}")
        self._systemctl(f"enable {self.serviceName}")

####+BEGIN: b:py3:cs:method/typing :methodName "disable" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /disable/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def disable(
####+END:
            self,
    ):
        log.info(f"Disabling {self.serviceName}")
        self._systemctl(f"disable {self.serviceName}")

####+BEGIN: b:py3:cs:method/typing :methodName "journalLogs" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /journalLogs/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def journalLogs(
####+END:
            self,
    ):
        log.info(f"Journal Logs {self.serviceName}")
        if b.subProc.Op(outcome=None, log=1).bash(
                f"""journalctl --user -u {self.serviceName} | tail -200""",
        ).isProblematic():  return(None)


####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "CSU" :anchor ""  :extraInfo "Command Services Section"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _CSU_: |]]  Command Services Section  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:


####+BEGIN: b:py3:cs:func/typing :funcName "examples_csuUserUnit" :funcType "eType" :retType "" :deco "default" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-eType  [[elisp:(outline-show-subtree+toggle)][||]] /examples_csuUserUnit/  deco=default  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def examples_csuUserUnit(
####+END:
        userUnitInstanceName: typing.AnyStr = '',
        sectionTitle: typing.AnyStr = '',
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Examples of Service Access Instance Commands.
    #+end_org """

    def cpsInit(): return collections.OrderedDict()
    def menuItem(verbosity): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity=verbosity) # 'little' or 'none'

    if sectionTitle == 'default':
        cs.examples.menuChapter('*Remote Operations Management*')

    cs.examples.menuChapter('*Systemd User Unit Actions*')

    cmndName = "serviceFilePath" ;  cmndArgs = ""
    cps=cpsInit(); cps['cls'] = userUnitInstanceName ;  menuItem(verbosity='none')

    cmndName = "sysdUserUnit" ;  cmndArgs = "serviceFileVerify"
    cps=cpsInit(); cps['cls'] = userUnitInstanceName
    menuItem(verbosity='none') ; menuItem(verbosity='full')

    cmndName = "sysdUserUnit" ;  cmndArgs = "ensure"
    cps=cpsInit(); cps['cls'] = userUnitInstanceName ;  menuItem(verbosity='none')

    cmndName = "sysdUserUnit" ;  cmndArgs = "remove"
    cps=cpsInit(); cps['cls'] = userUnitInstanceName ;  menuItem(verbosity='none')

    cs.examples.menuChapter('*Systemctl Actions*')

    cmndName = "sysdUserUnit" ;  cmndArgs = "reload"
    cps=cpsInit(); cps['cls'] = userUnitInstanceName ;  menuItem(verbosity='none')

    cmndName = "sysdUserUnit" ;  cmndArgs = "status"
    cps=cpsInit(); cps['cls'] = userUnitInstanceName ;  menuItem(verbosity='none')

    cmndName = "sysdUserUnit" ;  cmndArgs = "restart"
    cps=cpsInit(); cps['cls'] = userUnitInstanceName ;  menuItem(verbosity='none')

    cmndName = "sysdUserUnit" ;  cmndArgs = "stop"
    cps=cpsInit(); cps['cls'] = userUnitInstanceName ;  menuItem(verbosity='none')

    cmndName = "sysdUserUnit" ;  cmndArgs = "start"
    cps=cpsInit(); cps['cls'] = userUnitInstanceName ;  menuItem(verbosity='none')

    cmndName = "sysdUserUnit" ;  cmndArgs = "enable"
    cps=cpsInit(); cps['cls'] = userUnitInstanceName ;  menuItem(verbosity='none')

    cmndName = "sysdUserUnit" ;  cmndArgs = "disable"
    cps=cpsInit(); cps['cls'] = userUnitInstanceName ;  menuItem(verbosity='none')

    cmndName = "sysdUserUnit" ;  cmndArgs = "journalLogs"
    cps=cpsInit(); cps['cls'] = userUnitInstanceName ;  menuItem(verbosity='none')


####+BEGIN: b:py3:cs:func/typing :funcName "examples_csuSysUnit" :funcType "eType" :retType "" :deco "default" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-eType  [[elisp:(outline-show-subtree+toggle)][||]] /examples_csuSysUnit/  deco=default  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def examples_csuSysUnit(
####+END:
        userUnitInstanceName: typing.AnyStr = '',
        sectionTitle: typing.AnyStr = '',
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Examples of Service Access Instance Commands.
    #+end_org """


    od = collections.OrderedDict
    cmnd = cs.examples.cmndEnter
    literal = cs.examples.execInsert

    thisCls = getattr(__main__, userUnitInstanceName)
    serviceName = getattr(thisCls, f"serviceName")


    sysUnitNamePars = od([('cls', userUnitInstanceName),])

    if sectionTitle == 'default':
        cs.examples.menuChapter('*Remote Operations Management*')

    cs.examples.menuChapter('*Systemd Unit Actions *')

    cmnd('serviceFilePath', pars=sysUnitNamePars, comment=" # ")

    cmnd('sysdSysUnit', pars=sysUnitNamePars, args='''serviceFileVerify''', comment=" # NOTYET")
    cmnd('sysdSysUnit', pars=sysUnitNamePars, args='''ensure''', comment=" # fileVerify + reload + restart + enable")
    cmnd('sysdSysUnit', pars=sysUnitNamePars, args='''remove''', comment=" # stop + disable + unlink")

    cs.examples.menuChapter('*Systemctl Actions (sudo) *')

    cmnd('sysdSysUnit', pars=sysUnitNamePars, args='''reload''', comment=f" # systemctl reload {serviceName}")
    cmnd('sysdSysUnit', pars=sysUnitNamePars, args='''stop''', comment=f" # systemctl stop {serviceName}")
    cmnd('sysdSysUnit', pars=sysUnitNamePars, args='''start''', comment=f" # systemctl start {serviceName}")
    cmnd('sysdSysUnit', pars=sysUnitNamePars, args='''restart''', comment=f" # systemctl restart {serviceName}")
    cmnd('sysdSysUnit', pars=sysUnitNamePars, args='''enable''', comment=f" # systemctl enable {serviceName}")
    cmnd('sysdSysUnit', pars=sysUnitNamePars, args='''disable''', comment=f" # systemctl disable {serviceName}")

    cs.examples.menuChapter('*Systemctl Information*')

    cmnd('sysdSysUnit', pars=sysUnitNamePars, args='''status''', comment=f" # systemctl status {serviceName}")
    cmnd('sysdSysUnit', pars=sysUnitNamePars, args='''show''', comment=f" # systemctl show {serviceName}")

    cs.examples.menuChapter('*Journal Logs*')
    
    cmnd('sysdSysUnit', pars=sysUnitNamePars, args='''journalLogs''', comment=" # NOTYET")

    cs.examples.menuChapter('*Journal Logs -- Literal Commands*')

    literal(f"journalctl --list-boots", comment=" # NOTYET")
    literal(f"journalctl -b", comment=" # NOTYET")
    literal(f"journalctl -u {serviceName} --since today", comment=" # NOTYET")
    literal(f"journalctl -u {serviceName} -n 200", comment=" # tail -200")
    literal(f"journalctl -u {serviceName} -f", comment=" # tail -f")

####+BEGIN: b:py3:cs:func/typing :funcName "examples_csuSysUnitObsoleted" :funcType "eType" :retType "" :deco "default" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-eType  [[elisp:(outline-show-subtree+toggle)][||]] /examples_csuSysUnitObsoleted/  deco=default  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def examples_csuSysUnitObsoleted(
####+END:
        userUnitInstanceName: typing.AnyStr = '',
        sectionTitle: typing.AnyStr = '',
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr | ] Examples of Service Access Instance Commands.
    #+end_org """

    def cpsInit(): return collections.OrderedDict()
    def menuItem(verbosity): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity=verbosity) # 'little' or 'none'

    if sectionTitle == 'default':
        cs.examples.menuChapter('*Remote Operations Management*')

    cs.examples.menuChapter('*Systemd User Unit Actions*')

    cmndName = "serviceFilePath" ;  cmndArgs = ""
    cps=cpsInit(); cps['cls'] = userUnitInstanceName ;  menuItem(verbosity='none')

    cmndName = "sysdSysUnit" ;  cmndArgs = "serviceFileVerify"
    cps=cpsInit(); cps['cls'] = userUnitInstanceName
    menuItem(verbosity='none') ; menuItem(verbosity='full')

    cmndName = "sysdSysUnit" ;  cmndArgs = "ensure"
    cps=cpsInit(); cps['cls'] = userUnitInstanceName ;  menuItem(verbosity='none')

    cmndName = "sysdSysUnit" ;  cmndArgs = "remove"
    cps=cpsInit(); cps['cls'] = userUnitInstanceName ;  menuItem(verbosity='none')

    cs.examples.menuChapter('*Systemctl Actions*')

    cmndName = "sysdSysUnit" ;  cmndArgs = "reload"
    cps=cpsInit(); cps['cls'] = userUnitInstanceName ;  menuItem(verbosity='none')

    cmndName = "sysdSysUnit" ;  cmndArgs = "status"
    cps=cpsInit(); cps['cls'] = userUnitInstanceName ;  menuItem(verbosity='none')

    cmndName = "sysdSysUnit" ;  cmndArgs = "restart"
    cps=cpsInit(); cps['cls'] = userUnitInstanceName ;  menuItem(verbosity='none')

    cmndName = "sysdSysUnit" ;  cmndArgs = "stop"
    cps=cpsInit(); cps['cls'] = userUnitInstanceName ;  menuItem(verbosity='none')

    cmndName = "sysdSysUnit" ;  cmndArgs = "start"
    cps=cpsInit(); cps['cls'] = userUnitInstanceName ;  menuItem(verbosity='none')

    cmndName = "sysdSysUnit" ;  cmndArgs = "enable"
    cps=cpsInit(); cps['cls'] = userUnitInstanceName ;  menuItem(verbosity='none')

    cmndName = "sysdSysUnit" ;  cmndArgs = "disable"
    cps=cpsInit(); cps['cls'] = userUnitInstanceName ;  menuItem(verbosity='none')

    cmndName = "sysdSysUnit" ;  cmndArgs = "journalLogs"
    cps=cpsInit(); cps['cls'] = userUnitInstanceName ;  menuItem(verbosity='none')



####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "CmndSvcs" :anchor ""  :extraInfo "File Parameters Get/Set -- Commands"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _CmndSvcs_: |]]  File Parameters Get/Set -- Commands  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "sysdSysUnit" :extent "verify" :parsMand "cls" :parsOpt "" :argsMin 1 :argsMax 9999 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<sysdSysUnit>>  =verify= parsMand=cls argsMin=1 argsMax=9999 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class sysdSysUnit(cs.Cmnd):
    cmndParamsMandatory = [ 'cls', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 9999,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             cls: typing.Optional[str]=None,  # Cs Mandatory Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'cls': cls, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        cls = csParam.mappedValue('cls', cls)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Return a dict of parName:parValue as results
        #+end_org """)

        cmndArgsSpecDict = self.cmndArgsSpec()

        action = self.cmndArgsGet("0", cmndArgsSpecDict, argsList)

        print(f"Action {action}")

        thisCls = getattr(__main__, cls)
        getattr(thisCls, f"{action}")()

        return cmndOutcome

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
            argChoices=[],
            argDescription="Action to be specified by each"
        )

        return cmndArgsSpecDict


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "sysdUserUnit" :extent "verify" :parsMand "cls" :parsOpt "" :argsMin 1 :argsMax 9999 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<sysdUserUnit>>  =verify= parsMand=cls argsMin=1 argsMax=9999 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class sysdUserUnit(cs.Cmnd):
    cmndParamsMandatory = [ 'cls', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 9999,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             cls: typing.Optional[str]=None,  # Cs Mandatory Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        callParamsDict = {'cls': cls, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        cls = csParam.mappedValue('cls', cls)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]] Return a dict of parName:parValue as results
        #+end_org """)

        cmndArgsSpecDict = self.cmndArgsSpec()

        action = self.cmndArgsGet("0", cmndArgsSpecDict, argsList)

        print(f"Action {action}")

        thisCls = getattr(__main__, cls)
        getattr(thisCls, f"{action}")()

        return cmndOutcome

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
            argDescription="Action to be specified by each"
        )

        return cmndArgsSpecDict


    
####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "serviceFilePath" :extent "verify" :parsMand "cls" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<serviceFilePath>>  =verify= parsMand=cls ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class serviceFilePath(cs.Cmnd):
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
        path = thisCls.serviceFilePath()

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


####+BEGIN: b:py3:cs:framework/endOfFile :basedOn "classification"
""" #+begin_org
* [[elisp:(org-cycle)][| *End-Of-Editable-Text* |]] :: emacs and org variables and control parameters
#+end_org """

#+STARTUP: showall

### local variables:
### no-byte-compile: t
### end:
####+END:
