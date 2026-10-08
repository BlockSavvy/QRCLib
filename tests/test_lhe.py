"""CKKS envelope. Skipped when TenSEAL is not installed."""

import pytest

pytest.importorskip("tenseal")

from qrclib.errors import PolicyError  # noqa: E402
from qrclib.hybrid import generate_kem_keys, generate_sign_keys  # noqa: E402
from qrclib.lhe import evaluate, open_result, open_values, seal  # noqa: E402


def test_sum_mean_and_mask_without_giving_the_agent_the_secret():
    values = [1.5, 2.5, 3.0, 4.0, 10.25]
    recipient = generate_kem_keys()
    sender = generate_sign_keys()
    envelope = seal(values, recipient.public_key, sender.secret_key)
    total = evaluate(envelope, "sum", sender.public_key)
    average = evaluate(envelope, "mean", sender.public_key)
    masked = evaluate(envelope, "mask", sender.public_key, operand=[1, 0, 1, 0, 0])
    opened_sum = open_result(envelope, total, recipient.secret_key, sender.public_key)
    opened_mean = open_result(envelope, average, recipient.secret_key, sender.public_key)
    opened_mask = open_result(envelope, masked, recipient.secret_key, sender.public_key)
    opened = open_values(envelope, recipient.secret_key, sender.public_key)
    assert opened_sum == pytest.approx(sum(values), abs=0.05)
    assert opened_mean == pytest.approx(sum(values) / len(values), abs=0.05)
    assert opened_mask == pytest.approx(1.5 + 3.0, abs=0.05)
    assert opened == pytest.approx(values, abs=0.05)
    with pytest.raises(PolicyError):
        evaluate(
            seal(
                values,
                recipient.public_key,
                sender.secret_key,
                policy={"ops": ["sum"]},
            ),
            "mean",
            sender.public_key,
        )
