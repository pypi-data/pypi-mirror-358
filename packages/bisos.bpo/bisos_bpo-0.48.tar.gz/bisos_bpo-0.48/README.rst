=================================
bisos.bpo: BISOS Portable Objects
=================================

.. contents::
   :depth: 3
..

Overview
========

\*bisos.bpo (**BISOS Portable Objects**) is a python package which
abstracts Git based portable objects.

bisos.bpo is part of PyCS-BISOS-Framework. BISOS is part of ByStar
*(By*)*.

The **Libre-Halaal ByStar Digital Ecosystem** (*By\* DE*) is an
interdisciplinary, and ethics-oriented non-proprietary digital ecosystem
which challenges the existing proprietary American digital ecosystem
while operating concurrently alongside it. On a global scale, By\*
provide Internet Application Services which preserve autonomy and
privacy of the individual. **BISOS**: (*By\* Internet Services Operating
System*) layered on top of Debian, is a unified and universal framework
for developing both internet services and software-service continuums
that use internet services. BISOS is a layer on top of Debian. **Blee**:
(*BISOS Libre-Halaal Emacs Environment*) is a layer on top of Emacs and
BISOS, which creates a comprehensive integrated usage and development
environment. Blee and BISOS are fully integrated. See the "**Nature of
Polyexistentials**" book for the bigger picture of how all of ByStar
fits together.

For bootstraping BISOS, Blee and ByStar; you can start at:
https://github.com/bxgenesis/start

.. _table-of-contents:

Table of Contents TOC
=====================

-  `Overview <#overview>`__
-  `BISOS Portable Objects (BPO) <#bisos-portable-objects-bpo>`__
-  `Installation <#installation>`__

   -  `With pip <#with-pip>`__
   -  `With pipx <#with-pipx>`__

-  `Usage <#usage>`__

   -  `Locally (system command-line) <#locally-system-command-line>`__
   -  `Remotely (as a service) <#remotely-as-a-service>`__

-  `Support <#support>`__
-  `Documentation <#documentation>`__

BISOS Portable Objects (BPO)
============================

 [sec:BISOSPortableObjects(BPO)]

A fundamental abstraction of BISOS is the concept of BISOS Portable
Objects (BPO). BPOs are packages of information. There are some
similarities between BPOs as packages of information and software
packages such as deb-packages or rpm-packages.

Like software packages, BPOs are named uniquely and can depend on each
other and can be collectively installed and uninstalled. BPOs are used
for many things similar to how the files system is used for many things.
BPOs can be used to hold the complete configuration information of a
system. BPOs can be used to hold configuration information for software
packages. BPOs can be used to hold private user data. BPOs can be used
to hold collections of content and source code.

For its own operation, BISOS uses various BPO types. Other types of BPOs
can be created or generic BPO types (for example the Project type) can
be used.

Each BPO consists of a number of Git Repositories (hereafter called
"repos"). Each of the BPO's repos can be synchronized using generic Git
tools. With Blee/Emacs we use MaGit exclusively.

Scope of access and use of BPOs can be private, group, public or system
oriented.

BPOs can be private, residing entirely in the Inner Rims, and used for
private exclusive use of their owners. Private BPOs are used by their
owners for a variety of purposes. For example, one's address book
(rolodex) can be captured in a private BPO. This allows for
synchronization of the address book as a git based portable object
across different devices and across different environments.

BPOs can be used to facilitate collaboration among groups of autonomous
users. Group BPOs are only accessible to you, and people you explicitly
share access with. Group BPOs are functionally similar to GitHub private
repositories — but in a decentralized fashion instead of GitHub's
central model.

Public BPOs facilitate publication of content and public evolution of
that content through git. Public BPOs are functionally similar to GitHub
public repositories — but in a decentralized fashion instead of GitHub's
central model.

System BPOs are BISOS specific information that contain system related
information. System BPOs can be "materialized" and function as Virtual
Machines and Services and PALS (Possession Assertable Libre Services).
System BPOs can be used to capture System configurations and SBOMs
(Software Bill Of Material). System BPOs can be private or public.

BPOs are currently implemented as Gitlab accounts. Gitlab accounts are
Unix non-login shell accounts. BISOS's interactions with Gitlab is
exclusively through an API (Remote Operations). Each Gitlab account then
can contain repos subject to common access control mechanisms. Gitlab
accounts map to BPO-Identifiers (BPO-Id). Each BPO-id then maps to Unix
non-login shell accounts. The Unix account then becomes the base for
cloning of the repos in the corresponding Gitlab account.

BPOs go through different states and stages. A "Registered" BPO reserves
a particular name/number for that BPO. "Realization" of a BPO results in
creation of the git account that holds the repositories of that BPO and
its subsequent activation. "Activation" of the BPO results in creation
of a non-login account on the system and cloning of the repositories of
that BPO. Activated BPOs can then be kept in sync through Git. An
activated System BPO can then be "Materialized". Materialization of a
System BPO results in creation of BISOS entities.

Combinations of profiled deb-packages for internet application services
and their configurations in the form of BPOs can then create Libre
Services that are possession assertable, portable and transferable.

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

Remotely (as a service)
-----------------------

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

Support
=======

| For support, criticism, comments and questions; please contact the
  author/maintainer
| `Mohsen Banan <http://mohsen.1.banan.byname.net>`__ at:
  http://mohsen.1.banan.byname.net/contact

Documentation
=============

Part of ByStar Digital Ecosystem http://www.by-star.net.

This module's primary documentation is in
http://www.by-star.net/PLPC/180047
