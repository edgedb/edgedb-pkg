import * as fs from 'fs'
import * as process from 'process'

const re = /^(?:\w+)-(\d+(-(alpha|beta|rc)\d+)?(-dev\d+)?).*\.(rpm|deb|img|pkg)$/gm;

async function run() {
  try {
    const target = process.env['INPUT_TARGET'];
    const path = process.env['INPUT_PATH'];
    const dest = `${path}/artifacts/${target}`;
    let version_slot = '';
    let found_file = '';
    let files: string[] = [];
    try {
      files = fs.readdirSync(dest);
    } catch {
    }

    console.log(`Looking for artifacts in ${dest}...`);
    for (let file of files) {
      let match = re.exec(file);
      if (match !== null) {
        found_file = file;
        version_slot = match[1];
        break;
      }
    }
    console.log(`File ${found_file} yields version slot ${version_slot}`)
    console.log(`::set-output name=version-slot,::${version_slot}`)
  } catch (error) {
    console.log(`::error ${error.message}`)
    process.exit(1)
  }
}

run();
