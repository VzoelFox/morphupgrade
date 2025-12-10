# tests/fox_engine/test_security.py
import pytest
import asyncio
import pickle
import subprocess

from fox_engine.api import sfox, dapatkan_manajer_fox
from fox_engine import api as fox_api

@pytest.fixture(autouse=True)
def reset_manajer_global():
    fox_api._manajer_fox = None
    yield
    fox_api._manajer_fox = None

@pytest.mark.asyncio
async def test_does_not_execute_arbitrary_code_from_string():
    """
    Memverifikasi bahwa ManajerFox tidak secara inheren mengevaluasi string sebagai kode.
    """
    malicious_string = "__import__('os').system('echo VULNERABLE')"
    with pytest.raises(TypeError):
        # Coroutine harus berupa callable, bukan string.
        await sfox("test_injection", malicious_string)

@pytest.mark.asyncio
async def test_handles_task_with_dangerous_operations_gracefully():
    """
    Menguji bahwa ManajerFox dapat menjalankan tugas yang berisi operasi
    berbahaya dan melaporkan kegagalan dengan benar.
    """
    async def task_with_malicious_exec():
        raise ValueError("Simulasi kegagalan eksekusi berbahaya")

    with pytest.raises(ValueError, match="Simulasi kegagalan eksekusi berbahaya"):
        await sfox("security_test_exec", task_with_malicious_exec)

    manajer = dapatkan_manajer_fox()
    assert manajer.metrik.tugas_gagal == 1

@pytest.mark.asyncio
async def test_pickle_injection_triggers_circuit_breaker():
    """
    Menguji bahwa kegagalan berulang dari tugas yang tidak aman (seperti deserialisasi pickle)
    akan memicu pemutus sirkuit.
    """
    manajer = dapatkan_manajer_fox()
    ambang_batas = manajer.pemutus_sirkuit.ambang_kegagalan

    class MaliciousPickle:
        def __reduce__(self):
            return (subprocess.run, (["non_existent_command"],))

    malicious_data = pickle.dumps(MaliciousPickle())

    async def unpickle_task():
        pickle.loads(malicious_data)
        return "pickle_vulnerable"

    # Picu kegagalan sebanyak ambang batas
    for i in range(ambang_batas):
        with pytest.raises(FileNotFoundError):
            await sfox(f"pickle_security_test_{i}", unpickle_task)

    assert manajer.metrik.tugas_gagal == ambang_batas
    # Sekarang, pemutus sirkuit seharusnya terbuka
    assert not manajer.pemutus_sirkuit.bisa_eksekusi()
