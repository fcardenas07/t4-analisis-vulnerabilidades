from __future__ import annotations

import argparse
import json
import logging
import subprocess
from pathlib import Path


RUTA_BASE = Path(__file__).resolve().parents[1]
RUTA_REPOS = RUTA_BASE / "data" / "repos"
RUTA_RESULTADOS = RUTA_BASE / "data" / "results"
SUFIJO_CI = "-ci.json"


if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s | %(message)s")

LOGGER = logging.getLogger(__name__)


class CIAnalyzer:
    def __init__(self, repos_path: str, output_path: str):
        self.repos_path = Path(repos_path).resolve()
        self.output_path = Path(output_path).resolve()
        self.dry_run = False

    # ----------------------------
    # 1. Descubrir repos
    # ----------------------------
    def discover_repositories(self) -> list[Path]:
        if not self.repos_path.exists():
            raise FileNotFoundError(f"No existe: {self.repos_path}")

        repos = [r for r in self.repos_path.iterdir() if r.is_dir()]

        if not repos:
            LOGGER.warning("No se encontraron repos")

        return sorted(repos)

    # ----------------------------
    # 2. Buscar workflows
    # ----------------------------
    def find_workflows(self, repo: Path) -> list[Path]:
        workflows_dir = repo / ".github" / "workflows"

        if not workflows_dir.exists():
            return []

        return list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))

    # ----------------------------
    # 3. Ejecutar Checkov
    # ----------------------------
    def run_checkov(self, workflows_path: Path) -> dict:
        result = subprocess.run(
            [
                "checkov",
                "-d", str(workflows_path),
                "--framework", "github_actions",
                "-o", "json",
            ],
            capture_output=True,
            text=True,
        )

        # 0 = limpio, 1 = findings
        if result.returncode not in (0, 1):
            raise RuntimeError(result.stderr)

        return json.loads(result.stdout)

    # ----------------------------
    # 4. Normalizar output
    # ----------------------------
    def normalize(self, raw: dict) -> dict:
        results = {
            "total_issues": 0,
            "issues_by_severity": {
                "HIGH": 0,
                "MEDIUM": 0,
                "LOW": 0,
                "UNKNOWN": 0,
            },
            "issues": [],
        }

        failed = raw.get("results", {}).get("failed_checks", [])

        for check in failed:
            severity = check.get("severity", "UNKNOWN")

            issue = {
                "check_id": check.get("check_id"),
                "check_name": check.get("check_name"),
                "file": check.get("file_path"),
                "resource": check.get("resource"),
                "severity": severity,
                "guideline": check.get("guideline"),
            }

            results["issues"].append(issue)
            results["total_issues"] += 1

            if severity not in results["issues_by_severity"]:
                results["issues_by_severity"]["UNKNOWN"] += 1
            else:
                results["issues_by_severity"][severity] += 1

        return results

    # ----------------------------
    # 5. Guardar resultados
    # ----------------------------
    def save(self, repo_name: str, data: dict):
        self.output_path.mkdir(parents=True, exist_ok=True)

        output_file = self.output_path / f"{repo_name}{SUFIJO_CI}"

        output_file.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        LOGGER.info(f"Guardado: {output_file}")

    # ----------------------------
    # 6. Run completo
    # ----------------------------
    def run(self):
        repos = self.discover_repositories()

        for repo in repos:
            LOGGER.info(f"Analizando {repo.name}")

            workflows = self.find_workflows(repo)

            if not workflows:
                LOGGER.info(f"{repo.name}: sin workflows")
                continue

            if self.dry_run:
                LOGGER.info(
                    f"{repo.name}: {len(workflows)} workflows encontrados")
                continue

            try:
                raw = self.run_checkov(repo / ".github" / "workflows")
                normalized = self.normalize(raw)
                self.save(repo.name, normalized)

            except Exception as e:
                LOGGER.error(f"Error en {repo.name}: {e}")


# ----------------------------
# CLI
# ----------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repos-path", default=str(RUTA_REPOS))
    parser.add_argument("--output-path", default=str(RUTA_RESULTADOS))
    parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    analyzer = CIAnalyzer(args.repos_path, args.output_path)
    analyzer.dry_run = args.dry_run
    analyzer.run()


if __name__ == "__main__":
    main()
