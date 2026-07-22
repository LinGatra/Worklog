import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.core.image import DockerImage
from testcontainers.core.network import Network
from testcontainers.core.wait_strategies import LogMessageWaitStrategy
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope='session')
def dev_image():
    with DockerImage(path='.', tag='dev') as image:
        yield image


@pytest.fixture(scope='session')
def app_environment(dev_image):
    with Network() as network:
        postgres = (
            PostgresContainer('postgres:16')
            .with_network(network=network)
            .with_network_aliases('test-db')
        )

        postgres.start()

        def apply_env(container: DockerContainer, env: dict) -> DockerContainer:
            for key, value in env.items():
                container = container.with_env(key, value)
            return container

        common_env = {
            'POSTGRES_USER': postgres.username,
            'POSTGRES_PASSWORD': postgres.password,
            'POSTGRES_HOST': 'test-db',
            'POSTGRES_PORT': '5432',
            'POSTGRES_DB': postgres.dbname,
            'SECRET_KEY': 'test-secret-key',
            'ACCESS_TOKEN_EXPIRE_MINUTES': '30',
            'APP_HOST': '0.0.0.0',
            'APP_PORT': '8000',
        }

        app = apply_env(
            DockerContainer('dev')
            .with_network(network=network)
            .with_network_aliases('test-worklog')
            .with_exposed_ports(8000)
            .with_command(
                f'uvicorn app.main:app --host {common_env["APP_HOST"]} --port {common_env["APP_PORT"]}'
            )
            .waiting_for(LogMessageWaitStrategy('Application startup complete')),
            common_env,
        )

        alembic = apply_env(
            DockerContainer('dev')
            .with_network(network=network)
            .with_network_aliases('test-alembic')
            .with_command('alembic upgrade head'),
            common_env,
        )

        alembic.start()
        exit_code = alembic.get_wrapped_container().wait()['StatusCode']
        if exit_code != 0:
            raise RuntimeError(alembic.get_logs())
        alembic.stop()

        app.start()
        # wait_for_logs(app, 'Application startup complete')

        yield {
            'app_url': f'http://{app.get_container_host_ip()}:{app.get_exposed_port(8000)}',
        }

        app.stop()
        postgres.stop()
