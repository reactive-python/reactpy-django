class SessionStateModel(models.Model):
    """A model for storing `session_state` data.

    This is used to persistently store ReactPy state across WebSocket reconnects (and, depending
    on the configured `REACTPY_SESSION_STATE_MODE`, optionally across page reloads as well).

    The `scope_id` uniquely identifies the scope that the state belongs to. By default it is a
    per-component (per-tab) token that is stable across WebSocket reconnects. When
    `REACTPY_SESSION_STATE_MODE` is set to `"user"`, the scope is instead the authenticated user's
    primary key (falling back to a per-tab token for anonymous users)."""

    scope_id = models.CharField(max_length=255)
    key = models.CharField(max_length=255)
    data = models.BinaryField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["scope_id", "key"], name="reactpy_session_state_unique"),
        ]
        indexes = [
            models.Index(fields=["scope_id", "updated_at"], name="reactpy_session_state_idx"),
        ]
