import asyncio
import aioboto3
from typing import List, Dict, Any

from .config import Config

class LightsailManager:
    def __init__(self, config: Config):
        self.config = config
        self.session = aioboto3.Session(
            aws_access_key_id=self.config.aws_access_key_id,
            aws_secret_access_key=self.config.aws_secret_access_key,
            region_name=self.config.aws_region,
        )

    async def get_all_instances(self) -> List[Dict[str, Any]]:
        """Gets a list of all Lightsail instances."""
        async with self.session.client("lightsail") as lightsail:
            response = await lightsail.get_instances()
            return response.get('instances', [])

    async def start_instance(self, instance_name: str) -> Dict[str, Any]:
        """Starts a specific Lightsail instance."""
        async with self.session.client("lightsail") as lightsail:
            return await lightsail.start_instance(instanceName=instance_name)

    async def stop_instance(self, instance_name: str) -> Dict[str, Any]:
        """Stops a specific Lightsail instance."""
        async with self.session.client("lightsail") as lightsail:
            return await lightsail.stop_instance(instanceName=instance_name)

    async def wait_for_status(self, instance_name: str, target_status: str, timeout: int = 300, delay: int = 15):
        """Waits for a lightsail instance to reach a specific status."""
        async with self.session.client("lightsail") as lightsail:
            elapsed_time = 0
            while elapsed_time < timeout:
                response = await lightsail.get_instance(instanceName=instance_name)
                instance = response.get('instance')
                if instance and instance.get('state', {}).get('name') == target_status:
                    return
                await asyncio.sleep(delay)
                elapsed_time += delay
            raise asyncio.TimeoutError(f"Instance {instance_name} did not reach {target_status} within {timeout} seconds.")
