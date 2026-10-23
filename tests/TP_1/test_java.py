from pathlib import Path
import shutil
import subprocess
import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def java_build(tmp_path_factory):
    if shutil.which("javac") is None or shutil.which("java") is None:
        pytest.skip("Requiere un JDK")
    build = tmp_path_factory.mktemp("java")
    sources = list((ROOT / "main/TP_1_Java/src").rglob("*.java"))
    subprocess.run(["javac", "-d", str(build), *map(str, sources),
                    str(ROOT / "benchmarks/VerifyDijkstra.java")], check=True,
                   capture_output=True, text=True)
    return build


@pytest.mark.java
def test_java_oraculo_y_caminos(java_build):
    result = subprocess.run(["java", "-cp", str(java_build), "VerifyDijkstra"],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert "102 grafos" in result.stdout


@pytest.mark.java
@pytest.mark.parametrize("probe", ["overflow", "sentinel"])
@pytest.mark.xfail(strict=True, reason="Limitaciones numéricas reproducidas del Java original")
def test_java_limites_numericos(java_build, probe):
    result = subprocess.run(["java", "-cp", str(java_build), "VerifyDijkstra", probe],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
