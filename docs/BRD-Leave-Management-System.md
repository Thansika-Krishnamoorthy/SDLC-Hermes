# Business Requirements Document — Leave Management System

## Executive Summary
KovanLabs requires a centralized Leave Management System to replace the current paper-based and email-based leave request process. The system will handle the full lifecycle of employee leave—submission, approval, and tracking—across six leave types. A multi-level approval workflow (Manager → HR → Director) will be implemented, with Director approval required only for leave exceeding 5 consecutive days. Leave entitlements will be fixed annual allocations per leave type, with a carryover limit of 7 unused days per year. The system will provide leave usage trend reports for departmental and organizational analysis.

## Business Context
The company currently manages leave requests manually using paper forms and email. This process is inefficient, prone to errors, and lacks visibility into leave balances, approval status, and usage trends. A digital system is needed to streamline operations, enforce leave policies consistently, and provide accurate tracking.

## Problem Statement
Manual leave management leads to:
- Delays in request processing and approvals
- Difficulty tracking employee leave balances
- Inconsistent enforcement of leave policies
- Lack of visibility for managers, HR, and directors
- No historical data for leave usage analysis

## Business Objectives
1. Automate the leave request lifecycle from submission to final approval
2. Enforce consistent multi-level approval workflows
3. Provide accurate, real-time leave balance information
4. Enable leave usage reporting for data-driven decisions
5. Reduce administrative overhead for HR and managers

## Stakeholders
- **Employees** – submit leave requests and view balances
- **Managers** – approve leave requests for their direct reports
- **HR Department** – approve all leave requests and manage policies
- **Directors** – approve leave requests exceeding 5 consecutive days
- **Finance/Payroll** – may use leave data for payroll processing (future integration)

## Current Process
1. Employee fills out a paper leave form or sends an email to their manager.
2. Manager manually reviews and approves/rejects (no formal tracking).
3. HR is notified via email or paper handoff for final approval.
4. No automated balance deduction or tracking.
5. Leave records are stored in physical files or email threads.

## Proposed Process
1. Employee logs into the system and submits a leave request selecting leave type, dates, and reason.
2. System checks leave balance and validates eligibility.
3. Request is routed to the employee's manager for approval.
4. After manager approval, request is routed to HR for approval.
5. If the leave duration exceeds 5 consecutive days, the request is additionally routed to the Director for approval.
6. Upon final approval, the system automatically updates the employee's leave balance.
7. Employee and relevant stakeholders receive notifications at each stage.
8. Leave usage reports are available on demand.

## Scope

### In Scope
- Leave request submission by employees
- Multi-level approval workflow (Manager → HR → Director) with conditional Director approval
- Support for six leave types: Annual/Vacation, Sick, Personal/Casual, Maternity/Paternity, Compensatory/Overtime, Public Holidays
- Fixed annual leave entitlement per leave type
- Carryover of up to 7 unused days to the next year
- Real-time leave balance display
- Leave usage trend reports (by department, leave type, time period)
- Notifications for request status changes
- User roles: Employee, Manager, HR, Director

### Out of Scope
- Integration with payroll or HR systems (future phase)
- Leave encashment processing
- Public holiday calendar management (automatic handling only)
- Mobile application (web-based only initially)
- Timesheet or attendance tracking
- Leave policy configuration UI (policies will be configured during implementation)

## Functional Requirements
1. **Leave Request Submission** – Employees can submit leave requests specifying leave type, start date, end date, reason, and optional attachments.
2. **Leave Balance Display** – Employees and managers can view current leave balances for each leave type.
3. **Approval Workflow** – System routes requests through Manager → HR → Director (Director only if duration > 5 consecutive days).
4. **Approval/Rejection** – Authorized users can approve or reject requests with optional comments.
5. **Balance Deduction** – Upon final approval, system deducts the leave days from the employee's balance.
6. **Carryover Management** – At year-end, unused leave up to 7 days is carried forward; excess is forfeited.
7. **Notifications** – Email or in-system notifications for request submission, approval, rejection, and pending actions.
8. **Leave Calendar** – Managers and HR can view team/department leave calendars.
9. **Public Holidays** – System marks public holidays automatically (no request needed).

## Non-Functional Requirements
1. **Usability** – Intuitive interface requiring minimal training.
2. **Performance** – Leave requests should be processed and visible within 2 seconds.
3. **Availability** – System should be available during business hours with 99.5% uptime.
4. **Security** – Role-based access control; only authorized users can view or act on leave data.
5. **Audit Trail** – All actions (submission, approval, rejection) must be logged with timestamps and user IDs.
6. **Scalability** – Support up to 500 employees initially, with ability to scale.

## Business Rules
1. Leave requests must be submitted at least 1 day in advance (except sick leave, which can be submitted on the same day).
2. Director approval is required only when the total consecutive leave days exceed 5.
3. Unused leave at year-end: up to 7 days can be carried over; remaining days are forfeited.
4. Public holidays do not require a leave request and are not deducted from leave balances.
5. Employees cannot submit leave requests that exceed their available balance.
6. Leave requests cannot be modified after submission; employees must cancel and resubmit.

## Reports & Dashboards
- **Leave Usage Trends** – Report showing leave consumption by department, leave type, and time period (monthly, quarterly, annually). Accessible by HR and Directors.

## Integration Requirements
- No integration with external systems in the initial phase.

## Risks
1. **Policy Compliance** – Employees may attempt to bypass the 5-day Director approval rule by splitting leave into multiple requests. Mitigation: System should detect consecutive leave requests within a short gap and flag them.
2. **Adoption Resistance** – Employees accustomed to paper/email may resist the new system. Mitigation: Training and phased rollout.
3. **Data Accuracy** – Manual migration of existing leave balances may introduce errors. Mitigation: Data validation and reconciliation before go-live.

## Assumptions
1. All employees have access to a computer and company network.
2. Employee leave entitlements are defined and known for each leave type.
3. The company has an organizational hierarchy that maps employees to managers and directors.
4. Public holiday dates are provided by the company and will be configured during implementation.

## Dependencies
1. Employee master data (names, departments, reporting hierarchy) must be available.
2. Leave entitlement rules per leave type must be finalized by HR.

## Success Criteria
1. 100% of leave requests are submitted through the system within 3 months of launch.
2. Average approval time reduces by 50% compared to the current manual process.
3. HR reports zero discrepancies in leave balance tracking.
4. Leave usage trend reports are generated and used for quarterly planning.

## Open Decisions
1. Maximum number of consecutive days allowed per single leave request (if any, beyond Director approval threshold).
2. Whether sick leave requires supporting documentation (doctor's note) beyond a certain duration.
3. Notification delivery method (email only, or in-app + email).

## Glossary
- **Leave Balance** – The number of leave days an employee is entitled to and has remaining for a given leave type.
- **Carryover** – The transfer of unused leave days from one year to the next.
- **Multi-Level Approval** – An approval workflow where a request must be approved by multiple users in a defined sequence.
- **Consecutive Days** – The total number of calendar days from start date to end date of a leave request.
