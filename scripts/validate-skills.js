#!/usr/bin/env node
/*
 * validate-skills.js - quality gate for this repository's skills.
 *
 *   node scripts/validate-skills.js          check everything, exit 1 on errors
 *   node scripts/validate-skills.js --sync   copy each SKILL.md description into skills.json, then check
 *
 * Checks per skill (rules from Anthropic's skill authoring guidance):
 *   - folder has SKILL.md with frontmatter containing only name, description (plus optional license, metadata, ...)
 *   - name: lowercase letters/digits/hyphens, max 64 chars, equals the folder name, no reserved words
 *   - description: non-empty, max 1024 chars, no angle brackets
 *   - body: at most 500 lines (move detail into references/)
 *   - every `references/...`, `scripts/...`, `assets/...` path mentioned in backticks exists
 *   - skills.json entry exists, description is in sync, category and summary present, `requires` resolve
 *   - every skills/ folder is listed in skills.json
 */
const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, '..');
const skillsDir = path.join(root, 'skills');
const manifestPath = path.join(root, 'skills.json');
const sync = process.argv.includes('--sync');
const ALLOWED = new Set(['name', 'description', 'license', 'allowed-tools', 'metadata', 'compatibility']);
const RESERVED = ['anthropic', 'claude'];

function parseFrontmatter(text) {
  const m = text.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?([\s\S]*)$/);
  if (!m) return null;
  const data = {};
  const lines = m[1].split(/\r?\n/);
  for (let i = 0; i < lines.length; i++) {
    const kv = lines[i].match(/^([A-Za-z][\w-]*):\s*(.*)$/);
    if (!kv) continue;
    const [, key, rest] = kv;
    if (/^[>|][+-]?$/.test(rest.trim())) {            // folded or literal block scalar
      const block = [];
      while (i + 1 < lines.length && (/^\s+/.test(lines[i + 1]) || lines[i + 1] === '')) block.push(lines[++i].trim());
      data[key] = block.filter(Boolean).join(' ');
    } else {
      data[key] = rest.replace(/^(['"])(.*)\1$/, '$2').trim();
    }
  }
  return { data, body: m[2] };
}

const errors = [];
const warnings = [];
const err = (skill, msg) => errors.push(`${skill}: ${msg}`);
const warn = (skill, msg) => warnings.push(`${skill}: ${msg}`);

const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
const byName = new Map(manifest.skills.map((s) => [s.name, s]));
const folders = fs.readdirSync(skillsDir, { withFileTypes: true }).filter((d) => d.isDirectory()).map((d) => d.name).sort();

for (const folder of folders) {
  const dir = path.join(skillsDir, folder);
  const file = path.join(dir, 'SKILL.md');
  if (!fs.existsSync(file)) { err(folder, 'SKILL.md is missing'); continue; }
  const fm = parseFrontmatter(fs.readFileSync(file, 'utf8'));
  if (!fm) { err(folder, 'no valid YAML frontmatter'); continue; }
  const { data, body } = fm;

  for (const key of Object.keys(data)) if (!ALLOWED.has(key)) err(folder, `unexpected frontmatter key '${key}'`);
  const name = data.name || '';
  if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(name) || name.length > 64) err(folder, `invalid name '${name}'`);
  if (name !== folder) err(folder, `name '${name}' does not match the folder name`);
  if (RESERVED.some((w) => name.includes(w))) err(folder, `name contains a reserved word (${RESERVED.join(', ')})`);

  const desc = data.description || '';
  if (!desc) err(folder, 'description is empty');
  if (desc.length > 1024) err(folder, `description is ${desc.length} chars (max 1024)`);
  if (/[<>]/.test(desc)) err(folder, 'description contains angle brackets');

  const lines = body.split(/\r?\n/).length;
  if (lines > 500) err(folder, `SKILL.md body is ${lines} lines (max 500); move detail into references/`);
  else if (lines > 400) warn(folder, `SKILL.md body is ${lines} lines; consider splitting`);

  const refs = new Set([...body.matchAll(/`((?:references|scripts|assets|agents|eval-viewer)\/[A-Za-z0-9_./-]+)`/g)].map((m) => m[1]));
  for (const ref of refs) {
    if (/[*<>]|\.\.\./.test(ref) || ref.endsWith('/')) continue;
    if (!fs.existsSync(path.join(dir, ref))) err(folder, `referenced path does not exist: ${ref}`);
  }

  const entry = byName.get(folder);
  if (!entry) { err(folder, 'not listed in skills.json'); continue; }
  if (sync && desc) entry.description = desc;
  if (entry.description !== desc) err(folder, 'skills.json description is out of sync (run: node scripts/validate-skills.js --sync)');
  if (!entry.category) err(folder, 'skills.json: category is missing');
  if (!entry.summary) err(folder, 'skills.json: summary is missing');
  else if (entry.summary.length > 90) warn(folder, `summary is ${entry.summary.length} chars; keep it under 90 for the list view`);
  for (const dep of entry.requires || []) if (!folders.includes(dep)) err(folder, `requires unknown skill '${dep}'`);
}

for (const s of manifest.skills) if (!folders.includes(s.name)) err(s.name, 'listed in skills.json but the folder does not exist');

if (sync) {
  manifest.updated = new Date().toISOString().slice(0, 10);
  fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2) + '\n');
  console.log(`skills.json synced (${manifest.skills.length} skills).`);
}

warnings.forEach((w) => console.log(`warning: ${w}`));
errors.forEach((e) => console.error(`error:   ${e}`));
console.log(`\n${folders.length} skill(s) checked: ${errors.length} error(s), ${warnings.length} warning(s).`);
process.exit(errors.length ? 1 : 0);
