<%inherit file="../layout/master.mako"/>
<%block name="top_script">
    <link href="${static_url('css/main.css')}" rel="stylesheet"/>
</%block>

<%block name="title">
    ${parent.title()}
</%block>
<%block name="bottom_script">
    <script src="${static_url('js/agl.main.js')}"></script>
    <script src="${static_url('js/agl.controller.js')}"></script>
    <script src="${static_url('js/agl.service.js')}"></script>
    <script src="${static_url('js/agl.directive.js')}"></script>
    <script type="text/javascript">
        var i = 0;
        function rotate(obj) {

            if (i >= 360) {
                i = 0;
            }
            obj.css("-moz-transform", "rotate(" + i + "deg)");
            obj.css("-o-transform", "rotate(" + i + "deg)");
            obj.css("-webkit-transform", "rotate(" + i + "deg)");
            obj.css("transform", "rotate(" + i + "deg)");
            i += 0.5;


        }
        $(function () {

            setInterval('rotate($("#reote"))', 1);

        })
    </script>
</%block>
<div class="banner-player">
    <div class="img-rounded bg-banner" style="background-image: url(${static_url('img/banner.png')})">
    </div>
    <div class="cdplayer">

        <div class="img-circle disc-default disc-size "></div>

        <div id="reote" class="img-circle disc disc-size "
             style="background-image: url(${static_url('img/disc-covr.jpg')})"></div>
        <div class="plyctrl plyctrl"></div>
        <div class="plyctrl-play plyctrl"></div>
    </div>

</div>

<div class="row marketing">

    <div class="col-lg-6">
        <h4>Subheading</h4>

        <p>Donec id elit non mi porta gravida at eget metus. Maecenas faucibus mollis interdum.</p>

        <h4>Subheading</h4>

        <p>Morbi leo risus, porta ac consectetur ac, vestibulum at eros. Cras mattis consectetur purus sit amet
            fermentum.</p>

        <h4>Subheading</h4>

        <p>Maecenas sed diam eget risus varius blandit sit amet non magna.</p>
    </div>

    <div class="col-lg-6">
        <h4>Subheading</h4>

        <p>Donec id elit non mi porta gravida at eget metus. Maecenas faucibus mollis interdum.</p>

        <h4>Subheading</h4>

        <p>Morbi leo risus, porta ac consectetur ac, vestibulum at eros. Cras mattis consectetur purus sit amet
            fermentum.</p>

        <h4>Subheading</h4>

        <p>Maecenas sed diam eget risus varius blandit sit amet non magna.</p>
    </div>
</div>




