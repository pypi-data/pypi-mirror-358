from django import forms
from .widgets import AutocompleteWidget


class AutocompleteField(forms.CharField):
    """Form field that uses the AutocompleteWidget by default."""
    
    def __init__(self, *args, url=None, min_length=2, debounce_delay=300, attrs=None, 
                 host_attrs=None, **kwargs):
        self.url = url
        self.min_length = min_length
        self.debounce_delay = debounce_delay
        self.host_attrs = host_attrs
        
        # Set the widget if not already specified
        if 'widget' not in kwargs:
            kwargs['widget'] = AutocompleteWidget(
                url=url,
                min_length=min_length,
                debounce_delay=debounce_delay,
                attrs=attrs,
                host_attrs=host_attrs
            )
        
        super().__init__(*args, **kwargs)


class ModelAutocompleteField(forms.ModelChoiceField):
    """Model choice field that uses the AutocompleteWidget."""
    
    def __init__(self, queryset, *args, url=None, min_length=2, debounce_delay=300, attrs=None, 
                 host_attrs=None, search_fields=None, **kwargs):
        self.url = url
        self.min_length = min_length
        self.debounce_delay = debounce_delay
        self.host_attrs = host_attrs
        self.search_fields = search_fields or []
        
        # Set the widget if not already specified
        if 'widget' not in kwargs:
            kwargs['widget'] = AutocompleteWidget(
                url=url,
                min_length=min_length,
                debounce_delay=debounce_delay,
                attrs=attrs,
                host_attrs=host_attrs
            )
        
        super().__init__(queryset, *args, **kwargs)
    
    
    def to_python(self, value):
        """Convert the autocomplete value to a model instance."""
        if value in self.empty_values:
            return None
        try:
            # Try to get by primary key first
            key = self.to_field_name or 'pk'
            value = self.queryset.get(**{key: value})
        except (ValueError, TypeError, self.queryset.model.DoesNotExist):
            # If that fails, try to get by string representation
            # This allows for more flexible autocomplete implementations
            try:
                for obj in self.queryset:
                    if str(obj) == value:
                        return obj
            except:
                pass
            raise forms.ValidationError(
                self.error_messages['invalid_choice'],
                code='invalid_choice',
                params={'value': value},
            )
        return value
    
    def get_display_value(self, obj):
        """
        Get a display value for the given model instance.
        Uses the first search field if available, otherwise str(obj).
        """
        if not obj:
            return ''
            
        # If search_fields are specified, use the first one
        if self.search_fields:
            first_field = self.search_fields[0]
            # Handle related fields (e.g., 'user__username')
            if '__' in first_field:
                parts = first_field.split('__')
                value = obj
                for part in parts:
                    value = getattr(value, part, None)
                    if value is None:
                        break
                return str(value) if value is not None else str(obj)
            else:
                return str(getattr(obj, first_field, obj))
        
        # Fall back to string representation
        return str(obj)
    
    def prepare_value(self, value):
        """
        Prepare the value for display in the widget.
        Also sets the initial_display_value for model instances.
        """
        # Let the parent class handle the basic value preparation
        prepared_value = super().prepare_value(value)
        
        # Set the initial_display_value if we have a model instance and no manual value
        if value and not self.widget.initial_display_value:
            try:
                if hasattr(value, 'pk'):
                    # It's already a model instance
                    obj = value
                elif prepared_value:
                    # It's an ID, try to fetch the instance
                    obj = self.queryset.get(pk=prepared_value)
                else:
                    obj = None
                
                if obj:
                    # Use the widget's helper method
                    self.widget.set_initial_display_value_from_instance(obj, self.search_fields)
            except (ValueError, TypeError, self.queryset.model.DoesNotExist):
                pass
        
        # Ensure we return a string
        return str(prepared_value) if prepared_value is not None else ''