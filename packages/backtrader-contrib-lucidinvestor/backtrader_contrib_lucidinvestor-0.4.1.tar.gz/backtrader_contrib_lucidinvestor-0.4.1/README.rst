backtrader_contrib
==================

This is the repository for third-party contributions to ``backtrader`` maintained by LucidInvestor at
`LucidInvestor's public gitlab instance <https://gitlab.com/algorithmic-trading-library/>`__.

The package will scan ``.py`` file inside the corresponding subpackages (like
``analyzers``, ``indicators``, etc) and will import the classes which are
subclasses of the corresponding subpackages (``Analyzer``, ``Indicator``)

Errors will be silently ignored.

Successfully imported elements will be added to the corresponding subpackage of
``backtrader``, i.e. anything inside ``backtrader_contrib.indicators`` will be
monkey-patched (added) to ``backtrader.indicators``

The package will auto-replace itself and return ``backtrader``

Third-party Trading Framework
#############################

LucidInvestor
-------------
The LucidInvestor platform framework has been contributed in
`backtrader_contrib/framework/lucid/README.rst </backtrader_contrib/framework/lucid/README.rst>`__.
LUCID follows an open-core business model, contributing to Backtrader while enhancing it with proprietary add-ons
bundled in a commercial Software-as-a-Service offering at https://lucidinvestor.ca/.

Installation
============

Use pip::

   pip install backtrader_contrib-lucidinvestor

Usage
=====

As simple as::

  import backtrader_contrib as bt

And carry on using ``bt`` as if you had directly imported *backtrader*

Contribute
==========

Pull Requests can be accepted with the following LICENSES:

  - GPLv3
  - MIT
  - BSD 3-Clause
  - Apache 2.0

Tickets
#######

The ticket system is available at
`LucidInvestor's public gitlab instance <https://gitlab.com/algorithmic-trading-library/backtrader_contrib/-/issues>`__.

credits
#######

- original author: Daniel Rodriguez (danjrod@gmail.com)
- original unmaintained github: https://github.com/mementum/backtrader
- alternative unmaintained github: https://github.com/backtrader2/backtrader

