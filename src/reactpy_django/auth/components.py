from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from reactpy import component, hooks, web

if TYPE_CHECKING:
    from django.contrib.sessions.backends.base import SessionBase


SetCookie = web.export(
    web.module_from_file("reactpy-django", file=Path(__file__).parent.parent / "static" / "client.js"),
    ("SetCookie"),
)


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

    def on_complete_callback(success: bool):
        """Remove the cookie from server-side memory if it was successfully set.
        This will subsequently remove the client-side cookie-setter component from the DOM."""
        if success:
            set_session_cookie("")

    # If a session cookie was generated, send it to the client
    if session_cookie:
        print("Session Cookie: ", session_cookie)
        return SetCookie({"sessionCookie": session_cookie}, on_complete_callback)
