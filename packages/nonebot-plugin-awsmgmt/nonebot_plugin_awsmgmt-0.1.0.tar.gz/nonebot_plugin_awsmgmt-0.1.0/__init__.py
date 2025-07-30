import time
import re
from typing import Tuple, List, Optional, Dict, Any
from functools import wraps

from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata, get_plugin_config
from nonebot.params import CommandArg
from nonebot.adapters import Message
from nonebot.log import logger
from nonebot.exception import FinishedException

from .config import Config
from .ec2_manager import EC2Manager
from .cost_explorer_manager import CostExplorerManager
from .lightsail_manager import LightsailManager

__plugin_meta__ = PluginMetadata(
    name="AWS Manager",
    description="Manage AWS EC2, Lightsail, and Cost Explorer via commands.",
    usage=(
        "--- EC2 ---\n"
        "/ec2_start|stop|reboot|status [target]\n"
        "Target: tag:Key:Value | id:i-xxxx\n"
        "--- Lightsail ---\n"
        "/lightsail_list\n"
        "/lightsail_start|stop <instance_name>\n"
        "--- Cost ---\n"
        "/aws_cost today|month|month by_service"
    ),
    type="application",
    homepage="https://github.com/maxesisn/nonebot-plugin-awsmgmt",
    config=Config,
)

def handle_non_finish_exceptions(error_message: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except FinishedException:
                raise
            except Exception as e:
                matcher = args[0] if args else None
                logger.error(f"Error in {func.__name__}: {e}")
                if matcher:
                    await matcher.finish(error_message)
        return wrapper
    return decorator

# --- Init --- #
plugin_config = get_plugin_config(Config)
ec2_manager = EC2Manager(plugin_config)
cost_manager = CostExplorerManager(plugin_config)
lightsail_manager = LightsailManager(plugin_config)

# --- Command Matchers --- #
# EC2
ec2_start_matcher = on_command("ec2_start", aliases={"ec2启动"}, permission=SUPERUSER)
ec2_stop_matcher = on_command("ec2_stop", aliases={"ec2停止"}, permission=SUPERUSER)
ec2_reboot_matcher = on_command("ec2_reboot", aliases={"ec2重启"}, permission=SUPERUSER)
ec2_status_matcher = on_command("ec2_status", aliases={"ec2状态"}, permission=SUPERUSER)
# Lightsail
lightsail_list_matcher = on_command("lightsail_list", permission=SUPERUSER)
lightsail_start_matcher = on_command("lightsail_start", permission=SUPERUSER)
lightsail_stop_matcher = on_command("lightsail_stop", permission=SUPERUSER)
# Cost Explorer
cost_matcher = on_command("aws_cost", permission=SUPERUSER)


# --- Helper Functions --- #

async def parse_ec2_target(matcher: Matcher, args: Message) -> Tuple[str, str, Optional[str]]:
    arg_str = args.extract_plain_text().strip()
    if not arg_str:
        if plugin_config.aws_default_target_tag:
            arg_str = f"tag:{plugin_config.aws_default_target_tag}"
        else:
            await matcher.finish(__plugin_meta__.usage)
    match = re.match(r"^(tag|id):(.*)$", arg_str)
    if not match:
        await matcher.finish(f"Invalid EC2 target format. \n{__plugin_meta__.usage}")
    target_type, value = match.groups()
    if target_type == "tag":
        if ":" not in value:
            await matcher.finish(f"Invalid tag format. Expected Key:Value. \n{__plugin_meta__.usage}")
        tag_key, tag_value = value.split(":", 1)
        return "tag", tag_key, tag_value
    elif target_type == "id":
        return "id", value, None
    return "unknown", "", None

def format_ec2_status(instance: Dict[str, Any]) -> str:
    instance_id = instance.get('InstanceId', 'N/A')
    state = instance.get('State', {}).get('Name', 'N/A')
    public_ip = instance.get('PublicIpAddress', 'None')
    name_tag = next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'), 'No Name Tag')
    return f"- {instance_id} ({name_tag})\n  State: {state}\n  Public IP: {public_ip}"


# --- EC2 Handlers --- #

@ec2_status_matcher.handle()
@handle_non_finish_exceptions("An error occurred while fetching EC2 status.")
async def handle_ec2_status(matcher: Matcher, args: Message = CommandArg()):
    target_type, value1, value2 = await parse_ec2_target(matcher, args)

    if target_type == "tag":
        instances = await ec2_manager.get_instances_by_tag(value1, value2, states=['pending', 'running', 'stopping', 'stopped'])
    else:
        instances = await ec2_manager.get_instances_by_id([value1], states=['pending', 'running', 'stopping', 'stopped'])
    if not instances:
        await matcher.finish("No EC2 instances found for the specified target.")
    status_list = [format_ec2_status(inst) for inst in instances]
    await matcher.finish("EC2 Instance Status:\n" + "\n".join(status_list))


# ... (omitting other EC2 handlers for brevity, they remain the same)


# --- Lightsail Handlers ---

@lightsail_list_matcher.handle()
@handle_non_finish_exceptions("An error occurred listing Lightsail instances.")
async def handle_lightsail_list(matcher: Matcher):
    instances = await lightsail_manager.get_all_instances()
    if not instances:
        await matcher.finish("No Lightsail instances found.")
    
    def format_lightsail(inst): 
        return f"- {inst['name']} ({inst['state']['name']})\n  Region: {inst['location']['regionName']}\n  IP: {inst['publicIpAddress']}"

    status_list = [format_lightsail(inst) for inst in instances]
    await matcher.finish("Lightsail Instances:\n" + "\n".join(status_list))

@lightsail_start_matcher.handle()
@handle_non_finish_exceptions("An error occurred while starting the Lightsail instance.")
async def handle_lightsail_start(matcher: Matcher, args: Message = CommandArg()):
    instance_name = args.extract_plain_text().strip()
    if not instance_name:
        await matcher.finish("Please provide a Lightsail instance name.")
    
    await matcher.send(f"Sending start command to {instance_name}...\nWaiting for it to become running...")
    await lightsail_manager.start_instance(instance_name)
    await lightsail_manager.wait_for_status(instance_name, 'running')
    await matcher.finish(f"Successfully started Lightsail instance: {instance_name}")

@lightsail_stop_matcher.handle()
@handle_non_finish_exceptions("An error occurred while stopping the Lightsail instance.")
async def handle_lightsail_stop(matcher: Matcher, args: Message = CommandArg()):
    instance_name = args.extract_plain_text().strip()
    if not instance_name:
        await matcher.finish("Please provide a Lightsail instance name.")
    
    await matcher.send(f"Sending stop command to {instance_name}...\nWaiting for it to become stopped...")
    await lightsail_manager.stop_instance(instance_name)
    await lightsail_manager.wait_for_status(instance_name, 'stopped')
    await matcher.finish(f"Successfully stopped Lightsail instance: {instance_name}")


# --- Cost Explorer Handlers ---

@cost_matcher.handle()
@handle_non_finish_exceptions("An error occurred while fetching AWS cost data.")
async def handle_cost(matcher: Matcher, args: Message = CommandArg()):
    sub_command = args.extract_plain_text().strip()
    
    if sub_command == "today":
        result = await cost_manager.get_cost_today()
        cost = result['ResultsByTime'][0]['Total']['UnblendedCost']
        await matcher.finish(f"AWS cost for today: {float(cost['Amount']):.4f} {cost['Unit']}")
    elif sub_command == "month":
        result = await cost_manager.get_cost_this_month()
        cost = result['ResultsByTime'][0]['Total']['UnblendedCost']
        await matcher.finish(f"AWS cost this month: {float(cost['Amount']):.4f} {cost['Unit']}")
    elif sub_command == "month by_service":
        result = await cost_manager.get_cost_this_month_by_service()
        lines = ["Cost this month by service:"]
        for group in sorted(result['ResultsByTime'][0]['Groups'], key=lambda x: float(x['Metrics']['UnblendedCost']['Amount']), reverse=True):
            service_name = group['Keys'][0]
            cost = group['Metrics']['UnblendedCost']
            if float(cost['Amount']) > 0:
                lines.append(f"- {service_name}: {float(cost['Amount']):.4f} {cost['Unit']}")
        await matcher.finish("\n".join(lines))
    else:
        await matcher.finish("Invalid cost command. Use: today, month, month by_service")