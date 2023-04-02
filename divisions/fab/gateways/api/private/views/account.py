import typing

import simplejson
from django import http
from django import views

from divisions.account import services as account_services
from divisions.fab.common import services as fab_common_services
from divisions.fab.gateways.api.private.schemas import account as account_schemas


class AccountRegistration(views.View):
    def post(
        self, request: http.HttpRequest, *args: typing.Any, **kwargs: typing.Any
    ) -> http.HttpResponse:
        try:
            payload = simplejson.loads(request.body.decode("utf8"))
        except Exception:
            return http.HttpResponse(
                headers={"Content-Type": "application/json"},
                content=simplejson.dumps({"error": {"title": "Payload is not valid."}}),
                status=400,
            )

        validated_data = fab_common_services.validate_data_schema(
            data=payload, schema=account_schemas.AccountRegistration()
        )
        if not validated_data:
            return http.HttpResponse(
                headers={"Content-Type": "application/json"},
                content=simplejson.dumps({"error": {"title": "Payload is not valid."}}),
                status=400,
            )

        try:
            account_services.register_user(
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                email=validated_data['email'],
                password=validated_data['password'],
            )
        except:
            pass

        return http.HttpResponse(
            headers={"Content-Type": "application/json"},
            content=simplejson.dumps({"data": {"attributes": validated_data}}),
            status=201,
        )
