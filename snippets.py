head = """<!DOCTYPE html>
<html>
<head>
	<title> CTF@MSU </title>
	<link rel="stylesheet" href="//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css">
	<link rel="stylesheet" href="//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap-theme.min.css">
        <link rel="icon" href="data:;base64,=">
	<script src="//netdna.bootstrapcdn.com/bootstrap/3.1.1/js/bootstrap.min.js"></script>

</head>
<body>
"""

menu = """
<div style="padding-top: 100px;" class="container">
	<ul class="nav nav-pills">
		<li class = "%s">
			<a href="/"> Home </a>
		</li>
		<li class = "%s">
			<a href="tasks"> Tasks </a>
		</li>
		<li class = "%s">
			<a href="scoreboard"> Scoreboard </a>
		</li>
	</ul>
</div>
"""

title = """
<div class="container">
	<h1>%s</h1>
</div>
"""

hint_top = """
<div class="well">
	<h3><b>Hints!</b></h3>
		<div class="collapse-group">
	</div>
"""

snipp_hint = "<p> %s </p>"

hints_disabled = "<p> <b>  Sorry</b>, but hints are not available yet! </p>"

hint_bottom = "</div>"

div_row_h = "<div class='row' style='float: center;'>"
div_row_e = "</div>"

task_row_h = """
	<div style="height: 250px;" class="col-xs-4 col-md-4" align="center">
	  <h2>%s</h2>
"""

task_div = """
<div class="task">
	<p><a href= "/?t={0}&c={1}" class="btn {2}"> {0}. {3}</a></p>
</div>
"""

task_row_f = """ </div>"""

footer = """</body> </html>"""

home = """
<div class='well' align='center' >
	<h2>Hello! And welcome to the MSU CTF!</h2> <h3>Today's CTF sponsors are Kalan, Destro, iad42 and PaulCher</h3><br>
	<h4> May be there will be some more info in future, but not today!
</div>
"""
scoreboard_head = """
<div style="padding: 40px">
	<table class="table table-striped table-bordered" >
				  <thead>
					<tr>
					  <th>#</th>
					  <th>Team Name</th>
					  <th>Pts</th>
					</tr>
				  </thead>
				  <tbody>
"""

scoreboard_cell = """
					<tr>
	        			  <td>%s</td>
					  <td>%s</td>
					  <td>%s</td>
					</tr>
"""
scoreboard_footer = """
					</tbody>
				</table>
</div>
"""


submit_bar = """
<div class="navbar navbar-inverse navbar-fixed-top" role="navigation">
      <div class="container">
        <div class="navbar-header">
          <span class="navbar-brand" > Submit Bar </span>
        </div>
        <div class="navbar-collapse collapse">
          <form class="navbar-form navbar-right" method='POST'>

            <div class="form-group">
              <input type="text" placeholder="Team Name" class="form-control" name='team_name'>
            </div>

            <div class="form-group">
              <input type="text" placeholder="Flag" class="form-control" name='flag'>
            </div>

            <button type="submit" class="btn btn-success">Submit</button>

          </form>
        </div>
      </div>
    </div>
"""

task_description = """
<div class="well">
	<h3> {1} </h3>
	{2}
	<a target="_blank" href= "http://{3}:{4}/{5}/{0}"  class="link"> {0} </a>
</div>
"""

flag_added = """<div class="alert alert-success"><b> Well done! </b> Your flag has been added! </div>"""

flag_declined = """<div class="alert alert-danger"><b> Oh snap! </b> Wrong flag! Try again later!  </div>"""

flag_already_been_added = """<div class="alert alert-warning"><b> Warning! </b> The flag has already been added! The incedent will be reported!  </div>"""
