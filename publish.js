const fs = require("fs");
const axios = require("axios");
const matter = require("gray-matter");
const { marked } = require("marked");

// Read the file path from the environment variable set by the workflow
const filePath = process.env.POST_FILE;

if (!filePath) {
  console.error("ERROR: No POST_FILE environment variable provided.");
  process.exit(1);
}

if (!fs.existsSync(filePath)) {
  console.error("ERROR: File not found: " + filePath);
  process.exit(1);
}

// Read the raw markdown file
const rawFile = fs.readFileSync(filePath, "utf-8");

// Parse frontmatter AND body separately using gray-matter
const { data: frontmatter, content: markdownBody } = matter(rawFile);

// Convert the Markdown body (without frontmatter) to HTML
const htmlContent = marked.parse(markdownBody);

// Pull values from frontmatter with sensible fallbacks
const title   = frontmatter.title   || "Untitled Post";
const slug    = frontmatter.slug    || "";
const excerpt = frontmatter.excerpt || "";
const status  = frontmatter.status  || "draft";

// Build Basic Auth from WordPress Application Password
const credentials = Buffer.from(
  process.env.WP_USER + ":" + process.env.WP_APP_PASSWORD
).toString("base64");

// Build the post payload
const postData = {
  title:   title,
  content: htmlContent,
  status:  status,
  excerpt: excerpt,
};

// Only set the slug if one is provided
if (slug) {
  postData.slug = slug;
}

console.log('Publishing: "' + title + '" (status: ' + status + ') from ' + filePath);

axios
  .post(process.env.WP_URL + "/wp-json/wp/v2/posts", postData, {
    headers: {
      Authorization: "Basic " + credentials,
      "Content-Type": "application/json",
    },
  })
  .then(function(res) {
    console.log("Post published successfully!");
    console.log("   ID:  " + res.data.id);
    console.log("   URL: " + res.data.link);
  })
  .catch(function(err) {
    if (err.response) {
      console.error("WordPress API error:", JSON.stringify(err.response.data, null, 2));
    } else {
      console.error("Network/connection error:", err.message);
    }
    process.exit(1);
  });
