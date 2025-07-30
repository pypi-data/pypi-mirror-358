from NEMO.decorators import customization
from NEMO.utilities import render_email_template
from NEMO.views.customization import CustomizationBase, get_media_file_contents


@customization("stockroom", "Stockroom")
class StockroomCustomization(CustomizationBase):
    files = [("stockroom_order_confirmation_email", ".html")]

    @staticmethod
    def render_template(template_name, dictionary: dict, request=None):
        template = get_media_file_contents(template_name)
        return render_email_template(template, dictionary, request=request)
