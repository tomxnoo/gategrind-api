~/workspace$ python fix.py
🚀 Starting Missing Skill Tree Node Creation
============================================================
🌳 Creating missing skill tree nodes...
📋 Found 315 existing nodes
❌ Error during node creation: 'MovementCategory' object has no attribute 'category_id'
Traceback (most recent call last):
  File "/home/runner/workspace/fix.py", line 414, in <module>
    asyncio.run(main())
  File "/nix/store/7d088dip86hlzri9sk0h78b63yfmx0a0-python3-3.11.13/lib/python3.11/asyncio/runners.py", line 190, in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
  File "/nix/store/7d088dip86hlzri9sk0h78b63yfmx0a0-python3-3.11.13/lib/python3.11/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/nix/store/7d088dip86hlzri9sk0h78b63yfmx0a0-python3-3.11.13/lib/python3.11/asyncio/base_events.py", line 654, in run_until_complete
    return future.result()
           ^^^^^^^^^^^^^^^
  File "/home/runner/workspace/fix.py", line 409, in main
    await creator.create_all_missing_nodes()
  File "/home/runner/workspace/fix.py", line 43, in create_all_missing_nodes
    category_ids = {cat.category_id for cat in categories}
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/workspace/fix.py", line 43, in <setcomp>
    category_ids = {cat.category_id for cat in categories}
                    ^^^^^^^^^^^^^^^
AttributeError: 'MovementCategory' object has no attribute 'category_id'
~/workspace$ 
