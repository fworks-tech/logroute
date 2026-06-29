"""
Structured FMCSA HOS reference data, extracted from the Interstate Truck
Driver's Guide to Hours of Service for Property Carriers (April 2022).

These dictionaries mirror the OpenAPI schemas in
docs/fmcsahos395driversguidetohos2022042801.openapi.yaml.
"""

HOS_SUMMARY = {
    "guide_title": "Interstate Truck Driver's Guide to Hours of Service",
    "audience": "Property-carrying CMV drivers operating in interstate commerce",
    "disclaimer": "This is a guide only and does not have the force and effect of law.",
    "governing_regulation": "49 CFR Part 395",
}

COMPLIANCE_REQUIREMENTS = {
    "applies_when": [
        "CMV used on highways in interstate commerce",
        "Transporting property",
        "Weighs 10,001 lbs or more including load",
        "Has GVWR or GCWR of 10,001 lbs or more",
        "Transporting placarded hazardous materials",
    ],
    "key_reference": "49 CFR Part 395",
}

COMMERCE_DEFINITIONS = {
    "interstate": {
        "description": (
            "Trade, traffic, or transportation between a State and a place "
            "outside that State, between two places in a State through another "
            "State, or as part of trade originating or terminating outside "
            "the State or the United States."
        ),
        "cfr_reference": "§ 390.5T",
    },
    "intrastate": {
        "description": (
            "Transportation not covered by the interstate definition, usually "
            "occurring within a single State."
        ),
        "note": "Federal HOS generally do not apply, but State rules may.",
    },
}

DUTY_STATUS_DEFINITIONS = {
    "on_duty": {
        "cfr_reference": "§ 395.2",
        "description": (
            "All time working or required to be ready to work for any employer."
        ),
        "includes": [
            "Waiting to be dispatched",
            "Inspecting, servicing, fueling, or washing a truck",
            "Driving a CMV",
            "Loading, unloading, supervising, or paperwork",
            "Caring for a broken-down truck",
            "Drug/alcohol testing",
            "Other work for a motor carrier",
            "Paid work for a non-motor-carrier employer",
        ],
        "exclusions": [
            "Resting in a parked CMV",
            "Resting in a sleeper berth",
            "Up to 3 hours passenger-seat time paired with 7 sleeper hours",
        ],
    },
    "off_duty": {
        "description": (
            "Relieved of all duty and responsibility, free to pursue "
            "activities of own choosing, and able to leave where the vehicle "
            "is parked."
        ),
    },
    "personal_conveyance": {
        "description": (
            "Movement of a CMV for personal use while off duty when relieved "
            "from all work responsibility."
        ),
    },
    "yard_moves": {
        "description": (
            "Transfers of CMVs between locations within a terminal or similar "
            "private facility; classified as on-duty not driving under ELD rules."
        ),
    },
}

HOS_LIMITS = {
    "fourteen_hour_window": {
        "cfr_reference": "§ 395.3(a)(2)",
        "window_hours": 14,
        "off_duty_required_before": 10,
        "description": (
            "A 14 consecutive-hour driving window begins when any work starts. "
            "You may drive up to 11 hours inside that window. Once the window "
            "expires, you cannot drive again until after 10 consecutive hours off duty."
        ),
    },
    "eleven_hour_limit": {
        "cfr_reference": "§ 395.3(a)(3)",
        "max_driving_hours": 11,
        "break_threshold_hours": 8,
        "break_required_minutes": 30,
    },
    "sleeper_berth": {
        "cfr_reference": "§ 395.1(g)",
        "options": [
            "10 consecutive hours in sleeper berth",
            "7 consecutive hours in sleeper berth + up to 3 hours off duty or passenger",
            "Split sleeper berth: 7 hours + 2 hours qualifying rest",
        ],
    },
    "thirty_minute_break": {
        "cfr_reference": "§ 395.3(a)(3)(ii)",
        "description": (
            "Required after 8 cumulative driving hours; may be on duty, "
            "off duty, or in sleeper berth."
        ),
        "applies_to_short_haul": False,
    },
    "weekly_limit": {
        "cfr_reference": "§ 395.3(b)",
        "sixty_hour_seven_day": {"hours": 60, "days": 7},
        "seventy_hour_eight_day": {"hours": 70, "days": 8},
        "rolling_basis": True,
    },
    "restart": {
        "cfr_references": ["§ 395.3(c)(1)", "§ 395.3(c)(2)"],
        "hours_required": 34,
        "optional": True,
    },
}

HOS_EXCEPTIONS = [
    {
        "id": "cdl-short-haul",
        "title": "CDL Short-Haul Exception",
        "cfr_section": "§ 395.1(e)(1)",
        "exception_type": [
            "No ELD/logbook required when using time records",
            "30-minute break does not apply",
        ],
        "conditions": [
            "Return to normal work reporting location within 14 consecutive hours",
            "Operate within 150 air-mile radius",
            "At least 10 consecutive hours off duty between shifts",
            "11-hour driving limit still applies",
        ],
        "notes": None,
    },
    {
        "id": "non-cdl-short-haul",
        "title": "Non-CDL Short-Haul Exception",
        "cfr_section": "§ 395.1(e)(2)",
        "exception_type": [
            "No ELD/logbook required when using time records",
            "30-minute break does not apply",
            "Extended 16-hour driving window allowed twice per 7-day period",
        ],
        "conditions": [
            "Vehicle does not require a CDL",
            "Return to work reporting location every day",
            "Operate within 150 air-mile radius",
            "No driving past 14th hour for 5 days of 7",
            "No driving past 16th hour for 2 days of 7",
        ],
        "notes": "Not eligible for CDL short-haul, 16-hour short-haul, or split sleeper berth.",
    },
    {
        "id": "adverse-driving-conditions",
        "title": "Adverse Driving Conditions",
        "cfr_section": "§ 395.1(b)(1)",
        "exception_type": [
            "Up to 2 additional hours of driving time",
            "Up to 2 additional hours of driving window",
        ],
        "conditions": [
            "Condition unknown or not reasonably knowable before dispatch or before driving after a qualifying rest break",
        ],
        "notes": "Typical rush-hour congestion is not included.",
    },
    {
        "id": "agricultural-operations",
        "title": "Agricultural Operations",
        "cfr_section": "§ 395.1(k)",
        "exception_type": [
            "All HOS regulations exempt",
        ],
        "conditions": [
            "Transporting agricultural commodities or farm supplies for agricultural purposes",
            "Within 150 air-miles of source",
            "Seasonal limitation applies",
        ],
        "notes": None,
    },
    {
        "id": "sixteen-hour-short-haul",
        "title": "16-Hour Short-Haul Exception (CDL)",
        "cfr_section": "§ 395.1(o)",
        "exception_type": [
            "16-hour duty period allowed once per 7-day period or after a 34-hour restart",
        ],
        "conditions": [
            "Return to reporting location that day and for last 5 duty tours",
            "Released within 16 hours",
        ],
        "notes": "Not available if driver is eligible for § 395.1(e)(2).",
    },
    {
        "id": "construction-materials",
        "title": "Construction Materials and Equipment",
        "cfr_section": "§ 395.1(m)",
        "exception_type": [
            "24 consecutive hours off duty restarts 60/7 or 70/8 limit",
        ],
        "conditions": [
            "Transporting construction/pavement materials, construction equipment, or maintenance vehicles",
            "To or from active construction site",
            "Within 75 air-miles",
            "No placarded hazmat",
        ],
        "notes": None,
    },
    {
        "id": "oilfield-operations",
        "title": "Oilfield Operations",
        "cfr_section": "§ 395.1(d)(1)",
        "exception_type": [
            "24 consecutive hours off duty restarts the 70/8 calculation",
        ],
        "conditions": [
            "CMVs used exclusively in transportation of oilfield equipment and servicing field operations",
        ],
        "notes": "Waiting time at well site may be recorded as off duty under § 395.1(d)(2).",
    },
    {
        "id": "propane-winter-heating",
        "title": "Propane Winter Heating Fuel / Pipeline Emergencies",
        "cfr_section": "§ 390.3T(f)(7)",
        "exception_type": [
            "All HOS regulations exempt",
        ],
        "conditions": [
            "Regulations must prevent a driver from responding to emergency conditions",
        ],
        "notes": None,
    },
    {
        "id": "emergency-relief",
        "title": "Emergency Relief",
        "cfr_section": "§ 390.23",
        "exception_type": [
            "All HOS regulations exempt",
        ],
        "conditions": [
            "Declared national, regional, State, or local emergency",
            "Providing direct assistance",
        ],
        "notes": None,
    },
    {
        "id": "utility-service-vehicles",
        "title": "Utility Service Vehicles",
        "cfr_section": "§ 395.1(n)",
        "exception_type": [
            "All HOS regulations exempt",
        ],
        "conditions": [
            "Repairing, maintaining, or delivering public utility services",
            "Within service area",
            "No new construction activity",
        ],
        "notes": None,
    },
]

LOGGING_REQUIREMENTS = {
    "primary_method": "ELD",
    "eld_info_url": "https://eld.fmcsa.dot.gov",
    "paper_log_allowed_when": [
        "RODS required 8 or fewer days in the last 30 days",
        "Driveaway-towaway operations",
        "Vehicles manufactured before model year 2000",
    ],
    "required_rods_fields": [
        "Date",
        "Total miles driven today",
        "Truck or tractor and trailer number",
        "Name of carrier",
        "Main office address",
        "Driver's signature",
        "Name of co-driver",
        "Time base",
        "Remarks",
        "Total hours",
        "Shipping documents",
    ],
}

RESOURCE_LINKS = {
    "hos_web_page": "https://www.fmcsa.dot.gov/regulations/hours-of-service",
    "eld_information": "https://eld.fmcsa.dot.gov",
    "personal_conveyance_guidance": (
        "https://www.fmcsa.dot.gov/regulations/hours-service/personal-conveyance"
    ),
    "information_line": "1-800-832-5660",
    "email": "hoursofservice@dot.gov",
}
