========================================
bisos.qmail: Python Command-Services for
========================================

.. contents::
   :depth: 3
..

Overview
========

bisos.qmail is a python package that uses the PyCS-Framework for NOTYET.
It is a BISOS-Capability and a Standalone-BISOS-Package.

*bisos.qmail* is based on PyCS-Foundation and can be used both as a
Command and as a Service (invoke/perform model of remote operations)
using RPYC for central management of multiple systems.

.. _table-of-contents:

Table of Contents TOC
=====================

-  `Overview <#overview>`__
-  `Part of BISOS — ByStar Internet Services Operating
   System <#part-of-bisos-----bystar-internet-services-operating-system>`__
-  `bisos.qmail is a Command Services (PyCS)
   Facility <#bisosqmail-is-a-command-services-pycs-facility>`__
-  `Uses of bisos.qmail <#uses-of-bisosqmail>`__
-  `bisos.qmail as a Standalone Piece of
   BISOS <#bisosqmail-as-a-standalone-piece-of-bisos>`__
-  `Installation <#installation>`__

   -  `Installation With pip <#installation-with-pip>`__
   -  `Installation With pipx <#installation-with-pipx>`__

-  `Usage <#usage>`__

   -  `Locally (system command-line) <#locally-system-command-line>`__
   -  `Remotely (as a service –
      Performer+Invoker) <#remotely-as-a-service----performerinvoker>`__
   -  `Use by Python script <#use-by-python-script>`__

-  `Documentation and Blee-Panels <#documentation-and-blee-panels>`__

   -  `bisos.qmail Blee-Panels <#bisosqmail-blee-panels>`__

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

*bisos.qmail* is part of BISOS.

bisos.qmail is a Command Services (PyCS) Facility
=================================================

bisos.qmail can be used locally on command-line or remotely as a
service. bisos.qmail is a PyCS multi-unit command-service. PyCS is a
framework that converges developement of CLI and Services. PyCS is an
alternative to FastAPI, Typer and Click.

bisos.qmail uses the PyCS Framework to:

#. Provide access to qmail facilities through native python.
#. Provide local access to qmail facilities on CLI.
#. Provide remote access to qmail facilities through remote invocation
   of python Expection Complete Operations using
   `rpyc <https://github.com/tomerfiliba-org/rpyc>`__.
#. Provide remote access to qmail facilities on CLI.

What is unique in the PyCS-Framework is that these four models are all a
single abstraction.

The core of PyCS-Framework is the *bisos.b* package (the
PyCS-Foundation). See https://github.com/bisos-pip/b for an overview.

Uses of bisos.qmail
===================

Within BISOS, bisos.qmail is used as a common facility.

bisos.qmail as a Standalone Piece of BISOS
==========================================

bisos.qmail is a standalone piece of BISOS. It can be used as a
self-contained Python package separate from BISOS. Follow the
installtion and usage instructions below for your own use.

Installation
============

The sources for the bisos.qmail pip package is maintained at:
https://github.com/bisos-pip/qmail.

The bisos.qmail pip package is available at PYPI as
https://pypi.org/project/bisos.qmail

You can install bisos.qmail with pip or pipx.

Installation With pip
---------------------

If you need access to bisos.qmail as a python module, you can install it
with pip:

.. code:: bash

   pip install bisos.qmail

Installation With pipx
----------------------

If you only need access to bisos.qmail as a command on command-line, you
can install it with pipx:

.. code:: bash

   pipx install bisos.qmail

The following commands are made available:

-  qmail.cs
-  roInv-qmail.cs
-  roPerf-qmail.cs

These are all one file with 3 names. *roInv-qmail.cs* and
*roPerf-qmail.cs* are sym-links to *qmail.cs*

Usage
=====

Locally (system command-line)
-----------------------------

``qmail.cs`` can be invoked directly as

.. code:: bash

   bin/qmail.cs

Remotely (as a service – Performer+Invoker)
-------------------------------------------

You can also run

Performer
~~~~~~~~~

Run performer as:

.. code:: bash

   bin/roPerf-qmail.cs

Invoker
~~~~~~~

Run invoker as:

.. code:: bash

   bin/roInv-qmail.cs

Use by Python script
--------------------

bisos.qmail Source Code is in writen in COMEEGA (Collaborative Org-Mode Enhanced Emacs Generalized Authorship) – https://github.com/bx-blee/comeega.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The primary API for bisos.qmail is ./bisos/qmail/qmail-csu.py. It is self documented in COMEEGA.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Documentation and Blee-Panels
=============================

bisos.qmail is part of ByStar Digital Ecosystem http://www.by-star.net.

This module's primary documentation is in the form of Blee-Panels.
Additional information is also available in:
http://www.by-star.net/PLPC/180047

bisos.qmail Blee-Panels
-----------------------

bisos.qmail Blee-Panles are in ./panels directory. From within Blee and
BISOS these panles are accessible under the Blee "Panels" menu.

Support
=======

| For support, criticism, comments and questions; please contact the
  author/maintainer
| `Mohsen Banan <http://mohsen.1.banan.byname.net>`__ at:
  http://mohsen.1.banan.byname.net/contact
