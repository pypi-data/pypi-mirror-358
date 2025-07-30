import logging
from sparrow_cloud.utils.get_settings_value import get_settings_value

logger = logging.getLogger(__name__)

def get_user_token(user_id):
    """
    get user token
    :param user_id:
    """
    service_conf = get_settings_value("SERVICE_CONF")
    return {"iss":"sparrow_cloud", "uid":user_id, "src":service_conf["NAME"]}


def get_app_token():
    """
    get app token
    """
    service_conf = get_settings_value("SERVICE_CONF")
    return {"iss":"sparrow_cloud", "uid":service_conf["NAME"], "src":service_conf["NAME"]}