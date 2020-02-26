appsync-athena-async-resolver
=============================

.. _APL2: http://www.apache.org/licenses/LICENSE-2.0.txt
.. _named placeholders: https://pyformat.info/#named_placeholders
.. _AWS Athena: https://docs.aws.amazon.com/athena/latest/ug/what-is.html
.. _PyFormat: https://pyformat.info/
.. _AWS AppSync: https://docs.aws.amazon.com/appsync/latest/devguide/welcome.html

This is a generic Lambda task function that can execute athena queries and
return results asynchronously.
It is intended to be used in `AWS AppSync`_.
This function will take the input information, call `AWS Athena`_, and respond
to `AWS AppSync`_ with the results of the SQL call.

Environment Variables
---------------------
:DATABASE: The `AWS Athena`_ Database to query. May be overridden in the ``query`` request. Defaults to ``default``
:WORKGROUP: The `AWS Athena`_ Workgroup to use during queries. May be overridden in the ``query`` request. Defaults to ``primary``.
:LIMIT: The maximum number of results to return during the ``results`` request. May be overridden in the ``results`` request. Defaults to ``100``.

AWS Permissions Required
------------------------
* **AmazonAthenaFullAccess** arn:aws:iam::aws:policy/AmazonAthenaFullAccess

You will also require read access to the underlying `AWS Athena`_ datasource and access to any KMS
keys used.


Handler Method
--------------
.. code::

  function.handler

Request Syntax
--------------

This function supports three different request type: ``query``, ``status`` and ``results``.
These are defined below, and must be present in the ``payload`` field in `AWS AppSync`_ request mapping template.

Query
^^^^^

Request::

  {
    "action": "query",
    "arguments": {
      "database": "foo", (OPTIONAL, defaults to the DATABASE environment variable)
      "query": "select * from bar",
      "workgroup": "myworkgroup" (OPTIONAL, defaults to the WORKGROUP environment variable)
    }
  }

Response::

  {
    "id": "string", (The query execution id, used for status and results)
    "state": ["QUEUED" | "RUNNING" | "SUCCEEDED" | "FAILED" | "CANCELLED"],
    "stateChangeReason": "string",
    "submissionDateTime": datetime,
    "completionDateTime": datetime (If not QUEUED or RUNNING)
  }

Status
^^^^^^

Request::

  {
    "action": "status",
    "arguments": {
      "id": "string"
    }
  }

Response::

  {
    "id": "string", (The query execution id, used for status and results)
    "state": ["QUEUED" | "RUNNING" | "SUCCEEDED" | "FAILED" | "CANCELLED"],
    "stateChangeReason": "string",
    "submissionDateTime": datetime,
    "completionDateTime": datetime (If not QUEUED or RUNNING)
  }

Results
^^^^^^^

Request::

  {
    "action": "results",
    "arguments": {
      "id": "string",
      "limit": int, (OPTIONAL, defaults to the LIMIT environment variable)
      "nextToken": "string" (OPTIONAL, the nextToken returned from the previous results request)
    }
  }

Response::

  {
    "nextToken": "string", (Present if additional results exist)
    "results": [
      {
        "Key": Value,
        (Keys and values are generated from the query results. 
        Keys are the column names, values are converted to their
        specified types.)
      }
    ]
  }

Lambda Package Location
-----------------------
https://s3.amazonaws.com/lambdalambdalambda-repo/quinovas/appsync-athena-async-resolver/appsync-athena-async-resolver-0.1.0.zip

License: `APL2`_
