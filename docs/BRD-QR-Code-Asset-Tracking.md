# Business Requirements Document — QR Code Asset Tracking

## Executive Summary

The company currently tracks all physical assets using paper records and logbooks, with assets identified by serial number. This manual process makes it difficult to quickly locate assets, track their movement, or perform audits. The business requires a QR code-based system that allows employees to scan an asset’s QR code to view its basic details and update its location when moved. The system will be owned by Facilities / Office Management and will cover approximately 100–500 assets across 1–5 locations.

## Business Context

The company maintains a variety of physical assets including IT equipment, office furniture, and fixtures. Asset records are kept on paper, and there is no automated way to determine an asset’s current location or movement history. As the company grows, this manual approach becomes increasingly inefficient and error-prone.

## Problem Statement

Paper-based asset tracking is slow, prone to data loss, and does not support real-time location visibility. When assets are moved, the paper records are often not updated promptly or at all, leading to misplaced assets, difficulty during audits, and wasted time searching for equipment.

## Business Objectives

1. Enable any employee to quickly view an asset’s basic details by scanning a QR code.
2. Allow employees to update an asset’s location immediately when it is moved.
3. Reduce time spent on physical inventory audits by at least 50%.
4. Eliminate reliance on paper logbooks for day-to-day asset tracking.

## Stakeholders

| Stakeholder | Role |
|-------------|------|
| Facilities / Office Management | Primary owner and administrator of the system |
| All employees | Users who scan QR codes and update asset locations |
| Finance / Accounting | Secondary stakeholder for audit and asset valuation |
| IT Department | May assist with initial setup and integration |

## Current Process

1. When a new asset arrives, its serial number and basic details are handwritten into a paper logbook.
2. The asset is placed in a location (e.g., office, floor, room).
3. When the asset is moved, the move is supposed to be noted in the logbook, but this often is forgotten or delayed.
4. During audits, staff manually walk through locations, compare assets to the logbook, and note discrepancies.
5. Finding a specific asset requires searching through paper records or physically walking the premises.

## Proposed Process

1. Each asset is assigned a unique QR code label that encodes a unique asset ID.
2. The QR code is affixed to the asset.
3. An asset database is created (initially populated from paper records) containing: asset name, category, serial number, current location, and unique asset ID.
4. When an employee scans the QR code using a mobile device or scanner, they see the asset’s basic details.
5. If the asset is moved, the employee scans the QR code at the new location and updates the location in the system themselves.
6. Facilities / Office Management can run reports and conduct audits using the digital system.
7. Paper logbooks are phased out.

## Scope

### In Scope

- QR code generation and printing for all existing and new assets (100–500 assets)
- A digital asset database storing asset name, category, serial number, location, and unique asset ID
- A scanning interface (mobile-friendly) that displays basic asset details
- Location update capability triggered by scanning at a new location
- Location history tracking (optional but recommended)
- Reporting for audit and inventory purposes
- Role-based access: Facilities / Office Management as administrators, all employees as users

### Out of Scope

- Integration with existing ERP or accounting software (future phase)
- Barcode or RFID alternatives
- Maintenance history tracking (not requested)
- Employee check-in/check-out of assets
- Automated location detection (e.g., Bluetooth beacons)
- Mobile app development — scanning can be done via web-based interface or existing device camera

## Functional Requirements

| ID | Requirement |
|----|-------------|
| FR1 | The system shall generate a unique QR code for each asset. |
| FR2 | The QR code shall encode a unique asset ID that maps to the asset record in the database. |
| FR3 | The system shall allow an administrator (Facilities) to add, edit, and delete asset records. |
| FR4 | The system shall display the following asset details when a QR code is scanned: asset name, category, serial number, current location. |
| FR5 | The system shall allow any employee to update the asset’s location by scanning the QR code and selecting or confirming the new location from a predefined list. |
| FR6 | The system shall record a timestamp and previous location when a location update occurs (location history). |
| FR7 | The system shall provide a search/filter function for administrators to find assets by name, serial number, category, or location. |
| FR8 | The system shall support exporting asset data to a CSV file for audit purposes. |

## Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR1 | The scanning interface shall load asset details within 2 seconds on a standard mobile device. |
| NFR2 | The system shall support up to 500 assets and 5 locations without performance degradation. |
| NFR3 | The system shall be accessible via standard web browsers on desktop and mobile devices. |
| NFR4 | Data shall be backed up daily. |
| NFR5 | The system shall require authentication for any data modification (location updates, asset edits). |

## Business Rules

| ID | Rule |
|----|------|
| BR1 | Each asset must have a unique asset ID. |
| BR2 | An asset’s location can only be one of the predefined locations (1–5). |
| BR3 | Only Facilities / Office Management can add or delete assets. |
| BR4 | Any authenticated employee can update an asset’s location. |
| BR5 | Location updates must include a timestamp and the previous location. |

## Reports & Dashboards

| Report | Description |
|--------|-------------|
| Asset Inventory List | Complete list of all assets with current location and details |
| Location Summary | Count of assets per location |
| Movement History | For a given asset, show all location changes with dates |
| Audit Report | List of assets with last location update date, highlighting assets not updated in >90 days |

## Integration Requirements

None in the initial scope. The system will be standalone.

## Risks

| Risk | Mitigation |
|------|------------|
| QR code labels may become damaged or fall off | Use durable, adhesive labels; include a process for re-labeling |
| Employees may forget to scan when moving assets | Provide training and periodic reminders; management reinforcement |
| Initial data entry from paper records may contain errors | Validate data with a physical audit before going live |
| System adoption may be low | Keep scanning interface simple; demonstrate time savings |

## Assumptions

- Employees have access to a smartphone or device with a camera and web browser.
- The company has 100–500 assets across 1–5 locations.
- Facilities / Office Management will administer the system.
- The existing paper records contain sufficient data to populate the initial database.
- QR codes will be printed on standard label stock using an existing printer.

## Dependencies

- Availability of a QR code generator (can be open-source or built-in library).
- A web server or cloud hosting environment to run the application.
- Label printer and adhesive label sheets for QR code printing.

## Success Criteria

| Criterion | Target |
|-----------|--------|
| 100% of existing assets labeled with QR codes within 2 weeks of go-live | Yes |
| At least 90% of asset moves are updated via QR scan within 1 day of move | Yes |
| Audit time reduced by 50% compared to paper-based process | Yes |
| Zero reliance on paper logbooks for day-to-day tracking after 1 month | Yes |

## Open Decisions

- Whether to use a web-based scanning interface or a dedicated mobile app (web preferred for simplicity).
- Whether to allow scanning without authentication for view-only (likely yes) but require authentication for updates.
- Exact list of predefined locations (to be confirmed by Facilities).

## Glossary

| Term | Definition |
|------|------------|
| Asset | Any physical item owned by the company (IT equipment, furniture, fixtures, etc.) |
| QR Code | Quick Response code — a 2D barcode that can be scanned by a camera |
| Asset ID | A unique identifier assigned to each asset for database lookup |
| Location | A physical area (e.g., "3rd Floor — Room 301", "Warehouse A") |
| Facilities / Office Management | The department responsible for managing physical assets and office space |
