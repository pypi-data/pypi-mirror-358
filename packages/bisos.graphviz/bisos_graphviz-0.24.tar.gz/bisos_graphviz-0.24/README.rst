====================================
bisos.graphviz: Seeded-PyCS Graphviz
====================================

.. contents::
   :depth: 3
..

Overview
========

bisos.graphviz (Seeded-PyCS Graphviz) is Python graphviz wrapped into
BISOS Command-Services and Seed Machinaries.

bisos.graphviz is a python package that uses the PyCS-Framework
(`bisos.PyCS <https://github.com/bisos-pip/pycs>`__) for processing
graphviz specifications. It is a layer on top of Python Graphviz —
https://github.com/xflr6/graphviz — which provides a python interface to
the DOT language of the Graphviz graph drawing software. It is a
BISOS-Capability and a Standalone-BISOS-Package.

Package Documentation At Github
===============================

The information below is a subset of the full of documentation for this
bisos-pip package. More complete documentation is available at:
https://github.com/bisos-pip/graphviz-cs

Abstract – Concepts and Terminology
===================================

Referring to the figure below, inputs are on the top and outputs are at
the bottom.

Layerings
---------

The ellipses represent processing layers.

-  The **graphviz.org layer** takes DOT (graph description language)
   input and produces graphs is a variety of formats. Graphviz is open
   source graph visualization software hosted at
   https://www.graphviz.org/.

-  The **Python Graphviz layer** builds on the graphviz.org layer and
   provides an interface to dot facilities in python. Python Graphviz
   software is hosted at https://github.com/xflr6/graphviz.

-  The **Seeded-PyCS Graphviz layer** Seeded-PyCS Graphviz layer
   enhances the Python Graphviz layer by providing the ability to
   include multiple graphs in one file (packaging) and by providing the
   ability to produce any desired output format from the command-line.
   Seeded-PyCS Graphviz uses
   `bisos.PyCS <https://github.com/bisos-pip/pycs>`__. Seeded-PyCS
   Graphviz software is hosted at
   https://github.com/bisos-pip/graphviz-cs.

Named Graphs Input Files – package-graphviz.cs
----------------------------------------------

Input files containing graph specifications (the top layer in the figure
below) can reside anywhere in the file system and are typically named
package-graphviz.cs where package conveys a name for a grouping of graph
specifications. Execution of input files (say
`file:./examples/exmpl-graphviz.cs <./examples/exmpl-graphviz.cs>`__)
produces output in any or all of the output formats. The output format
can be any of pdf, svg, png, jpeg or gv format. Output in various
formats is shown as the bottom layer of the figure below.

Input files are structured as **Named Graphs**. Named Graphs have two
elements:

#. **Graph specification function**. A python named function that takes
   no arguments and returns a type **graphviz.Digraph** object.
#. **Name**. The name is used to produce output files and is commonly
   the name of function (1) as well.

The list of Named Graphs forms the **namedGraphsList** which becomes an
argument to the **graphvizSeed.setup** function.

The `file:./bin/exmpl-graphviz.cs <./bin/exmpl-graphviz.cs>`__ in the
bin directory can be used as a starting point and example. The examples
directory contains many other examples. The images directory contains
the input
(`file:./images/readme-graphviz.cs <./images/readme-graphviz.cs>`__)
that produced the figure below.

Concept of Seeded-PyCS Input Files
----------------------------------

PyCS (`bisos.PyCS <https://github.com/bisos-pip/pycs>`__) provides a
framework for creating python mapping functions to the command line
(similar to click).

Often it make good sense to package the input with its processing
capabilities in one place. We do this using the Seeded-PyCS design
pattern. Seeded-PyCS-Graphviz is such an example.

.. _table-of-contents:

Table of Contents TOC
=====================

-  `Overview <#overview>`__
-  `Package Documentation At
   Github <#package-documentation-at-github>`__
-  `Abstract – Concepts and
   Terminology <#abstract----concepts-and-terminology>`__

   -  `Layerings <#layerings>`__
   -  `Named Graphs Input Files –
      package-graphviz.cs <#named-graphs-input-files----package-graphvizcs>`__
   -  `Concept of Seeded-PyCS Input
      Files <#concept-of-seeded-pycs-input-files>`__

-  `A Hello World Example —
   hello-graphviz.cs <#a-hello-world-example-----hello-graphvizcs>`__
-  `Installation <#installation>`__

   -  `Installation With pip <#installation-with-pip>`__
   -  `Installation With pipx <#installation-with-pipx>`__

-  `Part of BISOS and ByStar — ByStar Internet Services Operating
   System <#part-of-bisos-and-bystar-----bystar-internet-services-operating-system>`__
-  `bisos.graphviz as a Standalone Piece of
   BISOS <#bisosgraphviz-as-a-standalone-piece-of-bisos>`__
-  `Documentation and Blee-Panels <#documentation-and-blee-panels>`__

   -  `bisos.graphviz Blee-Panels <#bisosgraphviz-blee-panels>`__

-  `Support <#support>`__

A Hello World Example — hello-graphviz.cs
=========================================

Below we shall walk through
`file:./examples/hello-graphviz.cs <./examples/hello-graphviz.cs>`__
which produces This is the equivalent of
https://github.com/xflr6/graphviz/blob/master/examples/hello.py which
produces https://graphviz.org/Gallery/directed/hello.html.

`file:./examples/hello-graphviz.cs <./examples/hello-graphviz.cs>`__ is
written in Python COMEEGA, which is Python augmented by Emacs org-mode.
In that file everything inside of +BEGIN +END is a dynamic block and
everything that is in +begin\ :sub:`org` +end\ :sub:`org` is in org-mode
syntax. For more information about COMEEGA (Collaborative Org-Mode
Enhanced Emacs Generalized Authorship) see
https://github.com/bx-blee/comeega. PyCS and BISOS are developed in
COMEEGA.

The code fragment below is in pure Python.

.. code:: python

   import graphviz

   from bisos.graphviz import graphvizSeed
   ng = graphvizSeed.namedGraph  # just an abbreviation

   def hello() -> graphviz.Digraph:

       g = graphviz.Digraph('G',)

       g.edge('Hello', 'World')

       return g

   namedGraphsList = [
       ng("hello", func=hello),
   ]

   graphvizSeed.setup(
       namedGraphsList=namedGraphsList,
   )

The **b:py3:cs:seed/withWhich :seedName "seedGraphviz.cs"** dynamic
block then results in the execution of the seed:

.. code:: python

   __file__ = os.path.abspath(seedPath)
   with open(__file__) as f:
       exec(compile(f.read(), __file__, 'exec'))

If you wanted to include multiple graphs in one input file, you would
just add them the **namedGraphsList**.

You can then just run:

.. code:: bash

   hello-graphviz.cs

Which produces a menu for production of desired formats.

or you can run:

.. code:: bash

   hello-graphviz.cs --format="all"  -i ngProcess all

Which produces output in all formats.

Installation
============

The sources for the bisos.graphviz pip package is maintained at:
https://github.com/bisos-pip/graphviz.

The bisos.graphviz pip package is available at PYPI as
https://pypi.org/project/bisos.graphviz

You can install bisos.graphviz with pip or pipx.

Installation With pip
---------------------

If you need access to bisos.graphviz as a python module, you can install
it with pip:

.. code:: bash

   pip install bisos.graphviz

Installation With pipx
----------------------

If you only need access to bisos.graphviz as a command on command-line,
you can install it with pipx:

.. code:: bash

   pipx install bisos.graphviz

The following commands are made available:

-  seedGraphviz.cs
-  exmpl-graphviz.cs

Part of BISOS and ByStar — ByStar Internet Services Operating System
====================================================================

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

*bisos.graphviz* is part of BISOS.

bisos.graphviz as a Standalone Piece of BISOS
=============================================

bisos.graphviz is a standalone piece of BISOS. It can be used as a
self-contained Python package separate from BISOS. Follow the
installation and usage instructions below for your own use.

Documentation and Blee-Panels
=============================

bisos.graphviz is part of ByStar Digital Ecosystem
http://www.by-star.net.

This module's primary documentation is in the form of Blee-Panels.
Additional information is also available in:
http://www.by-star.net/PLPC/180047

bisos.graphviz Blee-Panels
--------------------------

bisos.graphviz Blee-Panels are in ./panels directory. From within Blee
and BISOS these panels are accessible under the Blee "Panels" menu.

Support
=======

| For support, criticism, comments and questions; please contact the
  author/maintainer
| `Mohsen Banan <http://mohsen.1.banan.byname.net>`__ at:
  http://mohsen.1.banan.byname.net/contact
