class UserData(NamedTuple):
    query: Query[dict | None]
    mutation: Mutation[dict]


class SessionState(NamedTuple):
    query: Query[Any]
    mutation: Mutation[Any]
