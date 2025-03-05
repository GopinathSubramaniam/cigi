import json

from odoo import http
from odoo.http import request


class CityController(http.Controller):

    @http.route('/city/bycountry/<int:country_id>', type="http", auth="public", website=True)
    def volunteer_form(self, country_id, **kwargs):
        cities = request.env["res.city"].sudo().search([('country_id', '=', country_id)])
        city_list = [{'id': c.id, 'country_id': c.country_id.id, 'city_name': c.city_name} for c in cities]
        return request.make_response(json.dumps(city_list), headers=[('Content-Type', 'application/json')])