from django import forms
from django.urls import reverse_lazy


class AutocompleteWidget(forms.TextInput):
    """A suitable autocomplete widget for Django forms using web components."""

    template_name = "suitable_django_autocomplete/autocomplete.html"

    def __init__(self, url=None, attrs=None, min_length=2, debounce_delay=300,
                 value_field='value', label_field='label', initial_display_value=None,
                 host_attrs=None):
        self.url = url
        self.min_length = min_length
        self.debounce_delay = debounce_delay
        self.value_field = value_field
        self.label_field = label_field
        self.initial_display_value = initial_display_value
        self.host_attrs = host_attrs or {}
        super().__init__(attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"].update(
            {
                "url": self.url or reverse_lazy("autocomplete"),
                "min_length": self.min_length,
                "debounce_delay": self.debounce_delay,
                "value_field": self.value_field,
                "label_field": self.label_field,
                "initial_display_value": self.initial_display_value,
                "host_attrs": self.host_attrs,
            }
        )
        return context
    
    def set_initial_display_value_from_instance(self, obj, search_fields=None):
        """
        Helper method to set initial_display_value from a model instance.
        This can be called by ModelAutocompleteField.
        """
        if not obj:
            return
            
        # Use search_fields if provided to determine display value
        if search_fields:
            first_field = search_fields[0]
            # Handle related fields (e.g., 'user__username')
            if '__' in first_field:
                parts = first_field.split('__')
                value = obj
                for part in parts:
                    value = getattr(value, part, None)
                    if value is None:
                        break
                self.initial_display_value = str(value) if value is not None else str(obj)
            else:
                self.initial_display_value = str(getattr(obj, first_field, obj))
        else:
            # Fall back to string representation
            self.initial_display_value = str(obj)

    # When migrating to 5.2 only, use this to module load instead of in template. Nice.
    # class Media:
    #     js = [
    #         Script(
    #             "suitable_django_autocomplete/autocomplete.js",
    #             **{
    #                 "type": "module",
    #             },
    #         ),
    #     ]
