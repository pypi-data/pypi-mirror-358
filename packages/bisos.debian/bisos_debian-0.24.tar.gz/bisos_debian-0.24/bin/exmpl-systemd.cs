#!/usr/bin/env python

####+BEGIN: b:prog:file/particulars :authors ("./inserts/authors-mb.org")
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars |]]* :: Authors, version
** This File: /bisos/git/auth/bxRepos/bisos-pip/binsprep/py3/bin/exmpl-func-binsPrep.cs
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

""" #+begin_org
* Panel::  [[file:/bisos/panels/bisos-apps/lcnt/lcntScreencasting/subTitles/_nodeBase_/fullUsagePanel-en.org]]
* Overview and Relevant Pointers
#+end_org """

from bisos import b

from bisos.debian import systemdSeed

def sysdUnitFileFunc():
    templateStr = """
[Unit]
Description=Facter Service
Documentation=man:facter(1)

[Service]
ExecStart=/bisos/venv/py3/dev-bisos3/bin/roPerf-facter.cs -v 20 --svcName="svcFacter"  -i csPerformer
Restart=always
RestartSec=60

[Install]
WantedBy=default.target
"""
    return templateStr


systemdSeed.setup(
    seedType="sysdSysUnit",  # or userUnit
    sysdUnitName="facter",
    sysdUnitFileFunc=sysdUnitFileFunc,
)


####+BEGIN: b:py3:cs:seed/withWhich :seedName "/bisos/git/auth/bxRepos/bisos-pip/debian/py3/bin/seedSystemd.cs"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  seed       [[elisp:(outline-show-subtree+toggle)][||]] <</bisos/git/auth/bxRepos/bisos-pip/debian/py3/bin/seedSystemd.cs>>   [[elisp:(org-cycle)][| ]]
#+end_org """
import shutil
import os
import sys

seedName = '/bisos/git/auth/bxRepos/bisos-pip/debian/py3/bin/seedSystemd.cs'
seedPath = shutil.which(seedName)
if seedPath is None:
    print(f'sys.exit() --- which found nothing for {seedName} --- Aborting')
    sys.exit()

__file__ = os.path.abspath(seedPath)
with open(__file__) as f:
    exec(compile(f.read(), __file__, 'exec'))

####+END:
