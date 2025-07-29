# Copyright 2013, 2016 Red Hat, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import json

from config_tempest.constants import LOG
from config_tempest.services.base import VersionedService


class NetworkService(VersionedService):
    def set_extensions(self):
        body = self.do_get(self.service_url + '/v2.0/extensions.json')
        body = json.loads(body)
        self.extensions = list(map(lambda x: x['alias'], body['extensions']))

    def set_versions(self):
        super(NetworkService, self).set_versions(top_level=False)

    def create_tempest_networks(self, conf, network):
        LOG.info("Setting up network")
        self.client = self.client.networks
        self.create_tempest_networks_neutron(conf, network)

    def create_tempest_networks_neutron(self, conf, public_network):
        self._public_network = public_network
        self._public_network_name = None
        self._public_network_id = None
        # if user supplied the network we should use
        if public_network:
            self._supplied_network()
        # no network id provided, try to auto discover a public network
        else:
            self._discover_network()
        if self._public_network_id is not None:
            conf.set('network', 'public_network_id', self._public_network_id)
        if self._public_network_name is not None:
            conf.set('network', 'floating_network_name',
                     self._public_network_name)

    def get_service_extension_key(self):
        return 'api_extensions'

    def _supplied_network(self):
        LOG.info("Looking for existing network: %s",
                 self._public_network)
        given_net = self._public_network
        # check if network exists
        network_list = self.client.list_networks()
        for network in network_list['networks']:
            if network['id'] == given_net or network['name'] == given_net:
                self._public_network_name = network['name']
                self._public_network_id = network['id']
                break
        else:
            raise ValueError('provided network: {0} was not found.'
                             ''.format(self._public_network))

    def _discover_network(self):
        LOG.info("No network supplied, trying auto discover for an external "
                 "network while prioritizing the one called public, if not "
                 "found, the network discovered last will be used.")
        network_list = self.client.list_networks()

        for network in network_list['networks']:
            if network['router:external'] and network['subnets']:
                if network['status'] != 'ACTIVE':
                    continue
                self._public_network_id = network['id']
                self._public_network_name = network['name']
                # usually the external network we use is called 'public'
                if network['name'] == 'public':
                    # we found a network called public, end the loop
                    break
        # Couldn't find an existing external network
        if not self._public_network_name:
            LOG.error("No external networks found. "
                      "Please note that any test that relies on external "
                      "connectivity would most likely fail.")
            return
        LOG.info("Setting %s as the public network for tempest",
                 self._public_network_id)

    @staticmethod
    def get_service_type():
        return ['network']

    @staticmethod
    def get_codename():
        return 'neutron'
