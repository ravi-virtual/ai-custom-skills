#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const manifestPath = path.join(__dirname, 'skills.json');
const skillsSourceDir = path.join(__dirname, 'skills');

// ─── Color Helpers ────────────────────────────────────────────────────────────
const c = {
  reset:   '\x1b[0m',
  bold:    '\x1b[1m',
  dim:     '\x1b[2m',
  cyan:    '\x1b[36m',
  green:   '\x1b[32m',
  yellow:  '\x1b[33m',
  red:     '\x1b[31m',
  magenta: '\x1b[35m',
  blue:    '\x1b[34m',
};
const col  = (color, text) => `${c[color]}${text}${c.reset}`;
const bold = (text) => col('bold', text);
const dim  = (text) => col('dim', text);
const ok   = (text) => col('green', text);
const warn = (text) => col('yellow', text);
const err  = (text) => col('red', text);

// ─── Manifest Loader ──────────────────────────────────────────────────────────
function loadManifest() {
  if (!fs.existsSync(manifestPath)) {
    console.error(err('✖  skills.json manifest not found.'));
    process.exit(1);
  }
  return JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
}

// ─── Recursive Copy ───────────────────────────────────────────────────────────
function copyDirSync(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    const srcPath  = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    if (entry.isDirectory()) {
      copyDirSync(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

// ─── Help ─────────────────────────────────────────────────────────────────────
function showHelp() {
  console.log(`
${bold(col('cyan', '🤖  ai-custom-skills'))} ${dim('v' + require('./package.json').version)}  — Install & manage AI skills

${bold('USAGE')}
  npx ai-custom-skills <command> [options]

${bold('COMMANDS')}
  ${col('green', 'list')}                       List all available skills
  ${col('green', 'info')} ${col('yellow', '<skill-name>')}         Show details for a specific skill
  ${col('green', 'install')}                    Install ALL skills to ./skills/ in current dir
  ${col('green', 'install')} ${col('yellow', '<skill-name>')}      Install a specific skill to ./skills/
  ${col('green', 'install --all')}              Install ALL skills (explicit flag)
  ${col('green', 'help')}                       Show this help message

${bold('EXAMPLES')}
  ${dim('npx ai-custom-skills list')}
  ${dim('npx ai-custom-skills info debug-reactjs-error')}
  ${dim('npx ai-custom-skills install')}
  ${dim('npx ai-custom-skills install mern-stack-project')}
  ${dim('npx ai-custom-skills install skill-creator')}
`);
}

// ─── List ─────────────────────────────────────────────────────────────────────
function listSkills() {
  const manifest = loadManifest();
  const skills   = manifest.skills;

  // Group by category
  const grouped = {};
  for (const skill of skills) {
    const cat = skill.category || 'Uncategorized';
    (grouped[cat] = grouped[cat] || []).push(skill);
  }

  console.log(`\n${bold('Available Skills')} ${dim(`(${skills.length} total)`)}\n`);

  for (const [category, catSkills] of Object.entries(grouped)) {
    console.log(`  ${col('magenta', bold(category))}`);
    for (const skill of catSkills) {
      const srcExists = fs.existsSync(path.join(skillsSourceDir, skill.name, 'SKILL.md'));
      const tag = srcExists ? ok('●') : warn('○');
      console.log(`    ${tag}  ${bold(skill.name.padEnd(28))} ${dim(skill.description.slice(0, 60) + '…')}`);
    }
    console.log('');
  }

  console.log(dim('  Use: npx ai-custom-skills info <name>  to see full details'));
  console.log(dim('       npx ai-custom-skills install       to copy skills into your project\n'));
}

// ─── Info ─────────────────────────────────────────────────────────────────────
function showSkillInfo(name) {
  if (!name) {
    console.error(err('✖  Usage: npx ai-custom-skills info <skill-name>'));
    process.exit(1);
  }

  const manifest = loadManifest();
  const skill    = manifest.skills.find(s => s.name === name);

  if (!skill) {
    console.error(err(`✖  Skill "${name}" not found.`));
    console.log(dim('   Run: npx ai-custom-skills list  to see all available skills.'));
    process.exit(1);
  }

  const skillDir  = path.join(skillsSourceDir, skill.name);
  const skillFile = path.join(skillDir, 'SKILL.md');
  const hasFile   = fs.existsSync(skillFile);

  // Find sub-resources
  const scripts  = fs.existsSync(path.join(skillDir, 'scripts'))
    ? fs.readdirSync(path.join(skillDir, 'scripts'))
    : [];
  const examples = fs.existsSync(path.join(skillDir, 'examples'))
    ? fs.readdirSync(path.join(skillDir, 'examples'))
    : [];
  const resources = fs.existsSync(path.join(skillDir, 'resources'))
    ? fs.readdirSync(path.join(skillDir, 'resources'))
    : [];

  console.log(`\n${bold('Skill:')} ${col('cyan', skill.name)}\n`);
  console.log(`  ${bold('Category:')}    ${skill.category || 'N/A'}`);
  console.log(`  ${bold('SKILL.md:')}    ${hasFile ? ok('✔ present') : warn('✖ missing')}`);
  if (scripts.length)   console.log(`  ${bold('Scripts:')}     ${scripts.join(', ')}`);
  if (examples.length)  console.log(`  ${bold('Examples:')}    ${examples.join(', ')}`);
  if (resources.length) console.log(`  ${bold('Resources:')}   ${resources.join(', ')}`);
  console.log(`\n  ${bold('Description:')}`);
  console.log(`  ${dim(skill.description)}\n`);
  console.log(dim(`  To install: npx ai-custom-skills install ${skill.name}\n`));
}

// ─── Install ─────────────────────────────────────────────────────────────────
function installSkills(target) {
  const manifest  = loadManifest();
  const cwd       = process.cwd();
  const destBase  = path.join(cwd, 'skills');
  const installAll = !target || target === '--all';

  const toInstall = installAll
    ? manifest.skills
    : (() => {
        const found = manifest.skills.find(s => s.name === target);
        if (!found) {
          console.error(err(`✖  Skill "${target}" not found in the manifest.`));
          console.log(dim('   Run: npx ai-custom-skills list  to see all available skills.'));
          process.exit(1);
        }
        return [found];
      })();

  console.log(`\n${bold('Installing')} ${col('cyan', installAll ? 'all skills' : `"${target}"`)} → ${col('yellow', destBase)}\n`);

  let installed = 0;
  for (const skill of toInstall) {
    const src  = path.join(skillsSourceDir, skill.name);
    const dest = path.join(destBase, skill.name);

    if (!fs.existsSync(src)) {
      console.log(`  ${warn('⚠')}  Skipped ${bold(skill.name)} ${dim('(source folder missing)')}`);
      continue;
    }

    const alreadyExists = fs.existsSync(dest);
    copyDirSync(src, dest);
    const status = alreadyExists ? warn('↻  Updated') : ok('✔  Installed');
    console.log(`  ${status}  ${bold(skill.name)}`);
    installed++;
  }

  console.log(`\n${ok(`✔  Done!`)} ${installed} skill(s) copied to ${col('cyan', destBase + path.sep)}\n`);
}

// ─── Entrypoint ───────────────────────────────────────────────────────────────
const [,, cmd, ...rest] = process.argv;

switch (cmd) {
  case 'list':
    listSkills();
    break;

  case 'info':
    showSkillInfo(rest[0]);
    break;

  case 'install':
    installSkills(rest[0]);
    break;

  case 'help':
  case '--help':
  case '-h':
  case undefined:
    showHelp();
    break;

  default:
    console.error(err(`✖  Unknown command: "${cmd}"`));
    showHelp();
    process.exit(1);
}
