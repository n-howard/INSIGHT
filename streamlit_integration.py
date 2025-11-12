from simple_salesforce import Salesforce
import streamlit as st
import pandas as pd

def create_sf():
    sf = Salesforce(
        username=st.secrets["SF_USERNAME"],
        consumer_key=st.secrets["SF_CONSUMER_KEY"], 
        privatekey=st.secrets["SF_JWT_PRIVATE_KEY"]
        )
    return sf


ASSESSMENTS = {
    "Environment, Health, and Safety": {
        "form_url": "https://docs.google.com/forms/d/e/1FAIpQLScTWIWH3ucfkk2Ud4Dsv5JGFst3kFxQvOMVp4aYXwyhrppPCg/viewform?embedded=true",
        "sheet_name": "Environment, Health, and Safety (Responses)",
        "fields": ['Timestamp__c', 'Site__c', 'Contact_Name__c',  'Overall_Score__c', 'Standard_1__c', 'Indicator_1_1__c', 'Indicator_1_2__c', 'Standard_2__c', 'Indicator_2_1__c', 'Indicator_2_2__c', 'Standard_3__c', 
            'Indicator_3_1__c', 'Indicator_3_2__c', 'Indicator_3_3__c', 'Standard_4__c', 'Indicator_4_1__c', 'Indicator_4_2__c', 'Indicator_4_3__c'
            ]
    },
    "Highly Skilled Personnel": {
        "form_url": "https://docs.google.com/forms/d/e/1FAIpQLSfCs3lUrb2hEB92aZn33ledpwKNXtDOuPjd1hw40p-ZW-Y0JA/viewform?embedded=true",
        "sheet_name": "Highly Skilled Personnel (Responses)",
        "fields": ['Timestamp__c', 'Site__c', 'Contact_Name__c',  'Overall_Score__c', 'Standard_1__c', 'Indicator_1_1__c', 'Standard_2__c', 'Indicator_2_1__c', 'Indicator_2_2__c', 'Standard_3__c', 
            'Indicator_3_1__c', 'Indicator_3_2__c'
            ]
    },
    "Program Management": {
        "form_url": "https://docs.google.com/forms/d/e/1FAIpQLSfiFsaUqThoawBo-vTQLp5vPslFV-4A_efQw9PBwd3QRiHSIA/viewform?embedded=true",
        "sheet_name": "Program Management (Responses)",
        "fields": ['Timestamp__c', 'Site__c', 'Contact_Name__c',  'Overall_Score__c', 'Percent_Complete__c', 'Percent_in_Progress__c', 'Standard_2__c', 'Indicator_2_1__c', 'Standard_3__c', 
            'Indicator_3_1__c', 'Standard_4__c', 'Indicator_4_1__c', 'Standard_5__c', 'Indicator_5_1__c',
            ]
    },
    "Youth Development and Engagement": {
        "form_url": "https://docs.google.com/forms/d/e/1FAIpQLSfvrLHuw7dqBQ5gN-i3rjNA-fusFxd96Hl4hsrC1MwKofBP9A/viewform?embedded=true",
        "sheet_name": "Youth Development and Engagement (Responses)",
        "fields": ['Timestamp__c', 'Site__c', 'Contact_Name__c',   'Overall_Score__c', 'Standard_1__c', 'Indicator_1_1__c', 'Standard_2__c', 'Indicator_2_1__c', 'Standard_3__c', 
            'Indicator_3_1__c', 'Indicator_3_2__c', 'Indicator_3_3__c', 'Standard_4__c', 'Indicator_4_1__c', 'Indicator_4_2__c', 'Indicator_4_3__c'
            ]
        
    },
    "Programming and Activities": {
        "form_url": "https://docs.google.com/forms/d/e/1FAIpQLSejk08smadc3IPkfoOYk9P8Hdj4JcS8UEfnh1bUXwAPUEpPDw/viewform?embedded=true",
        "sheet_name": "Programming and Activities (Responses)",
        "fields": ['Timestamp__c', 'Site__c', 'Contact_Name__c', 'Overall_Score__c', 'Standard_1__c', 'Indicator_1_1__c', 'Indicator_1_2__c', 'Indicator_1_3__c', 'Standard_2__c', 
            'Indicator_2_1__c', 'Indicator_2_2__c', 'Indicator_2_3__c'
            ]

    },
    "Families, Schools, and Communities": {
        "form_url": "https://docs.google.com/forms/d/e/1FAIpQLSf2jg-yPBIGx9w2Zhl1aX3SQGcASQIDMTBizMJ4v4zurNTF-w/viewform?embedded=true",
        "sheet_name": "Families, Schools, and Communities (Responses)",
        "fields": ['Timestamp__c', 'Site__c', 'Contact_Name__c', 'Overall_Score__c', 'Standard_1__c', 'Indicator_1_1__c', 'Indicator_1_2__c', 
                   'Indicator_1_3__c', 'Indicator_1_4__c']
    },
}

def get_recs_desc(sf, assessment, name, cat):
    fields = assessment["fields"][4:]
    if cat == "Recommendations":
        recs_fields = list(filter(lambda x: "Standard" not in x, fields))
        opts = ", ".join(recs_fields)
        results = sf.query_all(f"SELECT {opts} FROM Description__c WHERE Element__c='{name}' AND Category__c='Recommendations'")
        return results
    else:
        opts = ", ".join(fields)
        results = sf.query_all(f"SELECT {opts} FROM Description__c WHERE Element__c='{name}' AND Category__c='Descriptions'")
        return results

def get_org_records(org_input, sf, assessment, name, is_admin, access_level, email):
    """
    get_org_records(org_input, sf, assessment, name, is_admin, access_level, email)
    """
    fields = assessment["fields"]
    opts = ", ".join(fields)
    org_escaped = org_input.replace("'", "\'")
    if access_level:
        opts = opts + ", Organization__c" 
        results = sf.query_all(f"SELECT {opts} FROM INSIGHT_Results__c WHERE Element__c='{name}' AND (Organization__c NOT LIKE '%Average%') AND (Site__c NOT LIKE '%Average%')")
        return results
    if is_admin:
        results = sf.query_all(f"SELECT {opts} FROM INSIGHT_Results__c WHERE Organization__c='{org_escaped}' AND Element__c='{name}' AND (Organization__c NOT LIKE '%Average%') AND (Site__c NOT LIKE '%Average%')")
    else:
        results = sf.query_all(f"SELECT {opts} FROM INSIGHT_Results__c WHERE Contact_Email__c='{email}' AND Element__c='{name}' AND (Organization__c NOT LIKE '%Average%') AND (Site__c NOT LIKE '%Average%')")
    return results



def get_all_org_records(org_input, sf, is_admin, access_level, email):
    """
    get_all_org_records(org_input, sf, is_admin, access_level, email)
    """
    results = [{}]
    for assessment in ASSESSMENTS:
        re = get_org_records(org_input, sf, ASSESSMENTS[assessment], assessment, is_admin, access_level, email)
        results.append({assessment:re})
    return results

def get_overall(org_input, sf, name, is_admin, access_level, email):
    """
    get_overall(org_input, sf, name, is_admin, access_level, email)
    """
    org_escaped = org_input.replace("'", "\'")
    if access_level:
        results = sf.query_all(f"SELECT Overall_Score__c, Organization__c, Timestamp__c FROM INSIGHT_Results__c WHERE Element__c='{name}' AND ((Organization__c NOT LIKE '%Average%') AND (Site__c NOT LIKE '%Average%'))")
        return results
    if is_admin:
        results = sf.query_all(f"SELECT Overall_Score__c, Contact_Name__c, Timestamp__c FROM INSIGHT_Results__c WHERE Organization__c='{org_escaped}' AND Element__c='{name}' AND (Organization__c NOT LIKE '%Average%') AND (Site__c NOT LIKE '%Average%')")
    else:
        results = sf.query_all(f"SELECT Overall_Score__c FROM INSIGHT_Results__c, Timestamp__c WHERE Contact_Email__c='{email}' AND Element__c='{name}' AND (Organization__c NOT LIKE '%Average%') AND (Site__c NOT LIKE '%Average%')")
    return results

def get_all_overall(org_input, sf, is_admin, access_level, email):
    """
    get_all_overall(org_input, sf, is_admin, access_level, email)
    """
    org_escaped = org_input.replace("'", "\'")
    if access_level:
        results = sf.query_all(f"SELECT Overall_Score__c, Element__c, Organization__c FROM INSIGHT_Results__c WHERE (Organization__c NOT LIKE '%Average%') AND (Site__c NOT LIKE '%Average%')")
        return results
    if is_admin:
        results = sf.query_all(f"SELECT Overall_Score__c, Element__c, Contact_Name__c FROM INSIGHT_Results__c WHERE Organization__c='{org_escaped}' AND (Organization__c NOT LIKE '%Average%') AND (Site__c NOT LIKE '%Average%')")
    else:
        results = sf.query_all(f"SELECT Overall_Score__c, Element__c FROM INSIGHT_Results__c WHERE Contact_Email__c='{email}' AND (Organization__c NOT LIKE '%Average%') AND (Site__c NOT LIKE '%Average%')")
    return results

def get_avg_overall(org_input, sf, name, is_admin, access_level, email):
    """
    Retrieves average Overall_Score__c values for:
      - Access-level users: all org/site averages for all orgs
      - Admins: org-specific averages
      - Regular users: their own submissions
    """
    org_escaped = org_input.replace("'", "''")
    element_escaped = name.replace("'", "''")

    if access_level:
        # Access-level: all averages across orgs for this element
        query = (
            f"SELECT Overall_Score__c, Organization__c, Site__c "
            f"FROM INSIGHT_Results__c "
            f"WHERE Element__c='{element_escaped}' "
            f"AND ((Organization__c LIKE '%Average%') OR (Site__c LIKE '%Average%'))"
        )
        return sf.query_all(query)

    elif is_admin:
        # Admin: only averages for their own org
        query = (
            f"SELECT Overall_Score__c, Contact_Name__c, Organization__c, Site__c "
            f"FROM INSIGHT_Results__c "
            f"WHERE Organization__c='{org_escaped}' "
            f"AND Element__c='{element_escaped}' "
            f"AND ((Organization__c LIKE '%Average%') OR (Site__c LIKE '%Average%'))"
        )
        return sf.query_all(query)

    else:
        # Regular user: only their personal records (no averages)
        query = (
            f"SELECT Overall_Score__c, Element__c, Timestamp__c "
            f"FROM INSIGHT_Results__c "
            f"WHERE Contact_Email__c='{email}' "
            f"AND Element__c='{element_escaped}'"
        )
        return sf.query_all(query)


def get_all_avg_overall(org_input, sf, is_admin, access_level, email):
    """
    Retrieves all Overall_Score__c averages across all elements.
    Access-level: all org/site averages for all orgs.
    Admin: averages for the given org only.
    Regular users: their own records (no averages).
    """
    org_escaped = org_input.replace("'", "''")

    if access_level:
        query = (
            "SELECT Overall_Score__c, Element__c, Organization__c, Site__c "
            "FROM INSIGHT_Results__c "
            "WHERE ((Organization__c LIKE '%Average%') OR (Site__c LIKE '%Average%'))"
        )
        return sf.query_all(query)

    elif is_admin:
        query = (
            f"SELECT Overall_Score__c, Element__c, Contact_Name__c, Site__c "
            f"FROM INSIGHT_Results__c "
            f"WHERE Organization__c='{org_escaped}' "
            f"AND ((Organization__c LIKE '%Average%') OR (Site__c LIKE '%Average%'))"
        )
        return sf.query_all(query)

    else:
        query = (
            f"SELECT Overall_Score__c, Element__c "
            f"FROM INSIGHT_Results__c "
            f"WHERE Contact_Email__c='{email}'"
        )
        return sf.query_all(query)


def get_avg_records(org_input, sf, assessment, name, is_admin, access_level, email):
    """
    Retrieves average records (org/site averages) for a specific element.
    Access-level: all averages for all orgs.
    Admin: averages for their own org.
    Regular users: their own records only.
    """
    fields = assessment["fields"]
    opts = ", ".join(fields)
    org_escaped = org_input.replace("'", "''")
    element_escaped = name.replace("'", "''")

    if access_level:
        opts += ", Organization__c"
        query = (
            f"SELECT {opts} "
            f"FROM INSIGHT_Results__c "
            f"WHERE Element__c='{element_escaped}' "
            f"AND ((Organization__c LIKE '%Average%') OR (Site__c LIKE '%Average%'))"
        )
        return sf.query_all(query)

    elif is_admin:
        query = (
            f"SELECT {opts} "
            f"FROM INSIGHT_Results__c "
            f"WHERE Organization__c='{org_escaped}' "
            f"AND Element__c='{element_escaped}' "
            f"AND ((Organization__c LIKE '%Average%') OR (Site__c LIKE '%Average%'))"
        )
        return sf.query_all(query)

    else:
        query = (
            f"SELECT {opts} "
            f"FROM INSIGHT_Results__c "
            f"WHERE Contact_Email__c='{email}' "
            f"AND Element__c='{element_escaped}'"
        )
        return sf.query_all(query)


# results = get_avg_records("Nat Testing", create_sf(), ASSESSMENTS["Program Management"], "Program Management", True, True, "nat.howard@oregonask.org")


# st.write(results)
# st.write(pd.DataFrame.from_dict(results["records"]))