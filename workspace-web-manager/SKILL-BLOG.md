# SKILL-BLOG.md

Use this skill when asked to create, list, or manage blog posts on the Payload CMS website.

## CMS Connection

- Base URL: http://templategen.gaiada.online
- API base: http://templategen.gaiada.online/api
- Login: POST /api/users/login
- Posts: POST /api/posts (create), GET /api/posts (list)
- Media: POST /api/media (multipart upload)

## Credentials

- Email: demo-author@example.com
- Password: password

## Step 1: Authenticate

Use the `fetch` MCP tool to login and obtain a JWT token.

Request:
- Method: POST
- URL: http://templategen.gaiada.online/api/users/login
- Headers: Content-Type: application/json
- Body: {"email":"demo-author@example.com","password":"password"}

The response contains a `token` field. Use this as `Authorization: JWT <token>` for all subsequent requests.

## Step 2: Create a Blog Post

Use the `fetch` MCP tool to create the post.

Request:
- Method: POST
- URL: http://templategen.gaiada.online/api/posts
- Headers:
  - Content-Type: application/json
  - Authorization: JWT <token>
- Body format:

```json
{
  "title": "Your Post Title",
  "content": {
    "root": {
      "type": "root",
      "children": [
        {
          "type": "paragraph",
          "children": [
            {"text": "Your paragraph text here."}
          ]
        }
      ]
    }
  },
  "heroImage": null,
  "_status": "published",
  "meta": {
    "title": "Your Post Title",
    "description": "A short meta description for SEO."
  }
}
```

For multi-paragraph posts, add multiple paragraph objects inside the `children` array of the root.

For rich content, supported node types inside root.children:
- `{"type": "paragraph", "children": [{"text": "..."}]}` — paragraph
- `{"type": "heading", "tag": "h2", "children": [{"text": "..."}]}` — heading
- `{"type": "list", "listType": "bullet", "children": [{"type": "listitem", "children": [{"text": "..."}]}]}` — list

When asked to use a generic or placeholder image, set `heroImage` to `null` (skip the image). Do not attempt to upload unless a specific image URL or file is provided.

## Step 3: Confirm

After successful creation, respond to the user with:
- The post title
- The post URL: http://templategen.gaiada.online/posts/<slug>
- The post ID from the API response

## Listing and Counting Posts

To list or count posts:
- GET http://templategen.gaiada.online/api/posts
- To filter by date, use the `publishedAt` field with query params:
  - Today's posts: GET /api/posts?where[publishedAt][greater_than]=YYYY-MM-DDT00:00:00.000Z
- The response includes `totalDocs` for counting.

## Rules

- Always authenticate first. Tokens may expire; if a 401 is returned, re-authenticate.
- Use the `fetch` MCP tool for all API calls. Do not use playwright or shell commands for API interactions.
- Keep post content clean and well-structured.
- If the user provides a topic but no body text, generate appropriate content for the post.
