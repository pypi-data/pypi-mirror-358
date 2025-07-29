# -*- coding: utf-8 -*-
from os import makedirs, listdir, remove
from os.path import isdir, join, getmtime
from datetime import date, datetime, timedelta
import json
from decimal import Decimal
import logging
from collections import OrderedDict

from xlsxwriter.workbook import Workbook

from django.utils.translation import gettext as _
from django.utils import formats
from django.conf import settings
from django.db.models import Q, Count
from django.utils.timezone import now, localtime, make_aware, make_naive, get_current_timezone
from django.http import QueryDict

logger = logging.getLogger(__name__)

def formatDate(dt):
    if dt is None:
        return 'n.d.'
    return formats.date_format(dt, "SHORT_DATE_FORMAT")

def clean_dir(mydir):
    # elimina file vecchi da una cartella
    for f in listdir(mydir):
        curpath = join(mydir, f)
        file_modified = datetime.fromtimestamp(getmtime(curpath))
        if datetime.now() - file_modified > timedelta(hours=4):
            remove(curpath)

def create_media_dir(subdir):
    savedir = join(settings.MEDIA_ROOT, subdir)
    # crea una cartella, se non esiste gia'
    if not isdir(savedir):
        makedirs(savedir)
    return savedir

def field_dict_to_tuple(fielddict):
    fieldtuple = [fielddict['key'], fielddict['label'], fielddict['type']]
    if fielddict['type'] == 'enum':
        fieldtuple.append(fielddict['choices'])
    return tuple(fieldtuple)

def field_tuple_to_dict(fieldtuple):
    fielddict = {
        'key': fieldtuple[0],
        'label': fieldtuple[1],
        'type': fieldtuple[2],
    }
    if fielddict['type'] == 'enum':
        fielddict['choices'] = fieldtuple[3]
    return fielddict

def get_searchfields_dict(searchfields):
    searchfields_dict = OrderedDict()
    for searchfield in searchfields:
        if isinstance(searchfield, dict):
            fieldinfo = searchfield
        else:
            fieldinfo = field_tuple_to_dict(searchfield)
        if fieldinfo['type'] == 'bool':
            fieldinfo['choices'] = (('True', 'True'), ('False', 'False'))
        if 'choices' in fieldinfo:
            fieldinfo['choices_dict'] = dict(fieldinfo['choices'])
        searchfields_dict[fieldinfo['key']] = fieldinfo
    return searchfields_dict

def get_search_results_queryset(searchfields, postfields, queryset):
    searchfields_dict = get_searchfields_dict(searchfields)

    lookup_maps = {
        'char': {
            'contains': 'icontains',
            'not_contains': '!icontains',
            'exact': 'iexact',
            'not_exact': '!iexact',
        },
        'num': {
            'gt': 'gt',
            'gte': 'gte',
            'exact': 'exact',
            'lte': 'lte',
            'lt': 'lt',
        }
    }

    # inizializzo i filtri a un Q object vuoto (poi concatenero' altri Q objects con & o |)
    filters = Q()

    # costruisco la query
    for postfield in postfields:
        fieldname = postfield['key']
        searchfield = searchfields_dict.get(fieldname)
        if searchfield is None:
            continue

        logic = postfield.get('logic', 'AND')

        ftype = searchfield['type']
        get_q = searchfield.get('get_q')
        and_q = searchfield.get('and_q')

        # creazione Q object
        if ftype == 'date':
            # se il campo e' di tipo data parso le date di inizio e fine ricerca
            # per trasformarle in datetime.datetime
            try:
                date_start = datetime.strptime(postfield.get('start'), '%d/%m/%Y')
                if settings.USE_TZ:
                    date_start = make_aware(date_start, get_current_timezone())
            except:
                date_start = None
            try:
                date_end = datetime.strptime(postfield.get('end'), '%d/%m/%Y')
                if settings.USE_TZ:
                    date_end = make_aware(date_end, get_current_timezone())
            except:
                date_end = None
            if get_q is not None:
                q = get_q(date_start, date_end)
            else:
                # se il parsing delle date ha avuto esito positivo, le inserisco nella query
                q = Q()
                if date_start is None and date_end is None:
                    # se entrambi i campi sono vuoti cerco una data nulla
                    q &= Q(**{'%s__isnull' % fieldname: True})
                else:
                    # se almeno uno dei due campi e' stato popolato cerco un intervallo di date
                    if date_start is not None:
                        # se presente, data inizio viene inserita con gte (quindi e' compresa)
                        q &= Q(**{'%s__gte' % fieldname: date_start})
                    if date_end is not None:
                        # se presente, data fine viene inserita con lte (quindi e' compresa)
                        q &= Q(**{'%s__lte' % fieldname: date_end})
        else:
            criteria = postfield.get('criteria')
            # lookup, come cercare il valore del campo (esatto, contiene, maggiore di, ...)
            # di default e' exact, che viene usato per i campi di tipo enum, le date hanno un Q object diverso, vedi sotto
            lookup = 'exact'
            # nel caso di campo char e num dipende dalla scelta dell'utente nel form di ricerca
            if ftype in ('char', 'num'):
                try:
                    lookup = lookup_maps[ftype][criteria]
                except:
                    pass
            # se il campo non e' una data uso un Q object con lookup (deciso sopra) e value
            value = postfield.get('value')
            # se il criterio di ricerca e' between faccio diventare value una lista (a partire dalla stringa separata da spazi)
            if criteria == 'between':
                value = value.split()
            if get_q is not None:
                q = get_q(value, ftype, lookup, criteria)
            else:
                if ftype == 'num' and value == '':
                    q = Q(**{'%s__isnull' % fieldname: True})
                elif ftype == 'bool':
                    q = Q(**{'%s' % fieldname: (value == 'True')})
                elif ftype == 'enum' or criteria == 'between':
                    if value is None:
                        # se il menu a tendina multiplo non ha alcun elemento selezionato
                        # allora value e' None. In tal caso cerco record con il campo null
                        q = Q(**{'%s__isnull' % fieldname: True})
                    else:
                        # i campi enum sono select[multiple], quindi il loro valore e' una lista
                        # anche se il criterio di ricerca era between il valore e' stato convertito il lista
                        # in questi casi uso il lookup "__in"
                        q = Q(**{'%s__in' % fieldname: value})
                else:
                    negate = False
                    if lookup[0] == '!':
                        lookup = lookup[1:]
                        negate = True
                    q = Q(**{'%s__%s' % (fieldname, lookup): value})
                    if negate:
                        q = ~q

        if and_q:
            q &= and_q

        # combino il Q object ai precedenti con una certa logica, a seconda di quanto scelto dall'utente
        if logic == 'OR':
            filters |= q
        else:
            filters &= q

    # queryset con i filtri creati sopra
    qs = queryset.filter(filters).distinct()
    # logger.debug(qs.query)

    return qs

def get_search_results_count(searchfields, postfields, queryset):
    qs = get_search_results_queryset(searchfields, postfields, queryset)
    return qs.count()

def add_to_columns_shown(columns_shown, fielddict):
    if 'columns_shown' in fielddict:
        for col in get_searchfields_dict(fielddict['columns_shown']).values():
            columns_shown[col['key']] = col
    else:
        columns_shown[fielddict['key']] = fielddict

def get_search_results(searchfields, postfields, queryset, columns_shown):
    qs = get_search_results_queryset(searchfields, postfields, queryset)
    # lista dei risultati con i filtri creati sopra
    results = qs.values(
        *[ x for x in columns_shown.keys() ]
    )
    return results

def get_columns_shown(fields, postfields, always_shown_columns=None):
    searchfields_dict = get_searchfields_dict(fields)
    # colonne da mostrare nella tabella dei risultati di ricerca
    columns_shown = OrderedDict()
    if always_shown_columns is not None:
        for fieldname in always_shown_columns:
            searchfield = searchfields_dict.get(fieldname)
            if searchfield is None:
                logger.warning('Field name %s used in always_shown_columns is not valid' % fieldname)
            else:
                add_to_columns_shown(columns_shown, searchfield)
    else:
        # se non mi hanno passato always_shown_columns uso tutti i campi di ricerca
        # cio' avviene ad es. in esportazione Excel
        for searchfield in searchfields_dict.values():
            add_to_columns_shown(columns_shown, searchfield)

    for postfield in postfields:
        fieldname = postfield['key']
        searchfield = searchfields_dict.get(fieldname)
        if searchfield is None:
            continue
        # inserisco il campo nelle colonne da mostrare nella tabella dei risultati
        add_to_columns_shown(columns_shown, searchfield)

    return columns_shown

def get_search_response(searchfields, search_data, queryset, results_limit, always_shown_columns=None):
    postfields = json.loads(search_data.decode('utf-8'))
    columns_shown = get_columns_shown(searchfields, postfields, always_shown_columns)
    records = get_search_results(searchfields, postfields, queryset, columns_shown)

    results_count = len(records)
    results = []
    for cnt, v in enumerate(records):
        if results_limit and cnt >= results_limit:
            break
        col = 0
        result = []
        for key, field in columns_shown.items():
            fieldval = v[key]
            ftype = field['type']
            if ftype == 'date':
                try:
                    # provo a convertire in localtime, se fosse un datetime
                    fieldval = localtime(fieldval)
                except:
                    # se e' solo un date pazienza
                    pass
                fieldval = formatDate(fieldval)
            elif ftype == 'enum':
                fieldval = field['choices_dict'].get(fieldval, '')
            elif type(fieldval) == Decimal:
                fieldval = float(fieldval)
            result.append(fieldval)
            col += 1
        results.append(result)
    response = {
        'results_count': results_count,
        'results_limit': results_limit,
        'results': results,
        'columns': [ x['label'] for x in columns_shown.values() ]
    }
    return response

def get_search_excel(searchfields, search_data, queryset, excelfields=None, filename_prefix=None):
    if excelfields is None:
        excelfields = searchfields
    if filename_prefix is None:
        filename_prefix = 'search_results'

    postfields = json.loads(search_data.decode('utf-8'))
    columns_shown = get_columns_shown(excelfields, postfields)
    results = get_search_results(searchfields, postfields, queryset, columns_shown)
    subdir = 'search'
    savedir = create_media_dir(subdir)
    clean_dir(savedir)

    timestamp = now()
    filename = '%s_%s.xlsx' % (filename_prefix, timestamp.strftime('%Y%m%d%H%M%S%f'))
    filepath = join(savedir, filename)

    workbook = Workbook(filepath, {'constant_memory': True, 'tmpdir': savedir})
    bold = workbook.add_format({'bold': True})
    date_format = workbook.add_format({'num_format': 'DD/MM/YYYY'})
    currency_format = workbook.add_format({'num_format': '#,##0.00'})
    worksheet = workbook.add_worksheet(_('Search results'))

    headers = []
    for field in columns_shown.values():
        headers.append(field['label'])

    worksheet.write_row(0, 0, headers, bold)
    worksheet.set_column(0, len(headers), 30)

    row = 1
    for result in results:
        col = 0
        for key, field in columns_shown.items():
            fieldval = result[key]
            ftype = field['type']
            try:
                if fieldval is None:
                    worksheet.write_string(row, col, '')
                elif ftype == 'date':
                    try:
                        # provo a convertire in localtime, se fosse un datetime
                        fieldval = localtime(fieldval)
                        fieldval = make_naive(fieldval, get_current_timezone())
                    except:
                        # se e' solo un date pazienza
                        pass
                    worksheet.write_datetime(row, col, fieldval, date_format)
                elif ftype == 'currency':
                    worksheet.write_number(row, col, fieldval, currency_format)
                elif ftype in ('char', 'bool'):
                    worksheet.write_string(row, col, str(fieldval))
                elif ftype == 'enum':
                    worksheet.write_string(row, col, str(field['choices_dict'].get(fieldval, '')))
                elif ftype == 'num':
                    worksheet.write_number(row, col, fieldval)
            except:
                logger.exception('Errore durante la scrittura del campo %s, %s: %s' % (key, ftype, str(fieldval)))
                raise
            col += 1
        row += 1

    workbook.close()

    # ritorno il percorso al file Excel appena salvato
    return join(settings.MEDIA_URL, subdir, filename)

def search_results_multiple_edit(searchfields, search_data, queryset, form_class):
    # il decode('utf-8') per Py3 lo fa gia' a livello di SearchResultsMultipleEditMixin
    search_data = json.loads(search_data)
    form_data = QueryDict(search_data['formdata'])

    columns_shown = {
        'id': field_tuple_to_dict(('id', 'ID', 'char'))
    }
    results = get_search_results(searchfields, search_data['postfields'], queryset, columns_shown)
    success_ids = []
    error_list = []

    for result in results:
        if result['id'] in success_ids:
            continue
        instance = queryset.get(pk=result['id'])
        form = form_class(form_data, instance=instance)
        if form.is_valid():
            form.save()
            success_ids.append(result['id'])
        else:
            for key, errors in form.errors.items():
                for error in errors:
                    error_string = '%s - %s' % (instance, error)
                    error_list.append(error_string)

    ret = {'cnt_success': len(success_ids), 'error_list': error_list}
    if 'multiple_edit_timestamp' in form_data:
        ret['multiple_edit_timestamp'] = form_data['multiple_edit_timestamp']
    return ret
