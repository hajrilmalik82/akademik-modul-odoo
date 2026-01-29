from odoo import fields, models

class HostelAmenities(models.Model):
    _name = "hostel.amenities"
    _description = "Hostel Ameneties"
    
    name = fields.Char("Name", help="Provide Hostel Amenity")
    active = fields.Boolean("Active",
            help="Activate/Deactivate whether the amenity should be given or not")