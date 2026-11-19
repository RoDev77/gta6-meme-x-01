// gta6-meme-x-01 entrypoint (Node 22, standard library only).
//
// What it does, in order:
//   1. Reads POST.json from the bot directory (MAKEFUN_BOT_DIR, default /bot).
//   2. Parses it and checks that its `url` points at a real X/Twitter post.
//   3. Prints the validated post URL to stdout, then copies POST.json
//      byte-for-byte into the output directory (MAKEFUN_OUTPUT_DIR,
//      default /output), creating that directory first if needed.
// If the file cannot be read, is not valid JSON, or the URL is not a
// post address, the program reports the problem on stderr and exits
// with status 1, leaving nothing copied behind.

import { copyFileSync, mkdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

// Matches a plain X/Twitter post link, with an optional www. or
// mobile. prefix, and also the /i/web/status/<id> variant that the
// site itself uses for its canonical links:
//   https://x.com/<handle>/status/<digits>
//   https://twitter.com/<handle>/status/<digits>
//   https://x.com/i/web/status/<digits>
const POST_URL_PATTERN =
  /^https:\/\/(?:www\.|mobile\.)?(?:x\.com|twitter\.com)\/(?:[A-Za-z0-9_]+\/status|i\/web\/status)\/\d+$/;

function fail(message: string): never {
  console.error(`gta6-meme-x-01: ${message}`);
  process.exit(1);
}

const sourcePath = join(BOT_DIR, 'POST.json');
const targetPath = join(OUTPUT_DIR, 'POST.json');

let raw: string;
try {
  raw = readFileSync(sourcePath, 'utf8');
} catch (err) {
  fail(`could not read ${sourcePath}: ${(err as Error).message}`);
}

let post: unknown;
try {
  post = JSON.parse(raw);
} catch (err) {
  fail(`POST.json is not valid JSON: ${(err as Error).message}`);
}

const url =
  post !== null && typeof post === 'object'
    ? (post as Record<string, unknown>).url
    : undefined;

if (typeof url !== 'string' || !POST_URL_PATTERN.test(url)) {
  fail(
    'POST.json must contain a valid X/Twitter post URL, ' +
      'like https://x.com/<handle>/status/<digits>',
  );
}

// The file is good: announce the post, then hand it over untouched.
console.log(url);
mkdirSync(OUTPUT_DIR, { recursive: true });
try {
  copyFileSync(sourcePath, targetPath);
} catch (err) {
  fail(`could not copy POST.json to ${targetPath}: ${(err as Error).message}`);
}
