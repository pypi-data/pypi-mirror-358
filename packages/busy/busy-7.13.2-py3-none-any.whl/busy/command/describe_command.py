from busy.command import CollectionCommand


class DescribeCommand(CollectionCommand):
    """Show the full markup"""

    name = 'describe'

    @CollectionCommand.wrap
    def execute(self):
        return self.output_items(lambda i: i.markup)
