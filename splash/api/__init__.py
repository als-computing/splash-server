from splash.service import ServiceProvider

# context provides singleton access to a service provider, with
# the ability to set externally so that tests can mock the provider
# or it's dependencies
_context = {}


def set_service_provider(provider: ServiceProvider):
    # assert _context.get('provider') is None
    _context['provider'] = provider


def get_service_provider() -> ServiceProvider:
    return _context.get('provider')

