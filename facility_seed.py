from secret import api_app_token
import pandas as pd
from sodapy import Socrata
from models import Site, db
from app import app


# Create all tables
db.drop_all()
db.create_all()

client = Socrata("data.cityofnewyork.us", api_app_token)
api_ext = "4kpn-sezh"


result = client.get(api_ext, limit=700)

for f in result:
    id = int(f.get("facility_pk"))
    name = f.get("facilityname")
    service_category = f.get("service_category")
    service_type = f.get("service_type")
    building_number = f.get("buildingnumber")
    partner_type = f.get("partnertype")
    partner_type_detailed = f.get("partner_type_detailed")
    address = f.get("address")
    address_2 = f.get("address_2")
    borough = f.get("borough")
    zip_code = f.get("zipcode")
    latitude = f.get("latitude")
    longitude = f.get("longitude")
    phone = f.get("phone")
    additional_info = f.get("additionalinfo")
    start_date = f.get("startdate")
    end_date = f.get("enddate")
    monday = f.get("monday")
    tuesday = f.get("tuesday")
    wednesday = f.get("wednesday")
    thursday = f.get("thursday")
    friday = f.get("friday")
    saturday = f.get("saturday")
    sunday = f.get("sunday")
    condoms_male = f.get("condoms_male")
    fc2_female_insertive_condoms = f.get("fc2_female_insertive_condoms")
    lubricant = f.get("lubricant")
    facility_type = f.get("facility_type")
    website = f.get("website")

    new_site = Site(id=id, name=name, service_category=service_category, service_type=service_type, building_number=building_number, partner_type=partner_type, partner_type_detailed=partner_type_detailed, address=address, address_2=address_2, borough=borough, zip_code=zip_code, latitude=latitude, longitude=longitude, phone=phone, additional_info=additional_info, start_date=start_date, end_date=end_date, monday=monday, tuesday=tuesday, wednesday=wednesday, thursday=thursday, friday=friday, saturday=saturday, sunday=sunday, condoms_male=condoms_male, fc2_female_insertive_condoms=fc2_female_insertive_condoms, lubricant=lubricant, facility_type=facility_type, website=website)

    db.session.add(new_site)

db.session.commit()