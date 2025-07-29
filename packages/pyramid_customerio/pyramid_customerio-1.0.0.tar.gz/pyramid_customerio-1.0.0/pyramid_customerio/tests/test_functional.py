"""Functional tests against a real Pyramid app."""

from pyramid.config import Configurator
from pyramid.request import Request
from pyramid.router import Router
from pyramid.view import view_config
from pyramid_customerio.consumer import Endpoint
from testfixtures import LogCapture
from unittest import mock
from webtest import TestApp

import structlog
import typing as t


@view_config(route_name="hello", renderer="json", request_method="GET")
def hello(request: Request) -> t.Dict[str, str]:
    """Say hello."""
    # mocking that request has a user object
    request.user = mock.MagicMock(spec="distinct_id".split())
    request.user.distinct_id = "foo-123"

    # provide access to Pyramid request in WebTest response
    request.environ["paste.testing_variables"]["app_request"] = request

    request.customerio.identify({request.customerio.profile_properties.name: "Bob"})
    request.customerio.track(
        request.customerio.events.page_viewed,
        {request.customerio.event_properties.path: "/hello"},
    )
    return {"hello": "world"}


@view_config(route_name="bye", renderer="json", request_method="GET")
def bye(request: Request) -> t.Dict[str, str]:
    """Say bye."""
    return {"bye": "bye"}  # pragma: no cover


def app(settings) -> Router:
    """Create a dummy Pyramid app."""
    structlog.configure(
        processors=[structlog.processors.KeyValueRenderer(sort_keys=True)],
        logger_factory=structlog.stdlib.LoggerFactory(),
    )

    with Configurator() as config:
        config.add_route("hello", "/hello")
        config.add_route("bye", "/bye")
        config.scan(".")

        config.registry.settings.update(**settings)
        config.include("pyramid_customerio")

        return config.make_wsgi_app()


def test_MockedConsumer() -> None:
    """Test that request.customerio works as expected with MockedConsumer."""
    with LogCapture() as logs:
        testapp = TestApp(app({"pyramid_heroku.structlog": True}))

        # do two requests to make sure logs are not flooded with messages
        # on every request
        res = testapp.get("/hello", status=200)
        res = testapp.get("/hello", status=200)
        assert res.json == {"hello": "world"}

    logs.check(
        (
            "pyramid_customerio",
            "INFO",
            "consumer='MockedConsumer' event='Customer.io configured' "
            "event_properties='EventProperties' events='Events' "
            "profile_meta_properties='ProfileMetaProperties' "
            "profile_properties='ProfileProperties'",
        ),
        (
            "pyramid_customerio",
            "WARNING",
            "event='Customer.io is in testing mode, no messages will be sent!'",
        ),
    )

    assert res.app_request.customerio.consumer.flushed is True
    assert res.app_request.customerio.consumer.mocked_messages == [
        {
            "endpoint": Endpoint.identify,
            "msg": {"id": "foo-123", "name": "Bob"},
        },
        {
            "endpoint": Endpoint.track,
            "msg": {
                "id": "foo-123",
                "name": "Page Viewed",
                "Path": "/hello",
            },
        },
    ]


def test_no_user() -> None:
    """Test that the integration works when there's no request.user."""

    @view_config(route_name="no_user", renderer="json", request_method="GET")
    def no_user(request: Request) -> t.Dict[str, str]:
        request.environ["paste.testing_variables"]["app_request"] = request
        # Should not raise error even without user
        return {"no_user": "test"}

    with Configurator() as config:
        config.add_route("no_user", "/no_user")
        config.add_view(
            no_user, route_name="no_user", renderer="json", request_method="GET"
        )
        config.include("pyramid_customerio")
        testapp = TestApp(config.make_wsgi_app())

    res = testapp.get("/no_user", status=200)
    assert res.json == {"no_user": "test"}

    # Should have no distinct_id set
    assert res.app_request.customerio.distinct_id is None


def test_no_customerio_access() -> None:
    """Test that nothing breaks if customerio is never accessed."""

    @view_config(route_name="no_access", renderer="json", request_method="GET")
    def no_access(request: Request) -> t.Dict[str, str]:
        request.environ["paste.testing_variables"]["app_request"] = request
        # Don't access request.customerio at all
        return {"no_access": "test"}

    with Configurator() as config:
        config.add_route("no_access", "/no_access")
        config.add_view(
            no_access, route_name="no_access", renderer="json", request_method="GET"
        )
        config.include("pyramid_customerio")
        testapp = TestApp(config.make_wsgi_app())

    res = testapp.get("/no_access", status=200)
    assert res.json == {"no_access": "test"}

    # Should not have customerio in request dict
    assert "customerio" not in res.app_request.__dict__


@mock.patch("customerio.CustomerIO")
def test_BufferedConsumer_fallback(mock_cio) -> None:
    """Test that BufferedConsumer falls back to MockedConsumer when credentials missing."""

    @view_config(route_name="fallback", renderer="json", request_method="GET")
    def fallback(request: Request) -> t.Dict[str, str]:
        request.user = mock.MagicMock(spec="distinct_id".split())
        request.user.distinct_id = "foo-123"
        request.environ["paste.testing_variables"]["app_request"] = request

        request.customerio.track(request.customerio.events.page_viewed)
        return {"fallback": "test"}

    with Configurator() as config:
        config.add_route("fallback", "/fallback")
        config.add_view(
            fallback, route_name="fallback", renderer="json", request_method="GET"
        )
        config.registry.settings.update(
            {
                "customerio.consumer": ".consumer.BufferedConsumer",
                # Missing site_id and api_key - should fallback to MockedConsumer
            }
        )
        config.include("pyramid_customerio")
        testapp = TestApp(config.make_wsgi_app())

    res = testapp.get("/fallback", status=200)
    assert res.json == {"fallback": "test"}

    # Should have fallen back to MockedConsumer
    from pyramid_customerio.consumer import MockedConsumer

    assert isinstance(res.app_request.customerio.consumer, MockedConsumer)

    # Should not have called Customer.io client creation
    mock_cio.assert_not_called()


def test_standard_logging() -> None:
    """Test that standard logging works when structlog is disabled."""
    with LogCapture() as logs:
        testapp = TestApp(app({"pyramid_heroku.structlog": False}))
        res = testapp.get("/hello", status=200)
        assert res.json == {"hello": "world"}

    logs.check(
        (
            "pyramid_customerio",
            "INFO",
            "Customer.io configured consumer=MockedConsumer, events=Events, "
            "event_properties=EventProperties, profile_properties=ProfileProperties, "
            "profile_meta_properties=ProfileMetaProperties",
        ),
        (
            "pyramid_customerio",
            "WARNING",
            "Customer.io is in testing mode, no messages will be sent!",
        ),
    )
