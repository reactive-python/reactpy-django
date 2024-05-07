## Overview

<p class="intro" markdown>

ReactPy exposes Django management commands that can be used to perform various ReactPy-related tasks.

</p>

---

## Clean ReactPy Command

Command used to manually clean ReactPy data.

When using this command without arguments, it will perform all cleaning operations. You can limit cleaning to specific operations through arguments such as `--sessions`.

!!! example "Terminal"

    ```bash linenums="0"
    python manage.py clean_reactpy
    ```

??? example "See Interface"

    Type `python manage.py clean_reactpy --help` to see the available options.
