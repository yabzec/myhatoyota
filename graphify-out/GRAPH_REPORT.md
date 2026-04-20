# Graph Report - .  (2026-04-20)

## Corpus Check
- 106 files · ~51,143 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1057 nodes · 4022 edges · 35 communities detected
- Extraction: 31% EXTRACTED · 69% INFERRED · 0% AMBIGUOUS · INFERRED: 2778 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]

## God Nodes (most connected - your core abstractions)
1. `CustomAPIBaseModel` - 235 edges
2. `StatusModel` - 195 edges
3. `CustomEndpointBaseModel` - 158 edges
4. `ElectricResponseModel` - 100 edges
5. `Api` - 87 edges
6. `ToyotaDataUpdateCoordinator` - 80 edges
7. `ToyotaApiError` - 73 edges
8. `RemoteStatusResponseModel` - 70 edges
9. `ClimateSettingsModel` - 69 edges
10. `CommandType` - 68 edges

## Surprising Connections (you probably didn't know these)
- `ToyotaBaseEntity Base Class` --references--> `DOMAIN Constant`  [EXTRACTED]
  base_entity.py → const.py
- `ToyotaDeviceTracker` --uses--> `ToyotaDataUpdateCoordinator`  [INFERRED]
  device_tracker.py → coordinator.py
- `ToyotaBaseLock` --uses--> `CommandType`  [INFERRED]
  lock.py → pytoyoda-src/pytoyoda/models/endpoints/command.py
- `ToyotaDoorsLock` --uses--> `CommandType`  [INFERRED]
  lock.py → pytoyoda-src/pytoyoda/models/endpoints/command.py
- `ToyotaTrunkLock` --uses--> `CommandType`  [INFERRED]
  lock.py → pytoyoda-src/pytoyoda/models/endpoints/command.py

## Hyperedges (group relationships)
- **Core Triad: every platform depends on Coordinator, BaseEntity, and CoordinatorData** — architecture_toyota_data_update_coordinator, architecture_toyota_base_entity, architecture_toyota_coordinator_data [EXTRACTED 1.00]
- **Platform Pattern: Description dataclass + tuple + entity class + async_setup_entry** — style_description_dataclasses, style_value_fn_lambdas, style_entity_classes, style_async_setup_entry [EXTRACTED 0.95]
- **Translation sync: strings.json + en.json + it.json must stay in sync** — commands_translations, commands_adding_new_entity [EXTRACTED 1.00]

## Communities

### Community 0 - "Community 0"
Cohesion: 0.03
Nodes (140): Latest Location of car., Initialize Location model.          Args:             location (LocationResponse, Latitude.          Returns:             float: Latest latitude or None. _Not alw, Longitude.          Returns:             float: Latest longitude or None. _Not a, Timestamp.          Returns:             datetime: Position aquired timestamp or, State.          Returns:             str: The state of the position or None. _No, closed(), Door (+132 more)

### Community 1 - "Community 1"
Cohesion: 0.04
Nodes (120): AccountModel, AccountResponseModel, _AdditionalAttributesModel, _CustomerModel, _EmailModel, _PhoneNumberModel, Toyota Connected Services API - Account Models., Model for terms and conditions activity. (+112 more)

### Community 2 - "Community 2"
Cohesion: 0.04
Nodes (88): MyT, Client for connecting to Toyota Connected Services.  A client for connecting to, Toyota Connected Services client.      Provides a simple interface to access Toy, Initialize the Toyota Connected Services client.          Args:             user, Perform initial login to Toyota Connected Services.          This should be call, Retrieve all vehicles associated with the account.          Returns:, ToyotaConfigFlow, data_folder() (+80 more)

### Community 3 - "Community 3"
Cohesion: 0.09
Nodes (78): Api, Toyota Connected Services API., Create standard headers for API requests.          Returns:             Dictiona, Set a nickname/alias for a vehicle.          Args:             alias: New nickna, Get a list of vehicles registered with the Toyota account.          Returns:, Get the last known location of a vehicle.          Only updates when car is park, Get the latest health status of a vehicle.          Includes engine oil quantity, Get general information about a vehicle.          Args:             vin: Vehicle (+70 more)

### Community 4 - "Community 4"
Cohesion: 0.03
Nodes (78): ToyotaBaseEntity Base Class, Base entity class shared across all Toyota platforms., Common base for all Toyota entities., Store the VIN for use in unique_id and device_info., Return device info that groups all entities under one device per VIN., BINARY_SENSOR_DESCRIPTIONS Tuple, ToyotaBinarySensor, ToyotaBinarySensorEntityDescription (+70 more)

### Community 5 - "Community 5"
Cohesion: 0.05
Nodes (73): BaseModel, convert_distance(), convert_to_km(), convert_to_liter_per_100_miles(), convert_to_miles(), convert_to_mpg(), Conversion utilities for distance and fuel efficiency., Convert miles to kilometers.      Args:         miles: Distance in miles      Re (+65 more)

### Community 6 - "Community 6"
Cohesion: 0.1
Nodes (71): ACOperations, ACParameters, available(), category_display_name(), category_name(), ClimateOptions, ClimateOptionStatus, ClimateSettingsModel (+63 more)

### Community 7 - "Community 7"
Cohesion: 0.19
Nodes (62): ClimateSettings, ClimateStatus, CommandType, List of possible remote commands.      Each value represents a specific command, DataUpdateCoordinator for the Toyota Custom integration., Call an async method and return None on any exception., All data fetched for a single vehicle., Coordinator that polls a single Toyota vehicle every UPDATE_INTERVAL_MINUTES. (+54 more)

### Community 8 - "Community 8"
Cohesion: 0.04
Nodes (51): base_entity.py Module, Climate Endpoints Stripped at Init, coordinator.py Module, Core Triad (Coordinator + BaseEntity + CoordinatorData), Door Status Unavailable (empty sections), entry.runtime_data Storage Pattern, __init__.py Module, Lock Post-Command Refresh (20s delay) (+43 more)

### Community 9 - "Community 9"
Cohesion: 0.09
Nodes (33): Generate string representation based on properties., main(), Simulate coordinator data fetch to expose silent failures., Mirror _safe_fetch but print exceptions instead of swallowing them., _row(), safe_fetch(), _make_dashboard(), _make_electric_stub() (+25 more)

### Community 10 - "Community 10"
Cohesion: 0.13
Nodes (19): Toyota Connected Services API - Remote Commands Models., Enum, censor_all(), censor_string(), censor_value(), format_httpx_response_json(), get_sensitive_data_type(), Utilities for manipulating returns for log output tasks. (+11 more)

### Community 11 - "Community 11"
Cohesion: 0.24
Nodes (10): customer_created_record(), notes(), odometer(), operations_performed(), Toyota Connected Services API - Service History Models., ro_number(), service_category(), service_date() (+2 more)

### Community 12 - "Community 12"
Cohesion: 0.27
Nodes (7): format_odometer(), Formatters for instrument data., Format odometer information from a list to a dict.      Args:         raw: A lis, Test Formatter Utils., test_format_odometer_edge_cases(), test_format_odometer_error_cases(), test_format_odometer_happy_path()

### Community 13 - "Community 13"
Cohesion: 0.28
Nodes (6): add_with_none(), generate_hmac_sha256(), Helper functions for numeric operations with None handling., Add two items safely, handling None values.      If either value is None, return, Generate an HMAC-SHA256 hash for the given message using the key.      Args:, test_is_valid_locale_happy_path()

### Community 14 - "Community 14"
Cohesion: 0.31
Nodes (6): is_valid_locale(), Utilities for validating locale strings., Check if the provided locale string is valid according to language standards., test_is_valid_locale_edge_cases(), test_is_valid_locale_error_cases(), test_is_valid_locale_happy_path()

### Community 15 - "Community 15"
Cohesion: 0.48
Nodes (5): category(), message(), Models for vehicle notifications., read(), type()

### Community 16 - "Community 16"
Cohesion: 0.53
Nodes (4): latitude(), longitude(), state(), timestamp()

### Community 17 - "Community 17"
Cohesion: 0.5
Nodes (3): Pytest tests for pytoyoda.__init__., Ensure the imported module is the expected one., test_imports()

### Community 18 - "Community 18"
Cohesion: 0.67
Nodes (1): Toyota Connected Services API constants.

### Community 19 - "Community 19"
Cohesion: 1.0
Nodes (1): List of endpoints that sould be tested by 'endpoint_tester.py'.

### Community 20 - "Community 20"
Cohesion: 1.0
Nodes (2): Adding a New Entity Workflow, Translations (strings.json + en.json + it.json)

### Community 21 - "Community 21"
Cohesion: 1.0
Nodes (1): PLATFORMS List

### Community 22 - "Community 22"
Cohesion: 1.0
Nodes (1): UPDATE_INTERVAL_MINUTES Constant

### Community 23 - "Community 23"
Cohesion: 1.0
Nodes (1): Fetch all data from the Toyota API.

### Community 24 - "Community 24"
Cohesion: 1.0
Nodes (1): Call an async method and return None on any exception.

### Community 25 - "Community 25"
Cohesion: 1.0
Nodes (1): Config flow for Toyota Custom integration.

### Community 26 - "Community 26"
Cohesion: 1.0
Nodes (1): Handle a config flow for Toyota Custom.

### Community 27 - "Community 27"
Cohesion: 1.0
Nodes (1): Handle the initial step.

### Community 28 - "Community 28"
Cohesion: 1.0
Nodes (1): const.py Module

### Community 29 - "Community 29"
Cohesion: 1.0
Nodes (1): config_flow.py Module

### Community 30 - "Community 30"
Cohesion: 1.0
Nodes (1): API Inspection Tools (tools/)

### Community 31 - "Community 31"
Cohesion: 1.0
Nodes (1): Type Annotation Rules (Python 3.12)

### Community 32 - "Community 32"
Cohesion: 1.0
Nodes (1): Error Handling Tiers (hard/soft/silent)

### Community 33 - "Community 33"
Cohesion: 1.0
Nodes (1): Logging Rules (%s style, no INFO)

### Community 34 - "Community 34"
Cohesion: 1.0
Nodes (1): PARALLEL_UPDATES = 0 Constant

## Knowledge Gaps
- **165 isolated node(s):** `PLATFORMS List`, `CONF_EMAIL Constant`, `CONF_PASSWORD Constant`, `UPDATE_INTERVAL_MINUTES Constant`, `MANUFACTURER Constant` (+160 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 19`** (2 nodes): `List of endpoints that sould be tested by 'endpoint_tester.py'.`, `endpoints_to_test.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 20`** (2 nodes): `Adding a New Entity Workflow`, `Translations (strings.json + en.json + it.json)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 21`** (1 nodes): `PLATFORMS List`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (1 nodes): `UPDATE_INTERVAL_MINUTES Constant`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 23`** (1 nodes): `Fetch all data from the Toyota API.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 24`** (1 nodes): `Call an async method and return None on any exception.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 25`** (1 nodes): `Config flow for Toyota Custom integration.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 26`** (1 nodes): `Handle a config flow for Toyota Custom.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 27`** (1 nodes): `Handle the initial step.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 28`** (1 nodes): `const.py Module`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 29`** (1 nodes): `config_flow.py Module`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 30`** (1 nodes): `API Inspection Tools (tools/)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (1 nodes): `Type Annotation Rules (Python 3.12)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (1 nodes): `Error Handling Tiers (hard/soft/silent)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 33`** (1 nodes): `Logging Rules (%s style, no INFO)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (1 nodes): `PARALLEL_UPDATES = 0 Constant`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `CustomAPIBaseModel` connect `Community 0` to `Community 1`, `Community 3`, `Community 5`, `Community 6`, `Community 7`, `Community 9`, `Community 11`, `Community 15`?**
  _High betweenness centrality (0.216) - this node is a cross-community bridge._
- **Why does `StatusModel` connect `Community 1` to `Community 0`, `Community 3`, `Community 6`, `Community 7`, `Community 11`?**
  _High betweenness centrality (0.165) - this node is a cross-community bridge._
- **Why does `Vehicle` connect `Community 7` to `Community 0`, `Community 1`, `Community 2`, `Community 3`, `Community 4`, `Community 9`?**
  _High betweenness centrality (0.162) - this node is a cross-community bridge._
- **Are the 229 inferred relationships involving `CustomAPIBaseModel` (e.g. with `StatusHelper` and `Door`) actually correct?**
  _`CustomAPIBaseModel` has 229 INFERRED edges - model-reasoned connections that need verification._
- **Are the 191 inferred relationships involving `StatusModel` (e.g. with `Api` and `Toyota Connected Services API.`) actually correct?**
  _`StatusModel` has 191 INFERRED edges - model-reasoned connections that need verification._
- **Are the 153 inferred relationships involving `CustomEndpointBaseModel` (e.g. with `_TranslationModel` and `_CapabilitiesModel`) actually correct?**
  _`CustomEndpointBaseModel` has 153 INFERRED edges - model-reasoned connections that need verification._
- **Are the 96 inferred relationships involving `ElectricResponseModel` (e.g. with `Api` and `Toyota Connected Services API.`) actually correct?**
  _`ElectricResponseModel` has 96 INFERRED edges - model-reasoned connections that need verification._