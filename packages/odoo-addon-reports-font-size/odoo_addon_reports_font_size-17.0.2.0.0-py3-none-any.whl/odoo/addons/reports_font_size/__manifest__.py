# Copyright 2024 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Reports Font Size",
    "summary": "Change reports font size from the document layout configurator",
    "version": "17.0.2.0.0",
    "category": "repoting-engine",
    "website": "https://github.com/sygel-technology/sy-server-backend",
    "author": "Sygel, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "web",
    ],
    "data": {
        "templates/report_style_templates.xml",
        "views/base_document_layout.xml",
        "data/report_layout.xml",
    },
}
