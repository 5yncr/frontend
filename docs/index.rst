.. _index:

5yncr frontend
==============

The 5yncr frontend is simply a flask [1]_ app.  It will automatically connect
to the backend if the backend is running.  All the heavy lifting happens in the
backend.

.. [1] It's actually a quart app, which is a flask reimplementation that uses
    python's asyncio.

.. toctree::
    :maxdepth: 1
    :caption: Documentation

    quickstart
    usage


.. toctree::
    :maxdepth: 1
    :caption: API docs:

    generated/syncr_frontend

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
