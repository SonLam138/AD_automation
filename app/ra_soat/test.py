from app.ra_soat.file_loader import load_excel, validate_headers, normalize_email, extract_username, map_dataframe_to_source_users, map_row_to_source_user
from app.ra_soat.account_discovery import generate_search_keys
print(
    generate_search_keys("chienvm1")
)

df = load_excel("D:\\AD Automation\\app\\ra_soat\\HR_Offboard.xlsx")

print(df.columns.tolist())


validate_headers(df)
print("Header validation passed")

# Example of normalizing emails
df["Mail nội bộ"] = df["Mail nội bộ"].apply(normalize_email)
print("Email normalization completed")

# Example of extracting usernames
df["Username"] = df["Mail nội bộ"].apply(extract_username)
print("Username extraction completed")

print(df.head())

users = map_dataframe_to_source_users(df)

from app.ra_soat.account_discovery import (
    discover_users_and_build_requests,
)


requests, discovery_results = (
    discover_users_and_build_requests(
        users
    )
)

found_results = [
    result
    for result in discovery_results
    if result.found
]

not_found_results = [
    result
    for result in discovery_results
    if not result.found
]

print("=" * 80)
print("DISCOVERY COMPLETED")
print("=" * 80)

print(
    "Total source users:",
    len(users),
)

print(
    "Total search results:",
    len(discovery_results),
)

print(
    "Found related accounts:",
    len(found_results),
)

print(
    "Not found search keys:",
    len(not_found_results),
)

print(
    "Offboarding requests ready:",
    len(requests),
)

for request in requests:
    print(request.model_dump())
