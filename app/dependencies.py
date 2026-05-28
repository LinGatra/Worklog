from fastapi import Request


async def db_connect(request: Request):
    async_session_factory = request.app.state.session_factory
    async with async_session_factory() as session:
        yield session
