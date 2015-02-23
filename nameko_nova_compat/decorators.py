
import functools

from nameko_nova_compat.channelhandler import ChannelHandler


def ensure(func):
    """wraps an entire function with ensure to use as a decorator. """
    @functools.wraps(func)
    def wrapped(connection, *args, **kwargs):
        with ChannelHandler(connection, create_channel=False) as ch:
            return ch((ch, func), connection, *args, **kwargs)
    return wrapped
