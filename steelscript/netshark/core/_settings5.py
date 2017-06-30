# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from functools import partial

from _settings4 import Settings4, getted, \
    BasicSettingsFunctionality, ProfilerExport


class DPIResource(BasicSettingsFunctionality):
    def _get_by_name(self, name):
        for obj in self.data:
            if obj.get('name') == name:
                return obj
        return None

    def _get_by_priority(self, priority):
        obj = self.data[priority]
        if obj.get('priority') != priority:
            return None
        else:
            return obj

    def _port_string_to_port_list(self, port_string, protocol='TCP'):
        if port_string is not None:
            ports = [{'port_range': x.strip(), 'protocol': protocol}
                     for x in port_string.split(',')]
        else:
            ports = []
        return ports

    def _refresh_priorities(self):
        for i, obj in enumerate(self.data):
                obj['priority'] = i


class PortDefinitions(DPIResource):
    """Wrapper class and port definitions."""

    def __init__(self, api, srt_ports_api):
        super(PortDefinitions, self).__init__(api)
        self._srt_ports_api = srt_ports_api
        self._srtdata = None

    def get(self, force=False):
        if self._srtdata is None or force:
            self._srtdata = self._srt_ports_api.get()
        return super(PortDefinitions, self).get(force)

    @getted
    def save(self):
        super(PortDefinitions, self).save()
        self._srt_ports_api.update(self._srtdata)

    def _lookup_port(self, port):
        for port_obj in self.data:
            if port_obj['port'] == port:
                return port_obj
        return None

    @getted
    def add(self, name, port, protocol, srt):
        """Add a port definition

        :param str name: a name for the port

        :param int port: the port number

        :param str protocol: is the protocol the name is associated to
            can be `tcp` or `udp`

        :param bool srt: indicates if the port to be enabled as srt
            port

        """
        assert 0 < port < 65536
        assert srt is True or srt is False
        if protocol is not 'tcp' and protocol is not 'udp':
            raise ValueError('Protocol must be tcp or udp')

        port_obj = self._lookup_port(port)

        if port_obj is not None:
            if port_obj.get(protocol) is not None:
                raise ValueError('There is already a setting '
                                 'for port number {0}'.format(port))
            else:
                port_obj[protocol] = name
        else:
            self.data.append({protocol: name, 'port': port})

        if srt and protocol == 'tcp':
            if port not in self._srtdata:
                self._srtdata.append(port)

    @getted
    def remove(self, name, port):
        """Remove port identified by name and port number from the Port Definitions

        :param str name: a name for the port

        :param int port: the port number

        """
        assert 0 < port < 65536

        port_obj = self._lookup_port(port)

        if port_obj is None:
            raise ValueError('Port number {0} has no configuration '
                             'in the current netshark'.format(port))

        if port_obj.get('tcp') == name:
            del port_obj['tcp']
            if port in self._srtdata:
                self._srtdata.remove(port)

        if port_obj.get('udp') == name:
            del port_obj['udp']

        if port_obj.get('tcp') is None and port_obj.get('udp') is None:
            self.data.remove(port_obj)


class PortGroups(DPIResource):
    """Wrapper class and port group definitions."""

    @getted
    def add(self, name, tcp_ports=None, udp_ports=None, priority=None):
        # sort the list first by priority
        self.data.sort(key=lambda k: k['priority'])

        obj = self._get_by_name(name)

        if obj is not None:
            raise ValueError('A port group with the same name already exists')

        priority = priority or len(self.data)

        tcp = self._port_string_to_port_list(tcp_ports, 'TCP')

        udp = self._port_string_to_port_list(udp_ports, 'UDP')

        self.data.insert(priority, {'name': name,
                                    'priority': priority,
                                    'ports': tcp+udp
                                    })

        self._refresh_priorities()

    @getted
    def remove(self, name=None, priority=None):
        """Remove a port group by name or by priority

        It accepts one of name or priority. If name and priority are issued
        it will remove the rule named `name` only if it matches `priority`

        :param str name: the name of the port group

        :param int priority: the priority of the port group

        """
        if name is None and priority is None:
            raise ValueError('name and priority cannot be both None')

        obj = None

        if name is not None:
            obj = self._get_by_name(name)

        if priority is not None:
            obj = self._get_by_priority(priority)

        if name is not None and priority is not None:
            if obj.get('name') != name:
                raise ValueError(
                    'Port group with priority {0} has a '
                    'different name than {1}'.format(priority, name)
                )

        if obj is not None:
            self.data.remove(obj)
        else:
            if name is not None and priority is None:
                raise ValueError('Impossible to find port group '
                                 'with name {0}'.format(name))
            if name is None and priority is not None:
                raise ValueError('Impossible to find port group '
                                 'with priority {0}'.format(priority))
            if name is not None and priority is not None:
                raise ValueError(
                    'Impossible to find port group '
                    'with name {0} and priority {1}'.format(name, priority)
                )


class L4Mapping(PortGroups):
    """Wrapper class around Layer 4 Mappings."""

    @getted
    def add(self, name, hosts, tcp_ports=None, udp_ports=None, priority=None):
        """Add a l4 mapping rule

        :param str name: the name of the rule

        :param str hosts: comma separated list of hosts with optional
                          subnet mask

        :param str tcp_ports: comma separated list of ports or port range

        :param str udp_ports: comma separated list of ports or port range

        """
        assert tcp_ports is not None and udp_ports is not None

        priority = priority or len(self.data)

        obj = self._get_by_name(name)

        if obj is not None:
            raise ValueError('l4 mapping with name {0} '
                             'already exists'.format(name))

        tcp = self._port_string_to_port_list(tcp_ports, 'TCP')
        udp = self._port_string_to_port_list(udp_ports, 'UDP')

        self.data.insert(
            priority,
            {'name': name,
             'hosts': [x.strip() for x in hosts.split(',')],
             'priority': priority,
             'ports': tcp+udp
             }
        )

        self._refresh_priorities()

    @getted
    def remove(self, name=None, priority=None):
        """Remove a l4 mapping rule

        It accepts one of name or priority. If name and priority are issued
        it will remove the rule named `name` only if it matches `priority`

        :param str name: the name of the l4 mapping

        :param int priority: the priority of the l4 mapping
        """
        super(L4Mapping, self).remove(name, priority)


class CustomApplications(DPIResource):
    """Wrapper class around custom application definitions."""

    @getted
    def add(self, name, uri):
        """Add a custom application rule

        :param str name: the name of the rule

        :param str uri: a string representing a uri

        """

        obj = self._get_by_name(name)

        if obj is not None:
            raise ValueError('l4 mapping with name {0} '
                             'already exists'.format(name))

        self.data.append({'name': name, 'uri': uri})

    @getted
    def remove(self, name):
        """Remove a custom application rule

        :param str name: the name of the rule

        """
        obj = self._get_by_name(name)
        if obj is not None:
            self.data.remove(obj)
        else:
            raise ValueError('The rule with name {0} '
                             'does not exist'.format(name))


class ProfilerExport(ProfilerExport):
    """Wrapper class around Profiler Export"""

    def _lookup_profiler(self, address):
        for p in self.data['profilers']:
            if p['address'] == address:
                return p
        msg = ('No netprofiler with address {0} has been '
               'found in the configuration'.format(address))
        raise ValueError(msg)

    @getted
    def sync_dpi_with_profiler(self, address):
        """Helper method to select the current profiler to sync DPI with.

        This method modifes `self.data` to reflect the changes.  save() must
        be called to push the changes to the NetShark.

        """
        p = self._lookup_profiler(address)
        for prof in self.data['profilers']:
            if 'sync' in prof:
                del prof['sync']
        p['sync'] = {"sync_port_names": True,
                     "sync_port_groups": True,
                     "sync_layer4_mappings": True,
                     "sync_custom_applications": True}

    @getted
    def unsync_dpi_with_profiler(self, address):
        """Helper method to select the current profiler to sync DPI with.

        This method modifes `self.data` to reflect the changes.  save() must
        be called to push the changes to the NetShark.

        """
        p = self._lookup_profiler(address)
        if 'sync' in p:
            del p['sync']


class Alerts(BasicSettingsFunctionality):
    def test_snmp(self, obj):
        """Sends a test SNMP trap

        :param dict obj: object representing the trap to send.

        The ``obj`` must be of the form:

        .. code-block:: python

            {"address":"trap.riverbed.com","version":"V1","community":"test"}

        or

        .. code-block:: python

            {"address":"trap.riverbed.com","community":"public","version":"V2C"}

        or

        .. code-block:: python

            {
                "address": "trap.riverbed.com",
                "version": "V3",
                "username": "test",
                "engine_id": "testengine",
                "security_level": "AUTH_PRIVACY",
                "authentication": {"protocol":"MD5",
                                   "passphrase":"testpassword"},
                "privacy": {"protocol":"DES",
                            "passphrase":"testpassword"}
            }

        """
        return self._api.send_test_snmp(obj)

    def test_smtp(self, address, to_address, from_address, port=25):
        """Sends a test email via SMTP."""
        obj = {
            'smtp_server_address': address,
            'smtp_server_port': port,
            'to_address': to_address,
            'from_address': from_address
            }
        return self._api.send_test_smtp(obj)


class Settings5(Settings4):
    """Interface to various configuration settings on the netshark appliance.
    Version 5.0 API
    """

    def __init__(self, shark):
        super(Settings5, self).__init__(shark)
        self.port_definitions = PortDefinitions(shark.api.port_definitions,
                                                shark.api.srt_ports)
        self.port_groups = PortGroups(shark.api.port_groups)
        self.l4_mapping = L4Mapping(shark.api.l4_mappings)
        self.custom_applications = CustomApplications(
            shark.api.custom_applications
        )
        self.profiler_export = ProfilerExport(shark.api.settings)
        self.snmp = BasicSettingsFunctionality(shark.api.snmp)
        self.alerts = Alerts(shark.api.alerts)

        def raise_notimplemented_error(append):
            msg = ("This functionality has been replaced in this version of "
                   "NetShark with the DPI classes. "
                   "Please refer to the documentation for more information or "
                   "look at the instance of %s" % append)
            raise NotImplementedError(msg)

        # remove API 4.0 specific
        self.get_protocol_groups = partial(
            raise_notimplemented_error,
            'NetShark.settings.groups_definitions'
        )
        self.update_protocol_groups = partial(
            raise_notimplemented_error,
            'NetShark.settings.groups_definitions'
        )
        self.get_protocol_names = partial(
            raise_notimplemented_error,
            'NetShark.settings.l4_mapping'
        )
        self.update_protocol_names = partial(
            raise_notimplemented_error,
            'NetShark.settings.l4_mapping'
        )
