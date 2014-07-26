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
			<a href="/tasks"> Tasks </a>
		</li>
		<li class = "%s">
			<a href="/scoreboard"> Scoreboard </a>
		</li>
	</ul>
</div>
"""

title = """
<div class="container">
	<h1>{0}</h1>
</div>
"""

hint_top = """
<div class="well">
	<h3><b>Hints!</b></h3>
		<div class="collapse-group">
"""

snipp_hint = "<p> {0} </p>"

hints_disabled = "<p> <b>  Sorry</b>, but hints are not available yet! </p>"

hint_bottom = "</div>"

div_row_h = "<div class='row' style='float: center;'>"
div_row_e = "</div>"

task_row_h = """
<div style="height: 250px;" class="col-xs-4 col-md-4;" align="center">
  <h2>{0}</h2>
"""

task_div = """
		<div class="task">
			<p><a href= "task/{0}/{1}" class="btn {2}"> {1}. {3}</a></p>
		</div>
"""

task_row_f = """</div>\n"""

footer = """</body> </html>"""

home = """
<div class='well' align='center' >
	<h2>Hello! And welcome to the MSU CTF!</h2> <h3>Today's CTF sponsors are Kalan, neex, korsse, Destro, iad42 and PaulCher</h3><br><br>
	<h2> The Legend! </h2>
	<h4> Unsolved tasks are marked with <button class='btn btn-primary'> Blue buttons </button> </h4>
	<h4> Tasks solved by your team are marked with <button class='btn btn-success'> Green buttons </button> </h4>
	<h4> Tasks solved by other teams are marked with <button class='btn btn-warning'> Yellow buttons </button> </h4>
	<h2> Good luck and have fun! </h2>
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
	        			  <td>{0}</td>
					  <td>{1}</td>
					  <td>{2}</td>
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

faceless_task = """
<div class='well'>
    <h3> {1} </h3>
    {2}
</div>
"""

snip_login_page = """
<div class='well'>
	<center>
		<form method=POST>
			<input type='text' name='token' class='form-control' >
		</form>
	</center>
</div>
"""

snip_login_page = """
<div class='well'>
	<center>
		<form method=POST>
			<input type='text' name='token' class='form-control' >
		</form>
	</center>
</div>
"""

admin_commit_table_head = """
<table class='table table-bordered' width='80%' >
				  <thead>
					<tr>
					  <th>Team Name</th>
					  <th>Flag</th>
					  <th>Task</th>
					  <th>Time</th>
					  <th>IP</th>
					</tr>
				  </thead>


"""

admin_commit_table_cell = """
<tr class="{0}">
	<td> {1} </td>
	<td> {2} </td>
	<td> {3} </td>
	<td> {4} {5} </td>
	<td> {6} </td>
</tr>
"""
admin_commit_table_footer = """ </table> """
flag_added = """<div class="alert alert-success"><b> Well done! </b> Your flag has been added! </div>"""
flag_declined = """<div class="alert alert-danger"><b> Oh snap! </b> Wrong flag! Try again later!  </div>"""
flag_already_been_added = """<div class="alert alert-warning"><b> Warning! </b> The flag has already been added! The incident will be reported!  </div>"""

admin_commit_table_cell = """
<tr class="{0}">
	<td> {1} </td>
	<td> {2} </td>
	<td> {3} </td>
	<td> {4} {5} </td>
	<td> {6} </td>
</tr>
"""
admin_commit_table_footer = """ </table> """
flag_added = """<div class="alert alert-success"><b> Well done! </b> Your flag has been added! </div>"""
flag_declined = """<div class="alert alert-danger"><b> Oh snap! </b> Wrong flag! Try again later!  </div>"""
flag_already_been_added = """<div class="alert alert-warning"><b> Warning! </b> The flag has already been added! The incident will be reported!  </div>"""

admin_menu = """<div class='jumbotron container' style='padding-top:200px; border-bottom: solid 1px black;border-right: solid 1px black;border-left: solid 1px black;'>
<center>
	<ul class="nav nav-pills">
		<li class = "active">
			<a href="/admin/commits"> Commits </a>
		</li>
		<li class = "active">
			<a href="/admin/checksum"> Checksum </a>
		</li>
		<li class = "active">
			<a href="/admin/logout"> Log Out </a>
		</li>
	</ul>
</center>
</div>"""
