``estceque`` -- Elasticsearch ingest pipeline validation
========================================================

``estceque`` (*ElasticSearch Transform Conversion (and) Encapsulation QUEry*)
is a Python module for parsing and rendering Elasticsearch ingest pipelines.

As described in `Validating ingest pipelines`_, you can validate Elasticsearch
ingest pipelines using ``estceque`` with the following snippet:

.. code-block:: python

    from estceque import validate_ingest_pipeline_processors

    raw_pipeline = {
        "name": "hello",
        "processors": [
            {"json": {"field": "message"}},
        ],
    }

    print(validate_ingest_pipeline_processors(raw_pipeline))

The project is present at the following locations:

* `Official website and documentation at estceque.touhey.pro <Website_>`_;
* `estceque repository on Gitlab <Gitlab repository_>`_;
* `estceque project on PyPI <PyPI project_>`_.

.. _Validating ingest pipelines:
    https://estceque.touhey.pro/developer-guides/
    validating-ingest-pipelines.html
.. _Website: https://estceque.touhey.pro/
.. _Gitlab repository: https://gitlab.com/kaquel/estceque
.. _PyPI project: https://pypi.org/project/estceque/
