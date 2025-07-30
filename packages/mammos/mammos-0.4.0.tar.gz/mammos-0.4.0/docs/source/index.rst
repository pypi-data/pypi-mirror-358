MaMMoS documentation
====================

.. toctree::
   :maxdepth: 1
   :hidden:

   examples/index
   api/index
   design
   changelog


Framework
---------

The MaMMoS framework provides software components for magnetic multiscale
modeling. The following table provides a short overview and contains links to
example and API reference for the individual components. The binder badges allow
running the examples for the individual packages interactively in the cloud.

.. list-table::
   :header-rows: 1

   * - Package repository
     - Examples
     - API
     - Interactive examples
   * - `mammos <https://github.com/mammos-project/mammos>`__
     - :doc:`examples/workflows/index`
     - –
     - .. image:: https://static.mybinder.org/badge_logo.svg
          :target: https://mybinder.org/v2/gh/mammos-project/mammos/main?urlpath=lab%2Ftree%2Fexamples
   * - `mammos-analysis <https://github.com/mammos-project/mammos-analysis>`__
     - :doc:`examples/mammos-analysis/index`
     - :doc:`api/mammos_analysis`
     - .. image:: https://static.mybinder.org/badge_logo.svg
          :target: https://mybinder.org/v2/gh/mammos-project/mammos-analysis/main?urlpath=lab%2Ftree%2Fexamples
   * - `mammos-dft <https://github.com/mammos-project/mammos-dft>`__
     - :doc:`examples/mammos-dft/index`
     - :doc:`api/mammos_dft`
     - .. image:: https://static.mybinder.org/badge_logo.svg
          :target: https://mybinder.org/v2/gh/mammos-project/mammos-dft/main?urlpath=lab%2Ftree%2Fexamples
   * - `mammos-entity <https://github.com/mammos-project/mammos-entity>`__
     - :doc:`examples/mammos-entity/index`
     - :doc:`api/mammos_entity`
     - .. image:: https://static.mybinder.org/badge_logo.svg
          :target: https://mybinder.org/v2/gh/mammos-project/mammos-entity/main?urlpath=lab%2Ftree%2Fexamples
   * - `mammos-mumag <https://github.com/mammos-project/mammos-mumag>`__
     - :doc:`examples/mammos-mumag/index`
     - :doc:`api/mammos_mumag`
     - .. image:: https://static.mybinder.org/badge_logo.svg
          :target: https://mybinder.org/v2/gh/mammos-project/mammos-mumag/main?urlpath=lab%2Ftree%2Fexamples
   * - `mammos-spindynamics <https://github.com/mammos-project/mammos-spindynamics>`__
     - :doc:`examples/mammos-spindynamics/index`
     - :doc:`api/mammos_spindynamics`
     - .. image:: https://static.mybinder.org/badge_logo.svg
          :target: https://mybinder.org/v2/gh/mammos-project/mammos-spindynamics/main?urlpath=lab%2Ftree%2Fexamples
   * - `mammos-units <https://github.com/mammos-project/mammos-units>`__
     - :doc:`examples/mammos-units/index`
     - :doc:`api/mammos_units`
     - .. image:: https://static.mybinder.org/badge_logo.svg
          :target: https://mybinder.org/v2/gh/mammos-project/mammos-units/main?urlpath=lab%2Ftree%2Fexamples

Additional tools
----------------

An overview of other tools created through or supported by the MaMMoS project is
available at https://mammos-project.github.io/#additional-tools.

Framework installation
----------------------

The MaMMoS framework consists of a collection of packages (see :doc:`design
<design>` for more details). The metapackage ``mammos`` can be used to install a
consistent set of these packages.

The package ``mammos-mumag`` depends on ``jax``. To get jax with GPU support you
will need to manually install ``jax`` with the required optional dependencies
matching your GPU hardware/software, e.g. for an NVIDIA GPU you may need to
install ``jax[cuda12]``. For details please refer to the `jax installation
instructions <https://docs.jax.dev/en/latest/installation.html>`__.

.. tab-set::

   .. tab-item:: pixi

      Requirements: ``pixi`` (https://pixi.sh/)

      Pixi will install Python and mammos.

      To conveniently work with the notebook tutorials we install
      ``jupyterlab``. (``packaging`` needs to be pinned due to a limitation of
      pixi/PyPI.):

      Some examples also require `esys-escript
      <https://github.com/LutzGross/esys-escript.github.io>`__. On linux we can
      install it from conda-forge. On Mac or Windows refer to the esys-escript
      installation instructions:

      - Linux:

        .. code:: shell

           pixi init
           pixi add python jupyterlab "packaging<25" "pandas<2.3" esys-escript
           pixi add mammos --pypi
           pixi add --pypi "jax[cuda12]"  # assuming an NVIDIA GPU with CUDA 12, see comment above

      - Mac/Windows:

        .. code:: shell

           pixi init
           pixi add python jupyterlab "packaging<25" "pandas<2.3"
           pixi add mammos --pypi
           pixi add --pypi "jax[cuda12]"  # assuming an NVIDIA GPU with CUDA 12, see comment above

      Finally start a shell where the installed packages are available:

      .. code:: shell

         pixi shell

   .. tab-item:: conda

      Requirements: ``conda`` (https://conda-forge.org/download/)

      Use ``conda`` in combination with ``pip`` to get packages from
      conda-forge and PyPI.

      To conveniently work with the notebook tutorials we install
      ``jupyterlab``. (``packaging`` needs to be pinned due to a dependency
      issue in ``mammos-entity``.)

      Some examples also require `esys-escript
      <https://github.com/LutzGross/esys-escript.github.io>`__. On linux we can
      install it from conda-forge. On Mac or Windows refer to the esys-escript
      installation instructions.

      .. code:: shell

         conda create -n mammos-environment python pip jupyterlab "packaging<25" "pandas<2.3" esys-escript
         conda activate mammos-environment
         pip install mammos
         pip install "jax[cuda12]"  # assuming an NVIDIA GPU with CUDA 12, see comment above

   .. tab-item:: pip

      Requirements: ``python>=3.11`` and ``pip``

      When using ``pip`` we recommend creating a virtual environment to isolate the MaMMoS installation.

      First, create a new virtual environment. Here, we choose the name
      ``mammos-venv``.

      .. code:: shell

         python3 -m venv mammos-venv

      To activate it, run

      - on MacOS/Linux

        .. code:: shell

          . mammos-venv/bin/activate

      - on Windows

        .. code:: shell

           mammos-venv/bin/activate.sh

      Finally install ``mammos`` from PyPI:

      .. code:: shell

        pip install mammos
        pip install "jax[cuda12]"  # assuming an NVIDIA GPU with CUDA 12, see comment above

      Some examples also require `esys-escript
      <https://github.com/LutzGross/esys-escript.github.io>`__, which must be
      installed separately. Please refer to the documentation of esys-escript
      for installation instructions.

Framework example notebooks
---------------------------

To conveniently download all example notebooks use the ``mammos-fetch-examples``
script, which is installed as part of the ``mammos`` package (:ref:`further
details <download-all-examples>`).


Acknowledgements
----------------

This software has been supported by the European Union’s Horizon Europe research and innovation programme under grant agreement No 101135546 `MaMMoS <https://mammos-project.github.io/>`__.
