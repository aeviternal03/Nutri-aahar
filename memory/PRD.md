# Nutri-Aahar
<!-- 2026-06: Removed B2B and Export pages/routes/nav (catch-all redirect to home). Contact + Quote forms: name, company, phone, email, city (new field), country all mandatory. Enquiry emails wired via Resend to info.ashirwadt@gmail.com — PENDING RESEND_API_KEY in backend/.env (currently skips gracefully). Footer: email + Bangalore (Sarjapur 560035) & Bihar (Gaya 823001) factory addresses, PAN India delivery. Atta & Flours category added (6 products, catalogue total 35). Test run iteration_2.json: 100% pass. -->
<!-- 2026-06: Whole Spices now 13 products (removed carom, nigella, poppy, black cumin; added Star Anise). Uploaded photos applied to cumin, cinnamon, black pepper, mace, star anise. Generated accurate images replaced wrong stock photos (green cardamom, cloves, coriander, fennel). Catalogue total: 29 products. -->
<!-- 2026-06: Makhana expanded to 6 products (Raw White Bulk + 5 roasted flavours: Pink Salt, Black Salt, Pepper, Chilli Tomato, Cheese) with user-uploaded jar photos. Catalogue is now 32 products. All products enriched with benefits/nutrition/form details taken from the user's Google Slides deck (Bihar exim presentation). Product detail page renders Uses & benefits, Nutrition, Shelf life, Available form rows conditionally. Fonts: Manrope (headings) + Figtree (body). All page heroes use uploaded spice cover photo. -->
<!-- 2026-06: Hero cover photo replaced with user-uploaded spice image (customer-assets URL in App.js bulkImg) -->
 Product Requirements & Handoff

## Original problem statement
Build a premium, modern, responsive website for Nutri-Aahar as a healthy/natural Indian food brand, B2B wholesale supplier and Indian food exporter. The website must combine Indian heritage, premium food photography, earthy luxury, vibrant spice accents and modern B2B professionalism. Required pages: Home, About, Products, B2B/Bulk Orders, Export, Request a Quote and Contact. Include reusable product cards, product details, enquiry forms, strong Request a Quote calls-to-action, responsive navigation, editable/unverified product fields, and avoid fabricated certifications, testimonials, export destinations, statistics or business claims.

## User decisions
- Store quote, B2B, export and contact enquiries inside the website for now with a simple success message.
- Use the provided product list and leave unverified product details editable; do not invent MOQ, certifications or specifications.
- Use the uploaded Nutri-Aahar logo and earthy premium supporting photography.

## Architecture decisions
- React frontend with React Router, lucide-react, sonner and axios.
- FastAPI backend with MongoDB storage using existing MONGO_URL and DB_NAME environment variables.
- Product catalogue is served from `/api/products`; enquiry records are stored in MongoDB at `/api/enquiries`.
- Frontend requests use the existing `REACT_APP_BACKEND_URL`; no environment values were changed.
- Product data is intentionally structured as a simple editable list for future catalogue management.

## Implemented
- Premium responsive homepage with logo, hero, trust strip, category cards, story section and CTA.
- About page with story and values.
- Product catalogue with category filters, reusable cards and product detail pages.
- B2B, Export, Quote and Contact flows with reusable validated forms and success state.
- Backend enquiry persistence and product API, including Dates/Dry Fruits category aliases.
- Responsive mobile menu, mobile layout, hover states, editorial typography and earthy palette.
- Verified with production build, JavaScript/Python lint, API tests and browser flow tests.
- Browser title, meta description, keywords and Open Graph tags rebranded to Nutri-Aahar (24 Aug 2026).
- Full catalogue expansion to 27 products covering all 16 listed whole spices, spice powders, makhana, dates, dry fruits and seeds/specialty; all product images verified live (24 Aug 2026).
- User-requested visual edits: full tagline in header, bulk Indian spice market hero photo, distinct imagery per category card incl. dedicated Dates photo (24 Aug 2026).

## Prioritized backlog
- P0: Add verified business email, phone, address and registration details when available.
- P1: Add a secure internal enquiry dashboard for reviewing saved leads.
- P1: Expand the catalogue with verified products, images, packaging, shelf life and certifications.
- P2: Add downloadable product catalogue and enquiry follow-up workflow.