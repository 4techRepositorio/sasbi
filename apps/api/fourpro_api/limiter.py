from slowapi import Limiter

from fourpro_api.rate_limit_key import client_key_for_rate_limit

limiter = Limiter(key_func=client_key_for_rate_limit)
