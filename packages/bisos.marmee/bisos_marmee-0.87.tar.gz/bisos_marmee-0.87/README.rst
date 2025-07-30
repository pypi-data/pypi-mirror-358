===============================================================================================================================================================================================
bisos.marmee: Python Command-Services for MARMEE (Multi-Account Resident Mail Exchanger Envinronment) is a collection of CSs for maintaining multiple mail sending and host resident mailboxes.
===============================================================================================================================================================================================

.. contents::
   :depth: 3
..

Overview
========

bisos.marmee is a python package that uses the PyCS-Framework for
NOTYET. It is a BISOS-Capability and a Standalone-BISOS-Package.

*bisos.marmee* is based on PyCS-Foundation and can be used both as a
Command and as a Service (invoke/perform model of remote operations)
using RPYC for central management of multiple systems.

MARMEE is documented in: http://www.by-star.net/PLPC/180051

.. _table-of-contents:

Table of Contents TOC
=====================

-  `Overview <#overview>`__
-  `Part of BISOS — ByStar Internet Services Operating
   System <#part-of-bisos-----bystar-internet-services-operating-system>`__
-  `bisos.marmee is a Command Services (PyCS)
   Facility <#bisosmarmee-is-a-command-services-pycs-facility>`__
-  `Uses of bisos.marmee <#uses-of-bisosmarmee>`__
-  `bisos.marmee as a Standalone Piece of
   BISOS <#bisosmarmee-as-a-standalone-piece-of-bisos>`__
-  `Installation <#installation>`__

   -  `Installation With pip <#installation-with-pip>`__
   -  `Installation With pipx <#installation-with-pipx>`__

-  `Usage <#usage>`__

   -  `Locally (system command-line) <#locally-system-command-line>`__
   -  `Remotely (as a service –
      Performer+Invoker) <#remotely-as-a-service----performerinvoker>`__

      -  `Performer <#performer>`__
      -  `Invoker <#invoker>`__

   -  `Use by Python script <#use-by-python-script>`__

      -  `bisos.marmee Source Code is in writen in COMEEGA
         (Collaborative Org-Mode Enhanced Emacs Generalized Authorship)
         – <#bisosmarmee-source-code-is-in-writen-in-comeega-collaborative-org-mode-enhanced-emacs-generalized-authorship----httpsgithubcombx-bleecomeega>`__\ https://github.com/bx-blee/comeega\ `. <#bisosmarmee-source-code-is-in-writen-in-comeega-collaborative-org-mode-enhanced-emacs-generalized-authorship----httpsgithubcombx-bleecomeega>`__
      -  `The primary API for bisos.marmee is
         ./bisos/marmee/marmee-csu.py. It is self documented in
         COMEEGA. <#the-primary-api-for-bisosmarmee-is-bisosmarmeemarmee-csupy-it-is-self-documented-in-comeega>`__

-  `Documentation and Blee-Panels <#documentation-and-blee-panels>`__

   -  `bisos.marmee Blee-Panels <#bisosmarmee-blee-panels>`__

-  `Support <#support>`__

Part of BISOS — ByStar Internet Services Operating System
=========================================================

| Layered on top of Debian, **BISOS**: (By\* Internet Services Operating
  System) is a unified and universal framework for developing both
  internet services and software-service continuums that use internet
  services. See `Bootstrapping ByStar, BISOS and
  Blee <https://github.com/bxGenesis/start>`__ for information about
  getting started with BISOS.
| **BISOS** is a foundation for **The Libre-Halaal ByStar Digital
  Ecosystem** which is described as a cure for losses of autonomy and
  privacy in a book titled: `Nature of
  Polyexistentials <https://github.com/bxplpc/120033>`__

*bisos.marmee* is part of BISOS.

bisos.marmee is a Command Services (PyCS) Facility
==================================================

bisos.marmee can be used locally on command-line or remotely as a
service. bisos.marmee is a PyCS multi-unit command-service. PyCS is a
framework that converges developement of CLI and Services. PyCS is an
alternative to FastAPI, Typer and Click.

bisos.marmee uses the PyCS Framework to:

#. Provide access to marmee facilities through native python.
#. Provide local access to marmee facilities on CLI.
#. Provide remote access to marmee facilities through remote invocation
   of python Expection Complete Operations using
   `rpyc <https://github.com/tomerfiliba-org/rpyc>`__.
#. Provide remote access to marmee facilities on CLI.

What is unique in the PyCS-Framework is that these four models are all a
single abstraction.

The core of PyCS-Framework is the *bisos.b* package (the
PyCS-Foundation). See https://github.com/bisos-pip/b for an overview.

Uses of bisos.marmee
====================

Within BISOS, bisos.marmee is used as a common facility.

bisos.marmee as a Standalone Piece of BISOS
===========================================

bisos.marmee is a standalone piece of BISOS. It can be used as a
self-contained Python package separate from BISOS. Follow the
installtion and usage instructions below for your own use.

Installation
============

The sources for the bisos.marmee pip package is maintained at:
https://github.com/bisos-pip/marmee.

The bisos.marmee pip package is available at PYPI as
https://pypi.org/project/bisos.marmee

You can install bisos.marmee with pip or pipx.

Installation With pip
---------------------

If you need access to bisos.marmee as a python module, you can install
it with pip:

.. code:: bash

   pip install bisos.marmee

Installation With pipx
----------------------

If you only need access to bisos.marmee as a command on command-line,
you can install it with pipx:

.. code:: bash

   pipx install bisos.marmee

The following commands are made available:

-  marmee.cs
-  roInv-marmee.cs
-  roPerf-marmee.cs

These are all one file with 3 names. *roInv-marmee.cs* and
*roPerf-marmee.cs* are sym-links to *marmee.cs*

Usage
=====

Locally (system command-line)
-----------------------------

``marmee.cs`` can be invoked directly as

.. code:: bash

   bin/marmee.cs

Remotely (as a service – Performer+Invoker)
-------------------------------------------

You can also run

Performer
~~~~~~~~~

Run performer as:

.. code:: bash

   bin/roPerf-marmee.cs

Invoker
~~~~~~~

Run invoker as:

.. code:: bash

   bin/roInv-marmee.cs

Use by Python script
--------------------

bisos.marmee Source Code is in writen in COMEEGA (Collaborative Org-Mode Enhanced Emacs Generalized Authorship) – https://github.com/bx-blee/comeega.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The primary API for bisos.marmee is ./bisos/marmee/marmee-csu.py. It is self documented in COMEEGA.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Documentation and Blee-Panels
=============================

bisos.marmee is part of ByStar Digital Ecosystem http://www.by-star.net.

This module's primary documentation is in the form of Blee-Panels.
Additional information is also available in:
http://www.by-star.net/PLPC/180047

bisos.marmee Blee-Panels
------------------------

bisos.marmee Blee-Panles are in ./panels directory. From within Blee and
BISOS these panles are accessible under the Blee "Panels" menu.

Support
=======

| For support, criticism, comments and questions; please contact the
  author/maintainer
| `Mohsen Banan <http://mohsen.1.banan.byname.net>`__ at:
  http://mohsen.1.banan.byname.net/contact
