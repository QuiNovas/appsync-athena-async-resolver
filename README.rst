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


AWS Permissions Required
------------------------
- AmazonAthenaFullAccess (arn:aws:iam::aws:policy/AmazonAthenaFullAccess)

Handler Method
--------------
.. code::

  function.handler

Request Syntax
--------------


Lambda Package Location
-----------------------
https://s3.amazonaws.com/lambdalambdalambda-repo/quinovas/athena-task/appsync-athena-async-resolver-0.1.0.zip

License: `APL2`_
