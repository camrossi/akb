var searchableIcons = [];
var searchableEntries = [];
var curProgress = 1;

function populateSearchEntries() {
    searchableEntries = [];
    var entries = $('#search-dictionary .searchable');
    for (var ii = 0; ii < entries.length; ii++) {
        var retObj = {};
        for (var yy = 0; yy < entries[ii].attributes.length; yy++) {
            var attrObj = entries[ii].attributes[yy];
            if (attrObj.name === "data-ref") { retObj.ref = attrObj.value };
            if (attrObj.name === "data-depth") { retObj.depth = attrObj.value };
            if (attrObj.name === "data-name") { retObj.name = attrObj.value };
            if (attrObj.name === "data-description") { retObj.description = attrObj.value };
            if (attrObj.name === "data-group") { retObj.group = attrObj.value };
        }
        var category = retObj.ref.substring(0, retObj.ref.indexOf('-'));
        retObj.ref = 'section-' + category + '.html#' + retObj.ref;
        searchableEntries.push(retObj);
    }
}
function populateSearchIcons() {
    searchableIcons = $('#icon-container .icon-panel');
    setIcons(searchableIcons);
}
function removeClassWildcard($element, removals) {
    if (removals.indexOf('*') === -1) {
        // Use native jQuery methods if there is no wildcard matching
        $element.removeClass(removals);
        return $element;
    }

    var patt = new RegExp('\\s' +
        removals.replace(/\*/g, '[A-Za-z0-9-_]+').split(' ').join('\\s|\\s') +
        '\\s', 'g');

    $element.each(function (i, it) {
        var cn = ' ' + it.className + ' ';
        while (patt.test(cn)) {
            cn = cn.replace(patt, ' ');
        }
        it.className = $.trim(cn);
    });

    return $element;
}
function addCards(cnt) {
    $('main #grid').empty();
    for (var ii = 1; ii <= cnt; ii++) {
        $('main #grid').append('<div class="card"><div class="card__body"><h3 class="text-uppercase base-margin-bottom">Card ' + ii + '</h3><div class="flex"><div class="form-group form-group--inline"><div class="form-group__text"><input id="grid-card-cols" type="number" value="1"><label>Columns</label></div></div><div class="form-group form-group--inline"><div class="form-group__text"><input id="grid-card-rows" type="number" value="1"><label>Rows</label></div></div></div></div>');
    }
    wireCards();
}
function wireCards() {
    $(document).on('click','main #grid .card',function () {
        if ($(this).parent().hasClass('grid--selectable')) {
            $(this).toggleClass('selected');
        }
    });
    $(document).on('change','main #grid-cards', function () {
        addCards($(this).val());
    });
    $(document).on('click','main #grid .card #grid-card-cols',function (e) {
        e.stopPropagation();
    });
    $(document).on('change','main #grid .card #grid-card-cols',function () {
        removeClassWildcard($(this).closest('.card'), 'card--col-*');
        $(this).closest('.card').addClass('card card--col-' + $(this).val());
    });
    $(document).on('click','main #grid .card #grid-card-rows',function (e) {
        e.stopPropagation();
    });
    $(document).on('change','main #grid .card #grid-card-rows',function () {
        removeClassWildcard($(this).closest('.card'), 'card--row-*');
        $(this).closest('.card').addClass('card card--row-' + $(this).val());
    });
}
function calcSearchWindowHeight() {
    var el = $('#search-results');
    if ($('#search-kit').offset().top){
        var maxHeight = ($(window).height() - $('#search-kit').offset().top - $('#search-kit').height() - 40);
        el.css('max-height', maxHeight + 'px');
    }
}

function shouldHideSidebar() {
    if (window.innerWidth < 768) {
        $('#styleguideSidebar').addClass('sidebar--hidden');
    } else {
        $('#styleguideSidebar').addClass('sidebar--mini');
        $('#styleguideSidebar').removeClass('sidebar--hidden');
    }
}
function startProgress() {
    setTimeout(function () {
        curProgress += Math.floor(Math.random() * 25);
        if (curProgress >= 100) {
            curProgress = 100;
        }
        $('main #progressbar').attr('data-percentage', curProgress);
        $('main #progressbar').attr('data-balloon', curProgress + '%');
        $('main #progressbar .progressbar__label').html(curProgress + '%');

        if (curProgress == 100) {
            $('main #progressbar .progressbar__label').html('Upload Complete');
            $('main #progressbar').attr('data-balloon', 'Upload Complete');
        } else {
            startProgress();
        }
    }, 1000);
}
function jumpTo(ref) {
    document.location.href = "section-" + ref + ".html#" + ref;
}
function doNav(url) {
    shouldHideSidebar();
    document.location.href = url;
}
function updateUrl(ref) {
    var path = window.location.pathname;
    var url = path + '#' + ref;
    history.pushState({ id: url }, 'Cisco UI Kit - ' + ref, url);
}
function checkUrlAndSetupPage(url) {
    if (url.lastIndexOf('#') != -1) {
        var anchor = url.substring(url.lastIndexOf('#') + 1);
        var str = _.split(anchor, '-')[1];
        var str = str.toLowerCase().replace(/\b[a-z]/g, function (letter) {
            return letter.toUpperCase();
        });

        // Remove any existing active classes
        $('#styleguideTabs > li.tab').removeClass('active');
        $('#styleguideTabs-content > .tab-pane').removeClass('active');

        // Add the active class to the appropriate elements
        $('#styleguideTabs #styleguideTabs-' + str).addClass('active');
        $('#styleguideTabs-content #styleguideTabs-' + str + '-content').addClass('active');

        setTimeout(function () {
            // Now scroll to the appropriate anchor (if specified in the url)
            var el = document.getElementById(anchor + '-tmp');
            if (el !== null) {
                el.scrollIntoView();
            }
        }, 100);
    }
    else if (url.indexOf('index.html') !== -1) {
        $('#rootSidebar #section-gettingStarted').addClass('selected');
    }
}
function doGlobalSearch(searchStr, forceFlag) {
    var results = [];
    searchStr = searchStr.toLowerCase();
    for (var ii = 0; ii < searchableEntries.length; ii++) {
        var entry = searchableEntries[ii];
        if (entry.depth === "3") {
            if ((entry.name.toLowerCase().indexOf(searchStr) !== -1) || (entry.ref.toLowerCase().indexOf(searchStr) !== -1) || forceFlag) {
                results.push(entry);
            }
        }
    }
    $('#search-results').empty();
    var str = '<a class="text-italic disabled"> Found ' + results.length + ' results</a>';
    _.forEach(_.groupBy(results, 'group'), function (value, key) {
        str += '<div class="dropdown__group"><div class="dropdown__group-header">' + key + '</div>';
        _.each(value, function (result) {
            str += '<a href="' + result.ref + '">' + result.name + '</a>';
        });
        str += '</div>';
    });
    $('#search-results').append(str);
    calcSearchWindowHeight();
}
function searchIcons(icon) {
    var ret = [];
    for (var ii = 0; ii < searchableIcons.length; ii++) {
        if (searchableIcons[ii].innerText.indexOf(icon) !== -1) {
            ret.push(searchableIcons[ii]);
        }
    }
    return ret;
}
function clearSearch() {
    setIcons(searchableIcons);
}
function setActiveSlide(slide, animation) {
    $(slide).siblings().removeClass('active');
    $(slide).parent().parent().find('.carousel__slide').removeClass('active slideInLeftSmall slideInRightSmall fadeIn');
    $(slide).addClass('active');
    $(slide).parent().parent().find('#' + slide.id + '-content').addClass('active ' + animation);
}
function setIcons(icons) {
    $('#icon-container').empty();
    $('#icon-container').append(icons);
    $('#icon-count').text(icons.length);
    $('#icon-total-count').text(icons.length);
}
function debounce(func, wait) {
    var timeout;
    var context = this, args = arguments;
    clearTimeout(timeout);
    timeout = setTimeout(function () {
        func.apply(context, args);
    }, wait || 0);
}
function openModal(id) {
    $('#modal-backdrop').removeClass('hide');
    $('#' + id).before('<div id="' + id + '-placeholder"></div>').detach().appendTo('body').removeClass('hide');
}
function closeModal(id) {
    $('#' + id).detach().prependTo(('#' + id + '-placeholder')).addClass('hide');
    $('#modal-backdrop').addClass('hide');
}

$(document).ready(function () {

    // Wire the icon search
    $('#icon-search-input').on('input', function () {
        var searchStr = $('#icon-search-input').val();
        if (searchStr !== '') {
            setIcons(searchIcons(searchStr));
        }
        else {
            clearSearch();
        }
    });

    // Wire the global search
    $(document).on('click','#search-kit',function () {
        if ($('#search-kit').val() === '') {
            doGlobalSearch('', true);
        }
        calcSearchWindowHeight();
    });
    $(document).on('input','#search-kit', function () {
        doGlobalSearch($('#search-kit').val(), false);
    });

    // Wire the header sidebar toggle button
    $(document).on('click','#sidebar-toggle',function () {
        $('#styleguideSidebar').toggleClass('sidebar--mini');
        $('#sidebar-toggle span:first-child').removeClass();
        if ($('#styleguideSidebar').hasClass('sidebar--mini')) {
            $('#sidebar-toggle span:first-child').addClass('icon-list-menu');
        } else {
            $('#sidebar-toggle span:first-child').addClass('icon-toggle-menu');
        }
    });

    $(document).on('click','#mobile-sidebar-toggle',function () {
        $('#styleguideSidebar').removeClass('sidebar--mini');
        $('#styleguideSidebar').toggleClass('sidebar--hidden');
    });

    // Wire the sidebar drawer open/close toggles
    $(document).on('click','#styleguideSidebar .sidebar__drawer > a',function (e) {
        e.stopPropagation();
        $(this).parent().siblings().removeClass('sidebar__drawer--opened');
        $(this).parent().toggleClass('sidebar__drawer--opened');
    });

    // Wire the sidebar selected item
    $(document).on('click','#styleguideSidebar .sidebar__item > a',function () {
        $('#styleguideSidebar .sidebar__item').removeClass('sidebar__item--selected');
        $(this).parent().addClass('sidebar__item--selected');
    });

    // Wire the sidebar examples
    $(document).on('click','main .sidebar__drawer > a',function () {
        $(this).parent().toggleClass('sidebar__drawer--opened');
    });
    $(document).on('click','main .sidebar__item > a',function () {
        $(this).parent().siblings().removeClass('sidebar__item--selected');
        $(this).parent().addClass('sidebar__item--selected');
    });

    // Wire the button group examples
    $(document).on('click','main .btn-group .btn',function () {
        $(this).siblings().removeClass('selected');
        $(this).addClass('selected');
    });

    // Wire the markup toggles
    $('main .markup').removeClass('active');
    $(document).on('click','main .markup-toggle',function () {
        $(this).parent().next().toggleClass('hide');
        $(this).parent().toggleClass('active');

        if ($(this).hasClass('active')) {
            $(this).find('.markup-label').text('Hide code');
        }
        else if (!$(this).hasClass('active')) {
            $(this).find('.markup-label').text('View code');
        }
    });

    // Wire the markup clipboard
    $(document).on('click','main .clipboard-toggle',function () {
        clipboard.copy($(this).parent().parent().find('code.code-raw').text());
        $(this).addClass('text-bold').text('Copied!');
    });

    // Wire the tabs
    $(document).on('click','.tabs-main li.tab',function () {
        var a  = this;
        var index = 0;
        $(this).closest('.tabs-main').find('li.tab').each(function(i,el){
            if (a.isEqualNode(el)){
                index = i;
            }           
        });
        $(this).closest('.tabs-main').find('li').removeClass('active');
        $(this).closest('.tabs-main').find('.tab-pane').removeClass('active')
        
        $($(this).closest('.tabs-main').find('li')[index]).addClass('active');
        $($(this).closest('.tabs-main').find('.tab-pane')[index]).addClass('active')
    
    });

    // Wire pagination
    $(document).on('click','main ul.pagination > li > a',function () {
        var el = $(this).parent().siblings().find('.active');
        $(this).parent().siblings().removeClass('active');
        $(this).parent().addClass('active');
    });

    // Wire closeable alerts
    $(document).on('click','main .alert .alert__close',function () {
        $(this).parent().addClass('hide');
    });

    // Wire the gauge example
    $('main #input-gauge-example').bind('keyup mouseup', function () {
        var val = $('#input-gauge-example').val() * 1;
        if (val >= 0 && val <= 100) {
            $('#gauge-example').attr('data-percentage', val);
            $('#gauge-example-value').text(val);
        }
    });

    // Wire the Card pattern examples
    $(document).on('click','main a.card',function () {
        $(this).toggleClass('selected');
    });

    // Wire the Advanced Grid example
    $(document).on('click','main #grid-group',function () {
        $(this).parent().find('#grid-group').removeClass('selected');
        var cls = 'grid--' + $(this).text();
        $('main .grid').removeClass('grid--3up');
        $('main .grid').removeClass('grid--4up');
        $('main .grid').removeClass('grid--5up');
        $('main .grid').addClass(cls);
        $(this).addClass('selected');
    });

    $(document).on('change','main #grid-cards',function () {
        addCards($(this).val());
    });

    $(document).on('change','main #grid-gutters',function () {
        $('main #grid').css('gridGap', $(this).val() + 'px');
    });

    $(document).on('change','main #grid-selectable',function () {
        $('main #grid').toggleClass('grid--selectable');
        $('main .grid .card').removeClass('selected');
    });

    addCards(15);

    // Wire the carousel examples
    $(document).on('click','main .carousel__controls a.dot',function () {
        setActiveSlide(this, 'fadeIn');
    });
    $(document).on('click','main .carousel__controls a.back',function () {
        var last = $(this).parent().find('a.dot').last();
        var cur = $(this).parent().find('a.dot.active');
        var active = cur.prev();
        if (active[0].id === "") {
            active = last;
        }
        setActiveSlide(active[0], 'slideInLeftSmall');
    });
    $(document).on('click','main .carousel__controls a.next',function () {
        var first = $(this).parent().find('a.dot').first();
        var cur = $(this).parent().find('a.dot.active');
        var active = cur.next();
        if (active[0].id === "") {
            active = first;
        }
        setActiveSlide(active[0], 'slideInRightSmall');
    });

    // Wire the progressbar example
    startProgress();

    // Wire the dropdown examples
    $(document).on('click','main .dropdown',function (e) {
        e.stopPropagation();
        var el = $(this).find('input');
        if (!el.hasClass('disabled') && !el.attr('disabled') && !el.hasClass('readonly') && !el.attr('readonly')) {
            $(this).toggleClass('active');
        }
    });
    $(document).on('click','main .dropdown .select ~.dropdown__menu a',function (e) {
        e.stopPropagation();

        // Check multi-select
        var cb = $(this).find('label.checkbox input');
        if (cb.length) {
            cb.prop('checked', !cb.prop('checked'));
            if (cb[0].id === 'global-animation') {
                $('body').toggleClass('cui--animated');
            }
            else if (cb[0].id === 'global-headermargins') {
                $('body').toggleClass('cui--headermargins');
            }
            else if (cb[0].id === 'global-spacing') {
                $('body').toggleClass('cui--compressed');
            }
            else if (cb[0].id === 'global-wide') {
                $('body').toggleClass('cui--wide');
            }
            else if (cb[0].id === 'global-sticky') {
                $('body').toggleClass('cui--sticky');
            }
        }
        else { // Single select
            e.stopPropagation();
            var origVal = $(this).parent().parent().find('input').val();
            var newVal = $(this).text();

            $(this).parent().find('a').removeClass('selected');
            $(this).addClass('selected');
            $(this).parent().parent().find('input').val($(this).text());
            $(this).parent().parent().removeClass('active');

            var obj = $(this).parent().parent().find('input');
            if (obj[0].id === 'select-change-version') {
                if (origVal !== newVal) {
                    $("#uikit-css").attr('href', $(this).attr('data-value'));
                }
            }
        }
    });
    // Close dropdowns and open sidebar drawers on clicks outside the dropdowns
    $(document).click(function () {
        $('main .dropdown').removeClass('active');
        $('#styleguideSidebar .sidebar__drawer').removeClass('sidebar__drawer--opened');
    });

    // Wire the masonry layout dropdowns
    $(document).on('change','main #masonry-columns-dropdown',function () {
        $('main #masonry-columns-example').removeClass();
        $('main #masonry-columns-example').addClass('masonry masonry--cols-' + this.value);
    });
    $(document).on('change','main #masonry-gaps-dropdown',function () {
        $('main #masonry-gaps-example').removeClass();
        $('main #masonry-gaps-example').addClass('masonry masonry--gap-' + this.value);
    });

    // Wire the selectable tables
    $('main .table.table--selectable tbody > tr').click(function () {
        $(this).toggleClass('active');
    });
    // Wire the table wells example
    $('main #table-wells tbody > tr').click(function () {
        $(this).find('td span.icon-chevron-up').removeClass('icon-chevron-up').addClass('icon-chevron-down');
        $(this).find('td span.icon-chevron-down').removeClass('icon-chevron-down').addClass('icon-chevron-up');
        $(this).next().toggleClass('hide');
    });

    // Wire the global modifiers
    $(document).on('change','main #global-animation',function () {
        $('body').toggleClass('cui--animated');
    });
    $(document).on('change','main #global-headermargins',function () {
        $('body').toggleClass('cui--headermargins');
    });
    $(document).on('change','main #global-spacing',function () {
        $('body').toggleClass('cui--compressed');
    });
    $(document).on('change','main #global-wide',function () {
        $('body').toggleClass('cui--wide');
    });
    $(document).on('change','main #global-sticky',function () {
        $('body').toggleClass('cui--sticky');
    });

    // Load the changelog
    $.get('changelog.md', function (markdownContent) {
        var converter = new Markdown.Converter();
        $("#changelog-content").html(converter.makeHtml(markdownContent));
    });

    // Load the broadcast file (if it exists)
    $.getJSON('broadcast.json', function (data) {
        if (data && data.text && data.text.length) {
            $("#broadcast-msg").html(data.text);
            $("#broadcast").toggleClass('hide');
        }
    });

    window.addEventListener('hashchange', function (event) {
        checkUrlAndSetupPage(event.newURL);
    }, false);

    /* Check for anchor link in the URL */
    checkUrlAndSetupPage(window.location.href);

    // Listen of window changes and close the sidebar if necessary
    $(window).resize(function () {
        shouldHideSidebar();
        // calcSearchWindowHeight();
    });

    shouldHideSidebar();
    populateSearchIcons();
    populateSearchEntries();
    // calcSearchWindowHeight();
});