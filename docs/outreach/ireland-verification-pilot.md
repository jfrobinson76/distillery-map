# Ireland distillery verification pilot

**Status:** Draft plan — no outreach authorised or sent.  
**Owner:** John Robinson / Distillery Map by Stillbound  
**Date:** 29 August 2026

## Boundary

This is a Distillery Map accuracy and participation programme. It is not a Stillbound
sales sequence and has no connection to Spirit Executive/AIMS, recruiting, candidate
sourcing, or hiring outreach. Claim and response data never flows to a recruiter.

The first contact asks a distillery to check facts already published on its map listing.
It must not contain a product pitch, meeting request, newsletter enrolment, recruitment
language, tracking pixel, or disguised commercial CTA.

## Pilot cohort

Start with one manually reviewed batch of no more than 10 Irish distilleries. Prioritise:

1. Sites included in the Ireland brand-findability pilot.
2. Listings missing brands, visitor information, or a booking link.
3. Distilleries whose own website publishes a general business address such as
   `info@`, `hello@`, or `visitor@`.

Named personal addresses are excluded from the first batch unless the person has an
obvious responsibility for the public listing and there is no appropriate role address.
Every recipient record must carry the public source URL and the date it was checked.

## GDPR/ePrivacy operating position

- Purpose: a one-time factual accuracy request about an existing public listing.
- Legal basis for the limited personal-data processing: legitimate interests in
  maintaining an accurate public directory, documented per recipient/source.
- The message is service/accuracy-only. If promotional copy is added, stop: it becomes
  a different communication and requires a fresh compliance review.
- Identify John/Stillbound, the source of the address, the purpose, the privacy notice,
  and the right to object near the top of the email.
- No automatic follow-up to a non-responder during the pilot.
- Delete non-responder contact details within 90 days. Keep only a minimal suppression
  record after an objection.

This is an operational compliance position, not external legal advice. Re-review it
before expanding beyond Ireland, adding promotional content, or using named addresses
at scale.

### Legitimate-interests assessment for the pilot

- **Purpose test:** accurate public listings benefit the distillery, map users and the
  integrity of the community dataset.
- **Necessity test:** one short message to a business-published address is the least
  intrusive practical way to ask the organisation to verify facts that concern it.
- **Balancing test:** a business can reasonably expect a factual query about its own
  public information at an address it publishes for contact. Risk is reduced by using
  role addresses first, naming the source, sending once, excluding sales content,
  offering an immediate objection, avoiding tracking, and deleting non-responder data.

Record this assessment with the batch. Stop and re-assess if the message, audience,
frequency, purpose, territory, data source or automation changes.

### Provider pre-flight

Before the first send, retain evidence of the current Formspree processor/SCC position
and confirm that the Google Workspace data-processing terms apply to the sending account.
The website notice must stay aligned with the processors actually in use. A provider or
account change pauses the batch until the notice and transfer position are checked.

## Approval-gated Gmail workflow

Automation is allowed only as a drafting and controlled-send aid:

1. Build a recipient sheet containing distillery, listing URL, email, source URL,
   source date, missing fields, and suppression status.
2. John approves the exact template and the complete recipient sheet.
3. Automation creates individual Gmail drafts — never a BCC blast.
4. Spot-check every draft in the first batch for correct facts, recipient, source and
   links.
5. John gives a separate explicit send approval for that batch.
6. Send, label `Distillery Map / Ireland verification`, and log sent date/outcome.
7. Any objection is actioned immediately and added to the suppression list.

No message is sent merely because its draft was approved. Template approval, recipient
approval, and send approval are three separate gates.

## Draft email for approval

**Subject:** Quick accuracy check: {{distillery_name}} on Distillery Map

Hi {{name_or_team}},

I’m John Robinson, founder of Stillbound and the person behind Distillery Map. I’m
writing to this address because it is published on {{source_domain}}.

This is a one-time request to check your public map listing, not a sales email. You can
read how I use contact information at
https://distillerymap.org/privacy. If you would rather I did not contact this address
again, reply “no thanks” and I’ll record that.

Your listing is here: {{listing_url}}

Could you check these details when you have a moment?

- distillery/site name and map location
- website and booking link
- brands made at the site
- tours, tastings, shop or other visitor information

You can reply with corrections or claim the listing from the link above. Claiming,
verification and the enhanced listing are free.

Thanks,

John Robinson  
Distillery Map by Stillbound  
hello@distillerymap.org

## Pilot measures

- delivery/bounce rate
- objections and complaints (target: zero)
- replies
- verified claims
- corrected brands and visitor details
- time required per completed listing

The decision after 10 is whether the value exchange works and the process is safe — not
whether automation can send a larger batch.
