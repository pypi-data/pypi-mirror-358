import json
import logging
import six

from django.forms import modelform_factory
from django.template.loader import render_to_string
try:
    from django.core.context_processors import csrf
except:
    from django.template.context_processors import csrf

from crispy_forms.utils import render_crispy_form
from crispy_forms.helper import FormHelper

from .views_functions import search_results_multiple_edit, get_search_results_count, \
    field_dict_to_tuple


logger = logging.getLogger(__name__)


class SearchViewMixin(object):

    def get(self, request):
        searchfields = self.get_fields(request)
        # escludo campo id dai campi ricercabili
        # e converto eventuali dict affinche' siano una tupla (per permettere la serializzazione in json nel template)
        self.searchfields = []
        for f in searchfields[1:]:
            if isinstance(f, dict):
                f = field_dict_to_tuple(f)
            if f[2] == 'enum':
                f = (f[0], f[1], f[2], [ x for x in f[3] ])
            self.searchfields.append(f)
        self.searchfields.sort(key=lambda x: x[1])
        return super(SearchViewMixin, self).get(request)


class SearchResultsMultipleEditMixin(object):
    template_name_confirm = 'search/_multiple_edit_count.html'
    template_name_success = 'search/_multiple_edit_results.html'

    def get_form_class(self, for_display=True):
        return modelform_factory(self.model, fields=self.fields)

    def get_form(self, *args, **kwargs):

        class DefaultFormHelper(FormHelper):
            form_tag = False
            form_class = 'form-horizontal'
            label_class = 'col-lg-4'
            field_class = 'col-lg-8'

        form = self.get_form_class(True)(*args, **kwargs)
        form.helper = DefaultFormHelper()
        return form

    def get_queryset(self):
        return self.model.objects.all()

    def post_ajax(self, request, *args, **kwargs):
        request_body = request.body
        if six.PY3:
            request_body = request_body.decode('utf8')
        search_data = json.loads(request_body)
        if 'formdata' in search_data:
            result = search_results_multiple_edit(self.get_search_fields(), request_body, self.get_queryset(), self.get_form_class(False))
            result.update({ 'form': self.get_form() })
            html = render_to_string(self.template_name_success, result, request=request)
        else:
            cnt_results = get_search_results_count(self.get_search_fields(), search_data['postfields'], self.get_queryset())
            html = render_to_string(self.template_name_confirm, {
                'form': self.get_form(),
                'cnt_results': cnt_results,
            }, request=request)
        return self.render_json_response({'html': html})
