from django.apps import AppConfig


class NEMOPeriodicTableQuestionConfig(AppConfig):
    name = "NEMO_periodic_table_question"
    verbose_name = "Periodic table question"

    def ready(self):
        # Keep this here, or it won't get picked up and parsed
        from NEMO_periodic_table_question import periodic_table_question


default_app_config = "NEMO_periodic_table_question.NEMOPeriodicTableQuestionConfig"
