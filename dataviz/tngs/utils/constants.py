from st_aggrid import JsCode

onFilterChanged = JsCode(
    """
function onFilterChanged(params) {
    console.log('onFilterChanged start');
    const filterState = params.api.getFilterModel();
    const filterStateStr = JSON.stringify(filterState);
    console.log('filterState captured in JS:', filterState);
    console.log('filterStateStr captured in JS:', filterStateStr);
    localStorage.setItem('filterStateStr', filterStateStr);  // Save filter state to localStorage
    console.log('onFilterChanged end');
}
"""
)


onFirstDataRendered = JsCode(
    """
function onFirstDataRendered(params) {
  console.log('onFirstDataRendered start');
  var filterStateStr = localStorage.getItem('filterStateStr');
  console.log('filterStateStr loaded:', filterStateStr);
  console.log('JSON parsed filterStateStr:', JSON.parse(filterStateStr));
  params.api.setFilterModel(JSON.parse(filterStateStr));

  console.log('onFirstDataRendered end');
}
"""
)


RETAIN_FILTER_STATE_OPTIONS = {
    "onFirstDataRendered": onFirstDataRendered,
    "onFilterChanged": onFilterChanged,
}

LICENSE_KEY = "[TRIAL]_this_{AG_Grid}_Enterprise_key_{AG-062754}_is_granted_for_evaluation_only___Use_in_production_is_not_permitted___Please_report_misuse_to_legal@ag-grid.com___For_help_with_purchasing_a_production_key_please_contact_info@ag-grid.com___You_are_granted_a_{Single_Application}_Developer_License_for_one_application_only___All_Front-End_JavaScript_developers_working_on_the_application_would_need_to_be_licensed___This_key_will_deactivate_on_{14 August 2024}____[v3]_[01]_MTcyMzU5MDAwMDAwMA==a5f0bef6477e9746662f8e0f46e475b7"

SAMPLE_DTYPE = {
    "sample_id": "int64",
    "sample_name": "string",
    "patient": "string",
    "sample_type": "string",
    "gender": "string",
    "hospital": "string",
    "department": "string",
    "age": "string",
    "age_float": "float64",
    "age_group": "string",
    "hospital_num": "string",
    "hosp_sampled": "string",
    "doctor": "string",
    "collect_time": "datetime64[ns]",
    "clinical_diagnosis": "string",
    "receive_time": "datetime64[ns]",
    "receive_trial_name": "string",
    "bednumber": "string",
    "number_of_detected_pathos": "Int64",
    "number_of_detected_drugresis": "Int64",
    "出具结果": "string",
}

SAMPLE_COLUMNS = [
    "sample_name",
    "sample_type",
    "gender",
    "age",
    "age_float",
    "age_group",
    "hospital",
    "department",
    "collect_time",
    "receive_time",
    "number_of_detected_pathos",
    "number_of_detected_drugresis",
    "出具结果",
    "clinical_diagnosis",
]

ETIOLOGY_DTYPE = {
    "sample_name": "string",
    "patho_name": "string",
    "amp_cov": "string",
    "patho_reads": "int64",
    "patho_RPK": "int64",
    "filter_flag": "string",
    "patho_pvalue": "float64",
    "patho_semiquant": "string",
    "patho_clincialevel": "string",
}

ETIOLOGY_COLUMNS = [
    "sample_name",
    "patho_name",
    "amp_cov",
    "patho_reads",
    "patho_RPK",
    "filter_flag",
    "patho_pvalue",
    "patho_semiquant",
    "patho_cliniclevel",
]

DRUGRESIS_DTYPE = {
    "sample_name": "string",
    "drug_resistance_id": "int64",
    "trial_id": "int64",
    "is_show": "int64",
    "resis_DrugLog": "string",
    "resis_DrugName": "string",
    "resis_MutLog": "string",
    "resis_RawDep": "string",
    "resis_mut": "string",
    "resis_mut_ratio": "string",
    "resis_name": "string",
    "resis_rpk": "string",
    "resis_gene": "string",
    "patho_name": "string",
    "en_short": "string",
    "resis_ifreport": "string",
}

DRUGRESIS_COLUMNS = [
    "sample_name",
    "drug_resistance_id",
    "trial_id",
    "is_show",
    "resis_DrugLog",
    "resis_DrugName",
    "resis_MutLog",
    "resis_RawDep",
    "resis_mut",
    "resis_mut_ratio",
    "resis_name",
    "resis_rpk",
    "resis_gene",
    "patho_name",
    "en_short",
    "resis_ifreport",
]
