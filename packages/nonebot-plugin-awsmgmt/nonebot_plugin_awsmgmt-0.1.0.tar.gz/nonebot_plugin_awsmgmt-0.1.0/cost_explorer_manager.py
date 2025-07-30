import aioboto3
from datetime import datetime, date, timedelta
from typing import Dict, Any, List

from .config import Config

class CostExplorerManager:
    def __init__(self, config: Config):
        self.config = config
        # Cost Explorer is only available in us-east-1, but we use the session region for authentication
        self.session = aioboto3.Session(
            aws_access_key_id=self.config.aws_access_key_id,
            aws_secret_access_key=self.config.aws_secret_access_key,
            region_name=self.config.aws_region,
        )

    async def _get_cost(self, start_date: str, end_date: str, granularity: str, group_by: List[Dict[str, str]] = None) -> Dict[str, Any]:
        async with self.session.client("ce", region_name="us-east-1") as ce:
            kwargs = {
                "TimePeriod": {"Start": start_date, "End": end_date},
                "Granularity": granularity,
                "Metrics": ["UnblendedCost"],
            }
            if group_by:
                kwargs["GroupBy"] = group_by
            return await ce.get_cost_and_usage(**kwargs)

    async def get_cost_today(self) -> Dict[str, Any]:
        """Fetches the cost for today."""
        today = date.today()
        start_of_day = today.isoformat()
        end_of_day = (today + timedelta(days=1)).isoformat()
        return await self._get_cost(start_of_day, end_of_day, "DAILY")

    async def get_cost_this_month(self) -> Dict[str, Any]:
        """Fetches the cost for the current month."""
        today = date.today()
        start_of_month = today.replace(day=1).isoformat()
        # The end date is exclusive, so we use the first day of the next month
        next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
        end_of_month = next_month.isoformat()
        return await self._get_cost(start_of_month, end_of_month, "MONTHLY")

    async def get_cost_this_month_by_service(self) -> Dict[str, Any]:
        """Fetches the cost for the current month, grouped by service."""
        today = date.today()
        start_of_month = today.replace(day=1).isoformat()
        next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
        end_of_month = next_month.isoformat()
        group_by = [{"Type": "DIMENSION", "Key": "SERVICE"}]
        return await self._get_cost(start_of_month, end_of_month, "MONTHLY", group_by=group_by)
