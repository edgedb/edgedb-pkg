import * as fs from 'fs'
import * as process from 'process'

const re = /(?:\w+)-(\d+(-(dev|alpha|beta|rc)\d+)?).*\.(rpm|deb|img)/gm;

async function run() {
  try {
    const target = process.env['INPUT_TARGET'];
    const path = process.env['INPUT_PATH'];
    const dest = `${path}/artifacts/${target}`;
    let version_slot = '';
    let files: string[] = [];
    try {
      files = fs.readdirSync(dest);
    } catch {
    }

    console.log(`Looking for artifacts in ${dest}...`);
    for (let file of files) {
      let match = re.exec(file);
      if (match !== null) {
        version_slot = match[1];
      }
    }

    console.log(`::set-output name=version-slot,::${version_slot}`)
  } catch (error) {
    console.log(`::error ${error.message}`)
    process.exit(1)
  }
}

run();
