# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import logging

import requests

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


PIN_TYPES = [
        ('location',"Location"),
        ('chapter',"Chapter"),
        ('person',"Person")
    ]

STATUS = [
        ('active',"Active"),
        ('inactive',"Inactive"),
        ('dissolved',"Dissolved")
    ]

def geo_find(addr, apikey=False):
    if not addr:
        return None

    if not apikey:
        raise UserError(_('''API key for GeoCoding (Places) required.\n
                          Save this key in System Parameters with key: google.api_key_geocode, value: <your api key>
                          Visit https://developers.google.com/maps/documentation/geocoding/get-api-key for more information.
                          '''))

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    try:
        result = requests.get(url, params={'sensor': 'false', 'address': addr, 'key': apikey}).json()
    except Exception as e:
        raise UserError(_('Cannot contact geolocation servers. Please make sure that your Internet connection is up and running (%s).') % e)

    if result['status'] != 'OK':
        if result.get('error_message'):
            _logger.error(result['error_message'])
        return None

    try:
        geo = result['results'][0]['geometry']['location']
        return float(geo['lat']), float(geo['lng'])
    except (KeyError, ValueError):
        return None


def geo_query_address(street=None, zip=None, city=None, state=None, country=None):
    if country and ',' in country and (country.endswith(' of') or country.endswith(' of the')):
        # put country qualifier in front, otherwise GMap gives wrong results,
        # e.g. 'Congo, Democratic Republic of the' => 'Democratic Republic of the Congo'
        country = '{1} {0}'.format(*country.split(',', 1))
    return tools.ustr(', '.join(
        field for field in [street, ("%s %s" % (zip or '', city or '')).strip(), state, country]
        if field
    ))


class GeoMapEvent(models.Model):
    _name = 'geo.map.event'

    name = fields.Char("Event Name")
    event_address = fields.Char("Address")
    event_latitude = fields.Float("Event Latitude")
    event_longitude = fields.Float("Event Longitude")
    date_localization = fields.Date(string='Geolocation Date')
    pin_type = fields.Selection([('location',"Location"),('sortie',"Sortie")])

    @classmethod
    def _geo_localize(cls, apikey, street='', zip='', city='', state='', country=''):
        search = geo_query_address(street=street, zip=zip, city=city, state=state, country=country)
        result = geo_find(search, apikey)
        if result is None:
            search = geo_query_address(city=city, state=state, country=country)
            result = geo_find(search, apikey)
        return result

    @api.multi
    def geo_localize(self):
        # We need country names in English below
        apikey = self.env['ir.config_parameter'].sudo().get_param('google.api_key_geocode')
        for rec in self.with_context(lang='en_US'):
            result = rec._geo_localize(apikey,
                                           rec.event_address,
                                           '',# partner.zip,
                                           '',# partner.city,
                                           '',# partner.state_id.name,
                                           '',# partner.country_id.name
                                           )
            if result:
                rec.write({
                    'event_latitude': result[0],
                    'event_longitude': result[1],
                    'date_localization': fields.Date.context_today(rec)
                })
        return True



class GeoMapTag(models.Model):
    _name = 'geo.map.tag'

    name = fields.Char("Name")


class GeoMapLoc(models.Model):
    _name = 'geo.map.loc'

    name = fields.Char("Name")
    contact = fields.Char("Contact")
    phone = fields.Char("Phone")
    members = fields.Integer("Members")
    active = fields.Boolean("Active", default=True)
    tag_ids = fields.Many2many('geo.map.tag', 'geo_map_loc_tag_rel', 'loc_id', 'tag_id', "Tags")


    address = fields.Char("Address")
    latitude = fields.Float("Event Latitude")
    longitude = fields.Float("Event Longitude")
    date_localization = fields.Date(string='Geolocation Date')
    pin_type = fields.Selection(PIN_TYPES)
    status = fields.Selection(STATUS)

    @classmethod
    def _geo_localize(cls, apikey, street='', zip='', city='', state='', country=''):
        search = geo_query_address(street=street, zip=zip, city=city, state=state, country=country)
        result = geo_find(search, apikey)
        if result is None:
            search = geo_query_address(city=city, state=state, country=country)
            result = geo_find(search, apikey)
        return result

    @api.multi
    def geo_localize(self):
        # We need country names in English below
        apikey = self.env['ir.config_parameter'].sudo().get_param('google.api_key_geocode')
        for rec in self.with_context(lang='en_US'):
            result = rec._geo_localize(apikey,
                                           rec.address,
                                           '',# partner.zip,
                                           '',# partner.city,
                                           '',# partner.state_id.name,
                                           '',# partner.country_id.name
                                           )
            if result:
                rec.write({
                    'latitude': result[0],
                    'longitude': result[1],
                    'date_localization': fields.Date.context_today(rec)
                })
        return True