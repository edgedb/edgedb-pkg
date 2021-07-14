import * as fs from 'fs'
import * as process from 'process'

const slot_re = /^(?:(?:\w|-)+?)-(?<slot>\d+(?:-(?:alpha|beta|rc)\d+)?(?:-dev\d+)?).*\.(?:rpm|deb|img|pkg)$/gm;
const cv_re = /^(?:(?:\w|-)+?)-(?<slot>\d+(?:-(?:alpha|beta|rc)\d+)?(?:-dev\d+)?).*(?:\.cv(?<catver>\d+)).*\.(?:rpm|deb|img|pkg)$/gm;

async function run() {
  try {
    const target = process.env['INPUT_TARGET'];
    const path = process.env['INPUT_PATH'];
    const dest = `${path}/artifacts/${target}`;
    let version_slot = '';
    let catver = '';
    let found_file = '';
    let files: string[] = [];
    try {
      files = fs.readdirSync(dest);
    } catch {
    }

    console.log(`Looking for artifacts in ${dest}...`);
    for (let file of files) {
      let match = slot_re.exec(file);
      if (match !== null && match.groups !== undefined) {
        found_file = file;
        version_slot = match.groups.slot;

        match = cv_re.exec(file);
        if (match !== null && match.groups !== undefined) {
          catver = match.groups.catver;
        }

        break;
      }
    }

    if (found_file !== '') {
      console.log(`File ${found_file} yields version slot '${version_slot}'`
                  + ` and catalog version '${catver}'`)
    }
    console.log(`::set-output name=version-slot,::${version_slot}`)
    console.log(`::set-output name=catalog-version,::${catver}`)
  } catch (error) {
    console.log(`::error ${error.message}`)
    process.exit(1)
  }
}

run();
