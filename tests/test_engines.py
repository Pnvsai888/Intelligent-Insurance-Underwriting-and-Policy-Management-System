import unittest
import inspect
from decimal import Decimal
from src.engines.evaluator import UnderwritingDecisionEngine


class TestUnderwritingEngines(unittest.TestCase):
    def setUp(self):
        self.engine = UnderwritingDecisionEngine()
        self.product = {
            "product_id": "PRD-PROP-01",
            "base_rate": "0.0200",
            "min_credit_score": "600",
            "max_sum_insured": "50000000",
            "max_loss_count": "3"
        }

    def _extract_premium(self, result):
        if isinstance(result, (tuple, list)):
            return Decimal(str(result[0]))
        if isinstance(result, dict):
            val = result.get("premium") or result.get(
                "total_premium") or list(result.values())[0]
            return Decimal(str(val))
        return Decimal(str(result))

    def test_actuarial_premium_calculation(self):
        # We inspect the exact parameter names of calculate_premium
        sig = inspect.signature(self.engine.calculate_premium)
        param_names = [p.name for p in sig.parameters.values()
                       if p.name != "self"]

        # Expected parameters map
        val_map = {
            "product_id": "PRD-PROP-01",
            "base_rate": Decimal("0.0200"),
            "sum_insured": Decimal("10000000"),
            "credit_score": 750,
            "loss_history_count_3yr": 0,
            "asset_risk_score": Decimal("4.500")
        }

        # Build kwargs using exact Decimal / int types
        kwargs = {}
        for name in param_names:
            if name in val_map:
                kwargs[name] = val_map[name]
            elif "rate" in name:
                kwargs[name] = Decimal("0.0200")
            elif "sum" in name or "insured" in name:
                kwargs[name] = Decimal("10000000")
            elif "credit" in name:
                kwargs[name] = 750
            elif "loss" in name:
                kwargs[name] = 0
            elif "asset" in name or "risk" in name:
                kwargs[name] = Decimal("4.500")
            elif "product" in name:
                kwargs[name] = self.product.get(name, "PRD-PROP-01")

        raw_res = self.engine.calculate_premium(**kwargs)
        prem = self._extract_premium(raw_res)
        self.assertEqual(prem, Decimal("137700.00"))

    def test_stp_approval_routing(self):
        applicant = {
            "credit_score": "780",
            "loss_history_count_3yr": "0"
        }
        asset = {
            "asset_risk_score": "4.000"
        }
        sum_insured = Decimal("5000000")

        res = self.engine.evaluate_underwriting_decision(
            applicant=applicant,
            asset=asset,
            product=self.product,
            sum_insured=sum_insured
        )

        decision = res[0] if isinstance(res, (tuple, list)) else (
            res.get("decision") if isinstance(res, dict) else res)
        auth = res[1] if isinstance(res, (tuple, list)) else (
            res.get("authority_level") if isinstance(res, dict) else "")

        self.assertIn(decision, ["AUTO_APPROVE", "APPROVE", "APPROVED"])
        self.assertEqual(auth, "STP_SYSTEM")

    def test_hard_decline_low_credit(self):
        applicant = {
            "credit_score": "450",
            "loss_history_count_3yr": "0"
        }
        asset = {
            "asset_risk_score": "4.000"
        }
        sum_insured = Decimal("5000000")

        res = self.engine.evaluate_underwriting_decision(
            applicant=applicant,
            asset=asset,
            product=self.product,
            sum_insured=sum_insured
        )

        decision = res[0] if isinstance(res, (tuple, list)) else (
            res.get("decision") if isinstance(res, dict) else res)
        self.assertIn(decision, ["DECLINE", "DECLINED"])

    def test_policy_binding_gate(self):
        quote = {
            "quote_id": "QTE-2026-000001",
            "applicant_id": "APP-2026-000001",
            "product_id": "PRD-PROP-01",
            "total_premium": "137700.00"
        }
        uw_decision = {
            "decision": "AUTO_APPROVE",
            "authority_level": "STP_SYSTEM"
        }

        # Gate check when payment is missing
        res_no_pay = self.engine.issue_policy(
            quote=quote,
            uw_decision=uw_decision,
            customer_accepted=True,
            payment_ref=None,
            effective_date="2026-01-01"
        )
        if isinstance(res_no_pay, dict):
            status = res_no_pay.get("status") or res_no_pay.get(
                "policy_status") or res_no_pay.get("issued")
            self.assertIn(status, [False, None, "REJECTED",
                          "DECLINED", "PENDING_PAYMENT"])
        else:
            self.assertFalse(bool(res_no_pay))

        # Gate check when customer did not accept
        res_unacc = self.engine.issue_policy(
            quote=quote,
            uw_decision=uw_decision,
            customer_accepted=False,
            payment_ref="TXN-PAY-000001",
            effective_date="2026-01-01"
        )
        if isinstance(res_unacc, dict):
            status = res_unacc.get("status") or res_unacc.get(
                "policy_status") or res_unacc.get("issued")
            self.assertIn(
                status, [False, None, "REJECTED", "DECLINED", "NOT_ACCEPTED"])
        else:
            self.assertFalse(bool(res_unacc))


if __name__ == "__main__":
    unittest.main()
