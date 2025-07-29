// FIXME globalone perche' usate anche da terze parti. Trovare soluzione + elegante
var _ = strings_to_translate

var buildSearchData = function() {
    var postfields = [];
    $('.searchpanel-body').each(function() {
        var searchfield = $(this).find('.searchfield');
        var option = searchfield.find(':selected');
        var field = option.data('field');
        if (typeof field !== 'undefined') {
            var fieldname = field[0]
            var type = field[2];
            var postfield = {
                key: fieldname,
                type: type
            }

            var widget = $(this).find('.widget');
            if (type == 'char' || type == 'num') {
                var input = widget.find('input');
                postfield.value = input.val();
                postfield.criteria = input.data('criteria');
            } else if (type == 'date') {
                var input_start = widget.find('input.start');
                var input_end = widget.find('input.end');
                postfield.start = input_start.val();
                postfield.end = input_end.val();
            } else if (type == 'enum') {
                var choices = widget.find('.enum_choices');
                postfield.value = choices.val();
            } else if (type == 'bool') {
                var choices = widget.find('.bool_choices');
                postfield.value = choices.val();
            }

            var searchlogic = $(this).find('.searchlogic');
            if (searchlogic.length > 0) {
                postfield.logic = searchlogic.val();
            }

            postfields.push(postfield)
        }
    });
    return postfields;
};
var add_search_field = function(logic) {
    var template_id = '#searchfield_template';
    if (logic) {
        template_id += '_logic';
    }
    // recupero l'html del campo di ricerca dal div nascosto e lo inserisco in #searchfields
    $('#searchfields').append($(template_id).html());
    // ritorno l'elemento appena appeso a searchfields
    return $('#searchfields').find('.searchfield-container').last();
};
var showSearchWidget = function(elem) {
    var div = elem.closest('.searchpanel-body').find('.widget_container');
    div.find('.widget').remove();
    var option = elem.find(':selected');
    var field = option.data('field');
    var type = field[2];
    // recupero l'html del widget da uno dei div nascosti
    var html = $('#' + type + '_widget').html();
    div.append(html);
    // se e' un campo date devo attivare il datepicker
    if (type == 'date') {
        div.find('.input-daterange').datepicker({
            language: 'it',
            todayHighlight: true
        });
    } else if (type == 'enum') {
        var choices = field[3];
        var select = div.find('.enum_choices');
        $.each(choices, function(idx, choice) {
            select.append($('<option></option>').attr('value', choice[0]).text(choice[1]));
        });
    }
};
var searchDataToWidgets = function(searchconfig) {
    if (searchconfig.length) {
        // if there are actual fields in the preset, replicate them
        $('#searchfields').empty();
        $.each(searchconfig, function(idx, field) {
            var elem = add_search_field((idx != 0));
            var searchfield = elem.find('.searchfield');
            var searchlogic = elem.find('.searchlogic');
            searchfield.val(field.key);
            showSearchWidget(searchfield);
            if (elem.find('.input-daterange').length) {
                // se e' un campo data popolo .start e .end
                var datewidget = elem.find('.input-daterange');
                datewidget.find('.start').val(field.start);
                datewidget.find('.end').val(field.end);
            } else {
                // altrimenti popolo .searchvalue
                var searchvalue = elem.find('.searchvalue');
                searchvalue.val(field.value);
            }
            if (field.hasOwnProperty('logic')) {
                searchlogic.val(field.logic);
            }
            if (field.hasOwnProperty('criteria')) {
                elem.find('.criteria[data-criteria="' + field.criteria + '"]').trigger('click');
            }
        });
    } else {
        // if the preset had no fields, add a default empty field to the search fields panel
        add_search_field(false);
    }
};
var createSearchActionForm = function(modal_id, html) {
    $(modal_id + ' .modal-body').html(html);
    $('.dateinput').datepicker({
        language: 'it',
        todayHighlight: true,
        autoclose: true
    });
};
var doExport = function(id_button, click_handler) {
    var postfields = buildSearchData();
    var button = $(id_button);
    var searchurl = button.data('url');
    $('#wait-icon').addClass('fa-spinner fa-spin');
    button.off('click');
    $.ajax({
        type: "POST",
        url: searchurl,
        data: JSON.stringify(postfields),
        contentType: "application/json; charset=utf-8",
        success: function(data) {
            window.location = data;
        },
        failure: function(jqXHR, msg) {
            console.log(msg);
        },
        complete: function(jqXHR, msg) {
            $('#wait-icon').removeClass('fa-spinner fa-spin');
            button.on('click', click_handler);
        }
    });
};
var search_results_listeners = [];

$(function() {
    var searchfields = $('#searchfields').data('searchfields');
    $('#add_search_field').click(function() {
        add_search_field(true);
    });
    $('#reset_search').click(function() {
        $('#search_results').empty();
        $('#searchfields').empty();
        add_search_field(false);
    });
    $('#searchfields').on('change', '.searchfield', function() {
        showSearchWidget($(this));
    });
    $('#searchfields').on('click', '.criteria', function() {
        $(this).closest('.input-group').find('input').data('criteria', $(this).data('criteria'));
        $(this).closest('.input-group-btn').find('.dropdown-toggle').find('span').text($(this).text());
    });
    $('#searchfields').on('click', '.searchfield-delete', function() {
        $(this).closest('.searchfield-container').remove();
    });
    var clipboard;
    var doSearch = function() {
        var postfields = buildSearchData();
        var button = $('#start_search');
        var searchurl = button.data('url');
        button.find('i').removeClass('fa-search').addClass('fa-spinner fa-spin');
        button.off('click');
        $.ajax({
            type: "POST",
            url: searchurl,
            data: JSON.stringify(postfields),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data) {
                var table_container = $('#search_results');
                table_container.empty();

                // se i risultati sono troppi, mostro un alert
                var results_count = data.results_count;
                var results_limit = data.results_limit;
                if (results_count > results_limit) {
                    var alert_div = $('<div></div>').addClass('alert alert-warning').attr('role', 'alert');
                    alert_div.html(_('1000_results', 0) + results_count + _('1000_results', 1) + results_limit + _('1000_results', 2));
                    table_container.append(alert_div);
                }

                var table = $('<table></table>').addClass('table table-striped table-bordered table-hover');
                table_container.append(table);
                var detail_url = table_container.data('detail-url');
                var columns = [];
                $.each(data.columns, function(idx, title) {
                    if (title == 'id') {
                        columns.push({ sTitle: title, bVisible: false })
                    } else {
                        columns.push({ sTitle: title })
                    }
                });
                table.dataTable({
                    aaData: data.results,
                    aoColumns: columns,
                    fnRowCallback: function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
                        var id = aData[0];
                        var target = detail_url.replace('0', id);
                        $(nRow).find('td').off('mousedown contextmenu');
                        $(nRow).find('td').on('mousedown', function(e) {
                            // apro link in nuova finestra
                            window.open(target);
                        });
                    }
                });
                // cookie valido solo nel path corrente
                Cookies.set('django-search-last', JSON.stringify(postfields), { path: '' });
                if (typeof clipboard !== 'undefined') {
                    clipboard.destroy();
                }
                clipboard = new Clipboard('#last_search_copy', {
                    text: function(trigger) {
                        var url = [location.protocol, '//', location.host, location.pathname].join('');
                        return url + '?searchconfig=' + encodeURIComponent(JSON.stringify(postfields));
                    }
                });
                clipboard.on('success', function(e) {
                    $('#last_search_copy').tooltip('show');
                    setTimeout(function() {
                        $('#last_search_copy').tooltip('hide');
                    }, 3000);
                });
                $('#last_search_group').removeClass('hidden');

                // passo i dati di ricerca ricevuti ad eventuali listeners
                search_results_listeners.forEach(function(callback) {
                    callback(data);
                });
            },
            error: function(jqXHR, msg) {
                console.log(msg);
            },
            complete: function(jqXHR, msg) {
                button.find('i').removeClass('fa-spinner fa-spin').addClass('fa-search');
                button.on('click', doSearch);
            }
        });
    };
    var doExportXlsx = function() {
        doExport('#start_export_xlsx', doExportXlsx);
    };
    $('#start_search').click(doSearch);
    $('#start_export_xlsx').click(doExportXlsx);
    $('.search-action').click(function() {
        $('#form-search-action').attr('action', $(this).data('url'));
        // recupero html del form, gli passo anche i campi di ricerca
        // per permettergli di contare i risultati e mostrarli in un warning
        // sopra il form (in modo che uno sappia quanti record andra' ad aggiornare)
        var postfields = buildSearchData();
        $.ajax({
            type: "POST",
            url: $(this).data('url'),
            data: JSON.stringify({ postfields: postfields }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data) {
                createSearchActionForm('#modal-search-action', data.html);
                $('#modal-search-action').modal();
            },
            failure: function(jqXHR, msg) {
                console.log(msg);
            }
        });
    });
    $('#form-search-action').on('submit', function(e) {
        e.preventDefault();
        var icon = $(this).find('.btn-submit').find('i');
        if (icon.hasClass('fa-spin')) {
            return false;
        }
        icon.removeClass('fa-check').addClass('fa-spinner fa-spin');
        var postfields = buildSearchData();
        $.ajax({
            type: "POST",
            url: $(this).attr('action'),
            data: JSON.stringify({ postfields: postfields, formdata: $(this).serialize() }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data) {
                createSearchActionForm('#modal-search-action', data.html);
                icon.removeClass('fa-spinner fa-spin').addClass('fa-check');
            },
            failure: function(jqXHR, msg) {
                console.log(msg);
            }
        });
    });
    $('#searchfields').on('keydown', '.form-control', function(e) {
        var code = e.which;
        if (code == 13) {
            doSearch();
        }
    });
    var searchPreset = function(searchconfig) {
        $('#search_results').empty();
        searchDataToWidgets(searchconfig);
        doSearch($('#start_search'));
    };
    $('.search-preset').click(function() {
        searchPreset($(this).data('searchconfig'));
    });
    // leggo la querystring per pre-popolare i campi di ricerca
    var urlParam = function(name, url) {
        if (!url) {
         url = window.location.href;
        }
        var results = new RegExp('[\\?&]' + name + '=([^&#]*)').exec(url);
        if (!results) {
            return undefined;
        }
        return results[1] || undefined;
    };
    var searchconfig = urlParam('searchconfig');
    if (typeof searchconfig !== 'undefined' && searchconfig != '') {
        searchconfig = JSON.parse(decodeURIComponent(searchconfig));
        searchPreset(searchconfig);
    } else {
        add_search_field(false);
    }
    $('#last_search').click(function() {
        var searchconfig = Cookies.get('django-search-last');
        if (typeof searchconfig !== 'undefined' && searchconfig != '') {
            searchPreset(JSON.parse(searchconfig));
        }
    });
    $('#last_search_copy').tooltip({
        title: _('link_copied'),
        trigger: 'click',
        placement: 'top',
    });
    // se non ho dati da un'ultima ricerca al caricamento della pagina, nascondo il bottone
    var last_search_data = Cookies.get('django-search-last');
    if (typeof last_search_data === 'undefined' || last_search_data == '') {
        $('#last_search_group').addClass('hidden');
    }
    $('#modal-search-action').on('click', '#search-multiple-edit-results', function() {
        var timestamp = $(this).data('timestamp');
        var preset = [ { 'key': 'multiple_edit_timestamp', 'value': timestamp } ];
        $('#modal-search-action').modal('hide');
        searchPreset(preset);
    });
});
