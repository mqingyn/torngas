<!DOCTYPE html>
<html lang="zh-cn" ng-app="faster-main">
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="">
    <meta name="author" content="">

    <title>
        <%block name="title">${site_settings.site_title}</%block>
    </title>
    <link href="${static_url('css/bootstrap.css')}" rel="stylesheet"/>
    <%block name="top_script"/>
</head>
<body cz-shortcut-listen="true">
<div class="container">
    <div class="header">

            <%include file='../include/topbar.mako'/>
    </div>

    ${next.body()}
    <footer class="footer">
        <p>&copy; ${site_settings.footer['desc']} ${site_settings.footer['year']}</p>
    </footer>

</div>

<script src="${static_url('js/jquery.min.js')}"></script>
<script src="${static_url('js/bootstrap.js')}"></script>
<script src="${static_url('js/angular-1.15.min.js')}"></script>
    <%block name="bottom_script"/>
</body>
</html>
