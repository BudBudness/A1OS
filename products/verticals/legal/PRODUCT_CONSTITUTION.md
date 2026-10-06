# Barya, Byamugisha & Co. Advocates — Internal Legal Practice Platform

## Product identity
- Customer: M/S Barya, Byamugisha & Co. Advocates
- Internal A1OS identifier: legal-os
- Customer-facing name: Barya, Byamugisha & Co. Advocates — Internal Legal Practice Platform
- Purpose: governed internal practice-management system.

## Operating model
The platform is the firm's internal system of record for clients, matters, parties, tasks, deadlines, hearings, documents, evidence, fees, payments and audit history.

## Users and roles
- Partner: firm-wide oversight and approval authority.
- Advocate: assigned-matter work, legal work product and client communication.
- Clerk: matter administration, filing/deadline preparation and evidence/document handling within assigned matters.
- Finance: billing, invoices, receipts and payment records.
- Administrator: user/matter administration without legal-work authority.
- Client: optional future portal role, restricted to explicitly shared matter information.

## Matter lifecycle
Intake → conflict check → matter opening → assignment → active work → deadlines/hearings → documents/evidence → billing → closure → archive.

## Core domains
Clients, matters, parties, litigation, documents, evidence, legal research, calendar/diary, tasks, billing, payments, audit, users/roles.

## Security
Matter-level confidentiality is mandatory. Access is deny-by-default and granted by firm role plus matter assignment. Sensitive records are never exposed through public endpoints. AI cannot authorize access or execute consequential actions.

## External systems
ULII is a research source/integration boundary. ECCMIS and other court systems are external connectors. The platform does not impersonate or replace external government systems.

## AI boundary
AI may summarize, classify, search, draft, extract and recommend. A1OS governance controls authorization, persistence, security, workflow execution and auditability.

## Product boundary
This product is internal practice management, not an autonomous lawyer and not a substitute for professional legal judgment.

## Definition of done
Production deployment, authenticated access, RLS-enforced matter confidentiality, real persistence, core matter workflow, document/evidence metadata, tasks/deadlines, billing records, audit trail, integration boundaries, automated tests, CI, and successful production E2E verification.
