====================================================================================================
bisos.siteRegistrars: CS Services for implementation of BISOS Site Regsitrars – box, cntnr and nets.
====================================================================================================

.. contents::
   :depth: 3
..

Panel Controls:: `Show-All <elisp:(show-all)>`__
`Overview <elisp:(org-shifttab)>`__
`Content <elisp:(progn (org-shifttab) (org-content))>`__ \|
`(1) <elisp:(delete-other-windows)>`__ \|
`S&Q <elisp:(progn (save-buffer) (kill-buffer))>`__
`Save <elisp:(save-buffer)>`__ `Quit <elisp:(kill-buffer)>`__
`Bury <elisp:(bury-buffer)>`__ Links:
`file:./panels/_nodeBase_/fullUsagePanel-en.org <./panels/_nodeBase_/fullUsagePanel-en.org>`__
(Package Panel)

Overview
========

bisos.facter is a python package for adoption and adaptation of
**facter** to python and PyCS-Framework. It is a BISOS-Capability and a
Standalone-BISOS-Package.

*bisos.facter* provides access to facter information through python.

*bisos.facter* is based on PyCS-Foundation and can be used both as a
Command and as a Service (invoke/perform model of remote operations)
using RPYC for central management of multiple systems.

.. _table-of-contents:

Table of Contents TOC
=====================

-  `Overview <#overview>`__
-  `About facter <#about-facter>`__
-  `About BISOS — ByStar Internet Services Operating
   System <#about-bisos-----bystar-internet-services-operating-system>`__
-  `Uses of bisos.facter <#uses-of-bisosfacter>`__
-  `bisos.facter as an Example of Command Services
   (PyCS) <#bisosfacter-as-an-example-of-command-services-pycs>`__
-  `bisos.facter as a Standalone Piece of
   BISOS <#bisosfacter-as-a-standalone-piece-of-bisos>`__
-  `Installation <#installation>`__

   -  `With pip <#with-pip>`__
   -  `With pipx <#with-pipx>`__

-  `Usage <#usage>`__

   -  `Locally (system command-line) <#locally-system-command-line>`__
   -  `Remotely (as a service –
      Performer+Invoker) <#remotely-as-a-service----performerinvoker>`__

      -  `Performer <#performer>`__
      -  `Invoker <#invoker>`__

   -  `Use by python script <#use-by-python-script>`__

-  `bisos.facter Code Walkthrough <#bisosfacter-code-walkthrough>`__

   -  `bisos.facter Source Code is in
      COMEEGA <#bisosfacter-source-code-is-in-comeega>`__
   -  `Take from
      120033/common/engAdopt <#take-from-120033commonengadopt>`__
   -  `./bin/facter.cs (./bin/roPerf-facter.cs
      ./bin/roInv-facter.cs) <#binfactercs--binroperf-factercs--binroinv-factercs>`__
   -  `./bisos/facter/facter.py <#bisosfacterfacterpy>`__
   -  `./bisos/facter/facter\ csu.py <#bisosfacterfacter_csupy>`__

-  `Documentation <#documentation>`__

   -  `bisos.facter Blee-Panels <#bisosfacter-blee-panels>`__

-  `Support <#support>`__

About facter
============

`Facter <https://www.puppet.com/docs/puppet/7/facter.html>`__ gathers
information about the system, which can be used as variables. Facter is
part of `puppet <https://www.puppet.com/>`__, but it can also be used
without puppet.

To install facter:

.. code:: bash

   sudo apt-get install -y facter

Facter is a ruby package. This bisos.facter python package provides
access to facter information through python, both locally and remotely.

About BISOS — ByStar Internet Services Operating System
=======================================================

Layered on top of Debian, **BISOS**: (By\* Internet Services Operating
System) is a unified and universal framework for developing both
internet services and software-service continuums that use internet
services. See `Bootstrapping ByStar, BISOS and
Blee <https://github.com/bxGenesis/start>`__ for information about
getting started with BISOS.

bisos.facter/ is a small piece of a much bigger picture. **BISOS** is a
foundation for **The Libre-Halaal ByStar Digital Ecosystem** which is
described as a cure for losses of autonomy and privacy that we are
experiencing in a book titled: `Nature of
Polyexistentials <https://github.com/bxplpc/120033>`__

Uses of bisos.facter
====================

Within BISOS, bisos.cmdb uses bisos.facter for Configuration Management
DataBase purposes.

bisos.facter as an Example of Command Services (PyCS)
=====================================================

bisos.facter can be used locally on command-line or remotely as a
service. bisos.facter is a PyCS multi-unit command-service. PyCS is a
framework that converges developement of CLI and Services. PyCS is an
alternative to FastAPI, Typer and Click.

bisos.facter uses the PyCS Framework to:

#. Provide access to facter information through python namedtuple
#. Provide local access to facter information on CLI
#. Provide remote access to facter information through remote invocation
   of python Expection Complete Operations using
   `rpyc <https://github.com/tomerfiliba-org/rpyc>`__.
#. Provide remote access to facter information on CLI

What is unique in the PyCS Framework is that these four models are all a
single abstraction.

bisos.facter as a Standalone Piece of BISOS
===========================================

bisos.facter is a standalone piece of BISOS. It can be used as a
self-contained Python package separate from BISOS. Follow the
installtion and usage instructions below for your own use.

Installation
============

The sources for the bisos.facter pip package is maintained at:
https://github.com/bisos-pip/facter.

The bisos.facter pip package is available at PYPI as
https://pypi.org/project/bisos.facter

You can install bisos.facter with pip or pipx.

With pip
--------

If you need access to bisos.facter as a python module, you can install
it with pip:

.. code:: bash

   pip install bisos.facter

With pipx
---------

If you only need access to bisos.facter on command-line, you can install
it with pipx:

.. code:: bash

   pipx install bisos.facter

The following commands are made available:

-  facter.cs
-  roInv-facter.cs
-  roPerf-facter.cs

These are all one file with 3 names. *roInv-facter.cs* and
*roPerf-facter.cs* are sym-links to *facter.cs*

Usage
=====

Locally (system command-line)
-----------------------------

``facter.cs`` does the equivalent of facter.

.. code:: bash

   bin/facter.cs

Remotely (as a service – Performer+Invoker)
-------------------------------------------

You can also run

Performer
~~~~~~~~~

Invoke performer as:

.. code:: bash

   bin/roPerf-facter.cs

Invoker
~~~~~~~

.. code:: bash

   bin/roInv-facter.cs

Use by python script
--------------------

bisos.facter Code Walkthrough
=============================

bisos.facter Source Code is in COMEEGA
--------------------------------------

bisos.facter can be used locally on command-line or remotely as a
service.

.. _take-from-120033commonengadopt:

TODO Take from 120033/common/engAdopt
-------------------------------------

./bin/facter.cs (./bin/roPerf-facter.cs ./bin/roInv-facter.cs)
--------------------------------------------------------------

A multi-unit

./bisos/facter/facter.py
------------------------

./bisos/facter/facter\ :sub:`csu`.py
------------------------------------

Documentation
=============

Part of ByStar Digital Ecosystem http://www.by-star.net.

This module's primary documentation is in
http://www.by-star.net/PLPC/180047

bisos.facter Blee-Panels
------------------------

bisos.facter Blee-Panles are in ./panels directory. From within Blee and
BISOS these panles are accessible under the Blee "Panels" menu.

Support
=======

| For support, criticism, comments and questions; please contact the
  author/maintainer
| `Mohsen Banan <http://mohsen.1.banan.byname.net>`__ at:
  http://mohsen.1.banan.byname.net/contact
