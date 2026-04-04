// publish.js — Publishes a Markdown post to WordPress via the REST API
// Usage: node publish.js posts/my-post.md

const fs = require('fs');
const path = require('path');
const matter = require('gray-matter');
const axios = require('axios');
const { marked } = require('marked');

// ── 1. Validate environment variables ──────────────────────────────────────────
const WP_URL = (process.env.WP_URL || '').replace(/\/$/, '');
const WP_USER = process.env.WP_USER || '';
const WP_APP_PASSWORD = process.env.WP_APP_PASSWORD || '';

if (!WP_URL || !WP_USER || !WP_APP_PASSWORD) {
  console.error('ERROR: One or more required environment variables are missing.');
  if (!WP_URL)          console.error('  - WP_URL');
  if (!WP_USER)         console.error('  - WP_USER');
  if (!WP_APP_PASSWORD) console.error('  - WP_APP_PASSWORD');
  process.exit(1);
}

// ── 2. Validate file path argument ──────────────────────────────────────────────
const filePath = process.argv[2] || process.env.POST_FILE || '';
console.log('POST_FILE env:', process.env.POST_FILE);
console.log('filePath resolved:', filePath);

if (!filePath) {
  console.error('ERROR: No file path provided. Usage: node publish.js posts/my-post.md');
  process.exit(1);
}

if (!fs.existsSync(filePath)) {
  console.error('ERROR: File not found: ' + filePath);
  process.exit(1);
}

// ── 3. Main publish function ────────────────────────────────────────────────────
async function publishPost(filePath) {
  console.log('Reading: ' + filePath);
  const fileContent = fs.readFileSync(filePath, 'utf8');
  const { data: frontmatter, content: markdownBody } = matter(fileContent);

  if (!frontmatter.title) {
    console.error('ERROR: Frontmatter is missing a required "title" field.');
    process.exit(1);
  }

  const rawHtml = marked(markdownBody);

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
      if (/^(https?:\/\/|data:|^\/\/|mailto:)/.test(url)) return match;
      const resolved = url.startsWith('/')
        ? url.slice(1)
        : path.posix.normalize(path.posix.join(fileDir, url));
      return attr + '="' + rawBase + '/' + resolved + '"';
    });
  }

  const htmlContent = resolveImageUrls(rawHtml);

  const postData = {
    title:   frontmatter.title,
    content: htmlContent,
    status:  frontmatter.status || 'draft',
    slug:    frontmatter.slug   || '',
    excerpt: frontmatter.excerpt || '',
  };

  // WordPress REST API requires integer IDs for tags/categories.
  // Only include them if the frontmatter values are actually numbers.
  if (frontmatter.categories) {
    const cats = Array.isArray(frontmatter.categories) ? frontmatter.categories : [frontmatter.categories];
    const numericCats = cats.filter(c => Number.isInteger(Number(c)) && String(c).trim() !== '').map(Number);
    if (numericCats.length > 0) postData.categories = numericCats;
  }

  if (frontmatter.tags) {
    const tags = Array.isArray(frontmatter.tags) ? frontmatter.tags : [frontmatter.tags];
    const numericTags = tags.filter(t => Number.isInteger(Number(t)) && String(t).trim() !== '').map(Number);
    if (numericTags.length > 0) postData.tags = numericTags;
  }

  const cleanPassword = WP_APP_PASSWORD.replace(/\s+/g, '');
  const credentials = Buffer.from(WP_USER + ':' + cleanPassword).toString('base64');

  const apiUrl = WP_URL + '/wp-json/wp/v2/posts';
  console.log('Posting to: ' + apiUrl);
  console.log('Title: '     + postData.title);
  console.log('Status: '    + postData.status);
  console.log('Slug: '      + postData.slug);

  try {
    const response = await axios.post(apiUrl, postData, {
      headers: {
        'Authorization': 'Basic ' + credentials,
        'Content-Type':  'application/json',
      },
    });

    console.log('\nSUCCESS — Post created in WordPress!');
    console.log('  Post ID : ' + response.data.id);
    console.log('  Post URL: ' + response.data.link);

  } catch (error) {
    if (error.response) {
      console.error('\nERROR: WordPress API responded with status ' + error.response.status);
      console.error(JSON.stringify(error.response.data, null, 2));
      if (error.response.status === 401) {
        console.error('Hint: Check WP_USER and WP_APP_PASSWORD secrets.');
      }
      if (error.response.status === 403) {
        console.error('Hint: WP user must be Editor or Administrator.');
      }
    } else {
      console.error('\nERROR: Could not reach WordPress: ' + error.message);
    }
    process.exit(1);
  }
}

publishPost(filePath);
