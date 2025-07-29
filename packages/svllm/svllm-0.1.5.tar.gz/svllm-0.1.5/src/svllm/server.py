from fastapi import FastAPI, APIRouter
from .openai import add_routes

def create_app(title='svllm', description='svllm api', prefix='/v1', root_path='', *args, **kwargs) -> FastAPI:
    app = FastAPI(title=title, description=description, root_path=root_path, *args, **kwargs)
    app.include_router(add_routes(APIRouter(prefix=prefix)))
    return app
