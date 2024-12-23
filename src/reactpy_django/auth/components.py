from __future__ import annotations

from typing import TYPE_CHECKING

from reactpy import component, hooks

if TYPE_CHECKING:
    from django.contrib.sessions.backends.base import SessionBase

from reactpy_django.javascript_components import HttpRequest


@component
def auth_manager():
    session_cookie, set_session_cookie = hooks.use_state("")
    scope = hooks.use_connection().scope

    @hooks.use_effect(dependencies=None)
    async def _session_check():
        """Generate a session cookie if `login` was called in a user's component."""
        from django.conf import settings

        session: SessionBase | None = scope.get("session")
        login_required: bool = scope.get("reactpy-login", False)
        if not login_required or not session or not session.session_key:
            return

        # Begin generating a cookie string
        key = session.session_key
        domain: str | None = settings.SESSION_COOKIE_DOMAIN
        httponly: bool = settings.SESSION_COOKIE_HTTPONLY
        name: str = settings.SESSION_COOKIE_NAME
        path: str = settings.SESSION_COOKIE_PATH
        samesite: str | bool = settings.SESSION_COOKIE_SAMESITE
        secure: bool = settings.SESSION_COOKIE_SECURE
        new_cookie = f"{name}={key}"
        if domain:
            new_cookie += f"; Domain={domain}"
        if httponly:
            new_cookie += "; HttpOnly"
        if isinstance(path, str):
            new_cookie += f"; Path={path}"
        if samesite:
            new_cookie += f"; SameSite={samesite}"
        if secure:
            new_cookie += "; Secure"
        if not session.get_expire_at_browser_close():
            session_max_age: int = session.get_expiry_age()
            session_expiration: str = session.get_expiry_date().strftime("%a, %d-%b-%Y %H:%M:%S GMT")
            if session_expiration:
                new_cookie += f"; Expires={session_expiration}"
            if isinstance(session_max_age, int):
                new_cookie += f"; Max-Age={session_max_age}"

        # Save the cookie within this component's state so that the client-side component can ingest it
        scope.pop("reactpy-login")
        if new_cookie != session_cookie:
            set_session_cookie(new_cookie)

    def http_request_callback(status_code: int, response: str):
        """Remove the cookie from server-side memory if it was successfully set.
        Doing this will subsequently remove the client-side HttpRequest component from the DOM."""
        set_session_cookie("")
        # if status_code >= 300:
        #     print(f"Unexpected status code {status_code} while trying to login user.")

    # If a session cookie was generated, send it to the client
    if session_cookie:
        # print("Session Cookie: ", session_cookie)
        return HttpRequest(
            {
                "method": "POST",
                "url": "",
                "body": {},
                "callback": http_request_callback,
            },
        )

    return None
