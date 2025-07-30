===============================================================================================
bisos.bx-bases: Python scripts (Command Services) used for bootstrapping the BISOS environment.
===============================================================================================

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

bx-bases: python scripts (Command Services) are used for bootstrapping
the BISOS (ByStar Internet Services OS) environment.

bx-pip and bx-bases are CS scripts that will normally be installed in
/usr/local/bin. bx-bases then can create /bisos and that allows for
bx-pip to thereafter to install into bystar instead of /usr/local/bin.

.. _table-of-contents:

Table of Contents TOC
=====================

-  `Overview <#overview>`__
-  `About BISOS — ByStar Internet Services Operating
   System <#about-bisos-----bystar-internet-services-operating-system>`__
-  `Uses of bisos.bx-bases <#uses-of-bisosbx-bases>`__
-  `Installation <#installation>`__

   -  `With pip <#with-pip>`__
   -  `With pipx <#with-pipx>`__

-  `Usage <#usage>`__

   -  `Locally (system command-line) <#locally-system-command-line>`__

-  `Documentation <#documentation>`__

   -  `bisos.bx-bases Blee-Panels <#bisosbx-bases-blee-panels>`__

-  `Support <#support>`__

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

Uses of bisos.bx-bases
======================

Within BISOS, the installation process uses bx-bases.

Installation
============

The sources for the bisos.facter pip package is maintained at:
https://github.com/bisos-pip/bx-bases.

The bisos.bx-bases pip package is available at PYPI as
https://pypi.org/project/bisos.bx-bases

You can install bisos.bx-bases with pip or pipx.

With pip
--------

If you need access to bisos.facter as a python module, you can install
it with pip:

.. code:: bash

   pip install bisos.bx-bases

With pipx
---------

If you only need access to bisos.facter on command-line, you can install
it with pipx:

.. code:: bash

   pipx install bisos.bx-bases

The following commands are made available:

-  bx-bases

Usage
=====

Locally (system command-line)
-----------------------------

.. code:: bash

   bin/bx-bases

Documentation
=============

Part of ByStar Digital Ecosystem http://www.by-star.net.

This module's primary documentation is in
http://www.by-star.net/PLPC/180047

bisos.bx-bases Blee-Panels
--------------------------

bisos.bx-bases Blee-Panles are in ./panels directory. From within Blee
and BISOS these panles are accessible under the Blee "Panels" menu.

Support
=======

| For support, criticism, comments and questions; please contact the
  author/maintainer
| `Mohsen Banan <http://mohsen.1.banan.byname.net>`__ at:
  http://mohsen.1.banan.byname.net/contact
