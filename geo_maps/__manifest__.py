# -*- coding: utf-8 -*-
{
    'name': 'Geo Maps',
    'version': '11.0.1.0.5',
    'author': 'Toolkit',
    'license': 'AGPL-3',
    'maintainer': 'Toolkit<info@toolkt.com>',
    'support': 'info@toolkt.com',
    'category': 'Extra Tools',
    'description': """
Web Google Map and google places autocomplete address form
==========================================================

This module brings three features:
1. Allows user to view all partners addresses on google maps.
2. Enabled google places autocomplete address form into partner
form view, it provide autocomplete feature when typing address of partner
""",
    'depends': [
        'web_google_maps',
        'base_geolocalize',
    ],
    'website': '',
    'data': [
        'views/geo_map.xml',
    ],
    'demo': [],
    'images': ['static/description/thumbnails.png'],
    'qweb': [],
    'installable': True,
}
