import * as fs from 'fs'
import * as process from 'process'

async function run() {
  try {
    const target = process.env['INPUT_TARGET'];
    const path = process.env['INPUT_PATH'];
    const dest = `${path}/artifacts/${target}`;
    let metadata = JSON.parse(
      fs.readFileSync(`${dest}/package-version.json`, 'utf8'));

    let version_slot = metadata['version_slot'] ?? '';
    let catver = metadata['catalog_version'] ?? '';
    let installref = metadata['installref'] ?? '';

    console.log(`::set-output name=version-slot,::${version_slot}`)
    console.log(`::set-output name=catalog-version,::${catver}`)
    console.log(`::set-output name=install-ref,::${installref}`)
  } catch (error) {
    console.log(`::error ${error.message}`)
    process.exit(1)
  }
}

run();
