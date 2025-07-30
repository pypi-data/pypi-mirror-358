============================================================================================================================
bisos.bxoGitlab: Python Command-Services for managing GIT repositories of BPO (BISOS Portable Objects) using the gitlab API.
============================================================================================================================

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

bisos.bxoGitlab is a python package that uses the PyCS-Framework for
managing GIT repositories of BPO (BISOS Portable Objects).
bisos.bxoGitlab is layered on top of python-gitlab API.

It is a BISOS-Capability and a Standalone-BISOS-Package.

*bisos.bxoGitlab* is based on PyCS-Foundation and can be used both as a
Command and as a Service (invoke/perform model of remote operations)
using RPYC for central management of multiple systems.

.. _table-of-contents:

Table of Contents TOC
=====================

-  `Overview <#overview>`__
-  `About BISOS — ByStar Internet Services Operating
   System <#about-bisos-----bystar-internet-services-operating-system>`__
-  `bisos.bxoGitlab is a Command-Services (PyCS)
   Facility <#bisosbxogitlab-is-a-command-services-pycs-facility>`__
-  `Uses of bisos.bxoGitlab <#uses-of-bisosbxogitlab>`__
-  `bisos.bxoGitlab as a Standalone Piece of
   BISOS <#bisosbxogitlab-as-a-standalone-piece-of-bisos>`__
-  `Installation <#installation>`__

   -  `With pip <#with-pip>`__
   -  `With pipx <#with-pipx>`__

-  `Usage <#usage>`__

   -  `Locally (system command-line) <#locally-system-command-line>`__
   -  `Remotely (as a service –
      Performer+Invoker) <#remotely-as-a-service----performerinvoker>`__

      -  `Performer <#performer>`__
      -  `Invoker <#invoker>`__

   -  `Use by Python script <#use-by-python-script>`__

      -  `bisos.bxoGitlab Source Code is in writen in COMEEGA
         (Collaborative Org-Mode Enhanced Emacs Generalized Authorship)
         – <#bisosbxogitlab-source-code-is-in-writen-in-comeega-collaborative-org-mode-enhanced-emacs-generalized-authorship----httpsgithubcombx-bleecomeega>`__\ https://github.com/bx-blee/comeega\ `. <#bisosbxogitlab-source-code-is-in-writen-in-comeega-collaborative-org-mode-enhanced-emacs-generalized-authorship----httpsgithubcombx-bleecomeega>`__
      -  `See
         ./bisos/bxoGitlab/bxoGitlab-csu.py <#see-bisosbxogitlabbxogitlab-csupy>`__

-  `Documentation and Blee-Panels <#documentation-and-blee-panels>`__

   -  `bisos.bxoGitlab Blee-Panels <#bisosbxogitlab-blee-panels>`__

-  `Support <#support>`__

About BISOS — ByStar Internet Services Operating System
=======================================================

Layered on top of Debian, **BISOS**: (By\* Internet Services Operating
System) is a unified and universal framework for developing both
internet services and software-service continuums that use internet
services. See `Bootstrapping ByStar, BISOS and
Blee <https://github.com/bxGenesis/start>`__ for information about
getting started with BISOS.

bisos.bxoGitlab/ is a small piece of a much bigger picture. **BISOS** is
a foundation for **The Libre-Halaal ByStar Digital Ecosystem** which is
described as a cure for losses of autonomy and privacy that we are
experiencing in a book titled: `Nature of
Polyexistentials <https://github.com/bxplpc/120033>`__

bisos.bxoGitlab is a Command-Services (PyCS) Facility
=====================================================

bisos.bxoGitlab can be used locally on command-line or remotely as a
service. bisos.bxoGitlab is a PyCS multi-unit command-service. PyCS is a
framework that converges developement of CLI and Services. PyCS is an
alternative to FastAPI, Typer and Click.

bisos.bxoGitlab uses the PyCS Framework to:

#. Provide access to bxoGitlab facilities through native python.
#. Provide local access to bxoGitlab facilities on CLI
#. Provide remote access to bxoGitlab facilities through remote
   invocation of python Expection Complete Operations using
   `rpyc <https://github.com/tomerfiliba-org/rpyc>`__.
#. Provide remote access to bxoGitlab facilities on CLI

What is unique in the PyCS Framework is that these four models are all a
single abstraction.

Uses of bisos.bxoGitlab
=======================

Within BISOS, bisos.bxoGitlab is used as a common facility.

bisos.bxoGitlab as a Standalone Piece of BISOS
==============================================

bisos.bxoGitlab is a standalone piece of BISOS. It can be used as a
self-contained Python package separate from BISOS. Follow the
installtion and usage instructions below for your own use.

Installation
============

The sources for the bisos.bxoGitlab pip package is maintained at:
https://github.com/bisos-pip/bxoGitlab.

The bisos.bxoGitlab pip package is available at PYPI as
https://pypi.org/project/bisos.bxoGitlab

You can install bisos.bxoGitlab with pip or pipx.

With pip
--------

If you need access to bisos.bxoGitlab as a python module, you can
install it with pip:

.. code:: bash

   pip install bisos.bxoGitlab

With pipx
---------

If you only need access to bisos.bxoGitlab as a command on command-line,
you can install it with pipx:

.. code:: bash

   pipx install bisos.bxoGitlab

The following commands are made available:

-  bxoGitlab.cs

Usage
=====

Locally (system command-line)
-----------------------------

``bxoGitlab.cs`` can be invoked directly as

.. code:: bash

   bin/bxoGitlab.cs

Remotely (as a service – Performer+Invoker)
-------------------------------------------

You can also run:

Performer
~~~~~~~~~

Run performer as:

.. code:: bash

   bin/roPerf-bxoGitlab.cs

Invoker
~~~~~~~

Run invoker as:

.. code:: bash

   bin/roInv-bxoGitlab.cs

Use by Python script
--------------------

bisos.bxoGitlab Source Code is in writen in COMEEGA (Collaborative Org-Mode Enhanced Emacs Generalized Authorship) – https://github.com/bx-blee/comeega.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See ./bisos/bxoGitlab/bxoGitlab-csu.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Documentation and Blee-Panels
=============================

Part of ByStar Digital Ecosystem http://www.by-star.net.

This module's primary documentation is in the form of Blee-Panels.
Additional information is also available in:
http://www.by-star.net/PLPC/180047

bisos.bxoGitlab Blee-Panels
---------------------------

bisos.bxoGitlab Blee-Panles are in ./panels directory. From within Blee
and BISOS these panles are accessible under the Blee "Panels" menu.

Support
=======

| For support, criticism, comments and questions; please contact the
  author/maintainer
| `Mohsen Banan <http://mohsen.1.banan.byname.net>`__ at:
  http://mohsen.1.banan.byname.net/contact
