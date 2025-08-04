from contextvars import ContextVar
from app.schemas.user import User

user_id_ctx = ContextVar("user_id", default=None)
user_role_ctx = ContextVar("user_role", default=None)
request_id_ctx = ContextVar("request_id", default=None)
ip_address_ctx = ContextVar("ip_address", default=None)


#IDK why, but ContextVar.set() does not work in dependencies.py :(
def set_user_context(current_user: User):
    user_role_ctx.set(current_user.role)
    user_id_ctx.set(current_user.id)


def add_contextvars(_, __, event_dict):
    event_dict["request_id"] = request_id_ctx.get()
    event_dict["user_id"] = user_id_ctx.get()
    event_dict["user_role"] = user_role_ctx.get()
    event_dict["ip"] = ip_address_ctx.get()

    return event_dict