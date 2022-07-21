from urls import SERVICE_ID
from database.models import *


def toogle_testing(service_id, switch=False):
    try:
        service = (Services
                    .select()
                    .where(Services.id_service == service_id).get())
        if switch:
            service.test_mode = 1
        else:
            service.test_mode = 0
        service.save()
        return True

    except Exception as error:
        print("error", error)
        return False


def is_testing_enable():
    service_id = 1
    try:
        is_testing = (Services
                                .select()
                                .where(Services.id_service == SERVICE_ID))
        var = is_testing.dicts().get()
        if var['test_mode']:
            return True
        else:
            return False

    except Exception as error:
        print("error", error)
        return False
