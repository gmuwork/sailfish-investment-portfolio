import datetime
import logging
import uuid

import jwt
from django.conf import settings
from django.core import mail as django_mail_service
from django.core import exceptions as django_core_exceptions
from django.contrib.auth import models as auth_models
from django.contrib.auth import password_validation
from django.db import transaction as django_db_transaction
from urllib import parse as url_parser

from divisions.account import constants as account_constants
from divisions.account import enums as account_enums
from divisions.account import models as account_models
from divisions.account import exceptions as account_exceptions
from divisions.common import utils as common_utils

logger = logging.getLogger(__name__)

_LOG_PREFIX = "[ACCOUNT-SERVICE]"


def register_user(first_name: str, last_name: str, email: str, password: str) -> None:
    user = auth_models.User.objects.filter(email=email).first()
    if user:
        msg = "User (email={}) already exists".format(email)
        logger.info("{} {}.".format(_LOG_PREFIX, msg))
        raise account_exceptions.UserAlreadyExists()

    try:
        password_validation.validate_password(password=password)
    except django_core_exceptions.ValidationError as e:
        logger.exception(
            "{} User (email={}) password is not valid. Error: {}.".format(
                _LOG_PREFIX, email, common_utils.get_exception_message(exception=e)
            )
        )
        raise account_exceptions.UserInvalidPasswordError(
            "User (email={}) password is not valid".format(email)
        )

    with django_db_transaction.atomic():
        user = auth_models.User.objects.create_user(
                username=email,
                email=email,
                password=password,
                is_active=False,
                first_name=first_name,
                last_name=last_name,
            )
        account_profile = account_models.AccountProfile.objects.create(
            user=user,
            status=account_enums.AccountStatus.PENDING_ACTIVATION.value,
        )

    logger.info(
        "{} Registered new user (id={}, email={}, active=False).".format(
            _LOG_PREFIX, user.id, user.email
        )
    )

    email_template = open(
        "{}/templates/user-registration-confirmation.html".format(settings.BASE_DIR),
        "r",
    ).read()
    django_mail_service.send_mail(
        subject="Account activation",
        message=email_template.format(
            user_name="{} {}".format(first_name, last_name),
            confirmation_link=url_parser.urljoin(
                settings.BASE_DOMAIN,
                get_user_activation_token(user=user),
            ),
            contact_email=settings.DEFAULT_FROM_EMAIL,
        ),
        recipient_list=[user.email],
        from_email=None,
        fail_silently=True,
    )

    logger.info(
        "{} Sent confirmation email to user (id={}, email={}).".format(
            _LOG_PREFIX, user.id, user.email
        )
    )


def get_user_activation_token(user: auth_models.User) -> str:
    return jwt.encode(
        {
            "iss": settings.BASE_DOMAIN,
            "iat": datetime.datetime.utcnow(),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=4),
            "user_email": user.email,
            "jti": str(uuid.uuid4()),
        },
        settings.JWT_SECRET_TOKEN,
        algorithm="HS256",
    )
