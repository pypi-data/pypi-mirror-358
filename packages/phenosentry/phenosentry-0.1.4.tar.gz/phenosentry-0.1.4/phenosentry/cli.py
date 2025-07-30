import click
import logging
import pathlib
import io
from phenosentry.model.auditor_level import AuditorLevel
from .validation import get_cohort_auditor, get_phenopacket_auditor
from .io import read_phenopacket, read_cohort, read_phenopackets

def setup_logging():
    level = logging.INFO
    logger = logging.getLogger()
    logger.setLevel(level)
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(level)
    # create formatter
    formatter = logging.Formatter(
        "%(asctime)s %(name)-20s %(levelname)-3s : %(message)s"
    )
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)

@click.group()
def main():
    pass

@main.command('validate')
@click.option("--path", type=click.Path(exists=True, readable=True), required=True)
@click.option(
    "--level",
    type=click.Choice([m.value for m in AuditorLevel]),
    required=True,
    help="The level of validation to perform: strict or default."
)
@click.option('--cohort', is_flag=True, help='Indicates that the input is a cohort.')
def validate(path, level, is_cohort):
    """
    Validates phenopacket or cohort data based on the provided options.

    Args:
        path (str): The file or directory path to the phenopacket(s) or cohort.
        level (str): The validation level, either 'strict' or 'default'.
        is_cohort (bool): Flag indicating whether the input is a cohort.

    Returns:
        int: 0 if validation passes without errors or warnings, 1 otherwise.
    """

    setup_logging()
    logger = logging.getLogger(__name__)
    pathed = pathlib.Path(path)
    notepad = None
    if pathed.is_file():
        phenopacket = read_phenopacket(
            directory=str(path),
            logger=logger,
        )
        # single phenopacket
        auditor = get_phenopacket_auditor(level)
        notepad = auditor.prepare_notepad(auditor.id())
        auditor.audit(
            item=phenopacket,
            notepad=notepad,
        )
    elif pathed.is_dir():
        # cohort of phenopackets
        if is_cohort:
            cohort = read_cohort(
                directory=str(path),
                logger=logger,
            )
            auditor = get_cohort_auditor()
            notepad = auditor.prepare_notepad(auditor.id())
            auditor.audit(
                item=cohort,
                notepad=notepad,
            )
        else:
            # We iterate phenopackets and validate them seperately
            auditor = get_phenopacket_auditor(level)
            notepad = auditor.prepare_notepad(auditor.id())
            phenopackets = read_phenopackets(str(path), logger=logger)
            for phenopacket in phenopackets:
                notepad.add_subsection("Phenopacket {}".format(phenopacket.id))
                auditor.audit(
                    item=phenopacket,
                    notepad=notepad,
                )


    buf = io.StringIO()
    # TODO: Notepad summary should include source data and spot of issue
    notepad.summarize(file=buf)
    if notepad.has_errors_or_warnings(include_subsections=True):
        logger.error(buf.getvalue())
        return 1
    else:
        logger.info(buf.getvalue())
        return 0

if __name__ == '__main__':
    main()