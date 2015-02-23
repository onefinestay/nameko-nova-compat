import eventlet
eventlet.monkey_patch()  # noqa (code before rest of imports)

from functools import partial
import logging
import sys

from kombu import Connection
from kombu import pools
from nameko.containers import ServiceContainer
from nameko.testing.utils import (
    get_rabbit_config, get_rabbit_manager, get_rabbit_connections,
    reset_rabbit_connections, reset_rabbit_vhost)
import pytest

from nameko_nova_compat.testing import reset_state


def pytest_addoption(parser):
    parser.addoption(
        '--blocking-detection',
        action='store_true',
        dest='blocking_detection',
        default=False,
        help='turn on eventlet hub blocking detection')

    parser.addoption(
        "--log-level", action="store",
        default='DEBUG',
        help=("The logging-level for the test run."))

    parser.addoption(
        "--amqp-uri", action="store", dest='AMQP_URI',
        default='amqp://guest:guest@localhost:5672/nameko',
        help=("The AMQP-URI to connect to rabbit with."))

    parser.addoption(
        "--rabbit-ctl-uri", action="store", dest='RABBIT_CTL_URI',
        default='http://guest:guest@localhost:15672',
        help=("The URI for rabbit's management API."))


def pytest_configure(config):
    if config.option.blocking_detection:
        from eventlet import debug
        debug.hub_blocking_detection(True)

    log_level = config.getoption('log_level')
    if log_level is not None:
        log_level = getattr(logging, log_level)
        logging.basicConfig(level=log_level, stream=sys.stderr)


@pytest.fixture
def empty_config(request):
    return {'AMQP_URI': ""}


@pytest.fixture(scope='session')
def rabbit_manager(request):
    config = request.config
    return get_rabbit_manager(config.getoption('RABBIT_CTL_URI'))


@pytest.yield_fixture()
def rabbit_config(request, rabbit_manager):
    amqp_uri = request.config.getoption('AMQP_URI')

    conf = get_rabbit_config(amqp_uri)

    reset_rabbit_connections(conf['vhost'], rabbit_manager)
    reset_rabbit_vhost(conf['vhost'], conf['username'], rabbit_manager)

    yield conf

    pools.reset()  # close connections in pools

    # raise a runtime error if the test leaves any connections lying around
    connections = get_rabbit_connections(conf['vhost'], rabbit_manager)
    if connections:
        count = len(connections)
        raise RuntimeError("{} rabbit connection(s) left open.".format(count))


@pytest.yield_fixture
def container_factory(rabbit_config):

    all_containers = []

    def make_container(service_cls, config, worker_ctx_cls=None):
        container = ServiceContainer(service_cls, config, worker_ctx_cls)
        all_containers.append(container)
        return container

    yield make_container

    for c in all_containers:
        try:
            c.stop()
        except:
            pass


connections = []


def _get_connection(uri):
    conn = Connection(uri, transport_options={'confirm_publish': True})
    connections.append(conn)
    return conn


def close_connections():
    for c in connections:
        c.close()
    connections[:]


@pytest.yield_fixture
def connection(rabbit_config):
    amqp_uri = rabbit_config['AMQP_URI']

    yield _get_connection(amqp_uri)
    close_connections()


@pytest.yield_fixture
def get_connection(rabbit_config):
    amqp_uri = rabbit_config['AMQP_URI']

    yield partial(_get_connection, amqp_uri)
    close_connections()


@pytest.yield_fixture(autouse=True)
def reset_mock_proxy():
    yield
    reset_state()
