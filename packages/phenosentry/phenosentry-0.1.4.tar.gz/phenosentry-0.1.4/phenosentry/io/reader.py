import logging
import typing
import zipfile

from ..model import CohortInfo, PhenopacketInfo, EagerPhenopacketInfo, ZipPhenopacketInfo
from pathlib import Path
from google.protobuf.json_format import ParseError

def read_phenopacket(
    path: Path | zipfile.Path,
    logger: logging.Logger,
    lazy: bool = False
) -> PhenopacketInfo:
    """
     Reads a single phenopacket from a specified directory.

     Args:
         directory (Path): The path to the directory containing the phenopacket file.
         logger (logging.Logger): Logger instance for logging messages.
         lazy: bool: If True, reads the phenopacket lazily (not implemented yet).

     Returns:
         PhenopacketInfo: An object containing information about the phenopacket.

     Raises:
         ParseError: If the phenopacket file cannot be parsed due to invalid format.
     """
    logger.info("Reading phenopacket at `%s`", path)

    if lazy:
        if not isinstance(path, zipfile.Path):
            raise ParseError("Lazy loading is only supported for phenopackets in zip files.")
        return ZipPhenopacketInfo(str(path), path)
    return EagerPhenopacketInfo.from_path(path)

def read_phenopackets(directory: Path | zipfile.Path, logger: logging.Logger, lazy:  bool = False) -> typing.List[PhenopacketInfo]:
    """
    Reads all phenopackets from a specified directory or zip folder.

    Args:
        directory (Path): The path to the directory containing phenopacket files.
        logger (logging.Logger): Logger instance for logging messages.
        eager (bool): If True, reads phenopackets eagerly into memory.
    Returns:
        typing.List[PhenopacketInfo]: A list of objects containing information about each phenopacket.
    """
    logger.info("Reading phenopackets at `%s`", directory)
    return [
        read_phenopacket(path, logger, lazy=lazy)
        for path in find_json_files(directory)
        if path.name.endswith(".json")
    ]

def read_cohort(
    directory: Path | zipfile.Path,
    logger: logging.Logger,
    lazy: bool = False,
) -> CohortInfo:
    """
      Reads a cohort of phenopackets from a specified directory.

      Args:
          :param directory (Path): The path to the directory containing the cohort of phenopackets.
          :param logger (logging.Logger): Logger instance for logging messages.
          :param lazy (LoadStrategy): The strategy to use for loading phenopackets.
            Defaults to LoadStrategy.EAGER.

      Returns:
          CohortInfo: An object containing information about the cohort, including its name, path, and phenopackets.
      """
    logger.info("Reading cohort at `%s`", directory)
    name = ""
    if isinstance(directory, zipfile.Path) and directory.name.endswith(".zip"):
        name = directory.name[:-4]
    else:
        name = directory.stem
    phenopackets = read_phenopackets(directory, logger, lazy)
    return CohortInfo(name=name, path=str(directory), phenopackets=phenopackets)

def find_json_files(directory):
    for entry in directory.iterdir():
        if entry.is_dir():
            yield from find_json_files(entry)
        elif entry.name.endswith(".json"):
            yield entry