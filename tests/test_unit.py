import pytest
from unittest.mock import Mock

from notification_engine import NotificationEngine


# -------------------------------------------------
# Test 1: Valid Phone Number
# -------------------------------------------------

def test_valid_phone():

    repo = Mock()
    repo.get_status.return_value = None

    gateway = Mock()
    gateway.send_sms.return_value = True

    engine = NotificationEngine(repo, gateway)

    result = engine.dispatch(
        "1",
        "+250780000000",
        "Hello"
    )

    assert result == "SENT_PRIMARY"


# -------------------------------------------------
# Test 2: Invalid Phone Number (0780000000)
# -------------------------------------------------

def test_invalid_phone():

    repo = Mock()
    gateway = Mock()

    engine = NotificationEngine(repo, gateway)

    with pytest.raises(ValueError):
        engine.dispatch(
            "1",
            "0780000000",
            "Hello"
        )

    repo.get_status.assert_not_called()


# -------------------------------------------------
# Test 3: Invalid Phone Number (+00012)
# -------------------------------------------------

def test_invalid_phone_plus00012():

    repo = Mock()
    gateway = Mock()

    engine = NotificationEngine(repo, gateway)

    with pytest.raises(ValueError):
        engine.dispatch(
            "1",
            "+00012",
            "Hello"
        )

    repo.get_status.assert_not_called()


# -------------------------------------------------
# Test 4: Idempotency Check
# -------------------------------------------------

def test_already_sent():

    repo = Mock()
    repo.get_status.return_value = "SENT"

    gateway = Mock()

    engine = NotificationEngine(repo, gateway)

    result = engine.dispatch(
        "1",
        "+250780000000",
        "Hello"
    )

    assert result == "ALREADY_SENT"

    gateway.send_sms.assert_not_called()


# -------------------------------------------------
# Test 5: Retry Logic
# -------------------------------------------------

def test_retry_logic():

    repo = Mock()
    repo.get_status.return_value = None

    gateway = Mock()

    gateway.send_sms.side_effect = [
        Exception("Network Error"),
        True
    ]

    engine = NotificationEngine(repo, gateway)

    result = engine.dispatch(
        "1",
        "+250780000000",
        "Hello"
    )

    assert result == "SENT_PRIMARY"

    assert gateway.send_sms.call_count == 2

    repo.save_status.assert_called_with(
        "1",
        "+250780000000",
        "SENT"
    )


# -------------------------------------------------
# Test 6: Backup Gateway
# -------------------------------------------------

def test_backup_gateway():

    repo = Mock()
    repo.get_status.return_value = None

    primary = Mock()
    backup = Mock()

    primary.send_sms.side_effect = [
        Exception("Failure"),
        Exception("Failure")
    ]

    backup.send_sms.return_value = True

    engine = NotificationEngine(
        repo,
        primary,
        backup
    )

    result = engine.dispatch(
        "1",
        "+250780000000",
        "Hello"
    )

    assert result == "SENT_BACKUP"

    assert primary.send_sms.call_count == 2
    backup.send_sms.assert_called_once()

    repo.save_status.assert_called_with(
        "1",
        "+250780000000",
        "SENT_BACKUP"
    )


# -------------------------------------------------
# Test 7: Complete Failure
# -------------------------------------------------

def test_complete_failure():

    repo = Mock()
    repo.get_status.return_value = None

    primary = Mock()
    backup = Mock()

    primary.send_sms.side_effect = Exception("Primary Failed")
    backup.send_sms.side_effect = Exception("Backup Failed")

    engine = NotificationEngine(
        repo,
        primary,
        backup
    )

    with pytest.raises(RuntimeError):
        engine.dispatch(
            "1",
            "+250780000000",
            "Hello"
        )

    repo.save_status.assert_called_with(
        "1",
        "+250780000000",
        "FAILED"
    )