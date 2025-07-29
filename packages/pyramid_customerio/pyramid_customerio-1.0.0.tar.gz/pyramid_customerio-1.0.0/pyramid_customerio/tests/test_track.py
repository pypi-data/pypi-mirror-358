"""Tests for Customer.io tracking."""

from dataclasses import dataclass
from datetime import datetime
from freezegun import freeze_time
from pyramid_customerio import Event
from pyramid_customerio import EventProperties
from pyramid_customerio import Events
from pyramid_customerio import ProfileMetaProperties
from pyramid_customerio import ProfileProperties
from pyramid_customerio import Property
from pyramid_customerio.consumer import BufferedConsumer
from pyramid_customerio.consumer import Endpoint
from pyramid_customerio.consumer import MockedConsumer
from pyramid_customerio.track import CustomerIOTrack
from unittest import mock

import pytest


def test_customerio_init_distinct_id() -> None:
    """Test distinct_id is set in customerio_init function."""
    from pyramid_customerio.track import customerio_init

    # Requests without request.user
    request = mock.Mock(spec="registry headers".split())
    request.registry.settings = {}
    request.headers = {}

    result = customerio_init(request)

    assert result.__class__ == CustomerIOTrack
    assert result.distinct_id is None

    # Requests with request.user
    request = mock.Mock(spec="registry headers user".split())
    request.registry.settings = {}
    request.headers = {}
    request.user.distinct_id = "foo"

    result = customerio_init(request)

    assert result.__class__ == CustomerIOTrack
    assert result.distinct_id == "foo"


def test_init_consumers() -> None:
    """Test initialization of Consumer."""

    # default consumer (MockedConsumer when no credentials)
    customerio = CustomerIOTrack(settings={})
    assert isinstance(customerio.consumer, MockedConsumer)

    # if credentials are set, use BufferedConsumer
    with mock.patch("customerio.CustomerIO"):
        customerio = CustomerIOTrack(
            settings={
                "customerio.tracking.site_id": "site123",
                "customerio.tracking.api_key": "key123",
                "customerio.consumer": ".consumer.BufferedConsumer",
            }
        )
        assert isinstance(customerio.consumer, BufferedConsumer)

    # resolved from a dotted-name
    customerio = CustomerIOTrack(
        settings={
            "customerio.consumer": "pyramid_customerio.consumer.MockedConsumer",
        }
    )
    assert isinstance(customerio.consumer, MockedConsumer)


@dataclass(frozen=True)
class FooEvents(Events):
    foo: Event = Event("Foo")


@dataclass(frozen=True)
class FooEventProperties(EventProperties):
    foo: Property = Property("foo")


@dataclass(frozen=True)
class FooProfileProperties(ProfileProperties):
    foo: Property = Property("foo")


@dataclass(frozen=True)
class FooProfileMetaProperties(ProfileMetaProperties):
    foo: Property = Property("foo")


def test_init_events() -> None:
    """Test initialization of Events."""

    # default events
    customerio = CustomerIOTrack(settings={})
    assert isinstance(customerio.events, Events)

    # resolved from a dotted-name
    customerio = CustomerIOTrack(
        settings={
            "customerio.events": "pyramid_customerio.tests.test_track.FooEvents",
        }
    )
    assert isinstance(customerio.events, FooEvents)


def test_init_event_properties() -> None:
    """Test initialization of EventProperties."""

    # default event properties
    customerio = CustomerIOTrack(settings={})
    assert isinstance(customerio.event_properties, EventProperties)

    # resolved from a dotted-name
    customerio = CustomerIOTrack(
        settings={
            "customerio.event_properties": "pyramid_customerio.tests.test_track.FooEventProperties",
        }
    )
    assert isinstance(customerio.event_properties, FooEventProperties)


def test_init_profile_properties() -> None:
    """Test initialization of ProfileProperties."""

    # default profile properties
    customerio = CustomerIOTrack(settings={})
    assert isinstance(customerio.profile_properties, ProfileProperties)

    # resolved from a dotted-name
    customerio = CustomerIOTrack(
        settings={
            "customerio.profile_properties": "pyramid_customerio.tests.test_track.FooProfileProperties",
        }
    )
    assert isinstance(customerio.profile_properties, FooProfileProperties)


def test_init_profile_meta_properties() -> None:
    """Test initialization of ProfileMetaProperties."""

    # default profile meta properties
    customerio = CustomerIOTrack(settings={})
    assert isinstance(customerio.profile_meta_properties, ProfileMetaProperties)

    # resolved from a dotted-name
    customerio = CustomerIOTrack(
        settings={
            "customerio.profile_meta_properties": "pyramid_customerio.tests.test_track.FooProfileMetaProperties",
        }
    )
    assert isinstance(customerio.profile_meta_properties, FooProfileMetaProperties)


def test_track_event() -> None:
    """Test tracking events."""
    customerio = CustomerIOTrack(settings={}, distinct_id="foo-123")

    customerio.track(customerio.events.page_viewed)

    assert isinstance(customerio.consumer, MockedConsumer)
    assert customerio.consumer.mocked_messages == [
        {
            "endpoint": Endpoint.track,
            "msg": {
                "id": "foo-123",
                "name": "Page Viewed",
            },
        }
    ]


def test_track_event_with_properties() -> None:
    """Test tracking events with properties."""
    customerio = CustomerIOTrack(settings={}, distinct_id="foo-123")

    customerio.track(
        customerio.events.page_viewed,
        {
            customerio.event_properties.title: "Hello World",
            customerio.event_properties.path: "/hello",
        },
    )

    assert isinstance(customerio.consumer, MockedConsumer)
    assert customerio.consumer.mocked_messages == [
        {
            "endpoint": Endpoint.track,
            "msg": {
                "id": "foo-123",
                "name": "Page Viewed",
                "Title": "Hello World",
                "Path": "/hello",
            },
        }
    ]


@freeze_time("2019-01-01 00:00:00")
def test_track_event_with_datetime_properties() -> None:
    """Test tracking events with datetime properties."""
    customerio = CustomerIOTrack(settings={}, distinct_id="foo-123")

    dt = datetime(2019, 1, 1, 0, 0, 0)
    customerio.track(
        customerio.events.page_viewed,
        {customerio.event_properties.title: dt},
    )

    assert isinstance(customerio.consumer, MockedConsumer)
    assert customerio.consumer.mocked_messages == [
        {
            "endpoint": Endpoint.track,
            "msg": {
                "id": "foo-123",
                "name": "Page Viewed",
                "Title": 1546300800,  # Unix timestamp
            },
        }
    ]


def test_track_event_validation() -> None:
    """Test event validation."""
    customerio = CustomerIOTrack(settings={}, distinct_id="foo-123")

    # Invalid event
    with pytest.raises(
        ValueError, match="Event 'Invalid' must be a member of self.events"
    ):
        customerio.track(Event("Invalid"))

    # Invalid property
    with pytest.raises(
        ValueError, match="Property 'invalid' is not a member of self.event_properties"
    ):
        customerio.track(customerio.events.page_viewed, {Property("invalid"): "value"})


def test_track_event_requires_distinct_id() -> None:
    """Test that tracking requires distinct_id."""
    customerio = CustomerIOTrack(settings={})

    with pytest.raises(ValueError, match="self.distinct_id not set"):
        customerio.track(customerio.events.page_viewed)


def test_identify_user() -> None:
    """Test identifying users."""
    customerio = CustomerIOTrack(settings={}, distinct_id="foo-123")

    customerio.identify(
        {
            customerio.profile_properties.email: "test@example.com",
            customerio.profile_properties.name: "John Doe",
        }
    )

    assert isinstance(customerio.consumer, MockedConsumer)
    assert customerio.consumer.mocked_messages == [
        {
            "endpoint": Endpoint.identify,
            "msg": {
                "id": "foo-123",
                "email": "test@example.com",
                "name": "John Doe",
            },
        }
    ]


@freeze_time("2019-01-01 00:00:00")
def test_identify_user_with_datetime() -> None:
    """Test identifying users with datetime properties."""
    customerio = CustomerIOTrack(settings={}, distinct_id="foo-123")

    dt = datetime(2019, 1, 1, 0, 0, 0)
    customerio.identify(
        {
            customerio.profile_properties.created_at: dt,
            customerio.profile_properties.email: "test@example.com",
        }
    )

    assert isinstance(customerio.consumer, MockedConsumer)
    assert customerio.consumer.mocked_messages == [
        {
            "endpoint": Endpoint.identify,
            "msg": {
                "id": "foo-123",
                "created_at": 1546300800,  # Unix timestamp
                "email": "test@example.com",
            },
        }
    ]


def test_identify_user_with_meta() -> None:
    """Test identifying users with meta properties."""
    customerio = CustomerIOTrack(settings={}, distinct_id="foo-123")

    customerio.identify(
        {customerio.profile_properties.email: "test@example.com"},
        {customerio.profile_meta_properties.ip: "192.168.1.1"},
    )

    assert isinstance(customerio.consumer, MockedConsumer)
    assert customerio.consumer.mocked_messages == [
        {
            "endpoint": Endpoint.identify,
            "msg": {
                "id": "foo-123",
                "email": "test@example.com",
                "ip": "192.168.1.1",
            },
        }
    ]


def test_identify_user_validation() -> None:
    """Test user identification validation."""
    customerio = CustomerIOTrack(settings={}, distinct_id="foo-123")

    # Invalid property
    with pytest.raises(
        ValueError,
        match="Property 'invalid' is not a member of self.profile_properties",
    ):
        customerio.identify({Property("invalid"): "value"})

    # Invalid meta property
    with pytest.raises(
        ValueError,
        match="Property 'invalid' is not a member of self.profile_meta_properties",
    ):
        customerio.identify(
            {customerio.profile_properties.email: "test@example.com"},
            {Property("invalid"): "value"},
        )


def test_identify_user_requires_distinct_id() -> None:
    """Test that identification requires distinct_id."""
    customerio = CustomerIOTrack(settings={})

    with pytest.raises(ValueError, match="self.distinct_id not set"):
        customerio.identify({customerio.profile_properties.email: "test@example.com"})


def test_init_unknown_consumer() -> None:
    """Test initialization with unknown consumer."""
    with pytest.raises(ValueError, match="Unknown consumer: .UnknownConsumer"):
        CustomerIOTrack(settings={"customerio.consumer": ".UnknownConsumer"})


def test_init_unknown_events() -> None:
    """Test initialization with unknown events."""
    with pytest.raises(ValueError, match="Unknown events: .UnknownEvents"):
        CustomerIOTrack(settings={"customerio.events": ".UnknownEvents"})


def test_init_unknown_event_properties() -> None:
    """Test initialization with unknown event properties."""
    with pytest.raises(
        ValueError, match="Unknown event_properties: .UnknownEventProperties"
    ):
        CustomerIOTrack(
            settings={"customerio.event_properties": ".UnknownEventProperties"}
        )


def test_init_unknown_profile_properties() -> None:
    """Test initialization with unknown profile properties."""
    with pytest.raises(
        ValueError, match="Unknown profile_properties: .UnknownProfileProperties"
    ):
        CustomerIOTrack(
            settings={"customerio.profile_properties": ".UnknownProfileProperties"}
        )


def test_init_unknown_profile_meta_properties() -> None:
    """Test initialization with unknown profile meta properties."""
    with pytest.raises(
        ValueError,
        match="Unknown profile_meta_properties: .UnknownProfileMetaProperties",
    ):
        CustomerIOTrack(
            settings={
                "customerio.profile_meta_properties": ".UnknownProfileMetaProperties"
            }
        )


def test_init_with_custom_classes() -> None:
    """Test initialization with custom class instances."""
    custom_consumer = MockedConsumer()
    custom_events = Events()
    custom_event_properties = EventProperties()
    custom_profile_properties = ProfileProperties()
    custom_profile_meta_properties = ProfileMetaProperties()

    customerio = CustomerIOTrack(settings={}, distinct_id="test-id")
    customerio.consumer = custom_consumer
    customerio.events = custom_events
    customerio.event_properties = custom_event_properties
    customerio.profile_properties = custom_profile_properties
    customerio.profile_meta_properties = custom_profile_meta_properties

    assert customerio.consumer is custom_consumer
    assert customerio.events is custom_events
    assert customerio.event_properties is custom_event_properties
    assert customerio.profile_properties is custom_profile_properties
    assert customerio.profile_meta_properties is custom_profile_meta_properties


def test_init_with_object_instances() -> None:
    """Test initialization by passing object instances directly in settings."""
    custom_consumer = MockedConsumer()
    custom_events = Events()
    custom_event_properties = EventProperties()
    custom_profile_properties = ProfileProperties()
    custom_profile_meta_properties = ProfileMetaProperties()

    # Pass objects directly instead of strings
    customerio = CustomerIOTrack(
        settings={
            "customerio.consumer": custom_consumer,
            "customerio.events": custom_events,
            "customerio.event_properties": custom_event_properties,
            "customerio.profile_properties": custom_profile_properties,
            "customerio.profile_meta_properties": custom_profile_meta_properties,
        },
        distinct_id="test-id",
    )

    # Verify objects are used directly (not string-resolved)
    assert customerio.consumer is custom_consumer
    assert customerio.events is custom_events
    assert customerio.event_properties is custom_event_properties
    assert customerio.profile_properties is custom_profile_properties
    assert customerio.profile_meta_properties is custom_profile_meta_properties


def test_track_event_with_restricted_properties() -> None:
    """Test tracking event with restricted properties."""
    import typing as t

    @dataclass(frozen=True)
    class RestrictedEvent:
        name: str
        properties: t.Optional[t.List[Property]] = None

    @dataclass(frozen=True)
    class CustomEventProperties(EventProperties):
        allowed: Property = Property("allowed")

    @dataclass(frozen=True)
    class RestrictedEvents:
        restricted: RestrictedEvent = RestrictedEvent(
            "Restricted Event", [Property("allowed")]
        )

    customerio = CustomerIOTrack(settings={}, distinct_id="foo-123")
    customerio.events = RestrictedEvents()
    customerio.event_properties = CustomEventProperties()

    # Should work with allowed property
    customerio.track(
        customerio.events.restricted, {customerio.event_properties.allowed: "value"}
    )

    # Should fail with disallowed property
    with pytest.raises(
        ValueError, match="Property '.*' must be a member of Event.properties"
    ):
        customerio.track(
            customerio.events.restricted, {customerio.event_properties.title: "value"}
        )


def test_init_buffered_consumer_import_error() -> None:
    """Test BufferedConsumer initialization when customerio package not installed."""
    with mock.patch.dict("sys.modules", {"customerio": None}):
        with pytest.raises(ImportError, match="customerio package is not installed"):
            CustomerIOTrack(
                settings={
                    "customerio.consumer": ".consumer.BufferedConsumer",
                    "customerio.tracking.site_id": "site123",
                    "customerio.tracking.api_key": "key123",
                }
            )


def test_init_buffered_consumer_with_region() -> None:
    """Test BufferedConsumer initialization with custom region."""
    from customerio import Regions

    with mock.patch("customerio.CustomerIO") as mock_cio:
        CustomerIOTrack(
            settings={
                "customerio.consumer": ".consumer.BufferedConsumer",
                "customerio.tracking.site_id": "site123",
                "customerio.tracking.api_key": "key123",
                "customerio.tracking.region": "eu",
            }
        )
        mock_cio.assert_called_once_with(
            site_id="site123", api_key="key123", region=Regions.EU
        )


def test_init_buffered_consumer_with_invalid_region() -> None:
    """Test BufferedConsumer initialization with invalid region raises error."""
    import pytest

    with pytest.raises(
        ValueError, match="Unsupported region 'invalid'. Valid regions are: 'us', 'eu'"
    ):
        CustomerIOTrack(
            settings={
                "customerio.consumer": ".consumer.BufferedConsumer",
                "customerio.tracking.site_id": "site123",
                "customerio.tracking.api_key": "key123",
                "customerio.tracking.region": "invalid",
            }
        )


def test_flush_callback() -> None:
    """Test that flush callback is properly registered."""
    from pyramid_customerio.track import customerio_flush

    # Mock event and request
    request = mock.Mock(spec=[])
    response = mock.Mock()

    # Mock customerio with consumer
    customerio = mock.Mock()
    request.customerio = customerio
    request.add_response_callback = mock.Mock()

    event = mock.Mock()
    event.request = request

    # Call flush registration
    customerio_flush(event)

    # Verify callback was registered
    request.add_response_callback.assert_called_once()

    # Get the callback function and call it
    flush_callback = request.add_response_callback.call_args[0][0]
    flush_callback(request, response)

    # Verify consumer.flush was called
    customerio.consumer.flush.assert_called_once()


def test_flush_callback_no_customerio() -> None:
    """Test flush callback when customerio was never accessed."""
    from pyramid_customerio.track import customerio_flush

    # Mock event and request without customerio
    request = mock.Mock(spec=[])
    response = mock.Mock()

    # No customerio attribute
    request.add_response_callback = mock.Mock()

    event = mock.Mock()
    event.request = request

    # Call flush registration
    customerio_flush(event)

    # Get the callback function and call it
    flush_callback = request.add_response_callback.call_args[0][0]
    flush_callback(request, response)

    # Should not raise an error
