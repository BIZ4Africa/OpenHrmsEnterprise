import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Post-migration of ent_ohrms_loan 1.0.2.

    1. Provision one ``hr.loan.seq`` sequence **per company** (idempotent: a
       company already owning a sequence is left untouched). Up to now a
       single sequence was created without a company and therefore bound to
       the company active at installation time; every other company drew no
       sequence, so its loans were created with a blank name.
    2. Name the loans left with a blank reference (' ', '/', empty), from the
       sequence of **their own** company. Only ``hr.loan.name`` is written:
       no accounting entry is touched, so the labels of the entries already
       posted stay as they are.

    19.0 port of the 18.0 script ``migrations/1.0.3/post-migrate.py``
    (ent_ohrms_loan 1.0.3/1.0.4): the directory carries the version of the
    19.0 lineage (the manifest goes 1.0.1 -> 1.0.2), so the kernel's real
    loader reaches it on an installed base -- the 18.0 directory name would
    have been dead here (two distinct version lineages).

    Both steps are traced in the log; a second run finds nothing to do.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})

    created = env['hr.loan']._ensure_loan_sequences()
    _logger.info(
        "ent_ohrms_loan 1.0.2: %s loan sequence(s) provisioned (one per "
        "company).", len(created))

    renamed = env['hr.loan']._backfill_empty_loan_names()
    _logger.info(
        "ent_ohrms_loan 1.0.2: %s loan(s) named from their company sequence.",
        len(renamed))
