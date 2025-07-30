#!/usr/bin/env python

####+BEGIN: b:prog:file/particulars :authors ("./inserts/authors-mb.org")
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars |]]* :: Authors, version
** This File: /l/pip/sbom/py3/bin/exmpl-func-sbom.cs
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

""" #+begin_org
* Panel::  [[file:/bisos/panels/bisos-apps/NameOfThePanelComeHere/_nodeBase_/fullUsagePanel-en.org]]
* Overview and Relevant Pointers
#+end_org """

from bisos import b

from bisos.sbom import pkgsSeed
ap = pkgsSeed.aptPkg

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


aptPkgsList = [
    ap("gh", func=ghAptSource),   # Github API Cli -- taken from https://github.com/cli/cli/blob/trunk/docs/install_linux.md
]

pkgsSeed.setup(
    aptPkgsList=aptPkgsList,
    pipPkgsList=[],
    pipxPkgsList=[],
)

pkgsSeed.plantWithWhich("seedSbom.cs")
