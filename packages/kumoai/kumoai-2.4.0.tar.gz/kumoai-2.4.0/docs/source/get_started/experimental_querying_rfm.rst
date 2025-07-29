Querying KumoRFM
================================

.. currentmodule:: kumoai.experimental.querying_rfm

**Predictive Query** is a querying language that allows you to define a predictive problem.
It defines two main components: Entities to make the prediction for and target for each entity.
For the full thorough introduction to predictive query, please refer to
`the predictive query tutorial <https://docs.kumo.ai/docs/tutorial>`__.
In this page, you can find how to use predictive query to interact with KumoRFM.

.. note::
   KumoRFM is currently in experimental phase. Some of the predictive query
   features are not fully supported yet.

Defining Entities
-----------------

The general PQL structure stays the same:

.. code-block:: sql

    PREDICT <aggregation_expression> FOR <entity_specification>

Unlike the enterprise product, KumoRFM makes a prediction for a handful of selected
entities at a time.
As such, entities for each query can be specified in one of two ways:
- By specifying a single entity id, e.g. ``users.user_id=1``
- By specifying a tuple of entity ids, e.g. ``users.user_id IN (1, 2, 3 )``

Improving the context through Entity Filters
--------------------------------------------

KumoRFM makes its entity-specific predictions based on context examples,
collected from the database. Just like entity filters allow you to control the
training data in the Kumo enterprise product, they can be used to provide
more control over KumoRFM context examples.
For example, to exclude users without recent activity from the context, we
can write:

.. code-block:: sql

    PREDICT COUNT(orders.*, 0, 30, days) > 0
    FOR user.user_id=1 WHERE COUNT(orders.*, -30, 0, days) > 0

This limits the context examples to predicting churn for active users,
limiting the context to examples relevant to your case and improving the
performance. These filters are NOT applied to the provided entity list.

Evaluation mode
---------------
Adding an `EVALUATE` keyword before the query will perform the automatic
evaluation on a sample of up to 1024 examples.
The provided IDs are ignored.

.. code-block:: python

    # Query the model
    result = rfm.query(
        "EVALUATE PREDICT COUNT(orders.*, 0, 30, days) FOR users.user_id=1"
    )
    # Result is a pandas DataFrame with metrics
    print(result)  # MAE  MSE  RMSE
                   # ...  ...  ...

Unsupported features in KumoRFM Predictive Query
------------------------------------------------
Due to the experimental nature of KumoRFM, some features are not yet fully
supported and will be added soon.

 * Only numerical and categorical columns are valid columns, except for
   `LIST_DISTINCT()` aggregation, where only foreign key targets are supported.
 * `ASSUMING` clause is not permitted.
 * Filtering by column value (e.g. `WHERE user.age > 21`) is only supported for
   columns in the same table. Same goes for predicting a single non-aggregated
   value, e.g. `PREDICT user.age`.
 * `LIST_DISTINCT()` without a time interval is not supported.
 * `LAST` and `FIRST` aggregations are not supported.
 * The only currently supported string operations are `=` and `!=`.
