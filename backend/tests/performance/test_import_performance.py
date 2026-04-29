"""Performance regression tests."""

import importlib

import ekko.config.settings
import ekko.core.enums


class TestImportPerformance:
    def test_settings_import_fast(self, benchmark):
        """Settings module should import within a reasonable time."""

        def import_settings():
            importlib.reload(ekko.config.settings)

        benchmark(import_settings)

    def test_enums_import_fast(self, benchmark):
        """Enums module should import within a reasonable time."""

        def import_enums():
            importlib.reload(ekko.core.enums)

        benchmark(import_enums)
