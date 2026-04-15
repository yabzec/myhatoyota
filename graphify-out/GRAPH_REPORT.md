# Graph Report - .  (2026-04-15)

## Corpus Check
- Corpus is ~3,741 words - fits in a single context window. You may not need a graph.

## Summary
- 150 nodes · 320 edges · 9 communities detected
- Extraction: 58% EXTRACTED · 42% INFERRED · 0% AMBIGUOUS · INFERRED: 133 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Base Entity Definitions|Base Entity Definitions]]
- [[_COMMUNITY_Lock Platform|Lock Platform]]
- [[_COMMUNITY_Sensor Platform|Sensor Platform]]
- [[_COMMUNITY_Core Setup & Constants|Core Setup & Constants]]
- [[_COMMUNITY_Cross-Platform Semantic Layer|Cross-Platform Semantic Layer]]
- [[_COMMUNITY_Binary Sensor Platform|Binary Sensor Platform]]
- [[_COMMUNITY_Integration Bootstrap|Integration Bootstrap]]
- [[_COMMUNITY_Config Flow|Config Flow]]
- [[_COMMUNITY_API Data Fetching|API Data Fetching]]

## God Nodes (most connected - your core abstractions)
1. `ToyotaDataUpdateCoordinator` - 63 edges
2. `ToyotaBaseEntity` - 53 edges
3. `ToyotaCoordinatorData` - 21 edges
4. `ToyotaBaseLock` - 11 edges
5. `ToyotaDataUpdateCoordinator` - 11 edges
6. `ToyotaDoorsLock` - 9 edges
7. `ToyotaTrunkLock` - 9 edges
8. `ToyotaForceRefreshButton` - 9 edges
9. `ToyotaBinarySensor` - 9 edges
10. `ToyotaSensorEntity` - 9 edges

## Surprising Connections (you probably didn't know these)
- `Toyota Custom integration setup.` --uses--> `ToyotaDataUpdateCoordinator`  [INFERRED]
  __init__.py → coordinator.py
- `Set up Toyota integration from a config entry.` --uses--> `ToyotaDataUpdateCoordinator`  [INFERRED]
  __init__.py → coordinator.py
- `Unload a Toyota config entry.` --uses--> `ToyotaDataUpdateCoordinator`  [INFERRED]
  __init__.py → coordinator.py
- `Base entity class shared across all Toyota platforms.` --uses--> `ToyotaDataUpdateCoordinator`  [INFERRED]
  base_entity.py → coordinator.py
- `ToyotaSensorEntityDescription` --semantically_similar_to--> `ToyotaBinarySensorEntityDescription`  [INFERRED] [semantically similar]
  sensor.py → binary_sensor.py

## Hyperedges (group relationships)
- **Entity-Coordinator-Data Polling Pattern** — base_entity_ToyotaBaseEntity, coordinator_ToyotaDataUpdateCoordinator, coordinator_ToyotaCoordinatorData [EXTRACTED 0.95]
- **HA Platform Setup via ConfigEntry Pattern** — init_ToyotaConfigEntry, init_async_setup_entry, const_PLATFORMS [EXTRACTED 0.95]
- **Lock Status Data Shared by Lock and BinarySensor Platforms** — lock_ToyotaDoorsLock, lock_ToyotaTrunkLock, binary_sensor_BINARY_SENSOR_DESCRIPTIONS [INFERRED 0.80]

## Communities

### Community 0 - "Base Entity Definitions"
Cohesion: 0.1
Nodes (32): Common base for all Toyota entities., Store the VIN for use in unique_id and device_info., Return device info that groups all entities under one device per VIN., ToyotaBaseEntity, Extends BinarySensorEntityDescription with a value_fn.      is_on=True means the, ToyotaBinarySensorEntityDescription, BinarySensorEntityDescription, async_setup_entry() (+24 more)

### Community 1 - "Lock Platform"
Cohesion: 0.1
Nodes (14): async_setup_entry(), Lock platform for Toyota Custom integration., Initialise the trunk lock., Set up Toyota lock entities from a config entry., Shared base for Toyota lock entities., Initialise base lock state., Send a command and refresh coordinator data., Lock/unlock all main doors. (+6 more)

### Community 2 - "Sensor Platform"
Cohesion: 0.15
Nodes (17): Return True when the door/window is open., All data fetched for a single vehicle., ToyotaCoordinatorData, async_setup_entry(), _make_summary_sensors(), Sensor platform for Toyota Custom integration., Build 6 sensors for a given summary period., A single Toyota sensor. (+9 more)

### Community 3 - "Core Setup & Constants"
Cohesion: 0.14
Nodes (8): Base entity class shared across all Toyota platforms., Button platform for Toyota Custom integration., Constants for the Toyota Custom integration., DataUpdateCoordinator for the Toyota Custom integration., Device tracker platform for Toyota Custom integration., async_unload_entry(), Toyota Custom integration setup., Unload a Toyota config entry.

### Community 4 - "Cross-Platform Semantic Layer"
Cohesion: 0.22
Nodes (19): ToyotaBaseEntity Base Class, BINARY_SENSOR_DESCRIPTIONS Tuple, ToyotaBinarySensor, ToyotaBinarySensorEntityDescription, ToyotaForceRefreshButton, DOMAIN Constant, MANUFACTURER Constant, MODEL Constant (+11 more)

### Community 5 - "Binary Sensor Platform"
Cohesion: 0.18
Nodes (9): async_setup_entry(), _closed_to_is_on(), Binary sensor platform for Toyota Custom integration., A single Toyota binary sensor., Initialise the binary sensor., Set up Toyota binary sensors from a config entry., Convert a pytoyoda 'closed' value to a binary sensor is_on value.      Returns T, ToyotaBinarySensor (+1 more)

### Community 6 - "Integration Bootstrap"
Cohesion: 0.47
Nodes (6): ToyotaConfigFlow, CONF_EMAIL Constant, CONF_PASSWORD Constant, PLATFORMS List, async_setup_entry(), Set up Toyota integration from a config entry.

### Community 7 - "Config Flow"
Cohesion: 0.33
Nodes (4): Config flow for Toyota Custom integration., Handle a config flow for Toyota Custom., Handle the initial step., ToyotaConfigFlow

### Community 8 - "API Data Fetching"
Cohesion: 0.5
Nodes (2): Fetch all data from the Toyota API., Call an async method and return None on any exception.

## Knowledge Gaps
- **15 isolated node(s):** `Constants for the Toyota Custom integration.`, `DataUpdateCoordinator for the Toyota Custom integration.`, `All data fetched for a single vehicle.`, `Coordinator that polls a single Toyota vehicle every UPDATE_INTERVAL_MINUTES.`, `Initialise the coordinator.` (+10 more)
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ToyotaDataUpdateCoordinator` connect `Base Entity Definitions` to `Lock Platform`, `Sensor Platform`, `Core Setup & Constants`, `Binary Sensor Platform`, `Integration Bootstrap`, `API Data Fetching`?**
  _High betweenness centrality (0.522) - this node is a cross-community bridge._
- **Why does `async_setup_entry()` connect `Integration Bootstrap` to `Base Entity Definitions`, `Core Setup & Constants`, `Cross-Platform Semantic Layer`?**
  _High betweenness centrality (0.270) - this node is a cross-community bridge._
- **Why does `ToyotaDataUpdateCoordinator` connect `Cross-Platform Semantic Layer` to `Integration Bootstrap`?**
  _High betweenness centrality (0.210) - this node is a cross-community bridge._
- **Are the 58 inferred relationships involving `ToyotaDataUpdateCoordinator` (e.g. with `ToyotaDeviceTracker` and `Device tracker platform for Toyota Custom integration.`) actually correct?**
  _`ToyotaDataUpdateCoordinator` has 58 INFERRED edges - model-reasoned connections that need verification._
- **Are the 50 inferred relationships involving `ToyotaBaseEntity` (e.g. with `ToyotaDeviceTracker` and `Device tracker platform for Toyota Custom integration.`) actually correct?**
  _`ToyotaBaseEntity` has 50 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `ToyotaCoordinatorData` (e.g. with `ToyotaBinarySensorEntityDescription` and `ToyotaBinarySensor`) actually correct?**
  _`ToyotaCoordinatorData` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `ToyotaBaseLock` (e.g. with `ToyotaBaseEntity` and `ToyotaDataUpdateCoordinator`) actually correct?**
  _`ToyotaBaseLock` has 2 INFERRED edges - model-reasoned connections that need verification._