"""Track events to Customer.io."""

from datetime import datetime
from functools import wraps
from pyramid.events import NewRequest
from pyramid.request import Request
from pyramid.response import Response
from pyramid.settings import asbool
from pyramid_customerio import Event
from pyramid_customerio import PropertiesType
from pyramid_customerio.consumer import Consumer
from pyramid_customerio.consumer import Endpoint

import typing as t


def distinct_id_is_required(func: t.Callable) -> t.Callable:
    """Check if distinct_id is set before calling the wrapped function."""

    @wraps(func)
    def wrapper(instance: "CustomerIOTrack", *args: t.Any, **kwargs: t.Any) -> t.Any:
        """Check if distinct_id is set before calling the wrapped function."""
        if not instance.distinct_id:
            raise ValueError(
                "self.distinct_id not set. Pass it to __init__() or set it manually."
            )
        return func(instance, *args, **kwargs)

    return wrapper


class CustomerIOTrack:
    """Track events and update profiles in Customer.io."""

    def __init__(
        self,
        settings: t.Dict[str, t.Any],
        distinct_id: t.Optional[str] = None,
    ) -> None:
        """Configure Customer.io tracking."""
        # Consumer is what connects to Customer.io's HTTP API
        consumer: t.Union[str, t.Any] = settings.get(
            "customerio.consumer", ".consumer.MockedConsumer"
        )
        if isinstance(consumer, str):
            if not consumer.startswith("."):
                consumer = self._resolve_class(consumer)()
            elif consumer == ".consumer.MockedConsumer":
                from pyramid_customerio.consumer import MockedConsumer

                consumer = MockedConsumer()
            elif consumer == ".consumer.BufferedConsumer":
                from pyramid_customerio.consumer import BufferedConsumer

                # Initialize Customer.io client
                try:
                    from customerio import CustomerIO
                    from customerio import Regions
                except ImportError:
                    raise ImportError(
                        "customerio package is not installed. "
                        "Install it with: pip install customerio"
                    )

                site_id = settings.get("customerio.tracking.site_id")
                api_key = settings.get("customerio.tracking.api_key")
                region = settings.get("customerio.tracking.region", "us")

                if not site_id or not api_key:
                    # Fall back to MockedConsumer if credentials are missing
                    from pyramid_customerio.consumer import MockedConsumer

                    consumer = MockedConsumer()
                else:
                    # Convert string region to Regions enum
                    if region == "us":
                        region_enum = Regions.US
                    elif region == "eu":
                        region_enum = Regions.EU
                    else:
                        raise ValueError(
                            f"Unsupported region '{region}'. Valid regions are: 'us', 'eu'"
                        )

                    cio_client = CustomerIO(
                        site_id=site_id, api_key=api_key, region=region_enum
                    )
                    use_structlog = asbool(
                        settings.get("pyramid_heroku.structlog", False)
                    )
                    consumer = BufferedConsumer(cio_client, use_structlog)
            else:
                raise ValueError(f"Unknown consumer: {consumer}")
        self.consumer: Consumer = consumer

        # Events
        events = settings.get("customerio.events", ".Events")
        if isinstance(events, str):
            if not events.startswith("."):
                self.events = self._resolve_class(events)()
            elif events == ".Events":
                from pyramid_customerio import Events

                self.events = Events()
            else:
                raise ValueError(f"Unknown events: {events}")
        else:
            self.events = events

        # Event properties
        event_properties = settings.get(
            "customerio.event_properties", ".EventProperties"
        )
        if isinstance(event_properties, str):
            if not event_properties.startswith("."):
                self.event_properties = self._resolve_class(event_properties)()
            elif event_properties == ".EventProperties":
                from pyramid_customerio import EventProperties

                self.event_properties = EventProperties()
            else:
                raise ValueError(f"Unknown event_properties: {event_properties}")
        else:
            self.event_properties = event_properties

        # Profile properties
        profile_properties = settings.get(
            "customerio.profile_properties", ".ProfileProperties"
        )
        if isinstance(profile_properties, str):
            if not profile_properties.startswith("."):
                self.profile_properties = self._resolve_class(profile_properties)()
            elif profile_properties == ".ProfileProperties":
                from pyramid_customerio import ProfileProperties

                self.profile_properties = ProfileProperties()
            else:
                raise ValueError(f"Unknown profile_properties: {profile_properties}")
        else:
            self.profile_properties = profile_properties

        # Profile meta properties
        profile_meta_properties = settings.get(
            "customerio.profile_meta_properties", ".ProfileMetaProperties"
        )
        if isinstance(profile_meta_properties, str):
            if not profile_meta_properties.startswith("."):
                self.profile_meta_properties = self._resolve_class(
                    profile_meta_properties
                )()
            elif profile_meta_properties == ".ProfileMetaProperties":
                from pyramid_customerio import ProfileMetaProperties

                self.profile_meta_properties = ProfileMetaProperties()
            else:
                raise ValueError(
                    f"Unknown profile_meta_properties: {profile_meta_properties}"
                )
        else:
            self.profile_meta_properties = profile_meta_properties

        # Distinct ID
        self.distinct_id = distinct_id

    def _resolve_class(self, dotted_path: str) -> t.Any:
        """Resolve a dotted path to a class."""
        module_name, class_name = dotted_path.rsplit(".", 1)
        module = __import__(module_name, fromlist=[class_name])
        return getattr(module, class_name)

    @distinct_id_is_required
    def track(self, event: Event, props: t.Optional[PropertiesType] = None) -> None:
        """Track a Customer.io event.

        Args:
            event: Event object defining the event to track
            props: Optional dict of Property->value mappings
        """
        if not props:
            props = {}

        # Validate event
        if event not in self.events.__dict__.values():
            raise ValueError(f"Event '{event.name}' must be a member of self.events")

        # Validate properties
        for prop in props:
            if prop not in self.event_properties.__dict__.values():
                raise ValueError(
                    f"Property '{prop.name}' is not a member of self.event_properties"
                )

        # If event has specific allowed properties, validate against those
        if event.properties:
            for prop in props:
                if prop not in event.properties:
                    raise ValueError(
                        f"Property '{prop}' must be a member of Event.properties"
                    )

        # Format dates for Customer.io (unix timestamp)
        formatted_props = {}
        for prop, value in props.items():
            if isinstance(value, datetime):
                formatted_props[prop.name] = round(value.timestamp())
            else:
                formatted_props[prop.name] = value

        # Send to Customer.io
        msg = {
            "id": self.distinct_id,
            "name": event.name,
            **formatted_props,
        }
        self.consumer.send(Endpoint.track, msg)

    @distinct_id_is_required
    def identify(
        self,
        props: PropertiesType,
        meta: t.Optional[PropertiesType] = None,
    ) -> None:
        """Create or update a customer profile in Customer.io.

        Args:
            props: Dict of ProfileProperty->value mappings
            meta: Optional dict of ProfileMetaProperty->value mappings
        """
        if not meta:
            meta = {}

        # Validate properties
        for prop in props:
            if prop not in self.profile_properties.__dict__.values():
                raise ValueError(
                    f"Property '{prop.name}' is not a member of self.profile_properties"
                )

        for prop in meta:
            if prop not in self.profile_meta_properties.__dict__.values():
                raise ValueError(
                    f"Property '{prop.name}' is not a member of self.profile_meta_properties"
                )

        # Format properties for Customer.io
        formatted_props = {}
        for prop, value in props.items():
            if isinstance(value, datetime):
                formatted_props[prop.name] = round(value.timestamp())
            else:
                formatted_props[prop.name] = value

        # Merge in meta properties
        for prop, value in meta.items():
            formatted_props[prop.name] = value

        # Send to Customer.io
        msg = {
            "id": self.distinct_id,
            **formatted_props,
        }
        self.consumer.send(Endpoint.identify, msg)


def customerio_init(request: Request) -> CustomerIOTrack:
    """Return a configured CustomerIOTrack class instance."""
    distinct_id = None
    if getattr(request, "user", None):
        distinct_id = request.user.distinct_id

    customerio = CustomerIOTrack(
        settings=request.registry.settings, distinct_id=distinct_id
    )

    return customerio


def customerio_flush(event: NewRequest) -> None:
    """Send out all pending messages on Pyramid request end."""

    def flush(request: Request, response: Response) -> None:
        """Send all the enqueued messages at the end of request lifecycle."""

        # If request.customerio was never called during request runtime, then
        # skip initializing and flushing CustomerIOTrack.
        if "customerio" not in request.__dict__:
            return

        request.customerio.consumer.flush()

    event.request.add_response_callback(flush)
