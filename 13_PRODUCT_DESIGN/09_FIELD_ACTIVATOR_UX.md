# Phase 5 — POL Field Activator UX

## Product goal
Enable field staff to activate retailers/vendors, assist first orders and resolve follow-ups with minimal administrative burden.

## Core model
Field Activator is an operational actor, not the owner of the customer relationship. The customer remains attached to the canonical organization/membership model.

## Home
Show today's tasks first:
- assigned activations;
- pending follow-ups;
- assisted-order tasks;
- unresolved customer issues;
- completion status.

## Retailer activation
Flow:
`Find/create prospect → verify basic business context → consent → create/associate organization → membership → profile/persona → first assisted action → success receipt`.

Avoid long forms. Reuse previously captured data where valid.

## Assisted order
Field user should be able to:
- select retailer context;
- search catalog;
- add quantities;
- review allocation/constraints;
- submit only through canonical checkout/application boundary.

The app must not bypass server-side inventory, MOQ, price or authorization rules.

## Follow-up
Every task has:
- status;
- due time/date;
- next action;
- notes/evidence;
- outcome.

## Offline / weak network
Design for interrupted connectivity in field conditions:
- clear unsent state;
- retry;
- no duplicate submission;
- visible last-synced context.

Actual offline-write semantics are a backend/architecture decision and must not be simulated as guaranteed before implemented.
