from typing import List, Dict, Any, Optional
from django.http import JsonResponse, HttpRequest
from django.views import View
from django.views.generic.list import BaseListView
from django.db.models import Q, QuerySet
from django.core.serializers import serialize
from django.utils.html import escape
import json


class AutocompleteView(View):
    """Base view for handling autocomplete requests."""
    
    def get_results(self, query: str) -> List[Any]:
        """
        Override this method to return autocomplete results.
        Should return a list of strings or dictionaries.
        """
        raise NotImplementedError("Subclasses must implement get_results()")
    
    def get(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        query: str = request.GET.get('q', '')
        
        if not query:
            return JsonResponse({'results': [], 'query': query})
        
        results = self.get_results(query)
        return JsonResponse({'results': results, 'query': query})


class ModelAutocompleteView(AutocompleteView):
    """
    Base view for model-based autocomplete.
    Subclasses should set model and search_fields attributes.
    """
    model: Optional[type] = None
    search_fields: List[str] = []
    limit: int = 20
    
    def get_queryset(self) -> QuerySet:
        """Get the base queryset. Override to add custom filtering."""
        if self.model is None:
            raise NotImplementedError("ModelAutocompleteView requires a model attribute")
        return self.model.objects.all()
    
    def get_search_fields(self) -> List[str]:
        """Get the fields to search in. Override to customize."""
        if not self.search_fields:
            raise NotImplementedError("ModelAutocompleteView requires search_fields attribute")
        return self.search_fields
    
    def format_result(self, obj: Any) -> Dict[str, str]:
        """
        Format a model instance for the autocomplete response.
        Returns a dict with 'value' (obj.id) and 'label' (first search field).
        Override to customize the output format.
        
        Note: Values are HTML-escaped to prevent XSS attacks.
        """
        search_fields = self.get_search_fields()
        
        # Get the value for the label from the first search field
        if search_fields:
            label_field = search_fields[0]
            label_value = getattr(obj, label_field, str(obj))
        else:
            label_value = str(obj)
        
        return {
            'value': escape(str(obj.id)),
            'label': escape(str(label_value)),
        }
    
    def get_results(self, query: str) -> List[Dict[str, str]]:
        """Search the model and return results."""
        queryset = self.get_queryset()
        search_fields = self.get_search_fields()
        
        # Build the Q object for searching
        search_query = Q()
        for field in search_fields:
            search_query |= Q(**{f"{field}__icontains": query})
        
        # Filter and limit results
        results = queryset.filter(search_query)[:self.limit]
        
        # Format results
        return [self.format_result(obj) for obj in results]


class SimpleAutocompleteView(AutocompleteView):
    """
    Simple autocomplete view that returns static choices.
    Useful for non-model based autocomplete.
    """
    choices: List[Any] = []
    
    def get_choices(self) -> List[Any]:
        """Get the list of choices. Override to make dynamic."""
        return self.choices
    
    def get_results(self, query: str) -> List[Any]:
        """Filter choices based on query."""
        choices = self.get_choices()
        query_lower = query.lower()
        
        return [
            choice for choice in choices 
            if query_lower in str(choice).lower()
        ][:20]  # Limit to 20 results