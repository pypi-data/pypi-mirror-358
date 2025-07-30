#!/usr/bin/env python

####+BEGIN: b:prog:file/particulars :authors ("./inserts/authors-mb.org")
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars |]]* :: Authors, version
** This File: /l/pip/sbom/py3/bin/exmpl-sbom.cs
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

""" #+begin_org
* Panel::  [[file:/bisos/panels/bisos-apps/NameOfThePanelComeHere/_nodeBase_/fullUsagePanel-en.org]]
* Overview and Relevant Pointers
#+end_org """


from bisos.sbom import pkgsSeed
ap = pkgsSeed.aptPkg
pp = pkgsSeed.pipPkg

aptPkgsList = [
    ap("djbdns"),
    ap("facter"),
]

pipPkgsList = [
    pp("bisos.marmee"),
]

pipxPkgsList = [
    pp("bisos.marmee"),
]

pkgsSeed.setup(
    aptPkgsList=aptPkgsList,
    pipPkgsList=pipPkgsList,
    pipxPkgsList=pipxPkgsList,
)

# pkgsSeed.plantWithWhich("seedSbom.cs")
