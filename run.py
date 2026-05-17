import uvicorn

from app.config import config


def main():
    uvicorn.run(
        app='app.main:app',
        host=config.APP_HOST,
        port=config.APP_PORT,
        reload=True if config.ENVIRONMENT != 'prod' else False,
        workers=1,
    )


if __name__ == '__main__':
    main()
