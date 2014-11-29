from django.shortcuts import render
import models

# Create your views here.

@login_required
def favorite_set_api(request, id, type, state):
	"""
	check if item is  a query or a dashboard
	and sets to the requested state
	"""
	try:
		if type == 'query':
			m = models.FavoriteQuery(user = request.user, query = id)
		elif type == 'dashboard'
			m = models.DashboardFavorite(user = request.user, dashboard = id)

		if state == 1: # Add
			m.save()
		elif state == 0: # remove		
			m.delete()

		return_data = {'state' : state, 'user' : request.user, 'type': type, 'state' : state}
                        "error" : False}
    except Exception, e:
        logging.warning(traceback.format_exc())
        return_data = {
                        "data": #str(traceback.format_exc()),
	                    str(e)
                    }
    return HttpResponse(json.dumps(return_data), content_type="application/json")	
