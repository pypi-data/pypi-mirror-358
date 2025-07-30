====================================================================
bisos.cntnr: Python Command-Services forBISOS Container Abstractions
====================================================================

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

bisos.cntnr is a python package that uses the PyCS-Framework for BISOS
Container Abstractions. It is a BISOS-Capability and a
Standalone-BISOS-Package.

*bisos.cntnr* is based on PyCS-Foundation and can be used both as a
Command and as a Service (invoke/perform model of remote operations)
using RPYC for central management of multiple systems.

.. _table-of-contents:

Table of Contents TOC
=====================

-  `Overview <#overview>`__
-  `About BISOS — ByStar Internet Services Operating
   System <#about-bisos-----bystar-internet-services-operating-system>`__
-  `bisos.cntnr is a Command Services (PyCS)
   Facility <#bisoscntnr-is-a-command-services-pycs-facility>`__
-  `Uses of bisos.cntnr <#uses-of-bisoscntnr>`__
-  `bisos.cntnr as a Standalone Piece of
   BISOS <#bisoscntnr-as-a-standalone-piece-of-bisos>`__
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

      -  `bisos.cntnr Source Code is in writen in COMEEGA (Collaborative
         Org-Mode Enhanced Emacs Generalized Authorship)
         – <#bisoscntnr-source-code-is-in-writen-in-comeega-collaborative-org-mode-enhanced-emacs-generalized-authorship----httpsgithubcombx-bleecomeega>`__\ https://github.com/bx-blee/comeega\ `. <#bisoscntnr-source-code-is-in-writen-in-comeega-collaborative-org-mode-enhanced-emacs-generalized-authorship----httpsgithubcombx-bleecomeega>`__
      -  `The primary API for bisos.cntnr is ./bisos/cntnr/cntnr-csu.py.
         It is self documented in
         COMEEGA. <#the-primary-api-for-bisoscntnr-is-bisoscntnrcntnr-csupy-it-is-self-documented-in-comeega>`__

-  `Documentation and Blee-Panels <#documentation-and-blee-panels>`__

   -  `bisos.cntnr Blee-Panels <#bisoscntnr-blee-panels>`__

-  `Support <#support>`__

About BISOS — ByStar Internet Services Operating System
=======================================================

Layered on top of Debian, **BISOS**: (By\* Internet Services Operating
System) is a unified and universal framework for developing both
internet services and software-service continuums that use internet
services. See `Bootstrapping ByStar, BISOS and
Blee <https://github.com/bxGenesis/start>`__ for information about
getting started with BISOS.

*bisos.cntnr* as a PyCS facility is a small piece of a much bigger
picture. **BISOS** is a foundation for **The Libre-Halaal ByStar Digital
Ecosystem** which is described as a cure for losses of autonomy and
privacy that we are experiencing in a book titled: `Nature of
Polyexistentials <https://github.com/bxplpc/120033>`__

bisos.cntnr is a Command Services (PyCS) Facility
=================================================

bisos.cntnr can be used locally on command-line or remotely as a
service. bisos.cntnr is a PyCS multi-unit command-service. PyCS is a
framework that converges developement of CLI and Services. PyCS is an
alternative to FastAPI, Typer and Click.

bisos.cntnr uses the PyCS Framework to:

#. Provide access to cntnr facilities through native python.
#. Provide local access to cntnr facilities on CLI.
#. Provide remote access to cntnr facilities through remote invocation
   of python Expection Complete Operations using
   `rpyc <https://github.com/tomerfiliba-org/rpyc>`__.
#. Provide remote access to cntnr facilities on CLI.

What is unique in the PyCS-Framework is that these four models are all a
single abstraction.

The core of PyCS-Framework is the *bisos.b* package (the
PyCS-Foundation). See https://github.com/bisos-pip/b for an overview.

Uses of bisos.cntnr
===================

Within BISOS, bisos.cntnr is used as a common facility.

bisos.cntnr as a Standalone Piece of BISOS
==========================================

bisos.cntnr is a standalone piece of BISOS. It can be used as a
self-contained Python package separate from BISOS. Follow the
installtion and usage instructions below for your own use.

Installation
============

The sources for the bisos.cntnr pip package is maintained at:
https://github.com/bisos-pip/cntnr.

The bisos.cntnr pip package is available at PYPI as
https://pypi.org/project/bisos.cntnr

You can install bisos.cntnr with pip or pipx.

With pip
--------

If you need access to bisos.cntnr as a python module, you can install it
with pip:

.. code:: bash

   pip install bisos.cntnr

With pipx
---------

If you only need access to bisos.cntnr as a command on command-line, you
can install it with pipx:

.. code:: bash

   pipx install bisos.cntnr

The following commands are made available:

-  cntnr.cs
-  roInv-cntnr.cs
-  roPerf-cntnr.cs

These are all one file with 3 names. *roInv-cntnr.cs* and
*roPerf-cntnr.cs* are sym-links to *cntnr.cs*

Usage
=====

Locally (system command-line)
-----------------------------

``cntnr.cs`` can be invoked directly as

.. code:: bash

   bin/cntnr.cs

Remotely (as a service – Performer+Invoker)
-------------------------------------------

You can also run

Performer
~~~~~~~~~

Run performer as:

.. code:: bash

   bin/roPerf-cntnr.cs

Invoker
~~~~~~~

Run invoker as:

.. code:: bash

   bin/roInv-cntnr.cs

Use by Python script
--------------------

bisos.cntnr Source Code is in writen in COMEEGA (Collaborative Org-Mode Enhanced Emacs Generalized Authorship) – https://github.com/bx-blee/comeega.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The primary API for bisos.cntnr is ./bisos/cntnr/cntnr-csu.py. It is self documented in COMEEGA.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Documentation and Blee-Panels
=============================

bisos.cntnr is part of ByStar Digital Ecosystem http://www.by-star.net.

This module's primary documentation is in the form of Blee-Panels.
Additional information is also available in:
http://www.by-star.net/PLPC/180047

bisos.cntnr Blee-Panels
-----------------------

bisos.cntnr Blee-Panles are in ./panels directory. From within Blee and
BISOS these panles are accessible under the Blee "Panels" menu.

Support
=======

| For support, criticism, comments and questions; please contact the
  author/maintainer
| `Mohsen Banan <http://mohsen.1.banan.byname.net>`__ at:
  http://mohsen.1.banan.byname.net/contact
