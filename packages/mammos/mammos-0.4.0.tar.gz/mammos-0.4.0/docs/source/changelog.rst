=========
Changelog
=========

The format follows `Keep a Changelog <https://keepachangelog.com/>`__. Versions
follow `semantic versioning <https://semver.org/>`__, the metapackage version is
updated according to the largest bump of any of the dependent packages.

0.4.0 -- 2025-06-27
===================

Changed
-------

``mammos-entity``
  - The ``Entity`` class is no longer a subclass of ``mammos_units.Quantity``.
    As a consequence it does no longer support mathematical operations. Use the
    attribute ``.quantity`` (or the short-hand ``.q``) to access the underlying
    quantity and to perform (mathematical) operations. (`PR28
    <https://github.com/MaMMoS-project/mammos-entity/pull/28>`__)
  - The package now comes with a bundled ontology consisting of `EMMO
    <https://github.com/emmo-repo/EMMO>`__ (version 1.0.0-rc3) and `Magnetic
    Material <https://github.com/MaMMoS-project/MagneticMaterialsOntology>`__
    (version 0.0.3). Internet access is no longer required. (`PR33
    <https://github.com/MaMMoS-project/mammos-entity/pull/33>`__)
``mammos``
  - Use Fe16N2 instead of Nd2Fe14B in hard magnet workflow. (`PR17
    <https://github.com/MaMMoS-project/mammos/pull/17>`__)

0.3.0 -- 2025-06-11
===================

Added
-----

``mammos-entity``
  - New predefined entity ``mammos_entity.J``
  - New predefined entity ``mammos_entity.Js``
``mammos-mumag``
  - Optional argument ``plotter`` in ``plot_configuration`` to add a vector plot
    of a magnetization configuration to a :py:class:`pyvista.Plotter` provided
    by the caller.

Changed
-------

``mammos-entity``
  - Return a ``mammos_units.UnitConversionError`` (inherited from
    ``astropy.units``) when trying initialize an entity with incompatible units.

0.2.0 -- 2025-06-06
===================

Added
-----

``mammos``
  - Command-line script ``mammos-fetch-examples`` to download all example
    notebooks.
``mammos-entity``
  - Entity objects have ``ontology_label_with_iri`` attribute.

Changed
-------

``mammos-entity``
  - When trying to initialize an entity with a wrong unit the error message does
    now show the required unit defined in the ontology.

Fixed
-----

``mammos-entity``
  - ``Entity.to`` did not return a new entity in the requested units and instead
    used the default entity units.
  - ``Entity.axis_label``: unit inside parentheses instead of brackets.

0.1.0 -- 2025-06-05
===================

Added
-----

``mammos`` -- 0.1.0
  - Workflows for hard magnets and sensor shape optimization.
  - Ensures compatible software components are installed.
``mammos-analysis`` -- 0.1.0
  - Calculation of macroscopic properties (Mr, Hc, BHmax) from a hysteresis
    loop.
  - Fitting of the linear segment of a hysteresis loop.
  - Calculation of temperature-dependent micromagnetic properties from atomistic
    spin dynamics simulations using Kuz’min equations.
``mammos-dft`` -- 0.3.0
  - Database lookup functionality for a selection of pre-computed materials.
``mammos-entity`` -- 0.5.0
  - Provides entities: quantities with links to the MaMMoS ontology (based on
    EMMO) by combining ``mammos-units`` and `EMMOntoPy
    <https://github.com/emmo-repo/EMMOntoPy>`__.
  - Helper functions to simplify creation of commonly required magnetic entities.
``mammos-mumag`` -- 0.6.0
  - Finite-element hysteresis loop calculations.
  - Requires a separate installation of `esys-escript
    <https://github.com/LutzGross/esys-escript.github.io/>`__.
``mammos-spindynamics`` -- 0.2.0
  - Database lookup functionality for a selection of pre-computed materials.
``mammos-units`` -- 0.3.1
  - Extension of astropy.units that allows working with quantities (units with
    values) containing additional units relevant for magnetism.
