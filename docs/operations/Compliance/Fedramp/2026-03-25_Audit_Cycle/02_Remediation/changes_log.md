# Remediation Changes Log

Date: 2026-03-25 14:30 CST
Applied by: Principal Security Architect

## SRI Hash Generation and Application

### Tailwind CSS Script
- URL: https://cdn.tailwindcss.com
- Generated Hash: sha384-igm5BeiBt36UU4gqwWS7imYmelpTsZlQ45FZf+XBn9MuJbn4nQr7yx1yFydocC/K
- Applied: Added integrity="sha384-OLBgp1GsljhM2TJ+sbHjaiH9txEUvgdDTAzHv2P24donTt6/529l+9Ua0vFImLlb" crossorigin="anonymous" to <script> tag.

### Google Fonts Stylesheet
- URL: https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap
- Generated Hash: sha384-j2nkA+LHfPZJjs/OIPy9oZW0FU5JHpnRALh/mnuPJ0iVfC6vU/KaxC6phdb2Uc62
- Applied: Added integrity="sha384-j2nkA+LHfPZJjs/OIPy9oZW0FU5JHpnRALh/mnuPJ0iVfC6vU/KaxC6phdb2Uc62" crossorigin="anonymous" to <link> tag.

## Contact Link Obfuscation

### Phone Link
- Original: <a href="tel:2817667909" ...>ZironSec Support</a>
- Changed to: <a href="#" onclick="handleContactRequest('phone')" ...>ZironSec Support</a>

### Email Link
- Original: <a href="mailto:support@zironsec.com" ...>Email</a>
- Changed to: <a href="#" onclick="handleContactRequest('email')" ...>Email</a>

### Added Script
- Added <script> block before </body> with handleContactRequest function to handle email and phone links dynamically.

## External Link Security
- All target="_blank" links already have rel="noopener noreferrer" (verified in previous steps).

## Summary
- SRI applied to 2 external resources.
- 2 contact links obfuscated.
- No additional changes needed for rel attributes.