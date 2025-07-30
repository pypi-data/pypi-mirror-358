from django.apps import AppConfig


class NemoStockroomConfig(AppConfig):
    name = "NEMO_stockroom"
    verbose_name = "NEMO Stockroom"

    def ready(self):
        from NEMO.plugins.utils import check_extra_dependencies

        """
        This code will be run when Django starts.
        """
        check_extra_dependencies(self.name, ["NEMO", "NEMO-CE"])
