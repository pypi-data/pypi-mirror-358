import os
from typing import List, Optional, Tuple, cast

from modelbit.internal.local_config import AppDirs, getCacheDir


def objectCacheFilePath(workspaceId: str, contentHash: str, isShared: bool) -> str:
  contentHash = contentHash.replace(":", "_")
  if isShared:
    return os.path.join(getCacheDir(workspaceId, "sharedFiles"), f"{contentHash}.zstd")
  else:
    return os.path.join(getCacheDir(workspaceId, "largeFiles"), f"{contentHash}.zstd.enc")


def legacyStubCacheFilePath(workspaceId: str, contentHash: str) -> str:
  contentHash = contentHash.replace(":", "_")
  return os.path.join(getCacheDir(workspaceId, "largeFileStubs"), f"{contentHash}.yaml")


# Cache path changes in January 2025. Remove in a few months.
def maybeRenameCacheFiles(workspaceId: str, contentHash: str, newCachePath: str) -> None:
  oldCachePath = legacyStubCacheFilePath(workspaceId, contentHash)
  if os.path.exists(oldCachePath) and not os.path.exists(newCachePath):
    os.rename(oldCachePath, newCachePath)


def stubCacheFilePath(workspaceId: str, contentHash: str, filepath: str) -> str:
  contentHash = contentHash.replace(":", "_")
  filepath = filepath.replace("/", "~")
  cachePath = os.path.join(getCacheDir(workspaceId, "largeFileStubs"), f"{filepath}.yaml")
  maybeRenameCacheFiles(workspaceId, contentHash, cachePath)
  return cachePath


def _userCacheDir() -> str:
  return cast(str, AppDirs.user_cache_dir)  # type: ignore


def clearCache(workspace: Optional[str]) -> None:
  import shutil
  shutil.rmtree(os.path.join(_userCacheDir(), workspace or ""))


_cacheNameMap = {'largeFiles': 'Encrypted Data', 'largeFileStubs': 'Description'}


def getCacheList(workspace: Optional[str]) -> List[Tuple[str, str, str, int]]:
  import glob
  import stat
  if not os.path.exists(_userCacheDir()):
    return []
  filedata: List[Tuple[str, str, str, int]] = []
  try:
    for filepath in glob.iglob(os.path.join(_userCacheDir(), workspace or "", "**"), recursive=True):
      statinfo = os.stat(filepath)
      if not stat.S_ISDIR(statinfo.st_mode):
        relpath = os.path.relpath(filepath, _userCacheDir())
        if relpath.startswith("log/"):
          continue
        [workspace, kind, name] = relpath.split("/")
        filedata.append((workspace, _cacheNameMap.get(kind, 'Unknown'), name, statinfo[stat.ST_SIZE]))
  except FileNotFoundError:
    return []
  return filedata
