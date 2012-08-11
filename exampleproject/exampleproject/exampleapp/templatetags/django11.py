from django.template import Library, Node
register = Library()


class DumbNode(Node):
    def render(self, context):
        return ''


@register.tag
def csrf_token(parser, token):
    return DumbNode()
