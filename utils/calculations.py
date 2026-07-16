def safe_divide(numerator, denominator):
    """Safely handles division by zero and forces float casting to prevent UI crashes."""
    try:
        num = float(numerator)
        den = float(denominator)
        if den == 0.0:
            return 0.0
        return num / den
    except (ValueError, TypeError):
        return 0.0


def calc_percentage(numerator, denominator, label):
    """Calculate and validate a percentage KPI."""
    value = safe_divide(numerator, denominator) * 100
    if not 0 <= value <= 100:
        raise ValueError(
            f"{label} is {value:.2f}% (value: {float(numerator):,.2f}; "
            f"base: {float(denominator):,.2f}). It must be between 0% and 100%."
        )
    return round(value, 4)


def calc_intensity(value, denominator):
    """Keep low intensity values meaningful instead of rounding them to zero."""
    return round(safe_divide(value, denominator), 8)

def calculate_ghg_intensity(scope1, scope2, turnover_inr, ppp_usd_inr):
    # Sum absolute emissions
    absolute_emissions = float(scope1) + float(scope2)
    
    # Defense against zero-division if revenue is not yet entered
    safe_turnover = float(turnover_inr) if float(turnover_inr) > 0 else 1.0
    
    # Calculate intensity per rupee
    intensity_inr = absolute_emissions / safe_turnover
    
    # Calculate PPP adjusted intensity
    # Turnover in USD = INR / PPP_Rate
    turnover_ppp = safe_turnover / float(ppp_usd_inr)
    intensity_ppp = absolute_emissions / turnover_ppp
    
    return {
        "absolute_emissions": round(absolute_emissions, 4),
        "ghg_intensity_inr": round(intensity_inr, 8),
        "ghg_intensity_ppp": round(intensity_ppp, 8)
    }

def calculate_water_metrics(input_meters, output_meters, turnover_inr, ppp_usd_inr):
    # Water Consumption = Input Water - Output Water
    consumption = float(input_meters) - float(output_meters)
    if consumption < 0:
        consumption = 0.0
        
    intensity_inr = safe_divide(consumption, turnover_inr)
    turnover_ppp = safe_divide(turnover_inr, ppp_usd_inr)
    intensity_ppp = safe_divide(consumption, turnover_ppp)
    
    return {
        "water_consumption": round(consumption, 4),
        "water_intensity_inr": round(intensity_inr, 8),
        "water_intensity_ppp": round(intensity_ppp, 8)
    }

def calculate_energy_metrics(renewable_joules, non_renewable_joules, turnover_inr, ppp_usd_inr):
    total_energy = float(renewable_joules) + float(non_renewable_joules)
    
    renewable_percentage = safe_divide(renewable_joules, total_energy) * 100
    
    intensity_inr = safe_divide(total_energy, turnover_inr)
    turnover_ppp = safe_divide(turnover_inr, ppp_usd_inr)
    intensity_ppp = safe_divide(total_energy, turnover_ppp)
    
    return {
        "total_energy_consumed": round(total_energy, 4),
        "renewable_energy_share": round(renewable_percentage, 4),
        "energy_intensity_inr": round(intensity_inr, 8),
        "energy_intensity_ppp": round(intensity_ppp, 8)
    }

def calculate_waste_metrics(waste_gen_list, recovered_mass, turnover_inr, ppp_usd_inr):
    """
    Calculates total waste, recovery rates, and intensity adjusted for PPP.
    """
    total_waste = sum(waste_gen_list)
    
    # Standard Intensity
    intensity_inr = safe_divide(total_waste, turnover_inr)
    
    # PPP Adjusted Intensity
    turnover_ppp = safe_divide(turnover_inr, ppp_usd_inr)
    intensity_ppp = safe_divide(total_waste, turnover_ppp)
    
    recovery_rate = safe_divide(recovered_mass, total_waste) * 100
    disposal_rate = 100.0 - recovery_rate
    
    return {
        "total_waste_generated": round(total_waste, 4),
        "waste_intensity_inr": round(intensity_inr, 8),
        "waste_intensity_ppp": round(intensity_ppp, 8),
        "waste_recovery_percentage": round(recovery_rate, 4),
        "waste_disposal_percentage": round(disposal_rate, 4)
    }

def calculate_ltifr(lost_time_injuries, total_working_hours):
    # SEBI Formula: (Total Lost Time Injuries * 1,000,000) / Total Working Hours
    numerator = float(lost_time_injuries) * 1000000
    ltifr_value = safe_divide(numerator, total_working_hours)
    
    return round(ltifr_value, 4)

def calculate_gender_metrics(female_wages, total_wages):
    contribution_percentage = safe_divide(female_wages, total_wages) * 100
    
    return round(contribution_percentage, 4)

def calculate_inclusive_dev(msme_procurement, total_procurement, rural_wages, semi_urban_wages, total_wages):
    msme_share = safe_divide(msme_procurement, total_procurement) * 100
    rural_wage_share = safe_divide(rural_wages, total_wages) * 100
    semi_urban_wage_share = safe_divide(semi_urban_wages, total_wages) * 100
    
    return {
        "msme_procurement_percentage": round(msme_share, 4),
        "rural_job_creation_ratio": round(rural_wage_share, 4),
        "semi_urban_job_creation_ratio": round(semi_urban_wage_share, 4)
    }

def calculate_accounts_payable_days(accounts_payable, cost_of_goods_procured):
    # SEBI Formula: (Accounts Payable * 365) / Cost of Goods/Services Procured
    numerator = float(accounts_payable) * 365
    payable_days = safe_divide(numerator, cost_of_goods_procured)
    
    return round(payable_days, 4)

def calculate_rpt_shares(rpt_purchases, total_purchases, rpt_sales, total_sales, rpt_loans, total_loans, rpt_investments, total_investments):
    purchase_share = safe_divide(rpt_purchases, total_purchases) * 100
    sales_share = safe_divide(rpt_sales, total_sales) * 100
    loan_share = safe_divide(rpt_loans, total_loans) * 100
    investment_share = safe_divide(rpt_investments, total_investments) * 100
    
    return {
        "rpt_purchase_percentage": round(purchase_share, 4),
        "rpt_sales_percentage": round(sales_share, 4),
        "rpt_loan_percentage": round(loan_share, 4),
        "rpt_investment_percentage": round(investment_share, 4)
    }


def calculate_all(state):
    """Calculate and validate all BRSR Core metrics used for report export."""
    s = state
    revenue = float(s.get("revenue", 0) or 0)
    physical_output = float(s.get("physical_output_quantity", 0) or 0)
    ghg = calculate_ghg_intensity(s.get("scope1", 0), s.get("scope2", 0), revenue or 1.0, 1.0)
    water = calculate_water_metrics(s.get("input_m", 0), s.get("output_m", 0), revenue or 1.0, 1.0)
    energy = calculate_energy_metrics(s.get("renewable", 0), s.get("non_renewable", 0), revenue or 1.0, 1.0)
    waste_list = [s.get(key, 0) for key in ("waste_plastic", "waste_e", "waste_bio", "waste_cd", "waste_battery", "waste_radio", "waste_haz", "waste_nonhaz")]
    waste = calculate_waste_metrics(waste_list, s.get("waste_recovered", 0), revenue or 1.0, 1.0)

    total_waste = waste["total_waste_generated"]
    rpt = calculate_rpt_shares(
        s.get("rpt_pur", 0), s.get("tot_pur", 0), s.get("rpt_sal", 0), s.get("tot_sal", 0),
        s.get("rpt_loans", 0), s.get("total_loans", 0), s.get("rpt_investments", 0), s.get("total_investments", 0),
    )
    results = {
        "ghg": ghg,
        "water": water,
        "energy": energy,
        "waste": waste,
        "ghg_intensity_output": calc_intensity(ghg["absolute_emissions"], physical_output),
        "water_intensity_output": calc_intensity(water["water_consumption"], physical_output),
        "energy_intensity_output": calc_intensity(energy["total_energy_consumed"], physical_output),
        "waste_intensity_output": calc_intensity(total_waste, physical_output),
        "water_discharge": {
            "untreated": float(s.get("water_untreated", 0) or 0),
            "primary": float(s.get("water_primary_treated", 0) or 0),
            "secondary": float(s.get("water_secondary_treated", 0) or 0),
            "tertiary": float(s.get("water_tertiary_treated", 0) or 0),
        },
        "waste_disposal": {
            "incinerated": float(s.get("waste_incinerated", 0) or 0),
            "landfilled": float(s.get("waste_landfilled", 0) or 0),
            "other": float(s.get("waste_other_disposal", 0) or 0),
            "incinerated_intensity_inr": calc_intensity(s.get("waste_incinerated", 0), revenue),
            "landfilled_intensity_inr": calc_intensity(s.get("waste_landfilled", 0), revenue),
            "other_intensity_inr": calc_intensity(s.get("waste_other_disposal", 0), revenue),
        },
        "wellbeing_percentage": calc_percentage(s.get("wellbeing_spend", 0), revenue, "Wellbeing spending"),
        "ltifr": calculate_ltifr(s.get("lti_count", 0), s.get("working_hours", 0)),
        "permanent_disabilities": float(s.get("permanent_disabilities", 0) or 0),
        "fatalities": float(s.get("fatalities", 0) or 0),
        "female_wage_percentage": calc_percentage(s.get("female_wages", 0), s.get("total_wages", 0), "Female wage share"),
        "posh_complaint_percentage": calc_percentage(s.get("posh_reported", 0), s.get("female_workforce", 0), "POSH complaints as a share of female workforce"),
        "data_breach_percentage": calc_percentage(s.get("total_breaches", 0), s.get("total_cyber_events", 0), "Customer data-breach percentage"),
        "trading_house_purchase_percentage": calc_percentage(s.get("trading_house_purchases", 0), s.get("tot_pur", 0), "Trading-house purchases"),
        "top_10_trading_house_percentage": calc_percentage(s.get("top_10_trading_house_purchases", 0), s.get("trading_house_purchases", 0), "Top 10 trading-house purchases"),
        "dealer_sales_percentage": calc_percentage(s.get("dealer_distributor_sales", 0), s.get("tot_sal", 0), "Dealer/distributor sales"),
        "top_10_dealer_sales_percentage": calc_percentage(s.get("top_10_dealer_distributor_sales", 0), s.get("dealer_distributor_sales", 0), "Top 10 dealer/distributor sales"),
        "rpt": rpt,
    }
    return results


def calculate_all_safe(state):
    """Prevent a validation failure from crashing a Streamlit page."""
    try:
        return calculate_all(state), None
    except ValueError as error:
        return {}, str(error)
