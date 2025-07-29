kumoai.experimental.rfm
=======================

.. currentmodule:: kumoai.experimental.rfm

**KumoRFM** (Kumo Relational Foundation Model) is an experimental feature that provides
a powerful interface to query relational data using a pre-trained foundation model.
Unlike traditional machine learning approaches that require feature engineering and model
training, KumoRFM can generate predictions directly from raw relational data using
PQL queries.

.. note::
   KumoRFM is currently in experimental phase. The API may change in future releases.

Overview
--------

KumoRFM consists of three main components:

1. **LocalTable**: A :class:`pandas.DataFrame` wrapper that manages metadata including data types, semantic types, primary keys, and time columns
2. **LocalGraph**: A collection of related :class:`LocalTable` objects with edges defining relationships between tables
3. **KumoRFM**: The main interface to query the relational foundation model

Workflow
--------

The typical KumoRFM workflow follows these steps:

1. **Data Preparation**: Load your relational data into ``pandas.DataFrame`` objects
2. **Table Creation**: Create :class:`LocalTable` objects from your data frames
3. **Graph Construction**: Build a :class:`LocalGraph` that defines relationships between tables
4. **Model Initialization**: Initialize :class:`KumoRFM` with your graph
5. **Querying**: Execute PQL queries to get predictions

Quick Example
-------------

Here's a simple example showing how to use KumoRFM with e-commerce data:

.. code-block:: python

    import pandas as pd
    from kumoai.experimental.rfm import LocalTable, LocalGraph, KumoRFM

    # Load your data
    users_df = pd.DataFrame({
        'user_id': [1, 2, 3, 4, 5],
        'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'created_at': pd.date_range('2023-01-01', periods=5),
        'age': [25, 30, 35, 40, 45]
    })

    orders_df = pd.DataFrame({
        'order_id': [101, 102, 103, 104, 105],
        'user_id': [1, 2, 1, 3, 4],
        'amount': [100.0, 250.0, 75.0, 300.0, 150.0],
        'order_date': pd.date_range('2023-02-01', periods=5)
    })

    # Create LocalGraph from data
    graph = LocalGraph.from_data({
        'users': users_df,
        'orders': orders_df
    })

    # Initialize KumoRFM
    rfm = KumoRFM(graph)

    # Query the model
    result = rfm.query(
        "PREDICT COUNT(orders.*, 0, 30, days) > 0 FOR users.user_id=1"
    )
    # Result is a pandas DataFrame with prediction probabilities
    print(result)  # user_id  COUNT(orders.*, 0, 30, days) > 0
                   # 1        0.85

Query Language
--------------

KumoRFM uses the predictive query language (PQL) for making predictions. For a broader introduction to PQL, see the :doc:`../faq/pquery`.
The KumoRFM PQL syntax differs slightly from the general PQL syntax. The user must specify the entity (or entities) to make predictions for.

While the general PQL structure stays the same:
.. code-block:: sql

    PREDICT <aggregation_expression> FOR <entity_specification>

The entities for each query can be specified in one of two ways:
- By specifying a single entity id, e.g. ``users.user_id=1``
- By specifying a tuple of entity ids, e.g. ``users.user_id IN (1, 2, 3 )``

Classes
-------

LocalTable
~~~~~~~~~~

A :class:`LocalTable` represents a single table backed by a pandas DataFrame with
rich metadata support.

Key features:

- **Metadata Management**: Automatic inference of data types and semantic types
- **Primary Key Support**: Specify or auto-detect primary keys
- **Time Column Support**: Handle temporal data with designated time columns
- **Validation**: Comprehensive validation of table structure and metadata

Example usage:

.. code-block:: python

    # Create from DataFrame with explicit metadata
    table = LocalTable(
        df=df,
        table_name="users",
        primary_key="user_id",
        time_column="created_at"
    )

    # Infer metadata automatically
    table.infer_metadata()

    # Access column metadata
    column = table.column("user_id")
    print(column.stype)  # Stype.ID

LocalGraph
~~~~~~~~~~

A :class:`LocalGraph` represents relationships between multiple :class:`LocalTable` objects,
similar to a relational database schema.

Key features:

- **Multiple Construction Methods**: Create from tables or directly from DataFrames
- **Relationship Management**: Define and manage edges between tables
- **Automatic Link Inference**: Intelligent detection of foreign key relationships
- **Graph Validation**: Ensure graph structure meets requirements before using with KumoRFM

Example usage:

.. code-block:: python

    # Create from tables
    graph = LocalGraph(tables=[users_table, orders_table])

    # Or create directly from data
    graph = LocalGraph.from_data({
        'users': users_df,
        'orders': orders_df
    })

    # Manual relationship management
    graph.link('orders', 'user_id', 'users')
    graph.unlink('orders', 'user_id', 'users')

    # Validation
    graph.validate()

KumoRFM
~~~~~~~

The main :class:`KumoRFM` class provides the interface to query the relational
foundation model.

Key features:

- **Model Initialization**: Automatic setup of serving endpoints
- **Query Interface**: Execute PQL queries to get predictions
- **Async Operations**: Non-blocking operations with status monitoring
- **Resource Management**: Automatic cleanup of cloud resources

Example usage:

.. code-block:: python

    # Initialize with local graph
    rfm = KumoRFM(graph)

    # Query the model
    result = rfm.query(
        "PREDICT COUNT(orders.*, 0, 30, days) > 0 FOR users.user_id=1"
    )
    print(result)  # user_id  COUNT(orders.*, 0, 30, days) > 0
                   # 1        0.85

Best Practices
--------------

Data Preparation
~~~~~~~~~~~~~~~~

1. **Clean Data**: Ensure your DataFrames are clean with no duplicate column names
2. **Consistent Types**: Use consistent data types across related columns
3. **Consistent Column Names**: Ensure column names are consistent across related tables
4. **Primary Keys**: Include a primary key column in each table if possible
5. **Time Columns**: Each table should have at most one time column

Graph Design
~~~~~~~~~~~~

1. **Metapath lengths**: Keep metapath lengths reasonable (ideally 2-3 hops)
   - Longer paths may lead to performance issues and less interpretable results
   - If your relational schema is very complex, it might be worth splitting it into multiple graphs
2. **Meaningful Relationships**: Ensure that the inferred relationships are meaningful/correct
3. **Validation**: Always validate your graph before using with KumoRFM.
4. **Size Limits**: There is a 10GB limit on the total size of the graph.

Querying
~~~~~~~~

1. **Start Simple**: Begin with basic ``COUNT`` queries before moving to complex aggregations.
2. **Time Windows**: Use appropriate time windows for temporal queries.
3. **Entity Specification**: Be specific about which entities you're predicting for.

Limitations
-----------

- **Graph Size**: Maximum graph size is 10GB
- **Experimental Status**: API may change in future releases

See Also
--------

- :doc:`graph` - Core graph functionality
- :doc:`trainer` - Traditional ML training approaches
