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
            i += 0.3;


        }
        $(function () {

            setInterval('rotate($("#reote"))', 1);

        })
    </script>
</%block>
<div class="banner-player">
    <div class="img-rounded bg-banner" style="background-image: url(${static_url('img/lovely_fingers.jpg')})">
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
        <h1 class="quik-title">“是的ddvip是的疯狂哦哦的哦的偶读都哦都都都哦都都使肌肤 飞 的！”</h1>

        <p class="quik-cnt">
            <form action="/" method="post" enctype="multipart/form-data">
                ${xsrf_form_html()}
                <input type="text" name="username">
                <input type="file" name="file" id="file"/>
                <input type="submit" value="提交">
            </form>
        </p>

            <h1>“是的ddvip是的疯狂哦！”</h1>

        <p>如果你的手机已经使用了一年多，或许你已经不再会每天都去挖掘新的应用软件，没准，你好久都没有更新过手机里的那几十个应用了吧？

昨晚花两个小时更新了一下。</p>

        <h4>Subheading</h4>

        <p>Maecenas sed diam eget risus varius blandit sit amet non magna.</p>
    </div>

    <div class="col-lg-6">
      <h1>“是的ddvip是的疯狂哦！”</h1>

        <p>如果你的手机已经使用了一年多，或许你已经不再会每天都去挖掘新的应用软件，没准，你好久都没有更新过手机里的那几十个应用了吧？

昨晚花两个小时更新了一下。</p>
            <h1>“是的ddvip是的疯狂哦！”</h1>

        <p>如果你的手机已经使用了一年多，或许你已经不再会每天都去挖掘新的应用软件，没准，你好久都没有更新过手机里的那几十个应用了吧？

昨晚花两个小时更新了一下。</p>
    </div>
</div>




