
#################################################
# HolAdo (Holistic Automation do)
#
# (C) Copyright 2021-2025 by Eric Klumpp
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
#################################################

from holado_core.common.exceptions.functional_exception import FunctionalException
import time
import logging
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado.common.handlers.object import DeleteableObject
from holado_core.common.tools.tools import Tools

logger = logging.getLogger(__name__)

try:
    import docker
    with_docker = True
except Exception as exc:
    if Tools.do_log(logger, logging.DEBUG):
        logger.debug(f"DockerClient is not available. Initialization failed on error: {exc}")
    with_docker = False


class DockerClient(object):
    @classmethod
    def is_available(cls):
        return with_docker
    
    def __init__(self):
        self.__client = docker.from_env()
        self.__containers = {}
        self.__volumes = {}
        
    @property
    def client(self):
        return self.__client
    
    def has_container(self, name, in_list = True):
        # Note: Even if name exists in __containers, it is possible that the container has been removed
        if in_list:
            c = self.__get_container_from_list(name)
            res = c is not None
        else:
            res = name in self.__containers
        return res
    
    def get_container(self, name):
        if name not in self.__containers:
            c = self.__get_container_from_list(name)
            if c:
                self.__containers[name] = DockerContainer(self, c)
        return self.__containers.get(name)
    
    def get_all_container_names(self):
        for _ in range(3):
            try:
                return [c.name for c in self.__client.containers.list(all=True)]
            except docker.errors.NotFound:
                pass
    
    def __get_container_from_list(self, name):
        res = None
        for _ in range(3):
            try:
                for c in self.__client.containers.list(all=True):
                    if c.name == name:
                        res = c
                        break
            except docker.errors.NotFound:
                pass
        return res
    
    def has_volume(self, name, in_list = False):
        res = name in self.__volumes
        if not res and in_list:
            v = self.__get_volume_from_list(name)
            res = v is not None
        return res
    
    def get_volume(self, name):
        if name not in self.__volumes:
            v = self.__get_volume_from_list(name)
            if v:
                self.__volumes[name] = DockerVolume(v)
        return self.__volumes.get(name)
    
    def get_all_volume_names(self):
        return [v.name for v in self.__client.volumes.list()]
    
    def __get_volume_from_list(self, name):
        res = None
        for v in self.__client.volumes.list():
            if v.name == name:
                res = v
                break
        return res
    
    def run_container(self, name, image, remove_existing=False, wait_running=True, auto_stop=True, **kwargs):
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Running docker container '{name}' with image '{image}' and arguments {kwargs}{', and waiting running status' if wait_running else ''}")
        
        # Manage remove if already existing
        cont = self.get_container(name)
        if cont:
            if remove_existing:
                if cont.status == "running":
                    if Tools.do_log(logger, logging.DEBUG):
                        logger.debug(f"Docker container '{name}' is running, stopping it before remove")
                    self.stop_container(name)
                
                if self.has_container(name):    # After stop, container is able to be automatically removed depending on its run parameters 
                    self.remove_container(name)
            else:
                logger.info(f"Docker container '{name}' is already running")
                return
        
        # Run container
        c = self.__client.containers.run(image, name=name, detach=True, **kwargs)
        container = DockerContainer(self, c)
        self.__containers[name] = container
        
        # Manage wait running status
        if wait_running:
            for _ in range(100):
                time.sleep(1)
                if container.status == "running":
                    break
        if container.status != "running":
            raise TechnicalException("Failed to run container of name '{}' (status: {})".format(name, container.status))
        else:
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"Run docker container '{name}' with image '{image}' and arguments {kwargs}{', and wait running status' if wait_running else ''}")
            
        # Set properties
        container.auto_stop = auto_stop
        
        return container
    
    def start_container(self, name, wait_running=True, **kwargs):
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Starting docker container '{name}' with arguments {kwargs}{', and waiting running status' if wait_running else ''}")
        container = self.get_container(name)
        if not container:
            raise FunctionalException("Container of name '{}' doesn't exist")
        
        container.start(**kwargs)
        
        if wait_running:
            for _ in range(120):
                time.sleep(1)
                if container.status == "running":
                    break
        if container.status != "running":
            raise TechnicalException("Failed to run container of name '{}' (status: {})".format(name, container.status))
        else:
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"Started docker container '{name}' with arguments {kwargs}{', and waited running status' if wait_running else ''}")
        
    def stop_container(self, name):
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Stopping docker container of name '{name}'")
        if name not in self.__containers:
            raise FunctionalException("Unknown container of name '{}'".format(name))
        elif self.__containers[name].status != "running":
            raise FunctionalException("Container of name '{}' is not running (status: {})".format(name, self.__containers[name].status))
        
        self.__containers[name].stop()
        try:
            self.__containers[name].wait()
        except docker.errors.NotFound:
            # This exception occurs on containers automatically removed on stop
            pass
        
        if self.__containers[name].status == "running":
            raise FunctionalException("Failed to stop container of name '{}' (status: {})".format(name, self.__containers[name].status))
        else:
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"Stopped docker container of name '{name}'")
        
    def remove_container(self, name):
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Removing docker container of name '{name}'")
        if not self.has_container(name):
            raise FunctionalException(f"Container of name '{name}' doesn't exist")
        
        del self.__containers[name]
        self.client.api.remove_container(name)
        
        if self.has_container(name):
            raise FunctionalException(f"Failed to remove container of name '{name}'")
        else:
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"Removed docker container of name '{name}'")
        
class DockerContainer(DeleteableObject):
    def __init__(self, docker_client, container):
        super().__init__(container.name)
        
        self.__docker_client = docker_client
        self.__container = container
        self.__auto_stop = False
        
    def _delete_object(self):
        if self.auto_stop and self.__docker_client and self.__docker_client.has_container(self.name) \
                and self.__docker_client.get_container(self.name).status == "running":
            self.__docker_client.stop_container(self.name)
        
    @property
    def container(self):
        self.__container
        
    @property
    def status(self):
        try:
            self.__container.reload()
        except docker.errors.NotFound:
            return "removed"
        return self.__container.status
        
    @property
    def auto_stop(self):
        self.__auto_stop
        
    @auto_stop.setter
    def auto_stop(self, auto_stop):
        self.__auto_stop = auto_stop
    
    def start(self, **kwargs):
        return self.__container.start(**kwargs)
    
    def stop(self, **kwargs):
        return self.__container.stop(**kwargs)
    
    def wait(self, **kwargs):
        return self.__container.wait(**kwargs)
        
class DockerVolume(object):
    def __init__(self, volume):
        self.__volume = volume
        
    @property
    def volume(self):
        self.__volume
        
    @property
    def attributes(self):
        self.__volume.reload()
        return self.__volume.attrs
    
    def get_attribute(self, attr_path):
        names = attr_path.split('.')
        attrs = self.attributes
        res = attrs
        for i, name in enumerate(names):
            if name in res:
                res = res[name]
            else:
                raise FunctionalException(f"Attribute '{'.'.join(names[:i+1])}' doesn't exist (requested attribute: '{attr_path}' ; volume attributes: {attrs})")
        return res
    
