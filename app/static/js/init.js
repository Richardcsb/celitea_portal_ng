function flask_moment_render(elem) {
    $(elem).text(eval('moment("' + $(elem).data('timestamp') + '").' + $(elem).data('format') + ';'));
    $(elem).removeClass('flask-moment').show();
}
function flask_moment_render_all() {
    $('.flask-moment').each(function() {
        flask_moment_render(this);
        if ($(this).data('refresh')) {
            (function(elem, interval) { setInterval(function() { flask_moment_render(elem) }, interval); })(this, $(this).data('refresh'));
        }
    })
}
$(document).ready(function() {
    moment.locale("zh-cn");
    flask_moment_render_all();
    //Initial Materialize Scripts.
    $('select').material_select();
    $('.collapsible').collapsible({
      accordion : false // A setting that changes the collapsible behavior to expandable instead of the default accordion style
    });
    $(".button-collapse").sideNav();
    $('.modal-trigger').leanModal();
    $('ul.tabs').tabs({
        swipeable: true
    });
});


document.addEventListener("DOMContentLoaded", function() {
    $.getJSON( "https://raw.githubusercontent.com/Tust-Celitea/quotes/master/dist/quotes.json", function(data) {
        fortunes = data;
        randomFortune = fortunes[ Math.floor( Math.random() * fortunes.length ) ];
        if ( randomFortune.author === undefined ) {
            $("#quotes").html( "<span>"+randomFortune.content+"</span>" );
        } else {
            $("#quotes").html( "<span>"+randomFortune.content + "<br><small> --" + randomFortune.author + "</small></span>");
        }
        $("#quotes").velocity("slideDown", { duration: 400, easing: "easeOutQuad" });
    });
});