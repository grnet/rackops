Adding a provider
=================

1. Create a file with the name of the provider under `rackops/providers/`
2. Implement a provider class inheriting `ProviderBase` which is defined
in `rackops/providers/base.py`. The provider class is required to implement
all methods that raise a `NonImplementedError` on `ProviderBase`.
The provider class can also override methods defined on `ProviderBase` if they
don't apply to the provider implemented.
3. Import the new provider class on `rackops/rackops.py` and add a mapping
between the provider name and the provider class on the `_providers_table`
method.

Adding a host
=============

1. Create a file with the name of the host under `rackops/hosts/`
2. Implement a host class inheriting `HostBase` which is defined in
`rackops/hosts/base.py`. The host class is required to implement all methods
that raise a `NonImplementedError` on the `HostBase` class. Same as with
providers, other methods can be overrided.
3. Import the new host class on `rackops/rackops.py` and add a mapping
between the host name and the host class on the `_hosts_table` method.
