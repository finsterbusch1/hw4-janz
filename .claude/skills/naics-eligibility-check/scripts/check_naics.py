#!/usr/bin/env python3
"""
check_naics.py — NAICS Eligibility Checker for Government Contract Bids

Source: U.S. SBA Table of Small Business Size Standards
        Effective March 17, 2023

Usage:
    python check_naics.py <NAICS_CODE> [--revenue <MILLIONS>] [--employees <COUNT>] [--setaside <TYPE>]

Examples:
    python check_naics.py 622110 --revenue 36
    python check_naics.py 339112 --employees 160
    python check_naics.py 622110 --revenue 36 --setaside SDVOSB
"""

import argparse
import json

# ---------------------------------------------------------------------------
# COMPLETE NAICS Size Standards table from SBA, effective March 17, 2023
# Format: "NAICS": ("Description", "type", value)
#   type: "revenue_millions" or "employees"
# ---------------------------------------------------------------------------
NAICS_DATA = {

    # Sector 11 – Agriculture, Forestry, Fishing and Hunting
    "111110": ("Soybean Farming", "revenue_millions", 2.25),
    "111120": ("Oilseed (except Soybean) Farming", "revenue_millions", 2.25),
    "111130": ("Dry Pea and Bean Farming", "revenue_millions", 2.75),
    "111140": ("Wheat Farming", "revenue_millions", 2.25),
    "111150": ("Corn Farming", "revenue_millions", 2.5),
    "111160": ("Rice Farming", "revenue_millions", 2.5),
    "111191": ("Oilseed and Grain Combination Farming", "revenue_millions", 2.25),
    "111199": ("All Other Grain Farming", "revenue_millions", 2.25),
    "111211": ("Potato Farming", "revenue_millions", 4.25),
    "111219": ("Other Vegetable and Melon Farming", "revenue_millions", 3.75),
    "111310": ("Orange Groves", "revenue_millions", 4.0),
    "111320": ("Citrus (except Orange) Groves", "revenue_millions", 4.25),
    "111331": ("Apple Orchards", "revenue_millions", 4.5),
    "111332": ("Grape Vineyards", "revenue_millions", 4.0),
    "111333": ("Strawberry Farming", "revenue_millions", 5.5),
    "111334": ("Berry (except Strawberry) Farming", "revenue_millions", 3.75),
    "111335": ("Tree Nut Farming", "revenue_millions", 3.75),
    "111336": ("Fruit and Tree Nut Combination Farming", "revenue_millions", 5.0),
    "111339": ("Other Noncitrus Fruit Farming", "revenue_millions", 3.5),
    "111411": ("Mushroom Production", "revenue_millions", 4.5),
    "111419": ("Other Food Crops Grown Under Cover", "revenue_millions", 4.5),
    "111421": ("Nursery and Tree Production", "revenue_millions", 3.25),
    "111422": ("Floriculture Production", "revenue_millions", 3.75),
    "111910": ("Tobacco Farming", "revenue_millions", 2.5),
    "111920": ("Cotton Farming", "revenue_millions", 3.25),
    "111930": ("Sugarcane Farming", "revenue_millions", 5.0),
    "111940": ("Hay Farming", "revenue_millions", 2.5),
    "111991": ("Sugar Beet Farming", "revenue_millions", 2.5),
    "111992": ("Peanut Farming", "revenue_millions", 2.5),
    "111998": ("All Other Miscellaneous Crop Farming", "revenue_millions", 2.5),
    "112111": ("Beef Cattle Ranching and Farming", "revenue_millions", 2.5),
    "112112": ("Cattle Feedlots", "revenue_millions", 22.0),
    "112120": ("Dairy Cattle and Milk Production", "revenue_millions", 3.75),
    "112210": ("Hog and Pig Farming", "revenue_millions", 4.0),
    "112310": ("Chicken Egg Production", "revenue_millions", 19.0),
    "112320": ("Broilers and Other Meat Type Chicken Production", "revenue_millions", 3.5),
    "112330": ("Turkey Production", "revenue_millions", 3.75),
    "112340": ("Poultry Hatcheries", "revenue_millions", 4.0),
    "112390": ("Other Poultry Production", "revenue_millions", 3.75),
    "112410": ("Sheep Farming", "revenue_millions", 3.5),
    "112420": ("Goat Farming", "revenue_millions", 2.5),
    "112511": ("Finfish Farming and Fish Hatcheries", "revenue_millions", 3.75),
    "112512": ("Shellfish Farming", "revenue_millions", 3.75),
    "112519": ("Other Aquaculture", "revenue_millions", 3.75),
    "112910": ("Apiculture", "revenue_millions", 3.25),
    "112920": ("Horses and Other Equine Production", "revenue_millions", 2.75),
    "112930": ("Fur Bearing Animal and Rabbit Production", "revenue_millions", 3.75),
    "112990": ("All Other Animal Production", "revenue_millions", 2.75),
    "113110": ("Timber Tract Operations", "revenue_millions", 19.0),
    "113210": ("Forest Nurseries and Gathering of Forest Products", "revenue_millions", 20.5),
    "113310": ("Logging", "employees", 500),
    "114111": ("Finfish Fishing", "revenue_millions", 25.0),
    "114112": ("Shellfish Fishing", "revenue_millions", 14.0),
    "114119": ("Other Marine Fishing", "revenue_millions", 11.5),
    "114210": ("Hunting and Trapping", "revenue_millions", 8.5),
    "115111": ("Cotton Ginning", "revenue_millions", 16.0),
    "115112": ("Soil Preparation, Planting, and Cultivating", "revenue_millions", 9.5),
    "115113": ("Crop Harvesting, Primarily by Machine", "revenue_millions", 13.5),
    "115114": ("Postharvest Crop Activities (except Cotton Ginning)", "revenue_millions", 34.0),
    "115115": ("Farm Labor Contractors and Crew Leaders", "revenue_millions", 19.0),
    "115116": ("Farm Management Services", "revenue_millions", 15.5),
    "115210": ("Support Activities for Animal Production", "revenue_millions", 11.0),
    "115310": ("Support Activities for Forestry", "revenue_millions", 11.5),

    # Sector 21 – Mining
    "211120": ("Crude Petroleum Extraction", "employees", 1250),
    "211130": ("Natural Gas Extraction", "employees", 1250),
    "212114": ("Surface Coal Mining", "employees", 1250),
    "212115": ("Underground Coal Mining", "employees", 1500),
    "212210": ("Iron Ore Mining", "employees", 1400),
    "212220": ("Gold Ore and Silver Ore Mining", "employees", 1500),
    "212230": ("Copper, Nickel, Lead, and Zinc Mining", "employees", 1400),
    "212290": ("Other Metal Ore Mining", "employees", 1250),
    "212311": ("Dimension Stone Mining and Quarrying", "employees", 500),
    "212312": ("Crushed and Broken Limestone Mining and Quarrying", "employees", 750),
    "212313": ("Crushed and Broken Granite Mining and Quarrying", "employees", 850),
    "212321": ("Construction Sand and Gravel Mining", "employees", 500),
    "212322": ("Industrial Sand Mining", "employees", 750),
    "213111": ("Drilling Oil and Gas Wells", "employees", 1000),
    "213112": ("Support Activities for Oil and Gas Operations", "revenue_millions", 47.0),
    "213113": ("Support Activities for Coal Mining", "revenue_millions", 27.5),
    "213114": ("Support Activities for Metal Mining", "revenue_millions", 41.0),
    "213115": ("Support Activities for Nonmetallic Minerals Mining", "revenue_millions", 20.5),

    # Sector 22 – Utilities
    "221111": ("Hydroelectric Power Generation", "employees", 750),
    "221112": ("Fossil Fuel Electric Power Generation", "employees", 950),
    "221113": ("Nuclear Electric Power Generation", "employees", 1150),
    "221114": ("Solar Electric Power Generation", "employees", 500),
    "221115": ("Wind Electric Power Generation", "employees", 1150),
    "221116": ("Geothermal Electric Power Generation", "employees", 250),
    "221117": ("Biomass Electric Power Generation", "employees", 550),
    "221118": ("Other Electric Power Generation", "employees", 650),
    "221121": ("Electric Bulk Power Transmission and Control", "employees", 950),
    "221122": ("Electric Power Distribution", "employees", 1100),
    "221210": ("Natural Gas Distribution", "employees", 1150),
    "221310": ("Water Supply and Irrigation Systems", "revenue_millions", 41.0),
    "221320": ("Sewage Treatment Facilities", "revenue_millions", 35.0),
    "221330": ("Steam and Air Conditioning Supply", "revenue_millions", 30.0),

    # Sector 23 – Construction
    "236115": ("New Single-family Housing Construction", "revenue_millions", 45.0),
    "236116": ("New Multifamily Housing Construction", "revenue_millions", 45.0),
    "236117": ("New Housing For-Sale Builders", "revenue_millions", 45.0),
    "236118": ("Residential Remodelers", "revenue_millions", 45.0),
    "236210": ("Industrial Building Construction", "revenue_millions", 45.0),
    "236220": ("Commercial and Institutional Building Construction", "revenue_millions", 45.0),
    "237110": ("Water and Sewer Line Construction", "revenue_millions", 45.0),
    "237120": ("Oil and Gas Pipeline Construction", "revenue_millions", 45.0),
    "237130": ("Power and Communication Line Construction", "revenue_millions", 45.0),
    "237210": ("Land Subdivision", "revenue_millions", 34.0),
    "237310": ("Highway, Street, and Bridge Construction", "revenue_millions", 45.0),
    "237990": ("Other Heavy and Civil Engineering Construction", "revenue_millions", 45.0),
    "238110": ("Poured Concrete Foundation Contractors", "revenue_millions", 19.0),
    "238120": ("Structural Steel and Precast Concrete Contractors", "revenue_millions", 19.0),
    "238130": ("Framing Contractors", "revenue_millions", 19.0),
    "238140": ("Masonry Contractors", "revenue_millions", 19.0),
    "238150": ("Glass and Glazing Contractors", "revenue_millions", 19.0),
    "238160": ("Roofing Contractors", "revenue_millions", 19.0),
    "238170": ("Siding Contractors", "revenue_millions", 19.0),
    "238190": ("Other Foundation, Structure, and Building Exterior Contractors", "revenue_millions", 19.0),
    "238210": ("Electrical Contractors", "revenue_millions", 19.0),
    "238220": ("Plumbing, Heating, and Air Conditioning Contractors", "revenue_millions", 19.0),
    "238290": ("Other Building Equipment Contractors", "revenue_millions", 22.0),
    "238310": ("Drywall and Insulation Contractors", "revenue_millions", 19.0),
    "238320": ("Painting and Wall Covering Contractors", "revenue_millions", 19.0),
    "238330": ("Flooring Contractors", "revenue_millions", 19.0),
    "238340": ("Tile and Terrazzo Contractors", "revenue_millions", 19.0),
    "238350": ("Finish Carpentry Contractors", "revenue_millions", 19.0),
    "238390": ("Other Building Finishing Contractors", "revenue_millions", 19.0),
    "238910": ("Site Preparation Contractors", "revenue_millions", 19.0),
    "238990": ("All Other Specialty Trade Contractors", "revenue_millions", 19.0),

    # Sector 31-33 – Manufacturing (selected)
    "325411": ("Medicinal and Botanical Manufacturing", "employees", 1000),
    "325412": ("Pharmaceutical Preparation Manufacturing", "employees", 1300),
    "325413": ("In Vitro Diagnostic Substance Manufacturing", "employees", 1250),
    "325414": ("Biological Product Manufacturing", "employees", 1250),
    "334510": ("Electromedical and Electrotherapeutic Apparatus Manufacturing", "employees", 1250),
    "334511": ("Search, Detection, Navigation, Guidance, Aeronautical, and Nautical System Manufacturing", "employees", 1350),
    "334516": ("Analytical Laboratory Instrument Manufacturing", "employees", 1000),
    "334517": ("Irradiation Apparatus Manufacturing", "employees", 1200),
    "336411": ("Aircraft Manufacturing", "employees", 1500),
    "336412": ("Aircraft Engine and Engine Parts Manufacturing", "employees", 1500),
    "336413": ("Other Aircraft Part and Auxiliary Equipment Manufacturing", "employees", 1250),
    "336414": ("Guided Missile and Space Vehicle Manufacturing", "employees", 1300),
    "339112": ("Surgical and Medical Instrument Manufacturing", "employees", 1000),
    "339113": ("Surgical Appliance and Supplies Manufacturing", "employees", 800),
    "339114": ("Dental Equipment and Supplies Manufacturing", "employees", 750),
    "339115": ("Ophthalmic Goods Manufacturing", "employees", 1000),
    "339116": ("Dental Laboratories", "employees", 500),

    # Sector 42 – Wholesale Trade
    "423110": ("Automobile and Other Motor Vehicle Merchant Wholesalers", "employees", 250),
    "423120": ("Motor Vehicle Supplies and New Parts Merchant Wholesalers", "employees", 200),
    "423130": ("Tire and Tube Merchant Wholesalers", "employees", 200),
    "423140": ("Motor Vehicle Parts (Used) Merchant Wholesalers", "employees", 125),
    "423210": ("Furniture Merchant Wholesalers", "employees", 100),
    "423220": ("Home Furnishing Merchant Wholesalers", "employees", 100),
    "423310": ("Lumber, Plywood, Millwork, and Wood Panel Merchant Wholesalers", "employees", 150),
    "423390": ("Other Construction Material Merchant Wholesalers", "employees", 100),
    "423430": ("Computer and Computer Peripheral Equipment and Software Merchant Wholesalers", "employees", 250),
    "423450": ("Medical, Dental, and Hospital Equipment and Supplies Merchant Wholesalers", "employees", 200),
    "423460": ("Ophthalmic Goods Merchant Wholesalers", "employees", 175),
    "423490": ("Other Professional Equipment and Supplies Merchant Wholesalers", "employees", 150),
    "423690": ("Other Electronic Parts and Equipment Merchant Wholesalers", "employees", 250),
    "423810": ("Construction and Mining Machinery and Equipment Merchant Wholesalers", "employees", 250),
    "423990": ("Other Miscellaneous Durable Goods Merchant Wholesalers", "employees", 100),
    "424110": ("Printing and Writing Paper Merchant Wholesalers", "employees", 225),
    "424210": ("Drugs and Druggists' Sundries Merchant Wholesalers", "employees", 250),
    "424410": ("General Line Grocery Merchant Wholesalers", "employees", 250),
    "424490": ("Other Grocery and Related Products Merchant Wholesalers", "employees", 250),
    "424720": ("Petroleum and Petroleum Products Merchant Wholesalers", "employees", 200),
    "425120": ("Wholesale Trade Agents and Brokers", "employees", 125),

    # Sector 44-45 – Retail Trade
    "441110": ("New Car Dealers", "employees", 200),
    "441120": ("Used Car Dealers", "revenue_millions", 30.5),
    "441210": ("Recreational Vehicle Dealers", "revenue_millions", 40.0),
    "444110": ("Home Centers", "revenue_millions", 47.0),
    "444120": ("Paint and Wallpaper Retailers", "revenue_millions", 34.0),
    "444140": ("Hardware Retailers", "revenue_millions", 16.5),
    "445110": ("Supermarkets and Other Grocery Retailers", "revenue_millions", 40.0),
    "456110": ("Pharmacies and Drug Retailers", "revenue_millions", 37.5),

    # Sector 48-49 – Transportation and Warehousing
    "481111": ("Scheduled Passenger Air Transportation", "employees", 1500),
    "481112": ("Scheduled Freight Air Transportation", "employees", 1500),
    "481219": ("Other Nonscheduled Air Transportation", "revenue_millions", 25.0),
    "482111": ("Line Haul Railroads", "employees", 1500),
    "483111": ("Deep Sea Freight Transportation", "employees", 1050),
    "483113": ("Coastal and Great Lakes Freight Transportation", "employees", 800),
    "484110": ("General Freight Trucking, Local", "revenue_millions", 34.0),
    "484121": ("General Freight Trucking, Long Distance, Truckload", "revenue_millions", 34.0),
    "484122": ("General Freight Trucking, Long Distance, Less Than Truckload", "revenue_millions", 43.0),
    "484210": ("Used Household and Office Goods Moving", "revenue_millions", 34.0),
    "484220": ("Specialized Freight Trucking, Local", "revenue_millions", 34.0),
    "484230": ("Specialized Freight Trucking, Long Distance", "revenue_millions", 34.0),
    "485111": ("Mixed Mode Transit Systems", "revenue_millions", 29.0),
    "485112": ("Commuter Rail Systems", "revenue_millions", 47.0),
    "485113": ("Bus and Other Motor Vehicle Transit Systems", "revenue_millions", 32.5),
    "485310": ("Taxi and Ridesharing Services", "revenue_millions", 19.0),
    "485320": ("Limousine Service", "revenue_millions", 19.0),
    "485410": ("School and Employee Bus Transportation", "revenue_millions", 30.0),
    "485510": ("Charter Bus Industry", "revenue_millions", 19.0),
    "485999": ("All Other Transit and Ground Passenger Transportation", "revenue_millions", 19.0),
    "488111": ("Air Traffic Control", "revenue_millions", 40.0),
    "488119": ("Other Airport Operations", "revenue_millions", 40.0),
    "488190": ("Other Support Activities for Air Transportation", "revenue_millions", 40.0),
    "488210": ("Support Activities for Rail Transportation", "revenue_millions", 34.0),
    "488310": ("Port and Harbor Operations", "revenue_millions", 47.0),
    "488320": ("Marine Cargo Handling", "revenue_millions", 47.0),
    "488330": ("Navigational Services to Shipping", "revenue_millions", 47.0),
    "488390": ("Other Support Activities for Water Transportation", "revenue_millions", 47.0),
    "488410": ("Motor Vehicle Towing", "revenue_millions", 9.0),
    "488490": ("Other Support Activities for Road Transportation", "revenue_millions", 18.0),
    "488510": ("Freight Transportation Arrangement", "revenue_millions", 20.0),
    "488991": ("Packing and Crating", "revenue_millions", 34.0),
    "488999": ("All Other Support Activities for Transportation", "revenue_millions", 25.0),
    "491110": ("Postal Service", "revenue_millions", 9.0),
    "492110": ("Couriers and Express Delivery Services", "employees", 1500),
    "492210": ("Local Messengers and Local Delivery", "revenue_millions", 34.0),
    "493110": ("General Warehousing and Storage", "revenue_millions", 34.0),
    "493120": ("Refrigerated Warehousing and Storage", "revenue_millions", 36.5),
    "493130": ("Farm Product Warehousing and Storage", "revenue_millions", 34.0),
    "493190": ("Other Warehousing and Storage", "revenue_millions", 36.5),

    # Sector 51 – Information
    "512110": ("Motion Picture and Video Production", "revenue_millions", 40.0),
    "512131": ("Motion Picture Theaters (except Drive Ins)", "revenue_millions", 47.0),
    "513110": ("Newspaper Publishers", "employees", 1000),
    "513120": ("Periodical Publishers", "employees", 1000),
    "513130": ("Book Publishers", "employees", 1000),
    "513210": ("Software Publishers", "revenue_millions", 47.0),
    "516110": ("Radio Broadcasting Stations", "revenue_millions", 47.0),
    "516120": ("Television Broadcasting Stations", "revenue_millions", 47.0),
    "517111": ("Wired Telecommunications Carriers", "employees", 1500),
    "517112": ("Wireless Telecommunications Carriers", "employees", 1500),
    "517410": ("Satellite Telecommunications", "revenue_millions", 44.0),
    "517810": ("All Other Telecommunications", "revenue_millions", 40.0),
    "518210": ("Computing Infrastructure Providers, Data Processing, Web Hosting", "revenue_millions", 40.0),
    "519210": ("Libraries and Archives", "revenue_millions", 21.0),

    # Sector 52 – Finance and Insurance
    "522220": ("Sales Financing", "revenue_millions", 47.0),
    "522291": ("Consumer Lending", "revenue_millions", 47.0),
    "522292": ("Real Estate Credit", "revenue_millions", 47.0),
    "522310": ("Mortgage and Nonmortgage Loan Brokers", "revenue_millions", 15.0),
    "522320": ("Financial Transactions Processing", "revenue_millions", 47.0),
    "523150": ("Investment Banking and Securities Intermediation", "revenue_millions", 47.0),
    "523940": ("Portfolio Management and Investment Advice", "revenue_millions", 47.0),
    "524113": ("Direct Life Insurance Carriers", "revenue_millions", 47.0),
    "524114": ("Direct Health and Medical Insurance Carriers", "revenue_millions", 47.0),
    "524126": ("Direct Property and Casualty Insurance Carriers", "employees", 1500),
    "524210": ("Insurance Agencies and Brokerages", "revenue_millions", 15.0),
    "524291": ("Claims Adjusting", "revenue_millions", 25.0),
    "524292": ("Pharmacy Benefit Management and Other Third-Party Administration", "revenue_millions", 45.5),

    # Sector 53 – Real Estate and Rental and Leasing
    "531110": ("Lessors of Residential Buildings and Dwellings", "revenue_millions", 34.0),
    "531120": ("Lessors of Nonresidential Buildings", "revenue_millions", 34.0),
    "531210": ("Offices of Real Estate Agents and Brokers", "revenue_millions", 15.0),
    "531311": ("Residential Property Managers", "revenue_millions", 12.5),
    "531312": ("Nonresidential Property Managers", "revenue_millions", 19.5),
    "531320": ("Offices of Real Estate Appraisers", "revenue_millions", 9.5),
    "531390": ("Other Activities Related to Real Estate", "revenue_millions", 19.5),
    "532111": ("Passenger Car Rental", "revenue_millions", 47.0),
    "532112": ("Passenger Car Leasing", "revenue_millions", 47.0),
    "532120": ("Truck, Utility Trailer, and RV Rental and Leasing", "revenue_millions", 47.0),
    "532283": ("Home Health Equipment Rental", "revenue_millions", 41.0),

    # Sector 54 – Professional, Scientific and Technical Services
    "541110": ("Offices of Lawyers", "revenue_millions", 15.5),
    "541191": ("Title Abstract and Settlement Offices", "revenue_millions", 19.5),
    "541199": ("All Other Legal Services", "revenue_millions", 20.5),
    "541211": ("Offices of Certified Public Accountants", "revenue_millions", 26.5),
    "541213": ("Tax Preparation Services", "revenue_millions", 25.0),
    "541214": ("Payroll Services", "revenue_millions", 39.0),
    "541219": ("Other Accounting Services", "revenue_millions", 25.0),
    "541310": ("Architectural Services", "revenue_millions", 12.5),
    "541320": ("Landscape Architectural Services", "revenue_millions", 9.0),
    "541330": ("Engineering Services", "revenue_millions", 25.5),
    "541340": ("Drafting Services", "revenue_millions", 9.0),
    "541350": ("Building Inspection Services", "revenue_millions", 11.5),
    "541360": ("Geophysical Surveying and Mapping Services", "revenue_millions", 28.5),
    "541370": ("Surveying and Mapping Services", "revenue_millions", 19.0),
    "541380": ("Testing Laboratories and Services", "revenue_millions", 19.0),
    "541410": ("Interior Design Services", "revenue_millions", 9.0),
    "541420": ("Industrial Design Services", "revenue_millions", 17.0),
    "541430": ("Graphic Design Services", "revenue_millions", 9.0),
    "541490": ("Other Specialized Design Services", "revenue_millions", 13.5),
    "541511": ("Custom Computer Programming Services", "revenue_millions", 34.0),
    "541512": ("Computer Systems Design Services", "revenue_millions", 34.0),
    "541513": ("Computer Facilities Management Services", "revenue_millions", 37.0),
    "541519": ("Other Computer Related Services", "revenue_millions", 34.0),
    "541611": ("Administrative Management and General Management Consulting Services", "revenue_millions", 24.5),
    "541612": ("Human Resources Consulting Services", "revenue_millions", 29.0),
    "541613": ("Marketing Consulting Services", "revenue_millions", 19.0),
    "541614": ("Process, Physical Distribution and Logistics Consulting Services", "revenue_millions", 20.0),
    "541618": ("Other Management Consulting Services", "revenue_millions", 19.0),
    "541620": ("Environmental Consulting Services", "revenue_millions", 19.0),
    "541690": ("Other Scientific and Technical Consulting Services", "revenue_millions", 19.0),
    "541713": ("Research and Development in Nanotechnology", "employees", 1000),
    "541714": ("Research and Development in Biotechnology", "employees", 1000),
    "541715": ("Research and Development in Physical, Engineering, and Life Sciences", "employees", 1000),
    "541720": ("Research and Development in the Social Sciences and Humanities", "revenue_millions", 28.0),
    "541810": ("Advertising Agencies", "revenue_millions", 25.5),
    "541820": ("Public Relations Agencies", "revenue_millions", 19.0),
    "541830": ("Media Buying Agencies", "revenue_millions", 32.5),
    "541840": ("Media Representatives", "revenue_millions", 21.0),
    "541860": ("Direct Mail Advertising", "revenue_millions", 22.0),
    "541910": ("Marketing Research and Public Opinion Polling", "revenue_millions", 22.5),
    "541921": ("Photography Studios, Portrait", "revenue_millions", 16.0),
    "541922": ("Commercial Photography", "revenue_millions", 9.0),
    "541930": ("Translation and Interpretation Services", "revenue_millions", 22.5),
    "541940": ("Veterinary Services", "revenue_millions", 10.0),
    "541990": ("All Other Professional, Scientific and Technical Services", "revenue_millions", 19.5),

    # Sector 55 – Management of Companies
    "551111": ("Offices of Bank Holding Companies", "revenue_millions", 38.5),
    "551112": ("Offices of Other Holding Companies", "revenue_millions", 45.5),

    # Sector 56 – Administrative and Support Services
    "561110": ("Office Administrative Services", "revenue_millions", 12.5),
    "561210": ("Facilities Support Services", "revenue_millions", 47.0),
    "561311": ("Employment Placement Agencies", "revenue_millions", 34.0),
    "561312": ("Executive Search Services", "revenue_millions", 34.0),
    "561320": ("Temporary Help Services", "revenue_millions", 34.0),
    "561330": ("Professional Employer Organizations", "revenue_millions", 41.5),
    "561410": ("Document Preparation Services", "revenue_millions", 19.0),
    "561421": ("Telephone Answering Services", "revenue_millions", 19.0),
    "561422": ("Telemarketing Bureaus and Other Contact Centers", "revenue_millions", 25.5),
    "561431": ("Private Mail Centers", "revenue_millions", 19.0),
    "561439": ("Other Business Service Centers", "revenue_millions", 26.5),
    "561440": ("Collection Agencies", "revenue_millions", 19.5),
    "561450": ("Credit Bureaus", "revenue_millions", 41.0),
    "561491": ("Repossession Services", "revenue_millions", 19.0),
    "561499": ("All Other Business Support Services", "revenue_millions", 21.5),
    "561510": ("Travel Agencies", "revenue_millions", 25.0),
    "561520": ("Tour Operators", "revenue_millions", 25.0),
    "561591": ("Convention and Visitors Bureaus", "revenue_millions", 25.0),
    "561599": ("All Other Travel Arrangement and Reservation Services", "revenue_millions", 32.5),
    "561611": ("Investigation and Personal Background Check Services", "revenue_millions", 25.0),
    "561612": ("Security Guards and Patrol Services", "revenue_millions", 29.0),
    "561613": ("Armored Car Services", "revenue_millions", 43.0),
    "561621": ("Security Systems Services (except Locksmiths)", "revenue_millions", 25.0),
    "561622": ("Locksmiths", "revenue_millions", 25.0),
    "561710": ("Exterminating and Pest Control Services", "revenue_millions", 17.5),
    "561720": ("Janitorial Services", "revenue_millions", 22.0),
    "561730": ("Landscaping Services", "revenue_millions", 9.5),
    "561740": ("Carpet and Upholstery Cleaning Services", "revenue_millions", 8.5),
    "561790": ("Other Services to Buildings and Dwellings", "revenue_millions", 9.0),
    "561910": ("Packaging and Labeling Services", "revenue_millions", 19.5),
    "561920": ("Convention and Trade Show Organizers", "revenue_millions", 20.0),
    "561990": ("All Other Support Services", "revenue_millions", 16.5),
    "562111": ("Solid Waste Collection", "revenue_millions", 47.0),
    "562112": ("Hazardous Waste Collection", "revenue_millions", 47.0),
    "562211": ("Hazardous Waste Treatment and Disposal", "revenue_millions", 47.0),
    "562212": ("Solid Waste Landfill", "revenue_millions", 47.0),
    "562910": ("Remediation Services", "revenue_millions", 25.0),
    "562920": ("Materials Recovery Facilities", "revenue_millions", 25.0),
    "562998": ("All Other Miscellaneous Waste Management Services", "revenue_millions", 16.5),

    # Sector 61 – Educational Services
    "611110": ("Elementary and Secondary Schools", "revenue_millions", 20.0),
    "611210": ("Junior Colleges", "revenue_millions", 32.5),
    "611310": ("Colleges, Universities and Professional Schools", "revenue_millions", 34.5),
    "611410": ("Business and Secretarial Schools", "revenue_millions", 20.5),
    "611420": ("Computer Training", "revenue_millions", 16.0),
    "611430": ("Professional and Management Development Training", "revenue_millions", 15.0),
    "611512": ("Flight Training", "revenue_millions", 34.0),
    "611519": ("Other Technical and Trade Schools", "revenue_millions", 21.0),
    "611610": ("Fine Arts Schools", "revenue_millions", 9.0),
    "611620": ("Sports and Recreation Instruction", "revenue_millions", 9.0),
    "611630": ("Language Schools", "revenue_millions", 20.5),
    "611691": ("Exam Preparation and Tutoring", "revenue_millions", 12.5),
    "611699": ("All Other Miscellaneous Schools and Instruction", "revenue_millions", 16.5),
    "611710": ("Educational Support Services", "revenue_millions", 24.0),

    # Sector 62 – Health Care and Social Assistance
    "621111": ("Offices of Physicians (except Mental Health Specialists)", "revenue_millions", 16.0),
    "621112": ("Offices of Physicians, Mental Health Specialists", "revenue_millions", 13.5),
    "621210": ("Offices of Dentists", "revenue_millions", 9.0),
    "621310": ("Offices of Chiropractors", "revenue_millions", 9.0),
    "621320": ("Offices of Optometrists", "revenue_millions", 9.0),
    "621330": ("Offices of Mental Health Practitioners (except Physicians)", "revenue_millions", 9.0),
    "621340": ("Offices of Physical, Occupational and Speech Therapists and Audiologists", "revenue_millions", 12.5),
    "621391": ("Offices of Podiatrists", "revenue_millions", 9.0),
    "621399": ("Offices of All Other Miscellaneous Health Practitioners", "revenue_millions", 10.0),
    "621410": ("Family Planning Centers", "revenue_millions", 19.0),
    "621420": ("Outpatient Mental Health and Substance Abuse Centers", "revenue_millions", 19.0),
    "621491": ("HMO Medical Centers", "revenue_millions", 44.5),
    "621492": ("Kidney Dialysis Centers", "revenue_millions", 47.0),
    "621493": ("Freestanding Ambulatory Surgical and Emergency Centers", "revenue_millions", 19.0),
    "621498": ("All Other Outpatient Care Centers", "revenue_millions", 25.5),
    "621511": ("Medical Laboratories", "revenue_millions", 41.5),
    "621512": ("Diagnostic Imaging Centers", "revenue_millions", 19.0),
    "621610": ("Home Health Care Services", "revenue_millions", 19.0),
    "621910": ("Ambulance Services", "revenue_millions", 22.5),
    "621991": ("Blood and Organ Banks", "revenue_millions", 40.0),
    "621999": ("All Other Miscellaneous Ambulatory Health Care Services", "revenue_millions", 20.5),
    "622110": ("General Medical and Surgical Hospitals", "revenue_millions", 47.0),
    "622210": ("Psychiatric and Substance Abuse Hospitals", "revenue_millions", 47.0),
    "622310": ("Specialty (except Psychiatric and Substance Abuse) Hospitals", "revenue_millions", 47.0),
    "623110": ("Nursing Care Facilities (Skilled Nursing Facilities)", "revenue_millions", 34.0),
    "623210": ("Residential Intellectual and Developmental Disability Facilities", "revenue_millions", 19.0),
    "623220": ("Residential Mental Health and Substance Abuse Facilities", "revenue_millions", 19.0),
    "623311": ("Continuing Care Retirement Communities", "revenue_millions", 34.0),
    "623312": ("Assisted Living Facilities for the Elderly", "revenue_millions", 23.5),
    "623990": ("Other Residential Care Facilities", "revenue_millions", 16.0),
    "624110": ("Child and Youth Services", "revenue_millions", 15.5),
    "624120": ("Services for the Elderly and Persons with Disabilities", "revenue_millions", 15.0),
    "624190": ("Other Individual and Family Services", "revenue_millions", 16.0),
    "624210": ("Community Food Services", "revenue_millions", 19.5),
    "624221": ("Temporary Shelters", "revenue_millions", 13.5),
    "624229": ("Other Community Housing Services", "revenue_millions", 19.0),
    "624230": ("Emergency and Other Relief Services", "revenue_millions", 41.5),
    "624310": ("Vocational Rehabilitation Services", "revenue_millions", 15.0),
    "624410": ("Child Care Services", "revenue_millions", 9.5),

    # Sector 71 – Arts, Entertainment and Recreation
    "711110": ("Theater Companies and Dinner Theaters", "revenue_millions", 25.0),
    "711120": ("Dance Companies", "revenue_millions", 18.0),
    "711130": ("Musical Groups and Artists", "revenue_millions", 15.0),
    "711190": ("Other Performing Arts Companies", "revenue_millions", 34.0),
    "711211": ("Sports Teams and Clubs", "revenue_millions", 47.0),
    "711212": ("Race Tracks", "revenue_millions", 47.0),
    "711310": ("Promoters of Performing Arts, Sports with Facilities", "revenue_millions", 40.0),
    "711320": ("Promoters of Performing Arts, Sports without Facilities", "revenue_millions", 22.0),
    "712110": ("Museums", "revenue_millions", 34.0),
    "712130": ("Zoos and Botanical Gardens", "revenue_millions", 34.0),
    "713110": ("Amusement and Theme Parks", "revenue_millions", 47.0),
    "713210": ("Casinos (except Casino Hotels)", "revenue_millions", 34.0),
    "713910": ("Golf Courses and Country Clubs", "revenue_millions", 19.0),
    "713920": ("Skiing Facilities", "revenue_millions", 35.0),
    "713940": ("Fitness and Recreational Sports Centers", "revenue_millions", 17.5),
    "713950": ("Bowling Centers", "revenue_millions", 12.5),
    "713990": ("All Other Amusement and Recreation Industries", "revenue_millions", 9.0),

    # Sector 72 – Accommodation and Food Services
    "721110": ("Hotels (except Casino Hotels) and Motels", "revenue_millions", 40.0),
    "721120": ("Casino Hotels", "revenue_millions", 40.0),
    "721191": ("Bed and Breakfast Inns", "revenue_millions", 9.0),
    "722310": ("Food Service Contractors", "revenue_millions", 47.0),
    "722320": ("Caterers", "revenue_millions", 9.0),
    "722410": ("Drinking Places (Alcoholic Beverages)", "revenue_millions", 9.0),
    "722511": ("Full-Service Restaurants", "revenue_millions", 11.5),
    "722513": ("Limited-Service Restaurants", "revenue_millions", 13.5),
    "722514": ("Cafeterias, Grill Buffets, and Buffets", "revenue_millions", 34.0),
    "722515": ("Snack and Nonalcoholic Beverage Bars", "revenue_millions", 22.5),

    # Sector 81 – Other Services
    "811111": ("General Automotive Repair", "revenue_millions", 9.0),
    "811114": ("Specialized Automotive Repair", "revenue_millions", 9.0),
    "811210": ("Electronic and Precision Equipment Repair and Maintenance", "revenue_millions", 34.0),
    "811310": ("Commercial and Industrial Machinery and Equipment Repair and Maintenance", "revenue_millions", 12.5),
    "811411": ("Home and Garden Equipment Repair and Maintenance", "revenue_millions", 9.0),
    "811412": ("Appliance Repair and Maintenance", "revenue_millions", 19.0),
    "812111": ("Barber Shops", "revenue_millions", 9.5),
    "812112": ("Beauty Salons", "revenue_millions", 9.5),
    "812191": ("Diet and Weight Reducing Centers", "revenue_millions", 27.5),
    "812210": ("Funeral Homes and Funeral Services", "revenue_millions", 12.5),
    "812220": ("Cemeteries and Crematories", "revenue_millions", 25.0),
    "812310": ("Coin Operated Laundries and Drycleaners", "revenue_millions", 13.0),
    "812320": ("Drycleaning and Laundry Services (except Coin Operated)", "revenue_millions", 8.0),
    "812331": ("Linen Supply", "revenue_millions", 40.0),
    "812332": ("Industrial Launderers", "revenue_millions", 47.0),
    "812910": ("Pet Care (except Veterinary) Services", "revenue_millions", 9.0),
    "812930": ("Parking Lots and Garages", "revenue_millions", 47.0),
    "812990": ("All Other Personal Services", "revenue_millions", 15.0),
    "813110": ("Religious Organizations", "revenue_millions", 13.0),
    "813211": ("Grantmaking Foundations", "revenue_millions", 40.0),
    "813212": ("Voluntary Health Organizations", "revenue_millions", 34.0),
    "813311": ("Human Rights Organizations", "revenue_millions", 34.0),
    "813410": ("Civic and Social Organizations", "revenue_millions", 9.5),
    "813910": ("Business Associations", "revenue_millions", 15.5),
    "813920": ("Professional Organizations", "revenue_millions", 23.5),
    "813930": ("Labor Unions and Similar Labor Organizations", "revenue_millions", 16.5),
    "813940": ("Political Organizations", "revenue_millions", 14.0),
    "813990": ("Other Similar Organizations", "revenue_millions", 13.5),
}

MEDICAL_SECTORS = {"621", "622", "623", "624", "334", "339"}

SETASIDE_NOTES = {
    "SDVOSB": "SBA-certified or VA-verified Service-Disabled Veteran-Owned Small Business required.",
    "VOSB": "Veteran-Owned Small Business; primarily used for VA contracts.",
    "WOSB": "Women-Owned Small Business; must be at least 51% woman-owned and controlled.",
    "8A": "SBA 8(a) Business Development program participant required.",
    "HUBZONE": "Business must be in a HUBZone with 35% employees in zone.",
    "SB": "Any concern qualifying as small under the applicable size standard.",
}


def check_size(standard_type, standard_value, revenue=None, employees=None):
    if standard_type == "revenue_millions":
        if revenue is None:
            return None, "Revenue not provided; cannot determine size qualification."
        if revenue <= standard_value:
            return True, f"${revenue}M avg annual revenue <= ${standard_value}M size standard limit."
        else:
            return False, f"${revenue}M avg annual revenue exceeds ${standard_value}M size standard limit."
    elif standard_type == "employees":
        if employees is None:
            return None, "Employee count not provided; cannot determine size qualification."
        if employees <= standard_value:
            return True, f"{employees} employees <= {standard_value} employee size standard limit."
        else:
            return False, f"{employees} employees exceeds {standard_value} employee size standard limit."
    return None, "Unknown standard type."


def build_result(naics_code, revenue=None, employees=None, setaside=None):
    code = naics_code.strip()

    if code not in NAICS_DATA:
        return {
            "naics_code": code,
            "found": False,
            "error": (
                f"NAICS code {code} not found in SBA size standards table. "
                "Verify at: https://www.sba.gov/document/support-table-size-standards"
            ),
        }

    description, standard_type, standard_value = NAICS_DATA[code]
    sector = code[:3]
    medical = sector in MEDICAL_SECTORS

    qualified, size_detail = check_size(standard_type, standard_value, revenue, employees)

    if standard_type == "revenue_millions":
        size_standard_display = f"${standard_value}M average annual receipts"
    else:
        size_standard_display = f"{standard_value} employees"

    if qualified is True:
        recommendation = "GO"
    elif qualified is False:
        recommendation = "NO-GO"
    else:
        recommendation = "CONDITIONAL"

    result = {
        "naics_code": code,
        "found": True,
        "description": description,
        "sector": sector,
        "is_medical": medical,
        "size_standard_type": standard_type,
        "size_standard_value": standard_value,
        "size_standard_display": size_standard_display,
        "company_revenue_millions": revenue,
        "company_employees": employees,
        "small_business_qualified": qualified,
        "size_determination_detail": size_detail,
        "sdvosb_eligible": qualified,
        "recommendation": recommendation,
        "source": "SBA Table of Small Business Size Standards, effective March 17, 2023",
    }

    if setaside:
        key = setaside.upper().replace("-", "").replace("_", "")
        note = SETASIDE_NOTES.get(key, f"Set-aside type '{setaside}' not recognized.")
        result["setaside_requested"] = setaside
        result["setaside_note"] = note

    return result


def main():
    parser = argparse.ArgumentParser(description="Check NAICS eligibility using official SBA size standards.")
    parser.add_argument("naics_code", help="6-digit NAICS code")
    parser.add_argument("--revenue", type=float, default=None, metavar="MILLIONS",
                        help="3-year average annual revenue in millions (e.g. 36 for $36M)")
    parser.add_argument("--employees", type=int, default=None, metavar="COUNT",
                        help="Employee count (e.g. 160)")
    parser.add_argument("--setaside", type=str, default=None,
                        help="Set-aside type: SDVOSB, VOSB, WOSB, 8A, HUBZONE, SB")

    args = parser.parse_args()
    result = build_result(args.naics_code, args.revenue, args.employees, args.setaside)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()