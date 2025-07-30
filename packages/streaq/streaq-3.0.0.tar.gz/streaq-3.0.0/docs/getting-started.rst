Getting started
===============

To start, you'll need to create a ``Worker`` object:

.. code-block:: python

   from contextlib import asynccontextmanager
   from dataclasses import dataclass
   from typing import AsyncIterator
   from httpx import AsyncClient
   from streaq import Worker

   @dataclass
   class WorkerContext:
       """
       Type safe way of defining the dependencies of your tasks.
       e.g. HTTP client, database connection, settings.
       """
       http_client: AsyncClient

   @asynccontextmanager
   async def lifespan(worker: Worker[WorkerContext]) -> AsyncIterator[WorkerContext]:
       """
       Here, we initialize the worker's dependencies.
       You can also do any startup/shutdown work here!
       """
       async with AsyncClient() as http_client:
           yield Context(http_client)

   worker = Worker(redis_url="redis://localhost:6379", lifespan=lifespan)

You can then register async tasks with the worker like this:

.. code-block:: python

   @worker.task(timeout=5)
   async def fetch(url: str) -> int:
       # worker.context here is of type WorkerContext, enforced by static typing
       res = await worker.context.http_client.get(url)
       return len(res.text)

   @worker.cron("* * * * mon-fri")  # every minute on weekdays
   async def cronjob() -> None:
       print("It's a bird... It's a plane... It's CRON!")

Finally, use the worker's async context manager to queue up tasks:

.. code-block:: python

   async with worker:
       await fetch.enqueue("https://tastyware.dev/")
       # this will be run directly locally, not enqueued
       await fetch.run("https://github.com/python-arq/arq")
       # enqueue returns a task object that can be used to get results/info
       task = await fetch.enqueue("https://github.com/tastyware/streaq").start(delay=3)
       print(await task.info())
       print(await task.result(timeout=5))

Putting this all together gives us `example.py <https://github.com/tastyware/streaq/blob/master/example.py>`_. Let's spin up a worker:

.. code-block:: bash

   $ streaq example.worker

and queue up some tasks like so:

.. code-block:: bash

   $ python example.py

Let's see what the output looks like:

.. code-block::

   [INFO] 19:49:44: starting worker db064c92 for 3 functions
   [INFO] 19:49:46: task dc844a5b5f394caa97e4c6e702800eba → worker db064c92
   [INFO] 19:49:46: task dc844a5b5f394caa97e4c6e702800eba ← 15
   [INFO] 19:49:50: task 178c4f4e057942d6b6269b38f5daaaa1 → worker db064c92
   [INFO] 19:49:50: task 178c4f4e057942d6b6269b38f5daaaa1 ← 293784
   [INFO] 19:50:00: task cde2413d9593470babfd6d4e36cf4570 → worker db064c92
   It's a bird... It's a plane... It's CRON!
   [INFO] 19:50:00: task cde2413d9593470babfd6d4e36cf4570 ← None

.. code-block:: python

   TaskData(fn_name='fetch', enqueue_time=1743468587037, task_try=None, scheduled=datetime.datetime(2025, 4, 1, 0, 49, 50, 37000, tzinfo=datetime.timezone.utc))
   TaskResult(success=True, result=293784, start_time=1743468590041, finish_time=1743468590576, queue_name='default')
