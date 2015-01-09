<html>
    <head>
    <meta charset="UTF-8">
    <link rel="stylesheet" type="text/css" href="/usr/local/openerp/community/omniship/report/label.css"></link>
    </head>
    <body style="width: 298px; margin-left: auto; margin-right: auto; height: 460px;">
        %for label in objects:
	    <img style="height:460px; width: 298px;" src="data:image/gif;base64,${label.file}"></img>
	%endfor
    </body>
</html>
