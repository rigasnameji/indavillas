// publish.js — Publishes a Markdown post to WordPress via the REST API
// Usage: node publish.js posts/my-post.md

const fs = require('fs');
const path = require('path');
const matter = require('gray-matter');
const axios = require('axios');
const { marked } = require('marked');

// ── 1. Validate environment variables ────────────────────────────────────────
const WP_URL = (process.env.WP_URL || '').replace(/\/$/, '');
const WP_USERNAME = process.env.WP_USERNAME || '';
const WP_APP_PASSWORD = process.env.WP_APP_PASSWORD || '';

if (!WP_URL || !WP_USERNAME || !WP_APP_PASSWORD) {
  console.error('ERROR: One or more required environment variables are missing.');
  if (!WP_URL)          console.error('  - WP_URL');
  if (!WP_USERNAME)     console.error('  - WP_USERNAME');
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
      if (/^(https?:\/\/|data:|^\/\/|mailto:)/.test(url)) return match;
      const resolved = url.startsWith('/')
        ? url.slice(1)
        : path.posix.normalize(path.posix.join(fileDir, url));
      return attr + '="' + rawBase + '/' + resolved + '"';
    });
  }

  const htmlContent = resolveImageUrls(rawHtml);

  // Build WordPress post payload
  const postData = {
    title:   frontmatter.title,
    content: htmlContent,
    status:  frontmatter.status  || 'draft',
    slug:    frontmatter.slug    || '',
    excerpt: frontmatter.excerpt || '',
  };

  if (frontmatter.categories) {
    postData.categories = Array.isArray(frontmatter.categories)
      ? frontmatter.categories : [frontmatter.categories];
  }
  if (frontmatter.tags) {
    postData.tags = Array.isArray(frontmatter.tags)
      ? frontmatter.tags : [frontmatter.tags];
  }

  // ── 4. Build Basic Auth header ───────────────────────────────────────────
  const cleanPassword = WP_APP_PASSWORD.replace(/\s+/g, '');
  const credentials   = Buffer.from(WP_USERNAME + ':' + cleanPassword).toString('base64');
  const apiUrl        = WP_URL + '/wp-json/wp/v2/posts';

  console.log('Posting to: ' + apiUrl);
  console.log('Title:      ' + postData.title);
  console.log('Status:     ' + postData.status);

  // ── 5. Send POST request ─────────────────────────────────────────────────
  try {
    const response = await axios.post(apiUrl, postData, {
      headers: {
        'Authorization': 'Basic ' + credentials,
        'Content-Type':  'application/json',
      },
    });
    console.log('\nPost published successfully!');
    console.log('  ID:  ' + response.data.id);
    console.log('  URL: ' + response.data.link);
  } catch (error) {
    if (error.response) {
      console.error('\nERROR: WordPress API responded with status ' + error.response.status);
      console.error(JSON.stringify(error.response.data, null, 2));
      if (error.response.status === 401)
        console.error('Hint: Check WP_USERNAME and WP_APP_PASSWORD in GitHub Secrets.');
      if (error.response.status === 403)
        console.error('Hint: WordPress user needs Editor or Administrator role.');
    } else {
      console.error('\nERROR: Could not reach WordPress: ' + error.message);
    }
    process.exit(1);
  }
}

publishPost(filePath);
