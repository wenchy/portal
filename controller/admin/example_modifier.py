"""Modifier"""

__priority__ = 1

from core import form
from core.context import Context
import userconf


@form.onpage
def query_users(ctx: Context):
    """
    {
        "title": "Query users",
        "submit": 999
    }
    """
    return userconf.USERS
