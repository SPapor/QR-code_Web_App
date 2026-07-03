from aiogram import Router

from handlers import auth, qr_create, qr_delete, qr_edit, qr_list


def build_router() -> Router:
    root = Router()
    root.include_router(auth.router)
    root.include_router(qr_list.router)
    root.include_router(qr_create.router)
    root.include_router(qr_edit.router)
    root.include_router(qr_delete.router)
    return root
