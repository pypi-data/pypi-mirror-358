import yaml
from functools import cached_property

from busy.command import MultiCollectionCommand
from busy.model.item import Item


class DumpCommand(MultiCollectionCommand):
    """Dump items as YAML with same filtering as view command"""

    name = 'dump'

    @MultiCollectionCommand.wrap
    def execute(self):
        items_data = []
        for index, item in self.viewable_items:
            item_dict = self._item_to_dict(item)
            if item_dict:  # Only add if has content
                items_data.append(item_dict)

        result = {self.queue: items_data}
        return yaml.dump(result, default_flow_style=False, sort_keys=False)

    @cached_property
    def viewable_items(self):
        """Filter for uniqueness if requested - copied from ViewCommand"""
        # TODO: Move this to a logical/sensible shared location to keep DRY
        if hasattr(self, 'unique') and self.unique:
            items = []
            fuzzmatches = set()
            for index, item in reversed(self.selection):
                fuzzkey = item.fuzzkey
                if fuzzkey not in fuzzmatches:
                    items.append((index, item))
                    fuzzmatches.add(item.fuzzkey)
            items.reverse()
            return items
        else:
            return self.selection

    def _item_to_dict(self, item):
        """Convert an Item to a dictionary with only non-empty values"""
        result = {}

        # Always include base and state
        result['base'] = item.base
        result['state'] = item.state

        # Tags as list (only if not empty)
        if item.tags:
            result['tags'] = sorted(list(item.tags))

        # Data section (preserve original types)
        # TODO: Consider using a simple method on item to return all the vals
        data_dict = {}
        for mark in item._marked("%"):
            key = mark[0]
            value = mark[1:]
            # Try to preserve type - if it's numeric, keep as number
            try:
                if '.' in value:
                    data_dict[key] = float(value)
                else:
                    data_dict[key] = int(value)
            except ValueError:
                data_dict[key] = value  # Keep as string

        if data_dict:
            result['data'] = data_dict

        # Timing section (only if has timing data)
        timing_dict = {}
        if item.elapsed > 0:
            timing_dict['elapsed'] = item.elapsed
        if item.start_time:
            timing_dict['start'] = None  # ISO format when timing is active

        if timing_dict:
            result['timing'] = timing_dict

        # URL (only if not empty)
        if item.url:
            result['url'] = item.url

        # Repeat (only if not empty)
        if item.repeat:
            result['repeat'] = item.repeat

        # Dates section (only if has any dates)
        dates_dict = {}
        if item.done_date:
            dates_dict['done'] = item.done_date.strftime('%Y-%m-%d')
        if item.plan_date:
            dates_dict['plan'] = item.plan_date.strftime('%Y-%m-%d')

        if dates_dict:
            result['dates'] = dates_dict

        return result
