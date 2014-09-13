from django.http import HttpResponse
import trademe

def searchtest(request):

	response = ["""
	<!DOCTYPE HTML>
	<HTML>
	<HEAD>
	<TITLE></TITLE>
	</HEAD>
	<BODY>
	"""]
	
	if 'category' in request.GET:
	
		by_place = {}
		search_cat = request.GET['category']
		for job in trademe.get_all_jobs():
			if job['Category'][0:len(search_cat)] == search_cat:
				place = job['District']+', '+job['Region']
				if place not in by_place: by_place[place] = 0
				by_place[place] += 1
		
		best_places = sorted(by_place, key=lambda place: -by_place[place])
		
		for place in best_places:
			response[0] += "<B>%s</B> - %i<BR>" % (place, by_place[place])
		
	else:
		response[0] += """
		<FORM action="" method=GET>
		Category: <SELECT name=category>
		"""
		
		cats = trademe.get_job_categories()
		def output(c, depth, path):
			path = path + c['Code'] + '-'
			response[0] += '<OPTION value="%s">%s%s</OPTION>' % (path, '&gt;' * depth, c['Name'])
			for c in c['SubCategories']: output(c, depth+1, path)
		for c in cats: output(c, 0, '5000-')
		
		response[0] += """
		<INPUT type=submit>
		</SELECT>
		</FORM>
		"""
	
	response[0] += """
	</BODY>
	</HTML>
	"""
	return HttpResponse(response[0])