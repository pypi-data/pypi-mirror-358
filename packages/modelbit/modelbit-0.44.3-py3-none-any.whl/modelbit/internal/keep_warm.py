from typing import List, Optional, Dict, Any, cast

from modelbit.ux import TableHeader, renderTemplate, printTemplate
from modelbit.api import KeepWarmApi, KeepWarmDesc, MbApi
from modelbit.error import UserFacingError

# Keep in sync with keep_warm_scheduler.tsx
MaxKeepWarms = 12
AllowedTimeZones: List[str] = [
    "UTC",
    "Australia/Sydney",
    "Australia/Adelaide",
    "America/Anchorage",
    "America/Puerto_Rico",
    "America/Chicago",
    "America/New_York",
    "America/Denver",
    "America/Los_Angeles",
    "America/Rio_Branco",
    "America/Sao_Paulo",
    "Africa/Maputo",
    "Africa/Lagos",
    "Africa/Nairobi",
    "Europe/Berlin",
    "Europe/Kiev",
    "Europe/Athens",
    "Europe/Madrid",
    "Europe/London",
    "Europe/Istanbul",
    "Europe/Paris",
    "Europe/Rome",
    "Europe/Warsaw",
    "Europe/Dublin",
    "Europe/Lisbon",
    "Asia/Tokyo",
    "Asia/Hong_Kong",
    "Asia/Seoul",
    "Asia/Bangkok",
    "Asia/Shanghai",
    "Asia/Riyadh",
    "Asia/Karachi",
    "Asia/Kolkata",
    "Asia/Jerusalem",
]

DailySchedule = Optional[List[Dict[str, int]]]


class KeepWarmList:

  def __init__(self, mbApi: MbApi, branch: str):
    self.branch = branch
    self.keepWarms: List[KeepWarmDesc] = KeepWarmApi(mbApi).listKeepWarms(branch=branch)
    self.isAuthenticated = mbApi.isAuthenticated()

  def _repr_html_(self) -> str:
    if not self.isAuthenticated:
      return "Not authenticated."
    return self.makeKeepWarmTable()

  def __str__(self) -> str:
    if not self.isAuthenticated:
      return "Not authenticated."
    return self.makeKeepWarmTable()

  def makeKeepWarmTable(self) -> str:
    if len(self.keepWarms) == 0:
      return f"No Keep Warms are enabled on branch '{self.branch}'."
    headers = [
        TableHeader("Deployment", TableHeader.LEFT, isCode=True),
        TableHeader("Version", TableHeader.RIGHT),
        TableHeader("Count", TableHeader.RIGHT),
    ]
    rows: List[List[str]] = []
    for k in self.keepWarms:
      count = 1
      if k.schedule:
        count = maxDailyCount(k.schedule["days"])
      rows.append([k.deployment, k.version, str(count)])
    return renderTemplate("table", headers=headers, rows=rows)


def dailySchedule(count: int, startHour: int, endHour: int) -> List[DailySchedule]:
  return [[{"startHour": startHour, "endHour": endHour}] * count] * 7


def maxDailyCount(scheduleDays: List[DailySchedule]) -> int:
  maxCount: int = 0
  for day in scheduleDays:
    if day is None:
      continue
    if len(day) > maxCount:
      maxCount = len(day)
  return maxCount


def assertAndConvertUserSchedule(userSchedule: Any) -> Dict[str, Any]:
  if type(userSchedule) is not dict:
    raise UserFacingError("Schedule must be a dictionary.")

  userSchedule = cast(Dict[str, Any], userSchedule)
  if "timezone" not in userSchedule:
    raise UserFacingError("Schedule missing 'timezone'.")
  if userSchedule["timezone"] not in AllowedTimeZones:
    raise UserFacingError(f"Schedule timezone must be one of: {', '.join(AllowedTimeZones)}")
  if "days" not in userSchedule:
    raise UserFacingError("Schedule missing 'days'.")

  userDays = userSchedule["days"]
  if type(userDays) is not list:
    raise UserFacingError("Schedule.days must be a list.")
  userDays = cast(List[Any], userDays)
  if len(userDays) != 7:
    raise UserFacingError("Schedule.days must be a list of 7 lists.")

  scheduleDays: List[DailySchedule] = []
  for idx, userDay in enumerate(userDays):
    errorStr = f"Schedule.days[{idx}]" + " must be a list of {'start_hour': int, 'end_hour': int} or None."

    if userDay is None:
      scheduleDays.append(None)
      continue

    if type(userDay) is not list:
      raise UserFacingError(errorStr)
    userDay = cast(List[Any], userDay)

    curDaySchedule: List[Dict[str, int]] = []
    for userInst in userDay:
      if type(userInst) is not dict or "start_hour" not in userInst or "end_hour" not in userInst:
        raise UserFacingError(errorStr)
      startHour = cast(Any, userInst["start_hour"])
      endHour = cast(Any, userInst["end_hour"])
      if type(startHour) is not int or type(
          endHour) is not int or endHour <= startHour or startHour < 0 or endHour > 24:
        raise UserFacingError("start_hour and end_hour must be integers between 0 and 24.")
      curDaySchedule.append({"startHour": startHour, "endHour": endHour})
    scheduleDays.append(curDaySchedule)

  dailyCount = maxDailyCount(scheduleDays)
  if dailyCount == 0:
    raise UserFacingError("At least one day needs a scheduled Keep Warm.")
  elif dailyCount > MaxKeepWarms:
    raise UserFacingError("At most 12 instances can be scheduled.")

  return {
      "timezone": userSchedule["timezone"],
      "schemaVersion": 1,
      "days": scheduleDays,
  }


def listKeepWarms(mbApi: MbApi, branch: str) -> KeepWarmList:
  return KeepWarmList(mbApi=mbApi, branch=branch)


def enableKeepWarm(
    mbApi: MbApi,
    branch: str,
    deployment: str,
    version: int,
    userSchedule: Optional[Dict[str, Any]] = None,
    count: Optional[int] = None,
) -> None:
  if count is not None and (type(count) is not int or count < 1 or count > MaxKeepWarms):
    raise UserFacingError(f"count= must be an int between 1 and {MaxKeepWarms}")

  kwSchedule: Dict[str, Any]
  if not userSchedule:
    kwSchedule = {
        "timezone": "UTC",
        "schemaVersion": 1,
        "days": dailySchedule(count=(count or 1), startHour=0, endHour=24),
    }
  else:
    kwSchedule = assertAndConvertUserSchedule(userSchedule)

  updateKeepWarm(
      mbApi=mbApi,
      branch=branch,
      deployment=deployment,
      version=version,
      enabled=True,
      schedule=kwSchedule,
  )
  printTemplate("message", None, msgText=f"Enabling Keep Warm for {deployment}/{version} on branch {branch}.")


def disableKeepWarm(
    mbApi: MbApi,
    branch: str,
    deployment: str,
    version: int,
) -> None:
  updateKeepWarm(
      mbApi=mbApi,
      deployment=deployment,
      version=version,
      branch=branch,
      enabled=False,
  )
  printTemplate("message",
                None,
                msgText=f"Disabling Keep Warm for {deployment}/{version} on branch {branch}.")


def updateKeepWarm(
    mbApi: MbApi,
    branch: str,
    deployment: str,
    version: int,
    enabled: bool,
    schedule: Optional[Dict[str, Any]] = None,
) -> None:
  KeepWarmApi(mbApi).updateKeepWarm(
      branch=branch,
      runtimeName=deployment,
      runtimeVersion=version,
      target=str(version),  # Supporting the 'latest' attachment is NYI
      enabled=enabled,
      schedule=schedule,
  )
