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

from bisos.lcnt import lcntProcSeed
pp = lcntProcSeed.pipPkg

def ghAptSource():
    outcome =  b.subProc.WOpW(invedBy=None, log=1).bash(
        f"""
(type -p wget >/dev/null || (sudo apt update && sudo apt-get install wget -y)) \
	&& sudo mkdir -p -m 755 /etc/apt/keyrings \
	&& wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
	&& sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
	&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
	&& sudo apt update \
	&& sudo apt install gh -y
""")


pipPkgsList = [
]

lcntProcSeed.setup(
    seedType="AudioVideoProcessing",
    pipPkgsList=pipPkgsList,
    # examplesHook=qmail_binsPrep.examples_csu,
)

####+BEGIN: b:py3:cs:seed/withWhich :seedName "seedLcntProc.cs"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  seed       [[elisp:(outline-show-subtree+toggle)][||]] <<seedLcntProc.cs>>   [[elisp:(org-cycle)][| ]]
#+end_org """
import shutil
import os

seedName = 'seedLcntProc.cs'
seedFullPath = os.path.abspath(shutil.which(seedName))

__file__ = seedFullPath
with open(__file__) as f:
    exec(compile(f.read(), __file__, 'exec'))

####+END:
