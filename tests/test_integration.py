import pytest

from notification_engine import NotificationEngine
from database import SQLiteWalletRepository


# ---------------------------------------------
# Fake SMS Gateway for Integration Testing
# ---------------------------------------------

class FakeSMSGateway:

    def send_sms(self, phone, message):

        return True


# ---------------------------------------------
# Pytest Fixture
# Creates real SQLite database
# ---------------------------------------------

@pytest.fixture
def repository():

    repo = SQLiteWalletRepository()

    yield repo

    repo.connection.close()


# ---------------------------------------------
# Test Successful Dispatch
# Verify data exists in SQLite
# ---------------------------------------------

def test_successful_dispatch_saved_in_database(repository):

    gateway = FakeSMSGateway()

    engine = NotificationEngine(
        repository,
        gateway
    )


    result = engine.dispatch(
        "100",
        "+250780000000",
        "Payment received"
    )


    assert result == "SENT_PRIMARY"


    # Verify real database content

    cursor = repository.connection.cursor()

    cursor.execute(
        """
        SELECT status
        FROM messages
        WHERE msg_id=?
        """,
        ("100",)
    )


    record = cursor.fetchone()


    assert record[0] == "SENT"