import aioboto3
from typing import List, Dict, Any
from .config import Config

class EC2Manager:
    def __init__(self, config: Config):
        self.config = config
        self.session = aioboto3.Session(
            aws_access_key_id=self.config.aws_access_key_id,
            aws_secret_access_key=self.config.aws_secret_access_key,
            region_name=self.config.aws_region,
        )

    async def get_instances_by_tag(self, tag_key: str, tag_value: str, states: List[str] = ['running', 'stopped']) -> List[Dict[str, Any]]:
        """Finds EC2 instances based on a specific tag."""
        instances = []
        async with self.session.client("ec2") as ec2:
            paginator = ec2.get_paginator('describe_instances')
            async for page in paginator.paginate(
                Filters=[
                    {'Name': f'tag:{tag_key}', 'Values': [tag_value]},
                    {'Name': 'instance-state-name', 'Values': states}
                ]
            ):
                for reservation in page['Reservations']:
                    for instance in reservation['Instances']:
                        instances.append(instance)
        return instances

    async def get_instances_by_id(self, instance_ids: List[str], states: List[str] = ['running', 'stopped']) -> List[Dict[str, Any]]:
        """Finds EC2 instances based on a list of IDs."""
        instances = []
        async with self.session.client("ec2") as ec2:
            paginator = ec2.get_paginator('describe_instances')
            async for page in paginator.paginate(
                InstanceIds=instance_ids,
                Filters=[{'Name': 'instance-state-name', 'Values': states}]
            ):
                for reservation in page['Reservations']:
                    for instance in reservation['Instances']:
                        instances.append(instance)
        return instances

    async def start_instances(self, instance_ids: List[str]) -> Dict[str, Any]:
        """Starts the specified EC2 instances."""
        if not instance_ids:
            return {"StartingInstances": []}
        async with self.session.client("ec2") as ec2:
            return await ec2.start_instances(InstanceIds=instance_ids)

    async def stop_instances(self, instance_ids: List[str]) -> Dict[str, Any]:
        """Stops the specified EC2 instances."""
        if not instance_ids:
            return {"StoppingInstances": []}
        async with self.session.client("ec2") as ec2:
            return await ec2.stop_instances(InstanceIds=instance_ids)

    async def reboot_instances(self, instance_ids: List[str]) -> Dict[str, Any]:
        """Reboots the specified EC2 instances."""
        if not instance_ids:
            return {}
        async with self.session.client("ec2") as ec2:
            return await ec2.reboot_instances(InstanceIds=instance_ids)

    async def wait_for_status(self, instance_ids: List[str], status: str):
        """Waits for instances to reach a specific status."""
        if not instance_ids:
            return
        async with self.session.client("ec2") as ec2:
            waiter = ec2.get_waiter(status)
            await waiter.wait(InstanceIds=instance_ids)
