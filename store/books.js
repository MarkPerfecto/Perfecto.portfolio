const fs = require('fs/promises');
const path = require('path');

const BOOKS_PATH = path.join(__dirname, '..', 'data', 'books.json');

async function readStore() {
  const raw = await fs.readFile(BOOKS_PATH, 'utf8');
  const parsed = JSON.parse(raw);
  if (!parsed || typeof parsed !== 'object') return { books: [] };
  if (!Array.isArray(parsed.books)) return { books: [] };
  return parsed;
}

async function writeStore(store) {
  const json = JSON.stringify(store, null, 2) + '\n';
  await fs.writeFile(BOOKS_PATH, json, 'utf8');
}

async function listBooks() {
  const store = await readStore();
  return store.books
    .slice()
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
}

async function addBook(book) {
  const store = await readStore();
  store.books.push(book);
  await writeStore(store);
  return book;
}

module.exports = {
  listBooks,
  addBook,
};
