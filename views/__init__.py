# views/__init__.py
# Exposes all top-level view screens for import by the main application.

from .login_view import LoginView
from .dashboard_kasir_view import DashboardKasirView
from .dashboard_admin_view import DashboardAdminView

__all__ = [
    "LoginView",
    "DashboardKasirView",
    "DashboardAdminView",
]
