import datetime

from .models import (
    Contract,
    STATE_NOTPROCESSED,#Повторная обработка
)


def timing_check(get_response):
    def middleware(request):
        contracts = Contract.objects.filter(infinity_plain=False, plain_later__isnull=False)
        for contract in contracts:
            if contract.plain_later is None:
                continue

            if datetime.datetime.now(datetime.timezone.utc) >= contract.plain_later:
                contract.plain_later = None
                contract.state = STATE_NOTPROCESSED
                contract.save()

        response = get_response(request)
        return response
    return middleware