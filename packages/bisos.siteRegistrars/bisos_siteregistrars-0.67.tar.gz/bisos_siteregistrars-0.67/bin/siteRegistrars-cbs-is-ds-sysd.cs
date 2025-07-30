#!/usr/bin/env python

####+BEGIN: b:prog:file/particulars :authors ("./inserts/authors-mb.org")
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars |]]* :: Authors, version
** This File: /bisos/git/bxRepos/bisos-pip/graphviz-cs/py3/bin/exmpl-graphviz.cs
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

""" #+begin_org
* Panel::  [[file:/bisos/panels/bisos-apps/NOTYET/_nodeBase_/fullUsagePanel-en.org]]
* Overview and Relevant Pointers --
See /bisos/git/auth/bxRepos/bisos-pip/capability/py3/panels/bisos.capability/_nodeBase_/fullUsagePanel-en.org
siteRegistrars-cbs-is-ds-sysd.cs
cbs: Capability Bundle Specification  -- Based on a cba-sysd.cs seed
is: An Independent Service  --- /Service Component/
d:      -- Materialization includes a dedicated BPO or BPOs in addition to Realm-BPO
s:      -- Materialization is based on Site-BPO. /bisos/site

#+end_org """

from bisos.capability import cba_sysd_seed
from bisos.capability import cba_seed

cba_seed.setup(
    seedType="systemd",  # Extend using cba_sysd_seed.setup
    loader=None,
    sbom="siteRegistrars-sbom.cs",
    assemble="siteRegistrars-assemble.cs",
    materialize=None,
)


sysdUnitsList = [
    cba_sysd_seed.sysdUnit("siteRegistrars", "siteRegistrars-roPerf-sysd.cs")
]

cba_sysd_seed.setup(
    sysdUnitsList=sysdUnitsList,
)

cba_sysd_seed.plantWithWhich("cba-sysd.cs")
