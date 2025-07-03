import pytest

@pytest.fixture
def sample_text():
    return """
    CAFET CXB LAS ROZ -1,50€
    02/07/2025 15769,06€
    BIZUM ENVIADO -3,00€
    01/07/2025 15770,56€
    BIZUM RECIBIDO +30,36€
    01/07/2025 15773,56€
    """
