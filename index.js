#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const pkgPath = path.join(__dirname, 'package.json');
const manifestPath = path.join(__dirname, 'skills.json');

const c = {
  reset: "\x1b[0m",
  bold: "\x1b[1m",
  cyan: "\x1b[36m",
  green: "\x1b[32m",
  dim: "\x1b[2m",
};

const col = (color, text) => `${c[color]}${text}${c.reset}`;

function showHelp() {
  console.log(`
${col("bold", col("cyan", "🤖  custom-skills"))} — Manage your AI skill collection

${col("bold", "USAGE")}
  npx custom-skills [options]

${col("bold", "OPTIONS")}
  ${col("green", "--list")}          List all available skills
  ${col("green", "--info=<name>")}   Show details and path for a specific skill
  ${col("green", "--help")}          Show this help message
`);
}

function listSkills() {
  if (!fs.existsSync(manifestPath)) {
    console.error("Error: skills.json manifest not found.");
    process.exit(1);
  }

  const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  console.log(`\n${col("bold", "Available Skills:")}\n`);
  
  manifest.skills.forEach(skill => {
    console.log(`  ${col("cyan", "◆")} ${col("bold", skill.name.padEnd(20))} ${col("dim", skill.description)}`);
  });
  console.log("");
}

function showSkillInfo(name) {
  if (!fs.existsSync(manifestPath)) {
    console.error("Error: skills.json manifest not found.");
    process.exit(1);
  }

  const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  const skill = manifest.skills.find(s => s.name === name);

  if (!skill) {
    console.error(`Error: Skill "${name}" not found.`);
    process.exit(1);
  }

  const skillDir = path.join(__dirname, 'skills', skill.name);
  const skillFile = path.join(skillDir, 'SKILL.md');

  console.log(`\n${col("bold", "Skill Information:")}`);
  console.log(`  ${col("cyan", "Name:")}        ${skill.name}`);
  console.log(`  ${col("cyan", "Description:")} ${skill.description}`);
  console.log(`  ${col("cyan", "Category:")}    ${skill.category}`);
  console.log(`  ${col("cyan", "Path:")}        ${skillFile}`);
  console.log("");
}

const args = process.argv.slice(2);
const listArg = args.includes('--list');
const helpArg = args.includes('--help');
const infoArg = args.find(a => a.startsWith('--info='));

if (helpArg || args.length === 0) {
  showHelp();
} else if (listArg) {
  listSkills();
} else if (infoArg) {
  const name = infoArg.split('=')[1];
  showSkillInfo(name);
} else {
  showHelp();
}
