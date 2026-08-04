import queue
import threading


MAX_QUEUE_SIZE = 100

_subscribers = set()
_subscribers_lock = threading.Lock()


def subscribe():
    """
    Register a new runtime event subscriber.

    Each subscriber gets its own queue.
    SSE endpoint will use this queue later.
    """

    subscriber_queue = queue.Queue(
        maxsize=MAX_QUEUE_SIZE
    )

    with _subscribers_lock:
        _subscribers.add(
            subscriber_queue
        )

    print(
        "SUBSCRIBE CALLED"
    )

    print(
        "SUBSCRIBERS AFTER ADD =",
        len(_subscribers)
    )

    return subscriber_queue


def unsubscribe(
    subscriber_queue
):
    """
    Remove subscriber when SSE connection closes.
    """

    with _subscribers_lock:
        _subscribers.discard(
            subscriber_queue
        )


def publish_monitor_refresh():

    """
    Publish monitor refresh signal
    to all dashboard subscribers.
    """

    with _subscribers_lock:
        subscribers_snapshot = list(
            _subscribers
        )

    print(
    "SUBSCRIBERS =",
    len(subscribers_snapshot)
    )
    for subscriber_queue in subscribers_snapshot:

        try:
            if subscriber_queue.full():
                try:
                    subscriber_queue.get_nowait()
                except queue.Empty:
                    pass

            subscriber_queue.put_nowait(
                {
                    "type": "refresh"
                }
            )


        except Exception as ex:
            print(
                "MONITOR BUS PUBLISH ERROR =",
                ex
            )