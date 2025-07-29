Fixed the get search results in v0.1.25

Call app service is broken in both SDKs (only Apps, not remote page), test:
```python

records = [{'entity_id': 'AAvB/9hvPr4p8VvLjz9oggAAAAAAAAAAAAAAAAAAAADDDhlixyb4ZM8NMN8vGeHG', 'entity_type': 'person', 'entity_label': 'Giovanni Orlando ', 'age': None, 'blood_type': None, 'build': None, 'citizenship': None, 'city_of_birth': None, 'complexion': None, 'country_of_birth': None, 'date_of_birth': '1971-12-01', 'date_of_death': None, 'description': None, 'distinguishing_marks': None, 'first_name': 'Giovanni', 'gender': 'male', 'handedness': None, 'height': None, 'last_name': 'Orlando', 'main_language': None, 'middle_name': '', 'os_concept': 'person', 'os_content_size': None, 'os_created_at': None, 'os_created_by': None, 'os_deleted_at': None, 'os_deleted_by': None, 'os_entity_uid': 'AAvB/9hvPr4p8VvLjz9oggAAAAAAAAAAAAAAAAAAAADDDhlixyb4ZM8NMN8vGeHG', 'os_hidden_at': None, 'os_hidden_by': None, 'os_icon': None, 'os_last_updated_at': None, 'os_last_updated_by': None, 'os_textsearchfield': None, 'os_workspace': None, 'residence_address': 'E  27 ST 1277', 'residence_city': 'New York City', 'residence_country': 'United States', 'source_name': None, 'speaking_accent': None, 'weight': None}]

if st.button("Call EBA using old SDK"):
    from streamlit_octostar_research.desktop import call_app_service
    call_app_service("open_eba_from_only_this_file",
        records=records)

if st.button("Call EBA using new SDK"):
    from octostar_streamlit.desktop import call_app_service
    from octostar_streamlit.core.desktop.params import CallAppServiceParams
    call_app_service(params=CallAppServiceParams(service="open_eba_from_only_this_file", context={"records": records}, options=None))

```

poetry publish -vv -p pypi-AgEIcHlwaS5vcmcCJDY4Mjc0ZWY3LWNmYTMtNDBlMy1hMjIwLTc1NWY1MjFhNjhlMAACGlsxLFsib2N0b3N0YXItc3RyZWFtbGl0Il1dAAIsWzIsWyI4OWJhNTNkNy0wMWQyLTRhZmEtOTE3NS03MDBhOGM5ZGYyY2EiXV0AAAYgSB2V5eM5aRGoOjrh2vzFyhLZ-thUNp4duhG7Yb7M4CY -u "__token__" --no-interaction