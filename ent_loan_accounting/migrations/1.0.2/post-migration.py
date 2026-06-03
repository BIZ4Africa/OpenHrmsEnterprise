from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    loan_model = env["hr.loan"]
    move_model = env["account.move"]

    # Target only moves created for loan disbursement entries.
    loans = loan_model.search([])
    for loan in loans:
        moves = move_model.search([
            ("line_ids.loan_id", "=", loan.id),
        ])
        for move in moves:
            was_posted = move.state == "posted"
            if was_posted:
                move.button_draft()

            line_name = "Loan " + (loan.name or "") + " " + loan.employee_id.name
            move_ref = "Loan " + (loan.name or "") + " for " + loan.employee_id.name

            move.write({
                "name": "",
                "ref": move_ref,
            })

            loan_lines = move.line_ids.filtered(lambda line: line.loan_id == loan)
            loan_lines.write({"name": line_name})

            if was_posted:
                move.action_post()
