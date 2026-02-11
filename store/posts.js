const fs = require('fs/promises');
const path = require('path');

const POSTS_PATH = path.join(__dirname, '..', 'data', 'posts.json');

async function readStore() {
  const raw = await fs.readFile(POSTS_PATH, 'utf8');
  const parsed = JSON.parse(raw);
  if (!parsed || typeof parsed !== 'object') return { posts: [] };
  if (!Array.isArray(parsed.posts)) return { posts: [] };
  return parsed;
}

async function writeStore(store) {
  const json = JSON.stringify(store, null, 2) + '\n';
  await fs.writeFile(POSTS_PATH, json, 'utf8');
}

function makeId(title) {
  const base = title
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '')
    .slice(0, 60);
  return `${base || 'post'}-${Date.now()}`;
}

async function listPosts() {
  const store = await readStore();
  return store.posts
    .slice()
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
}

async function addPost({ title, body }) {
  const store = await readStore();
  const now = new Date().toISOString();
  const post = { id: makeId(title), title, body, createdAt: now };
  store.posts.push(post);
  await writeStore(store);
  return post;
}

module.exports = {
  listPosts,
  addPost,
};
