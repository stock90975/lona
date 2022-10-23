from lona.events.event_types import CHANGE
from lona.html.node import Node


class Option(Node):
    TAG_NAME = 'option'

    def __init__(self, *args, value='', selected=False, disabled=False,
                 **kwargs):

        super().__init__(*args, **kwargs)

        self._select = None
        self.value = value
        self.selected = selected
        self.disabled = disabled

    def _set_selected(self, selected):
        with self.lock:
            if selected and 'selected' not in self.attributes:
                self.attributes['selected'] = ''

            elif not selected and 'selected' in self.attributes:
                del self.attributes['selected']

    # properties ##############################################################
    # value
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        with self.lock:
            self.attributes['value'] = str(new_value)
            self._value = new_value

    # selected
    @property
    def selected(self):
        return 'selected' in self.attributes

    @selected.setter
    def selected(self, new_value):
        with self.lock:
            if self._select:
                self._select._set_selected(self, new_value)

            else:
                self._set_selected(new_value)

    # disabled
    @property
    def disabled(self):
        return 'disabled' in self.attributes

    @disabled.setter
    def disabled(self, new_value):
        if new_value:
            self.attributes['disabled'] = ''

        else:
            del self.attributes['disabled']


class Select(Node):
    TAG_NAME = 'select'
    EVENTS = [CHANGE]

    def __init__(self, *options, disabled=False, multiple=False,
                 readonly=False, bubble_up=False, **kwargs):

        super().__init__(**kwargs)

        self.options = options
        self.disabled = disabled
        self.multiple = multiple
        self.readonly = readonly
        self.bubble_up = bubble_up

    def handle_input_event(self, input_event):
        if input_event.name != 'change':
            return super().handle_input_event(input_event)

        # select options by index
        selected_option_indexes = input_event.data

        with self.lock:
            for index, option in enumerate(self.options):
                option._set_selected(index in selected_option_indexes)

        # run custom change event handler
        input_event = self.handle_change(input_event)

        if self.bubble_up:
            return input_event

    def _set_selected(self, option, selected):
        with self.lock:
            if self.multiple:
                option._set_selected(selected)

                return

            for _option in self.options:
                _option._set_selected(_option is option)

    # select properties #######################################################
    # disabled
    @property
    def disabled(self):
        return 'disabled' in self.attributes

    @disabled.setter
    def disabled(self, new_value):
        if not isinstance(new_value, bool):
            raise TypeError('disabled is a boolean property')

        if new_value:
            self.attributes['disabled'] = ''

        else:
            del self.attributes['disabled']

    # multiple
    @property
    def multiple(self):
        return 'multiple' in self.attributes

    @multiple.setter
    def multiple(self, new_value):
        if not isinstance(new_value, bool):
            raise TypeError('multiple is a boolean property')

        if new_value:
            self.attributes['multiple'] = ''

        else:
            del self.attributes['multiple']

    # readonly
    @property
    def readonly(self):
        return 'readonly' in self.attributes

    @readonly.setter
    def readonly(self, new_value):
        if not isinstance(new_value, bool):
            raise TypeError('readonly is a boolean property')

        if new_value:
            self.attributes['readonly'] = ''

        else:
            del self.attributes['readonly']

    # option properties #######################################################
    # options
    @property
    def options(self):
        with self.lock:
            options = ()

            for node in self.nodes:
                if node.tag_name != 'option':
                    continue

                options += (node, )

            return options

    @options.setter
    def options(self, new_options):
        with self.lock:
            self.nodes.clear()

            if not isinstance(new_options, (list, tuple)):
                new_options = [new_options]

            for option in new_options:
                self.add_option(option)

    # selected options
    @property
    def selected_options(self):
        with self.lock:
            options = ()

            for option in self.options:
                if not option.selected:
                    continue

                options += (option, )

            if not options and self.options and not self.multiple:
                return (self.options[0], )

            return options

    # value
    @property
    def value(self):
        with self.lock:
            values = ()

            for option in self.selected_options:
                values += (option.value, )

            if not self.multiple:
                if not values:
                    return self.options[0].value

                return values[-1]

            return values

    @value.setter
    def value(self, new_value):
        with self.lock:
            if not isinstance(new_value, list):
                new_value = [new_value]

            old_values = self.values

            for value in new_value:
                if value not in old_values:
                    raise RuntimeError(f'unknown value: {value}')

            for option in self.options:
                option._set_selected(option.value in new_value)

    # values
    @property
    def values(self):
        with self.lock:
            values = ()

            for option in self.options:
                values += (option.value, )

            return values

    # helper ##################################################################
    def add_option(self, option):
        with self.lock:
            option._select = self
            self.nodes.append(option)

    def remove_option(self, option):
        with self.lock:
            option._select = None
            self.nodes.remove(option)

    def select_all(self):
        with self.lock:
            for option in self.options:
                option.selected = True

    def select_none(self):
        with self.lock:
            for option in self.options:
                option.selected = False
