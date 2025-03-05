

from odoo import models, fields, api

class City(models.Model):

    _name = "res.city"
    _description = "Cities"
    
    country_id = fields.Many2one(
        'res.country',
        string='Country',
        required=True,
        copy=True,
    )
    city_name= fields.Text(
        string='City',
        required = True,
        copy = True
    )