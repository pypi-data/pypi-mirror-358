import logging
from typing import Any, Dict, List, Optional

from .api import MbApi, writeLimiter, readLimiter

logger = logging.getLogger(__name__)


class KeepWarmDesc:

  def __init__(self, runtimeName: str, runtimeVersion: str, data: Dict[str, Any]):
    self.deployment: str = runtimeName
    self.version: str = runtimeVersion
    self.latest: bool = data["latest"]
    self.schedule: Optional[Dict[str, Any]] = data.get("schedule", None)  # ScheduleJson


class KeepWarmApi:
  api: MbApi

  def __init__(self, api: MbApi):
    self.api = api

  def listKeepWarms(self, branch: str) -> List[KeepWarmDesc]:
    readLimiter.maybeDelay()
    resp = self.api.getJsonOrThrow("api/cli/v1/runtimes/provisioned/list", {"branch": branch})
    keepWarms: List[KeepWarmDesc] = []
    for runtimeName in resp["status"].keys():
      for runtimeVersion, data in resp["status"][runtimeName].items():
        if not data.get("isProvisioned", False) and not data.get("isProvisioning", False):
          continue
        keepWarms.append(KeepWarmDesc(
            runtimeName=runtimeName,
            runtimeVersion=runtimeVersion,
            data=data,
        ))
    return keepWarms

  def updateKeepWarm(
      self,
      branch: str,
      runtimeName: str,
      runtimeVersion: int,
      target: str,
      enabled: bool,
      schedule: Optional[Dict[str, Any]] = None,
  ) -> None:
    writeLimiter.maybeDelay()
    self.api.getJsonOrThrow(
        "api/cli/v1/runtimes/provisioned/update", {
            "branch": branch,
            "runtimeName": runtimeName,
            "runtimeVersion": runtimeVersion,
            "target": target,
            "enabled": enabled,
            "schedule": schedule,
        })
