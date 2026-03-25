const fs = require("fs");
const axios = require("axios");
const marked = require("marked");

const file = fs.readFileSync("posts/latest.md", "utf-8");
const html = marked.parse(file);

const auth = Buffer.from(
  process.env.WP_USER + ":" + process.env.WP_APP_PASSWORD
).toString("base64");

axios.post(
  process.env.WP_URL + "/wp-json/wp/v2/posts",
  {
    title: "Auto Post",
    content: html,
    status: "publish"
  },
  {
    headers: {
      Authorization: `Basic ${auth}`
    }
  }
).then(() => console.log("Posted!"))
  .catch(err => console.error(err.response.data));
