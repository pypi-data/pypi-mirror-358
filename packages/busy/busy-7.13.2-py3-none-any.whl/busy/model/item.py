import re
from dataclasses import KW_ONLY, dataclass
from datetime import date, datetime
from functools import cached_property


from busy.util.date_util import absolute_date
from busy.util.date_util import relative_date
from busy.util import date_util


class ItemStateError(Exception):
    pass


START_TIME_FORMAT = '%Y%m%d%H%M'
DATE_FORMAT = '%Y-%m-%d'


class Item:
    """A single entry in a queue"""

    markup: str
    state: str
    plan_date: date
    done_date: date

    @classmethod
    def get_properties(cls):
        result = []
        for name, attr in cls.__dict__.items():
            if isinstance(attr, cached_property):
                result.append(name)
        return result

    def __init__(
            self, markup: str, state: str = 'todo', done_date: date = None,
            plan_date: date = None):
        self.markup = markup
        self.state = state
        self.done_date = done_date
        self.plan_date = plan_date

        # Preload the cache to populate __dict__ and vars()
        for attr in self.get_properties():
            getattr(self, attr)

    # ---- Basic properties ----

    def __str__(self):
        """Represent the item as its simple form"""
        return self.simple

    @cached_property
    def body(self):
        """Without the repeat followon"""
        split = self.FOLLOW_SPLIT.split(self.markup, maxsplit=1)
        if split:
            return split[0]
        else:
            return ""

    @cached_property
    def _words(self):
        return self.body.split()

    @cached_property
    def base(self):
        """body with no tags, resource, or data"""
        wins = [w for w in self._words if w[0] not in '#@!%']
        return " ".join(wins)

    @cached_property
    def noparens(self):
        """remove parenthetical expressions"""
        result = ''
        depth = 0
        for char in self.base:
            if char == '(':
                depth += 1
            elif char == ')' and depth > 0:
                depth -= 1
            elif depth == 0:
                result += char
        return result.strip()

    @cached_property
    def simple(self):
        """Base plus tags"""
        wins = [w for w in self._words if w[0] not in '@!']
        return " ".join(wins)

    @cached_property
    def listable(self):
        """Simple plus repeat"""
        if self.repeat:
            return f"{self.simple} > {self.repeat}"
        else:
            return self.simple

    @cached_property
    def notiming(self):
        """Everything but the timing data"""
        wins = [w for w in self._words if w[0] not in '!']
        return " ".join(wins)

    @cached_property
    def checkbox(self):
        """GitLab-style Markdown checkbox"""
        checked = 'x' if self.state == 'done' else ' '
        return f"- [{checked}]"

    @cached_property
    def fuzzkey(self):
        """Key for fuzzy matching and deduplication"""
        return self.noparens.lower()

    # ---- Date operations ----

    def __setattr__(self, name, value):
        """Allow dates to be set with words"""
        if name in self.__annotations__ and \
                self.__annotations__[name] == date:
            value = absolute_date(value)
        super().__setattr__(name, value)

    # ---- Marked properties ----

    def _marked(self, mark):
        return [w[1:] for w in self._words if w.startswith(mark)]

    @cached_property
    def tags(self):
        """A set of tags - indicated with #"""
        return {m.lower() for m in self._marked('#')}

    @cached_property
    def url(self):
        """A single URL associated with the item - indicated with @"""
        return (self._marked('@') + ['']).pop(0)

    def data_value(self, key: str):
        """A data value for a given 1-letter key - indicted with % and the key.
        Note there can only be one of each key in the markup."""
        return next((m[1:] for m in self._marked("%") if m[0] == key), None)

    # ---- Repeat operations ----

    # Older versions of Busy supported an elaborate "followon" mechanism
    FOLLOW_SPLIT = re.compile(r'\s*\-*\>\s*')
    LEGACY_REPEAT = re.compile(r'^\s*repeat(?:\s+[io]n)?\s+(.+)\s*$', re.I)

    @cached_property
    def repeat(self):
        """Second and successive segments, all but body"""
        split = self.FOLLOW_SPLIT.split(self.markup, maxsplit=1)
        if len(split) > 1:
            next = split[1]
            # Legacy "repeat" text
            match = self.LEGACY_REPEAT.match(next)
            if match:
                return match.group(1)
            else:
                return next
        else:
            return ""

    # ---- State operations ----

    def restricted(*allowed_states):
        """Restrict a method to a specific set of states"""
        def wrapper(method):
            def replacement(self, *args, **kwargs):
                if self.state in allowed_states:
                    return method(self, *args, **kwargs)
                else:
                    raise ItemStateError
            return replacement
        return wrapper

    @restricted('todo')
    def done(self, done_date: date, plan_date: date = None):
        """Updates the item to done and returns a copy as a plan for the
        plan_date if provided"""
        self.state = 'done'
        self.done_date = done_date
        plan_repeat = self.repeat
        self.repeat = ''
        self.rewrite_markup()
        if plan_date:
            plan_markup = self.notiming
            if plan_repeat:
                plan_markup += f" > {plan_repeat}"
            return Item(plan_markup, state='plan', plan_date=plan_date)

    @restricted('done')
    def undone(self):
        self.state = 'todo'

    @restricted('todo')
    def plan(self, plan_date: date):
        self.state = 'plan'
        self.plan_date = plan_date

    @restricted('plan')
    def unplan(self):
        self.state = 'todo'

    # ---- Time operations ----

    @cached_property
    def timing_data(self):
        """Dict of words starting with !"""
        return {m[0]: m[1:] for m in self._marked("!")}

    @cached_property
    def elapsed(self):
        if 'e' in self.timing_data:
            return int(self.timing_data['e'])
        else:
            return 0

    @cached_property
    def start_time(self):
        if 's' in self.timing_data:
            return datetime.strptime(self.timing_data['s'], START_TIME_FORMAT)

    @restricted('todo')
    def update_time(self):
        """Update elapsed time based on start time - also updates markup for
        saving"""
        if self.start_time and self.base:
            prev = self.elapsed
            new = (date_util.now() - self.start_time).seconds // 60
            self.elapsed = new + prev
            self.start_time = None
            self.rewrite_markup()

    def rewrite_markup(self):
        changed = self.notiming
        if self.elapsed:
            changed += f" !e{self.elapsed}"
        if self.repeat:
            changed += f" > {self.repeat}"
        self.markup = changed

    @restricted('todo')
    def start_timer(self):
        """Starts timing when activity begins on a task"""
        if self.base and not self.start_time:
            self.start_time = date_util.now()
            formatted = self.start_time.strftime(START_TIME_FORMAT)
            changed = f"{self.notiming} !s{formatted}"
            if self.elapsed:
                changed += f" !e{self.elapsed}"
            if self.repeat:
                changed += f" > {self.repeat}"
            self.markup = changed

    # ---- Named filters for Selector ----

    def filter_val(self, key_val):
        val = self.data_value(key_val[0])
        return ((val is not None) and (val == key_val[1:]))

    def filter_donemin(self, min_date):
        if self.done_date:
            return self.done_date >= absolute_date(min_date)

    def filter_donemax(self, max_date):
        if self.done_date:
            return self.done_date <= absolute_date(max_date)

    def filter_planmin(self, min_date):
        if self.plan_date:
            return self.plan_date >= absolute_date(min_date)

    def filter_planmax(self, max_date):
        if self.plan_date:
            return self.plan_date <= absolute_date(max_date)

    # ---- Properties for reading in formatted output

    # @property
    # def __dict__(self):
    #     return {
    #         'base': self.base,
    #         'tag': self.tagobj,
    #         'val': self.valobj
    #     }

    @cached_property
    def tag(self):
        result = Obj()
        for tag in self.tags:
            setattr(result, tag, tag)
        return result

    @cached_property
    def val(self):
        result = Obj()
        for mark in self._marked("%"):
            setattr(result, mark[0], mark[1:])
        return result

    # ---- Cached versions of attributes for view command

    @cached_property
    def donedate(self):
        if self.state == 'done' and self.done_date:
            return self.done_date.strftime(DATE_FORMAT)

    @cached_property
    def plandate(self):
        if self.state == 'plan' and self.plan_date:
            return self.plan_date.strftime(DATE_FORMAT)

    @cached_property
    def markup(self):
        return self.markup


class Obj:

    def __getattr__(self, attr):
        return ''
