from copy import copy
from typing import Dict

from NEMO.widgets.dynamic_form import PostUsageQuestion, question_types
from django.template.loader import render_to_string
from django.templatetags.static import static


class PeriodicQuestion(PostUsageQuestion):
    def __init__(self, properties: Dict, index: int = None, initial_data=None):
        super().__init__(properties, index, initial_data)
        self.css_file = static("NEMO_periodic_table_question/periodic_table.css")
        self.collapsible = self._init_property("collapsible", boolean=True)
        self.collapsed = self._init_property("collapsed", boolean=True)

    def render_element(self, virtual_inputs: bool, group_question_url: str, group_item_id: int, extra_class="") -> str:
        title = self.title_html or self.title
        default_value = self.get_default_value()
        if default_value:
            if isinstance(default_value, str):
                default_value = [default_value]
        dictionary = {
            "default_value": default_value,
            "question_title": title,
            "form_name": self.form_name,
            "collapsible": self.collapsible,
            "collapsed": self.collapsed,
            "required_span": self.required_span if self.required else "",
            "help": self.help,
        }
        return render_to_string("NEMO_periodic_table_question/periodic_table.html", dictionary)

    def extract(self, request, index=None) -> Dict:
        answered_question = copy(self.properties)
        user_input = request.POST.getlist(f"{self.form_name}_{index}" if index else self.form_name)
        if user_input:
            answered_question["user_input"] = user_input
        return answered_question


question_types["periodic-table"] = PeriodicQuestion
