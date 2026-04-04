// publish.js — Publishes a Markdown post to WordPress via the REST API
// Usage: node publish.js posts/my-post.md


const fs = require('fs');
const path = require('path');
const matter = require('gray-matter');
const axios = require('axios');
const { marked } = require('marked');


// ── 1. Validate environment variables ────────────────────────────────────────
const WP_URL = (process.env.WP_URL || '').replace(/\/$/, '');
const WP_USER = process.env.WP_USER || '';
const WP_APP_PASSWORD = process.env.WP_APP_PASSWORD || '';


if (!WP_URL || !WP_USER || !WP_APP_PASSWORD) {
  console.error('ERROR: One or more required environment variables are missing.');
  if (!WP_URL)          console.error('  - WP_URL');
  if (!WP_USER)     console.error('  - WP_USER');
  if (!WP_APP_PASSWORD) console.error('  - WP_APP_PASSWORD');
  process.exit(1);
}


// ── 2. Validate file path argument ───────────────────────────────────────────
const filePath = process.argv[2];


if (!filePath) {
  console.error('ERROR: No file path provided. Usage: node publish.js posts/my-post.md');
  process.exit(1);
}
if (!fs.existsSync(filePath)) {
  console.error('ERROR: File not found: ' + filePath);
  process.exit(1);
}


// ── 3. Main publish function ──────────────────────────────────────────────────
async function publishPost(filePath) {
  console.log('Reading: ' + filePath);


  const fileContent = fs.readFileSync(filePath, 'utf8');
  const { data: frontmatter, content: markdownBody } = matter(fileContent);


  if (!frontmatter.title) {
    console.error('ERROR: Frontmatter is missing a required "title" field.');
    process.exit(1);
  }


  // Convert Markdown body to HTML
  const rawHtml = marked(markdownBody);


  // ── Fix image URLs: relative paths → absolute GitHub raw URLs ────────────
  // e.g. ../assets/photo.png becomes:
  // https://raw.githubusercontent.com/owner/repo/main/assets/photo.png
  // GITHUB_REPOSITORY and GITHUB_REF_NAME are auto-provided by GitHub Actions.
  const GITHUB_REPOSITORY = process.env.GITHUB_REPOSITORY || '';
  const GITHUB_REF_NAME   = process.env.GITHUB_REF_NAME   || 'main';
  const fileDir           = path.dirname(filePath);


  function resolveImageUrls(html) {
    if (!GITHUB_REPOSITORY) {
      console.warn('Warning: GITHUB_REPOSITORY not set — skipping image URL rewrite.');
      return html;
    }
    const rawBase = 'https://raw.githubusercontent.com/' + GITHUB_REPOSITORY + '/' + GITHUB_REF_NAME;


    return html.replace(/\b(src|href)="([^"]+)"/g, function(match, attr, url) {
