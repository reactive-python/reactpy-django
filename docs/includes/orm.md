<!--orm-excp-start-->

Due to Django's ORM design, database queries must be deferred using hooks. Otherwise, you will see a `SynchronousOnlyOperation` exception.

These `SynchronousOnlyOperation` exceptions may be resolved in a future version of Django containing an asynchronous ORM. However, it is best practice to always perform ORM calls in the background via hooks.

<!--orm-excp-end-->

<!--orm-fetch-start-->

By default, automatic recursive fetching of `ManyToMany` or `ForeignKey` fields is enabled within the default `QueryOptions.postprocessor`. This is needed to prevent `SynchronousOnlyOperation` exceptions when accessing these fields within your ReactPy components.

<!--orm-fetch-end-->
