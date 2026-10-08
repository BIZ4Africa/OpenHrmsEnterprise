# -*- coding: utf-8 -*-
################################################################################
#
#    Part of the BIZ4A OpenHrmsEnterprise fork.
#
#    The loan reference sequence is provisioned **per company** (one
#    'hr.loan.seq' sequence per company, each bound to its own company).
#    A post-init hook runs at installation, and
#    ``migrations/1.0.3/post-migrate.py`` runs the very same provisioning on
#    an upgrade (a post-init hook is never called on update).
#
################################################################################
import logging

_logger = logging.getLogger(__name__)


def post_init(env):
    """Provision the loan reference sequences at installation.

    One sequence per company, created idempotently: a company that already
    owns a sequence keeps it, so installing or upgrading never produces a
    duplicate series.
    """
    created = env['hr.loan']._ensure_loan_sequences()
    _logger.info(
        "ent_ohrms_loan: post_init provisioned %s loan sequence(s).",
        len(created))
