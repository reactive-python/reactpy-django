<!--orm-excp-start-->

Due to Django's ORM design, database queries must be deferred using hooks. Otherwise, you will see a `#!python SynchronousOnlyOperation` exception.

These `#!python SynchronousOnlyOperation` exceptions may be removed in a future version of Django. However, it is best practice to always perform IO operations (such as ORM queries) via hooks to prevent performance issues.

<!--orm-excp-end-->

<!--orm-fetch-start-->

By default, automatic recursive fetching of `#!python ManyToMany` or `#!python ForeignKey` fields is enabled within the `#!python django_query_postprocessor`. This is needed to prevent `#!python SynchronousOnlyOperation` exceptions when accessing these fields within your ReactPy components.

<!--orm-fetch-end-->
