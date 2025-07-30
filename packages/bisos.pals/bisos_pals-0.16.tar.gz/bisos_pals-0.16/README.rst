================================================
bisos.bals: Possession Assertible Libre Services
================================================

.. contents::
   :depth: 3
..

Overview
========

\*bisos.pals (**Possession Assertible Libre Services**) is a python
package which is used to manage abstrations of ByStar Autonomy
Assertable Internet Services BPOs

bisos.pals is part of PyCS-BISOS-Framework. BISOS is part of ByStar
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
-  `BISOS Possession Assertable Libre Services
   (PALS) <#bisos-possession-assertable-libre-services-pals>`__
-  `Installation <#installation>`__

   -  `With pip <#with-pip>`__
   -  `With pipx <#with-pipx>`__

-  `Usage <#usage>`__

   -  `Locally (system command-line) <#locally-system-command-line>`__
   -  `Remotely (as a service) <#remotely-as-a-service>`__

-  `Support <#support>`__
-  `Documentation <#documentation>`__

BISOS Possession Assertable Libre Services (PALS)
=================================================

Based on capabilities of BPOs and the capabilities of service-side
profiled Debian packages, we can now create Libre Services.

BISOS Libre Services can be thought of four parts:

#. Libre-Halaal software of the services (usually a Debian Package)

#. Configuration information for the software for the service (often as
   a repo of a PALS-BPO)

#. Names and numbers for binding of services (as a repo of a PAAI-BPO)

#. Service owner data (in the form of one or more BPOs)

This model provides for portability and transferability of Libre
Services between network abodes. For example, a Libre Service at a
provider can be transferred to its owner to be self-hosted.

There are some similarities between PALS-BPO and container
virtualization (Docker and Kubernetes). PALS-BPOs include comprehensive
information for construction of services and these can be mapped to
container virtualization. However, at this time BISOS does not use
container virtualization, as it is redundant. BISOS uses BPOs to create
and recreate Kernel-based Virtual Machines (KVM) inside of which
PALS-BPOs are deployed.

Self-hosting is the practice of running and maintaining a Libre Service
under one's own full control at one's own premise. BISOS Possession
Assertable Libre Services (PALS) can be initially self-hosted and then
transferred to a Libre Service provider. PALS can also be initially
externally hosted and then become self-hosted on demand. The concept of
"transferability" between network abodes is well supported in BISOS.

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
