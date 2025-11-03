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
        results = sf.query_all(f"SELECT {opts} FROM INSIGHT_Results__c WHERE Element__c='{name}'")
        return results
    if is_admin:
        results = sf.query_all(f"SELECT {opts} FROM INSIGHT_Results__c WHERE Organization__c='{org_escaped}' AND Element__c='{name}'")
    else:
        results = sf.query_all(f"SELECT {opts} FROM INSIGHT_Results__c WHERE Contact_Email__c='{email}' AND Element__c='{name}'")
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
        results = sf.query_all(f"SELECT Overall_Score__c, Organization__c FROM INSIGHT_Results__c WHERE Element__c='{name}'")
        return results
    if is_admin:
        results = sf.query_all(f"SELECT Overall_Score__c, Contact_Name__c FROM INSIGHT_Results__c WHERE Organization__c='{org_escaped}' AND Element__c='{name}'")
    else:
        results = sf.query_all(f"SELECT Overall_Score__c FROM INSIGHT_Results__c WHERE Contact_Email__c='{email}' AND Element__c='{name}'")
    return results

def get_all_overall(org_input, sf, is_admin, access_level, email):
    """
    get_all_overall(org_input, sf, is_admin, access_level, email)
    """
    org_escaped = org_input.replace("'", "\'")
    if access_level:
        results = sf.query_all(f"SELECT Overall_Score__c, Element__c, Organization__c FROM INSIGHT_Results__c")
        return results
    if is_admin:
        results = sf.query_all(f"SELECT Overall_Score__c, Element__c, Contact_Name__c FROM INSIGHT_Results__c WHERE Organization__c='{org_escaped}'")
    else:
        results = sf.query_all(f"SELECT Overall_Score__c, Element__c FROM INSIGHT_Results__c WHERE Contact_Email__c='{email}'")
    return results

# results = get_org_records("Nat Testing", create_sf(), ASSESSMENTS["Program Management"], "Program Management", True, False, "nat.howard@oregonask.org")

# st.write(results)
# st.write(pd.DataFrame.from_dict(results["records"]))