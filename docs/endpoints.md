# TextVerified API v2 endpoint coverage

This manifest is generated from `api-v2.openapi.json` fetched from the official documentation on 2026-09-30. The MCP tool `textverified_request` exposes every path below.

## Rentals

- `Rentals`
- `Rentals / Rental Billing Cycle Upgrades`
- `Rentals / Renewable Rentals`
- `Rentals / Non-Renewable Rentals`

## All paths

| Method | Path | Operation | Summary |
|---|---|---|---|
| `POST` | `/api/pub/v2/auth` | `` | Generate Bearer Token |
| `GET` | `/api/pub/v2/account/me` | `GetAccountExpandedPublic` | Get Account Details |
| `GET` | `/api/pub/v2/area-codes` | `ListAdvertisedAreaCodesPublic` | Area Codes List |
| `GET` | `/api/pub/v2/services` | `ListAdvertisedTargetsPublic` | Service List |
| `POST` | `/api/pub/v2/inventory/rentals` | `CheckRentalInventoryPublic` | Rental Inventory |
| `POST` | `/api/pub/v2/inventory/verifications` | `CheckVerificationInventoryPublic` | Verification Inventory |
| `POST` | `/api/pub/v2/pricing/rentals` | `PriceCheckRentalPublic` | Rental Pricing |
| `POST` | `/api/pub/v2/pricing/verifications` | `PriceCheckVerificationPublic` | Verification Pricing |
| `GET` | `/api/pub/v2/sales/{id}` | `GetReservationSaleExpandedPublic` | Get Reservation Sale Details |
| `GET` | `/api/pub/v2/sales` | `` | List Reservation Sales |
| `GET` | `/api/pub/v2/billing-cycles/{id}` | `GetBillingCyclePublic` | Get Billing Cycle Details |
| `POST` | `/api/pub/v2/billing-cycles/{id}` | `UpdateBillingCyclePublic` | Updating a Billing Cycle |
| `GET` | `/api/pub/v2/billing-cycles/{id}/invoices` | `ListBillingCycleInvoicesPublic` | Get Billing Cycle Invoices |
| `GET` | `/api/pub/v2/billing-cycles` | `ListBillingCyclesPublic` | List Billing Cycles |
| `POST` | `/api/pub/v2/billing-cycles/{id}/next-invoice` | `GenerateNextBillingCycleRenewableInvoicePublic` | Preview Billing Cycle Invoice |
| `POST` | `/api/pub/v2/billing-cycles/{id}/renew` | `RenewBillingCyclePublic` | Renew Billing Cycle |
| `GET` | `/api/pub/v2/backorders/{id}` | `GetBackOrderReservationExpandedPublic` | Get Back Order Reservation Detail |
| `GET` | `/api/pub/v2/reservations/{id}` | `GetLineReservationExpandedPublic` | Line Reservation Details |
| `GET` | `/api/pub/v2/reservations/{id}/health` | `GetReservationLineHealthPublic` | Reservation Health Check |
| `POST` | `/api/pub/v2/verifications` | `` | Create Verification |
| `GET` | `/api/pub/v2/verifications` | `ListVerificationsPublic` | List Verifications |
| `GET` | `/api/pub/v2/verifications/{id}` | `GetVerificationExpandedPublic` | Verification Details |
| `POST` | `/api/pub/v2/verifications/{id}/cancel` | `CancelVerificationPublic` | Cancel Verification |
| `POST` | `/api/pub/v2/verifications/{id}/reactivate` | `ReactivateVerificationPublic` | Reactivate Verification |
| `POST` | `/api/pub/v2/verifications/{id}/report` | `ReportVerificationPublic` | Report Verification |
| `POST` | `/api/pub/v2/verifications/{id}/reuse` | `ReuseVerificationPublic` | Reuse Verification |
| `POST` | `/api/pub/v2/reservations/rental` | `` | Create New Rental |
| `GET` | `/api/pub/v2/reservations/rental/{id}/reactivate` | `GetRentalReactivationCostPublic` | Rental Reactivation Cost |
| `POST` | `/api/pub/v2/reservations/rental/{id}/reactivate` | `ReactivateRentalPublic` | Reactivate Rental |
| `GET` | `/api/pub/v2/reservations/rental/{id}/user-notes` | `GetRentalUserNotesPublic` | Get a Rental's User Notes |
| `POST` | `/api/pub/v2/reservations/rental/tags/search` | `SearchRentalTagsPublic` | Search Rental Tags |
| `GET` | `/api/pub/v2/reservations/rental/{id}/billing-cycle-upgrade-options` | `ListRentalBillingCycleUpgradeOptionsPublic` | List Rental Billing Cycle Upgrade Options |
| `POST` | `/api/pub/v2/reservations/rental/{id}/billing-cycle-upgrade` | `ScheduleRentalBillingCycleUpgradePublic` | Schedule Rental Billing Cycle Upgrade |
| `GET` | `/api/pub/v2/reservations/rental/{id}/billing-cycle-upgrade` | `GetPendingRentalBillingCycleUpgradePublic` | Get Pending Rental Billing Cycle Upgrade |
| `DELETE` | `/api/pub/v2/reservations/rental/{id}/billing-cycle-upgrade/{jobId}` | `CancelRentalBillingCycleUpgradePublic` | Cancel Rental Billing Cycle Upgrade |
| `GET` | `/api/pub/v2/reservations/rental/renewable/{id}` | `GetRenewableRentalPublic` | Renewable Rental Details |
| `POST` | `/api/pub/v2/reservations/rental/renewable/{id}` | `UpdateRenewableRentalPublic` | Update a Renewable Rental |
| `GET` | `/api/pub/v2/reservations/rental/renewable` | `ListRenewableLineRentalsPublic` | List Renewable Rentals |
| `POST` | `/api/pub/v2/reservations/rental/renewable/{id}/refund` | `RenewableSelfServiceRefundRentalPublic` | Refund Renewable Rental |
| `POST` | `/api/pub/v2/reservations/rental/renewable/{id}/renew` | `RenewOverdueRenewableRental` | Renew Overdue Rental |
| `GET` | `/api/pub/v2/reservations/rental/nonrenewable/{id}` | `GetNonrenewableRentalPublic` | Non-Renewable Rental Details |
| `POST` | `/api/pub/v2/reservations/rental/nonrenewable/{id}` | `UpdateNonrenewableRentalPublic` | Update a Non-Renewable Rental |
| `GET` | `/api/pub/v2/reservations/rental/nonrenewable` | `ListNonrenewableRentalsPublic` | List Non-Renewable Rentals |
| `POST` | `/api/pub/v2/reservations/rentals/extensions` | `ExtendNonrenewableRentalPublic` | Extend a Non-Renewable rental |
| `POST` | `/api/pub/v2/reservations/rental/nonrenewable/{id}/refund` | `NonrenewableSelfServiceRefundRentalPublic` | Refund Non-Renewable Rental |
| `GET` | `/api/pub/v2/sms` | `ListSmsPublic` | List SMS |
| `POST` | `/api/pub/v2/sms/reply` | `ReplyToSmsPublic` | Reply to an SMS |
| `POST` | `/api/pub/v2/sms/send` | `SendSmsPublic` | Send an SMS |
| `GET` | `/api/pub/v2/calls` | `ListCallsPublic` | List Calls |
| `POST` | `/api/pub/v2/calls/access-token` | `SetupCallingContextPublic` | Create Call Access Token |
| `GET` | `/api/pub/v2/wake-requests/{id}` | `GetWakeRequestPublic` | Get Wake Request |
| `POST` | `/api/pub/v2/wake-requests` | `CreateWakeRequestPublic` | Create Wake Request |
| `POST` | `/api/pub/v2/wake-requests/estimate` | `EstimateUsageWindow` | Estimate Usage Window |
| `GET` | `/api/pub/v2/webhook-events` | `GetWebhookEventDefinitionsPublic` | List Webhook Events |
| `GET` | `/api/pub/v2/legacy/reservation-id-lookup` | `GetNewReservationId` | Legacy Reservation ID Lookup |
