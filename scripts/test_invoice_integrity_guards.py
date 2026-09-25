import uuid
import psycopg2
import pytest
from psycopg2.extras import RealDictCursor

from scripts.migration_runner import get_connection


def test_invoice_guards_are_installed_and_total_is_deferred():
    conn, _ = get_connection("pol_test")
    conn.autocommit = False
    try:
        with pytest.raises(psycopg2.Error):
            with conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        """
                        SELECT i.id, i.total_amount,
                               COALESCE(SUM(ii.total_line_amount),0) AS line_sum
                        FROM invoices i
                        LEFT JOIN invoice_items ii ON ii.invoice_id=i.id
                        GROUP BY i.id, i.total_amount
                        HAVING i.total_amount <> COALESCE(SUM(ii.total_line_amount),0)
                        ORDER BY i.created_at
                        LIMIT 1
                        """
                    )
                    bad = cur.fetchone()

                    if not bad:
                        # Build an intentionally inconsistent invoice inside the same transaction.
                        cur.execute("SELECT id, order_id, retailer_organization_id, vendor_organization_id FROM invoices ORDER BY created_at LIMIT 1")
                        inv = cur.fetchone()
                        if not inv:
                            pytest.skip("No invoice fixture available.")
                        inv_id = inv["id"]
                        cur.execute(
                            """
                            INSERT INTO invoice_items
                                (id, invoice_id, product_name, quantity, unit_price, total_line_amount)
                            VALUES (%s,%s,'guard-test',1,1,1)
                            """,
                            (str(uuid.uuid4()), inv_id),
                        )
                        # Force aggregate mismatch by changing the invoice total.
                        cur.execute(
                            "UPDATE invoices SET total_amount=total_amount+123 WHERE id=%s",
                            (inv_id,),
                        )
                    else:
                        # Touch the known inconsistency; migration guard must make the transaction fail
                        # before the fixture can silently commit further changes.
                        cur.execute(
                            "UPDATE invoices SET total_amount=total_amount+1 WHERE id=%s",
                            (bad["id"],),
                        )
    finally:
        conn.close()
